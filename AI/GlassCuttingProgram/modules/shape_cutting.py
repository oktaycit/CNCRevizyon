#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Shape Cutting Module
Non-rectangular shape cutting for glass

Supports:
- Circles
- Polygons (triangle, hexagon, etc.)
- Arcs
- Custom shapes
"""

import math
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional


@dataclass
class ShapeVertex:
    """Vertex in a shape"""
    x: float
    y: float
    cut_type: str = "linear"  # linear, arc_cw, arc_ccw
    radius: Optional[float] = None  # For arc moves


@dataclass
class ShapeDefinition:
    """Shape definition"""
    shape_id: str
    shape_type: str  # circle, polygon, arc, custom
    base_x: float
    base_y: float
    vertices: List[ShapeVertex]
    parameters: Dict = field(default_factory=dict)
    
    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Calculate bounding box (x_min, y_min, x_max, y_max)"""
        xs = [v.x for v in self.vertices]
        ys = [v.y for v in self.vertices]
        return (min(xs), min(ys), max(xs), max(ys))
    
    @property
    def perimeter(self) -> float:
        """Calculate perimeter length"""
        total = 0.0
        for i in range(len(self.vertices)):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % len(self.vertices)]
            dx = v2.x - v1.x
            dy = v2.y - v1.y
            total += math.sqrt(dx*dx + dy*dy)
        return total


class ShapeGenerator:
    """Generate standard shapes"""
    
    @staticmethod
    def create_circle(center_x: float, center_y: float,
                      radius: float, num_points: int = 36,
                      shape_id: str = "circle") -> ShapeDefinition:
        """
        Create circular shape
        
        Args:
            center_x, center_y: Circle center
            radius: Circle radius
            num_points: Number of points (higher = smoother)
            shape_id: Shape identifier
        
        Returns:
            ShapeDefinition
        """
        vertices = []
        angle_step = 360 / num_points
        
        for i in range(num_points):
            angle = math.radians(i * angle_step)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            vertices.append(ShapeVertex(x, y, "linear"))
        
        return ShapeDefinition(
            shape_id=shape_id,
            shape_type="circle",
            base_x=center_x,
            base_y=center_y,
            vertices=vertices,
            parameters={"radius": radius, "num_points": num_points}
        )
    
    @staticmethod
    def create_polygon(center_x: float, center_y: float,
                       radius: float, num_sides: int,
                       shape_id: str = "polygon") -> ShapeDefinition:
        """
        Create regular polygon
        
        Args:
            center_x, center_y: Polygon center
            radius: Circumradius
            num_sides: Number of sides (3=triangle, 6=hexagon, etc.)
            shape_id: Shape identifier
        
        Returns:
            ShapeDefinition
        """
        vertices = []
        angle_step = 360 / num_sides
        
        # Rotate so first vertex is at top
        angle_offset = -90
        
        for i in range(num_sides):
            angle = math.radians(i * angle_step + angle_offset)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            vertices.append(ShapeVertex(x, y, "linear"))
        
        return ShapeDefinition(
            shape_id=shape_id,
            shape_type="polygon",
            base_x=center_x,
            base_y=center_y,
            vertices=vertices,
            parameters={"num_sides": num_sides, "radius": radius}
        )
    
    @staticmethod
    def create_rectangle(x: float, y: float,
                         width: float, height: float,
                         shape_id: str = "rectangle") -> ShapeDefinition:
        """
        Create rectangle
        
        Args:
            x, y: Bottom-left corner
            width, height: Dimensions
        
        Returns:
            ShapeDefinition
        """
        vertices = [
            ShapeVertex(x, y, "linear"),
            ShapeVertex(x + width, y, "linear"),
            ShapeVertex(x + width, y + height, "linear"),
            ShapeVertex(x, y + height, "linear"),
        ]
        
        return ShapeDefinition(
            shape_id=shape_id,
            shape_type="rectangle",
            base_x=x,
            base_y=y,
            vertices=vertices,
            parameters={"width": width, "height": height}
        )
    
    @staticmethod
    def create_arc(center_x: float, center_y: float,
                   radius: float, start_angle: float,
                   end_angle: float, clockwise: bool = True,
                   shape_id: str = "arc") -> ShapeDefinition:
        """
        Create arc shape
        
        Args:
            center_x, center_y: Arc center
            radius: Arc radius
            start_angle: Start angle (degrees)
            end_angle: End angle (degrees)
            clockwise: Direction
            shape_id: Shape identifier
        
        Returns:
            ShapeDefinition
        """
        vertices = []
        
        # Create multiple points along arc
        angle_step = 5  # degrees
        if clockwise:
            if end_angle < start_angle:
                end_angle += 360
            angles = list(range(int(start_angle), int(end_angle) + 1, angle_step))
        else:
            if start_angle < end_angle:
                start_angle += 360
            angles = list(range(int(start_angle), int(end_angle) - 1, -angle_step))
        
        for angle in angles:
            rad = math.radians(angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)
            cut_type = "arc_cw" if clockwise else "arc_ccw"
            vertices.append(ShapeVertex(x, y, cut_type, radius=radius))
        
        return ShapeDefinition(
            shape_id=shape_id,
            shape_type="arc",
            base_x=center_x,
            base_y=center_y,
            vertices=vertices,
            parameters={
                "radius": radius,
                "start_angle": start_angle,
                "end_angle": end_angle,
                "clockwise": clockwise
            }
        )
    
    @staticmethod
    def create_custom_shape(base_x: float, base_y: float,
                            points: List[Tuple[float, float]],
                            shape_id: str = "custom") -> ShapeDefinition:
        """
        Create custom shape from points
        
        Args:
            base_x, base_y: Base position
            points: List of (dx, dy) relative coordinates
            shape_id: Shape identifier
        
        Returns:
            ShapeDefinition
        """
        vertices = []
        for dx, dy in points:
            vertices.append(ShapeVertex(base_x + dx, base_y + dy, "linear"))
        
        return ShapeDefinition(
            shape_id=shape_id,
            shape_type="custom",
            base_x=base_x,
            base_y=base_y,
            vertices=vertices,
            parameters={"num_points": len(points)}
        )


class ShapeNestingOptimizer:
    """
    Nesting optimizer for shaped parts
    Uses bounding box approximation
    """
    
    def __init__(self, sheet_width: float, sheet_height: float):
        self.sheet_width = sheet_width
        self.sheet_height = sheet_height
    
    def can_place(self, shape: ShapeDefinition,
                  x: float, y: float) -> bool:
        """
        Check if shape can be placed at position
        
        Args:
            shape: Shape to place
            x, y: Position
        
        Returns:
            True if can be placed
        """
        # Get bounding box
        x_min, y_min, x_max, y_max = shape.bounding_box
        
        # Translate to placement position
        translate_x = x - shape.base_x
        translate_y = y - shape.base_y
        
        # Check bounds
        if x_min + translate_x < 0:
            return False
        if y_min + translate_y < 0:
            return False
        if x_max + translate_x > self.sheet_width:
            return False
        if y_max + translate_y > self.sheet_height:
            return False
        
        return True
    
    def nest_shapes(self, shapes: List[ShapeDefinition]) -> List[Tuple[ShapeDefinition, float, float]]:
        """
        Nest shapes on sheet
        
        Args:
            shapes: List of shapes to place
        
        Returns:
            List of (shape, x, y) placements
        """
        placements = []
        placed = []  # List of (x, y, bounding_box)
        
        for shape in shapes:
            # Try to find placement
            placed_flag = False
            
            # Grid search
            step = 50  # mm
            for y in range(0, int(self.sheet_height), step):
                for x in range(0, int(self.sheet_width), step):
                    if self.can_place(shape, x, y):
                        # Check collision with placed shapes
                        collision = False
                        x_min, y_min, x_max, y_max = shape.bounding_box
                        translate_x = x - shape.base_x
                        translate_y = y - shape.base_y
                        
                        for px, py, (px_min, py_min, px_max, py_max) in placed:
                            # Simple bounding box collision
                            if not (x_max + translate_x < px_min or
                                   px_max < x_min + translate_x or
                                   y_max + translate_y < py_min or
                                   py_max < y_min + translate_y):
                                collision = True
                                break
                        
                        if not collision:
                            placements.append((shape, x, y))
                            placed.append((x, y, (x_min + translate_x, y_min + translate_y,
                                                  x_max + translate_x, y_max + translate_y)))
                            placed_flag = True
                            break
                
                if placed_flag:
                    break
            
            if not placed_flag:
                print(f"Warning: Could not place shape {shape.shape_id}")
        
        return placements


def demo():
    """Demo usage"""
    print("=" * 60)
    print("Shape Cutting Demo")
    print("=" * 60)
    
    # Create shapes
    generator = ShapeGenerator()
    
    # Circle
    circle = generator.create_circle(3000, 1500, 500, shape_id="C1")
    print(f"\nCircle: {circle.shape_id}")
    print(f"  Perimeter: {circle.perimeter:.1f} mm")
    print(f"  Bounding box: {circle.bounding_box}")
    
    # Hexagon
    hexagon = generator.create_polygon(1500, 1500, 400, 6, shape_id="H1")
    print(f"\nHexagon: {hexagon.shape_id}")
    print(f"  Perimeter: {hexagon.perimeter:.1f} mm")
    print(f"  Vertices: {len(hexagon.vertices)}")
    
    # Triangle
    triangle = generator.create_polygon(4500, 1500, 400, 3, shape_id="T1")
    print(f"\nTriangle: {triangle.shape_id}")
    print(f"  Perimeter: {triangle.perimeter:.1f} mm")
    
    # Arc
    arc = generator.create_arc(3000, 2500, 600, 0, 90, shape_id="A1")
    print(f"\nArc: {arc.shape_id}")
    print(f"  Vertices: {len(arc.vertices)}")
    
    # Nesting
    print("\n--- Nesting Test ---")
    optimizer = ShapeNestingOptimizer(6000, 3000)
    placements = optimizer.nest_shapes([circle, hexagon, triangle])
    
    print(f"Placed {len(placements)} shapes:")
    for shape, x, y in placements:
        print(f"  {shape.shape_id}: ({x}, {y})")


if __name__ == "__main__":
    demo()
