# FreeCAD Operatör Terminal Kutusu Modeli
# CNC Revizyon Projesi - GFB-60/30RE
# DOP-110CS HMI + R1-EC Uzak I/O Entegrasyonu

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/05_Electronics"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "Electronics")
os.makedirs(EXPORT_DIR, exist_ok=True)

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height,
                              App.Vector(position),
                              App.Vector(direction))

def create_hollow_box(outer_w, outer_h, outer_d, wall_thickness, position=(0, 0, 0), open_top=False):
    """İçi boş kutu oluştur"""
    outer = create_box(outer_w, outer_h, outer_d, position)
    
    inner_w = outer_w - 2 * wall_thickness
    inner_h = outer_h - 2 * wall_thickness
    if open_top:
        inner_d = outer_d - wall_thickness  # Alt kapalı, üst açık
        inner = create_box(inner_w, inner_h, inner_d + 2,
                          (position[0] + wall_thickness, 
                           position[1] + wall_thickness, 
                           position[2] + wall_thickness - 1))
    else:
        inner_d = outer_d - 2 * wall_thickness
        inner = create_box(inner_w, inner_h, inner_d,
                          (position[0] + wall_thickness, 
                           position[1] + wall_thickness, 
                           position[2] + wall_thickness))
    
    return outer.cut(inner)

def create_dop_110cs_housing(doc, name="DOP-110CS_Housing"):
    """
    DOP-110CS HMI Panel Montaj Modeli
    
    Dış Ölçüler: 286 x 226 x 58 mm (W x H x D)
    Panel Cutout: 271 x 211 mm (W x H)
    Panel Kalınlığı: 2-6 mm
    """
    # DOP-110CS dış ölçüler
    width = 286
    height = 226
    depth = 58
    
    # Ön panel (ekran tarafı)
    front_panel = create_box(width, 8, depth, (-width/2, 0, -depth/2))
    
    # Ekran cutout (10.1" TFT için)
    screen_width = 220
    screen_height = 140
    screen_cutout = create_box(screen_width, 2, depth + 4,
                               (-screen_width/2, 9, -depth/2 - 2))
    front_panel = front_panel.cut(screen_cutout)
    
    # Montaj klipsleri için boşluklar (4 köşe)
    clip_positions = [
        (-width/2 + 15, 0, -depth/2 + 10),
        (width/2 - 15, 0, -depth/2 + 10),
        (-width/2 + 15, 0, depth/2 - 10),
        (width/2 - 15, 0, depth/2 - 10)
    ]
    
    for pos in clip_positions:
        clip_cutout = create_box(20, 2, 15,
                                (pos[0] - 10, pos[1] - 1, pos[2]))
        front_panel = front_panel.cut(clip_cutout)
    
    # Arka kasa
    rear_housing = create_hollow_box(width - 10, height - 10, depth - 8, 
                                     3, (-width/2 + 5, 8, -depth/2 + 8))
    
    # Birleştir
    housing = front_panel.fuse(rear_housing)
    
    # Kablo girişleri (arkada)
    cable_holes = [
        (0, height - 5, 0),      # Üst giriş
        (0, 5, 0),               # Alt giriş
        (width/2, height/2, 0),  # Sağ giriş
    ]
    
    for pos in cable_holes:
        hole = create_cylinder(25, 10, pos, (0, 1, 0))
        housing = housing.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = housing
    
    return shape

def create_dop_110cs_panel_cutout(doc, name="DOP-110CS_Panel_Cutout"):
    """
    DOP-110CS için panel kesim şablonu
    
    Cutout: 271 x 211 mm
    Montaj delikleri: 4x Ø4.5mm
    """
    width = 271
    height = 211
    thickness = 6
    
    # Panel
    panel = create_box(width, height, thickness, (-width/2, 0, -thickness/2))
    
    # Ekran penceresi
    screen_width = 220
    screen_height = 140
    screen_window = create_box(screen_width, screen_height, thickness + 2,
                               (-screen_width/2, 0, -thickness/2 - 1))
    panel = panel.cut(screen_window)
    
    # Montaj delikleri (4 köşe)
    hole_radius = 4.5  # M5 vida için
    hole_positions = [
        (-width/2 + 20, height/2, 0),
        (width/2 - 20, height/2, 0),
        (-width/2 + 20, -height/2, 0),
        (width/2 - 20, -height/2, 0)
    ]
    
    for pos in hole_positions:
        hole = create_cylinder(hole_radius, thickness + 2, pos)
        panel = panel.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = panel
    
    return shape

def create_terminal_enclosure(doc, name="Operator_Terminal_Enclosure"):
    """
    Operatör Terminal Kutusu Ana Gövde
    
    DOP-110CS HMI + R1-EC modülleri için entegre kutu
    IP65 koruma sınıfı
    """
    # Ana kutu dış ölçüler
    width = 400
    height = 500
    depth = 250
    wall_thickness = 5
    
    # Ana gövde (arkası kapalı)
    enclosure = create_hollow_box(width, height, depth, wall_thickness,
                                  (-width/2, 0, -depth/2), open_top=False)
    
    # Ön panel montaj yüzeyi (DOP-110CS için)
    front_mount_width = 320
    front_mount_height = 260
    front_mount_thickness = 10
    
    front_mount = create_box(front_mount_width, front_mount_height, front_mount_thickness,
                            (-front_mount_width/2, height, -front_mount_thickness/2))
    enclosure = enclosure.fuse(front_mount)
    
    # DOP-110CS cutout (panel montajı için)
    dop_cutout = create_box(271, 211, front_mount_thickness + 5,
                           (-271/2, height, 0))
    enclosure = enclosure.cut(dop_cutout)
    
    # DOP-110CS montaj delikleri
    dop_hole_radius = 4.5
    dop_hole_positions = [
        (-271/2 + 20, height, 211/2 - 20),
        (271/2 - 20, height, 211/2 - 20),
        (-271/2 + 20, height, -211/2 + 20),
        (271/2 - 20, height, -211/2 + 20)
    ]
    
    for pos in dop_hole_positions:
        hole = create_cylinder(dop_hole_radius, front_mount_thickness + 5, pos, (0, 1, 0))
        enclosure = enclosure.cut(hole)
    
    # DIN ray montaj profili (içeride, R1-EC için)
    din_rail_width = 35
    din_rail_height = 15
    din_rail_length = width - 40
    
    din_rail = create_box(din_rail_length, din_rail_height, din_rail_width,
                         (-din_rail_length/2, 20, -din_rail_width/2))
    
    # DIN ray oluğu (TS 35 standardı)
    din_channel = create_box(din_rail_length - 4, din_rail_height + 5, din_rail_width - 5,
                            (-din_rail_length/2 + 2, 20, -din_rail_width/2 + 2.5))
    din_rail = din_rail.cut(din_channel)
    
    enclosure = enclosure.fuse(din_rail)
    
    # Kablo girişleri (alt tarafta)
    cable_hole_diameter = 40
    cable_hole_positions = [
        (-width/4, 0, -depth/2),
        (width/4, 0, -depth/2),
        (0, 0, -depth/2)
    ]
    
    for pos in cable_hole_positions:
        hole = create_cylinder(cable_hole_diameter/2, wall_thickness + 5, pos)
        enclosure = enclosure.cut(hole)
    
    # Havalandırma delikleri (yan duvarlarda, IP65 için filtereli)
    vent_radius = 5
    vent_rows = 3
    vent_cols = 5
    
    for row in range(vent_rows):
        for col in range(vent_cols):
            # Sol yan
            vent_x_left = -width/2 + 30 + col * 60
            vent_y_left = 100 + row * 150
            vent_left = create_cylinder(vent_radius, wall_thickness + 2,
                                       (vent_x_left, vent_y_left, -depth/2 - 1), (0, 0, 1))
            enclosure = enclosure.cut(vent_left)
            
            # Sağ yan
            vent_x_right = width/2 - 30 - col * 60
            vent_right = create_cylinder(vent_radius, wall_thickness + 2,
                                        (vent_x_right, vent_y_left, depth/2 + 1), (0, 0, 1))
            enclosure = enclosure.cut(vent_right)
    
    # Kapı menteşe montajları (sol tarafta)
    hinge_mount_width = 50
    hinge_mount_height = 80
    hinge_mount_depth = 40
    
    hinge_positions = [
        (-width/2, height/2, -depth/2 + 40),
        (-width/2, height/2, -depth/2 + depth - 40)
    ]
    
    for pos in hinge_positions:
        hinge = create_box(hinge_mount_depth, hinge_mount_height, hinge_mount_width,
                          (pos[0], pos[1] - hinge_mount_height/2, pos[2] - hinge_mount_width/2))
        enclosure = enclosure.fuse(hinge)
    
    # Kapı kilit montajı (sağ tarafta)
    lock_cutout = create_cylinder(20, wall_thickness + 5,
                                 (width/2, height/2, 0), (0, 1, 0))
    enclosure = enclosure.cut(lock_cutout)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = enclosure
    
    return shape

def create_terminal_door(doc, name="Operator_Terminal_Door"):
    """
    Operatör Terminal Kutusu Kapağı
    
    DOP-110CS ekranını içerir
    IP65 contalı
    """
    width = 400
    height = 500
    thickness = 5
    
    # Ana kapak
    door = create_box(width, thickness, 490, (-width/2, 0, -245))
    
    # DOP-110CS ekran penceresi
    screen_width = 280
    screen_height = 220
    screen_window = create_box(screen_width, thickness + 2, screen_height,
                              (-screen_width/2, -1, 0))
    door = door.cut(screen_window)
    
    # Conta kanalı (IP65 için)
    gasket_channel_width = width - 20
    gasket_channel_height = 490 - 20
    gasket_depth = 3
    gasket_width = 10
    
    # Üst kanal
    top_gasket = create_box(gasket_channel_width, gasket_depth, gasket_width,
                           (-gasket_channel_width/2, thickness, 245 - gasket_width/2))
    door = door.fuse(top_gasket)
    
    # Alt kanal
    bottom_gasket = create_box(gasket_channel_width, gasket_depth, gasket_width,
                              (-gasket_channel_width/2, thickness, -245 + gasket_width/2))
    door = door.fuse(bottom_gasket)
    
    # Yan kanallar
    left_gasket = create_box(gasket_width, gasket_depth, gasket_channel_height,
                            (-width/2 + gasket_width/2, thickness, 0))
    door = door.fuse(left_gasket)
    
    right_gasket = create_box(gasket_width, gasket_depth, gasket_channel_height,
                             (width/2 - gasket_width/2, thickness, 0))
    door = door.fuse(right_gasket)
    
    # Menteşe delikleri (sol tarafta)
    hinge_hole_radius = 6
    hinge_hole_positions = [
        (-width/2 + 30, 0, 200),
        (-width/2 + 30, 0, -200)
    ]
    
    for pos in hinge_hole_positions:
        hole = create_cylinder(hinge_hole_radius, thickness + 2, pos, (0, 1, 0))
        door = door.cut(hole)
    
    # Kilit deliği (sağ tarafta)
    lock_hole = create_cylinder(15, thickness + 2, (width/2 - 30, 0, 0), (0, 1, 0))
    door = door.cut(lock_hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = door
    
    return shape

def create_r1_ec_mounting_plate(doc, name="R1-EC_Mounting_Plate"):
    """
    R1-EC Modülleri için DIN Ray Montaj Plakası
    
    3-4 adet R1-EC modülü için
    """
    width = 350
    height = 200
    thickness = 5
    
    # Ana plaka
    plate = create_box(width, thickness, height, (-width/2, 0, -height/2))
    
    # DIN ray montaj delikleri
    din_rail_positions = [
        (-width/2 + 50, 0, -height/2 + 30),
        (width/2 - 50, 0, -height/2 + 30),
        (-width/2 + 50, 0, height/2 - 30),
        (width/2 - 50, 0, height/2 - 30)
    ]
    
    for pos in din_rail_positions:
        hole = create_cylinder(5, thickness + 2, pos, (0, 1, 0))
        plate = plate.cut(hole)
    
    # R1-EC modül yerleşim kılavuzları
    module_width = 120
    module_spacing = 10
    num_modules = 3
    
    for i in range(num_modules):
        x_pos = -width/2 + 50 + i * (module_width + module_spacing)
        
        # Modül konumlandırma pimleri
        pin_positions = [
            (x_pos, 0, -height/2 + 50),
            (x_pos + module_width, 0, -height/2 + 50),
            (x_pos, 0, height/2 - 50),
            (x_pos + module_width, 0, height/2 - 50)
        ]
        
        for pin_pos in pin_positions:
            pin = create_cylinder(3, 10, pin_pos)
            plate = plate.fuse(pin)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = plate
    
    return shape

def create_cable_gland(doc, name="Cable_Gland_M40", size="M40"):
    """
    Kablo Giriş Rakoru (Cable Gland)
    
    IP65 koruma için
    """
    if size == "M40":
        outer_diameter = 40
        inner_diameter = 32
        height = 25
    elif size == "M32":
        outer_diameter = 32
        inner_diameter = 25
        height = 22
    else:  # M25
        outer_diameter = 25
        inner_diameter = 18
        height = 20
    
    # Dış gövde
    outer = create_cylinder(outer_diameter/2, height, (0, 0, -height/2))
    
    # İç delik
    inner = create_cylinder(inner_diameter/2, height + 2, (0, 0, -height/2 - 1))
    gland = outer.cut(inner)
    
    # Diş profili (basitleştirilmiş)
    thread_height = 5
    thread_depth = 1
    num_threads = 3
    
    for i in range(num_threads):
        thread_z = -height/2 + i * 3
        thread = create_cylinder(outer_diameter/2 + thread_depth, thread_depth,
                                (0, 0, thread_z))
        gland = gland.fuse(thread)
    
    # Sıkıştırma somunu
    nut_outer = create_cylinder(outer_diameter/2 + 5, 10, (0, 0, height/2))
    nut_inner = create_cylinder(inner_diameter/2 + 1, 12, (0, 0, height/2 - 1))
    nut = nut_outer.cut(nut_inner)
    
    gland = gland.fuse(nut)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = gland
    
    return gland

def create_ip65_filter(doc, name="IP65_Vent_Filter"):
    """
    IP65 Havalandırma Filtresi
    
    Soğutma için havalandırma + toz/nem koruması
    """
    width = 120
    height = 120
    thickness = 15
    
    # Ana gövde
    housing = create_box(width, thickness, height, (-width/2, 0, -height/2))
    
    # Hava kanalları (labirent tipi, IP65 için)
    channel_width = 5
    channel_depth = 10
    num_channels = 10
    
    for i in range(num_channels):
        x_pos = -width/2 + 10 + i * 12
        
        # Dikey kanal
        channel = create_box(channel_width, channel_depth, height - 20,
                            (x_pos, thickness, 0))
        housing = housing.cut(channel)
        
        # Yatay deflektör
        baffle = create_box(channel_width + 4, 2, 8,
                           (x_pos, thickness - 2, 0))
        housing = housing.fuse(baffle)
    
    # Filtre elemanı yuvası
    filter_slot = create_box(width - 10, 5, height - 10,
                            (0, thickness/2, 0))
    housing = housing.cut(filter_slot)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = housing
    
    return shape

def create_complete_terminal_assembly(doc, name="Operator_Terminal_Complete"):
    """
    Tam Operatör Terminal Montajı
    
    Tüm bileşenleri içerir:
    - Ana kutu
    - Kapak
    - DOP-110CS
    - R1-EC modülleri
    - Kablo girişleri
    """
    parts = []
    
    # 1. Ana kutu
    enclosure = create_terminal_enclosure(doc, "Enclosure")
    parts.append(enclosure)
    
    # 2. Kapak
    door = create_terminal_door(doc, "Door")
    parts.append(door)
    
    # 3. DOP-110CS HMI
    hmi = create_dop_110cs_housing(doc, "HMI")
    parts.append(hmi)
    
    # 4. R1-EC montaj plakası
    r1_plate = create_r1_ec_mounting_plate(doc, "R1-EC_Plate")
    parts.append(r1_plate)
    
    # 5. Kablo giriş rakorları
    gland1 = create_cable_gland(doc, "Gland_1", "M40")
    parts.append(gland1)
    
    gland2 = create_cable_gland(doc, "Gland_2", "M32")
    parts.append(gland2)
    
    # 6. IP65 filtreler
    filter1 = create_ip65_filter(doc, "Filter_Left")
    parts.append(filter1)
    
    filter2 = create_ip65_filter(doc, "Filter_Right")
    parts.append(filter2)
    
    # Tüm parçaları birleştir (basit montaj)
    if len(parts) > 0:
        combined = parts[0]
        for part in parts[1:]:
            combined = combined.fuse(part)
        
        shape = doc.addObject("Part::Feature", name)
        shape.Shape = combined
        
        return shape
    
    return None

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_all_terminal_parts():
    """Tüm terminal parçalarını oluştur"""
    print("=" * 60)
    print("Operatör Terminal Kutusu Generator")
    print("GFB-60/30RE - DOP-110CS + R1-EC Entegrasyonu")
    print("=" * 60)
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # DOP-110CS HMI model
    print("1. DOP-110CS HMI modeli oluşturuluyor...")
    doc_hmi = App.newDocument("DOP-110CS")
    hmi = create_dop_110cs_housing(doc_hmi)
    doc_hmi.recompute()
    export_to_step(doc_hmi, hmi, "DOP-110CS_Housing.stp")
    
    # DOP-110CS Panel cutout şablonu
    print("2. DOP-110CS Panel Cutout şablonu oluşturuluyor...")
    doc_cutout = App.newDocument("DOP-110CS_Cutout")
    cutout = create_dop_110cs_panel_cutout(doc_cutout)
    doc_cutout.recompute()
    export_to_step(doc_cutout, cutout, "DOP-110CS_Panel_Cutout.stp")
    
    # Terminal kutusu ana gövde
    print("3. Terminal kutusu ana gövde oluşturuluyor...")
    doc_enclosure = App.newDocument("Terminal_Enclosure")
    enclosure = create_terminal_enclosure(doc_enclosure)
    doc_enclosure.recompute()
    export_to_step(doc_enclosure, enclosure, "Operator_Terminal_Enclosure.stp")
    
    # Terminal kutusu kapağı
    print("4. Terminal kutusu kapağı oluşturuluyor...")
    doc_door = App.newDocument("Terminal_Door")
    door = create_terminal_door(doc_door)
    doc_door.recompute()
    export_to_step(doc_door, door, "Operator_Terminal_Door.stp")
    
    # R1-EC montaj plakası
    print("5. R1-EC montaj plakası oluşturuluyor...")
    doc_plate = App.newDocument("R1-EC_Plate")
    plate = create_r1_ec_mounting_plate(doc_plate)
    doc_plate.recompute()
    export_to_step(doc_plate, plate, "R1-EC_Mounting_Plate.stp")
    
    # Kablo giriş rakoru
    print("6. Kablo giriş rakorları oluşturuluyor...")
    doc_gland = App.newDocument("Cable_Gland")
    gland = create_cable_gland(doc_gland)
    doc_gland.recompute()
    export_to_step(doc_gland, gland, "Cable_Gland_M40.stp")
    
    # IP65 filtre
    print("7. IP65 havalandırma filtresi oluşturuluyor...")
    doc_filter = App.newDocument("IP65_Filter")
    filter_obj = create_ip65_filter(doc_filter)
    doc_filter.recompute()
    export_to_step(doc_filter, filter_obj, "IP65_Vent_Filter.stp")
    
    # Tam montaj
    print("8. Tam terminal montajı oluşturuluyor...")
    doc_assembly = App.newDocument("Terminal_Complete")
    assembly = create_complete_terminal_assembly(doc_assembly)
    doc_assembly.recompute()
    export_to_step(doc_assembly, assembly, "Operator_Terminal_Complete.stp")
    
    print()
    print("=" * 60)
    print("Tüm terminal parçaları oluşturuldu!")
    print("=" * 60)
    print()
    print("Oluşturulan Dosyalar:")
    print("  1. DOP-110CS_Housing.stp")
    print("  2. DOP-110CS_Panel_Cutout.stp")
    print("  3. Operator_Terminal_Enclosure.stp")
    print("  4. Operator_Terminal_Door.stp")
    print("  5. R1-EC_Mounting_Plate.stp")
    print("  6. Cable_Gland_M40.stp")
    print("  7. IP65_Vent_Filter.stp")
    print("  8. Operator_Terminal_Complete.stp")
    print()
    
    return doc_assembly

if __name__ == "__main__":
    create_all_terminal_parts()
