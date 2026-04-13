# FreeCAD Ana Montaj (Main Assembly) Modeli
# CNC Revizyon Projesi - GFB-60/30RE
# Tam Makine Montajı

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "Assembly")
os.makedirs(EXPORT_DIR, exist_ok=True)

# Makine Parametreleri
MACHINE_LENGTH = 6000  # X ekseni
MACHINE_WIDTH = 3000   # Y ekseni
MACHINE_HEIGHT = 800   # Şase yüksekliği

def create_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height, 
                              App.Vector(position), 
                              App.Vector(direction))

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_simplified_frame(doc, name="Simplified_Frame"):
    """
    Basitleştirilmiş şase modeli
    Montaj için referans olarak kullanılır
    """
    profile_size = 80
    
    # 4 ana köşe profili
    profiles = []
    
    # Uzun profiller (X ekseni)
    front_left = create_box(profile_size, profile_size, MACHINE_LENGTH,
                           (0, 0, 0))
    front_right = create_box(profile_size, profile_size, MACHINE_LENGTH,
                            (0, MACHINE_WIDTH - profile_size, 0))
    rear_left = create_box(profile_size, profile_size, MACHINE_LENGTH,
                          (0, MACHINE_WIDTH, 0))
    rear_right = create_box(profile_size, profile_size, MACHINE_LENGTH,
                           (0, MACHINE_WIDTH - profile_size + profile_size, 0))
    
    profiles.extend([front_left, front_right, rear_left, rear_right])
    
    # Kısa profiller (Y ekseni)
    left_front = create_box(profile_size, MACHINE_WIDTH, profile_size,
                           (0, 0, 0))
    left_front.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
    
    right_front = create_box(profile_size, MACHINE_WIDTH, profile_size,
                            (MACHINE_LENGTH - profile_size, 0, 0))
    right_front.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), 90)
    
    profiles.extend([left_front, right_front])
    
    # Birleştir
    combined = profiles[0]
    for p in profiles[1:]:
        combined = combined.fuse(p)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_simplified_motor(doc, name="Simplified_Motor", 
                            housing_diameter=130, housing_length=170,
                            shaft_diameter=24, shaft_length=50,
                            position=(0, 0, 0)):
    """
    Basitleştirilmiş motor modeli
    """
    # Gövde
    housing = create_cylinder(housing_diameter/2, housing_length, position)
    
    # Flanş
    flange = create_cylinder(housing_diameter/2 + 25, 10, 
                            (position[0], position[1], position[2] - 5))
    housing = housing.fuse(flange)
    
    # Mil
    shaft = create_cylinder(shaft_diameter/2, shaft_length,
                           (position[0], position[1], position[2] + housing_length))
    housing = housing.fuse(shaft)
    
    # Konektör
    connector = create_box(50, 40, 45,
                          (position[0] - 25, position[1] + housing_diameter/2, 
                           position[2] + housing_length/2))
    housing = housing.fuse(connector)
    
    moved = housing.copy()
    moved.translate(App.Vector(position))
    
    return moved

def create_simplified_rail(doc, name="Simplified_Rail", 
                           width=23, height=40, length=1000,
                           position=(0, 0, 0)):
    """
    Basitleştirilmiş lineer ray modeli
    """
    rail = create_box(width, height, length,
                     (-width/2, 0, 0))
    
    # T-slot (basitleştirilmiş)
    t_slot = create_box(8, 5, length, (-4, height - 5, 0))
    rail = rail.cut(t_slot)
    
    moved = rail.copy()
    moved.translate(App.Vector(position))
    
    return moved

def create_simplified_block(doc, name="Simplified_Block",
                            width=60, height=40, length=98,
                            position=(0, 0, 0)):
    """
    Basitleştirilmiş kızak modeli
    """
    block = create_box(width, height, length,
                      (-width/2, 0, -length/2))
    
    moved = block.copy()
    moved.translate(App.Vector(position))
    
    return moved

def create_x_axis_assembly(doc, name="XAxis_Assembly"):
    """
    X Ekseni Montajı
    
    - 2 adet lineer ray
    - 4 adet kızak
    - Portal köprüsü
    - X ekseni motoru
    """
    parts = []
    
    # Lineer raylar
    rail_length = MACHINE_LENGTH
    rail_positions = [
        (100, 0, 0),  # Sol ray
        (MACHINE_WIDTH - 100, 0, 0)  # Sağ ray
    ]
    
    for i, pos in enumerate(rail_positions):
        rail = create_simplified_rail(doc, f"X_Rail_{i+1}", 23, 40, rail_length, pos)
        parts.append(rail)
    
    # Kızaklar
    block_positions = [
        (100, 40, 500),  # Sol ön
        (MACHINE_WIDTH - 100, 40, 500),  # Sağ ön
        (100, 40, MACHINE_LENGTH - 500),  # Sol arka
        (MACHINE_WIDTH - 100, 40, MACHINE_LENGTH - 500)  # Sağ arka
    ]
    
    for i, pos in enumerate(block_positions):
        block = create_simplified_block(doc, f"X_Block_{i+1}", 60, 40, 98, pos)
        parts.append(block)
    
    # Portal köprüsü
    portal_width = MACHINE_WIDTH - 200
    portal_height = 400
    portal_beam = create_box(120, 120, portal_width,
                            (-60, portal_height, 0))
    portal_beam.translate(App.Vector(MACHINE_LENGTH/2, 0, MACHINE_WIDTH/2 - portal_width/2))
    parts.append(portal_beam)
    
    # X ekseni motoru
    motor = create_simplified_motor(doc, "X_Motor", 130, 170, 24, 50,
                                   (MACHINE_LENGTH - 200, 100, 50))
    parts.append(motor)
    
    # Tüm parçaları birleştir
    if len(parts) == 0:
        return create_box(100, 100, 100)
    
    combined = parts[0]
    for p in parts[1:]:
        combined = combined.fuse(p)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_y_axis_assembly(doc, name="YAxis_Assembly"):
    """
    Y Ekseni Montajı
    
    - 1 adet lineer ray (portal üzerinde)
    - 2 adet kızak
    - Y ekseni motoru
    """
    parts = []
    
    # Y ekseni rayı (portal üzerinde)
    rail_length = MACHINE_WIDTH - 200
    y_rail = create_simplified_rail(doc, "Y_Rail", 23, 40, rail_length,
                                    (MACHINE_LENGTH/2, 400, MACHINE_WIDTH/2 - rail_length/2))
    y_rail.rotate(App.Vector(MACHINE_LENGTH/2, 400, MACHINE_WIDTH/2), 
                  App.Vector(0, 0, 1), 90)
    parts.append(y_rail)
    
    # Y ekseni kızakları
    block_positions = [
        (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2 - 100),
        (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2 + 100)
    ]
    
    for i, pos in enumerate(block_positions):
        block = create_simplified_block(doc, f"Y_Block_{i+1}", 60, 40, 98, pos)
        parts.append(block)
    
    # Y ekseni motoru
    motor = create_simplified_motor(doc, "Y_Motor", 130, 170, 24, 50,
                                   (MACHINE_LENGTH - 200, 450, 100))
    parts.append(motor)
    
    # Birleştir
    combined = parts[0]
    for p in parts[1:]:
        combined = combined.fuse(p)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_z_axis_assembly(doc, name="ZAxis_Assembly"):
    """
    Z Ekseni Montajı (Kesim Kafası)
    
    - Z ekseni motoru
    - Z ekseni yuvası
    - Kesim tekeri
    """
    parts = []
    
    # Z ekseni motoru (frenli)
    motor = create_simplified_motor(doc, "Z_Motor", 100, 165, 24, 50,
                                   (MACHINE_LENGTH/2, 500, MACHINE_WIDTH - 100))
    parts.append(motor)
    
    # Z ekseni yuvası
    housing = create_box(150, 200, 120,
                        (MACHINE_LENGTH/2 - 75, 300, MACHINE_WIDTH - 180))
    parts.append(housing)
    
    # Kesim tekeri
    wheel = create_cylinder(40, 10,
                           (MACHINE_LENGTH/2, 250, MACHINE_WIDTH - 50),
                           (1, 0, 0))
    parts.append(wheel)
    
    # Birleştir
    combined = parts[0]
    for p in parts[1:]:
        combined = combined.fuse(p)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_full_assembly(doc, name="Full_Machine_Assembly"):
    """
    Tam Makine Montajı
    
    Tüm eksenler ve bileşenler
    """
    part_names = []
    
    # Şase
    frame = create_simplified_frame(doc, "Frame")
    part_names.append("Frame")
    
    # X ekseni
    x_axis = create_x_axis_assembly(doc, "X_Assembly")
    part_names.append("X_Assembly")
    
    # Y ekseni
    y_axis = create_y_axis_assembly(doc, "Y_Assembly")
    part_names.append("Y_Assembly")
    
    # Z ekseni
    z_axis = create_z_axis_assembly(doc, "Z_Assembly")
    part_names.append("Z_Assembly")
    
    # Tüm parçaları geometri seviyesinde birleştir
    if not part_names:
        return None

    combined = doc.getObject(part_names[0]).Shape
    for part_name in part_names[1:]:
        combined = combined.fuse(doc.getObject(part_name).Shape)

    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined

    return shape

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_all_assemblies():
    """Tüm montajları oluştur"""
    print("=" * 50)
    print("Ana Montaj (Assembly) Generator - GFB-60/30RE")
    print("=" * 50)
    print(f"Makine Boyutları: {MACHINE_LENGTH} x {MACHINE_WIDTH} x {MACHINE_HEIGHT} mm")
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # X ekseni montajı
    print("X ekseni montajı oluşturuluyor...")
    doc_x = App.newDocument("XAxis_Assembly")
    x_assembly = create_x_axis_assembly(doc_x)
    doc_x.recompute()
    export_to_step(doc_x, x_assembly, "XAxis_Assembly.stp")
    
    # Y ekseni montajı
    print("Y ekseni montajı oluşturuluyor...")
    doc_y = App.newDocument("YAxis_Assembly")
    y_assembly = create_y_axis_assembly(doc_y)
    doc_y.recompute()
    export_to_step(doc_y, y_assembly, "YAxis_Assembly.stp")
    
    # Z ekseni montajı
    print("Z ekseni montajı oluşturuluyor...")
    doc_z = App.newDocument("ZAxis_Assembly")
    z_assembly = create_z_axis_assembly(doc_z)
    doc_z.recompute()
    export_to_step(doc_z, z_assembly, "ZAxis_Assembly.stp")
    
    # Tam montaj
    print("Tam makine montajı oluşturuluyor...")
    doc_full = App.newDocument("Full_Assembly")
    full_assembly = create_full_assembly(doc_full)
    doc_full.recompute()
    export_to_step(doc_full, full_assembly, "Full_Machine_Assembly.stp")
    
    print()
    print("=" * 50)
    print("Tüm montajlar oluşturuldu!")
    print("=" * 50)
    
    return doc_full

if __name__ == "__main__":
    create_all_assemblies()
