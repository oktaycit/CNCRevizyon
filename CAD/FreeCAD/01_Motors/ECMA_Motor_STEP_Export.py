# FreeCAD ECMA Motor STEP Export Script
# Delta ECMA Servo Motorları için STEP Dosyası Oluşturucu
# CNC Revizyon Projesi - GFB-60/30RE

import FreeCAD as App
import Part
import math
import os

# Export dizinini oluştur (exec ile çalıştırıldığında __file__ tanımlı değil)
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/01_Motors"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "Motors")
os.makedirs(EXPORT_DIR, exist_ok=True)

def create_cylinder(doc, name, radius, height, position=(0, 0, 0)):
    """Silindir oluştur"""
    cylinder = Part.makeCylinder(radius, height, 
                                  App.Vector(position[0], position[1], position[2]),
                                  App.Vector(0, 0, 1))
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = cylinder
    return shape

def create_motor_housing(doc, name, outer_radius, inner_radius, length, position=(0, 0, 0)):
    """Motor gövdesi oluştur (içi boş silindir)"""
    outer = Part.makeCylinder(outer_radius, length,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    inner = Part.makeCylinder(inner_radius, length,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    housing = outer.cut(inner)
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = housing
    return shape

def create_flange(doc, name, outer_radius, inner_radius, thickness, 
                  bolt_pcd, bolt_hole_radius, num_bolts, position=(0, 0, 0)):
    """Montaj flanşı oluştur"""
    outer = Part.makeCylinder(outer_radius, thickness,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    if inner_radius > 0:
        inner = Part.makeCylinder(inner_radius, thickness,
                                   App.Vector(position[0], position[1], position[2]),
                                   App.Vector(0, 0, 1))
        outer = outer.cut(inner)
    
    for i in range(num_bolts):
        angle = 2 * math.pi * i / num_bolts
        hole_x = bolt_pcd * math.cos(angle)
        hole_y = bolt_pcd * math.sin(angle)
        hole = Part.makeCylinder(bolt_hole_radius, thickness,
                                  App.Vector(position[0] + hole_x, position[1] + hole_y, position[2]),
                                  App.Vector(0, 0, 1))
        outer = outer.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = outer
    return shape

def create_shaft(doc, name, radius, length, keyway_width=0, keyway_depth=0, position=(0, 0, 0)):
    """Motor mili oluştur (kama yuvası opsiyonel)"""
    shaft = Part.makeCylinder(radius, length,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    
    if keyway_width > 0 and keyway_depth > 0:
        keyway = Part.makeBox(keyway_width, keyway_depth, length,
                               App.Vector(position[0] - keyway_width/2, 
                                         position[1] + radius - keyway_depth,
                                         position[2]))
        shaft = shaft.cut(keyway)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = shaft
    return shape

def create_connector_housing(doc, name, width, height, depth, position=(0, 0, 0)):
    """Konektör kabuğu oluştur"""
    box = Part.makeBox(width, height, depth,
                        App.Vector(position[0] - width/2, position[1] - height/2, position[2]))
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = box
    return shape

def create_brake(doc, name, outer_radius, inner_radius, thickness, position=(0, 0, 0)):
    """Fren ünitesi oluştur"""
    brake = Part.makeCylinder(outer_radius, thickness,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    if inner_radius > 0:
        hole = Part.makeCylinder(inner_radius, thickness,
                                  App.Vector(position[0], position[1], position[2]),
                                  App.Vector(0, 0, 1))
        brake = brake.cut(hole)
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = brake
    return shape

def fuse_shapes(doc, name, shapes):
    """Birden fazla şekli birleştir"""
    if len(shapes) < 2:
        return shapes[0]
    
    result = shapes[0].Shape.fuse(shapes[1].Shape)
    for i in range(2, len(shapes)):
        result = result.fuse(shapes[i].Shape)
    
    fused = doc.addObject("Part::Feature", name)
    fused.Shape = result
    return fused

def export_to_step(doc, motor, filename):
    """Motoru STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([motor], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_ecma_l11845(doc, name="ECMA-L11845", export=True):
    """ECMA-L11845 (4.5kW X Ekseni) Motor Modeli"""
    housing = create_motor_housing(doc, f"{name}_Housing", 90, 65, 215, (0, 0, 0))
    flange = create_flange(doc, f"{name}_Flange", 90, 65, 10, 107.5, 7, 4, (0, 0, -10))
    shaft = create_shaft(doc, f"{name}_Shaft", 24, 110, 14, 9, (0, 0, 215))
    connector = create_connector_housing(doc, f"{name}_Connector", 60, 40, 50, (0, 70, 100))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    if export:
        export_to_step(doc, motor, f"{name}.stp")
    
    return motor

def create_ecma_e11320(doc, name="ECMA-E11320", export=True):
    """ECMA-E11320 (2.0kW Y/Alt Ekseni) Motor Modeli"""
    housing = create_motor_housing(doc, f"{name}_Housing", 65, 45, 170, (0, 0, 0))
    flange = create_flange(doc, f"{name}_Flange", 65, 45, 8, 82.5, 6, 4, (0, 0, -8))
    shaft = create_shaft(doc, f"{name}_Shaft", 12, 50, 8, 4, (0, 0, 170))
    connector = create_connector_housing(doc, f"{name}_Connector", 50, 35, 45, (0, 55, 80))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    if export:
        export_to_step(doc, motor, f"{name}.stp")
    
    return motor

def create_ecma_c11010_brake(doc, name="ECMA-C11010", export=True):
    """ECMA-C11010 (1.0kW Frenli Z Ekseni) Motor Modeli"""
    housing = create_motor_housing(doc, f"{name}_Housing", 50, 35, 125, (0, 0, 0))
    flange = create_flange(doc, f"{name}_Flange", 50, 35, 8, 65, 5.5, 4, (0, 0, -8))
    shaft = create_shaft(doc, f"{name}_Shaft", 12, 50, 8, 4, (0, 0, 125))
    brake = create_brake(doc, f"{name}_Brake", 45, 20, 40, (0, 0, -48))
    connector = create_connector_housing(doc, f"{name}_Connector", 45, 30, 40, (0, 45, 60))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, brake, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    if export:
        export_to_step(doc, motor, f"{name}.stp")
    
    return motor

def create_ecma_e11315(doc, name="ECMA-E11315", export=True):
    """ECMA-E11315 (1.5kW IP67) Motor Modeli"""
    housing = create_motor_housing(doc, f"{name}_Housing", 65, 45, 155, (0, 0, 0))
    flange = create_flange(doc, f"{name}_Flange", 65, 45, 8, 82.5, 6, 4, (0, 0, -8))
    shaft = create_shaft(doc, f"{name}_Shaft", 12, 50, 8, 4, (0, 0, 155))
    connector = create_connector_housing(doc, f"{name}_Connector", 50, 35, 45, (0, 55, 75))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    if export:
        export_to_step(doc, motor, f"{name}.stp")
    
    return motor

def create_all_motors_with_export():
    """Tüm motorları oluştur ve STEP dosyalarını export et"""
    print("=" * 50)
    print("ECMA Motor STEP Export Script")
    print("=" * 50)
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # Her motor için ayrı doküman oluştur
    motors_created = []
    
    # ECMA-L11845
    print("ECMA-L11845 (4.5kW) oluşturuluyor...")
    doc1 = App.newDocument("ECMA_L11845")
    motor1 = create_ecma_l11845(doc1, export=True)
    doc1.recompute()
    motors_created.append(("ECMA-L11845", doc1))
    
    # ECMA-E11320
    print("ECMA-E11320 (2.0kW) oluşturuluyor...")
    doc2 = App.newDocument("ECMA_E11320")
    motor2 = create_ecma_e11320(doc2, export=True)
    doc2.recompute()
    motors_created.append(("ECMA-E11320", doc2))
    
    # ECMA-C11010
    print("ECMA-C11010 (1.0kW Frenli) oluşturuluyor...")
    doc3 = App.newDocument("ECMA_C11010")
    motor3 = create_ecma_c11010_brake(doc3, export=True)
    doc3.recompute()
    motors_created.append(("ECMA-C11010", doc3))
    
    # ECMA-E11315
    print("ECMA-E11315 (1.5kW IP67) oluşturuluyor...")
    doc4 = App.newDocument("ECMA_E11315")
    motor4 = create_ecma_e11315(doc4, export=True)
    doc4.recompute()
    motors_created.append(("ECMA-E11315", doc4))
    
    print()
    print("=" * 50)
    print("Tüm motorlar ve STEP dosyaları başarıyla oluşturuldu!")
    print("=" * 50)
    
    # Aktif dokümanı ilk motor yap
    App.ActiveDocument = doc1
    
    return motors_created

def create_motor_assembly():
    """Tüm motorları tek montaj dosyasında oluştur"""
    print("Motor montaj dosyası oluşturuluyor...")
    
    doc = App.newDocument("ECMA_Motor_Assembly")
    doc.Label = "ECMA Motor Assembly"
    
    # Motorları farklı pozisyonlarda yerleştir
    create_ecma_l11845(doc, export=False)
    
    # ECMA-E11320'yi X ekseni boyunca kaydır
    doc2 = App.newDocument("Temp_E11320")
    m2 = create_ecma_e11320(doc2, export=False)
    # Kopyala ve taşı
    doc2.recompute()
    App.closeDocument("Temp_E11320")
    
    # ECMA-C11010'ı Y ekseni boyunca kaydır
    doc3 = App.newDocument("Temp_C11010")
    m3 = create_ecma_c11010_brake(doc3, export=False)
    doc3.recompute()
    App.closeDocument("Temp_C11010")
    
    # ECMA-E11315'i Z ekseni boyunca kaydır
    doc4 = App.newDocument("Temp_E11315")
    m4 = create_ecma_e11315(doc4, export=False)
    doc4.recompute()
    App.closeDocument("Temp_E11315")
    
    doc.recompute()
    App.ActiveDocument = doc
    
    print("Montaj dosyası hazır!")
    return doc

# Script'i çalıştır
if __name__ == "__main__":
    create_all_motors_with_export()