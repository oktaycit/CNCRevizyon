# FreeCAD Elektronik Parçalar Modeli
# CNC Revizyon Projesi - GFB-60/30RE
# R1-EC Modül, Sensör Braketleri, Kablo Kanalı

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

def create_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height, 
                              App.Vector(position), 
                              App.Vector(direction))

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_hollow_box(outer_w, outer_h, outer_d, wall_thickness, position=(0, 0, 0)):
    """İçi boş kutu oluştur"""
    outer = create_box(outer_w, outer_h, outer_d, position)
    
    inner_w = outer_w - 2 * wall_thickness
    inner_h = outer_h - 2 * wall_thickness
    inner_d = outer_d - wall_thickness  # Alt kapalı
    
    inner = create_box(inner_w, inner_h, inner_d + 2,
                       (position[0], position[1], position[2] + wall_thickness - 1))
    
    return outer.cut(inner)

def create_r1_ec_housing(doc, name="R1-EC_Housing"):
    """
    R1-EC Modül Kutusu
    
    EtherCAT servo sürücü modülü için
    """
    # Dış boyutlar
    width = 120
    height = 80
    depth = 60
    wall_thickness = 3
    
    # Ana kutu gövdesi
    housing = create_hollow_box(width, height, depth, wall_thickness, 
                                (-width/2, 0, -depth/2))
    
    # Kablo giriş delikleri
    cable_hole_diameter = 20
    cable_holes = [
        (0, height - 2, -depth/2 + 15),   # Üst giriş
        (0, 2, -depth/2 + 15),            # Alt giriş
        (width/2 - 10, height/2, -depth/2)  # Yan giriş
    ]
    
    for pos in cable_holes:
        hole = create_cylinder(cable_hole_diameter/2, wall_thickness + 5, pos)
        housing = housing.cut(hole)
    
    # Montaj delikleri (4 köşe)
    mount_hole_radius = 3.5  # M6 için
    mount_positions = [
        (-width/2 + 10, 10, -depth/2 + 10),
        (width/2 - 10, 10, -depth/2 + 10),
        (-width/2 + 10, height - 10, -depth/2 + 10),
        (width/2 - 10, height - 10, -depth/2 + 10)
    ]
    
    for pos in mount_positions:
        hole = create_cylinder(mount_hole_radius, depth, pos, (0, 0, 1))
        housing = housing.cut(hole)
    
    # Soğutma delikleri (havalandırma)
    vent_radius = 4
    vent_positions = []
    for i in range(5):
        vent_positions.append((-width/2 + 20 + i * 25, height - 2, -depth/2 + 5))
        vent_positions.append((-width/2 + 20 + i * 25, 2, -depth/2 + 5))
    
    for pos in vent_positions:
        hole = create_cylinder(vent_radius, wall_thickness + 2, pos, (0, 1, 0))
        housing = housing.cut(hole)
    
    # Kapak montaj için kanal
    lid_channel = create_box(width - 6, 5, 5, (-width/2 + 3, height - 5, -depth/2 + 3))
    housing = housing.fuse(lid_channel)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = housing
    
    return shape

def create_r1_ec_lid(doc, name="R1-EC_Lid"):
    """
    R1-EC Modül Kapağı
    """
    width = 120
    height = 80
    thickness = 3
    
    # Ana kapak
    lid = create_box(width, thickness, 54, (-width/2, 0, -27))
    
    # Montaj kulakları
    ear_width = 15
    ear_positions = [
        (-width/2 + 5, 0, -25),
        (width/2 - 5, 0, -25),
        (-width/2 + 5, 0, 25),
        (width/2 - 5, 0, 25)
    ]
    
    for pos in ear_positions:
        ear = create_box(ear_width, thickness, 10, 
                        (pos[0] - ear_width/2, 0, pos[2] - 5))
        lid = lid.fuse(ear)
    
    # Montaj delikleri
    hole_radius = 3.5
    hole_positions = [
        (-width/2 + 10, 0, -25),
        (width/2 - 10, 0, -25),
        (-width/2 + 10, 0, 25),
        (width/2 - 10, 0, 25)
    ]
    
    for pos in hole_positions:
        hole = create_cylinder(hole_radius, thickness + 2, pos, (0, 1, 0))
        lid = lid.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = lid
    
    return shape

def create_sensor_bracket(doc, name="Sensor_Bracket", sensor_type="proximity"):
    """
    Sensör Montaj Braketi
    
    Proximity sensör veya encoder için
    """
    if sensor_type == "proximity":
        # Proximity sensör için
        bracket_width = 40
        bracket_height = 60
        bracket_thickness = 5
        
        # L şeklinde braket
        vertical = create_box(bracket_thickness, bracket_height, bracket_width,
                              (0, 0, 0))
        horizontal = create_box(bracket_width, bracket_thickness, bracket_width,
                                (0, 0, 0))
        
        bracket = vertical.fuse(horizontal)
        
        # Sensör deliği
        sensor_hole_radius = 9  # M8 sensör için
        sensor_hole = create_cylinder(sensor_hole_radius, bracket_thickness + 5,
                                      (0, bracket_height/2, 0), (0, 1, 0))
        bracket = bracket.cut(sensor_hole)
        
        # Sıkıştırma vidası deliği
        screw_hole = create_cylinder(2, bracket_thickness + 5,
                                     (0, bracket_height/2 + 5, 0), (0, 1, 0))
        bracket = bracket.cut(screw_hole)
        
        # Montaj delikleri
        mount_hole_radius = 3.5
        mount_positions = [
            (-15, 10, -15),
            (15, 10, -15),
            (-15, 10, 15),
            (15, 10, 15)
        ]
        
        for pos in mount_positions:
            hole = create_cylinder(mount_hole_radius, bracket_thickness + 2, pos, (0, 1, 0))
            bracket = bracket.cut(hole)
    
    else:  # encoder
        # Encoder braketi
        bracket_width = 50
        bracket_height = 80
        bracket_thickness = 6
        
        bracket = create_box(bracket_width, bracket_height, bracket_thickness,
                            (-bracket_width/2, 0, -bracket_thickness/2))
        
        # Encoder mil deliği
        shaft_hole_radius = 12
        shaft_hole = create_cylinder(shaft_hole_radius, bracket_thickness + 5,
                                     (0, bracket_height/2, 0), (0, 1, 0))
        bracket = bracket.cut(shaft_hole)
        
        # Montaj delikleri
        mount_hole_radius = 4
        mount_positions = [
            (-20, 20, 0),
            (20, 20, 0),
            (-20, 60, 0),
            (20, 60, 0)
        ]
        
        for pos in mount_positions:
            hole = create_cylinder(mount_hole_radius, bracket_thickness + 2, pos)
            bracket = bracket.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = bracket
    
    return shape

def create_cable_carrier(doc, name="Cable_Carrier", length=500, width=80, height=40):
    """
    Kablo Kanalı / Tela
    
    Hareketli kablo koruma
    """
    # Tek bir segment
    segment_length = 50
    wall_thickness = 3
    
    segments = []
    num_segments = int(length / segment_length)
    
    for i in range(num_segments):
        z_pos = i * segment_length
        
        # Segment tabanı
        segment = create_box(width, wall_thickness, segment_length,
                            (-width/2, 0, z_pos))
        
        # Yan duvarlar
        left_wall = create_box(wall_thickness, height, segment_length,
                              (-width/2, 0, z_pos))
        right_wall = create_box(wall_thickness, height, segment_length,
                               (width/2 - wall_thickness, 0, z_pos))
        
        segment = segment.fuse(left_wall).fuse(right_wall)
        
        # Bölme duvarları (isteğe bağlı)
        if i < num_segments - 1:
            # Eklem delikleri
            hinge_hole_radius = 3
            hinge_positions = [
                (-width/2 + 5, wall_thickness, z_pos + 5),
                (width/2 - 8, wall_thickness, z_pos + 5),
                (-width/2 + 5, wall_thickness, z_pos + segment_length - 5),
                (width/2 - 8, wall_thickness, z_pos + segment_length - 5)
            ]
            
            for pos in hinge_positions:
                hole = create_cylinder(hinge_hole_radius, wall_thickness + 2, pos)
                segment = segment.cut(hole)
        
        segments.append(segment)
    
    # Tüm segmentleri birleştir
    if len(segments) == 0:
        return create_box(width, height, length, (-width/2, 0, 0))
    
    combined = segments[0]
    for s in segments[1:]:
        combined = combined.fuse(s)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = combined
    
    return shape

def create_control_panel_box(doc, name="Control_Panel_Box"):
    """
    Kontrol Panosu Kutusu
    """
    width = 400
    height = 500
    depth = 200
    wall_thickness = 4
    
    # Ana kutu
    box = create_hollow_box(width, height, depth, wall_thickness,
                           (-width/2, 0, -depth/2))
    
    # Kapı menteşe montajları
    hinge_mount_width = 40
    hinge_mount_height = 60
    hinge_mount_depth = 30
    
    hinge_positions = [
        (-width/2, height/2, -depth/2 + 30),
        (-width/2, height/2, -depth/2 + depth - 30)
    ]
    
    for pos in hinge_positions:
        hinge = create_box(hinge_mount_depth, hinge_mount_height, hinge_mount_width,
                          (pos[0], pos[1] - hinge_mount_height/2, pos[2] - hinge_mount_width/2))
        box = box.fuse(hinge)
    
    # Havalandırma delikleri
    vent_radius = 5
    for i in range(8):
        for j in range(3):
            vent_x = -width/2 + 30 + i * 50
            vent_y = 50 + j * 200
            vent = create_cylinder(vent_radius, wall_thickness + 2,
                                  (vent_x, vent_y, -depth/2 - 1), (0, 0, 1))
            box = box.cut(vent)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = box
    
    return shape

def create_junction_box(doc, name="Junction_Box"):
    """
    Dağıtım Kutusu (Junction Box)
    """
    width = 150
    height = 100
    depth = 80
    wall_thickness = 3
    
    # Ana kutu
    box = create_hollow_box(width, height, depth, wall_thickness,
                           (-width/2, 0, -depth/2))
    
    # Kablo girişleri
    cable_holes = [
        (0, height, -depth/2 + 20),    # Üst
        (0, 0, -depth/2 + 20),         # Alt
        (width/2, height/2, 0),        # Sağ
        (-width/2, height/2, 0),       # Sol
    ]
    
    for pos in cable_holes:
        hole = create_cylinder(15, wall_thickness + 5, pos)
        box = box.cut(hole)
    
    # Kapak montaj delikleri
    mount_hole_radius = 4
    mount_positions = [
        (-width/2 + 15, height - 10, -depth/2 + 5),
        (width/2 - 15, height - 10, -depth/2 + 5),
        (-width/2 + 15, 10, -depth/2 + 5),
        (width/2 - 15, 10, -depth/2 + 5)
    ]
    
    for pos in mount_positions:
        hole = create_cylinder(mount_hole_radius, depth, pos)
        box = box.cut(hole)
    
    shape = doc.addObject("Part::Feature", name)
    shape.Shape = box
    
    return shape

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def create_all_electronics_parts():
    """Tüm elektronik parçaları oluştur"""
    print("=" * 50)
    print("Elektronik Parçalar Generator")
    print("=" * 50)
    print(f"Export dizini: {EXPORT_DIR}")
    print()
    
    # R1-EC modül kutusu
    print("R1-EC modül kutusu oluşturuluyor...")
    doc_r1 = App.newDocument("R1-EC_Housing")
    r1_housing = create_r1_ec_housing(doc_r1)
    doc_r1.recompute()
    export_to_step(doc_r1, r1_housing, "R1-EC_Housing.stp")
    
    # R1-EC kapak
    print("R1-EC kapak oluşturuluyor...")
    doc_lid = App.newDocument("R1-EC_Lid")
    r1_lid = create_r1_ec_lid(doc_lid)
    doc_lid.recompute()
    export_to_step(doc_lid, r1_lid, "R1-EC_Lid.stp")
    
    # Sensör braketi (proximity)
    print("Sensör braketi (proximity) oluşturuluyor...")
    doc_sensor = App.newDocument("Sensor_Bracket")
    sensor_bracket = create_sensor_bracket(doc_sensor, "Sensor_Bracket", "proximity")
    doc_sensor.recompute()
    export_to_step(doc_sensor, sensor_bracket, "Sensor_Bracket_Proximity.stp")
    
    # Sensör braketi (encoder)
    print("Sensör braketi (encoder) oluşturuluyor...")
    doc_encoder = App.newDocument("Encoder_Bracket")
    encoder_bracket = create_sensor_bracket(doc_encoder, "Encoder_Bracket", "encoder")
    doc_encoder.recompute()
    export_to_step(doc_encoder, encoder_bracket, "Encoder_Bracket.stp")
    
    # Kablo kanalı
    print("Kablo kanalı oluşturuluyor...")
    doc_cable = App.newDocument("Cable_Carrier")
    cable_carrier = create_cable_carrier(doc_cable, "Cable_Carrier", 500, 80, 40)
    doc_cable.recompute()
    export_to_step(doc_cable, cable_carrier, "Cable_Carrier.stp")
    
    # Kontrol panosu
    print("Kontrol panosu kutusu oluşturuluyor...")
    doc_panel = App.newDocument("Control_Panel")
    panel_box = create_control_panel_box(doc_panel)
    doc_panel.recompute()
    export_to_step(doc_panel, panel_box, "Control_Panel_Box.stp")
    
    # Dağıtım kutusu
    print("Dağıtım kutusu oluşturuluyor...")
    doc_junction = App.newDocument("Junction_Box")
    junction_box = create_junction_box(doc_junction)
    doc_junction.recompute()
    export_to_step(doc_junction, junction_box, "Junction_Box.stp")
    
    print()
    print("=" * 50)
    print("Tüm elektronik parçalar oluşturuldu!")
    print("=" * 50)
    
    return doc_r1

if __name__ == "__main__":
    create_all_electronics_parts()