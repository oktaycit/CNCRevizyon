# FreeCAD Kesim Kafası (Cutting Head) Modeli
# CNC Revizyon Projesi - GFB-60/30RE
# Z Ekseni ve Kesim Tekeri Montajı

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/04_CuttingHead"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "CuttingHead")
os.makedirs(EXPORT_DIR, exist_ok=True)

# Kesim Kafası Parametreleri
Z_TRAVEL = 300       # Z ekseni hareket mesafesi (mm)
Z_MOTOR_OFFSET = 50  # Motor montaj ofseti
WHEEL_DIAMETER = 80  # Kesim tekeri çapı (mm)

def create_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height, 
                              App.Vector(position), 
                              App.Vector(direction))

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_hollow_cylinder(outer_radius, inner_radius, height, position=(0, 0, 0)):
    """İçi boş silindir oluştur"""
    outer = create_cylinder(outer_radius, height, position)
    inner = create_cylinder(inner_radius, height + 2, 
                           (position[0], position[1], position[2] - 1))
    return outer.cut(inner)

def create_z_axis_housing(doc, name="ZAxis_Housing"):
    """
    Z Ekseni Motor Yuvası
    
    ECMA-C11010 (1.0kW frenli) motor için
    """
    housing_width = 150
    housing_height = 200
    housing_depth = 120
    
    # Ana gövde
    main_body = create_box(housing_width, housing_height, housing_depth,
                           (-housing_width/2, 0, -housing_depth/2))
    
    # Motor montaj yüzeyi
    motor_mount_thickness = 20
    motor_mount = create_box(housing_width, motor_mount_thickness, housing_depth,
                             (-housing_width/2, housing_height - motor_mount_thickness, -housing_depth/2))
    main_body = main_body.fuse(motor_mount)
    
    # Motor flanş delikleri
    bolt_pcd = 115  # ECMA-C11010 için PCD
    bolt_hole_radius = 5.5  # M10 için Ø11
    bolt_positions = [
        (-bolt_pcd/2, housing_height - 10, -bolt_pcd/2),
        (bolt_pcd/2, housing_height - 10, -bolt_pcd/2),
        (-bolt_pcd/2, housing_height - 10, bolt_pcd/2),
        (bolt_pcd/2, housing_height - 10, bolt_pcd/2)
    ]
    
    for pos in bolt_positions:
        hole = create_cylinder(bolt_hole_radius, motor_mount_thickness + 5, pos)
        main_body = main_body.cut(hole)
    
    # Mil geçiş deliği
    shaft_hole_radius = 15  # 24mm mil için
    shaft_hole = create_cylinder(shaft_hole_radius, housing_height + 10,
                                 (0, -5, 0))
    main_body = main_body.cut(shaft_hole)
    
    # Lineer ray montaj yüzeyi
    rail_mount_width = 80
    rail_mount_thickness = 15
    rail_mount = create_box(rail_mount_width, housing_height, rail_mount_thickness,
                            (-rail_mount_width/2, 0, housing_depth/2 - rail_mount_thickness))
    main_body = main_body.fuse(rail_mount)
    
    # Ray delikleri
    rail_hole_positions = [
        (-30, 50, housing_depth - 10),
        (30, 50, housing_depth - 10),
        (-30, 150, housing_depth - 10),
        (30, 150, housing_depth - 10)
    ]
    
    for pos in rail_hole_positions:
        hole = create_cylinder(4, rail_mount_thickness, pos)
        main_body = main_body.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = main_body
    
    return shape

def create_z_axis_slide(doc, name="ZAxis_Slide"):
    """
    Z Ekseni Kızak (Hareketli Parça)
    """
    slide_width = 120
    slide_height = 100
    slide_depth = 100
    
    # Ana kızak gövdesi
    slide_body = create_box(slide_width, slide_height, slide_depth,
                            (-slide_width/2, 0, -slide_depth/2))
    
    # Kesim kafası montaj yüzeyi
    head_mount_thickness = 20
    head_mount = create_box(slide_width, slide_height, head_mount_thickness,
                            (-slide_width/2, 0, slide_depth/2 - head_mount_thickness))
    slide_body = slide_body.fuse(head_mount)
    
    # Lineer ray montaj delikleri (arkada)
    rail_hole_positions = [
        (-30, 50, -slide_depth/2),
        (30, 50, -slide_depth/2),
        (-30, 150, -slide_depth/2),
        (30, 150, -slide_depth/2)
    ]
    
    for pos in rail_hole_positions:
        hole = create_cylinder(4, slide_depth, pos, (0, 0, 1))
        slide_body = slide_body.cut(hole)
    
    # Kaplaj montaj delikleri (altta)
    coupling_mount_radius = 40
    coupling_hole = create_cylinder(15, slide_height, (0, 5, 0))
    slide_body = slide_body.cut(coupling_hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = slide_body
    
    return shape

def create_cutting_wheel(doc, name="Cutting_Wheel"):
    """
    Kesim Tekeri
    
    Cam kesimi için elmas kaplama teker
    """
    wheel_radius = WHEEL_DIAMETER / 2
    wheel_thickness = 10
    
    # Ana teker gövdesi
    wheel = create_cylinder(wheel_radius, wheel_thickness, (0, 0, 0))
    
    # Mil deliği
    shaft_hole_radius = 10
    shaft_hole = create_cylinder(shaft_hole_radius, wheel_thickness + 2,
                                 (0, 0, -1))
    wheel = wheel.cut(shaft_hole)
    
    # Rulman yuvası
    bearing_seat_radius = 20
    bearing_seat = create_hollow_cylinder(bearing_seat_radius, shaft_hole_radius, 
                                          wheel_thickness/2, (0, 0, 0))
    wheel = wheel.fuse(bearing_seat)
    
    # Kesici kenar (eğimli)
    edge_angle = 45  # derece
    # Basitleştirilmiş: küçük bir pah
    edge_cut = create_cylinder(wheel_radius - 2, 3, (0, 0, wheel_thickness/2 - 1.5))
    wheel = wheel.cut(edge_cut)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = wheel
    
    return shape

def create_cutting_head_assembly(doc, name="Cutting_Head_Assembly"):
    """
    Tam Kesim Kafası Montajı
    
    - Z ekseni motor yuvası
    - Hareketli kızak
    - Kesim tekeri
    - Motor kaplajı
    """
    parts = []
    
    # Z ekseni yuvası
    housing = create_z_axis_housing(doc, "Z_Housing")
    parts.append(housing)
    
    # Z ekseni kızak
    slide = create_z_axis_slide(doc, "Z_Slide")
    slide.Placement = App.Placement(
        App.Vector(0, 0, 50),  # Yuva içinde hareketli
        App.Rotation(0, 0, 0)
    )
    parts.append(slide)
    
    # Kesim tekeri
    wheel = create_cutting_wheel(doc, "Wheel")
    wheel.Placement = App.Placement(
        App.Vector(0, 50, 100),  # Kızak altında
        App.Rotation(90, 0, 0)  # Döndür
    )
    parts.append(wheel)
    
    # Teker koruyucu
    wheel_radius = WHEEL_DIAMETER / 2
    guard_radius = wheel_radius + 10
    guard = create_hollow_cylinder(guard_radius, wheel_radius + 5, 15,
                                   (0, 50, 100))
    parts.append(guard)
    
    # Şaft ve kaplaj
    shaft = create_cylinder(12, 80, (0, 0, 100))
    parts.append(shaft)
    
    combined = parts[0].Shape
    for p in parts[1:]:
        if hasattr(p, "Shape"):
            combined = combined.fuse(p.Shape)
        else:
            combined = combined.fuse(p)

    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_wheel_mount(doc, name="Wheel_Mount"):
    """
    Kesim Tekeri Montaj Braketi
    """
    mount_width = 60
    mount_height = 80
    mount_thickness = 15
    
    # Ana montaj plakası
    plate = create_box(mount_width, mount_height, mount_thickness,
                       (-mount_width/2, 0, -mount_thickness/2))
    
    # Teker aksı delikleri
    axle_hole_radius = 12
    axle_positions = [
        (-mount_width/2 + 15, mount_height/2, 0),
        (mount_width/2 - 15, mount_height/2, 0)
    ]
    
    for pos in axle_positions:
        hole = create_cylinder(axle_hole_radius, mount_thickness + 2, pos)
        plate = plate.cut(hole)
    
    # Montaj delikleri
    mount_hole_radius = 5
    mount_hole_positions = [
        (-mount_width/2 + 10, 20, 0),
        (mount_width/2 - 10, 20, 0),
        (-mount_width/2 + 10, mount_height - 20, 0),
        (mount_width/2 - 10, mount_height - 20, 0)
    ]
    
    for pos in mount_hole_positions:
        hole = create_cylinder(mount_hole_radius, mount_thickness + 2, pos)
        plate = plate.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = plate
    
    return shape

def create_coupling(doc, name="Coupling"):
    """
    Motor-Mil Kaplajı
    
    Esnek kaplaj
    """
    coupling_diameter = 50
    coupling_length = 60
    
    # Dış gövde
    outer = create_cylinder(coupling_diameter/2, coupling_length, (0, 0, 0))
    
    # İç delik (mil için)
    inner_radius = 12
    inner = create_cylinder(inner_radius, coupling_length + 2, (0, 0, -1))
    coupling = outer.cut(inner)
    
    # Sıkıştırma vidaları için delikler
    screw_hole_radius = 3
    screw_positions = [
        (coupling_diameter/2 - 5, 0, 15),
        (0, coupling_diameter/2 - 5, 15),
        (-coupling_diameter/2 + 5, 0, 15),
        (0, -coupling_diameter/2 + 5, 15)
    ]
    
    for pos in screw_positions:
        hole = create_cylinder(screw_hole_radius, 20, pos, (1, 0, 0))
        coupling = coupling.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = coupling
    
    return shape

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_all_cutting_head_parts():
    """Tüm kesim kafası parçalarını oluştur"""
    print("=" * 50)
    print("Kesim Kafası (Cutting Head) Generator")
    print("=" * 50)
    print(f"Z Ekseni Hareket: {Z_TRAVEL} mm")
    print(f"Kesim Tekeri Çapı: {WHEEL_DIAMETER} mm")
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # Z ekseni yuvası
    print("Z ekseni motor yuvası oluşturuluyor...")
    doc_housing = App.newDocument("ZAxis_Housing")
    housing = create_z_axis_housing(doc_housing)
    doc_housing.recompute()
    export_to_step(doc_housing, housing, "ZAxis_Housing.stp")
    
    # Z ekseni kızak
    print("Z ekseni kızak oluşturuluyor...")
    doc_slide = App.newDocument("ZAxis_Slide")
    slide = create_z_axis_slide(doc_slide)
    doc_slide.recompute()
    export_to_step(doc_slide, slide, "ZAxis_Slide.stp")
    
    # Kesim tekeri
    print("Kesim tekeri oluşturuluyor...")
    doc_wheel = App.newDocument("Cutting_Wheel")
    wheel = create_cutting_wheel(doc_wheel)
    doc_wheel.recompute()
    export_to_step(doc_wheel, wheel, "Cutting_Wheel.stp")
    
    # Teker montaj braketi
    print("Teker montaj braketi oluşturuluyor...")
    doc_mount = App.newDocument("Wheel_Mount")
    mount = create_wheel_mount(doc_mount)
    doc_mount.recompute()
    export_to_step(doc_mount, mount, "Wheel_Mount.stp")
    
    # Kaplaj
    print("Motor kaplajı oluşturuluyor...")
    doc_coupling = App.newDocument("Coupling")
    coupling = create_coupling(doc_coupling)
    doc_coupling.recompute()
    export_to_step(doc_coupling, coupling, "Motor_Coupling.stp")
    
    # Tam montaj
    print("Tam kesim kafası montajı oluşturuluyor...")
    doc_assembly = App.newDocument("Cutting_Head_Assembly")
    assembly = create_cutting_head_assembly(doc_assembly)
    doc_assembly.recompute()
    export_to_step(doc_assembly, assembly, "Cutting_Head_Assembly.stp")
    
    print()
    print("=" * 50)
    print("Tüm kesim kafası parçaları oluşturuldu!")
    print("=" * 50)
    
    return doc_assembly

if __name__ == "__main__":
    create_all_cutting_head_parts()
