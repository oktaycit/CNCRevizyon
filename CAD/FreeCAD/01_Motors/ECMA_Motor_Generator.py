# FreeCAD ECMA Motor Model Generator
# Delta ECMA Servo Motorları için Parametrik Modelleme Scripti
# CNC Revizyon Projesi - GFB-60/30RE

import FreeCAD as App
import Part
import math

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
    # Dış silindir
    outer = Part.makeCylinder(outer_radius, length,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    # İç silindir (boşluk için)
    inner = Part.makeCylinder(inner_radius, length,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    # Boolean cut ile içi boş gövde
    housing = outer.cut(inner)
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = housing
    return shape

def create_flange(doc, name, outer_radius, inner_radius, thickness, 
                  bolt_pcd, bolt_hole_radius, num_bolts, position=(0, 0, 0)):
    """Montaj flanşı oluştur"""
    # Ana flanş diski
    outer = Part.makeCylinder(outer_radius, thickness,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    # Merkez delik
    if inner_radius > 0:
        inner = Part.makeCylinder(inner_radius, thickness,
                                   App.Vector(position[0], position[1], position[2]),
                                   App.Vector(0, 0, 1))
        outer = outer.cut(inner)
    
    # Cıvata delikleri
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
    # Ana mil
    shaft = Part.makeCylinder(radius, length,
                               App.Vector(position[0], position[1], position[2]),
                               App.Vector(0, 0, 1))
    
    # Kama yuvası (keyway)
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
    # Merkez delik
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

def create_ecma_l11845(doc, name="ECMA-L11845"):
    """
    ECMA-L11845 (4.5kW X Ekseni) Motor Modeli
    Flanş: 180 mm, Mil Çapı: 48 mm, Mil Uzunluğu: 110 mm
    Gövde Uzunluğu: 215 mm (frensiz), Toplam: 340 mm (konektörlü)
    """
    # Gövde (içi boş)
    housing = create_motor_housing(doc, f"{name}_Housing", 
                                    90, 65, 215, (0, 0, 0))
    
    # Arka flanş
    flange = create_flange(doc, f"{name}_Flange",
                           90, 65, 10,
                           107.5, 7, 4, (0, 0, -10))
    
    # Mil
    shaft = create_shaft(doc, f"{name}_Shaft",
                         24, 110, 14, 9, (0, 0, 215))
    
    # Konektör kabuğu
    connector = create_connector_housing(doc, f"{name}_Connector",
                                          60, 40, 50, (0, 70, 100))
    
    # Tüm parçaları birleştir
    motor = fuse_shapes(doc, name, [housing, flange, shaft, connector])
    
    # Malzeme rengi (gri)
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    return motor

def create_ecma_e11320(doc, name="ECMA-E11320"):
    """
    ECMA-E11320 (2.0kW Y/Alt Ekseni) Motor Modeli
    Flanş: 130 mm, Mil Çapı: 24 mm
    """
    # Gövde
    housing = create_motor_housing(doc, f"{name}_Housing",
                                    65, 45, 170, (0, 0, 0))
    
    # Arka flanş
    flange = create_flange(doc, f"{name}_Flange",
                           65, 45, 8,
                           82.5, 6, 4, (0, 0, -8))
    
    # Mil
    shaft = create_shaft(doc, f"{name}_Shaft",
                         12, 50, 8, 4, (0, 0, 170))
    
    # Konektör
    connector = create_connector_housing(doc, f"{name}_Connector",
                                          50, 35, 45, (0, 55, 80))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    return motor

def create_ecma_c11010_brake(doc, name="ECMA-C11010"):
    """
    ECMA-C11010 (1.0kW Frenli Z Ekseni) Motor Modeli
    Flanş: 100 mm, Mil Çapı: 24 mm, Fren Çapı: Ø90 mm
    """
    # Gövde
    housing = create_motor_housing(doc, f"{name}_Housing",
                                    50, 35, 125, (0, 0, 0))
    
    # Arka flanş
    flange = create_flange(doc, f"{name}_Flange",
                           50, 35, 8,
                           65, 5.5, 4, (0, 0, -8))
    
    # Mil
    shaft = create_shaft(doc, f"{name}_Shaft",
                         12, 50, 8, 4, (0, 0, 125))
    
    # Fren ünitesi (arka tarafa)
    brake = create_brake(doc, f"{name}_Brake",
                         45, 20, 40, (0, 0, -48))
    
    # Konektör
    connector = create_connector_housing(doc, f"{name}_Connector",
                                          45, 30, 40, (0, 45, 60))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, brake, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    return motor

def create_ecma_e11315(doc, name="ECMA-E11315"):
    """
    ECMA-E11315 (1.5kW IP67) Motor Modeli
    Flanş: 130 mm, Mil Çapı: 24 mm
    """
    # Gövde
    housing = create_motor_housing(doc, f"{name}_Housing",
                                    65, 45, 155, (0, 0, 0))
    
    # Arka flanş
    flange = create_flange(doc, f"{name}_Flange",
                           65, 45, 8,
                           82.5, 6, 4, (0, 0, -8))
    
    # Mil
    shaft = create_shaft(doc, f"{name}_Shaft",
                         12, 50, 8, 4, (0, 0, 155))
    
    # Konektör
    connector = create_connector_housing(doc, f"{name}_Connector",
                                          50, 35, 45, (0, 55, 75))
    
    motor = fuse_shapes(doc, name, [housing, flange, shaft, connector])
    motor.ViewObject.ShapeColor = (0.5, 0.5, 0.5)
    
    return motor

def create_all_motors():
    """Tüm motorları oluştur"""
    # Yeni doküman oluştur
    doc = App.newDocument("ECMA_Motors")
    doc.Label = "ECMA Servo Motors"
    
    # Motorları oluştur
    print("ECMA-L11845 (4.5kW) oluşturuluyor...")
    create_ecma_l11845(doc)
    
    print("ECMA-E11320 (2.0kW) oluşturuluyor...")
    create_ecma_e11320(doc)
    
    print("ECMA-C11010 (1.0kW Frenli) oluşturuluyor...")
    create_ecma_c11010_brake(doc)
    
    print("ECMA-E11315 (1.5kW IP67) oluşturuluyor...")
    create_ecma_e11315(doc)
    
    # Dokümanı yeniden hesapla ve kaydet
    doc.recompute()
    App.ActiveDocument = doc
    
    print("Tüm motorlar başarıyla oluşturuldu!")
    print("Dosyayı kaydetmek için: File → Save As...")
    
    return doc

# Script'i çalıştır
if __name__ == "__main__":
    create_all_motors()