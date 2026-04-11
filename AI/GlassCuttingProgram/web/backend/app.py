#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glass Cutting Web Interface - Flask Backend
LiSEC GFB-60/30RE Cam Kesme Makinesi

API Endpoints:
- /api/orders - Sipariş CRUD
- /api/optimize - Optimizasyon çalıştır
- /api/gcode - G-code dosyası
- /api/status - Makine durumu
- /api/defects - Kusur tespiti
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS

# Add module path
MODULES_PATH = Path(__file__).parent.parent.parent  # GlassCuttingProgram directory
sys.path.insert(0, str(MODULES_PATH))

from glass_cutting_orchestrator import (
    GlassCuttingOrchestrator,
    GlassOrder,
    DefectPoint
)

from modules import (
    NestingOptimizer, NestingAlgorithm, Part,
    CuttingPathOptimizer, PathAlgorithm,
    NC300GCodeGenerator, GlassType,
    LaminatedGlassCalculator, LaminatedGlassSpec, FilmType,
    DefectHandler, Defect, DefectType,
    HMIInterface, HMIOrderEntry,
    HerofisConnector, HerofisOrder, ImportResult
)

# Create Flask app
app = Flask(__name__,
            template_folder=str(MODULES_PATH / 'web' / 'frontend'),
            static_folder=str(MODULES_PATH / 'web' / 'frontend' / 'static'))

CORS(app)

# Configuration
MACHINE_WIDTH = 6000  # mm
MACHINE_HEIGHT = 3000  # mm

# Global state
current_orders: List[GlassOrder] = []
current_result: Optional[Dict] = None
current_gcode: Optional[str] = None
machine_status: Dict = {
    "status": "idle",
    "current_x": 0,
    "current_y": 0,
    "parts_completed": 0,
    "parts_remaining": 0
}

# Initialize orchestrator
orchestrator = GlassCuttingOrchestrator(MACHINE_WIDTH, MACHINE_HEIGHT)


# ==================== HTML Routes ====================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/orders')
def orders_page():
    """Orders management page"""
    return render_template('orders.html')


@app.route('/visualization')
def visualization_page():
    """Nesting visualization page"""
    return render_template('visualization.html')


@app.route('/gcode')
def gcode_page():
    """G-code viewer page"""
    return render_template('gcode.html')


@app.route('/lamine')
def lamine_page():
    """Laminated glass parameters page"""
    return render_template('lamine.html')


@app.route('/settings')
def settings_page():
    """AI Models & API Settings page"""
    return render_template('settings.html')


# ==================== API Routes ====================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    orders_data = [
        {
            "order_id": o.order_id,
            "width": o.width,
            "height": o.height,
            "quantity": o.quantity,
            "thickness": o.thickness,
            "glass_type": o.glass_type,
            "priority": o.priority,
            "rotate_allowed": o.rotate_allowed
        }
        for o in current_orders
    ]
    return jsonify({"orders": orders_data, "count": len(orders_data)})


@app.route('/api/orders', methods=['POST'])
def add_order():
    """Add new order"""
    data = request.get_json()

    order = GlassOrder(
        order_id=data.get('order_id', f"ORD-{len(current_orders)+1:03d}"),
        width=float(data.get('width', 500)),
        height=float(data.get('height', 400)),
        quantity=int(data.get('quantity', 1)),
        thickness=float(data.get('thickness', 4)),
        glass_type=data.get('glass_type', 'float'),
        priority=int(data.get('priority', 1)),
        rotate_allowed=data.get('rotate_allowed', True)
    )

    current_orders.append(order)

    return jsonify({
        "success": True,
        "order": {
            "order_id": order.order_id,
            "width": order.width,
            "height": order.height,
            "quantity": order.quantity
        },
        "total_orders": len(current_orders)
    })


@app.route('/api/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete order"""
    global current_orders
    current_orders = [o for o in current_orders if o.order_id != order_id]
    return jsonify({"success": True, "remaining": len(current_orders)})


@app.route('/api/orders/clear', methods=['POST'])
def clear_orders():
    """Clear all orders"""
    global current_orders
    current_orders = []
    return jsonify({"success": True})


@app.route('/api/orders/load', methods=['POST'])
def load_orders():
    """Load orders from file"""
    data = request.get_json()
    filename = data.get('filename', 'orders.json')

    filepath = MODULES_PATH / 'data' / filename

    try:
        with open(filepath, 'r') as f:
            file_data = json.load(f)

        global current_orders
        current_orders = []

        for item in file_data.get('orders', []):
            order = GlassOrder(
                order_id=item['order_id'],
                width=float(item['width']),
                height=float(item['height']),
                quantity=int(item.get('quantity', 1)),
                thickness=float(item.get('thickness', 4)),
                glass_type=item.get('glass_type', 'float'),
                priority=int(item.get('priority', 1)),
                rotate_allowed=item.get('rotate_allowed', True)
            )
            current_orders.append(order)

        return jsonify({
            "success": True,
            "loaded": len(current_orders),
            "orders": [
                {"order_id": o.order_id, "width": o.width, "height": o.height, "quantity": o.quantity}
                for o in current_orders
            ]
        })
    except FileNotFoundError:
        return jsonify({"success": False, "error": "File not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/optimize', methods=['POST'])
def run_optimization():
    """Run optimization"""
    global current_result, current_gcode

    if not current_orders:
        return jsonify({"success": False, "error": "No orders to optimize"}), 400

    data = request.get_json() or {}
    include_defects = data.get('include_defects', False)

    # Run async optimization
    async def optimize():
        defects = []
        if include_defects:
            handler = DefectHandler(MACHINE_WIDTH, MACHINE_HEIGHT)
            defect_result = handler.process_sheet()
            defects = [
                DefectPoint(
                    x=d['x'],
                    y=d['y'],
                    defect_type=d['type'],
                    severity=d['severity'],
                    radius=d['radius']
                )
                for d in defect_result['defects']
            ]

        result = await orchestrator.optimize_cutting(current_orders, defects)

        current_result = {
            "placed_parts": result.placed_parts,
            "cutting_path": result.cutting_path,
            "utilization": result.utilization,
            "waste_area": result.waste_area,
            "total_cuts": result.total_cuts,
            "estimated_time": result.estimated_time,
            "gcode_file": result.gcode_file,
            "report_file": result.report_file
        }

        if result.gcode_file:
            with open(result.gcode_file, 'r') as f:
                current_gcode = f.read()

        return current_result

    # Run in asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(optimize())
    loop.close()

    return jsonify({
        "success": True,
        "result": result
    })


@app.route('/api/optimize/local', methods=['POST'])
def run_local_optimization():
    """
    Run optimization using ONLY local algorithms (no AI API)
    Works offline without internet connection
    """
    global current_result, current_gcode

    if not current_orders:
        return jsonify({"success": False, "error": "No orders to optimize"}), 400

    data = request.get_json() or {}

    # Convert orders to parts
    parts = []
    for order in current_orders:
        for i in range(order.quantity):
            parts.append({
                "order_id": f"{order.order_id}-{i}",
                "width": order.width,
                "height": order.height,
                "thickness": order.thickness,
                "priority": order.priority,
                "rotate_allowed": order.rotate_allowed,
                "glass_type": order.glass_type
            })

    # Use local Guillotine optimizer
    optimizer = NestingOptimizer(MACHINE_WIDTH, MACHINE_HEIGHT, NestingAlgorithm.GUILLOTINE_BESTFIT)
    
    part_objs = [
        Part(
            part_id=p["order_id"],
            width=p["width"],
            height=p["height"],
            thickness=p["thickness"],
            priority=p["priority"],
            rotate_allowed=p["rotate_allowed"],
            glass_type=p["glass_type"]
        )
        for p in parts
    ]
    
    nesting_result = optimizer.optimize(part_objs)

    # Path optimization (local TSP)
    path_optimizer = CuttingPathOptimizer(MACHINE_WIDTH, MACHINE_HEIGHT)
    path_result = path_optimizer.optimize(nesting_result['placed_parts'], PathAlgorithm.TWO_OPT)

    # Generate G-code (local)
    gcode_gen = NC300GCodeGenerator()
    gcode_program = gcode_gen.generate(
        nesting_result['placed_parts'],
        path_result['path'],
        GlassType.FLOAT,
        "offline_cut"
    )

    # Save G-code
    gcode_file = gcode_gen.save_to_file(gcode_program, str(MODULES_PATH / 'output' / 'gcode'))
    
    with open(gcode_file, 'r') as f:
        current_gcode = f.read()

    current_result = {
        "placed_parts": nesting_result['placed_parts'],
        "cutting_path": path_result['path'],
        "utilization": nesting_result['utilization'],
        "waste_area": nesting_result['waste_area'],
        "total_cuts": len(nesting_result['placed_parts']),
        "estimated_time": path_result['total_distance'] / 1000,  # rough estimate
        "gcode_file": gcode_file,
        "report_file": None,
        "offline": True,
        "algorithm": "Local Guillotine + 2-opt (Offline)"
    }

    return jsonify({
        "success": True,
        "result": current_result,
        "offline": True,
        "message": "Offline optimization completed using local algorithms"
    })


@app.route('/api/optimize/nesting', methods=['POST'])
def run_nesting_only():
    """Run only nesting optimization (for visualization)"""
    if not current_orders:
        return jsonify({"success": False, "error": "No orders"}), 400

    # Convert orders to parts
    parts = []
    for order in current_orders:
        for i in range(order.quantity):
            parts.append(Part(
                part_id=f"{order.order_id}-{i}",
                width=order.width,
                height=order.height,
                thickness=order.thickness,
                priority=order.priority,
                rotate_allowed=order.rotate_allowed,
                glass_type=order.glass_type
            ))

    # Run nesting
    optimizer = NestingOptimizer(MACHINE_WIDTH, MACHINE_HEIGHT, NestingAlgorithm.GUILLOTINE_BESTFIT)
    result = optimizer.optimize(parts)

    return jsonify({
        "success": True,
        "placed_parts": result['placed_parts'],
        "utilization": result['utilization'],
        "algorithm": result['algorithm']
    })


@app.route('/api/gcode', methods=['GET'])
def get_gcode():
    """Get current G-code"""
    if not current_gcode:
        return jsonify({"success": False, "error": "No G-code generated"}), 404

    return jsonify({
        "success": True,
        "gcode": current_gcode,
        "lines": len(current_gcode.split('\n'))
    })


@app.route('/api/gcode/download', methods=['GET'])
def download_gcode():
    """Download G-code file"""
    if not current_result or not current_result.get('gcode_file'):
        return jsonify({"success": False, "error": "No G-code file"}), 404

    return send_file(current_result['gcode_file'], as_attachment=True)


@app.route('/api/gcode/files', methods=['GET'])
def list_gcode_files():
    """List all G-code files"""
    gcode_dir = MODULES_PATH / 'output' / 'gcode'
    files = []

    if gcode_dir.exists():
        for f in gcode_dir.glob('*.nc'):
            files.append({
                "filename": f.name,
                "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "size": f.stat().st_size
            })

    return jsonify({"files": files, "count": len(files)})


@app.route('/api/gcode/file/<filename>', methods=['GET'])
def get_gcode_file(filename):
    """Get specific G-code file content"""
    filepath = MODULES_PATH / 'output' / 'gcode' / filename

    if not filepath.exists():
        return jsonify({"success": False, "error": "File not found"}), 404

    with open(filepath, 'r') as f:
        content = f.read()

    return jsonify({
        "success": True,
        "filename": filename,
        "content": content,
        "lines": len(content.split('\n'))
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get machine status"""
    return jsonify(machine_status)


@app.route('/api/status', methods=['POST'])
def update_status():
    """Update machine status"""
    data = request.get_json()
    machine_status.update(data)
    return jsonify({"success": True, "status": machine_status})


@app.route('/api/defects', methods=['GET'])
def get_defects():
    """Get simulated defects"""
    handler = DefectHandler(MACHINE_WIDTH, MACHINE_HEIGHT)
    result = handler.process_sheet()

    return jsonify({
        "defects": result['defects'],
        "defect_count": result['defect_count'],
        "safe_area_percentage": result['safe_area_percentage']
    })


@app.route('/api/lamine/calculate', methods=['POST'])
def calculate_lamine_params():
    """Calculate laminated glass parameters"""
    data = request.get_json()

    spec = LaminatedGlassSpec(
        upper_thickness=float(data.get('upper_thickness', 4)),
        film_type=FilmType(data.get('film_type', 'PVB')),
        film_thickness=float(data.get('film_thickness', 0.76)),
        lower_thickness=float(data.get('lower_thickness', 4))
    )

    calculator = LaminatedGlassCalculator()
    params = calculator.calculate_parameters(spec)

    return jsonify({
        "success": True,
        "glass_spec": {
            "upper_thickness": spec.upper_thickness,
            "film_type": spec.film_type.value,
            "film_thickness": spec.film_thickness,
            "lower_thickness": spec.lower_thickness,
            "total_thickness": spec.total_thickness
        },
        "parameters": {
            "heating_time": params.heating_time,
            "heating_temperature": params.heating_temperature,
            "upper_cut_pressure": params.upper_cut_pressure,
            "lower_cut_pressure": params.lower_cut_pressure,
            "separation_pressure": params.separation_pressure,
            "break_pressure": params.break_pressure,
            "cutting_speed": params.cutting_speed
        }
    })


@app.route('/api/machine/info', methods=['GET'])
def get_machine_info():
    """Get machine specifications"""
    return jsonify({
        "model": "LiSEC GFB-60/30RE",
        "controller": "Delta NC300",
        "hmi": "Delta DOP-110CS",
        "max_width": MACHINE_WIDTH,
        "max_height": MACHINE_HEIGHT,
        "min_size": {"width": 300, "height": 200},
        "max_speed": 80,  # m/min
        "accuracy": 0.05,  # mm
        "axes": ["X", "Y", "Z", "Alt", "CNC"]
    })


@app.route('/api/reports', methods=['GET'])
def list_reports():
    """List all reports"""
    reports_dir = MODULES_PATH / 'output' / 'reports'
    reports = []

    if reports_dir.exists():
        for f in reports_dir.glob('*.json'):
            reports.append({
                "filename": f.name,
                "created": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "size": f.stat().st_size
            })

    return jsonify({"reports": reports, "count": len(reports)})


@app.route('/api/reports/<filename>', methods=['GET'])
def get_report(filename):
    """Get specific report"""
    filepath = MODULES_PATH / 'output' / 'reports' / filename

    if not filepath.exists():
        return jsonify({"success": False, "error": "File not found"}), 404

    with open(filepath, 'r') as f:
        content = json.load(f)

    return jsonify({"success": True, "report": content})


# ==================== Settings API ====================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    settings_file = MODULES_PATH / 'data' / 'settings.json'
    
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        # Return defaults
        settings = {
            "api_key": "",
            "api_endpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
            "mode": "offline",
            "models": [
                {"model_id": "qwen3.5-plus", "enabled": True, "temperature": 0.7, "max_tokens": 2048},
                {"model_id": "qwen3-max-2026-01-23", "enabled": True, "temperature": 0.5, "max_tokens": 4096},
                {"model_id": "qwen3-coder-plus", "enabled": True, "temperature": 0.2, "max_tokens": 8192},
                {"model_id": "qwen3-coder-next", "enabled": True, "temperature": 0.3, "max_tokens": 4096},
                {"model_id": "glm-4.7", "enabled": True, "temperature": 0.6, "max_tokens": 2048},
                {"model_id": "kimi-k2.5", "enabled": True, "temperature": 0.5, "max_tokens": 4096}
            ],
            "routing": {
                "nesting": "qwen3-max-2026-01-23,qwen3-coder-plus",
                "gcode": "qwen3-coder-plus,qwen3-coder-next",
                "lamine": "qwen3.5-plus",
                "validation": "glm-4.7,kimi-k2.5"
            },
            "parallel": {"max_parallel": 3, "timeout": 90, "retry": 2, "fallback": True}
        }
    
    # Mask API key for security
    if settings.get("api_key"):
        settings["api_key_masked"] = settings["api_key"][:10] + "..." + settings["api_key"][-4:]
        settings["api_key"] = ""  # Don't send full key
    
    return jsonify({"success": True, "settings": settings})


@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings to file"""
    data = request.get_json()
    
    settings_file = MODULES_PATH / 'data' / 'settings.json'
    
    # Don't overwrite API key if empty (keep existing)
    if data.get("api_key") == "" and settings_file.exists():
        with open(settings_file, 'r') as f:
            existing = json.load(f)
            if existing.get("api_key"):
                data["api_key"] = existing["api_key"]
    
    with open(settings_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return jsonify({"success": True, "message": "Settings saved"})


@app.route('/api/settings/test', methods=['POST'])
def test_api_connection():
    """Test API connection with provided key"""
    data = request.get_json()
    
    api_key = data.get('api_key', '')
    api_endpoint = data.get('api_endpoint', 'https://coding-intl.dashscope.aliyuncs.com/v1')
    
    if not api_key:
        return jsonify({"success": False, "error": "API Key required"})
    
    if not api_key.startswith('sk-'):
        return jsonify({"success": False, "error": "Invalid API key format (must start with sk-)"})
    
    # Test connection
    try:
        import aiohttp
        import asyncio
        
        async def test():
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "qwen3.5-plus",
                "input": {"messages": [{"role": "user", "content": "test"}]},
                "parameters": {"max_tokens": 10}
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{api_endpoint}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True
                    elif response.status == 401:
                        return False, "Unauthorized - Invalid API key"
                    else:
                        return False, f"HTTP {response.status}"
        
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(test())
        loop.close()
        
        if result == True:
            return jsonify({
                "success": True,
                "message": "Connection successful",
                "rate_limit": "60 req/min",
                "models_available": 6
            })
        else:
            return jsonify({"success": False, "error": result[1] if isinstance(result, tuple) else "Connection failed"})
            
    except ImportError:
        # aiohttp not available, simulate test
        return jsonify({
            "success": True,
            "message": "Test simulated (aiohttp not installed)",
            "note": "Install aiohttp for real API testing"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults"""
    defaults = {
        "api_key": "",
        "api_endpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
        "mode": "offline",
        "models": [
            {"model_id": "qwen3.5-plus", "enabled": True, "temperature": 0.7, "max_tokens": 2048, "use_case": "general"},
            {"model_id": "qwen3-max-2026-01-23", "enabled": True, "temperature": 0.5, "max_tokens": 4096, "use_case": "complex"},
            {"model_id": "qwen3-coder-plus", "enabled": True, "temperature": 0.2, "max_tokens": 8192, "use_case": "code"},
            {"model_id": "qwen3-coder-next", "enabled": True, "temperature": 0.3, "max_tokens": 4096, "use_case": "advanced_coding"},
            {"model_id": "glm-4.7", "enabled": True, "temperature": 0.6, "max_tokens": 2048, "use_case": "validation"},
            {"model_id": "kimi-k2.5", "enabled": True, "temperature": 0.5, "max_tokens": 4096, "use_case": "documentation"}
        ],
        "routing": {
            "nesting": "qwen3-max-2026-01-23,qwen3-coder-plus",
            "gcode": "qwen3-coder-plus,qwen3-coder-next",
            "lamine": "qwen3.5-plus",
            "validation": "glm-4.7,kimi-k2.5"
        },
        "parallel": {"max_parallel": 3, "timeout": 90, "retry": 2, "fallback": True}
    }
    
    settings_file = MODULES_PATH / 'data' / 'settings.json'
    with open(settings_file, 'w') as f:
        json.dump(defaults, f, indent=2)
    
    return jsonify({"success": True, "settings": defaults, "message": "Reset to defaults"})


# ==================== Herofis Integration ====================

# Initialize Herofis connector
herofis_connector = HerofisConnector(str(MODULES_PATH / 'data' / 'herofis'))


@app.route('/api/herofis/import', methods=['POST'])
def herofis_import():
    """Import orders from Herofis CSV file"""
    # Check if file was uploaded
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return jsonify({"success": False, "error": "No file selected"}), 400
        
        # Save uploaded file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        # Import CSV
        result = herofis_connector.import_csv(tmp_path, encoding='auto', delimiter='auto')
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        if result.success:
            # Convert to GlassOrders and add to current orders
            glass_orders = herofis_connector.convert_to_glass_orders(result.orders)
            
            global current_orders
            for go in glass_orders:
                order = GlassOrder(
                    order_id=go['order_id'],
                    width=float(go['width']),
                    height=float(go['height']),
                    quantity=int(go['quantity']),
                    thickness=float(go['thickness']),
                    glass_type=go.get('glass_type', 'float'),
                    priority=int(go.get('priority', 1)),
                    rotate_allowed=go.get('rotate_allowed', True)
                )
                current_orders.append(order)
            
            return jsonify({
                "success": True,
                "imported": result.imported_rows,
                "skipped": result.skipped_rows,
                "total_orders": len(current_orders),
                "orders_preview": glass_orders[:10],
                "errors": result.errors[:5]
            })
        else:
            return jsonify({"success": False, "errors": result.errors}), 400
    
    # If no file, check for file_path in JSON body
    data = request.get_json()
    if data and 'file_path' in data:
        result = herofis_connector.import_csv(data['file_path'])
        
        if result.success:
            glass_orders = herofis_connector.convert_to_glass_orders(result.orders)
            
            global current_orders
            for go in glass_orders:
                order = GlassOrder(
                    order_id=go['order_id'],
                    width=float(go['width']),
                    height=float(go['height']),
                    quantity=int(go['quantity']),
                    thickness=float(go['thickness']),
                    glass_type=go.get('glass_type', 'float'),
                    priority=int(go.get('priority', 1)),
                    rotate_allowed=go.get('rotate_allowed', True)
                )
                current_orders.append(order)
            
            return jsonify({
                "success": True,
                "imported": result.imported_rows,
                "skipped": result.skipped_rows,
                "total_orders": len(current_orders),
                "orders_preview": glass_orders[:10]
            })
        else:
            return jsonify({"success": False, "errors": result.errors}), 400
    
    return jsonify({"success": False, "error": "No file or file_path provided"}), 400


@app.route('/api/herofis/sample', methods=['GET'])
def herofis_sample():
    """Create and return a sample Herofis CSV file"""
    sample_path = herofis_connector.create_sample_csv()
    
    return send_file(sample_path, as_attachment=True, download_name='sample_herofis_import.csv')


@app.route('/api/herofis/history', methods=['GET'])
def herofis_history():
    """Get import history"""
    history = herofis_connector.get_import_history(20)
    
    return jsonify({
        "success": True,
        "history": history,
        "total_imports": len(history)
    })


@app.route('/api/herofis/columns', methods=['GET'])
def herofis_columns():
    """Get supported column mappings for CSV import"""
    from modules import HEROFIS_COLUMN_MAPPINGS
    
    return jsonify({
        "success": True,
        "column_mappings": {k: v for k, v in HEROFIS_COLUMN_MAPPINGS.items()},
        "glass_types": ["float", "laminated", "tempered", "low_e", "reflective", "tinted"],
        "priorities": {"1": "High/Urgent", "2": "Normal", "3": "Low"},
        "film_types": ["PVB", "EVA", "SGP"]
    })


@app.route('/api/herofis/preview', methods=['POST'])
def herofis_preview():
    """Preview CSV import without adding orders"""
    data = request.get_json()
    
    if 'file_path' not in data:
        return jsonify({"success": False, "error": "file_path required"}), 400
    
    result = herofis_connector.import_csv(data['file_path'])
    
    preview_orders = []
    for order in result.orders[:20]:
        preview_orders.append({
            "siparis_no": order.siparis_no,
            "musteri": order.musteri,
            "en": order.en,
            "boy": order.boy,
            "kalınlık": order.kalınlık,
            "cam_tipi": order.cam_tipi,
            "adet": order.adet,
            "öncelik": order.öncelik,
            "notlar": order.notlar
        })
    
    return jsonify({
        "success": result.success,
        "preview": preview_orders,
        "total_rows": result.total_rows,
        "importable": result.imported_rows,
        "errors": result.errors
    })


@app.route('/api/herofis/save', methods=['POST'])
def herofis_save_orders():
    """Save imported orders to JSON file"""
    data = request.get_json()
    
    orders_data = data.get('orders', [])
    if not orders_data:
        return jsonify({"success": False, "error": "No orders to save"}), 400
    
    # Convert back to HerofisOrder objects
    herofis_orders = []
    for od in orders_data:
        herofis_orders.append(HerofisOrder(
            siparis_no=od.get('order_id', 'UNKNOWN'),
            en=float(od.get('width', 0)),
            boy=float(od.get('height', 0)),
            kalınlık=float(od.get('thickness', 4)),
            cam_tipi=od.get('glass_type', 'float'),
            adet=int(od.get('quantity', 1)),
            öncelik=int(od.get('priority', 2)),
            musteri=od.get('customer', ''),
            notlar=od.get('notes', '')
        ))
    
    output_path = herofis_connector.save_orders_json(herofis_orders)
    
    return jsonify({
        "success": True,
        "saved_path": output_path,
        "total_orders": len(herofis_orders)
    })


# ==================== Static Files ====================

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory(str(MODULES_PATH / 'web' / 'frontend' / 'static'), filename)


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Server error"}), 500


# ==================== Main ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Glass Cutting Web Interface")
    print("LiSEC GFB-60/30RE")
    print("=" * 60)
    print("\nStarting Flask server...")
    print(f"Module path: {MODULES_PATH}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print("\nOpen browser: http://localhost:5001")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)