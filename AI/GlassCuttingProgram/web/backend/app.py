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
import re
from functools import wraps
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import emit

# Add module path
MODULES_PATH = Path(__file__).parent.parent.parent  # GlassCuttingProgram directory
sys.path.insert(0, str(MODULES_PATH))

from glass_cutting_orchestrator import (
    GlassCuttingOrchestrator,
    GlassOrder,
    DefectPoint
)
from web.backend.backend_services import (
    build_cutting_history,
    build_report_dataset,
    build_report_history,
    load_json_file,
    parse_iso_date,
    persist_imported_shapes,
    save_json_file,
)
from web.backend.integration_api import create_integration_blueprint

from modules import (
    NestingOptimizer, NestingAlgorithm, Part,
    CuttingPathOptimizer, PathAlgorithm,
    NC300GCodeGenerator, GlassType,
    LaminatedGlassCalculator, LaminatedGlassSpec, FilmType,
    DefectHandler, Defect, DefectType,
    HMIInterface, HMIOrderEntry,
    BladeManager, BladeType,
    DXFParser, DXFToShapeConverter,
    AuthManager,
    ReportGenerator, AnalyticsEngine,
    BatchOptimizer, CuttingQueue, GlassSheet, CuttingOrder, OrderPriority,
    WebSocketManager, MachineStatus, MachinePosition, ws_manager, init_socketio,
    HerofisConnector
)
from modules.reports import REPORTLAB_AVAILABLE, OPENPYXL_AVAILABLE

# Create Flask app
app = Flask(__name__,
            template_folder=str(MODULES_PATH / 'web' / 'frontend'),
            static_folder=str(MODULES_PATH / 'web' / 'frontend' / 'static'))

CORS(app)
app.register_blueprint(create_integration_blueprint(MODULES_PATH))

# Initialize SocketIO
socketio = init_socketio(app)

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

# Initialize blade manager
blade_manager = BladeManager(str(MODULES_PATH / 'data' / 'blades'))

# Initialize auth manager
auth_manager = AuthManager(str(MODULES_PATH / 'data' / 'auth'))

# Initialize report generator
report_generator = ReportGenerator(str(MODULES_PATH / 'output' / 'reports'))
analytics_engine = AnalyticsEngine()

# Initialize batch optimizer
batch_optimizer = BatchOptimizer()
cutting_queue = CuttingQueue(str(MODULES_PATH / 'data' / 'queue'))
REPORTS_DIR = MODULES_PATH / 'output' / 'reports'
SETTINGS_FILE = MODULES_PATH / 'data' / 'settings.json'
DXF_IMPORTS_FILE_DIR = MODULES_PATH / 'data'
ORDERS_STATE_FILE = MODULES_PATH / 'data' / 'runtime' / 'current_orders.json'
REPO_ROOT = MODULES_PATH.parent
AGENT_RUNTIME_DIR = REPO_ROOT / 'AI' / 'orchestration' / 'runtime'
AGENT_GOALS_FILE = AGENT_RUNTIME_DIR / 'goals.json'
AGENT_RESULTS_DIR = AGENT_RUNTIME_DIR / 'results'


def _deep_merge_dict(base: Dict, override: Dict) -> Dict:
    """Recursively merge settings dictionaries while preserving defaults."""
    merged = dict(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def _agent_now_iso() -> str:
    return datetime.now().astimezone().isoformat()


def _load_agent_goals() -> Dict[str, Any]:
    AGENT_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    AGENT_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not AGENT_GOALS_FILE.exists():
        AGENT_GOALS_FILE.write_text('{\n  "goals": []\n}\n', encoding='utf-8')

    try:
        return json.loads(AGENT_GOALS_FILE.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        fallback = AGENT_GOALS_FILE.with_suffix('.broken.json')
        AGENT_GOALS_FILE.replace(fallback)
        AGENT_GOALS_FILE.write_text('{\n  "goals": []\n}\n', encoding='utf-8')
        return {"goals": []}


def _save_agent_goals(payload: Dict[str, Any]) -> None:
    AGENT_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    temp_file = AGENT_GOALS_FILE.with_name(f'{AGENT_GOALS_FILE.name}.tmp')
    temp_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp_file.replace(AGENT_GOALS_FILE)


def _load_agent_result(goal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    result_path = goal.get('result_path')
    if not result_path:
        return None

    candidate = Path(result_path)
    if not candidate.exists():
        return None

    try:
        return json.loads(candidate.read_text(encoding='utf-8'))
    except json.JSONDecodeError:
        return None


def _build_agent_goal_response(goal: Dict[str, Any], include_result: bool = False) -> Dict[str, Any]:
    response = dict(goal)
    if include_result:
        response['result'] = _load_agent_result(goal)
    return response


def _agent_summary(goals: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts = {
        'pending': 0,
        'running': 0,
        'done': 0,
        'failed': 0,
    }
    for goal in goals:
        status = goal.get('status', 'pending')
        counts[status] = counts.get(status, 0) + 1

    latest_goal = None
    if goals:
        latest_goal = max(goals, key=lambda item: item.get('updated_at', item.get('created_at', '')))

    return {
        'counts': counts,
        'total': len(goals),
        'latest_goal': latest_goal,
    }


def _infer_glass_type_from_line(line: Dict) -> str:
    """Infer a local glass type from a Herofis payload line."""
    text = " ".join(
        str(part)
        for part in [
            line.get("stockCode", ""),
            line.get("stockName", ""),
            line.get("formulaCode", ""),
            line.get("processCode", ""),
            json.dumps(line.get("glassItems", []), ensure_ascii=False),
        ]
    ).lower()
    if "lamine" in text or "laminated" in text or "pvb" in text or "eva" in text:
        return "laminated"
    if "temper" in text:
        return "tempered"
    return "float"


def _infer_thickness_from_line(line: Dict) -> float:
    """Best-effort thickness inference from stock code or stock name."""
    candidates = [
        str(line.get("stockName") or ""),
        str(line.get("formulaCode") or ""),
        str(line.get("stockCode") or ""),
    ]
    for candidate in candidates:
        matches = re.findall(r"(\d+(?:[.,]\d+)?)", candidate)
        for raw in matches:
            value = float(raw.replace(",", "."))
            if 2 <= value <= 25:
                return value
    return 4.0


def _infer_laminated_details_from_line(line: Dict, thickness: float) -> Dict:
    """Extract film metadata from Herofis payload lines when available."""
    parameter_map = {}
    for item in line.get("parameters", []) or []:
        name = str(item.get("ParameterName") or "").strip()
        value = item.get("ParameterValue")
        if not name:
            continue
        parameter_map.setdefault(name, [])
        if value not in parameter_map[name]:
            parameter_map[name].append(value)

    def _first_value(*keys: str) -> str:
        for key in keys:
            values = parameter_map.get(key) or []
            if values:
                return str(values[0]).strip()
            direct = line.get(key)
            if direct not in (None, ""):
                return str(direct).strip()
        return ""

    film_type = _first_value("FilmType", "filmType", "film_type")
    if not film_type:
        film_text = " ".join(
            str(part)
            for part in [
                line.get("stockName", ""),
                line.get("formulaCode", ""),
                json.dumps(line.get("glassItems", []), ensure_ascii=False),
            ]
        ).upper()
        for candidate in ("PVB", "EVA", "SGP"):
            if candidate in film_text:
                film_type = candidate
                break

    film_thickness_raw = _first_value("FilmThickness", "filmThickness", "film_thickness")
    film_thickness = 0.0
    if film_thickness_raw:
        try:
            film_thickness = float(film_thickness_raw.replace(",", "."))
        except ValueError:
            film_thickness = 0.0

    if film_type and film_thickness <= 0:
        film_thickness = 0.76

    if not film_type and str(_infer_glass_type_from_line(line)).lower() == "laminated":
        film_type = "PVB"
        film_thickness = film_thickness or 0.76

    upper_thickness = lower_thickness = 0.0
    if str(_infer_glass_type_from_line(line)).lower() == "laminated" and thickness > 0:
        interlayer = film_thickness or 0.76
        monolithic = max(0.0, thickness - interlayer)
        upper_thickness = round(monolithic / 2.0, 3)
        lower_thickness = round(monolithic / 2.0, 3)

    return {
        "film_type": film_type,
        "film_thickness": film_thickness,
        "upper_thickness": upper_thickness,
        "lower_thickness": lower_thickness,
        "parameter_map": parameter_map,
    }


def _value_is_truthy(raw_value) -> bool:
    text = str(raw_value).strip().lower()
    return text not in ("", "0", "0.0", "0,0", "false", "hayir", "hayır", "no", "off", "pasif", "none", "null")


def _infer_processing_flags_from_line(line: Dict, parameter_map: Dict) -> Dict:
    """Infer blade delete and trimming flags from Herofis payload fields."""
    line_text = " ".join(
        str(part)
        for part in [
            line.get("lineNote", ""),
            line.get("edgeProcessing", ""),
            line.get("processCode", ""),
            json.dumps(parameter_map, ensure_ascii=False),
        ]
    ).lower()

    blade_delete_keys = (
        "BladeDelete",
        "BladeDeleteEnabled",
        "LamaSil",
        "LamaSilme",
        "LamaSiyirma",
        "LamaSıyırma",
        "BladeWipe",
        "BladeClean",
    )
    trimming_keys = (
        "RoundAmount",
        "RoundType",
        "Trimming",
        "TrimmingEnabled",
        "Rodaj",
        "RodajAktif",
    )

    blade_delete_enabled = any(
        parameter_map.get(key) and any(_value_is_truthy(value) for value in parameter_map.get(key, []))
        for key in blade_delete_keys
    )
    trimming_enabled = any(
        parameter_map.get(key) and any(_value_is_truthy(value) for value in parameter_map.get(key, []))
        for key in trimming_keys
    )

    if not blade_delete_enabled and any(keyword in line_text for keyword in ("lama sil", "lama sıyır", "lama siyir", "blade delete", "blade wipe")):
        blade_delete_enabled = True

    if not trimming_enabled and any(keyword in line_text for keyword in ("rodaj", "trim", "round")):
        trimming_enabled = True

    return {
        "blade_delete_enabled": blade_delete_enabled,
        "trimming_enabled": trimming_enabled,
    }


def _import_live_payload_to_current_orders(payload: Dict) -> List[GlassOrder]:
    """Convert normalized Herofis payload into local order list."""
    imported_orders: List[GlassOrder] = []
    order_no = str(payload.get("order", {}).get("orderNo") or "HERO")
    customer_name = str(payload.get("order", {}).get("customerName") or "")
    for line in payload.get("lines", []):
        thickness = _infer_thickness_from_line(line)
        glass_type = _infer_glass_type_from_line(line)
        lamine_meta = _infer_laminated_details_from_line(line, thickness)
        parameter_map = lamine_meta["parameter_map"]
        process_flags = _infer_processing_flags_from_line(line, parameter_map)

        edge_processing = str(line.get("edgeProcessing") or "").strip()
        if not edge_processing:
            if parameter_map.get("RoundAmount") and any(str(value) not in ("0", "0,0", "0.0") for value in parameter_map["RoundAmount"]):
                edge_processing = "rodaj"
            elif parameter_map.get("RoundType") and any(str(value) not in ("0", "0,0", "0.0") for value in parameter_map["RoundType"]):
                edge_processing = "rodaj"

        imported_orders.append(
            GlassOrder(
                order_id=str(line.get("lineId") or f"{order_no}-{line.get('rowNo') or len(imported_orders) + 1}"),
                width=float(line.get("width") or 0),
                height=float(line.get("height") or 0),
                quantity=int(float(line.get("quantity") or 1)),
                thickness=thickness,
                glass_type=glass_type,
                priority=1,
                rotate_allowed=not bool(line.get("isShape")),
                blade_delete_enabled=process_flags["blade_delete_enabled"],
                trimming_enabled=process_flags["trimming_enabled"],
                source_system="herofis",
                source_order_no=order_no,
                customer_name=customer_name,
                edge_processing=edge_processing,
                process_code=str(line.get("processCode") or ""),
                herofis_options={
                    "group_code": line.get("groupCode"),
                    "batch_no": line.get("batchNo"),
                    "package_id": line.get("packageId"),
                    "is_warranty": bool(line.get("isWarranty")),
                    "is_shape": bool(line.get("isShape")),
                    "shape_base_string": line.get("shapeBaseString"),
                    "is_laminated": glass_type == "laminated",
                    "blade_delete_enabled": process_flags["blade_delete_enabled"],
                    "trimming_enabled": process_flags["trimming_enabled"],
                    "line_note": line.get("lineNote"),
                    "single_glass_count": len(line.get("singleGlasses") or []),
                    "parameter_keys": sorted(parameter_map.keys()),
                    "parameters": parameter_map,
                    "upper_thickness": lamine_meta["upper_thickness"],
                    "lower_thickness": lamine_meta["lower_thickness"],
                },
                film_type=lamine_meta["film_type"],
                film_thickness=lamine_meta["film_thickness"],
            )
        )
    return imported_orders


def _serialize_orders(orders: List[GlassOrder]) -> List[Dict]:
    """Convert GlassOrder objects to JSON-serializable dictionaries."""
    return [
        {
            "order_id": order.order_id,
            "width": order.width,
            "height": order.height,
            "quantity": order.quantity,
            "thickness": order.thickness,
            "glass_type": order.glass_type,
            "priority": order.priority,
            "rotate_allowed": order.rotate_allowed,
            "grinding_allowance": order.grinding_allowance,
            "blade_delete_enabled": order.blade_delete_enabled,
            "trimming_enabled": order.trimming_enabled,
            "source_system": order.source_system,
            "source_order_no": order.source_order_no,
            "customer_name": order.customer_name,
            "edge_processing": order.edge_processing,
            "process_code": order.process_code,
            "herofis_options": order.herofis_options,
            "film_type": order.film_type,
            "film_thickness": order.film_thickness,
        }
        for order in orders
    ]


def _deserialize_orders(payload: List[Dict]) -> List[GlassOrder]:
    """Restore GlassOrder objects from persisted JSON."""
    orders: List[GlassOrder] = []
    for item in payload or []:
        orders.append(
            GlassOrder(
                order_id=item["order_id"],
                width=float(item["width"]),
                height=float(item["height"]),
                quantity=int(item.get("quantity", 1)),
                thickness=float(item.get("thickness", 4)),
                glass_type=item.get("glass_type", "float"),
                priority=int(item.get("priority", 1)),
                rotate_allowed=bool(item.get("rotate_allowed", True)),
                grinding_allowance=item.get("grinding_allowance", "none"),
                blade_delete_enabled=bool(item.get("blade_delete_enabled", False)),
                trimming_enabled=bool(item.get("trimming_enabled", False)),
                source_system=item.get("source_system", "manual"),
                source_order_no=item.get("source_order_no", ""),
                customer_name=item.get("customer_name", ""),
                edge_processing=item.get("edge_processing", ""),
                process_code=item.get("process_code", ""),
                herofis_options=item.get("herofis_options", {}) or {},
                film_type=item.get("film_type", ""),
                film_thickness=float(item.get("film_thickness", 0.0) or 0.0),
            )
        )
    return orders


def _persist_current_orders() -> None:
    """Persist the in-memory orders list to disk for stable UI behavior."""
    save_json_file(ORDERS_STATE_FILE, {"orders": _serialize_orders(current_orders)})


def _ensure_current_orders_loaded() -> None:
    """Load persisted orders back into memory if current state is empty."""
    global current_orders
    if current_orders:
        return
    stored = load_json_file(ORDERS_STATE_FILE, {"orders": []})
    current_orders = _deserialize_orders(stored.get("orders", []))


def _get_bearer_token() -> str:
    """Extract bearer token from Authorization header."""
    return request.headers.get('Authorization', '').replace('Bearer ', '').strip()


def _get_authenticated_user() -> Optional[Dict]:
    """Return authenticated user info if the token is valid."""
    token = _get_bearer_token()
    if not token:
        return None
    return auth_manager.verify_token(token)


def require_auth(role: Optional[str] = None):
    """Protect endpoints with authentication and optional role checks."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_info = _get_authenticated_user()
            if not user_info:
                return jsonify({"success": False, "error": "Authentication required"}), 401

            if role and user_info.get('role') != role:
                return jsonify({"success": False, "error": "Insufficient permissions"}), 403

            return func(*args, current_user=user_info, **kwargs)
        return wrapper
    return decorator


# ==================== HTML Routes ====================

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/login')
def login_page():
    """Login page"""
    return render_template('login.html')


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


@app.route('/shapes')
def shapes_page():
    """Shape cutting page"""
    return render_template('shapes.html')


@app.route('/blades')
def blades_page():
    """Blade management page"""
    return render_template('blades.html')


@app.route('/dxf')
def dxf_page():
    """DXF import page"""
    return render_template('dxf.html')


@app.route('/reports')
def reports_page():
    """Reports page"""
    return render_template('reports.html')


@app.route('/batch')
def batch_page():
    """Batch processing page"""
    return render_template('batch.html')


@app.route('/queue')
def queue_page():
    """Cutting queue page"""
    return render_template('queue.html')


@app.route('/agent')
def agent_page():
    """AI agent dashboard page"""
    return render_template('agent.html')


@app.route('/test_api')
def test_api_page():
    """API Test Page for debugging"""
    return send_file(MODULES_PATH / 'web' / 'test_api.html')


# ==================== API Routes ====================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Get all orders"""
    _ensure_current_orders_loaded()
    orders_data = [
        {
            "order_id": o.order_id,
            "width": o.width,
            "height": o.height,
            "quantity": o.quantity,
            "thickness": o.thickness,
            "glass_type": o.glass_type,
            "priority": o.priority,
            "rotate_allowed": o.rotate_allowed,
            "grinding_allowance": o.grinding_allowance,
            "blade_delete_enabled": o.blade_delete_enabled,
            "trimming_enabled": o.trimming_enabled,
            "source_system": o.source_system,
            "source_order_no": o.source_order_no,
            "customer_name": o.customer_name,
            "edge_processing": o.edge_processing,
            "process_code": o.process_code,
            "herofis_options": o.herofis_options,
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
        rotate_allowed=data.get('rotate_allowed', True),
        # Blade management options
        grinding_allowance=data.get('grinding_allowance', 'none'),
        blade_delete_enabled=data.get('blade_delete_enabled', False),
        trimming_enabled=data.get('trimming_enabled', False),
        source_system=data.get('source_system', 'manual'),
        source_order_no=data.get('source_order_no', ''),
        customer_name=data.get('customer_name', ''),
        edge_processing=data.get('edge_processing', ''),
        process_code=data.get('process_code', ''),
        herofis_options=data.get('herofis_options', {}) or {},
    )

    current_orders.append(order)
    _persist_current_orders()

    # Record blade usage if blade delete is enabled
    if order.blade_delete_enabled and blade_manager.get_active_blade():
        # Estimate cut length (perimeter of all parts)
        estimated_cut = (order.width + order.height) * 2 * order.quantity / 1000  # meters
        blade_manager.record_cut(estimated_cut, order.order_id)

    return jsonify({
        "success": True,
        "order": {
            "order_id": order.order_id,
            "width": order.width,
            "height": order.height,
            "quantity": order.quantity,
            "grinding_allowance": order.grinding_allowance,
            "blade_delete_enabled": order.blade_delete_enabled,
            "trimming_enabled": order.trimming_enabled,
            "source_system": order.source_system,
            "source_order_no": order.source_order_no,
            "customer_name": order.customer_name,
            "edge_processing": order.edge_processing,
            "process_code": order.process_code,
            "herofis_options": order.herofis_options,
        },
        "total_orders": len(current_orders)
    })


@app.route('/api/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete order"""
    global current_orders
    _ensure_current_orders_loaded()
    current_orders = [o for o in current_orders if o.order_id != order_id]
    _persist_current_orders()
    return jsonify({"success": True, "remaining": len(current_orders)})


@app.route('/api/orders/clear', methods=['POST'])
def clear_orders():
    """Clear all orders"""
    global current_orders
    current_orders = []
    _persist_current_orders()
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

        _persist_current_orders()

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


@app.route('/api/orders/import-live-herofis', methods=['POST'])
def import_live_herofis_orders():
    """Fetch a live Herofis order and import its lines into the local orders list."""
    data = request.get_json() or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "").strip()
    order_no = str(data.get("orderNo") or "").strip()
    base_url = str(data.get("baseUrl") or "https://herofis.com").strip()
    verify_ssl = bool(data.get("verifySsl", True))
    replace_existing = bool(data.get("replaceExisting", True))

    if not username or not password or not order_no:
        return jsonify({"success": False, "error": "username, password and orderNo are required"}), 400

    connector = HerofisConnector(data_dir=str(MODULES_PATH / "data" / "herofis"))

    try:
        payload = connector.fetch_live_order_payload(
            username=username,
            password=password,
            order_no=order_no,
            base_url=base_url,
            verify_ssl=verify_ssl,
        )
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    imported = _import_live_payload_to_current_orders(payload)

    global current_orders
    if imported:
        if replace_existing:
            current_orders = imported
        else:
            current_orders.extend(imported)
        _persist_current_orders()

    return jsonify(
        {
            "success": True,
            "orderNo": order_no,
            "imported": len(imported),
            "replaceExisting": replace_existing,
            "orders": [
                {
                    "order_id": order.order_id,
                    "width": order.width,
                    "height": order.height,
                    "quantity": order.quantity,
                    "thickness": order.thickness,
                    "glass_type": order.glass_type,
                    "priority": order.priority,
                    "rotate_allowed": order.rotate_allowed,
                    "film_type": order.film_type,
                    "film_thickness": order.film_thickness,
                }
                for order in current_orders
            ],
            "customerName": payload.get("order", {}).get("customerName"),
        }
    )


@app.route('/api/orders/list-latest-herofis', methods=['POST'])
def list_latest_herofis_orders():
    """List latest unproduced Herofis orders before importing."""
    data = request.get_json() or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "").strip()
    base_url = str(data.get("baseUrl") or "https://herofis.com").strip()
    verify_ssl = bool(data.get("verifySsl", True))
    limit = max(1, min(int(data.get("limit", 20) or 20), 50))
    production_status_threshold = int(data.get("productionStatusThreshold", 20) or 20)
    exclude_status_ids = data.get("excludeStatusIds") or [19]

    if not username or not password:
        return jsonify({"success": False, "error": "username and password are required"}), 400

    connector = HerofisConnector(data_dir=str(MODULES_PATH / "data" / "herofis"))
    _ensure_current_orders_loaded()
    imported_order_nos = {
        str(order.source_order_no or "").strip()
        for order in current_orders
        if str(order.source_system).lower() == "herofis" and str(order.source_order_no or "").strip()
    }

    try:
        recent_orders = connector.list_live_recent_orders(
            username=username,
            password=password,
            base_url=base_url,
            verify_ssl=verify_ssl,
            limit=limit,
            unproduced_only=True,
            production_status_threshold=production_status_threshold,
            exclude_status_ids=exclude_status_ids,
            max_pages=10,
        )
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 400

    return jsonify(
        {
            "success": True,
            "orders": [
                {
                    **item,
                    "alreadyImported": item.get("orderNo") in imported_order_nos,
                }
                for item in recent_orders
            ],
            "count": len(recent_orders),
        }
    )


@app.route('/api/orders/import-latest-herofis', methods=['POST'])
def import_latest_herofis_orders():
    """Fetch the latest unproduced Herofis orders and import them locally."""
    data = request.get_json() or {}
    username = str(data.get("username") or "").strip()
    password = str(data.get("password") or "").strip()
    base_url = str(data.get("baseUrl") or "https://herofis.com").strip()
    verify_ssl = bool(data.get("verifySsl", True))
    replace_existing = bool(data.get("replaceExisting", True))
    limit = max(1, min(int(data.get("limit", 10) or 10), 25))
    production_status_threshold = int(data.get("productionStatusThreshold", 20) or 20)
    exclude_status_ids = data.get("excludeStatusIds") or [19]
    selected_order_nos = [
        str(item).strip()
        for item in (data.get("orderNos") or [])
        if str(item).strip()
    ]

    if not username or not password:
        return jsonify({"success": False, "error": "username and password are required"}), 400

    connector = HerofisConnector(data_dir=str(MODULES_PATH / "data" / "herofis"))

    if selected_order_nos:
        recent_orders = [{"orderNo": order_no} for order_no in selected_order_nos]
    else:
        try:
            recent_orders = connector.list_live_recent_orders(
                username=username,
                password=password,
                base_url=base_url,
                verify_ssl=verify_ssl,
                limit=limit,
                unproduced_only=True,
                production_status_threshold=production_status_threshold,
                exclude_status_ids=exclude_status_ids,
                max_pages=10,
            )
        except Exception as exc:
            return jsonify({"success": False, "error": str(exc)}), 400

    imported: List[GlassOrder] = []
    imported_order_refs: List[Dict] = []
    errors: List[str] = []

    for item in recent_orders:
        order_no = str(item.get("orderNo") or "").strip()
        if not order_no:
            continue
        try:
            payload = connector.fetch_live_order_payload(
                username=username,
                password=password,
                order_no=order_no,
                base_url=base_url,
                verify_ssl=verify_ssl,
            )
            order_lines = _import_live_payload_to_current_orders(payload)
            imported.extend(order_lines)
            imported_order_refs.append(
                {
                    "orderNo": order_no,
                    "customerName": item.get("customerName") or "",
                    "status": item.get("status") or "",
                    "statusId": item.get("statusId"),
                    "lineCount": len(order_lines),
                }
            )
        except Exception as exc:
            errors.append(f"{order_no}: {exc}")

    global current_orders
    if replace_existing:
        current_orders = imported
    else:
        current_orders.extend(imported)
    _persist_current_orders()

    return jsonify(
        {
            "success": True,
            "requestedLimit": limit,
            "matchedOrders": len(recent_orders),
            "importedOrders": len(imported_order_refs),
            "importedLines": len(imported),
            "replaceExisting": replace_existing,
            "sourceOrders": imported_order_refs,
            "errors": errors,
            "orders": [
                {
                    "order_id": order.order_id,
                    "width": order.width,
                    "height": order.height,
                    "quantity": order.quantity,
                    "thickness": order.thickness,
                    "glass_type": order.glass_type,
                    "priority": order.priority,
                    "rotate_allowed": order.rotate_allowed,
                    "film_type": order.film_type,
                    "film_thickness": order.film_thickness,
                    "source_order_no": order.source_order_no,
                    "customer_name": order.customer_name,
                }
                for order in (imported if replace_existing else current_orders)
            ],
        }
    )


@app.route('/api/optimize', methods=['POST'])
def run_optimization():
    """Run optimization"""
    global current_result, current_gcode
    _ensure_current_orders_loaded()

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
    _ensure_current_orders_loaded()

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
    detected_glass_type = GlassType.FLOAT
    if any(order.glass_type == GlassType.LAMINATED.value for order in current_orders):
        detected_glass_type = GlassType.LAMINATED
    elif any(order.glass_type == GlassType.TEMPERED.value for order in current_orders):
        detected_glass_type = GlassType.TEMPERED

    gcode_gen = NC300GCodeGenerator()
    gcode_program = gcode_gen.generate(
        nesting_result['placed_parts'],
        path_result['path'],
        detected_glass_type,
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
        "glass_type": detected_glass_type.value,
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
    _ensure_current_orders_loaded()
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
    defaults = {
        "api_key": "",
        "api_endpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
        "mode": "offline",
        "models": [
            {"model_id": "qwen3.5-plus", "enabled": True, "temperature": 0.7, "max_tokens": 2048},
            {"model_id": "qwen3-max-2026-01-23", "enabled": True, "temperature": 0.5, "max_tokens": 4096},
            {"model_id": "qwen3-coder-plus", "enabled": True, "temperature": 0.2, "max_tokens": 8192},
            {"model_id": "qwen3-coder-next", "enabled": True, "temperature": 0.3, "max_tokens": 4096},
            {"model_id": "glm-5", "enabled": True, "temperature": 0.4, "max_tokens": 4096},
            {"model_id": "kimi-k2.5", "enabled": True, "temperature": 0.5, "max_tokens": 4096},
            {"model_id": "MiniMax-M2.5", "enabled": True, "temperature": 0.5, "max_tokens": 4096}
        ],
        "routing": {
            "nesting": "qwen3-max-2026-01-23,qwen3-coder-plus",
            "gcode": "qwen3-coder-plus,qwen3-coder-next",
            "lamine": "qwen3.5-plus",
            "validation": "glm-5,MiniMax-M2.5",
            "documentation": "kimi-k2.5,qwen3.5-plus",
            "review": "glm-5,MiniMax-M2.5"
        },
        "integration": {
            "herofis_base_url": "https://herofis.com",
            "herofis_username": "",
            "herofis_password": "",
            "verify_ssl": False,
            "default_target_status_id": 20,
            "test_order_no": "",
            "status_override": ""
        },
        "parallel": {"max_parallel": 3, "timeout": 90, "retry": 2, "fallback": True}
    }
    settings = _deep_merge_dict(defaults, load_json_file(SETTINGS_FILE, {}))
    
    # Mask API key for security
    if settings.get("api_key"):
        settings["api_key_masked"] = settings["api_key"][:10] + "..." + settings["api_key"][-4:]
        settings["api_key"] = ""  # Don't send full key
    
    return jsonify({"success": True, "settings": settings})


@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings to file"""
    data = request.get_json()

    # Don't overwrite API key if empty (keep existing)
    if data.get("api_key") == "" and SETTINGS_FILE.exists():
        existing = load_json_file(SETTINGS_FILE, {})
        if existing.get("api_key"):
            data["api_key"] = existing["api_key"]

    save_json_file(SETTINGS_FILE, data)
    
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
                "models_available": 7
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
            {"model_id": "glm-5", "enabled": True, "temperature": 0.4, "max_tokens": 4096, "use_case": "validation"},
            {"model_id": "kimi-k2.5", "enabled": True, "temperature": 0.5, "max_tokens": 4096, "use_case": "documentation"},
            {"model_id": "MiniMax-M2.5", "enabled": True, "temperature": 0.5, "max_tokens": 4096, "use_case": "alternate"}
        ],
        "routing": {
            "nesting": "qwen3-max-2026-01-23,qwen3-coder-plus",
            "gcode": "qwen3-coder-plus,qwen3-coder-next",
            "lamine": "qwen3.5-plus",
            "validation": "glm-5,MiniMax-M2.5",
            "documentation": "kimi-k2.5,qwen3.5-plus",
            "review": "glm-5,MiniMax-M2.5"
        },
        "integration": {
            "herofis_base_url": "https://herofis.com",
            "herofis_username": "",
            "herofis_password": "",
            "verify_ssl": False,
            "default_target_status_id": 20,
            "test_order_no": "",
            "status_override": ""
        },
        "parallel": {"max_parallel": 3, "timeout": 90, "retry": 2, "fallback": True}
    }

    save_json_file(SETTINGS_FILE, defaults)
    
    return jsonify({"success": True, "settings": defaults, "message": "Reset to defaults"})


# ==================== Blade Management API ====================

@app.route('/api/blades', methods=['GET'])
def get_blades():
    """Get all blades"""
    blades = {bid: b.to_dict() for bid, b in blade_manager.blades.items()}
    active = blade_manager.get_active_blade()
    alerts = blade_manager.get_blade_alerts()
    stats = blade_manager.get_statistics()
    
    return jsonify({
        "success": True,
        "blades": blades,
        "active_blade": active.to_dict() if active else None,
        "active_blade_id": blade_manager.active_blade_id,
        "alerts": alerts,
        "statistics": stats
    })


@app.route('/api/blades/install', methods=['POST'])
def install_blade():
    """Install new blade"""
    data = request.get_json()
    
    blade = blade_manager.install_blade(
        blade_id=data.get('blade_id', f'BLADE-{len(blade_manager.blades)+1:03d}'),
        blade_type=BladeType(data.get('blade_type', 'standard')),
        total_life=float(data.get('total_life', 5000)),
        spin_interval=float(data.get('spin_interval', 1000))
    )
    
    return jsonify({
        "success": True,
        "blade": blade.to_dict(),
        "message": "Bıçak takıldı"
    })


@app.route('/api/blades/spin', methods=['POST'])
def spin_blade():
    """Spin active blade"""
    success = blade_manager.spin_active_blade()
    
    if success:
        return jsonify({
            "success": True,
            "message": "Bıçak döndürüldü"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Bıçak döndürmeye hazır değil"
        }), 400


@app.route('/api/blades/replace', methods=['POST'])
def replace_blade():
    """Replace active blade"""
    data = request.get_json()
    
    blade = blade_manager.replace_blade(
        new_blade_id=data.get('new_blade_id'),
        blade_type=BladeType(data.get('blade_type', 'standard'))
    )
    
    return jsonify({
        "success": True,
        "blade": blade.to_dict(),
        "message": "Bıçak değiştirildi"
    })


@app.route('/api/blades/grinding/calculate', methods=['POST'])
def calculate_grinding():
    """Calculate dimensions with grinding allowance"""
    data = request.get_json()
    
    result = blade_manager.calculate_with_grinding(
        width=float(data.get('width', 0)),
        height=float(data.get('height', 0)),
        allowance_type=data.get('allowance_type', 'none')
    )
    
    return jsonify({
        "success": True,
        "result": result
    })


@app.route('/api/blades/grinding/allowances', methods=['GET'])
def get_grinding_allowances():
    """Get available grinding allowances"""
    allowances = {
        key: {
            "type": v.allowance_type,
            "x_allowance": v.x_allowance,
            "y_allowance": v.y_allowance,
            "total_x": v.total_x_addition,
            "total_y": v.total_y_addition,
            "description": v.description
        }
        for key, v in blade_manager.GRINDING_ALLOWANCES.items()
    }
    
    return jsonify({
        "success": True,
        "allowances": allowances
    })


# ==================== Authentication API ====================

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """User login"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "Invalid request"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    
    # Authenticate
    result = auth_manager.authenticate(username, password)
    
    if result:
        return jsonify({
            "success": True,
            "access_token": result['access_token'],
            "refresh_token": result['refresh_token'],
            "user": result['user']
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid username or password"
        }), 401


@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """User logout"""
    token = _get_bearer_token()
    
    if token:
        auth_manager.logout(token)
    
    return jsonify({"success": True, "message": "Logged out"})


@app.route('/api/auth/register', methods=['POST'])
@require_auth(role='admin')
def api_register(current_user: Dict):
    """Register new user (admin only)"""
    data = request.get_json()
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    role = data.get('role', 'operator')
    
    if not username or not password:
        return jsonify({"success": False, "error": "Username and password required"}), 400
    
    user = auth_manager.create_user(username, password, email, role)
    
    if user:
        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "message": "User created"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Username already exists"
        }), 400


@app.route('/api/auth/me', methods=['GET'])
def api_get_current_user():
    """Get current user info"""
    token = _get_bearer_token()
    
    if not token:
        return jsonify({"success": False, "error": "No token provided"}), 401
    
    user_info = auth_manager.verify_token(token)
    
    if user_info:
        return jsonify({
            "success": True,
            "user": user_info
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid or expired token"
        }), 401


@app.route('/api/auth/refresh', methods=['POST'])
def api_refresh_token():
    """Refresh access token"""
    data = request.get_json()
    refresh_token = data.get('refresh_token')
    
    if not refresh_token:
        return jsonify({"success": False, "error": "Refresh token required"}), 400
    
    result = auth_manager.refresh_access_token(refresh_token)
    
    if result:
        return jsonify({
            "success": True,
            "access_token": result['access_token'],
            "expires_in": result['expires_in']
        })
    else:
        return jsonify({
            "success": False,
            "error": "Invalid refresh token"
        }), 401


@app.route('/api/auth/users', methods=['GET'])
@require_auth(role='admin')
def api_get_users(current_user: Dict):
    """Get all users (admin only)"""
    users = [auth_manager.get_user(uid).to_dict() for uid in auth_manager.users.keys()]
    
    return jsonify({
        "success": True,
        "users": users,
        "total": len(users)
    })


@app.route('/api/auth/statistics', methods=['GET'])
@require_auth(role='admin')
def api_auth_statistics(current_user: Dict):
    """Get authentication statistics"""
    stats = auth_manager.get_statistics()
    
    return jsonify({
        "success": True,
        "statistics": stats
    })


# ==================== DXF Import API ====================

@app.route('/api/dxf/parse', methods=['POST'])
def parse_dxf():
    """Parse DXF file"""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Dosya yok"}), 400
    
    file = request.files['file']
    units = request.form.get('units', 'mm')
    scale = float(request.form.get('scale', 1.0))
    
    # Save file temporarily
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        # Parse DXF
        parser = DXFParser(scale=scale, units=units)
        result = parser.parse(tmp_path)
        
        if result.success:
            # Convert shapes to serializable format
            shapes = []
            for shape in result.shapes:
                shapes.append({
                    'shape_id': shape.shape_id,
                    'shape_type': shape.shape_type,
                    'layer': shape.layer,
                    'points': shape.points,
                    'parameters': shape.parameters,
                    'bounding_box': shape.bounding_box,
                    'perimeter': shape.perimeter
                })
            
            return jsonify({
                "success": True,
                "shapes": shapes,
                "total_shapes": result.total_shapes,
                "layers": result.layers,
                "file_info": result.file_info,
                "errors": result.errors
            })
        else:
            return jsonify({
                "success": False,
                "error": "Parse başarısız",
                "errors": result.errors
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
    finally:
        # Clean up temp file
        import os
        os.unlink(tmp_path)


@app.route('/api/dxf/import', methods=['POST'])
def import_dxf_shapes():
    """Import DXF shapes to program"""
    data = request.get_json()
    
    shapes = data.get('shapes', [])
    placement = data.get('placement', 'manual')
    offset_x = data.get('offset_x', 100)
    offset_y = data.get('offset_y', 100)
    grinding = data.get('grinding_allowance', 'none')
    
    # Convert DXF shapes to program shapes
    converter = DXFToShapeConverter()
    program_shapes = converter.convert(shapes, base_x=offset_x, base_y=offset_y)
    
    # Apply grinding allowance if needed
    if grinding != 'none':
        blade_mgr = BladeManager()
        for shape in program_shapes:
            bbox = shape['bounding_box']
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            
            adjusted = blade_mgr.calculate_with_grinding(width, height, grinding)
            shape['adjusted_dimensions'] = adjusted
    
    import_record = persist_imported_shapes(
        DXF_IMPORTS_FILE_DIR,
        program_shapes,
        {
            "placement": placement,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "grinding_allowance": grinding,
        }
    )
    
    return jsonify({
        "success": True,
        "imported_count": len(program_shapes),
        "shapes": program_shapes,
        "import_record": {
            "imported_at": import_record["imported_at"],
            "count": import_record["count"],
        },
        "message": f"{len(program_shapes)} şekil aktarıldı"
    })


# ==================== Reports API ====================

@app.route('/api/reports/generate', methods=['POST'])
def api_generate_report():
    """Generate report"""
    data = request.get_json()
    
    report_type = data.get('type', 'daily')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    
    sample_data = build_report_dataset(
        REPORTS_DIR,
        parse_iso_date(start_date),
        parse_iso_date(end_date),
    )
    
    if report_type == 'daily':
        from datetime import datetime
        date = datetime.fromisoformat(start_date) if start_date else datetime.now()
        report = report_generator.generate_daily_report(date, sample_data)
    elif report_type == 'weekly':
        from datetime import datetime
        start = datetime.fromisoformat(start_date) if start_date else datetime.now()
        report = report_generator.generate_weekly_report(start, sample_data)
    elif report_type == 'monthly':
        from datetime import datetime
        now = datetime.now()
        report = report_generator.generate_monthly_report(now.year, now.month, sample_data)
    else:
        report = report_generator.generate_daily_report(datetime.now(), sample_data)
    
    return jsonify({
        "success": True,
        "report": {
            "type": report.report_type,
            "title": report.title,
            "summary": report.summary,
            "data": report.data
        }
    })


@app.route('/api/reports/export/<format>', methods=['POST'])
def api_export_report(format):
    """Export report to specified format"""
    data = request.get_json()
    
    report_type = data.get('type', 'daily')
    
    # Generate report
    from datetime import datetime
    sample_data = build_report_dataset(REPORTS_DIR)
    report = report_generator.generate_daily_report(datetime.now(), sample_data)
    
    try:
        if format == 'pdf':
            if not REPORTLAB_AVAILABLE:
                return jsonify({"success": False, "error": "reportlab not installed"}), 400
            filepath = report_generator.export_to_pdf(report)
        elif format == 'excel':
            if not OPENPYXL_AVAILABLE:
                return jsonify({"success": False, "error": "openpyxl not installed"}), 400
            filepath = report_generator.export_to_excel(report)
        elif format == 'json':
            filepath = report_generator.generate_json_report(report)
        else:
            return jsonify({"success": False, "error": "Invalid format"}), 400
        
        return jsonify({
            "success": True,
            "filepath": filepath,
            "download_url": f"/api/reports/download/{Path(filepath).name}"
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/reports/download/<filename>', methods=['GET'])
def api_download_report(filename):
    """Download report file"""
    from flask import send_file
    filepath = MODULES_PATH / 'output' / 'reports' / filename
    
    if filepath.exists():
        return send_file(str(filepath), as_attachment=True)
    else:
        return jsonify({"success": False, "error": "File not found"}), 404


@app.route('/api/analytics/utilization', methods=['GET'])
def api_utilization_analytics():
    """Get utilization analytics"""
    history = build_cutting_history(REPORTS_DIR)
    stats = analytics_engine.calculate_utilization_stats(history)
    
    return jsonify({
        "success": True,
        "statistics": stats,
        "history_count": len(history)
    })


@app.route('/api/analytics/waste', methods=['GET'])
def api_waste_analytics():
    """Get waste analytics"""
    history = build_cutting_history(REPORTS_DIR)
    stats = analytics_engine.calculate_waste_stats(history)
    
    return jsonify({
        "success": True,
        "statistics": stats,
        "history_count": len(history)
    })


@app.route('/api/reports/history', methods=['GET'])
def api_report_history():
    """Return generated report history for the frontend."""
    history = build_report_history(REPORTS_DIR)
    return jsonify({
        "success": True,
        "history": history,
        "total": len(history)
    })


# ==================== Batch Processing API ====================

@app.route('/api/batch/sheets', methods=['GET'])
def api_get_sheets():
    """Get all sheets"""
    sheets = [s.to_dict() for s in batch_optimizer.sheets]
    return jsonify({
        "success": True,
        "sheets": sheets,
        "total": len(sheets)
    })


@app.route('/api/batch/sheets', methods=['POST'])
def api_add_sheet():
    """Add new sheet"""
    data = request.get_json()
    
    sheet = GlassSheet(
        sheet_id=data.get('sheet_id', f'SHEET-{len(batch_optimizer.sheets)+1:03d}'),
        width=float(data.get('width', 6000)),
        height=float(data.get('height', 3000)),
        thickness=float(data.get('thickness', 4)),
        glass_type=data.get('glass_type', 'float'),
        status=SheetStatus.AVAILABLE
    )
    
    batch_optimizer.add_sheet(sheet)
    
    return jsonify({
        "success": True,
        "sheet": sheet.to_dict(),
        "message": "Levha eklendi"
    })


@app.route('/api/batch/orders', methods=['GET'])
def api_get_orders():
    """Get all orders"""
    orders = [o.to_dict() for o in batch_optimizer.orders]
    return jsonify({
        "success": True,
        "orders": orders,
        "total": len(orders)
    })


@app.route('/api/batch/orders', methods=['POST'])
def api_add_order():
    """Add new order"""
    data = request.get_json()
    
    order = CuttingOrder(
        order_id=data.get('order_id', f'ORD-{len(batch_optimizer.orders)+1:03d}'),
        width=float(data.get('width', 500)),
        height=float(data.get('height', 400)),
        quantity=int(data.get('quantity', 1)),
        thickness=float(data.get('thickness', 4)),
        glass_type=data.get('glass_type', 'float'),
        priority=OrderPriority(int(data.get('priority', 2))),
        rotate_allowed=data.get('rotate_allowed', True)
    )
    
    batch_optimizer.add_order(order)
    
    return jsonify({
        "success": True,
        "order": order.to_dict(),
        "message": "Sipariş eklendi"
    })


@app.route('/api/batch/optimize', methods=['POST'])
def api_optimize_batch():
    """Run batch optimization"""
    data = request.get_json()
    
    strategy = data.get('strategy', 'efficiency')
    use_remnants = data.get('use_remnants', True)
    
    jobs = batch_optimizer.optimize_batch(strategy=strategy)
    
    # Add to queue if requested
    if data.get('auto_queue', True):
        for job in jobs:
            cutting_queue.add_job(job)
    
    return jsonify({
        "success": True,
        "jobs": [j.to_dict() for j in jobs],
        "statistics": batch_optimizer.get_statistics(),
        "message": f"{len(jobs)} iş oluşturuldu"
    })


@app.route('/api/batch/statistics', methods=['GET'])
def api_batch_statistics():
    """Get batch statistics"""
    stats = batch_optimizer.get_statistics()
    return jsonify({
        "success": True,
        "statistics": stats
    })


@app.route('/api/queue/status', methods=['GET'])
def api_queue_status():
    """Get queue status"""
    status = cutting_queue.get_queue_status()
    return jsonify({
        "success": True,
        "status": status
    })


@app.route('/api/queue/start', methods=['POST'])
def api_queue_start():
    """Start next job in queue"""
    job = cutting_queue.start_next_job()
    
    if job:
        return jsonify({
            "success": True,
            "job": job.to_dict(),
            "message": f"İş başlatıldı: {job.job_id}"
        })
    else:
        return jsonify({
            "success": False,
            "error": "Kuyruk boş"
        }), 400


@app.route('/api/queue/complete', methods=['POST'])
def api_queue_complete():
    """Complete current job"""
    data = request.get_json()
    actual_time = data.get('actual_time')
    
    cutting_queue.complete_job(actual_time)
    
    return jsonify({
        "success": True,
        "message": "İş tamamlandı"
    })


@app.route('/api/agent/summary', methods=['GET'])
def api_agent_summary():
    """Get AI agent queue summary"""
    payload = _load_agent_goals()
    goals = payload.get('goals', [])
    return jsonify({
        "success": True,
        "summary": _agent_summary(goals),
    })


@app.route('/api/agent/goals', methods=['GET'])
def api_agent_goals():
    """List AI agent goals"""
    payload = _load_agent_goals()
    include_results = request.args.get('include_results', 'false').lower() == 'true'
    goals = [
        _build_agent_goal_response(goal, include_result=include_results)
        for goal in reversed(payload.get('goals', []))
    ]
    return jsonify({
        "success": True,
        "goals": goals,
        "summary": _agent_summary(payload.get('goals', [])),
    })


@app.route('/api/agent/goals', methods=['POST'])
def api_agent_submit_goal():
    """Submit a new AI agent goal"""
    data = request.get_json(silent=True) or {}
    title = str(data.get('title', '')).strip()
    prompt = str(data.get('prompt', '')).strip()
    if not title or not prompt:
        return jsonify({
            "success": False,
            "error": "Başlık ve hedef açıklaması zorunlu",
        }), 400

    goal_type = str(data.get('goal_type', 'ai')).strip() or 'ai'
    if goal_type not in ('ai', 'simulator_check'):
        return jsonify({"success": False, "error": "Geçersiz hedef tipi"}), 400

    mode = str(data.get('mode', 'parallel')).strip() or 'parallel'
    if mode not in ('single', 'parallel', 'voting', 'aggregate'):
        return jsonify({"success": False, "error": "Geçersiz çalışma modu"}), 400

    payload = _load_agent_goals()
    goals = payload.setdefault('goals', [])
    goal_id = f"web-{int(datetime.now().timestamp())}"
    while any(goal.get('id') == goal_id for goal in goals):
        goal_id = f"{goal_id}-x"

    goal = {
        "id": goal_id,
        "title": title,
        "prompt": prompt,
        "goal_type": goal_type,
        "mode": mode,
        "task_type": data.get('task_type') or None,
        "status": "pending",
        "created_at": _agent_now_iso(),
        "updated_at": _agent_now_iso(),
    }
    if goal_type == 'simulator_check':
        goal['seconds'] = int(data.get('seconds', 3) or 3)

    goals.append(goal)
    _save_agent_goals(payload)

    return jsonify({
        "success": True,
        "goal": goal,
        "message": "Hedef kuyruğa eklendi",
    }), 201


@app.route('/api/agent/goals/<goal_id>', methods=['GET'])
def api_agent_goal_detail(goal_id: str):
    """Get a single AI agent goal with result"""
    payload = _load_agent_goals()
    goal = next((item for item in payload.get('goals', []) if item.get('id') == goal_id), None)
    if not goal:
        return jsonify({"success": False, "error": "Hedef bulunamadı"}), 404

    return jsonify({
        "success": True,
        "goal": _build_agent_goal_response(goal, include_result=True),
    })


# ==================== WebSocket API ====================

@socketio.on('connect')
def handle_connect(auth=None):
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('status', {'message': 'Connected', 'sid': request.sid})
    
    # Send current machine status
    emit('machine_status', ws_manager.machine_status.to_dict())


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    from flask import request
    print(f"Client disconnected: {request.sid}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Subscribe to channel"""
    from flask_socketio import join_room
    from flask import request
    channel = data.get('channel')
    if channel:
        join_room(channel)
        print(f"Client {request.sid} joined {channel}")
        emit('subscribed', {'channel': channel})


@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Unsubscribe from channel"""
    from flask_socketio import leave_room
    from flask import request
    channel = data.get('channel')
    if channel:
        leave_room(channel)
        print(f"Client {request.sid} left {channel}")


@socketio.on('simulate_position')
def handle_simulate_position(data):
    """Simulate machine position updates"""
    import random
    import time
    
    for i in range(10):
        position = {
            'x': random.uniform(0, 6000),
            'y': random.uniform(0, 3000),
            'z': random.uniform(0, 100),
            'velocity': random.uniform(0, 80000)
        }
        emit('position_update', position)
        ws_manager.update_position(**position)
        time.sleep(0.5)


@socketio.on('start_cutting')
def handle_start_cutting(data):
    """Start cutting simulation"""
    import random
    import time
    
    # Update machine status
    ws_manager.update_status('running', cutting_speed=1000)
    emit('machine_status', ws_manager.machine_status.to_dict())
    
    # Simulate progress
    for progress in range(0, 101, 5):
        ws_manager.update_progress(progress)
        emit('progress_update', {'progress': progress})
        time.sleep(0.3)
    
    # Complete
    ws_manager.update_status('idle')
    emit('machine_status', ws_manager.machine_status.to_dict())
    emit('cut_complete', {
        'order_id': data.get('order_id'),
        'actual_time': 30
    })


@app.route('/api/ws/status', methods=['GET'])
def api_ws_status():
    """Get WebSocket status"""
    return jsonify({
        "success": True,
        "connected": ws_manager is not None,
        "clients": len(ws_manager.clients) if ws_manager else 0,
        "rooms": list(ws_manager.rooms.keys()) if ws_manager else [],
        "machine_status": ws_manager.machine_status.to_dict() if ws_manager else {}
    })


@app.route('/api/ws/simulate', methods=['POST'])
def api_ws_simulate():
    """Simulate machine data"""
    data = request.get_json()
    action = data.get('action')
    
    if action == 'position':
        import random
        ws_manager.update_position(
            x=random.uniform(0, 6000),
            y=random.uniform(0, 3000),
            z=random.uniform(0, 100)
        )
    elif action == 'status':
        ws_manager.update_status(data.get('status', 'running'))
    elif action == 'progress':
        ws_manager.update_progress(data.get('progress', 50))
    elif action == 'alarm':
        ws_manager.send_alarm(
            alarm_code=data.get('code', 100),
            message_text=data.get('message', 'Test alarm'),
            severity=data.get('severity', 'warning')
        )
    
    return jsonify({"success": True})


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
    host = os.getenv('GLASSCUTTING_HOST', '0.0.0.0')
    port = int(os.getenv('GLASSCUTTING_PORT', '5001'))
    debug_enabled = os.getenv('GLASSCUTTING_DEBUG', 'false').lower() == 'true'

    print("=" * 60)
    print("Glass Cutting Web Interface")
    print("LiSEC GFB-60/30RE")
    print("=" * 60)
    print("\nStarting Flask-SocketIO server...")
    print(f"Module path: {MODULES_PATH}")
    print(f"Template folder: {app.template_folder}")
    print(f"Static folder: {app.static_folder}")
    print(f"\n🌐 HTTP: http://localhost:{port}")
    print(f"⚡ WebSocket: ws://localhost:{port}/socket.io/")
    print("=" * 60)

    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug_enabled,
        allow_unsafe_werkzeug=True,
    )
