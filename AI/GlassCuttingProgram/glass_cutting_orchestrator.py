#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Glass Cutting Program Orchestrator
LiSEC GFB-60/30RE Cam Kesme Makinesi

7 AI Model Paralel Orkestrasyon:
- qwen3.5-plus: Genel, hızlı
- qwen3-max: Karmaşık analiz
- qwen3-coder-plus: Kod/G-code
- qwen3-coder-next: İleri kod
- glm-5: Doğrulama ve review
- kimi-k2.5: Dokümantasyon
- MiniMax-M2.5: Alternatif yaklaşım
"""

import os
import sys
import json
import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from datetime import datetime

# Orchestration module path
ORCHESTRATION_PATH = Path(__file__).parent.parent / "orchestration"
sys.path.insert(0, str(ORCHESTRATION_PATH))

try:
    from ai_orchestrator import AIOrchestrator, ModelConfig, ModelResponse
    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False
    print("Warning: ai_orchestrator not available, using mock mode")

# Machine constants
MACHINE_WIDTH = 6000  # mm
MACHINE_HEIGHT = 3000  # mm
MIN_PART_SIZE = (300, 200)  # mm
MAX_SPEED = 80000  # mm/min (80 m/min)
POSITIONING_ACCURACY = 0.05  # mm


@dataclass
class GlassOrder:
    """Glass order item"""
    order_id: str
    width: float  # mm
    height: float  # mm
    quantity: int
    thickness: float  # mm
    glass_type: str = "float"  # float, laminated, tempered
    priority: int = 1  # 1=high, 2=medium, 3=low
    rotate_allowed: bool = True
    edge_quality: str = "standard"  # standard, polished
    
    # Blade management options
    grinding_allowance: str = "none"  # none, grinding, fine_grinding, polishing, bevelling, edge_sealing
    blade_delete_enabled: bool = False  # Lama silme aktif
    trimming_enabled: bool = False  # Rodaj aktif
    
    # Source and integration metadata
    source_system: str = "manual"
    source_order_no: str = ""
    customer_name: str = ""
    edge_processing: str = ""
    process_code: str = ""
    herofis_options: Dict[str, Any] = field(default_factory=dict)
    film_type: str = ""
    film_thickness: float = 0.0


@dataclass
class CuttingResult:
    """Cutting optimization result"""
    placed_parts: List[Dict]
    cutting_path: List[int]
    utilization: float
    waste_area: float
    total_cuts: int
    estimated_time: float  # minutes
    gcode_file: Optional[str] = None
    report_file: Optional[str] = None


@dataclass
class DefectPoint:
    """Glass defect location"""
    x: float
    y: float
    defect_type: str  # scratch, bubble, crack, inclusion
    severity: float  # 0.0-1.0
    radius: float  # mm - affected area radius


class GlassCuttingOrchestrator:
    """
    Main orchestrator for glass cutting optimization
    Uses 7 AI models in parallel for different tasks
    """

    # Task routing for models
    TASK_ROUTING = {
        "nesting_analysis": ["qwen3-max-2026-01-23", "qwen3-coder-plus"],
        "path_planning": ["qwen3-coder-plus"],
        "gcode_generation": ["qwen3-coder-plus", "qwen3-coder-next"],
        "lamine_params": ["qwen3.5-plus"],
        "defect_validation": ["glm-5", "MiniMax-M2.5"],
        "documentation": ["kimi-k2.5"],
        "quick_query": ["qwen3.5-plus"]
    }

    def __init__(self,
                 sheet_width: float = MACHINE_WIDTH,
                 sheet_height: float = MACHINE_HEIGHT,
                 config_path: Optional[str] = None):
        """
        Initialize glass cutting orchestrator

        Args:
            sheet_width: Glass sheet width (mm)
            sheet_height: Glass sheet height (mm)
            config_path: Path to orchestrator config
        """
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.config_path = config_path or str(ORCHESTRATION_PATH / "orchestrator_config.json")

        # Load config
        self.config = self._load_config()

        # Initialize AI orchestrator
        self.ai_orchestrator = self._init_ai_orchestrator()
        self.model_index_by_id = {
            model["model_id"]: index
            for index, model in enumerate(self.config.get("models", []))
        }

        # Modules
        self.modules_dir = Path(__file__).parent / "modules"
        self.data_dir = Path(__file__).parent / "data"
        self.output_dir = Path(__file__).parent / "output"

        # Results
        self.last_result: Optional[CuttingResult] = None
        self.defects: List[DefectPoint] = []

    def _load_config(self) -> Dict:
        """Load orchestrator configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()

    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "api_key": os.getenv("QWEN_API_KEY", ""),
            "api_endpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
            "models": [
                {
                    "model_id": "qwen3.5-plus",
                    "temperature": 0.7,
                    "max_tokens": 2048
                },
                {
                    "model_id": "qwen3-max-2026-01-23",
                    "temperature": 0.5,
                    "max_tokens": 4096
                },
                {
                    "model_id": "qwen3-coder-plus",
                    "temperature": 0.2,
                    "max_tokens": 8192
                },
                {
                    "model_id": "glm-5",
                    "temperature": 0.4,
                    "max_tokens": 4096
                },
                {
                    "model_id": "kimi-k2.5",
                    "temperature": 0.5,
                    "max_tokens": 4096
                },
                {
                    "model_id": "MiniMax-M2.5",
                    "temperature": 0.5,
                    "max_tokens": 4096
                }
            ]
        }

    def _init_ai_orchestrator(self) -> Optional[AIOrchestrator]:
        """Initialize AI orchestrator with model configs"""
        if not ORCHESTRATOR_AVAILABLE:
            return None

        api_key = self.config.get("api_key", os.getenv("QWEN_API_KEY", ""))
        if not api_key:
            return None

        model_configs = []
        for m in self.config.get("models", []):
            model_configs.append(ModelConfig(
                model_id=m["model_id"],
                api_key=api_key,
                api_endpoint=self.config.get("api_endpoint", ""),
                temperature=m.get("temperature", 0.7),
                max_tokens=m.get("max_tokens", 2048),
                system_prompt=m.get("system_prompt", "")
            ))

        return AIOrchestrator(model_configs)

    def _resolve_model_indices(self, route_name: str) -> List[int]:
        """Resolve configured model ids to orchestrator indices."""
        indices = []
        for model_id in self.TASK_ROUTING.get(route_name, []):
            index = self.model_index_by_id.get(model_id)
            if index is not None:
                indices.append(index)
        return indices

    def _get_successful_contents(self, responses: List[Any]) -> List[str]:
        """Normalize orchestrator responses into successful content strings."""
        contents = []
        for response in responses or []:
            status = getattr(response, "status", None)
            content = getattr(response, "content", None)
            if status == "success" and content:
                contents.append(content)
        return contents

    async def optimize_cutting(self,
                               orders: List[GlassOrder],
                               defects: Optional[List[DefectPoint]] = None,
                               optimize_path: bool = True,
                               generate_gcode: bool = True) -> CuttingResult:
        """
        Main optimization pipeline

        Args:
            orders: List of glass orders
            defects: Optional defect points on sheet
            optimize_path: Whether to optimize cutting path
            generate_gcode: Whether to generate G-code

        Returns:
            CuttingResult with optimization details
        """
        start_time = time.time()

        # Store defects
        self.defects = defects or []

        # Step 1: Nesting optimization
        print("1. Nesting optimization...")
        placed_parts = await self._optimize_nesting(orders)

        # Step 2: Path planning
        print("2. Path planning...")
        cutting_path = await self._optimize_path(placed_parts) if optimize_path else list(range(len(placed_parts)))

        # Step 3: G-code generation
        print("3. G-code generation...")
        gcode_file = None
        if generate_gcode:
            gcode_file = await self._generate_gcode(placed_parts, cutting_path, orders)

        # Step 4: Calculate metrics
        total_area = self.sheet_width * self.sheet_height
        used_area = sum(p["width"] * p["height"] for p in placed_parts)
        utilization = used_area / total_area
        waste_area = total_area - used_area

        # Estimate cutting time
        total_distance = self._calculate_total_distance(placed_parts, cutting_path)
        estimated_time = total_distance / MAX_SPEED * 60  # minutes

        # Step 5: Generate report
        print("4. Generating report...")
        report_file = await self._generate_report(orders, placed_parts, utilization)

        result = CuttingResult(
            placed_parts=placed_parts,
            cutting_path=cutting_path,
            utilization=utilization,
            waste_area=waste_area,
            total_cuts=len(cutting_path),
            estimated_time=estimated_time,
            gcode_file=gcode_file,
            report_file=report_file
        )

        self.last_result = result
        elapsed = time.time() - start_time
        print(f"\nOptimization completed in {elapsed:.2f}s")
        print(f"Utilization: {utilization*100:.1f}%")
        print(f"Waste: {waste_area/1000000:.2f} m²")
        print(f"Estimated time: {estimated_time:.1f} min")

        return result

    async def _optimize_nesting(self, orders: List[GlassOrder]) -> List[Dict]:
        """
        Nesting optimization using AI models

        Uses: qwen3-max (analysis) + qwen3-coder-plus (algorithm)
        """
        # Sort by priority
        sorted_orders = sorted(orders, key=lambda x: x.priority, reverse=True)

        # Prepare nesting data
        parts = []
        for order in sorted_orders:
            for i in range(order.quantity):
                parts.append({
                    "order_id": order.order_id,
                    "width": order.width,
                    "height": order.height,
                    "thickness": order.thickness,
                    "glass_type": order.glass_type,
                    "rotate_allowed": order.rotate_allowed,
                    "priority": order.priority
                })

        # Use Guillotine algorithm (from existing optimization module)
        placed = self._guillotine_pack(parts)

        # If AI orchestrator available, get optimization suggestions
        if self.ai_orchestrator:
            try:
                prompt = f"""Analyze this glass cutting nesting result and suggest improvements:

Sheet: {self.sheet_width}x{self.sheet_height} mm
Parts placed: {len(placed)}
Utilization: {sum(p['width']*p['height'] for p in placed)/(self.sheet_width*self.sheet_height)*100:.1f}%

Suggest:
1. Better placement strategies
2. Edge quality considerations
3. Cutting sequence optimization"""

                model_indices = self._resolve_model_indices("nesting_analysis")
                responses = await self.ai_orchestrator.run_parallel(prompt, model_indices or None)
                suggestions = self._get_successful_contents(responses)
                if suggestions:
                    print(f"AI nesting suggestions received from {len(suggestions)} model(s)")
            except Exception as e:
                print(f"AI suggestion failed: {e}")

        return placed

    def _guillotine_pack(self, parts: List[Dict]) -> List[Dict]:
        """
        Guillotine packing algorithm

        Args:
            parts: List of parts to place

        Returns:
            List of placed parts with positions
        """
        # Free rectangles (x, y, width, height)
        free_rects = [(0, 0, self.sheet_width, self.sheet_height)]
        placed = []

        for part in parts:
            best_rect = None
            best_score = float('inf')
            best_rotated = False

            pw, ph = part["width"], part["height"]

            for i, (x, y, rw, rh) in enumerate(free_rects):
                # Normal placement
                if pw <= rw and ph <= rh:
                    score = min(rw - pw, rh - ph)  # Best fit heuristic
                    if score < best_score:
                        best_score = score
                        best_rect = (i, x, y, False)

                # Rotated placement
                if part["rotate_allowed"] and ph <= rw and pw <= rh:
                    score = min(rw - ph, rh - pw)
                    if score < best_score:
                        best_score = score
                        best_rect = (i, x, y, True)

            if best_rect is None:
                # Cannot place this part
                print(f"Warning: Could not place part {part['order_id']}")
                continue

            rect_idx, x, y, rotated = best_rect
            rx, ry, rw, rh = free_rects[rect_idx]

            # Place the part
            if rotated:
                placed.append({
                    **part,
                    "x": x,
                    "y": y,
                    "placed_width": ph,
                    "placed_height": pw,
                    "rotated": True
                })
                pw, ph = ph, pw  # Swap for splitting
            else:
                placed.append({
                    **part,
                    "x": x,
                    "y": y,
                    "placed_width": pw,
                    "placed_height": ph,
                    "rotated": False
                })

            # Split remaining space
            free_rects.pop(rect_idx)

            # Add remaining rectangles (guillotine split)
            if pw < rw:
                free_rects.append((x + pw, y, rw - pw, rh))
            if ph < rh:
                free_rects.append((x, y + ph, pw, rh - ph))

        return placed

    async def _optimize_path(self, placed_parts: List[Dict]) -> List[int]:
        """
        Optimize cutting path using TSP algorithm

        Uses: qwen3-coder-plus
        """
        n = len(placed_parts)
        if n <= 1:
            return list(range(n))

        # Calculate distance matrix
        def get_center(part: Dict) -> Tuple[float, float]:
            return (part["x"] + part["placed_width"]/2,
                    part["y"] + part["placed_height"]/2)

        centers = [get_center(p) for p in placed_parts]

        # Nearest neighbor heuristic
        path = [0]
        unvisited = set(range(1, n))

        while unvisited:
            current = path[-1]
            current_pos = centers[current]

            # Find nearest unvisited
            nearest = min(unvisited,
                          key=lambda i: ((centers[i][0]-current_pos[0])**2 +
                                         (centers[i][1]-current_pos[1])**2))
            path.append(nearest)
            unvisited.remove(nearest)

        # 2-opt improvement
        path = self._2opt_improve(path, centers)

        return path

    def _2opt_improve(self, path: List[int], centers: List[Tuple[float, float]]) -> List[int]:
        """
        2-opt local search improvement
        """
        def distance(i: int, j: int) -> float:
            return ((centers[i][0]-centers[j][0])**2 +
                    (centers[i][1]-centers[j][1])**2)**0.5

        def path_length(p: List[int]) -> float:
            return sum(distance(p[i], p[i+1]) for i in range(len(p)-1))

        improved = True
        best_path = path[:]
        best_length = path_length(best_path)

        while improved:
            improved = False
            for i in range(1, len(best_path) - 1):
                for j in range(i + 1, len(best_path)):
                    new_path = best_path[:i] + best_path[i:j+1][::-1] + best_path[j+1:]
                    new_length = path_length(new_path)

                    if new_length < best_length:
                        best_path = new_path
                        best_length = new_length
                        improved = True
                        break
                if improved:
                    break

        return best_path

    async def _generate_gcode(self,
                              placed_parts: List[Dict],
                              cutting_path: List[int],
                              orders: List[GlassOrder]) -> str:
        """
        Generate G-code for NC300 controller

        Uses: qwen3-coder-plus + qwen3-coder-next (parallel)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        gcode_file = self.output_dir / "gcode" / f"cut_{timestamp}.nc"

        gcode_lines = [
            "; LiSEC GFB-60/30RE Glass Cutting Program",
            "; Generated by AI GlassCuttingOrchestrator",
            f"; Date: {datetime.now().isoformat()}",
            f"; Sheet: {self.sheet_width}x{self.sheet_height} mm",
            f"; Parts: {len(placed_parts)}",
            "",
            "; Machine initialization",
            "G21 ; Metric units (mm)",
            "G90 ; Absolute positioning",
            "G17 ; XY plane selection",
            "",
            "; Set cutting parameters",
            "M03 S1000 ; Spindle/carriage start",
            "",
            "; Begin cutting sequence"
        ]

        # Add each cut in optimized order
        for idx in cutting_path:
            part = placed_parts[idx]
            x, y = part["x"], part["y"]
            w, h = part["placed_width"], part["placed_height"]
            order_id = part["order_id"]

            gcode_lines.extend([
                "",
                f"; Part {idx+1}: Order {order_id}",
                f"; Size: {w}x{h} mm at ({x}, {y})",
                f"G00 X{x} Y{y} F{MAX_SPEED} ; Rapid move to start",
                f"G01 X{x+w} Y{y} F1000 ; Bottom edge",
                f"G01 X{x+w} Y{y+h} ; Right edge",
                f"G01 X{x} Y{y+h} ; Top edge",
                f"G01 X{x} Y{y} ; Left edge (complete)",
            ])

            # Add break-out point for tempered glass
            if any(o.glass_type == "tempered" and o.order_id == order_id for o in orders):
                gcode_lines.append(f"; Break-out point")
                gcode_lines.append(f"G00 X{x+w/2} Y{y+h/2}")

        gcode_lines.extend([
            "",
            "; End program",
            "M05 ; Spindle stop",
            "G00 X0 Y0 ; Return home",
            "M30 ; Program end"
        ])

        # Write G-code file
        with open(gcode_file, 'w') as f:
            f.write('\n'.join(gcode_lines))

        # If AI available, validate G-code
        if self.ai_orchestrator:
            try:
                prompt = f"""Validate this G-code for Delta NC300 CNC controller:

{gcode_lines[:50]}

Check for:
1. Correct G-code syntax
2. NC300 compatibility
3. Safety considerations"""

                model_indices = self._resolve_model_indices("gcode_generation")
                await self.ai_orchestrator.run_parallel(prompt, model_indices or None)
            except Exception as e:
                print(f"G-code validation skipped: {e}")

        return str(gcode_file)

    async def _generate_report(self,
                               orders: List[GlassOrder],
                               placed_parts: List[Dict],
                               utilization: float) -> str:
        """
        Generate optimization report

        Uses: kimi-k2.5 for documentation
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / "reports" / f"report_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "machine": {
                "model": "LiSEC GFB-60/30RE",
                "sheet_size": f"{self.sheet_width}x{self.sheet_height} mm",
                "max_speed": f"{MAX_SPEED/1000} m/min"
            },
            "orders": [
                {
                    "order_id": o.order_id,
                    "size": f"{o.width}x{o.height} mm",
                    "quantity": o.quantity,
                    "glass_type": o.glass_type,
                    "priority": o.priority
                }
                for o in orders
            ],
            "optimization_result": {
                "parts_placed": len(placed_parts),
                "utilization": f"{utilization*100:.2f}%",
                "waste_area": f"{(1-utilization)*self.sheet_width*self.sheet_height/1000000:.2f} m²",
                "placed_parts": placed_parts
            },
            "defects": [
                {
                    "x": d.x,
                    "y": d.y,
                    "type": d.defect_type,
                    "severity": d.severity
                }
                for d in self.defects
            ]
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return str(report_file)

    def _calculate_total_distance(self,
                                   placed_parts: List[Dict],
                                   cutting_path: List[int]) -> float:
        """Calculate total cutting distance"""
        total = 0.0

        for i, idx in enumerate(cutting_path):
            part = placed_parts[idx]
            # Perimeter of part
            total += 2 * (part["placed_width"] + part["placed_height"])

            # Travel distance to next part
            if i < len(cutting_path) - 1:
                next_part = placed_parts[cutting_path[i+1]]
                dx = next_part["x"] - part["x"]
                dy = next_part["y"] - part["y"]
                total += (dx**2 + dy**2)**0.5

        return total

    async def calculate_lamine_params(self,
                                       upper_thickness: float,
                                       film_thickness: float,
                                       lower_thickness: float,
                                       film_type: str = "PVB") -> Dict:
        """
        Calculate laminated glass cutting parameters

        Uses: qwen3.5-plus (quick response)
        """
        if not self.ai_orchestrator:
            # Return default params
            return {
                "heating_time": 4.0,
                "heating_temp": 135,
                "upper_cut_pressure": 3.5,
                "lower_cut_pressure": 3.2,
                "separation_pressure": 2.8,
                "break_pressure": 4.0,
                "cutting_speed": 1800,
                "offset_x": 0.02,
                "offset_y": -0.01
            }

        prompt = f"""Calculate laminated glass cutting parameters for LiSEC GFB-60/30RE:

Upper glass: {upper_thickness} mm
Film (PVB/EVA/SGP): {film_thickness} mm ({film_type})
Lower glass: {lower_thickness} mm

Return JSON with:
- heating_time (seconds)
- heating_temp (Celsius)
- upper_cut_pressure (bar)
- lower_cut_pressure (bar)
- separation_pressure (bar)
- break_pressure (bar)
- cutting_speed (mm/min)
- offset_x, offset_y (mm) for upper/lower alignment"""

        try:
            model_indices = self._resolve_model_indices("lamine_params")
            model_index = model_indices[0] if model_indices else 0
            responses = await self.ai_orchestrator.run_single_model(prompt, model_index)
            # Parse response
            if responses and responses.content:
                # Extract JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', responses.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        except Exception as e:
            print(f"Lamine params calculation failed: {e}")

        return {}

    def load_orders_from_file(self, file_path: str) -> List[GlassOrder]:
        """Load orders from JSON file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        orders = []
        for item in data.get("orders", []):
            orders.append(GlassOrder(
                order_id=item["order_id"],
                width=item["width"],
                height=item["height"],
                quantity=item.get("quantity", 1),
                thickness=item.get("thickness", 4),
                glass_type=item.get("glass_type", "float"),
                priority=item.get("priority", 1),
                rotate_allowed=item.get("rotate_allowed", True)
            ))

        return orders

    def save_orders_to_file(self, orders: List[GlassOrder], file_path: str):
        """Save orders to JSON file"""
        data = {
            "orders": [
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
                for o in orders
            ]
        }

        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)


async def main():
    """Demo usage"""
    print("=" * 60)
    print("Glass Cutting Program - AI Orchestrator")
    print("LiSEC GFB-60/30RE")
    print("=" * 60)

    # Create orchestrator
    orchestrator = GlassCuttingOrchestrator()

    # Create sample orders
    orders = [
        GlassOrder("ORD-001", 500, 400, 10, 4, "float", 1),
        GlassOrder("ORD-002", 300, 200, 20, 4, "float", 2),
        GlassOrder("ORD-003", 800, 600, 5, 6, "float", 1),
        GlassOrder("ORD-004", 400, 300, 15, 4, "float", 3),
        GlassOrder("ORD-005", 1000, 800, 2, 8, "laminated", 1),
    ]

    # Save sample orders
    orchestrator.save_orders_to_file(orders, str(orchestrator.data_dir / "orders.json"))
    print(f"\nSample orders saved to: {orchestrator.data_dir / 'orders.json'}")

    # Run optimization
    result = await orchestrator.optimize_cutting(orders)

    print(f"\nG-code file: {result.gcode_file}")
    print(f"Report file: {result.report_file}")

    # Calculate lamine params if laminated glass
    lamine_orders = [o for o in orders if o.glass_type == "laminated"]
    if lamine_orders:
        print("\nCalculating laminated glass parameters...")
        params = await orchestrator.calculate_lamine_params(
            upper_thickness=4,
            film_thickness=0.76,
            lower_thickness=4,
            film_type="PVB"
        )
        print(f"Lamine params: {params}")


if __name__ == "__main__":
    asyncio.run(main())
