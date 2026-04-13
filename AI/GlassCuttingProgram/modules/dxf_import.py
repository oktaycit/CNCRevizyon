#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
"""
DXF Import Module
AutoCAD DXF file parser for glass cutting shapes

Requirements:
    pip install ezdxf

Supports:
    - LINE, ARC, CIRCLE entities
    - POLYLINE, LWPOLYLINE
    - Layer filtering
    - Scale conversion
    - Multiple shapes per file
"""

import math
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field

try:
    import ezdxf
    from ezdxf.entities import Line, Arc, Circle, Polyline, LWPolyline
    EZDXF_AVAILABLE = True
except ImportError:
    EZDXF_AVAILABLE = False
    print("Warning: ezdxf not installed. Run: pip install ezdxf")


@dataclass
class DXFShape:
    """Shape extracted from DXF"""
    shape_id: str
    shape_type: str  # line, arc, circle, polyline
    layer: str
    points: List[Tuple[float, float]]
    parameters: Dict = field(default_factory=dict)
    
    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """Calculate bounding box"""
        if not self.points:
            return (0, 0, 0, 0)
        
        xs = [p[0] for p in self.points]
        ys = [p[1] for p in self.points]
        return (min(xs), min(ys), max(xs), max(ys))
    
    @property
    def perimeter(self) -> float:
        """Calculate approximate perimeter"""
        if len(self.points) < 2:
            return 0
        
        total = 0
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            total += math.sqrt(dx*dx + dy*dy)
        
        return total


@dataclass
class DXFImportResult:
    """Result of DXF import"""
    success: bool
    shapes: List[DXFShape]
    total_shapes: int
    layers: List[str]
    errors: List[str]
    file_info: Dict


class DXFParser:
    """Parse AutoCAD DXF files"""
    
    # Supported entity types
    SUPPORTED_ENTITIES = {'LINE', 'ARC', 'CIRCLE', 'POLYLINE', 'LWPOLYLINE'}
    
    def __init__(self, scale: float = 1.0, units: str = 'mm'):
        """
        Initialize DXF parser
        
        Args:
            scale: Scale factor (drawing units to mm)
            units: Drawing units ('mm', 'cm', 'm', 'inch')
        """
        self.scale = scale
        self.units = units
        self.errors: List[str] = []
        
        # Auto scale based on units
        if units == 'mm':
            self.scale = 1.0
        elif units == 'cm':
            self.scale = 10.0
        elif units == 'm':
            self.scale = 1000.0
        elif units == 'inch':
            self.scale = 25.4
    
    def parse(self, file_path: str, layer_filter: Optional[List[str]] = None) -> DXFImportResult:
        """
        Parse DXF file
        
        Args:
            file_path: Path to DXF file
            layer_filter: Optional list of layers to import
        
        Returns:
            DXFImportResult
        """
        if not EZDXF_AVAILABLE:
            return DXFImportResult(
                success=False,
                shapes=[],
                total_shapes=0,
                layers=[],
                errors=["ezdxf library not installed"],
                file_info={}
            )
        
        self.errors = []
        shapes = []
        layers = set()
        
        try:
            # Read DXF file
            doc = ezdxf.readfile(file_path)
            msp = doc.modelspace()
            
            # Get all layers
            for layer in doc.layers:
                layers.add(layer.dxf.name)
            
            # Filter layers if specified
            if layer_filter:
                layers = set(l for l in layers if l in layer_filter)
            
            # Parse entities
            shape_count = 0
            for entity in msp:
                if entity.dxftype() not in self.SUPPORTED_ENTITIES:
                    continue
                
                # Check layer filter
                if entity.dxf.layer not in layers:
                    continue
                
                try:
                    shape = self._parse_entity(entity, shape_count)
                    if shape:
                        shapes.append(shape)
                        shape_count += 1
                except Exception as e:
                    self.errors.append(f"Error parsing entity {shape_count}: {str(e)}")
            
            file_info = {
                'filename': Path(file_path).name,
                'dxf_version': doc.dxfversion,
                'units': self.units,
                'scale': self.scale,
                'entity_count': len(list(msp)),
                'imported_count': shape_count
            }
            
            return DXFImportResult(
                success=True,
                shapes=shapes,
                total_shapes=len(shapes),
                layers=list(layers),
                errors=self.errors,
                file_info=file_info
            )
            
        except Exception as e:
            self.errors.append(f"File parse error: {str(e)}")
            return DXFImportResult(
                success=False,
                shapes=[],
                total_shapes=0,
                layers=[],
                errors=self.errors,
                file_info={}
            )
    
    def _parse_entity(self, entity, index: int) -> Optional[DXFShape]:
        """Parse single entity"""
        dxftype = entity.dxftype()
        
        if dxftype == 'LINE':
            return self._parse_line(entity, index)
        elif dxftype == 'ARC':
            return self._parse_arc(entity, index)
        elif dxftype == 'CIRCLE':
            return self._parse_circle(entity, index)
        elif dxftype in ('POLYLINE', 'LWPOLYLINE'):
            return self._parse_polyline(entity, index)
        
        return None
    
    def _parse_line(self, entity: Line, index: int) -> DXFShape:
        """Parse LINE entity"""
        start = entity.dxf.start
        end = entity.dxf.end
        
        points = [
            (float(start[0]) * self.scale, float(start[1]) * self.scale),
            (float(end[0]) * self.scale, float(end[1]) * self.scale)
        ]
        
        return DXFShape(
            shape_id=f"LINE_{index}",
            shape_type="line",
            layer=entity.dxf.layer,
            points=points,
            parameters={
                'length': math.sqrt((end[0]-start[0])**2 + (end[1]-start[1])**2) * self.scale
            }
        )
    
    def _parse_arc(self, entity: Arc, index: int) -> DXFShape:
        """Parse ARC entity"""
        center = entity.dxf.center
        radius = float(entity.dxf.radius) * self.scale
        start_angle = float(entity.dxf.start_angle)
        end_angle = float(entity.dxf.end_angle)
        
        # Generate points along arc
        points = []
        angle_step = 5  # degrees
        if end_angle < start_angle:
            end_angle += 2 * math.pi
        
        current_angle = start_angle
        while current_angle <= end_angle:
            x = float(center[0]) + radius * math.cos(current_angle)
            y = float(center[1]) + radius * math.sin(current_angle)
            points.append((x * self.scale, y * self.scale))
            current_angle += math.radians(angle_step)
        
        return DXFShape(
            shape_id=f"ARC_{index}",
            shape_type="arc",
            layer=entity.dxf.layer,
            points=points,
            parameters={
                'center': (float(center[0]) * self.scale, float(center[1]) * self.scale),
                'radius': radius,
                'start_angle': math.degrees(start_angle),
                'end_angle': math.degrees(end_angle),
                'arc_length': radius * (end_angle - start_angle)
            }
        )
    
    def _parse_circle(self, entity: Circle, index: int) -> DXFShape:
        """Parse CIRCLE entity"""
        center = entity.dxf.center
        radius = float(entity.dxf.radius) * self.scale
        
        # Generate points around circle
        points = []
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            x = float(center[0]) + radius * math.cos(rad)
            y = float(center[1]) + radius * math.sin(rad)
            points.append((x * self.scale, y * self.scale))
        points.append(points[0])  # Close circle
        
        return DXFShape(
            shape_id=f"CIRCLE_{index}",
            shape_type="circle",
            layer=entity.dxf.layer,
            points=points,
            parameters={
                'center': (float(center[0]) * self.scale, float(center[1]) * self.scale),
                'radius': radius,
                'circumference': 2 * math.pi * radius
            }
        )
    
    def _parse_polyline(self, entity, index: int) -> DXFShape:
        """Parse POLYLINE or LWPOLYLINE entity"""
        points = []
        
        try:
            for vertex in entity:
                x = float(vertex[0]) * self.scale
                y = float(vertex[1]) * self.scale
                points.append((x, y))
            
            # Close polyline if needed
            if entity.is_closed and points:
                points.append(points[0])
            
        except Exception as e:
            self.errors.append(f"Polyline parse error: {str(e)}")
            return None
        
        return DXFShape(
            shape_id=f"POLY_{index}",
            shape_type="polyline",
            layer=entity.dxf.layer,
            points=points,
            parameters={
                'vertex_count': len(points),
                'is_closed': entity.is_closed
            }
        )


class DXFToShapeConverter:
    """Convert DXF shapes to GlassCuttingProgram shapes"""
    
    def __init__(self):
        pass
    
    def convert(self, dxf_shapes: List[DXFShape], 
                base_x: float = 0, base_y: float = 0) -> List[Dict]:
        """
        Convert DXF shapes to program shapes
        
        Args:
            dxf_shapes: List of DXFShape objects
            base_x, base_y: Offset for placement on sheet
        
        Returns:
            List of shape dictionaries
        """
        converted = []
        
        for dxf_shape in dxf_shapes:
            shape = {
                'shape_id': dxf_shape.shape_id,
                'shape_type': dxf_shape.shape_type,
                'layer': dxf_shape.layer,
                'base_x': base_x,
                'base_y': base_y,
                'points': dxf_shape.points,
                'parameters': dxf_shape.parameters,
                'bounding_box': dxf_shape.bounding_box,
                'perimeter': dxf_shape.perimeter
            }
            converted.append(shape)
        
        return converted


def demo():
    """Demo usage"""
    print("=" * 60)
    print("DXF Import Demo")
    print("=" * 60)
    
    if not EZDXF_AVAILABLE:
        print("\n❌ ezdxf not installed!")
        print("   Run: pip install ezdxf")
        return
    
    # Create parser
    parser = DXFParser(units='mm')
    
    # Test file path
    test_file = Path(__file__).parent.parent / 'data' / 'test.dxf'
    
    if not test_file.exists():
        print(f"\n⚠️ Test file not found: {test_file}")
        print("   Please provide a DXF file for testing")
        
        # Show example usage
        print("\n📖 Usage Example:")
        print("""
from modules.dxf_import import DXFParser, DXFToShapeConverter

# Parse DXF
parser = DXFParser(units='mm')
result = parser.parse('path/to/file.dxf')

if result.success:
    print(f"Imported {result.total_shapes} shapes")
    print(f"Layers: {result.layers}")
    
    # Convert to program shapes
    converter = DXFToShapeConverter()
    shapes = converter.convert(result.shapes, base_x=100, base_y=100)
    
    for shape in shapes:
        print(f"  {shape['shape_id']}: {shape['shape_type']} - {len(shape['points'])} points")
""")
        return
    
    # Parse file
    print(f"\n📂 Parsing: {test_file}")
    result = parser.parse(str(test_file))
    
    if result.success:
        print(f"\n✅ Import successful!")
        print(f"   Shapes: {result.total_shapes}")
        print(f"   Layers: {', '.join(result.layers)}")
        print(f"   Entities in file: {result.file_info.get('entity_count', 0)}")
        
        if result.errors:
            print(f"\n⚠️ Errors: {len(result.errors)}")
            for err in result.errors[:5]:
                print(f"   - {err}")
        
        # Show shapes
        print(f"\n📐 Shapes:")
        for shape in result.shapes[:10]:
            print(f"   {shape.shape_id}: {shape.shape_type}")
            print(f"      Layer: {shape.layer}")
            print(f"      Points: {len(shape.points)}")
            print(f"      Perimeter: {shape.perimeter:.1f}mm")
            print(f"      Bounding: {shape.bounding_box}")
        
        # Convert to program shapes
        print(f"\n🔄 Converting to program shapes...")
        converter = DXFToShapeConverter()
        program_shapes = converter.convert(result.shapes)
        
        print(f"   Converted {len(program_shapes)} shapes")
        
    else:
        print(f"\n❌ Import failed!")
        for err in result.errors:
            print(f"   - {err}")


if __name__ == "__main__":
    demo()
