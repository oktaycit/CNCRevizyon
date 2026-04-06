# FreeCAD HIWIN HGH25CA Lineer Ray ve Kızak Modeli
# CNC Revizyon Projesi - GFB-60/30RE

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/03_LinearGuides"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "LinearGuides")
os.makedirs(EXPORT_DIR, exist_ok=True)

def create_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height, 
                              App.Vector(position), 
                              App.Vector(direction))

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_hole_pattern(base_shape, hole_radius, positions, height=100):
    """Delik deseni oluştur"""
    result = base_shape
    for pos in positions:
        hole = create_cylinder(hole_radius, height, pos)
        result = result.cut(hole)
    return result

def create_hiwin_hgh25_rail(doc, name="HIWIN_HGH25_Rail", length=6000):
    """
    HIWIN HGH25CA Lineer Ray Modeli
    
    Ölçüler:
    - Genişlik: 23 mm
    - Yükseklik: 40 mm
    - Delik Aralığı: 60 mm
    - Delik Çapı: Ø7 mm (M6 için)
    """
    # Ray gövdesi
    rail_width = 23
    rail_height = 40
    
    # Ana gövde
    rail_body = create_box(rail_width, rail_height, length, (0, 0, 0))
    
    # T-Slot üst oluk (basitleştirilmiş)
    t_slot_width = 8
    t_slot_depth = 5
    t_slot = create_box(t_slot_width, t_slot_depth, length, 
                        (-t_slot_width/2, rail_height - t_slot_depth, 0))
    rail_body = rail_body.cut(t_slot)
    
    # Montaj delikleri (60mm aralıklı)
    hole_radius = 3.5  # Ø7 mm
    hole_depth = rail_height
    holes = []
    
    # Her iki tarafta delikler
    hole_offset_x = 8  # Kenardan uzaklık
    hole_start = 30  # İlk delik mesafesi
    hole_spacing = 60  # Delikler arası mesafe
    
    num_holes = int((length - 2 * hole_start) / hole_spacing) + 1
    
    for i in range(num_holes):
        z_pos = hole_start + i * hole_spacing
        # Sol delik
        left_hole = create_cylinder(hole_radius, hole_depth, 
                                    (-hole_offset_x, 0, z_pos), (0, 1, 0))
        # Sağ delik
        right_hole = create_cylinder(hole_radius, hole_depth, 
                                     (hole_offset_x, 0, z_pos), (0, 1, 0))
        rail_body = rail_body.cut(left_hole)
        rail_body = rail_body.cut(right_hole)
    
    # Köşe pahları (chamfers) - basitleştirilmiş
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = rail_body
    
    return shape

def create_hiwin_hgh25_block(doc, name="HIWIN_HGH25_Block"):
    """
    HIWIN HGH25CA Kızak (Block) Modeli
    
    Ölçüler:
    - Uzunluk: ~80 mm
    - Genişlik: ~60 mm
    - Yükseklik: ~40 mm
    """
    block_length = 98  # Toplam uzunluk
    block_width = 60   # Genişlik
    block_height = 40  # Yükseklik
    
    # Ana gövde
    main_body = create_box(block_width, block_height, block_length, 
                           (0, 0, 0))
    
    # Üst eğimli yüzeyler (basitleştirilmiş)
    chamfer_height = 10
    chamfer_width = 15
    
    # Ön üst pah
    front_chamfer = create_box(block_width, chamfer_height, chamfer_width,
                               (0, block_height - chamfer_height, -block_length/2 + chamfer_width/2))
    main_body = main_body.cut(front_chamfer)
    
    # Arka üst pah
    rear_chamfer = create_box(block_width, chamfer_height, chamfer_width,
                              (0, block_height - chamfer_height, block_length/2 - chamfer_width/2))
    main_body = main_body.cut(rear_chamfer)
    
    # Montaj delikleri (4 köşe)
    hole_radius = 3.5  # M6 için Ø7
    hole_height = block_height
    
    hole_positions = [
        (-23, 0, -35),   # Sol ön
        (23, 0, -35),    # Sağ ön
        (-23, 0, 35),    # Sol arka
        (23, 0, 35)      # Sağ arka
    ]
    
    for pos in hole_positions:
        hole = create_cylinder(hole_radius, hole_height, pos, (0, 1, 0))
        main_body = main_body.cut(hole)
    
    # Yağlama deliği (üstte)
    grease_hole_radius = 2  # Ø4 mm
    grease_hole = create_cylinder(grease_hole_radius, 15, (0, block_height, 0), (0, -1, 0))
    main_body = main_body.cut(grease_hole)
    
    # T-Slot uyum oyuğu (alt kısım)
    t_slot_cutout = create_box(10, 10, block_length, (-5, 0, 0))
    main_body = main_body.cut(t_slot_cutout)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = main_body
    
    return shape

def create_hiwin_hgh25_assembly(doc, name="HIWIN_HGH25_Assembly", rail_length=1000):
    """
    Ray ve Kızak Montajı
    """
    # Ray oluştur
    rail = create_hiwin_hgh25_rail(doc, "Rail", rail_length)
    
    # Kızak oluştur
    block = create_hiwin_hgh25_block(doc, "Block")
    
    # Kızağı ray üzerine yerleştir
    # Kızak pozisyonu: rayın ortasına yakın
    block.Placement = App.Placement(
        App.Vector(0, 40, rail_length/2),  # Rayin üstüne
        App.Rotation(0, 0, 0)
    )
    
    return rail, block

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_all_linear_guides():
    """Tüm lineer ray ve kızak modellerini oluştur"""
    print("=" * 50)
    print("HIWIN HGH25CA Lineer Ray Generator")
    print("=" * 50)
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # X ekseni rayı (6000 mm)
    print("X Ekseni Rayı (6000 mm) oluşturuluyor...")
    doc_x_rail = App.newDocument("HIWIN_HGH25_X_Rail")
    x_rail = create_hiwin_hgh25_rail(doc_x_rail, "X_Rail", 6000)
    doc_x_rail.recompute()
    export_to_step(doc_x_rail, x_rail, "HIWIN_HGH25_X_Rail.stp")
    
    # Y ekseni rayı (3000 mm)
    print("Y Ekseni Rayı (3000 mm) oluşturuluyor...")
    doc_y_rail = App.newDocument("HIWIN_HGH25_Y_Rail")
    y_rail = create_hiwin_hgh25_rail(doc_y_rail, "Y_Rail", 3000)
    doc_y_rail.recompute()
    export_to_step(doc_y_rail, y_rail, "HIWIN_HGH25_Y_Rail.stp")
    
    # Kızak (Block)
    print("Kızak (Block) oluşturuluyor...")
    doc_block = App.newDocument("HIWIN_HGH25_Block")
    block = create_hiwin_hgh25_block(doc_block, "Block")
    doc_block.recompute()
    export_to_step(doc_block, block, "HIWIN_HGH25_Block.stp")
    
    # Montaj örneği (kısa ray + kızak)
    print("Montaj örneği oluşturuluyor...")
    doc_assembly = App.newDocument("HIWIN_HGH25_Assembly")
    rail, block = create_hiwin_hgh25_assembly(doc_assembly, "Assembly", 500)
    doc_assembly.recompute()
    export_to_step(doc_assembly, rail, "HIWIN_HGH25_Assembly.stp")
    
    print()
    print("=" * 50)
    print("Tüm lineer ray modelleri oluşturuldu!")
    print("=" * 50)
    
    return doc_x_rail

if __name__ == "__main__":
    create_all_linear_guides()