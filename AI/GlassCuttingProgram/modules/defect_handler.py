#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Defect Handler Module
Glass Defect Detection and Avoidance for Cutting Optimization

Features:
- Defect classification (scratch, bubble, crack, inclusion)
- Defect map generation
- Cutting path adjustment around defects
- Integration with vision system

Uses: glm-4.7 + kimi-k2.5 (validation and documentation)
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum


class DefectType(Enum):
    """Glass defect types"""
    SCRATCH = "scratch"
    BUBBLE = "bubble"
    CRACK = "crack"
    INCLUSION = "inclusion"
    WAVE = "wave"
    TIN = "tin"  # Tin side defect
    NONE = "none"


@dataclass
class Defect:
    """Single defect on glass sheet"""
    x: float  # mm position
    y: float  # mm position
    defect_type: DefectType
    severity: float  # 0.0-1.0 (higher = worse)
    radius: float  # mm - affected area radius
    orientation: Optional[float] = None  # degrees (for scratches)
    length: Optional[float] = None  # mm (for scratches)

    @property
    def avoidance_margin(self) -> float:
        """Margin to avoid this defect"""
        # Severity affects margin
        return self.radius * (1 + self.severity)

    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Bounding box (x_min, y_min, x_max, y_max)"""
        margin = self.avoidance_margin
        return (
            self.x - margin,
            self.y - margin,
            self.x + margin,
            self.y + margin
        )


@dataclass
class DefectMap:
    """Defect map for glass sheet"""
    width: float
    height: float
    defects: List[Defect]
    grid_resolution: int = 10  # mm per grid cell

    @property
    def grid_width(self) -> int:
        return int(self.width / self.grid_resolution)

    @property
    def grid_height(self) -> int:
        return int(self.height / self.grid_resolution)


class DefectDetector:
    """
    Simulated defect detection
    In production, this would connect to vision system
    """

    # Severity thresholds by defect type
    SEVERITY_MAP = {
        DefectType.CRACK: 0.8,     # Always avoid cracks
        DefectType.INCLUSION: 0.7,  # High priority
        DefectType.BUBBLE: 0.5,    # Medium
        DefectType.SCRATCH: 0.3,   # Low (surface only)
        DefectType.WAVE: 0.2,      # Minimal
        DefectType.TIN: 0.1,       # Very low
    }

    def __init__(self, vision_client=None):
        """
        Initialize defect detector

        Args:
            vision_client: Vision system client (optional)
        """
        self.vision_client = vision_client

    def detect_defects(self,
                       image_path: Optional[str] = None,
                       sheet_width: float = 6000,
                       sheet_height: float = 3000) -> List[Defect]:
        """
        Detect defects on glass sheet

        Args:
            image_path: Path to glass image (for vision system)
            sheet_width: Sheet width (mm)
            sheet_height: Sheet height (mm)

        Returns:
            List of detected defects
        """
        if self.vision_client and image_path:
            # Use vision system
            return self._detect_with_vision(image_path)
        else:
            # Simulated detection for demo
            return self._simulate_detection(sheet_width, sheet_height)

    def _detect_with_vision(self, image_path: str) -> List[Defect]:
        """Use vision system for detection"""
        # Placeholder - would call actual vision API
        # The Vision/qwen_client.py can be integrated here
        defects = []

        try:
            # Import vision client if available
            # from AI.Vision.qwen_client import ...
            # Process image and return defects
            pass
        except ImportError:
            pass

        return defects

    def _simulate_detection(self,
                            width: float,
                            height: float,
                            num_defects: int = 5) -> List[Defect]:
        """Simulate defect detection for testing"""
        import random

        defects = []
        defect_types = [DefectType.SCRATCH, DefectType.BUBBLE,
                        DefectType.CRACK, DefectType.INCLUSION]

        for _ in range(num_defects):
            defect_type = random.choice(defect_types)
            x = random.uniform(100, width - 100)
            y = random.uniform(100, height - 100)
            severity = self.SEVERITY_MAP.get(defect_type, 0.5) + random.uniform(-0.1, 0.1)
            radius = random.uniform(10, 50)

            defect = Defect(
                x=x,
                y=y,
                defect_type=defect_type,
                severity=max(0, min(1, severity)),
                radius=radius
            )

            if defect_type == DefectType.SCRATCH:
                defect.orientation = random.uniform(0, 180)
                defect.length = random.uniform(20, 100)

            defects.append(defect)

        return defects


class DefectAvoidanceOptimizer:
    """
    Optimize cutting to avoid defects
    """

    def __init__(self, defect_map: DefectMap):
        """
        Initialize avoidance optimizer

        Args:
            defect_map: DefectMap object
        """
        self.defect_map = defect_map
        self.sheet_width = defect_map.width
        self.sheet_height = defect_map.height

    def generate_avoidance_map(self) -> np.ndarray:
        """
        Generate avoidance heat map

        Returns:
            2D numpy array with avoidance scores
        """
        grid_w = self.defect_map.grid_width
        grid_h = self.defect_map.grid_height
        res = self.defect_map.grid_resolution

        # Initialize map
        avoidance_map = np.zeros((grid_h, grid_w), dtype=np.float32)

        # Add Gaussian influence for each defect
        for defect in self.defect_map.defects:
            cx = int(defect.x / res)
            cy = int(defect.y / res)
            sigma = defect.avoidance_margin / res

            # Create Gaussian kernel
            for dy in range(-int(3*sigma), int(3*sigma)+1):
                for dx in range(-int(3*sigma), int(3*sigma)+1):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < grid_w and 0 <= ny < grid_h:
                        dist = math.sqrt(dx**2 + dy**2)
                        avoidance_map[ny, nx] += defect.severity * \
                                                 math.exp(-dist**2 / (2*sigma**2))

        # Normalize to 0-1
        if avoidance_map.max() > 0:
            avoidance_map = avoidance_map / avoidance_map.max()

        return avoidance_map

    def check_part_placement(self,
                              x: float, y: float,
                              width: float, height: float) -> Tuple[bool, float]:
        """
        Check if a part can be placed without hitting defects

        Args:
            x, y: Part position
            width, height: Part size

        Returns:
            Tuple of (is_safe, max_defect_score)
        """
        max_score = 0.0

        for defect in self.defect_map.defects:
            # Check if part intersects defect zone
            x_min, y_min, x_max, y_max = defect.bounding_box

            # Part bounds
            px_min, px_max = x, x + width
            py_min, py_max = y, y + height

            # Check intersection
            if not (px_max < x_min or px_min > x_max or
                    py_max < y_min or py_min > y_max):
                # Part intersects defect zone
                # Calculate severity of intersection
                overlap_x = min(px_max, x_max) - max(px_min, x_min)
                overlap_y = min(py_max, y_max) - max(py_min, py_min)
                overlap_area = overlap_x * overlap_y

                score = defect.severity * overlap_area / (width * height)
                max_score = max(max_score, score)

        # Safe if max_score below threshold
        threshold = 0.1  # 10% overlap threshold
        is_safe = max_score < threshold

        return is_safe, max_score

    def find_safe_positions(self,
                            width: float,
                            height: float,
                            min_gap: float = 50) -> List[Tuple[float, float]]:
        """
        Find all safe positions for a part

        Args:
            width, height: Part size
            min_gap: Minimum gap between parts

        Returns:
            List of safe (x, y) positions
        """
        safe_positions = []

        # Grid search
        step = min_gap  # Search step size

        for y in range(0, int(self.sheet_height - height), int(step)):
            for x in range(0, int(self.sheet_width - width), int(step)):
                is_safe, score = self.check_part_placement(x, y, width, height)
                if is_safe:
                    safe_positions.append((x, y, score))

        # Sort by score (lowest defect overlap first)
        safe_positions.sort(key=lambda p: p[2])

        return [(p[0], p[1]) for p in safe_positions]

    def adjust_cutting_path(self,
                            path: List[Tuple[float, float]],
                            margin: float = 10) -> List[Tuple[float, float]]:
        """
        Adjust cutting path to avoid defects

        Args:
            path: Original cutting path
            margin: Distance to keep from defects

        Returns:
            Adjusted cutting path
        """
        adjusted_path = []

        for x, y in path:
            # Check if point is near a defect
            nearest_defect = None
            min_dist = float('inf')

            for defect in self.defect_map.defects:
                dist = math.sqrt((x - defect.x)**2 + (y - defect.y)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_defect = defect

            if nearest_defect and min_dist < nearest_defect.avoidance_margin:
                # Adjust point away from defect
                # Calculate direction away from defect
                dx = x - nearest_defect.x
                dy = y - nearest_defect.y
                length = math.sqrt(dx**2 + dy**2)

                if length > 0:
                    # Normalize and scale
                    safe_dist = nearest_defect.avoidance_margin + margin
                    factor = safe_dist / length
                    new_x = nearest_defect.x + dx * factor
                    new_y = nearest_defect.y + dy * factor

                    # Ensure within bounds
                    new_x = max(0, min(self.sheet_width, new_x))
                    new_y = max(0, min(self.sheet_height, new_y))

                    adjusted_path.append((new_x, new_y))
                else:
                    adjusted_path.append((x, y))
            else:
                adjusted_path.append((x, y))

        return adjusted_path


class DefectHandler:
    """
    Main defect handling class
    Combines detection and avoidance
    """

    def __init__(self, sheet_width: float = 6000, sheet_height: float = 3000):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
        self.detector = DefectDetector()

    def process_sheet(self,
                      image_path: Optional[str] = None) -> Dict:
        """
        Process glass sheet for defect handling

        Args:
            image_path: Path to glass image

        Returns:
            Processing result
        """
        # Detect defects
        defects = self.detector.detect_defects(
            image_path, self.sheet_width, self.sheet_height
        )

        # Create defect map
        defect_map = DefectMap(
            width=self.sheet_width,
            height=self.sheet_height,
            defects=defects
        )

        # Create optimizer
        optimizer = DefectAvoidanceOptimizer(defect_map)

        # Generate avoidance map
        avoidance_map = optimizer.generate_avoidance_map()

        return {
            "defects": [
                {
                    "x": d.x,
                    "y": d.y,
                    "type": d.defect_type.value,
                    "severity": d.severity,
                    "radius": d.radius,
                    "avoidance_margin": d.avoidance_margin
                }
                for d in defects
            ],
            "defect_count": len(defects),
            "avoidance_map": avoidance_map,
            "critical_defects": [
                d for d in defects if d.severity > 0.5
            ],
            "safe_area_percentage": 100 - avoidance_map.mean() * 100
        }

    def optimize_with_defects(self,
                              placed_parts: List[Dict],
                              defects: List[Defect]) -> List[Dict]:
        """
        Re-optimize placements considering defects

        Args:
            placed_parts: Original placements
            defects: Detected defects

        Returns:
            Adjusted placements
        """
        defect_map = DefectMap(
            width=self.sheet_width,
            height=self.sheet_height,
            defects=defects
        )
        optimizer = DefectAvoidanceOptimizer(defect_map)

        adjusted_parts = []
        rejected_parts = []

        for part in placed_parts:
            x = part["x"]
            y = part["y"]
            w = part.get("placed_width", part.get("width", 100))
            h = part.get("placed_height", part.get("height", 100))

            is_safe, score = optimizer.check_part_placement(x, y, w, h)

            if is_safe:
                adjusted_parts.append(part)
            else:
                # Try to find alternative position
                safe_positions = optimizer.find_safe_positions(w, h)

                if safe_positions:
                    new_x, new_y = safe_positions[0]
                    adjusted_part = {**part, "x": new_x, "y": new_y}
                    adjusted_parts.append(adjusted_part)
                else:
                    rejected_parts.append(part)

        return adjusted_parts, rejected_parts


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Defect Handler Demo")
    print("=" * 60)

    # Create handler
    handler = DefectHandler(6000, 3000)

    # Process sheet (simulated defects)
    result = handler.process_sheet()

    print(f"\nDefects detected: {result['defect_count']}")
    print(f"Safe area: {result['safe_area_percentage']:.1f}%")

    print("\nDefect details:")
    for d in result['defects']:
        print(f"  {d['type']} at ({d['x']:.0f}, {d['y']:.0f}) "
              f"severity={d['severity']:.2f} radius={d['radius']:.0f}mm")

    # Test part placement
    print("\n--- Testing placements ---")
    test_parts = [
        {"x": 0, "y": 0, "width": 500, "height": 400, "order_id": "P1"},
        {"x": 1000, "y": 1000, "width": 300, "height": 200, "order_id": "P2"},
    ]

    defects = [Defect(d['x'], d['y'], DefectType(d['type']),
                      d['severity'], d['radius']) for d in result['defects']]

    adjusted, rejected = handler.optimize_with_defects(test_parts, defects)

    print(f"Adjusted: {len(adjusted)}, Rejected: {len(rejected)}")

    for part in adjusted:
        print(f"  {part['order_id']}: ({part['x']:.0f}, {part['y']:.0f})")


if __name__ == "__main__":
    demo()