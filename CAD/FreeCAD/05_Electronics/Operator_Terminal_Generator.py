# FreeCAD Operatör Terminal Kutusu Modeli
# CNC Revizyon Projesi - GFB-60/30RE
# DOP-110CS HMI + R1-EC Uzak I/O Entegrasyonu
# MEKANİK + ELEKTRİKSEL BAĞLANTILAR

import FreeCAD as App
import Part
import math
import os
import csv
import json
from datetime import datetime

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/05_Electronics"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "Electronics")
ELECTRICAL_EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "Electrical")
os.makedirs(EXPORT_DIR, exist_ok=True)
os.makedirs(ELECTRICAL_EXPORT_DIR, exist_ok=True)

# ============================================================================
# ELEKTRİKSEL BAĞLANTI VERİ YAPILARI
# ============================================================================

class ElectricalConnection:
    """Elektriksel bağlantı tanımı"""
    def __init__(self, wire_id, source_device, source_terminal, target_device, 
                 target_terminal, cable_type, cross_section, color, length=0):
        self.wire_id = wire_id
        self.source_device = source_device
        self.source_terminal = source_terminal
        self.target_device = target_device
        self.target_terminal = target_terminal
        self.cable_type = cable_type
        self.cross_section = cross_section
        self.color = color
        self.length = length  # metre
    
    def to_dict(self):
        return {
            'Wire_ID': self.wire_id,
            'Source_Device': self.source_device,
            'Source_Terminal': self.source_terminal,
            'Target_Device': self.target_device,
            'Target_Terminal': self.target_terminal,
            'Cable_Type': self.cable_type,
            'Cross_Section_mm2': self.cross_section,
            'Color': self.color,
            'Length_m': self.length
        }

class TerminalBlock:
    """Terminal bloğu tanımı"""
    def __init__(self, terminal_id, terminal_type, pole_count, voltage_rating, 
                 current_rating, wire_range, torque, manufacturer, part_number):
        self.terminal_id = terminal_id
        self.terminal_type = terminal_type
        self.pole_count = pole_count
        self.voltage_rating = voltage_rating
        self.current_rating = current_rating
        self.wire_range = wire_range
        self.torque = torque  # Nm
        self.manufacturer = manufacturer
        self.part_number = part_number
        self.connections = []
    
    def add_connection(self, wire_id, signal_name, wire_color):
        self.connections.append({
            'wire_id': wire_id,
            'signal_name': signal_name,
            'wire_color': wire_color
        })
    
    def to_dict(self):
        return {
            'Terminal_ID': self.terminal_id,
            'Type': self.terminal_type,
            'Poles': self.pole_count,
            'Voltage_V': self.voltage_rating,
            'Current_A': self.current_rating,
            'Wire_Range_mm2': self.wire_range,
            'Torque_Nm': self.torque,
            'Manufacturer': self.manufacturer,
            'Part_Number': self.part_number,
            'Connection_Count': len(self.connections)
        }

class Device:
    """Cihaz tanımı"""
    def __init__(self, device_id, device_type, manufacturer, model, 
                 power_rating, voltage, location, ip_rating):
        self.device_id = device_id
        self.device_type = device_type
        self.manufacturer = manufacturer
        self.model = model
        self.power_rating = power_rating
        self.voltage = voltage
        self.location = location  # 'Main_Cabinet' veya 'Operator_Terminal'
        self.ip_rating = ip_rating
        self.connections = []
    
    def add_connection(self, connection):
        self.connections.append(connection)
    
    def to_dict(self):
        return {
            'Device_ID': self.device_id,
            'Type': self.device_type,
            'Manufacturer': self.manufacturer,
            'Model': self.model,
            'Power_Rating': self.power_rating,
            'Voltage': self.voltage,
            'Location': self.location,
            'IP_Rating': self.ip_rating,
            'Connection_Count': len(self.connections)
        }

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
    Operatör Terminal Başlığı Ana Gövde

    Tasarım dili:
    - LiSEC operatör istasyonu ergonomisi
    - Beckhoff benzeri ince çerçeveli, sade endüstriyel yüzey
    - Ayaklı terminal üst başlığı olarak kullanılacak kompakt gövde
    """
    # Terminal başlığı dış ölçüler
    width = 420
    height = 340
    depth = 220
    wall_thickness = 5
    
    # Ana gövde (arkası kapalı)
    enclosure = create_hollow_box(width, height, depth, wall_thickness,
                                  (-width/2, 0, -depth/2), open_top=False)
    
    # Ön panel montaj yüzeyi (DOP-110CS için)
    front_mount_width = 320
    front_mount_height = 250
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
                         (-din_rail_length/2, 25, -din_rail_width/2))
    
    # DIN ray oluğu (TS 35 standardı)
    din_channel = create_box(din_rail_length - 4, din_rail_height + 5, din_rail_width - 5,
                            (-din_rail_length/2 + 2, 25, -din_rail_width/2 + 2.5))
    din_rail = din_rail.cut(din_channel)

    enclosure = enclosure.fuse(din_rail)

    # Operatora bakan ust baslikta yumusak bir omuz olusturur
    crown = create_box(width - 40, 18, depth - 30,
                       (-(width - 40)/2, height - 10, -(depth - 30)/2))
    enclosure = enclosure.fuse(crown)
    
    # Kablo girişleri (alt tarafta, kolon icine dusen bolge)
    cable_hole_diameter = 36
    cable_hole_positions = [
        (-70, 0, -depth/2 + 30),
        (0, 0, -depth/2 + 30),
        (70, 0, -depth/2 + 30)
    ]
    
    for pos in cable_hole_positions:
        hole = create_cylinder(cable_hole_diameter/2, wall_thickness + 5, pos)
        enclosure = enclosure.cut(hole)
    
    # Havalandırma delikleri (yan duvarlarda, IP65 için filtreli)
    vent_radius = 4
    vent_rows = 2
    vent_cols = 4
    
    for row in range(vent_rows):
        for col in range(vent_cols):
            # Sol yan
            vent_x_left = -width/2 + 30 + col * 60
            vent_y_left = 95 + row * 110
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
        (-width/2, height/2, -depth/2 + 35),
        (-width/2, height/2, -depth/2 + depth - 35)
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
    Operatör terminal başlığı ön kapağı

    Beckhoff benzeri sade bir yüzey için
    ekran penceresi etrafında daha ince bordür kullanılır.
    """
    width = 420
    height = 340
    thickness = 5
    
    # Ana kapak
    door = create_box(width, thickness, height - 10, (-width/2, 0, -(height - 10)/2))
    
    # DOP-110CS ekran penceresi
    screen_width = 294
    screen_height = 234
    screen_window = create_box(screen_width, thickness + 2, screen_height,
                              (-screen_width/2, -1, 0))
    door = door.cut(screen_window)
    
    # Conta kanalı (IP65 için)
    gasket_channel_width = width - 20
    gasket_channel_height = height - 30
    gasket_depth = 3
    gasket_width = 10
    
    # Üst kanal
    top_gasket = create_box(gasket_channel_width, gasket_depth, gasket_width,
                           (-gasket_channel_width/2, thickness, (height - 10)/2 - gasket_width/2))
    door = door.fuse(top_gasket)
    
    # Alt kanal
    bottom_gasket = create_box(gasket_channel_width, gasket_depth, gasket_width,
                              (-gasket_channel_width/2, thickness, -(height - 10)/2 + gasket_width/2))
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
        (-width/2 + 30, 0, 110),
        (-width/2 + 30, 0, -110)
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


def create_terminal_pedestal_base(doc, name="Operator_Terminal_Base"):
    """
    Ayaklı terminal için ağır taban.
    Makine yanında devrilmeye dirençli, ince ama geniş bir ayak formu.
    """
    width = 520
    depth = 420
    height = 18

    base = create_box(width, height, depth, (-width/2, 0, -depth/2))

    # Kolon oturma pabucu
    plinth = create_box(180, 70, 140, (-90, height, -70))
    base = base.fuse(plinth)

    shape = doc.addObject("Part::Feature", name)
    shape.Shape = base
    return shape


def create_terminal_pedestal_column(doc, name="Operator_Terminal_Column"):
    """
    Kabloyu gizleyen kolon.
    LiSEC benzeri saha ergonomisi ile Beckhoff benzeri sade geometri arasında bir form.
    """
    outer = create_box(150, 1080, 110, (-75, 0, -55))
    inner = create_box(110, 1060, 70, (-55, 10, -35))
    column = outer.cut(inner)

    # Uste dogru hafif daralan omuz
    shoulder = create_box(210, 120, 150, (-105, 1080, -75))
    column = column.fuse(shoulder)

    shape = doc.addObject("Part::Feature", name)
    shape.Shape = column
    return shape


def create_terminal_head_support(doc, name="Operator_Terminal_Head_Support"):
    """
    Terminal basligini operatora dogru tasiyan one egimli destek.
    """
    support = create_box(220, 120, 150, (-110, 0, -75))

    # Egimli gorunus vermek icin ustte ikinci bir kademeli kitle
    wedge = create_box(180, 90, 120, (-90, 90, -60))
    support = support.fuse(wedge)

    shape = doc.addObject("Part::Feature", name)
    shape.Shape = support
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
    
    # 1. Ayak tabani
    base = create_terminal_pedestal_base(doc, "Pedestal_Base")
    parts.append(base)

    # 2. Kolon
    column = create_terminal_pedestal_column(doc, "Pedestal_Column")
    parts.append(column)

    # 3. Baslik tasiyici
    head_support = create_terminal_head_support(doc, "Head_Support")
    parts.append(head_support)

    # 4. Ana kutu / terminal basligi
    enclosure = create_terminal_enclosure(doc, "Enclosure")
    parts.append(enclosure)
    
    # 5. Kapak
    door = create_terminal_door(doc, "Door")
    parts.append(door)
    
    # 6. DOP-110CS HMI
    hmi = create_dop_110cs_housing(doc, "HMI")
    parts.append(hmi)
    
    # 7. R1-EC montaj plakası
    r1_plate = create_r1_ec_mounting_plate(doc, "R1-EC_Plate")
    parts.append(r1_plate)
    
    # 8. Kablo giriş rakorları
    gland1 = create_cable_gland(doc, "Gland_1", "M40")
    parts.append(gland1)
    
    gland2 = create_cable_gland(doc, "Gland_2", "M32")
    parts.append(gland2)
    
    # 9. IP65 filtreler
    filter1 = create_ip65_filter(doc, "Filter_Left")
    parts.append(filter1)
    
    filter2 = create_ip65_filter(doc, "Filter_Right")
    parts.append(filter2)
    
    # Tüm parçaları birleştir (basit montaj)
    if len(parts) > 0:
        combined = parts[0].Shape if hasattr(parts[0], "Shape") else parts[0]
        for part in parts[1:]:
            part_shape = part.Shape if hasattr(part, "Shape") else part
            combined = combined.fuse(part_shape)

        shape = doc.addObject("Part::Feature", name)
        shape.Shape = combined

        return shape
    
    return None

# ============================================================================
# ELEKTRİKSEL BAĞLANTI TANIMLARI VE EXPORT FONKSİYONLARI
# ============================================================================

def create_electrical_definitions():
    """
    Operatör Terminal Kutusu için elektriksel bağlantı tanımları
    
    Returns:
        devices: Device listesi
        terminals: TerminalBlock listesi
        connections: ElectricalConnection listesi
    """
    devices = []
    terminals = []
    connections = []
    
    # =========================================================================
    # CİHAZ TANIMLARI
    # =========================================================================
    
    # --- Terminal Kutusu İçindeki Cihazlar ---
    
    # DOP-110CS HMI
    dop_110cs = Device(
        device_id='U2',
        device_type='HMI_Panel',
        manufacturer='Delta',
        model='DOP-110CS',
        power_rating='15W',
        voltage='24VDC',
        location='Operator_Terminal',
        ip_rating='IP65 (front)'
    )
    devices.append(dop_110cs)
    
    # R1-EC01 Bus Coupler
    r1_ec01 = Device(
        device_id='U3',
        device_type='EtherCAT_Bus_Coupler',
        manufacturer='Delta',
        model='R1-EC01',
        power_rating='5W',
        voltage='24VDC',
        location='Operator_Terminal',
        ip_rating='IP20'
    )
    devices.append(r1_ec01)
    
    # R1-EC0902D (32-CH DI)
    r1_ec0902d = Device(
        device_id='U4',
        device_type='32-CH_Digital_Input',
        manufacturer='Delta',
        model='R1-EC0902D',
        power_rating='3W',
        voltage='24VDC',
        location='Operator_Terminal',
        ip_rating='IP20'
    )
    devices.append(r1_ec0902d)
    
    # R1-EC0902O (32-CH DO Relay)
    r1_ec0902o = Device(
        device_id='U5',
        device_type='32-CH_Relay_Output',
        manufacturer='Delta',
        model='R1-EC0902O',
        power_rating='5W',
        voltage='24VDC/250VAC',
        location='Operator_Terminal',
        ip_rating='IP20'
    )
    devices.append(r1_ec0902o)
    
    # --- Ana Pano İçindeki Cihazlar (Terminal'den bağlanan) ---
    
    # NC300 CNC Controller
    nc300 = Device(
        device_id='U1',
        device_type='CNC_Controller',
        manufacturer='Delta',
        model='NC300',
        power_rating='50W',
        voltage='24VDC',
        location='Main_Cabinet',
        ip_rating='IP20'
    )
    devices.append(nc300)
    
    # PSU (24V/10A)
    psu = Device(
        device_id='PS1',
        device_type='Power_Supply',
        manufacturer='Delta',
        model='DVP-PS02',
        power_rating='240W',
        voltage='24VDC/10A',
        location='Main_Cabinet',
        ip_rating='IP20'
    )
    devices.append(psu)
    
    # =========================================================================
    # TERMİNAL BLOKLARI (Terminal Kutusu İçinde)
    # =========================================================================
    
    # X1: 24V DC Power Distribution (Terminal Kutusu)
    x1 = TerminalBlock(
        terminal_id='X1',
        terminal_type='Power_Distribution',
        pole_count=8,
        voltage_rating=48,
        current_rating=24,
        wire_range='0.5-4.0',
        torque=0.6,
        manufacturer='Phoenix Contact',
        part_number='MSTB 2.5/8-ST'
    )
    terminals.append(x1)
    
    # X2: EtherCAT Network
    x2 = TerminalBlock(
        terminal_id='X2',
        terminal_type='Ethernet_RJ45',
        pole_count=8,
        voltage_rating=0,
        current_rating=0,
        wire_range='CAT6',
        torque=0,
        manufacturer='Phoenix Contact',
        part_number='VS-RJ45-RJ45-945/5m'
    )
    terminals.append(x2)
    
    # X3: HMI Ethernet
    x3 = TerminalBlock(
        terminal_id='X3',
        terminal_type='Ethernet_RJ45',
        pole_count=8,
        voltage_rating=0,
        current_rating=0,
        wire_range='CAT6',
        torque=0,
        manufacturer='Phoenix Contact',
        part_number='VS-RJ45-RJ45-945/5m'
    )
    terminals.append(x3)
    
    # X4: Digital Inputs (Push Buttons)
    x4 = TerminalBlock(
        terminal_id='X4',
        terminal_type='Signal_DI',
        pole_count=16,
        voltage_rating=48,
        current_rating=2,
        wire_range='0.25-1.5',
        torque=0.5,
        manufacturer='Phoenix Contact',
        part_number='MSTB 2.5/16-ST'
    )
    terminals.append(x4)
    
    # X5: Digital Outputs (Indicators)
    x5 = TerminalBlock(
        terminal_id='X5',
        terminal_type='Signal_DO',
        pole_count=12,
        voltage_rating=250,
        current_rating=2,
        wire_range='0.25-1.5',
        torque=0.5,
        manufacturer='Phoenix Contact',
        part_number='MSTB 2.5/12-ST'
    )
    terminals.append(x5)
    
    # X6: PE Ground Bar
    x6 = TerminalBlock(
        terminal_id='X6',
        terminal_type='PE_Ground_Bar',
        pole_count=10,
        voltage_rating=0,
        current_rating=100,
        wire_range='1.5-6.0',
        torque=1.5,
        manufacturer='Phoenix Contact',
        part_number='PTTB 2.5-PE'
    )
    terminals.append(x6)
    
    # =========================================================================
    # ELEKTRİKSEL BAĞLANTILAR
    # =========================================================================
    wire_counter = 1
    
    # --- GÜÇ BAĞLANTILARI ---
    
    # Ana panodan terminal kutusuna 24V DC güç
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='PS1',
        source_terminal='+24V',
        target_device='X1',
        target_terminal='1',
        cable_type='H07V-K',
        cross_section=2.5,
        color='Red',
        length=20
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='PS1',
        source_terminal='0V',
        target_device='X1',
        target_terminal='2',
        cable_type='H07V-K',
        cross_section=2.5,
        color='Black',
        length=20
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='PS1',
        source_terminal='PE',
        target_device='X6',
        target_terminal='1',
        cable_type='H07V-K',
        cross_section=4.0,
        color='Green/Yellow',
        length=20
    ))
    wire_counter += 1
    
    # X1'den DOP-110CS'e güç
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X1',
        source_terminal='3',
        target_device='U2',
        target_terminal='+24V',
        cable_type='H07V-K',
        cross_section=1.5,
        color='Red',
        length=0.5
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X1',
        source_terminal='4',
        target_device='U2',
        target_terminal='0V',
        cable_type='H07V-K',
        cross_section=1.5,
        color='Black',
        length=0.5
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X6',
        source_terminal='2',
        target_device='U2',
        target_terminal='PE',
        cable_type='H07V-K',
        cross_section=1.5,
        color='Green/Yellow',
        length=0.5
    ))
    wire_counter += 1
    
    # X1'den R1-EC01'e güç
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X1',
        source_terminal='5',
        target_device='U3',
        target_terminal='V+',
        cable_type='H07V-K',
        cross_section=1.5,
        color='Red',
        length=0.3
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X1',
        source_terminal='6',
        target_device='U3',
        target_terminal='0V',
        cable_type='H07V-K',
        cross_section=1.5,
        color='Black',
        length=0.3
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X6',
        source_terminal='3',
        target_device='U3',
        target_terminal='PE',
        cable_type='H07V-K',
        cross_section=1.5,
        color='Green/Yellow',
        length=0.3
    ))
    wire_counter += 1
    
    # --- ETHERCAT BAĞLANTILARI ---
    
    # NC300'den R1-EC01'e EtherCAT
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U1',
        source_terminal='CN1 (EtherCAT)',
        target_device='X2',
        target_terminal='RJ45',
        cable_type='CAT6 SF/UTP',
        cross_section=0.14,
        color='Blue',
        length=20
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X2',
        source_terminal='RJ45',
        target_device='U3',
        target_terminal='ECAT IN',
        cable_type='CAT6 SF/UTP',
        cross_section=0.14,
        color='Blue',
        length=0.5
    ))
    wire_counter += 1
    
    # NC300'den DOP-110CS'e Ethernet
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U1',
        source_terminal='CN3 (Ethernet)',
        target_device='X3',
        target_terminal='RJ45',
        cable_type='CAT5e UTP',
        cross_section=0.14,
        color='Gray',
        length=20
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X3',
        source_terminal='RJ45',
        target_device='U2',
        target_terminal='ETH',
        cable_type='CAT5e UTP',
        cross_section=0.14,
        color='Gray',
        length=0.5
    ))
    wire_counter += 1
    
    # --- DİJİTAL GİRİŞLER (Operatör Butonları) ---
    
    # START butonu (Yeşil)
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X4',
        source_terminal='1',
        target_device='X1',
        target_terminal='7',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Green',
        length=0.5
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U4',
        source_terminal='DI_0',
        target_device='X4',
        target_terminal='2',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Blue',
        length=0.3
    ))
    wire_counter += 1
    
    # STOP butonu (Kırmızı)
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X4',
        source_terminal='3',
        target_device='X1',
        target_terminal='7',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Green',
        length=0.5
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U4',
        source_terminal='DI_1',
        target_device='X4',
        target_terminal='4',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Blue',
        length=0.3
    ))
    wire_counter += 1
    
    # E-STOP butonu (Sarı)
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X4',
        source_terminal='5',
        target_device='X1',
        target_terminal='8',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Yellow',
        length=0.5
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U4',
        source_terminal='DI_2',
        target_device='X4',
        target_terminal='6',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Blue',
        length=0.3
    ))
    wire_counter += 1
    
    # RESET butonu (Mavi)
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X4',
        source_terminal='7',
        target_device='X1',
        target_terminal='7',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Green',
        length=0.5
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U4',
        source_terminal='DI_3',
        target_device='X4',
        target_terminal='8',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Blue',
        length=0.3
    ))
    wire_counter += 1
    
    # --- DİJİTAL ÇIKIŞLAR (İndikatörler) ---
    
    # RUN LED (Yeşil)
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U5',
        source_terminal='DO_0',
        target_device='X5',
        target_terminal='1',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Green',
        length=0.3
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X5',
        source_terminal='2',
        target_device='X1',
        target_terminal='7',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Green',
        length=0.5
    ))
    wire_counter += 1
    
    # FAULT LED (Kırmızı)
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='U5',
        source_terminal='DO_1',
        target_device='X5',
        target_terminal='3',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Red',
        length=0.3
    ))
    wire_counter += 1
    
    connections.append(ElectricalConnection(
        wire_id=f'W{wire_counter:03d}',
        source_device='X5',
        source_terminal='4',
        target_device='X1',
        target_terminal='7',
        cable_type='H07V-K',
        cross_section=0.5,
        color='Red',
        length=0.5
    ))
    wire_counter += 1
    
    return devices, terminals, connections

def export_to_step(doc, obj, filename):
    """STEP dosyası olarak export et"""
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"  → {filepath} oluşturuldu")
    return filepath

def export_connections_to_csv(connections, filename='Wire_Connections.csv'):
    """Elektriksel bağlantıları CSV'ye export et"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Wire_ID', 'Source_Device', 'Source_Terminal', 
                      'Target_Device', 'Target_Terminal', 'Cable_Type', 
                      'Cross_Section_mm2', 'Color', 'Length_m']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for conn in connections:
            writer.writerow(conn.to_dict())
    
    print(f"  → {filepath} oluşturuldu ({len(connections)} bağlantı)")
    return filepath

def export_terminals_to_csv(terminals, filename='Terminal_Blocks.csv'):
    """Terminal bloklarını CSV'ye export et"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Terminal_ID', 'Type', 'Poles', 'Voltage_V', 'Current_A',
                      'Wire_Range_mm2', 'Torque_Nm', 'Manufacturer', 
                      'Part_Number', 'Connection_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for term in terminals:
            writer.writerow(term.to_dict())
    
    print(f"  → {filepath} oluşturuldu ({len(terminals)} terminal)")
    return filepath

def export_devices_to_csv(devices, filename='Device_List.csv'):
    """Cihaz listesini CSV'ye export et"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Device_ID', 'Type', 'Manufacturer', 'Model', 
                      'Power_Rating', 'Voltage', 'Location', 'IP_Rating', 
                      'Connection_Count']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for dev in devices:
            writer.writerow(dev.to_dict())
    
    print(f"  → {filepath} oluşturuldu ({len(devices)} cihaz)")
    return filepath

def export_bom_to_csv(devices, terminals, connections, filename='BOM.csv'):
    """Malzeme listesini (BOM) CSV'ye export et"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    # Kablo özeti
    cable_summary = {}
    for conn in connections:
        key = (conn.cable_type, conn.cross_section, conn.color)
        if key not in cable_summary:
            cable_summary[key] = {'length': 0, 'count': 0}
        cable_summary[key]['length'] += conn.length
        cable_summary[key]['count'] += 1
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Category', 'Item', 'Specification', 'Quantity', 'Unit']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        # Cihazlar
        for dev in devices:
            writer.writerow({
                'Category': 'Device',
                'Item': f"{dev.device_id} - {dev.model}",
                'Specification': f"{dev.device_type}, {dev.voltage}, {dev.power_rating}",
                'Quantity': 1,
                'Unit': 'pcs'
            })
        
        # Terminaller
        for term in terminals:
            writer.writerow({
                'Category': 'Terminal',
                'Item': f"{term.terminal_id} - {term.part_number}",
                'Specification': f"{term.terminal_type}, {term.pole_count}-pole, {term.torque}Nm",
                'Quantity': 1,
                'Unit': 'pcs'
            })
        
        # Kablolar
        for (cable_type, cross_section, color), data in cable_summary.items():
            writer.writerow({
                'Category': 'Cable',
                'Item': cable_type,
                'Specification': f"{cross_section}mm², {color}",
                'Quantity': round(data['length'], 2),
                'Unit': 'meters'
            })
    
    print(f"  → {filepath} oluşturuldu")
    return filepath

def export_to_json(devices, terminals, connections, filename='Electrical_Data.json'):
    """Tüm elektriksel verileri JSON'a export et"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    data = {
        'metadata': {
            'project': 'GFB-60/30RE CNC Revizyon',
            'document': 'Operator Terminal Electrical Connections',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0'
        },
        'devices': [dev.to_dict() for dev in devices],
        'terminals': [term.to_dict() for term in terminals],
        'connections': [conn.to_dict() for conn in connections]
    }
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=2, ensure_ascii=False)
    
    print(f"  → {filepath} oluşturuldu")
    return filepath

def export_connection_matrix(connections, filename='Connection_Matrix.csv'):
    """Bağlantı matrisini export et (From/To formatı)"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Wire_ID', 'From_Device', 'From_Terminal', 'To_Device', 
                      'To_Terminal', 'Signal_Name', 'Cable_Type', 'Color']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for conn in connections:
            # Signal name'ı terminal'den çıkar
            signal_name = f"{conn.source_terminal} → {conn.target_terminal}"
            
            writer.writerow({
                'Wire_ID': conn.wire_id,
                'From_Device': conn.source_device,
                'From_Terminal': conn.source_terminal,
                'To_Device': conn.target_device,
                'To_Terminal': conn.target_terminal,
                'Signal_Name': signal_name,
                'Cable_Type': conn.cable_type,
                'Color': conn.color
            })
    
    print(f"  → {filepath} oluşturuldu ({len(connections)} bağlantı)")
    return filepath

def export_cable_schedule(connections, filename='Cable_Schedule.csv'):
    """Kablo programını export et (kablo tipi ve uzunluk özeti)"""
    filepath = os.path.join(ELECTRICAL_EXPORT_DIR, filename)
    
    # Kablo tipi ve güzergah bazında grupla
    route_summary = {}
    for conn in connections:
        route_key = f"{conn.source_device} → {conn.target_device}"
        if route_key not in route_summary:
            route_summary[route_key] = {
                'cable_type': conn.cable_type,
                'cross_section': conn.cross_section,
                'color': conn.color,
                'wires': [],
                'total_length': 0
            }
        route_summary[route_key]['wires'].append(conn.wire_id)
        route_summary[route_key]['total_length'] = max(
            route_summary[route_key]['total_length'], 
            conn.length
        )
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Route', 'Cable_Type', 'Cross_Section_mm2', 'Color', 
                      'Wire_Count', 'Wire_IDs', 'Total_Length_m']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for route, data in route_summary.items():
            writer.writerow({
                'Route': route,
                'Cable_Type': data['cable_type'],
                'Cross_Section_mm2': data['cross_section'],
                'Color': data['color'],
                'Wire_Count': len(data['wires']),
                'Wire_IDs': ', '.join(data['wires']),
                'Total_Length_m': data['total_length']
            })
    
    print(f"  → {filepath} oluşturuldu ({len(route_summary)} güzergah)")
    return filepath

def create_all_terminal_parts():
    """Tüm terminal parçalarını ve elektriksel bağlantıları oluştur"""
    print("=" * 70)
    print("Operatör Terminal Kutusu Generator")
    print("GFB-60/30RE - DOP-110CS + R1-EC Entegrasyonu")
    print("MEKANİK + ELEKTRİKSEL BAĞLANTILAR")
    print("=" * 70)
    print(f"STEP Export dizini: {EXPORT_DIR}")
    print(f"Elektrik Export dizini: {ELECTRICAL_EXPORT_DIR}")
    print()

    # ========================================================================
    # MEKANİK PARÇALAR
    # ========================================================================
    print(">>> MEKANİK PARÇALAR <<<")
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
    
    # ========================================================================
    # ELEKTRİKSEL BAĞLANTILAR
    # ========================================================================
    print(">>> ELEKTRİKSEL BAĞLANTILAR <<<")
    print()
    
    print("9. Elektriksel bağlantı tanımları oluşturuluyor...")
    devices, terminals, connections = create_electrical_definitions()
    print(f"   → {len(devices)} cihaz tanımlandı")
    print(f"   → {len(terminals)} terminal bloğu tanımlandı")
    print(f"   → {len(connections)} elektriksel bağlantı tanımlandı")
    print()
    
    print("10. Elektriksel veriler export ediliyor...")
    export_connections_to_csv(connections, 'Wire_Connections.csv')
    export_terminals_to_csv(terminals, 'Terminal_Blocks.csv')
    export_devices_to_csv(devices, 'Device_List.csv')
    export_bom_to_csv(devices, terminals, connections, 'BOM.csv')
    export_to_json(devices, terminals, connections, 'Electrical_Data.json')
    export_connection_matrix(connections, 'Connection_Matrix.csv')
    export_cable_schedule(connections, 'Cable_Schedule.csv')
    print()

    print("=" * 70)
    print("TÜM TERMINAL PARÇALARI VE BAĞLANTILAR OLUŞTURULDU!")
    print("=" * 70)
    print()
    print("MEKANİK DOSYALAR (STEP):")
    print("  1. DOP-110CS_Housing.stp")
    print("  2. DOP-110CS_Panel_Cutout.stp")
    print("  3. Operator_Terminal_Enclosure.stp")
    print("  4. Operator_Terminal_Door.stp")
    print("  5. R1-EC_Mounting_Plate.stp")
    print("  6. Cable_Gland_M40.stp")
    print("  7. IP65_Vent_Filter.stp")
    print("  8. Operator_Terminal_Complete.stp")
    print()
    print("ELEKTRİK DOSYALAR (CSV + JSON):")
    print("  1. Wire_Connections.csv (Tüm kablo bağlantıları)")
    print("  2. Terminal_Blocks.csv (Terminal blokları)")
    print("  3. Device_List.csv (Cihaz listesi)")
    print("  4. BOM.csv (Malzeme listesi)")
    print("  5. Electrical_Data.json (Tüm veriler)")
    print("  6. Connection_Matrix.csv (From/To matrisi)")
    print("  7. Cable_Schedule.csv (Kablo programı)")
    print()
    print("DİZİNLER:")
    print(f"  STEP: {EXPORT_DIR}")
    print(f"  Elektrik: {ELECTRICAL_EXPORT_DIR}")
    print()

    return doc_assembly

if __name__ == "__main__":
    create_all_terminal_parts()
