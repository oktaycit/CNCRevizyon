#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
G-Code Generator Module
NC300 Compatible G-code Generation for Glass Cutting

Features:
- Standard G-code commands (G00, G01, G02, G03)
- NC300 specific codes
- Laminated glass cutting sequences
- E-Cam profile integration
- Break-out points for tempered glass

Uses: qwen3-coder-plus + qwen3-coder-next (parallel generation)
"""

import os
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from enum import Enum


class GlassType(Enum):
    """Glass type enumeration"""
    FLOAT = "float"
    LAMINATED = "laminated"
    TEMPERED = "tempered"
    WIRED = "wired"


class CutType(Enum):
    """Cut type enumeration"""
    PERIMETER = "perimeter"
    SHAPE = "shape"
    HOLE = "hole"
    LINE = "line"
    ARC = "arc"
    CIRCLE = "circle"
    POLYGON = "polygon"


@dataclass
class ShapePoint:
    """Point in a shape"""
    x: float
    y: float
    cut_type: str = "linear"  # linear, arc_cw, arc_ccw
    arc_radius: Optional[float] = None
    arc_center_x: Optional[float] = None
    arc_center_y: Optional[float] = None


@dataclass
class ShapeDefinition:
    """Shape definition for non-rectangular cuts"""
    shape_id: str
    shape_type: str  # rectangle, circle, polygon, arc
    base_x: float
    base_y: float
    points: List[ShapePoint]
    parameters: Dict = field(default_factory=dict)  # radius, width, height, etc.


@dataclass
class GCodeParams:
    """G-code generation parameters"""
    rapid_speed: int = 80000  # mm/min (80 m/min)
    cut_speed: int = 1000  # mm/min for cutting
    approach_speed: int = 500  # mm/min for approach
    spindle_start: int = 1000  # RPM equivalent
    coolant: bool = False
    home_x: float = 0
    home_y: float = 0
    safe_z: float = 10  # mm above glass
    cut_z: float = 0  # mm at cutting depth


@dataclass
class GCodeProgram:
    """Generated G-code program"""
    filename: str
    lines: List[str]
    parts_count: int
    total_distance: float
    estimated_time: float
    glass_type: str
    created_at: datetime


class NC300GCodeGenerator:
    """
    G-code generator for Delta NC300 CNC controller
    Compatible with LiSEC GFB-60/30RE glass cutting machine
    """

    # NC300 specific G-codes
    NC300_CODES = {
        "rapid": "G00",
        "linear": "G01",
        "arc_cw": "G02",
        "arc_ccw": "G03",
        "absolute": "G90",
        "incremental": "G91",
        "metric": "G21",
        "inch": "G20",
        "plane_xy": "G17",
        "plane_xz": "G18",
        "plane_yz": "G19",
        "spindle_on": "M03",
        "spindle_off": "M05",
        "program_end": "M30",
        "coolant_on": "M08",
        "coolant_off": "M09",
        "dwell": "G04",
        "blade_delete_on": "M10",
        "blade_delete_off": "M11",
    }

    def __init__(self, params: Optional[GCodeParams] = None):
        """
        Initialize G-code generator

        Args:
            params: Cutting parameters
        """
        self.params = params or GCodeParams()

    def generate(self,
                 placed_parts: List[Dict],
                 cutting_path: List[int],
                 glass_type: GlassType = GlassType.FLOAT,
                 program_name: str = "glass_cut",
                 include_header: bool = True,
                 include_footer: bool = True) -> GCodeProgram:
        """
        Generate complete G-code program

        Args:
            placed_parts: List of placed parts
            cutting_path: Optimized cutting sequence (indices)
            glass_type: Type of glass being cut
            program_name: Program identifier
            include_header: Include initialization header
            include_footer: Include termination footer

        Returns:
            GCodeProgram object
        """
        lines = []
        total_distance = 0.0
        current_pos = (self.params.home_x, self.params.home_y)

        # Header
        if include_header:
            lines.extend(self._generate_header(program_name, glass_type, placed_parts))

        # Main cutting sequence
        for path_idx in cutting_path:
            part = placed_parts[path_idx]
            part_gcode, part_distance = self._generate_part_cut(part, glass_type)
            lines.extend(part_gcode)
            total_distance += part_distance

        # Footer
        if include_footer:
            lines.extend(self._generate_footer())

        # Calculate estimated time
        # Rapid moves at 80 m/min, cuts at 1 m/min
        cut_time = total_distance / self.params.cut_speed * 60  # minutes
        rapid_time = len(cutting_path) * 0.5  # approximate rapid moves
        estimated_time = cut_time + rapid_time

        filename = f"{program_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.nc"

        return GCodeProgram(
            filename=filename,
            lines=lines,
            parts_count=len(placed_parts),
            total_distance=total_distance,
            estimated_time=estimated_time,
            glass_type=glass_type.value,
            created_at=datetime.now()
        )

    def _generate_header(self, program_name: str,
                         glass_type: GlassType,
                         placed_parts: List[Dict]) -> List[str]:
        """Generate program header"""
        header = [
            f"; ================================================",
            f"; LiSEC GFB-60/30RE Glass Cutting Program",
            f"; Generated by AI GlassCuttingProgram",
            f"; Date: {datetime.now().isoformat()}",
            f"; Program: {program_name}",
            f"; ================================================",
            "",
            f"; Glass type: {glass_type.value}",
            f"; Parts count: {len(placed_parts)}",
            "",
            "; --- Machine Initialization ---",
            self.NC300_CODES["metric"],
            self.NC300_CODES["absolute"],
            self.NC300_CODES["plane_xy"],
            "",
            "; --- Safety Check ---",
            "; Verify sheet position",
            "; Verify coolant (if required)",
            "",
            "; --- Start Cutting ---",
            self.NC300_CODES["spindle_on"] + f" S{self.params.spindle_start}",
            "",
        ]

        if self.params.coolant:
            header.append(self.NC300_CODES["coolant_on"])

        return header

    def _generate_footer(self) -> List[str]:
        """Generate program footer"""
        footer = [
            "",
            "; --- End Cutting ---",
            self.NC300_CODES["spindle_off"],
            "",
            "; Return to home",
            f"{self.NC300_CODES['rapid']} X{self.params.home_x} Y{self.params.home_y}",
            "",
            self.NC300_CODES["program_end"],
            "",
            f"; --- End of Program ---",
        ]

        if self.params.coolant:
            footer.insert(2, self.NC300_CODES["coolant_off"])

        return footer

    def _generate_part_cut(self, part: Dict, glass_type: GlassType) -> Tuple[List[str], float]:
        """
        Generate G-code for single part

        Args:
            part: Part placement data
            glass_type: Glass type

        Returns:
            Tuple of (gcode_lines, total_distance)
        """
        lines = []
        distance = 0.0

        x = part["x"]
        y = part["y"]
        w = part.get("placed_width", part.get("width", 100))
        h = part.get("placed_height", part.get("height", 100))
        part_id = part.get("order_id", part.get("part_id", "unknown"))
        thickness = part.get("thickness", 4)
        blade_delete_enabled = bool(part.get("blade_delete_enabled", False))

        lines.extend([
            "",
            f"; --- Part: {part_id} ---",
            f"; Position: ({x:.2f}, {y:.2f})",
            f"; Size: {w:.0f}x{h:.0f} mm",
            f"; Thickness: {thickness} mm",
        ])

        # Rapid move to start position
        lines.append(f"{self.NC300_CODES['rapid']} X{x:.2f} Y{y:.2f} F{self.params.rapid_speed}")

        if blade_delete_enabled:
            blade_lines, blade_distance = self._generate_blade_delete_sequence(x, y, w, h)
            lines.extend(blade_lines)
            distance += blade_distance

        # Cutting sequence depends on glass type
        if glass_type == GlassType.LAMINATED:
            cut_lines, cut_dist = self._generate_laminated_cut(x, y, w, h)
        elif glass_type == GlassType.TEMPERED:
            cut_lines, cut_dist = self._generate_tempered_cut(x, y, w, h)
        else:
            cut_lines, cut_dist = self._generate_float_cut(x, y, w, h)

        lines.extend(cut_lines)
        distance += cut_dist

        return lines, distance

    def _generate_blade_delete_sequence(self, x: float, y: float,
                                        w: float, h: float) -> Tuple[List[str], float]:
        """Generate a simple blade wiping / lama siyirma sequence."""
        lines = [
            "",
            "; Blade delete sequence",
            "; Step BD1: Move to wiping pad",
        ]
        distance = 0.0

        pad_x = max(0.0, x - min(80.0, max(20.0, w * 0.1)))
        pad_y = max(0.0, y - min(60.0, max(20.0, h * 0.1)))

        lines.append(f"{self.NC300_CODES['rapid']} X{pad_x:.2f} Y{pad_y:.2f} F{self.params.rapid_speed}")
        distance += abs(x - pad_x) + abs(y - pad_y)
        lines.append(self.NC300_CODES["blade_delete_on"])
        lines.append(f"{self.NC300_CODES['dwell']} P1.5 ; Blade wipe contact")
        lines.append(self.NC300_CODES["blade_delete_off"])
        lines.extend([
            "; Step BD2: Return to cut start",
            f"{self.NC300_CODES['rapid']} X{x:.2f} Y{y:.2f} F{self.params.rapid_speed}",
        ])
        distance += abs(x - pad_x) + abs(y - pad_y)
        return lines, distance

    def _generate_float_cut(self, x: float, y: float,
                            w: float, h: float) -> Tuple[List[str], float]:
        """Generate standard float glass cut"""
        lines = []
        distance = 0.0

        # Bottom edge (left to right)
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y:.2f} F{self.params.cut_speed}")
        distance += w

        # Right edge (bottom to top)
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y+h:.2f}")
        distance += h

        # Top edge (right to left)
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y+h:.2f}")
        distance += w

        # Left edge (top to bottom)
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y:.2f}")
        distance += h

        return lines, distance

    def _generate_laminated_cut(self, x: float, y: float,
                                 w: float, h: float) -> Tuple[List[str], float]:
        """
        Generate laminated glass cut sequence
        Requires heating and upper/lower separation
        """
        lines = []
        distance = 0.0

        # Heating approach
        lines.extend([
            "",
            "; Laminated glass sequence",
            "; Step 1: Upper glass cut",
        ])

        # Upper glass perimeter
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y:.2f} F{self.params.cut_speed}")
        distance += w
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y+h:.2f}")
        distance += h
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y+h:.2f}")
        distance += w
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y:.2f}")
        distance += h

        # Heating position (center)
        lines.extend([
            "",
            "; Step 2: Heating",
            f"{self.NC300_CODES['rapid']} X{x+w/2:.2f} Y{y+h/2:.2f}",
            f"{self.NC300_CODES['dwell']} P4.0 ; Heat for 4 seconds",
        ])

        # Lower glass cut
        lines.extend([
            "",
            "; Step 3: Lower glass cut",
        ])

        # Lower glass perimeter (same path)
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y:.2f}")
        distance += w
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y+h:.2f}")
        distance += h
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y+h:.2f}")
        distance += w
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y:.2f}")
        distance += h

        # Break-out
        lines.extend([
            "",
            "; Step 4: Break-out",
            f"{self.NC300_CODES['rapid']} X{x+w/2:.2f} Y{y+h/2:.2f}",
            "; Apply break pressure",
        ])

        return lines, distance

    def _generate_tempered_cut(self, x: float, y: float,
                                w: float, h: float) -> Tuple[List[str], float]:
        """
        Generate tempered glass cut sequence
        Tempered glass cannot be cut - only scored
        """
        lines = []
        distance = 0.0

        lines.extend([
            "",
            "; WARNING: Tempered glass",
            "; Only scoring - no full depth cut",
            "; Break-out required after scoring",
        ])

        # Score perimeter (light pressure)
        score_speed = self.params.cut_speed * 2  # Faster for scoring

        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y:.2f} F{score_speed}")
        distance += w
        lines.append(f"{self.NC300_CODES['linear']} X{x+w:.2f} Y{y+h:.2f}")
        distance += h
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y+h:.2f}")
        distance += w
        lines.append(f"{self.NC300_CODES['linear']} X{x:.2f} Y{y:.2f}")
        distance += h

        # Break-out point
        lines.extend([
            "",
            "; Break-out point",
            f"{self.NC300_CODES['rapid']} X{x+w/2:.2f} Y{y+h/2:.2f}",
            "; Manual break required",
        ])

        return lines, distance

    def generate_shape_cut(self,
                           x: float, y: float,
                           shape_points: List[Tuple[float, float]],
                           part_id: str = "shape") -> List[str]:
        """
        Generate G-code for custom shape

        Args:
            x, y: Base position
            shape_points: List of (dx, dy) relative points
            part_id: Part identifier

        Returns:
            G-code lines
        """
        lines = [
            "",
            f"; --- Shape: {part_id} ---",
            f"; Base position: ({x:.2f}, {y:.2f})",
        ]

        # Rapid to first point
        first_x = x + shape_points[0][0]
        first_y = y + shape_points[0][1]
        lines.append(f"{self.NC300_CODES['rapid']} X{first_x:.2f} Y{first_y:.2f}")

        # Cut through all points
        for dx, dy in shape_points[1:]:
            px = x + dx
            py = y + dy
            lines.append(f"{self.NC300_CODES['linear']} X{px:.2f} Y{py:.2f}")

        # Return to first point to close shape
        lines.append(f"{self.NC300_CODES['linear']} X{first_x:.2f} Y{first_y:.2f}")

        return lines

    def generate_arc_cut(self,
                         center_x: float, center_y: float,
                         radius: float, start_angle: float,
                         end_angle: float, clockwise: bool = True) -> List[str]:
        """
        Generate G-code for arc cut

        Args:
            center_x, center_y: Arc center
            radius: Arc radius
            start_angle: Start angle (degrees)
            end_angle: End angle (degrees)
            clockwise: Direction (CW=G02, CCW=G03)

        Returns:
            G-code lines
        """
        import math

        # Calculate start and end points
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)

        start_x = center_x + radius * math.cos(start_rad)
        start_y = center_y + radius * math.sin(start_rad)
        end_x = center_x + radius * math.cos(end_rad)
        end_y = center_y + radius * math.sin(end_rad)

        arc_code = self.NC300_CODES["arc_cw"] if clockwise else self.NC300_CODES["arc_ccw"]

        lines = [
            "",
            f"; Arc cut",
            f"{self.NC300_CODES['rapid']} X{start_x:.2f} Y{start_y:.2f}",
            f"{arc_code} X{end_x:.2f} Y{end_y:.2f} I{center_x-start_x:.2f} J{center_y-start_y:.2f}",
        ]

        return lines

    def save_to_file(self, program: GCodeProgram, output_dir: str) -> str:
        """
        Save G-code program to file

        Args:
            program: GCodeProgram object
            output_dir: Output directory path

        Returns:
            Full file path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / program.filename

        with open(file_path, 'w') as f:
            f.write('\n'.join(program.lines))

        return str(file_path)

    def get_program_summary(self, program: GCodeProgram) -> str:
        """Get program summary as string"""
        summary = [
            f"Program: {program.filename}",
            f"Glass type: {program.glass_type}",
            f"Parts: {program.parts_count}",
            f"Total distance: {program.total_distance:.0f} mm",
            f"Estimated time: {program.estimated_time:.1f} min",
            f"Lines: {len(program.lines)}",
        ]
        return '\n'.join(summary)


def demo():
    """Demo usage"""
    print("=" * 60)
    print("G-Code Generator Demo")
    print("=" * 60)

    # Sample placed parts
    placed_parts = [
        {"x": 0, "y": 0, "width": 500, "height": 400,
         "order_id": "P1", "thickness": 4},
        {"x": 500, "y": 0, "width": 300, "height": 200,
         "order_id": "P2", "thickness": 4},
        {"x": 0, "y": 400, "width": 800, "height": 600,
         "order_id": "P3", "thickness": 6},
        {"x": 1000, "y": 0, "width": 400, "height": 300,
         "order_id": "P4", "thickness": 8},
    ]

    cutting_path = [0, 1, 2, 3]  # Sequential order

    # Create generator
    generator = NC300GCodeGenerator()

    # Generate float glass program
    print("\n--- Float Glass Program ---")
    float_program = generator.generate(
        placed_parts, cutting_path, GlassType.FLOAT, "float_cut"
    )

    print(generator.get_program_summary(float_program))
    print("\nFirst 30 lines:")
    print('\n'.join(float_program.lines[:30]))

    # Generate laminated glass program
    print("\n--- Laminated Glass Program ---")
    lamine_parts = [
        {"x": 0, "y": 0, "width": 600, "height": 400,
         "order_id": "L1", "thickness": 8},
    ]
    lamine_program = generator.generate(
        lamine_parts, [0], GlassType.LAMINATED, "lamine_cut"
    )

    print(generator.get_program_summary(lamine_program))


if __name__ == "__main__":
    demo()
