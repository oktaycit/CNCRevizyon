# -*- coding: utf-8 -*-
"""
LiSEC GFB-60/30RE-S - Hibrit Sistem (Düz Cam + Lamine Cam)
FreeCAD Assembly4 Workbench için Python Script

Özellikler:
- X Ekseni (Gantry) - 6000mm hareket
- Y Ekseni (Portal) - 3000mm hareket  
- Z Ekseni (Üst Kesim Kafası) - 300mm strok
- V Ekseni (VB-Modul Alt Kesici) - Y ile senkronize
- VB-Modul Bileşenleri:
  * Alt kesici ünitesi
  * Isıtıcı çubuk (Heizstab)
  * Vakum vantuz sistemi
  * Kırma çıtası (Brechleiste)
  * Ayırma bıçağı (Trennklinge)

Yazar: CNC AI Orchestrator
Tarih: 2026-04-04
"""

import FreeCAD as App
import Part
import argparse
import ast
import datetime
import json
import math
import os
import re
import sys
import time

try:
    import Import
except ImportError:
    Import = None

try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None

# =============================================================================
# MAKİNE PARAMETRELERİ
# =============================================================================

class MachineParameters:
    """GFB-60/30RE-S hibrit sistem parametreleri"""
    
    # Eksen limitleri
    X_MAX = 6000.0  # mm
    Y_MAX = 3000.0  # mm
    Z_MAX = 300.0   # mm (üst kesim)
    V_MAX = 300.0   # mm (alt kesici strok)
    
    # Hız parametreleri
    X_HIZ_MAX = 80000.0   # mm/dk (80 m/dk)
    Y_HIZ_MAX = 60000.0   # mm/dk
    Z_HIZ_MAX = 5000.0    # mm/dk
    V_HIZ_MAX = 60000.0   # mm/dk (Y ile senkronize)
    
    # Başlangıç pozisyonları (Home)
    X_HOME = 0.0
    Y_HOME = 0.0
    Z_HOME = 300.0  # Üst pozisyon (güvenli)
    V_HOME = 0.0    # Alt pozisyon (geri çekilmiş)
    
    # Şase boyutları
    FRAME_LENGTH = 6800.0  # mm
    FRAME_WIDTH = 3600.0   # mm
    FRAME_HEIGHT = 820.0   # mm
    
    # Portal boyutları
    PORTAL_WIDTH = 3300.0  # mm (X köprüsü)
    PORTAL_HEIGHT = 500.0  # mm

    # Hat modulleri
    LOADER_LENGTH = 2600.0   # mm
    LOADER_WIDTH = 3600.0    # mm
    LOADER_HEIGHT = 980.0    # mm
    BREAKOUT_LENGTH = 3000.0 # mm
    BREAKOUT_WIDTH = 3600.0  # mm
    BREAKOUT_HEIGHT = 950.0  # mm
    INTERFACE_GAP = 250.0    # mm
    
    # Kesim parametreleri
    CAM_KALINLIGI = 16.0   # mm (düz cam)
    LAMINE_KALINLIK = 8.76 # mm (4+0.76+4 lamine)
    KESIM_BASINCI = 0.4    # MPa
    
    # VB-Modul parametreleri
    ISITMA_SICAKLIK = 135.0  # °C
    ISITMA_SURES = 4.0       # sn
    VAKUM_BASINC = 0.8       # bar
    AYIRMA_BASINC = 2.8      # bar
    KIRMA_BASINC = 4.0       # bar


# =============================================================================
# PARÇA OLUŞTURMA FONKSİYONLARI
# =============================================================================

def create_box(doc, name, width, height, depth, color, position=App.Vector(0,0,0)):
    """Basit kutu geometrisi oluştur"""
    box = doc.addObject("Part::Box", name)
    box.Width = width
    box.Height = height
    box.Length = depth
    box.Label = name
    box.Placement.Base = position
    if hasattr(box, 'ViewObject') and box.ViewObject:
        box.ViewObject.ShapeColor = color
    return box


def create_cylinder(doc, name, radius, height, color, position=App.Vector(0,0,0), rotation=App.Rotation(0,0,0)):
    """Silindir geometrisi oluştur"""
    cyl = doc.addObject("Part::Cylinder", name)
    cyl.Radius = radius
    cyl.Height = height
    cyl.Label = name
    cyl.Placement.Base = position
    cyl.Placement.Rotation = rotation
    if hasattr(cyl, 'ViewObject') and cyl.ViewObject:
        cyl.ViewObject.ShapeColor = color
    return cyl


def create_sphere(doc, name, radius, color, position=App.Vector(0,0,0)):
    """Küre geometrisi oluştur"""
    sph = doc.addObject("Part::Sphere", name)
    sph.Radius = radius
    sph.Label = name
    sph.Placement.Base = position
    if hasattr(sph, 'ViewObject') and sph.ViewObject:
        sph.ViewObject.ShapeColor = color
    return sph


def create_text_note(doc, name, text, position):
    """Belgelendirme icin basit etiket objesi olustur"""
    try:
        note = doc.addObject("App::AnnotationLabel", name)
        note.LabelText = [text]
        note.BasePosition = position
        return note
    except Exception:
        return None


def create_group(doc, name, label=None):
    """FreeCAD agacinda duzenli hiyerarsi icin grup olustur"""
    group = doc.addObject("App::DocumentObjectGroup", name)
    group.Label = label or name
    return group


def add_objects_to_group(group, items):
    """Sozluk/liste/tekil nesneleri recurse ederek gruba ekle"""
    if items is None:
        return
    if isinstance(items, dict):
        for value in items.values():
            add_objects_to_group(group, value)
        return
    if isinstance(items, (list, tuple, set)):
        for value in items:
            add_objects_to_group(group, value)
        return
    if hasattr(items, "Name"):
        try:
            group.addObject(items)
        except Exception:
            pass


# =============================================================================
# ANA ŞASE MONTAJI
# =============================================================================

def create_frame_assembly(doc, params):
    """
    Ana şase/profil assembly'si
    """
    print("  - Şase oluşturuluyor...")
    
    # Ana uzun profiller (X ekseni boyunca)
    left_rail = create_box(
        doc, "Frame_Left_Rail",
        width=100, height=100, depth=params.FRAME_LENGTH,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 0, 0)
    )
    
    right_rail = create_box(
        doc, "Frame_Right_Rail",
        width=100, height=100, depth=params.FRAME_LENGTH,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, params.FRAME_WIDTH - 100, 0)
    )
    
    # Ön ve arka profiller (Y ekseni boyunca)
    front_beam = create_box(
        doc, "Frame_Front_Beam",
        width=params.FRAME_WIDTH, height=100, depth=100,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 0, 0)
    )
    
    back_beam = create_box(
        doc, "Frame_Back_Beam",
        width=params.FRAME_WIDTH, height=100, depth=100,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 0, params.FRAME_LENGTH - 100)
    )
    
    # Destek ayakları
    for i in range(4):
        leg = create_box(
            doc, f"Frame_Leg_{i+1}",
            width=150, height=700, depth=150,
            color=(0.3, 0.3, 0.3),
            position=App.Vector(
                100 if i % 2 == 0 else params.FRAME_LENGTH - 200,
                100 if i < 2 else params.FRAME_WIDTH - 250,
                0
            )
        )
    
    # Masa üstü ızgarası (cam destek)
    table_grid = create_box(
        doc, "Table_Grid",
        width=params.FRAME_WIDTH - 100, height=50, depth=params.FRAME_LENGTH - 200,
        color=(0.4, 0.4, 0.4),
        position=App.Vector(100, 50, 100)
    )
    
    return {
        'left_rail': left_rail,
        'right_rail': right_rail,
        'front_beam': front_beam,
        'back_beam': back_beam,
        'table_grid': table_grid
    }


# =============================================================================
# PORTAL KÖPRÜSÜ (X EKSENİ)
# =============================================================================

def create_portal_assembly(doc, frame, params):
    """
    Portal köprüsü (X ekseni gantry)
    """
    print("  - Portal oluşturuluyor...")
    
    # X ekseni köprüsü
    bridge = create_box(
        doc, "Portal_Bridge",
        width=params.PORTAL_WIDTH, height=150, depth=220,
        color=(0.2, 0.4, 0.6),
        position=App.Vector(150, 100, 0)
    )
    
    # Dikey destekler
    left_support = create_box(
        doc, "Portal_Left_Support",
        width=200, height=400, depth=150,
        color=(0.2, 0.4, 0.6),
        position=App.Vector(150, 100, 100)
    )
    
    right_support = create_box(
        doc, "Portal_Right_Support",
        width=200, height=400, depth=150,
        color=(0.2, 0.4, 0.6),
        position=App.Vector(150, params.PORTAL_WIDTH - 50, 100)
    )
    
    # X ekseni lineer rayları
    rail_left = create_box(
        doc, "X_Rail_Left",
        width=50, height=30, depth=params.FRAME_LENGTH,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(50, 150, 100)
    )
    
    rail_right = create_box(
        doc, "X_Rail_Right",
        width=50, height=30, depth=params.FRAME_LENGTH,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(50, params.FRAME_WIDTH - 250, 100)
    )
    
    # X ekseni motorları (Delta ECMA-E11320)
    motor_x_left = create_cylinder(
        doc, "Motor_X_Left",
        radius=65, height=180,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(50, 50, 50)
    )
    
    motor_x_right = create_cylinder(
        doc, "Motor_X_Right",
        radius=65, height=180,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(50, params.FRAME_WIDTH - 300, 50)
    )
    
    return {
        'bridge': bridge,
        'left_support': left_support,
        'right_support': right_support,
        'rail_left': rail_left,
        'rail_right': rail_right,
        'motor_left': motor_x_left,
        'motor_right': motor_x_right
    }


# =============================================================================
# Y EKSENİ (PORTAL ÜZERİNDE HAREKET)
# =============================================================================

def create_y_axis_assembly(doc, portal, params):
    """
    Y ekseni (Portal üzerinde hareket)
    """
    print("  - Y ekseni oluşturuluyor...")
    
    # Y ekseni kızak
    carriage = create_box(
        doc, "Y_Carriage",
        width=400, height=200, depth=250,
        color=(0.8, 0.2, 0.2),
        position=App.Vector(
            portal['bridge'].Placement.Base.x + 1500,
            portal['bridge'].Placement.Base.y,
            portal['bridge'].Placement.Base.z + 150
        )
    )
    
    # Y ekseni lineer ray
    y_rail = create_box(
        doc, "Y_Rail",
        width=50, height=30, depth=params.PORTAL_WIDTH,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(
            portal['bridge'].Placement.Base.x + 100,
            portal['bridge'].Placement.Base.y,
            portal['bridge'].Placement.Base.z + 150
        )
    )
    
    # Y ekseni motoru (Delta ECMA-E11315)
    motor_y = create_cylinder(
        doc, "Motor_Y",
        radius=55, height=150,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(
            carriage.Placement.Base.x - 50,
            carriage.Placement.Base.y - 50,
            carriage.Placement.Base.z + 100
        )
    )
    
    return {
        'carriage': carriage,
        'rail': y_rail,
        'motor': motor_y
    }


# =============================================================================
# Z EKSENİ (ÜST KESİM KAFASI)
# =============================================================================

def create_z_axis_assembly(doc, y_axis):
    """
    Z ekseni (Üst kesim kafası assembly'si)
    """
    print("  - Z ekseni (üst kesim kafası) oluşturuluyor...")
    
    # Z dik mili
    column = create_box(
        doc, "Z_Column",
        width=80, height=350, depth=80,
        color=(0.4, 0.4, 0.4),
        position=App.Vector(
            y_axis['carriage'].Placement.Base.x + 160,
            y_axis['carriage'].Placement.Base.y + 100,
            y_axis['carriage'].Placement.Base.z
        )
    )
    
    # Z hareketli kızak
    z_carriage = create_box(
        doc, "Z_Carriage",
        width=100, height=100, depth=100,
        color=(0.2, 0.5, 0.8),
        position=App.Vector(
            column.Placement.Base.x - 10,
            column.Placement.Base.y + 200,
            column.Placement.Base.z
        )
    )
    
    # Kesim kafası gövdesi
    head_body = create_box(
        doc, "Cutting_Head",
        width=80, height=150, depth=80,
        color=(1.0, 0.5, 0.0),
        position=App.Vector(
            z_carriage.Placement.Base.x,
            z_carriage.Placement.Base.y - 100,
            z_carriage.Placement.Base.z
        )
    )
    
    # Kesim tekeri (üst)
    wheel = create_cylinder(
        doc, "Cutting_Wheel",
        radius=20, height=15,
        color=(0.8, 0.8, 0.8),
        position=App.Vector(
            head_body.Placement.Base.x,
            head_body.Placement.Base.y - 80,
            head_body.Placement.Base.z + 40
        )
    )
    
    # Z ekseni motoru
    motor_z = create_cylinder(
        doc, "Motor_Z",
        radius=40, height=100,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(
            column.Placement.Base.x,
            column.Placement.Base.y + 350,
            column.Placement.Base.z
        )
    )
    
    # Rodaj kafası (C ekseni)
    c_axis_head = create_cylinder(
        doc, "C_Axis_Head",
        radius=30, height=60,
        color=(0.6, 0.6, 0.6),
        position=App.Vector(
            head_body.Placement.Base.x + 50,
            head_body.Placement.Base.y - 50,
            head_body.Placement.Base.z + 40
        )
    )
    
    return {
        'column': column,
        'carriage': z_carriage,
        'head': head_body,
        'wheel': wheel,
        'motor': motor_z,
        'c_axis': c_axis_head
    }


# =============================================================================
# VB-MODUL: ALT KESİCİ ÜNİTESİ (V EKSENİ)
# =============================================================================

def create_vb_lower_cutter(doc, frame):
    """
    VB-Modul alt kesici ünitesi (V ekseni)
    Masa altında, Y ekseni ile senkronize hareket eder
    """
    print("  - VB-Modul alt kesici oluşturuluyor...")
    
    # V ekseni taban plakası
    base_plate = create_box(
        doc, "VB_Base_Plate",
        width=500, height=30, depth=400,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(100, 100, -50)
    )
    
    # V ekseni lineer ray
    v_rail = create_box(
        doc, "V_Rail",
        width=40, height=30, depth=3000,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(150, 50, -35)
    )
    
    # V ekseni kızak
    v_carriage = create_box(
        doc, "V_Carriage",
        width=300, height=100, depth=200,
        color=(0.6, 0.3, 0.3),
        position=App.Vector(
            base_plate.Placement.Base.x + 100,
            base_plate.Placement.Base.y,
            base_plate.Placement.Base.z
        )
    )
    
    # V ekseni motoru (Delta ECMA-E11315)
    motor_v = create_cylinder(
        doc, "Motor_V",
        radius=55, height=150,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(
            v_carriage.Placement.Base.x - 50,
            v_carriage.Placement.Base.y - 50,
            v_carriage.Placement.Base.z - 50
        )
    )
    
    # Alt kesici kafası (yukarı doğru hareket eder)
    lower_cutter_head = create_box(
        doc, "Lower_Cutter_Head",
        width=100, height=200, depth=80,
        color=(1.0, 0.6, 0.2),
        position=App.Vector(
            v_carriage.Placement.Base.x + 100,
            v_carriage.Placement.Base.y + 50,
            v_carriage.Placement.Base.z + 50
        )
    )
    
    # Alt kesici tekeri
    lower_wheel = create_cylinder(
        doc, "Lower_Cutting_Wheel",
        radius=20, height=15,
        color=(0.8, 0.8, 0.8),
        position=App.Vector(
            lower_cutter_head.Placement.Base.x,
            lower_cutter_head.Placement.Base.y + 100,
            lower_cutter_head.Placement.Base.z + 100
        )
    )
    
    # Pnömatik silindir (kesici kaldırma)
    pneu_cylinder = create_cylinder(
        doc, "VB_Pneu_Cylinder",
        radius=25, height=150,
        color=(0.3, 0.3, 0.4),
        position=App.Vector(
            lower_cutter_head.Placement.Base.x,
            lower_cutter_head.Placement.Base.y,
            lower_cutter_head.Placement.Base.z - 50
        )
    )
    
    return {
        'base': base_plate,
        'rail': v_rail,
        'carriage': v_carriage,
        'motor': motor_v,
        'head': lower_cutter_head,
        'wheel': lower_wheel,
        'cylinder': pneu_cylinder
    }


# =============================================================================
# VB-MODUL: ISITICI ÇUBUK (HEIZSTAB)
# =============================================================================

def create_vb_heater(doc, frame):
    """
    VB-Modul ısıtıcı çubuk (Heizstab)
    Lamine cam PVB filmini yumuşatır
    """
    print("  - VB-Modul ısıtıcı oluşturuluyor...")
    
    # Isıtıcı taban
    heater_base = create_box(
        doc, "Heater_Base",
        width=400, height=40, depth=300,
        color=(0.6, 0.5, 0.4),
        position=App.Vector(200, 200, -40)
    )
    
    # Isıtıcı çubuk (silindirik)
    heater_rod = create_cylinder(
        doc, "Heater_Rod",
        radius=15, height=2800,
        color=(0.9, 0.7, 0.5),
        position=App.Vector(200, 1600, -20),
        rotation=App.Rotation(90, 0, 0)
    )
    
    # Isıtıcı muhafaza
    heater_housing = create_box(
        doc, "Heater_Housing",
        width=100, height=60, depth=2900,
        color=(0.7, 0.6, 0.5),
        position=App.Vector(200, 1600, -10)
    )
    
    # Termokupl sensörü
    thermocouple = create_cylinder(
        doc, "Heater_Thermocouple",
        radius=5, height=30,
        color=(0.8, 0.8, 0.2),
        position=App.Vector(250, 300, 10)
    )
    
    # Pnömatik silindir (aşağı/yukarı hareket)
    heater_cylinder = create_cylinder(
        doc, "Heater_Pneu_Cylinder",
        radius=30, height=100,
        color=(0.3, 0.3, 0.4),
        position=App.Vector(200, 100, -60)
    )
    
    return {
        'base': heater_base,
        'rod': heater_rod,
        'housing': heater_housing,
        'sensor': thermocouple,
        'cylinder': heater_cylinder
    }


# =============================================================================
# HAT MODULLERI: YUKLEME VE BOSALTMA
# =============================================================================

def create_loading_station(doc, params):
    """
    ATH/BSK yukleme istasyonunu yarim-detayli olarak temsil et
    """
    print("  - ATH/BSK yukleme istasyonu olusturuluyor...")

    x_pos = -(params.LOADER_LENGTH + params.INTERFACE_GAP)

    base = create_box(
        doc, "Loading_Station_Base",
        width=params.LOADER_LENGTH, height=120, depth=params.LOADER_WIDTH,
        color=(0.25, 0.45, 0.75),
        position=App.Vector(x_pos, -200, -120)
    )

    deck = create_box(
        doc, "Loading_Station_Deck",
        width=params.LOADER_LENGTH - 150, height=40, depth=params.LOADER_WIDTH - 250,
        color=(0.65, 0.7, 0.8),
        position=App.Vector(x_pos + 75, -75, 760)
    )

    tower_left = create_box(
        doc, "Loading_Station_Tower_Left",
        width=120, height=params.LOADER_HEIGHT, depth=160,
        color=(0.2, 0.3, 0.5),
        position=App.Vector(x_pos + 120, 0, 0)
    )

    tower_right = create_box(
        doc, "Loading_Station_Tower_Right",
        width=120, height=params.LOADER_HEIGHT, depth=160,
        color=(0.2, 0.3, 0.5),
        position=App.Vector(x_pos + 120, params.LOADER_WIDTH - 160, 0)
    )

    back_tower_left = create_box(
        doc, "Loading_Station_Back_Tower_Left",
        width=100, height=params.LOADER_HEIGHT - 80, depth=140,
        color=(0.22, 0.32, 0.52),
        position=App.Vector(x_pos + params.LOADER_LENGTH - 260, 80, 0)
    )

    back_tower_right = create_box(
        doc, "Loading_Station_Back_Tower_Right",
        width=100, height=params.LOADER_HEIGHT - 80, depth=140,
        color=(0.22, 0.32, 0.52),
        position=App.Vector(x_pos + params.LOADER_LENGTH - 260, params.LOADER_WIDTH - 220, 0)
    )

    upper_frame = create_box(
        doc, "Loading_Station_Upper_Frame",
        width=params.LOADER_LENGTH - 260, height=80, depth=120,
        color=(0.3, 0.38, 0.58),
        position=App.Vector(x_pos + 160, 150, params.LOADER_HEIGHT - 60)
    )

    side_beam = create_box(
        doc, "Loading_Station_Side_Beam",
        width=params.LOADER_LENGTH - 300, height=70, depth=100,
        color=(0.28, 0.36, 0.55),
        position=App.Vector(x_pos + 180, params.LOADER_WIDTH - 220, params.LOADER_HEIGHT - 40)
    )

    brace_left = create_box(
        doc, "Loading_Station_Brace_Left",
        width=700, height=40, depth=60,
        color=(0.5, 0.55, 0.62),
        position=App.Vector(x_pos + 220, 170, 420)
    )

    brace_right = create_box(
        doc, "Loading_Station_Brace_Right",
        width=700, height=40, depth=60,
        color=(0.5, 0.55, 0.62),
        position=App.Vector(x_pos + 220, params.LOADER_WIDTH - 250, 420)
    )

    storage_ribs = []
    for idx in range(5):
        rib = create_box(
            doc, f"Loading_Station_Storage_Rib_{idx+1}",
            width=params.LOADER_LENGTH - 320, height=18, depth=45,
            color=(0.78, 0.82, 0.86),
            position=App.Vector(x_pos + 180, 250 + idx * 580, 825)
        )
        storage_ribs.append(rib)

    carriage = create_box(
        doc, "Loading_Station_Carriage",
        width=180, height=120, depth=500,
        color=(0.42, 0.42, 0.46),
        position=App.Vector(x_pos + 560, 170, 620)
    )

    suction_beam = create_box(
        doc, "Loading_Suction_Beam",
        width=80, height=80, depth=params.LOADER_WIDTH - 240,
        color=(0.4, 0.4, 0.45),
        position=App.Vector(x_pos + 640, 120, 680)
    )

    vacuum_manifold = create_box(
        doc, "Loading_Vacuum_Manifold",
        width=110, height=60, depth=params.LOADER_WIDTH - 320,
        color=(0.28, 0.28, 0.3),
        position=App.Vector(x_pos + 720, 160, 760)
    )

    suction_pads = []
    for row in range(6):
        for col in range(2):
            pad = create_cylinder(
                doc, f"Loading_Suction_Pad_{row+1}_{col+1}",
                radius=42, height=24,
                color=(0.12, 0.12, 0.12),
                position=App.Vector(x_pos + 820 + col * 220, 360 + row * 470, 760),
                rotation=App.Rotation(App.Vector(1, 0, 0), 90)
            )
            suction_pads.append(pad)
    chain_column = create_box(
        doc, "Loading_Chain_Column",
        width=70, height=params.LOADER_HEIGHT - 100, depth=100,
        color=(0.16, 0.16, 0.18),
        position=App.Vector(x_pos + 300, 40, 60)
    )

    drive_motor = create_cylinder(
        doc, "Loading_Station_Drive_Motor",
        radius=55, height=180,
        color=(0.15, 0.15, 0.16),
        position=App.Vector(x_pos + 260, 20, 120)
    )

    guide_roller_top = create_cylinder(
        doc, "Loading_Guide_Roller_Top",
        radius=35, height=180,
        color=(0.65, 0.65, 0.67),
        position=App.Vector(x_pos + 300, 40, params.LOADER_HEIGHT - 40)
    )

    guide_roller_bottom = create_cylinder(
        doc, "Loading_Guide_Roller_Bottom",
        radius=35, height=180,
        color=(0.65, 0.65, 0.67),
        position=App.Vector(x_pos + 300, 40, 20)
    )

    note = create_text_note(
        doc,
        "Loading_Station_Label",
        "ATH-60/30D / BSK-60/30 RE-S Loading",
        App.Vector(x_pos + 100, 200, 1100)
    )

    return {
        'base': base,
        'deck': deck,
        'towers': [tower_left, tower_right, back_tower_left, back_tower_right],
        'upper_frame': [upper_frame, side_beam],
        'braces': [brace_left, brace_right],
        'storage_ribs': storage_ribs,
        'carriage': carriage,
        'beam': suction_beam,
        'manifold': vacuum_manifold,
        'pads': suction_pads,
        'chain_drive': [chain_column, drive_motor, guide_roller_top, guide_roller_bottom],
        'note': note
    }


def create_breaking_table_module(doc, params):
    """
    BTS-60/30 cikis / kirma masasini yarim-detayli temsil et
    """
    print("  - BTS kirma ve bosaltma masasi olusturuluyor...")

    x_pos = params.FRAME_LENGTH + params.INTERFACE_GAP

    base = create_box(
        doc, "BTS_Table_Base",
        width=params.BREAKOUT_LENGTH, height=120, depth=params.BREAKOUT_WIDTH,
        color=(0.75, 0.45, 0.25),
        position=App.Vector(x_pos, -200, -120)
    )

    deck = create_box(
        doc, "BTS_Table_Deck",
        width=params.BREAKOUT_LENGTH - 120, height=35, depth=params.BREAKOUT_WIDTH - 200,
        color=(0.8, 0.78, 0.72),
        position=App.Vector(x_pos + 60, -100, 760)
    )

    frame_left = create_box(
        doc, "BTS_Frame_Left",
        width=90, height=760, depth=120,
        color=(0.55, 0.34, 0.18),
        position=App.Vector(x_pos + 120, 20, -20)
    )

    frame_right = create_box(
        doc, "BTS_Frame_Right",
        width=90, height=760, depth=120,
        color=(0.55, 0.34, 0.18),
        position=App.Vector(x_pos + 120, params.BREAKOUT_WIDTH - 180, -20)
    )

    upper_link = create_box(
        doc, "BTS_Upper_Link",
        width=params.BREAKOUT_LENGTH - 300, height=65, depth=110,
        color=(0.62, 0.40, 0.22),
        position=App.Vector(x_pos + 180, 100, 700)
    )

    transfer_beam = create_box(
        doc, "BTS_Transfer_Beam",
        width=120, height=120, depth=params.BREAKOUT_WIDTH - 220,
        color=(0.55, 0.35, 0.2),
        position=App.Vector(x_pos + 500, -90, 700)
    )

    roller_bed = []
    for idx in range(8):
        roller = create_cylinder(
            doc, f"BTS_Roller_{idx+1}",
            radius=42, height=params.BREAKOUT_WIDTH - 300,
            color=(0.62, 0.62, 0.64),
            position=App.Vector(x_pos + 280 + idx * 260, 60, 770),
            rotation=App.Rotation(App.Vector(1, 0, 0), 90)
        )
        roller_bed.append(roller)

    lift_cylinders = []
    for idx, z_shift in enumerate([220, 1500]):
        cyl = create_cylinder(
            doc, f"BTS_Lift_Cylinder_{idx+1}",
            radius=38, height=180,
            color=(0.35, 0.35, 0.4),
            position=App.Vector(x_pos + 950, 80 + z_shift, 500)
        )
        lift_cylinders.append(cyl)

    breakout_bar = create_box(
        doc, "BTS_Breakout_Bar",
        width=80, height=70, depth=params.BREAKOUT_WIDTH - 260,
        color=(0.45, 0.25, 0.15),
        position=App.Vector(x_pos + 1600, -70, 780)
    )

    breakout_arm_left = create_box(
        doc, "BTS_Breakout_Arm_Left",
        width=260, height=40, depth=80,
        color=(0.68, 0.46, 0.24),
        position=App.Vector(x_pos + 1500, 180, 690)
    )

    breakout_arm_right = create_box(
        doc, "BTS_Breakout_Arm_Right",
        width=260, height=40, depth=80,
        color=(0.68, 0.46, 0.24),
        position=App.Vector(x_pos + 1500, params.BREAKOUT_WIDTH - 260, 690)
    )

    stop_fence = create_box(
        doc, "BTS_Stop_Fence",
        width=60, height=140, depth=params.BREAKOUT_WIDTH - 260,
        color=(0.82, 0.2, 0.15),
        position=App.Vector(x_pos + params.BREAKOUT_LENGTH - 240, -40, 820)
    )

    note = create_text_note(
        doc,
        "BTS_Table_Label",
        "BTS-60/30 Breaking / Unload",
        App.Vector(x_pos + 150, 200, 1100)
    )

    return {
        'base': base,
        'deck': deck,
        'frame': [frame_left, frame_right, upper_link],
        'beam': transfer_beam,
        'rollers': roller_bed,
        'lift_cylinders': lift_cylinders,
        'breakout_bar': breakout_bar,
        'arms': [breakout_arm_left, breakout_arm_right],
        'fence': stop_fence,
        'note': note
    }


# =============================================================================
# VB-MODUL: VAKUM VANTUZ SİSTEMİ
# =============================================================================

def create_vb_vacuum(doc, frame):
    """
    VB-Modul vakum vantuz sistemi
    Camı sabitler
    """
    print("  - VB-Modul vakum sistemi oluşturuluyor...")
    
    # Vakum taban plakası
    vacuum_base = create_box(
        doc, "Vacuum_Base",
        width=600, height=50, depth=500,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(50, 50, -30)
    )
    
    # Vantuz pedleri (4 adet)
    suction_cups = []
    cup_positions = [
        (100, 100), (100, 400),
        (500, 100), (500, 400)
    ]
    
    for i, (x, y) in enumerate(cup_positions):
        cup = create_cylinder(
            doc, f"Vacuum_Cup_{i+1}",
            radius=40, height=30,
            color=(0.2, 0.2, 0.2),
            position=App.Vector(x, y, -15)
        )
        suction_cups.append(cup)
    
    # Vakum kanalları
    vacuum_channel = create_box(
        doc, "Vacuum_Channel",
        width=500, height=20, depth=20,
        color=(0.3, 0.3, 0.3),
        position=App.Vector(100, 250, -20)
    )
    
    # Basınç sensörü
    pressure_sensor = create_box(
        doc, "Vacuum_Pressure_Sensor",
        width=40, height=40, depth=30,
        color=(0.4, 0.4, 0.6),
        position=App.Vector(550, 250, -20)
    )
    
    return {
        'base': vacuum_base,
        'cups': suction_cups,
        'channel': vacuum_channel,
        'sensor': pressure_sensor
    }


# =============================================================================
# VB-MODUL: KIRMA ÇITASI (BRECHLEISTE)
# =============================================================================

def create_vb_breaking_bar(doc, frame):
    """
    VB-Modul kırma çıtası (Brechleiste)
    Camı kırmak için kullanılır
    """
    print("  - VB-Modul kırma çıtası oluşturuluyor...")
    
    # Kırma çıtası taban
    breaking_base = create_box(
        doc, "Breaking_Bar_Base",
        width=300, height=40, depth=200,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(300, 300, -30)
    )
    
    # Kırma çıtası profili (uzun)
    breaking_profile = create_box(
        doc, "Breaking_Profile",
        width=50, height=30, depth=2800,
        color=(0.6, 0.6, 0.6),
        position=App.Vector(300, 1600, -15)
    )
    
    # Kaldırma mekanizması
    lifting_arm_left = create_box(
        doc, "Breaking_Arm_Left",
        width=100, height=20, depth=80,
        color=(0.7, 0.5, 0.3),
        position=App.Vector(300, 200, 0)
    )
    
    lifting_arm_right = create_box(
        doc, "Breaking_Arm_Right",
        width=100, height=20, depth=80,
        color=(0.7, 0.5, 0.3),
        position=App.Vector(300, 2900, 0)
    )
    
    # Pnömatik silindirler
    breaking_cylinder_left = create_cylinder(
        doc, "Breaking_Cylinder_Left",
        radius=25, height=100,
        color=(0.3, 0.3, 0.4),
        position=App.Vector(300, 150, -40)
    )
    
    breaking_cylinder_right = create_cylinder(
        doc, "Breaking_Cylinder_Right",
        radius=25, height=100,
        color=(0.3, 0.3, 0.4),
        position=App.Vector(300, 2950, -40)
    )
    
    return {
        'base': breaking_base,
        'profile': breaking_profile,
        'arms': [lifting_arm_left, lifting_arm_right],
        'cylinders': [breaking_cylinder_left, breaking_cylinder_right]
    }


# =============================================================================
# VB-MODUL: AYIRMA BIÇAĞI (TRENNKLINGE)
# =============================================================================

def create_vb_separating_blade(doc, frame):
    """
    VB-Modul ayırma bıçağı (Trennklinge)
    Çizilen camı ayırır
    """
    print("  - VB-Modul ayırma bıçağı oluşturuluyor...")
    
    # Ayırma bıçağı taban
    separating_base = create_box(
        doc, "Separating_Blade_Base",
        width=250, height=40, depth=150,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(400, 400, -30)
    )
    
    # Bıçak gövdesi
    blade_body = create_box(
        doc, "Separating_Blade",
        width=30, height=100, depth=2700,
        color=(0.8, 0.8, 0.8),
        position=App.Vector(400, 1600, 0)
    )
    
    # Bıçak ucu (keskin)
    blade_edge = create_box(
        doc, "Separating_Blade_Edge",
        width=10, height=50, depth=2700,
        color=(0.9, 0.9, 0.9),
        position=App.Vector(400, 1600, 25)
    )
    
    # Ayarlama mekanizması (hassas pozisyonlama)
    adjustment_screw = create_cylinder(
        doc, "Separating_Adjustment",
        radius=10, height=50,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(400, 350, -20)
    )
    
    # Pnömatik silindir
    separating_cylinder = create_cylinder(
        doc, "Separating_Cylinder",
        radius=20, height=80,
        color=(0.3, 0.3, 0.4),
        position=App.Vector(400, 300, -40)
    )
    
    return {
        'base': separating_base,
        'body': blade_body,
        'edge': blade_edge,
        'adjustment': adjustment_screw,
        'cylinder': separating_cylinder
    }


# =============================================================================
# BASINÇ ROLLESİ (ANDRÜCKROLLE)
# =============================================================================

def create_vb_pressure_roller(doc, frame):
    """
    VB-Modul basınç rollesi (Andrückrolle)
    Kesim sırasında camı sabitler
    """
    print("  - VB-Modul basınç rollesi oluşturuluyor...")
    
    # Rolle taban
    roller_base = create_box(
        doc, "Pressure_Roller_Base",
        width=200, height=40, depth=150,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(500, 500, -30)
    )
    
    # Rolle kolu
    roller_arm = create_box(
        doc, "Pressure_Roller_Arm",
        width=50, height=100, depth=50,
        color=(0.6, 0.6, 0.6),
        position=App.Vector(500, 550, 0)
    )
    
    # Basınç rollesi (silindirik)
    roller = create_cylinder(
        doc, "Pressure_Roller",
        radius=30, height=2700,
        color=(0.4, 0.4, 0.4),
        position=App.Vector(500, 1600, 50),
        rotation=App.Rotation(90, 0, 0)
    )
    
    # Pnömatik silindir
    roller_cylinder = create_cylinder(
        doc, "Pressure_Roller_Cylinder",
        radius=25, height=80,
        color=(0.3, 0.3, 0.4),
        position=App.Vector(500, 500, -40)
    )
    
    return {
        'base': roller_base,
        'arm': roller_arm,
        'roller': roller,
        'cylinder': roller_cylinder
    }


# =============================================================================
# KABLO TANKLARI VE HORTUMLAR
# =============================================================================

def create_cable_tracks(doc, params):
    """
    Kablo tankları ve hortumlar
    """
    print("  - Kablo tankları oluşturuluyor...")
    
    # X ekseni kablo tankı
    cable_x = create_box(
        doc, "Cable_Track_X",
        width=50, height=30, depth=1000,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(0, 50, 50)
    )
    
    # Y ekseni kablo tankı
    cable_y = create_box(
        doc, "Cable_Track_Y",
        width=40, height=25, depth=500,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(1600, 100, 250)
    )
    
    # Z ekseni kablo tankı
    cable_z = create_box(
        doc, "Cable_Track_Z",
        width=30, height=20, depth=400,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(1750, 200, 50)
    )
    
    # VB-Modul kablo tankı
    cable_v = create_box(
        doc, "Cable_Track_V",
        width=40, height=25, depth=500,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(200, 100, -50)
    )
    
    # Pnömatik hortumlar
    pneu_hose_1 = create_cylinder(
        doc, "Pneu_Hose_1",
        radius=8, height=1000,
        color=(0.0, 0.5, 1.0),
        position=App.Vector(300, 200, -30),
        rotation=App.Rotation(90, 0, 0)
    )
    
    return {
        'x': cable_x,
        'y': cable_y,
        'z': cable_z,
        'v': cable_v,
        'pneu_hose': pneu_hose_1
    }


# =============================================================================
# DEĞİŞKEN TABLOSU (ASSEMBLY4)
# =============================================================================

def create_variables_spreadsheet(doc, params):
    """
    Assembly4 değişken tablosu
    """
    print("  - Değişken tablosu oluşturuluyor...")
    ss = doc.addObject('Spreadsheet::Sheet', 'Variables')
    
    # Eksen pozisyonları
    ss.set('A1', f'{params.X_HOME} mm')  # X_Position
    ss.set('B1', f'{params.Y_HOME} mm')  # Y_Position
    ss.set('C1', f'{params.Z_HOME} mm')  # Z_Position
    ss.set('D1', f'{params.V_HOME} mm')  # V_Position (alt kesici)
    
    # Eksen limitleri
    ss.set('E1', f'{params.X_MAX} mm')   # X_Max
    ss.set('F1', f'{params.Y_MAX} mm')   # Y_Max
    ss.set('G1', f'{params.Z_MAX} mm')   # Z_Max
    ss.set('H1', f'{params.V_MAX} mm')   # V_Max
    
    # Kesim parametreleri
    ss.set('I1', f'{params.CAM_KALINLIGI} mm')  # Cam_Kalinligi
    ss.set('J1', f'{params.LAMINE_KALINLIK} mm')  # Lamine_Kalinlik
    ss.set('K1', f'{params.KESIM_BASINCI} MPa')  # Kesim_Basinci
    
    # VB-Modul parametreleri
    ss.set('L1', f'{params.ISITMA_SICAKLIK} deg')  # Isitma_Sicaklik
    ss.set('M1', f'{params.ISITMA_SURES} s')  # Isitma_Suresi
    ss.set('N1', f'{params.VAKUM_BASINC} bar')  # Vakum_Basinc
    ss.set('O1', f'{params.AYIRMA_BASINC} bar')  # Ayirma_Basinc
    ss.set('P1', f'{params.KIRMA_BASINC} bar')  # Kirma_Basinci
    
    ss.Label = 'Variables'
    
    return ss


LAMINE_INPUT_DESCRIPTIONS = {
    "START_CMD": "Lamine çevrim başlatma komutu",
    "GLASS_DETECT": "Cam tabla üzerinde algılandı",
    "VACUUM_OK": "Vakum seviyesi yeterli",
    "AIR_PRESSURE_OK": "Pnömatik hava basıncı uygun",
    "HEATER_DOWN_OK": "Isıtıcı aşağı pozisyon sensörü",
    "HEATER_UP_OK": "Isıtıcı yukarı pozisyon sensörü",
    "TEMP_READY": "Isıtıcı sıcaklığı hedefe ulaştı",
    "UPPER_HEAD_READY": "Üst kafa güvenli kesim pozisyonunda",
    "UPPER_CUT_OK": "Üst kesim tamamlandı",
    "LOWER_HEAD_READY": "Alt kesici temas pozisyonunda",
    "LOWER_CUT_OK": "Alt kesim tamamlandı",
    "SEPARATION_OK": "Ayırma bıçağı işlemi tamam",
    "BREAK_OK": "Kırma işlemi tamam",
    "UNLOAD_READY": "Parça boşaltmaya hazır",
    "ESTOP_OK": "Acil stop devresi sağlıklı",
    "DOOR_CLOSED": "Güvenlik kapısı kapalı",
}


LAMINE_OUTPUT_DESCRIPTIONS = {
    "SERVO_ENABLE_X": "X servo aktif",
    "SERVO_ENABLE_Y": "Y servo aktif",
    "SERVO_ENABLE_Z": "Z servo aktif",
    "SERVO_ENABLE_V": "V servo aktif",
    "VACUUM_PUMP": "Vakum pompası aktif",
    "HEATER_DOWN": "Isıtıcı aşağı komutu",
    "HEATER_ENABLE": "Isıtıcı enerji verildi",
    "UPPER_CUT_ENABLE": "Üst kesim aktif",
    "LOWER_CUT_ENABLE": "Alt kesim aktif",
    "SEPARATING_BLADE": "Ayırma bıçağı aktif",
    "BREAKING_BAR": "Kırma çıtası aktif",
    "PRESSURE_ROLLER": "Basınç rollesi aktif",
    "CYCLE_COMPLETE": "Çevrim başarıyla tamamlandı",
    "ALARM": "Çevrim alarmda",
}


def create_lamine_io_spreadsheet(doc):
    """
    Lamine kesim için giriş/çıkış durum tablosu oluştur.
    """
    print("  - Lamine I/O tablosu oluşturuluyor...")
    ss = doc.addObject('Spreadsheet::Sheet', 'Lamine_IO')
    ss.Label = 'Lamine_IO'

    ss.set('A1', 'Tip')
    ss.set('B1', 'Sinyal')
    ss.set('C1', 'Durum')
    ss.set('D1', 'Aciklama')

    row = 2
    for signal, description in LAMINE_INPUT_DESCRIPTIONS.items():
        ss.set(f'A{row}', 'DI')
        ss.set(f'B{row}', signal)
        ss.set(f'C{row}', '0')
        ss.set(f'D{row}', description)
        row += 1

    for signal, description in LAMINE_OUTPUT_DESCRIPTIONS.items():
        ss.set(f'A{row}', 'DO')
        ss.set(f'B{row}', signal)
        ss.set(f'C{row}', '0')
        ss.set(f'D{row}', description)
        row += 1

    return ss


def create_lamine_phase_spreadsheet(doc):
    """
    Lamine proses fazlari ve gecis kurallarini dokumante eden tablo.
    """
    print("  - Lamine faz tablosu oluşturuluyor...")
    ss = doc.addObject('Spreadsheet::Sheet', 'Lamine_Phases')
    ss.Label = 'Lamine_Phases'

    headers = ['Faz', 'Giris Sarti', 'Cikislar', 'Sonraki Faz']
    for idx, header in enumerate(headers):
        col = chr(ord('A') + idx)
        ss.set(f'{col}1', header)

    return ss


# =============================================================================
# KİNEMATİK BAĞLANTILAR
# =============================================================================

def setup_kinematics(doc, params):
    """
    Eksenler arası kinematik bağlantıları kur
    """
    print("  - Kinematik bağlantılar kuruluyor...")
    
    # Makine eksenleri ile FreeCAD eksenleri birebir degil:
    # X (gantry) -> FreeCAD Z, Y (araba) -> FreeCAD X, Z/V (dikey) -> FreeCAD Y
    doc.Portal_Bridge.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Portal_Left_Support.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Portal_Right_Support.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Motor_X_Left.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Motor_X_Right.setExpression('Placement.Base.z', 'Variables.A1')
    doc.X_Rail_Left.setExpression('Placement.Base.z', 'Variables.A1')
    doc.X_Rail_Right.setExpression('Placement.Base.z', 'Variables.A1')
    
    # Y ekseni arabasi portal ile birlikte X hareketini takip eder,
    # kendi stroku ise FreeCAD X eksenindedir
    doc.Y_Carriage.setExpression('Placement.Base.x', '150 mm + Variables.B1')
    doc.Y_Carriage.setExpression('Placement.Base.z', '150 mm + Variables.A1')
    doc.Y_Rail.setExpression('Placement.Base.z', '150 mm + Variables.A1')
    doc.Motor_Y.setExpression('Placement.Base.x', 'Y_Carriage.Placement.Base.x - 50 mm')
    doc.Motor_Y.setExpression('Placement.Base.y', 'Y_Carriage.Placement.Base.y - 50 mm')
    doc.Motor_Y.setExpression('Placement.Base.z', 'Y_Carriage.Placement.Base.z + 100 mm')
    
    # Z ekseni ust kafa: X/Z duzleminde Y arabasini takip eder, dikey strok FreeCAD Y'dedir
    doc.Z_Column.setExpression('Placement.Base.x', 'Y_Carriage.Placement.Base.x + 160 mm')
    doc.Z_Column.setExpression('Placement.Base.y', 'Y_Carriage.Placement.Base.y + 100 mm')
    doc.Z_Column.setExpression('Placement.Base.z', 'Y_Carriage.Placement.Base.z')
    doc.Z_Carriage.setExpression('Placement.Base.x', 'Z_Column.Placement.Base.x - 10 mm')
    doc.Z_Carriage.setExpression('Placement.Base.y', 'Z_Column.Placement.Base.y + Variables.C1')
    doc.Z_Carriage.setExpression('Placement.Base.z', 'Z_Column.Placement.Base.z')
    doc.Cutting_Head.setExpression('Placement.Base.x', 'Z_Carriage.Placement.Base.x')
    doc.Cutting_Head.setExpression('Placement.Base.y', 'Z_Carriage.Placement.Base.y - 100 mm')
    doc.Cutting_Head.setExpression('Placement.Base.z', 'Z_Carriage.Placement.Base.z')
    doc.Cutting_Wheel.setExpression('Placement.Base.x', 'Cutting_Head.Placement.Base.x')
    doc.Cutting_Wheel.setExpression('Placement.Base.y', 'Cutting_Head.Placement.Base.y - 80 mm')
    doc.Cutting_Wheel.setExpression('Placement.Base.z', 'Cutting_Head.Placement.Base.z + 40 mm')
    doc.Motor_Z.setExpression('Placement.Base.x', 'Z_Column.Placement.Base.x')
    doc.Motor_Z.setExpression('Placement.Base.y', 'Z_Column.Placement.Base.y + 350 mm')
    doc.Motor_Z.setExpression('Placement.Base.z', 'Z_Column.Placement.Base.z')
    doc.C_Axis_Head.setExpression('Placement.Base.x', 'Cutting_Head.Placement.Base.x + 50 mm')
    doc.C_Axis_Head.setExpression('Placement.Base.y', 'Cutting_Head.Placement.Base.y - 50 mm')
    doc.C_Axis_Head.setExpression('Placement.Base.z', 'Cutting_Head.Placement.Base.z + 40 mm')
    
    # V ekseni alt kesici: Y arabasi ile ayni yatay stroku izler, V stroku FreeCAD Y'dedir
    doc.V_Carriage.setExpression('Placement.Base.x', '200 mm + Variables.B1')
    doc.V_Carriage.setExpression('Placement.Base.y', '100 mm + Variables.D1')
    doc.Motor_V.setExpression('Placement.Base.x', 'V_Carriage.Placement.Base.x - 50 mm')
    doc.Motor_V.setExpression('Placement.Base.y', 'V_Carriage.Placement.Base.y - 50 mm')
    doc.Lower_Cutter_Head.setExpression('Placement.Base.x', 'V_Carriage.Placement.Base.x + 100 mm')
    doc.Lower_Cutter_Head.setExpression('Placement.Base.y', 'V_Carriage.Placement.Base.y + 50 mm')
    doc.Lower_Cutter_Head.setExpression('Placement.Base.z', 'V_Carriage.Placement.Base.z + 50 mm')
    doc.Lower_Cutting_Wheel.setExpression('Placement.Base.x', 'Lower_Cutter_Head.Placement.Base.x')
    doc.Lower_Cutting_Wheel.setExpression('Placement.Base.y', 'Lower_Cutter_Head.Placement.Base.y + 100 mm')
    doc.Lower_Cutting_Wheel.setExpression('Placement.Base.z', 'Lower_Cutter_Head.Placement.Base.z + 100 mm')
    
    # VB-Modul bileşenleri (sabit pozisyonlar, işlem sırasında hareket eder)
    # Isıtıcı - Y ekseni stroku ile aynı hatta ilerler
    doc.Heater_Rod.setExpression('Placement.Base.x', '200 mm + Variables.B1')
    doc.Heater_Housing.setExpression('Placement.Base.x', '200 mm + Variables.B1')
    
    # Kırma çıtası - Y stroku ile aynı hizayi izler
    doc.Breaking_Profile.setExpression('Placement.Base.x', '300 mm + Variables.B1')
    
    # Ayırma bıçağı - Y stroku ile aynı hizayi izler
    doc.Separating_Blade.setExpression('Placement.Base.x', '400 mm + Variables.B1')
    doc.Separating_Blade_Edge.setExpression('Placement.Base.x', '400 mm + Variables.B1')
    
    # Basınç rollesi - Y stroku ile aynı hizayi izler
    doc.Pressure_Roller.setExpression('Placement.Base.x', '500 mm + Variables.B1')
    
    # Kablo tankları
    doc.Cable_Track_X.setExpression('Placement.Base.z', 'Variables.A1 / 6')
    doc.Cable_Track_Y.setExpression('Placement.Base.x', 'Y_Carriage.Placement.Base.x')
    doc.Cable_Track_Y.setExpression('Placement.Base.z', 'Y_Carriage.Placement.Base.z + 100 mm')
    doc.Cable_Track_V.setExpression('Placement.Base.x', 'V_Carriage.Placement.Base.x')
    doc.Cable_Track_V.setExpression('Placement.Base.y', 'V_Carriage.Placement.Base.y + 50 mm')


# =============================================================================
# YARDIMCI KONTROL FONKSIYONLARI
# =============================================================================

def _clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def set_axis_positions(doc, x=None, y=None, z=None, v=None):
    """
    Spreadsheet uzerinden eksen pozisyonlarini guncelle.
    Degerler makine koordinatlarindadir ve otomatik olarak limitlenir.
    """
    ss = doc.getObject("Variables")
    if ss is None:
        raise RuntimeError("Variables spreadsheet bulunamadi")

    if x is not None:
        ss.set("A1", f"{_clamp(float(x), 0.0, MachineParameters.X_MAX)} mm")
    if y is not None:
        ss.set("B1", f"{_clamp(float(y), 0.0, MachineParameters.Y_MAX)} mm")
    if z is not None:
        ss.set("C1", f"{_clamp(float(z), 0.0, MachineParameters.Z_MAX)} mm")
    if v is not None:
        ss.set("D1", f"{_clamp(float(v), 0.0, MachineParameters.V_MAX)} mm")

    doc.recompute()
    return ss


def _sheet_find_row(sheet, signal_name):
    row = 2
    while True:
        cell_value = sheet.get(f'B{row}')
        if not cell_value:
            return None
        if cell_value == signal_name:
            return row
        row += 1


def update_lamine_io_sheet(doc, inputs, outputs):
    sheet = doc.getObject("Lamine_IO")
    if sheet is None:
        return

    for signal_name, signal_value in {**inputs, **outputs}.items():
        row = _sheet_find_row(sheet, signal_name)
        if row is not None:
            sheet.set(f'C{row}', '1' if signal_value else '0')


def build_lamine_phase_sequence(params):
    """
    Faz bazli proses akisi, I/O ve eksen hedeflerini tanimlar.
    """
    return [
        {
            "phase": "Bekleme",
            "target": {"x": 0, "y": 0, "z": 300, "v": 0},
            "inputs": {"START_CMD": True, "ESTOP_OK": True, "DOOR_CLOSED": True, "AIR_PRESSURE_OK": True},
            "outputs": {"SERVO_ENABLE_X": True, "SERVO_ENABLE_Y": True, "SERVO_ENABLE_Z": True, "SERVO_ENABLE_V": True},
            "guards": ["START_CMD", "ESTOP_OK", "DOOR_CLOSED", "AIR_PRESSURE_OK"],
            "next_phase": "Yukleme",
        },
        {
            "phase": "Yukleme",
            "target": {"x": 500, "y": 500, "z": 300, "v": 0},
            "inputs": {"GLASS_DETECT": True, "VACUUM_OK": True, "UNLOAD_READY": False},
            "outputs": {"VACUUM_PUMP": True, "PRESSURE_ROLLER": True},
            "guards": ["GLASS_DETECT", "VACUUM_OK"],
            "next_phase": "Isitici Inis",
        },
        {
            "phase": "Isitici Inis",
            "target": {"x": 500, "y": 500, "z": 300, "v": 0},
            "inputs": {"HEATER_DOWN_OK": True, "TEMP_READY": False},
            "outputs": {"VACUUM_PUMP": True, "HEATER_DOWN": True},
            "guards": ["HEATER_DOWN_OK"],
            "next_phase": "Isitma",
        },
        {
            "phase": "Isitma",
            "target": {"x": 500, "y": 500, "z": 300, "v": 0},
            "inputs": {"HEATER_DOWN_OK": True, "TEMP_READY": True},
            "outputs": {"VACUUM_PUMP": True, "HEATER_DOWN": True, "HEATER_ENABLE": True},
            "guards": ["HEATER_DOWN_OK", "TEMP_READY"],
            "next_phase": "Isitici Kalkis",
        },
        {
            "phase": "Isitici Kalkis",
            "target": {"x": 500, "y": 500, "z": 300, "v": 0},
            "inputs": {"HEATER_UP_OK": True},
            "outputs": {"VACUUM_PUMP": True},
            "guards": ["HEATER_UP_OK"],
            "next_phase": "Ust Kesim Hazirlik",
        },
        {
            "phase": "Ust Kesim Hazirlik",
            "target": {"x": 500, "y": 500, "z": 284, "v": 0},
            "inputs": {"UPPER_HEAD_READY": True},
            "outputs": {"VACUUM_PUMP": True, "UPPER_CUT_ENABLE": True},
            "guards": ["UPPER_HEAD_READY"],
            "next_phase": "Ust Kesim",
        },
        {
            "phase": "Ust Kesim",
            "target": {"x": 2000, "y": 1400, "z": 284, "v": 0},
            "inputs": {"UPPER_CUT_OK": True},
            "outputs": {"VACUUM_PUMP": True, "UPPER_CUT_ENABLE": True},
            "guards": ["UPPER_CUT_OK"],
            "next_phase": "Alt Kesici Hazirlik",
        },
        {
            "phase": "Alt Kesici Hazirlik",
            "target": {"x": 2000, "y": 1400, "z": 284, "v": 100},
            "inputs": {"LOWER_HEAD_READY": True},
            "outputs": {"VACUUM_PUMP": True, "UPPER_CUT_ENABLE": True, "LOWER_CUT_ENABLE": True},
            "guards": ["LOWER_HEAD_READY"],
            "next_phase": "Senkronize Kesim",
        },
        {
            "phase": "Senkronize Kesim",
            "target": {"x": 3500, "y": 2300, "z": 284, "v": 250},
            "inputs": {"UPPER_CUT_OK": True, "LOWER_CUT_OK": True},
            "outputs": {"VACUUM_PUMP": True, "UPPER_CUT_ENABLE": True, "LOWER_CUT_ENABLE": True, "PRESSURE_ROLLER": True},
            "guards": ["UPPER_CUT_OK", "LOWER_CUT_OK"],
            "next_phase": "Kafalar Yukari",
        },
        {
            "phase": "Kafalar Yukari",
            "target": {"x": 3500, "y": 2300, "z": 300, "v": 0},
            "inputs": {"HEATER_UP_OK": True, "UPPER_HEAD_READY": True},
            "outputs": {"VACUUM_PUMP": True},
            "guards": ["UPPER_HEAD_READY"],
            "next_phase": "Ayirma",
        },
        {
            "phase": "Ayirma",
            "target": {"x": 3500, "y": 2300, "z": 300, "v": 0},
            "inputs": {"SEPARATION_OK": True},
            "outputs": {"VACUUM_PUMP": True, "SEPARATING_BLADE": True},
            "guards": ["SEPARATION_OK"],
            "next_phase": "Kirma",
        },
        {
            "phase": "Kirma",
            "target": {"x": 3500, "y": 2300, "z": 300, "v": 0},
            "inputs": {"BREAK_OK": True},
            "outputs": {"VACUUM_PUMP": True, "BREAKING_BAR": True, "PRESSURE_ROLLER": True},
            "guards": ["BREAK_OK"],
            "next_phase": "Bosaltma",
        },
        {
            "phase": "Bosaltma",
            "target": {"x": 500, "y": 500, "z": 300, "v": 0},
            "inputs": {"UNLOAD_READY": True},
            "outputs": {"CYCLE_COMPLETE": True},
            "guards": ["UNLOAD_READY"],
            "next_phase": "Tamamlandi",
        },
    ]


def populate_lamine_phase_sheet(doc, phase_sequence):
    sheet = doc.getObject("Lamine_Phases")
    if sheet is None:
        return

    for row, phase in enumerate(phase_sequence, start=2):
        sheet.set(f'A{row}', phase["phase"])
        sheet.set(f'B{row}', ", ".join(phase["guards"]))
        sheet.set(f'C{row}', ", ".join(sorted(phase["outputs"].keys())))
        sheet.set(f'D{row}', phase["next_phase"])


def _interpolate_phase_targets(start_target, end_target, progress_ratio):
    return {
        axis: start_target[axis] + (end_target[axis] - start_target[axis]) * progress_ratio
        for axis in ("x", "y", "z", "v")
    }


def _merge_io_states(default_inputs, default_outputs, phase_inputs, phase_outputs):
    inputs = dict(default_inputs)
    outputs = dict(default_outputs)
    inputs.update(phase_inputs)
    outputs.update(phase_outputs)
    return inputs, outputs


def _resolve_project_root():
    return "/Users/oktaycit/Projeler/CNCRevizyon"


def load_nc300_simulator_class():
    """
    Firmware/RaspberryPi/src altindaki NC300 simulatörünü yukler.
    """
    project_root = _resolve_project_root()
    simulator_dir = os.path.join(project_root, "Firmware", "RaspberryPi", "src")
    if simulator_dir not in sys.path:
        sys.path.insert(0, simulator_dir)

    from nc300_simulator import NC300Simulator  # type: ignore

    return NC300Simulator


def apply_nc300_snapshot_to_freecad(doc, snapshot):
    """
    NC300 snapshot bilgisini FreeCAD eksenlerine ve I/O sheet'ine uygular.
    """
    positions = snapshot.get("positions_mm", {})
    set_axis_positions(
        doc,
        x=positions.get("X", 0.0),
        y=positions.get("Y", 0.0),
        z=positions.get("Z", MachineParameters.Z_HOME),
        v=positions.get("V", 0.0),
    )

    update_lamine_io_sheet(doc, snapshot.get("di", {}), snapshot.get("do", {}))


def create_nc300_bridge(doc=None):
    """
    FreeCAD belgesi ile NC300Simulator arasinda canli bag kurar.
    """
    if doc is None:
        doc = App.ActiveDocument
    if doc is None:
        raise RuntimeError("Aktif FreeCAD dokumani bulunamadi")

    NC300Simulator = load_nc300_simulator_class()
    simulator = NC300Simulator()
    simulator.do["SERVO_ENABLE_X"] = True
    simulator.do["SERVO_ENABLE_Y"] = True
    simulator.do["SERVO_ENABLE_Z"] = True
    simulator.do["SERVO_ENABLE_V"] = True

    def _bridge_callback(_positions):
        apply_nc300_snapshot_to_freecad(doc, simulator.get_snapshot())

    simulator.freecad_callback = _bridge_callback
    apply_nc300_snapshot_to_freecad(doc, simulator.get_snapshot())
    return simulator


def _work_z_to_machine_z(z_value):
    """
    NC koordinatindaki Z degerini modelin guvenli/kesim yuksekligine map eder.

    Cikarim:
    - NC Z0 -> model guvenli yukseklik (300 mm)
    - NC Z-5 -> model kesim yuksekligi (284 mm)
    """
    z_value = float(z_value)
    if z_value <= 0.0:
        mapped = MachineParameters.Z_HOME + (z_value / 5.0) * 16.0
        return _clamp(mapped, 284.0, MachineParameters.Z_HOME)
    return MachineParameters.Z_HOME


def _nc_work_to_machine_position(work_position):
    return {
        "X": _clamp(float(work_position.get("X", 0.0)), 0.0, MachineParameters.X_MAX),
        "Y": _clamp(float(work_position.get("Y", 0.0)), 0.0, MachineParameters.Y_MAX),
        "Z": _work_z_to_machine_z(work_position.get("Z", 0.0)),
        "V": 0.0,
    }


def _build_nc_output_state(spindle_on=False, vacuum_on=False, cycle_complete=False):
    outputs = {signal: False for signal in LAMINE_OUTPUT_DESCRIPTIONS}
    outputs["UPPER_CUT_ENABLE"] = bool(spindle_on)
    outputs["PRESSURE_ROLLER"] = bool(spindle_on)
    outputs["VACUUM_PUMP"] = bool(vacuum_on)
    outputs["CYCLE_COMPLETE"] = bool(cycle_complete)
    return outputs


def _close_polyline_points(points):
    """Ilk ve son nokta farkliysa konturu kapat."""
    if not points:
        return []
    normalized = [(float(x), float(y)) for x, y in points]
    if len(normalized) > 1 and normalized[0] != normalized[-1]:
        normalized.append(normalized[0])
    return normalized


def _normalize_points_to_origin(points):
    """Noktalari sol-alt koseden baslayacak sekilde normalize et."""
    if not points:
        return []
    xs = [float(point[0]) for point in points]
    ys = [float(point[1]) for point in points]
    min_x = min(xs)
    min_y = min(ys)
    return [(float(x) - min_x, float(y) - min_y) for x, y in points]


def _scale_points_to_dimensions(points, target_width, target_height):
    """Konturu hedef genislik/yukseklige sigdir."""
    if not points:
        return []
    points = _normalize_points_to_origin(points)
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    width = max(xs) - min(xs)
    height = max(ys) - min(ys)
    scale_x = float(target_width) / width if width > 0.0001 else 1.0
    scale_y = float(target_height) / height if height > 0.0001 else 1.0
    return [(round(x * scale_x, 3), round(y * scale_y, 3)) for x, y in points]


def _coerce_points_from_object(value):
    """List/tuple/dict icinden nokta listesi cikar."""
    if isinstance(value, dict):
        if "points" in value:
            return _coerce_points_from_object(value["points"])
        if "vertices" in value:
            return _coerce_points_from_object(value["vertices"])
        if "x" in value and "y" in value:
            return [(float(value["x"]), float(value["y"]))]
        return []
    if isinstance(value, (list, tuple)):
        if value and all(isinstance(item, (int, float)) for item in value[:2]) and len(value) >= 2:
            return [(float(value[0]), float(value[1]))]
        points = []
        for item in value:
            points.extend(_coerce_points_from_object(item))
        return points
    return []


def parse_shape_base_string(shape_base_string):
    """
    Herofis ShapeBaseString benzeri veri formatlarini nokta listesine cevir.

    Desteklenen yaklasimlar:
    - JSON / Python literal listeleri
    - {'points': [...]} veya {'vertices': [...]} nesneleri
    - 'x,y;x,y;...' veya 'x y | x y' benzeri duz metinler
    """
    if not shape_base_string:
        return []

    raw = str(shape_base_string).strip()
    if not raw:
        return []

    parsers = []
    parsers.append(lambda text: json.loads(text))
    parsers.append(lambda text: ast.literal_eval(text))

    for parser in parsers:
        try:
            parsed = parser(raw)
            points = _coerce_points_from_object(parsed)
            if len(points) >= 3:
                return _close_polyline_points(points)
        except Exception:
            pass

    number_matches = re.findall(r"[-+]?\d+(?:[.,]\d+)?", raw)
    if len(number_matches) >= 6 and len(number_matches) % 2 == 0:
        values = [float(item.replace(",", ".")) for item in number_matches]
        points = list(zip(values[0::2], values[1::2]))
        if len(points) >= 3:
            return _close_polyline_points(points)

    return []


def load_latest_imported_dxf_shape_points():
    """Backend'in kaydettigi son DXF importundan ilk shape nokta listesini al."""
    store_path = os.path.join(
        _resolve_project_root(),
        "AI",
        "GlassCuttingProgram",
        "data",
        "dxf_imported_shapes.json",
    )
    if not os.path.exists(store_path):
        return []

    with open(store_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    imports = payload.get("imports", [])
    if not imports:
        return []

    latest_import = imports[-1]
    shapes = latest_import.get("shapes", [])
    if not shapes:
        return []

    points = _coerce_points_from_object(shapes[0].get("points", []))
    return _close_polyline_points(points)


def extract_shape_points_from_order(order):
    """
    Siparisten gercek kontur noktalarini bulmaya calis.
    Oncelik: ShapeBaseString -> herofis_options.shape_base_string -> DXF store.
    """
    herofis_options = order.get("herofis_options", {}) or {}
    shape_candidates = [
        order.get("shapeBaseString"),
        herofis_options.get("shape_base_string"),
        herofis_options.get("shapeBaseString"),
    ]

    for candidate in shape_candidates:
        points = parse_shape_base_string(candidate)
        if len(points) >= 3:
            return {
                "points": points,
                "source": "shape_base_string",
            }

    dxf_points = load_latest_imported_dxf_shape_points()
    if len(dxf_points) >= 3:
        return {
            "points": dxf_points,
            "source": "dxf_import_store",
        }

    return {
        "points": [],
        "source": "none",
    }


def find_latest_generated_nc_file():
    """
    Kesim programinin urettigi en guncel NC dosyasini bul.
    Once AI/GlassCuttingProgram/output/gcode altini, sonra firmware orneklerini kontrol eder.
    """
    project_root = _resolve_project_root()
    candidate_dirs = [
        os.path.join(project_root, "AI", "GlassCuttingProgram", "output", "gcode"),
        os.path.join(project_root, "Firmware", "NC300", "GCode"),
    ]

    candidates = []
    for directory in candidate_dirs:
        if not os.path.isdir(directory):
            continue
        for entry in os.listdir(directory):
            lower_name = entry.lower()
            if not lower_name.endswith((".nc", ".gcode", ".ngc", ".txt")):
                continue
            full_path = os.path.join(directory, entry)
            if os.path.isfile(full_path):
                candidates.append(full_path)

    if not candidates:
        return None

    candidates.sort(key=lambda path: os.path.getmtime(path), reverse=True)
    return candidates[0]


def generate_nc_from_current_orders(
    order_state_path=None,
    output_dir=None,
    program_name="current_orders_auto",
):
    """
    GlassCuttingProgram runtime siparislerinden yerel algoritmalar ile NC uret.
    """
    project_root = _resolve_project_root()
    if order_state_path is None:
        order_state_path = os.path.join(
            project_root,
            "AI",
            "GlassCuttingProgram",
            "data",
            "runtime",
            "current_orders.json",
        )
    if output_dir is None:
        output_dir = os.path.join(project_root, "AI", "GlassCuttingProgram", "output", "gcode")

    if not os.path.exists(order_state_path):
        raise FileNotFoundError(f"Siparis dosyasi bulunamadi: {order_state_path}")

    with open(order_state_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    raw_orders = payload.get("orders", [])
    if not raw_orders:
        raise RuntimeError("current_orders.json icinde siparis bulunamadi")

    glass_program_root = os.path.join(project_root, "AI", "GlassCuttingProgram")
    if glass_program_root not in sys.path:
        sys.path.insert(0, glass_program_root)

    from modules.gcode_generator import GlassType, NC300GCodeGenerator
    from modules.nesting_optimizer import NestingAlgorithm, NestingOptimizer, Part
    from modules.path_planner import CuttingPathOptimizer, PathAlgorithm

    parts = []
    detected_glass_type = GlassType.FLOAT
    for order in raw_orders:
        glass_type_value = str(order.get("glass_type", "float")).strip().lower()
        if glass_type_value == GlassType.LAMINATED.value:
            detected_glass_type = GlassType.LAMINATED
        elif glass_type_value == GlassType.TEMPERED.value and detected_glass_type != GlassType.LAMINATED:
            detected_glass_type = GlassType.TEMPERED

        quantity = max(1, int(order.get("quantity", 1)))
        for index in range(quantity):
            parts.append(
                Part(
                    part_id=f"{order.get('order_id', 'ORD')}-{index+1}",
                    width=float(order.get("width", 0.0)),
                    height=float(order.get("height", 0.0)),
                    thickness=float(order.get("thickness", 4.0)),
                    priority=int(order.get("priority", 1)),
                    rotate_allowed=bool(order.get("rotate_allowed", True)),
                    glass_type=glass_type_value or "float",
                    blade_delete_enabled=bool(order.get("blade_delete_enabled", False)),
                    trimming_enabled=bool(order.get("trimming_enabled", False)),
                )
            )

    optimizer = NestingOptimizer(
        MachineParameters.X_MAX,
        MachineParameters.Y_MAX,
        NestingAlgorithm.GUILLOTINE_BESTFIT,
    )
    nesting_result = optimizer.optimize(parts)
    placed_parts = nesting_result.get("placed_parts", [])
    if not placed_parts:
        raise RuntimeError("Yerel nesting sonucu yerlestirilmis parca uretmedi")

    path_optimizer = CuttingPathOptimizer(MachineParameters.X_MAX, MachineParameters.Y_MAX)
    path_result = path_optimizer.optimize(placed_parts, PathAlgorithm.TWO_OPT)
    cutting_path = path_result.get("path", list(range(len(placed_parts))))

    gcode_generator = NC300GCodeGenerator()
    gcode_program = gcode_generator.generate(
        placed_parts,
        cutting_path,
        detected_glass_type,
        program_name,
    )
    gcode_file = gcode_generator.save_to_file(gcode_program, output_dir)

    return {
        "order_state_path": order_state_path,
        "gcode_file": gcode_file,
        "parts_loaded": len(parts),
        "parts_placed": len(placed_parts),
        "cutting_path": cutting_path,
        "utilization": nesting_result.get("utilization"),
        "waste_area": nesting_result.get("waste_area"),
        "glass_type": detected_glass_type.value,
    }


def _build_representative_shape_points(width, height):
    """
    Gercek kontur olmadiginda kullanilacak temsilci sekilli kesim konturu.
    Dikdortgen sinirlari icinde kirik koseli 6 nokta uretir.
    """
    width = max(100.0, float(width))
    height = max(100.0, float(height))
    cut_x = min(width * 0.22, width * 0.4)
    cut_y = min(height * 0.18, height * 0.4)
    return [
        (0.0, 0.0),
        (width - cut_x, 0.0),
        (width, cut_y),
        (width, height),
        (cut_x, height),
        (0.0, height - cut_y),
    ]


def generate_shape_trial_nc_from_current_orders(
    order_state_path=None,
    output_dir=None,
    program_name="current_orders_shape_trial",
):
    """
    current_orders.json icindeki is_shape=true satirlar icin temsilci sekilli NC uret.

    Not:
    - Runtime siparislerinde gercek kontur koordinatlari olmadigi icin deneme amaclidir.
    - Kontur, parca bounding-box icinde temsilci bir polygon olarak uretilir.
    """
    project_root = _resolve_project_root()
    if order_state_path is None:
        order_state_path = os.path.join(
            project_root,
            "AI",
            "GlassCuttingProgram",
            "data",
            "runtime",
            "current_orders.json",
        )
    if output_dir is None:
        output_dir = os.path.join(project_root, "AI", "GlassCuttingProgram", "output", "gcode")

    if not os.path.exists(order_state_path):
        raise FileNotFoundError(f"Siparis dosyasi bulunamadi: {order_state_path}")

    with open(order_state_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    raw_orders = payload.get("orders", [])
    shape_orders = []
    for order in raw_orders:
        if bool((order.get("herofis_options") or {}).get("is_shape")):
            shape_orders.append(order)

    if not shape_orders:
        raise RuntimeError("current_orders.json icinde is_shape=true siparis bulunamadi")

    glass_program_root = os.path.join(project_root, "AI", "GlassCuttingProgram")
    if glass_program_root not in sys.path:
        sys.path.insert(0, glass_program_root)

    from modules.gcode_generator import NC300GCodeGenerator, GCodeProgram, GlassType

    generator = NC300GCodeGenerator()
    lines = generator._generate_header(program_name, GlassType.FLOAT, shape_orders)

    cursor_x = 150.0
    cursor_y = 150.0
    row_height = 0.0
    placed_shapes = []

    for order in shape_orders:
        width = float(order.get("width", 0.0))
        height = float(order.get("height", 0.0))
        quantity = max(1, int(order.get("quantity", 1)))
        shape_id_root = str(order.get("order_id", "SHAPE"))

        for index in range(quantity):
            if cursor_x + width > MachineParameters.X_MAX - 150.0:
                cursor_x = 150.0
                cursor_y += row_height + 150.0
                row_height = 0.0
            if cursor_y + height > MachineParameters.Y_MAX - 150.0:
                break

            part_id = f"{shape_id_root}-S{index+1}"
            points = _build_representative_shape_points(width, height)
            lines.extend(
                [
                    "",
                    f"; --- Shape trial part: {part_id} ---",
                    f"; Bounding size: {width:.0f}x{height:.0f} mm",
                    "; NOTE: Representative polygon generated because contour coordinates are unavailable",
                ]
            )
            lines.extend(generator.generate_shape_cut(cursor_x, cursor_y, points, part_id))
            placed_shapes.append(
                {
                    "part_id": part_id,
                    "x": cursor_x,
                    "y": cursor_y,
                    "width": width,
                    "height": height,
                    "points": points,
                }
            )
            cursor_x += width + 120.0
            row_height = max(row_height, height)

    if not placed_shapes:
        raise RuntimeError("Sekilli deneme icin yerlestirilebilir parca uretilemedi")

    lines.extend(generator._generate_footer())

    total_distance = 0.0
    for shape in placed_shapes:
        pts = shape["points"]
        for idx in range(len(pts)):
            x1, y1 = pts[idx]
            x2, y2 = pts[(idx + 1) % len(pts)]
            total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    program = GCodeProgram(
        filename=f"{program_name}_{time.strftime('%Y%m%d_%H%M%S')}.nc",
        lines=lines,
        parts_count=len(placed_shapes),
        total_distance=total_distance,
        estimated_time=(total_distance / max(1.0, generator.params.cut_speed) * 60.0),
        glass_type=GlassType.FLOAT.value,
        created_at=datetime.datetime.now(),
    )
    gcode_file = generator.save_to_file(program, output_dir)

    return {
        "order_state_path": order_state_path,
        "gcode_file": gcode_file,
        "shape_orders": len(shape_orders),
        "parts_placed": len(placed_shapes),
        "placed_shapes": placed_shapes,
        "note": "Representative shape polygons were generated because contour coordinates are unavailable in runtime orders.",
    }


def generate_real_shape_nc_from_current_orders(
    order_state_path=None,
    output_dir=None,
    program_name="current_orders_real_shape",
    fallback_to_trial=True,
):
    """
    current_orders.json icindeki sekilli siparislerden gercek kontur NC uret.

    Kaynak sirasi:
    1. ShapeBaseString
    2. herofis_options.shape_base_string
    3. dxf_imported_shapes.json icindeki son import
    4. opsiyonel olarak temsilci trial kontur
    """
    project_root = _resolve_project_root()
    if order_state_path is None:
        order_state_path = os.path.join(
            project_root,
            "AI",
            "GlassCuttingProgram",
            "data",
            "runtime",
            "current_orders.json",
        )
    if output_dir is None:
        output_dir = os.path.join(project_root, "AI", "GlassCuttingProgram", "output", "gcode")

    if not os.path.exists(order_state_path):
        raise FileNotFoundError(f"Siparis dosyasi bulunamadi: {order_state_path}")

    with open(order_state_path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    raw_orders = payload.get("orders", [])
    shape_orders = [order for order in raw_orders if bool((order.get("herofis_options") or {}).get("is_shape"))]
    if not shape_orders:
        raise RuntimeError("current_orders.json icinde is_shape=true siparis bulunamadi")

    glass_program_root = os.path.join(project_root, "AI", "GlassCuttingProgram")
    if glass_program_root not in sys.path:
        sys.path.insert(0, glass_program_root)

    from modules.gcode_generator import NC300GCodeGenerator, GCodeProgram, GlassType

    generator = NC300GCodeGenerator()
    lines = generator._generate_header(program_name, GlassType.FLOAT, shape_orders)

    cursor_x = 150.0
    cursor_y = 150.0
    row_height = 0.0
    placed_shapes = []
    source_counts = {}

    for order in shape_orders:
        width = float(order.get("width", 0.0))
        height = float(order.get("height", 0.0))
        quantity = max(1, int(order.get("quantity", 1)))
        shape_id_root = str(order.get("order_id", "SHAPE"))
        shape_data = extract_shape_points_from_order(order)
        source = shape_data["source"]
        base_points = shape_data["points"]

        if len(base_points) < 3 and not fallback_to_trial:
            continue
        if len(base_points) < 3:
            base_points = _build_representative_shape_points(width, height)
            source = "trial_fallback"

        fitted_points = _scale_points_to_dimensions(base_points, width, height)
        fitted_points = _close_polyline_points(fitted_points)

        for index in range(quantity):
            if cursor_x + width > MachineParameters.X_MAX - 150.0:
                cursor_x = 150.0
                cursor_y += row_height + 150.0
                row_height = 0.0
            if cursor_y + height > MachineParameters.Y_MAX - 150.0:
                break

            part_id = f"{shape_id_root}-S{index+1}"
            lines.extend(
                [
                    "",
                    f"; --- Real shape part: {part_id} ---",
                    f"; Bounding size: {width:.0f}x{height:.0f} mm",
                    f"; Shape source: {source}",
                ]
            )
            lines.extend(generator.generate_shape_cut(cursor_x, cursor_y, fitted_points, part_id))
            placed_shapes.append(
                {
                    "part_id": part_id,
                    "x": cursor_x,
                    "y": cursor_y,
                    "width": width,
                    "height": height,
                    "points": fitted_points,
                    "source": source,
                }
            )
            source_counts[source] = source_counts.get(source, 0) + 1
            cursor_x += width + 120.0
            row_height = max(row_height, height)

    if not placed_shapes:
        raise RuntimeError("Gercek sekil NC uretilemedi; ShapeBaseString veya DXF verisi bulunamadi")

    lines.extend(generator._generate_footer())

    total_distance = 0.0
    for shape in placed_shapes:
        pts = shape["points"]
        for idx in range(len(pts) - 1):
            x1, y1 = pts[idx]
            x2, y2 = pts[idx + 1]
            total_distance += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    program = GCodeProgram(
        filename=f"{program_name}_{time.strftime('%Y%m%d_%H%M%S')}.nc",
        lines=lines,
        parts_count=len(placed_shapes),
        total_distance=total_distance,
        estimated_time=(total_distance / max(1.0, generator.params.cut_speed) * 60.0),
        glass_type=GlassType.FLOAT.value,
        created_at=datetime.datetime.now(),
    )
    gcode_file = generator.save_to_file(program, output_dir)

    return {
        "order_state_path": order_state_path,
        "gcode_file": gcode_file,
        "shape_orders": len(shape_orders),
        "parts_placed": len(placed_shapes),
        "placed_shapes": placed_shapes,
        "source_counts": source_counts,
        "fallback_to_trial": fallback_to_trial,
    }


def _arc_to_segments(start_position, end_position, i_offset, j_offset, clockwise, segment_length_mm=150.0):
    """
    XY duzlemindeki G02/G03 hareketini lineer segmentlere boler.
    """
    center_x = start_position["X"] + i_offset
    center_y = start_position["Y"] + j_offset
    radius = math.sqrt((start_position["X"] - center_x) ** 2 + (start_position["Y"] - center_y) ** 2)

    if radius <= 0.0001:
        return [dict(end_position)]

    start_angle = math.atan2(start_position["Y"] - center_y, start_position["X"] - center_x)
    end_angle = math.atan2(end_position["Y"] - center_y, end_position["X"] - center_x)

    if clockwise:
        if end_angle >= start_angle:
            end_angle -= 2.0 * math.pi
        sweep_angle = end_angle - start_angle
    else:
        if end_angle <= start_angle:
            end_angle += 2.0 * math.pi
        sweep_angle = end_angle - start_angle

    arc_length = abs(sweep_angle) * radius
    segment_count = max(3, min(72, int(arc_length / max(1.0, segment_length_mm)) + 1))

    z_start = float(start_position.get("Z", 0.0))
    z_end = float(end_position.get("Z", z_start))
    segments = []
    for index in range(1, segment_count + 1):
        ratio = index / segment_count
        angle = start_angle + sweep_angle * ratio
        segments.append(
            {
                "X": center_x + radius * math.cos(angle),
                "Y": center_y + radius * math.sin(angle),
                "Z": z_start + (z_end - z_start) * ratio,
            }
        )

    segments[-1] = dict(end_position)
    return segments


def _distance_between_positions(start_position, end_position):
    """XYZ noktalar arasi 3B mesafe."""
    dx = float(end_position.get("X", 0.0)) - float(start_position.get("X", 0.0))
    dy = float(end_position.get("Y", 0.0)) - float(start_position.get("Y", 0.0))
    dz = float(end_position.get("Z", 0.0)) - float(start_position.get("Z", 0.0))
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def parse_nc_file(nc_path):
    """
    Basit G00/G01/G28 iceren NC dosyasini hareket listesine donusturur.
    """
    if not os.path.exists(nc_path):
        raise FileNotFoundError(f"NC dosyasi bulunamadi: {nc_path}")

    with open(nc_path, "r", encoding="utf-8") as handle:
        gcode = handle.read()

    absolute_mode = True
    current = {"X": 0.0, "Y": 0.0, "Z": 0.0}
    feed_rate = 1000.0
    moves = []
    spindle_on = False
    vacuum_on = False
    blade_delete_on = False
    motion_mode = None

    for raw_line in gcode.splitlines():
        line = raw_line.strip()
        if not line or line == "%":
            continue

        line = re.sub(r"\([^)]*\)", "", line).strip().upper()
        if not line:
            continue

        tokens = re.findall(r"[A-Z][+-]?\d+(?:\.\d+)?", line)
        if not tokens:
            continue

        g_codes = [token for token in tokens if token.startswith("G")]
        if "G90" in g_codes:
            absolute_mode = True
        if "G91" in g_codes:
            absolute_mode = False
        if "M03" in tokens:
            spindle_on = True
        if "M05" in tokens:
            spindle_on = False
        if "M08" in tokens:
            vacuum_on = True
        if "M09" in tokens:
            vacuum_on = False
        if "M10" in tokens:
            blade_delete_on = True
        if "M11" in tokens:
            blade_delete_on = False

        if any(code in ("G04", "G4") for code in g_codes):
            dwell_seconds = 0.0
            for token in tokens:
                if token.startswith("P"):
                    dwell_seconds = float(token[1:])
                    break
            moves.append(
                {
                    "type": "dwell",
                    "from": dict(current),
                    "to": dict(current),
                    "feed": 0.0,
                    "dwell_seconds": dwell_seconds,
                    "spindle": spindle_on,
                    "vacuum": vacuum_on,
                    "blade_delete": blade_delete_on,
                    "segments": [dict(current)],
                    "raw": raw_line,
                }
            )
            continue

        if "G00" in g_codes or "G0" in g_codes:
            motion_mode = "rapid"
        elif "G01" in g_codes or "G1" in g_codes:
            motion_mode = "cut"
        elif "G02" in g_codes or "G2" in g_codes:
            motion_mode = "arc_cw"
        elif "G03" in g_codes or "G3" in g_codes:
            motion_mode = "arc_ccw"

        if any(code == "G28" for code in g_codes):
            target = dict(current)
            axes_in_line = [token[0] for token in tokens if token[0] in "XYZ"]
            if axes_in_line:
                for axis in axes_in_line:
                    target[axis] = 0.0
            else:
                target = {"X": 0.0, "Y": 0.0, "Z": 0.0}

            moves.append(
                {
                    "type": "home",
                    "from": dict(current),
                    "to": dict(target),
                    "feed": 3000.0,
                    "spindle": spindle_on,
                    "vacuum": vacuum_on,
                    "blade_delete": blade_delete_on,
                    "segments": [dict(target)],
                    "raw": raw_line,
                }
            )
            current = target
            continue

        command = motion_mode
        if command is None:
            continue

        target = dict(current)
        i_offset = 0.0
        j_offset = 0.0
        for token in tokens:
            axis = token[0]
            if axis in "XYZ":
                value = float(token[1:])
                target[axis] = value if absolute_mode else current[axis] + value
            elif axis == "I":
                i_offset = float(token[1:])
            elif axis == "J":
                j_offset = float(token[1:])
            elif axis == "F":
                feed_rate = float(token[1:])

        segments = [dict(target)]
        if command in ("arc_cw", "arc_ccw"):
            segments = _arc_to_segments(
                current,
                target,
                i_offset=i_offset,
                j_offset=j_offset,
                clockwise=(command == "arc_cw"),
            )

        moves.append(
            {
                "type": command,
                "from": dict(current),
                "to": dict(target),
                "feed": 5000.0 if command == "rapid" else feed_rate,
                "spindle": spindle_on,
                "vacuum": vacuum_on,
                "blade_delete": blade_delete_on,
                "segments": segments,
                "raw": raw_line,
            }
        )
        current = target

    return moves


def run_nc_file_simulation(doc=None, nc_path=None, playback_step_mm=150.0, verbose=True):
    """
    NC dosyasindaki eksen hareketlerini FreeCAD modelinde oynatir.
    """
    if doc is None:
        doc = App.ActiveDocument
    if doc is None:
        raise RuntimeError("Aktif FreeCAD dokumani bulunamadi")
    if not nc_path:
        nc_path = find_latest_generated_nc_file()
    if not nc_path:
        raise ValueError("NC dosya yolu verilmedi ve otomatik bulunamadi")

    moves = parse_nc_file(nc_path)
    if not moves:
        raise RuntimeError(f"Simule edilecek hareket bulunamadi: {nc_path}")

    total_path_mm = 0.0
    total_cut_length_mm = 0.0
    total_rapid_length_mm = 0.0
    estimated_duration_s = 0.0
    estimated_cut_duration_s = 0.0
    estimated_rapid_duration_s = 0.0
    cut_moves = 0
    rapid_moves = 0
    arc_moves = 0
    event_log = []
    previous_spindle = None
    previous_vacuum = None
    previous_blade_delete = False

    if verbose:
        print("=" * 60)
        print("NC DOSYASI -> FREECAD PLAYBACK SIMULASYONU")
        print("=" * 60)
        print(f"Dosya: {nc_path}")
        print(f"Hareket sayisi: {len(moves)}")
        print("-" * 60)

    for index, move in enumerate(moves, start=1):
        if move["type"] == "cut":
            cut_moves += 1
        elif move["type"] in ("rapid", "home"):
            rapid_moves += 1
        elif move["type"] in ("arc_cw", "arc_ccw"):
            arc_moves += 1
        elif move["type"] == "dwell":
            event_log.append(
                {
                    "time_s": round(estimated_duration_s, 3),
                    "move_index": index,
                    "event": "dwell",
                    "source": move["raw"].strip(),
                    "duration_s": round(float(move.get("dwell_seconds", 0.0)), 3),
                }
            )

        spindle_state = bool(move.get("spindle", False))
        vacuum_state = bool(move.get("vacuum", False))
        blade_delete_state = bool(move.get("blade_delete", False))
        if previous_spindle is None or spindle_state != previous_spindle:
            event_log.append(
                {
                    "time_s": round(estimated_duration_s, 3),
                    "move_index": index,
                    "event": "spindle_on" if spindle_state else "spindle_off",
                    "source": move["raw"].strip(),
                }
            )
            previous_spindle = spindle_state
        if previous_vacuum is None or vacuum_state != previous_vacuum:
            event_log.append(
                {
                    "time_s": round(estimated_duration_s, 3),
                    "move_index": index,
                    "event": "vacuum_on" if vacuum_state else "vacuum_off",
                    "source": move["raw"].strip(),
                }
            )
            previous_vacuum = vacuum_state
        if previous_blade_delete is None or blade_delete_state != previous_blade_delete:
            event_log.append(
                {
                    "time_s": round(estimated_duration_s, 3),
                    "move_index": index,
                    "event": "blade_delete_on" if blade_delete_state else "blade_delete_off",
                    "source": move["raw"].strip(),
                }
            )
            previous_blade_delete = blade_delete_state

        current_outputs = _build_nc_output_state(
            spindle_on=spindle_state,
            vacuum_on=vacuum_state,
            cycle_complete=False,
        )
        update_lamine_io_sheet(doc, {}, current_outputs)

        if move["type"] == "dwell":
            estimated_duration_s += float(move.get("dwell_seconds", 0.0))
            estimated_cut_duration_s += float(move.get("dwell_seconds", 0.0))
            continue

        segment_points = [dict(move["from"])] + [dict(segment) for segment in move.get("segments", [move["to"]])]
        for segment_start, segment_end in zip(segment_points[:-1], segment_points[1:]):
            work_distance = _distance_between_positions(segment_start, segment_end)
            start = _nc_work_to_machine_position(segment_start)
            end = _nc_work_to_machine_position(segment_end)
            distance = _distance_between_positions(start, end)
            total_path_mm += distance
            if move["type"] in ("cut", "arc_cw", "arc_ccw"):
                total_cut_length_mm += work_distance
            else:
                total_rapid_length_mm += work_distance

            feed = max(1.0, float(move.get("feed", 1000.0)))
            segment_duration_s = (work_distance / feed) * 60.0
            estimated_duration_s += segment_duration_s
            if move["type"] in ("cut", "arc_cw", "arc_ccw"):
                estimated_cut_duration_s += segment_duration_s
            else:
                estimated_rapid_duration_s += segment_duration_s

            step_count = max(3, min(40, int(distance / max(1.0, playback_step_mm)) + 1))
            for step in range(1, step_count + 1):
                ratio = step / step_count
                x_pos = start["X"] + (end["X"] - start["X"]) * ratio
                y_pos = start["Y"] + (end["Y"] - start["Y"]) * ratio
                z_pos = start["Z"] + (end["Z"] - start["Z"]) * ratio
                set_axis_positions(doc, x=x_pos, y=y_pos, z=z_pos, v=0.0)

        end = _nc_work_to_machine_position(move["to"])

        if verbose:
            print(
                f"{index:02d}. {move['type'].upper():5s} | "
                f"{move['raw'].strip():35s} | "
                f"X:{end['X']:6.1f} Y:{end['Y']:6.1f} Z:{end['Z']:6.1f}"
            )

    final_position = _nc_work_to_machine_position(moves[-1]["to"])
    update_lamine_io_sheet(doc, {}, _build_nc_output_state(cycle_complete=True))
    event_log.append(
        {
            "time_s": round(estimated_duration_s, 3),
            "move_index": len(moves),
            "event": "cycle_complete",
            "source": "simulation_end",
        }
    )
    if verbose:
        print("-" * 60)
        print(f"Rapid/home hareket: {rapid_moves}")
        print(f"Kesim hareketi: {cut_moves}")
        print(f"Yay hareketi: {arc_moves}")
        print(f"Toplam yol (model mm): {total_path_mm:.1f}")
        print(f"Toplam kesim uzunlugu (NC mm): {total_cut_length_mm:.1f}")
        print(f"Tahmini sure (sn): {estimated_duration_s:.2f}")
        print(
            f"Final pozisyon: "
            f"X={final_position['X']:.1f} "
            f"Y={final_position['Y']:.1f} "
            f"Z={final_position['Z']:.1f} "
            f"V={final_position['V']:.1f}"
        )
        print("=" * 60)

    return {
        "moves": len(moves),
        "cut_moves": cut_moves,
        "rapid_moves": rapid_moves,
        "arc_moves": arc_moves,
        "total_path_mm": round(total_path_mm, 1),
        "total_cut_length_mm": round(total_cut_length_mm, 1),
        "total_rapid_length_mm": round(total_rapid_length_mm, 1),
        "estimated_duration_s": round(estimated_duration_s, 3),
        "estimated_cut_duration_s": round(estimated_cut_duration_s, 3),
        "estimated_rapid_duration_s": round(estimated_rapid_duration_s, 3),
        "event_log": event_log,
        "final_position": final_position,
        "nc_path": nc_path,
    }


def export_nc_simulation_report(result, report_path=None):
    """
    NC simulasyon sonucunu JSON raporu olarak disa aktarir.
    """
    if result is None:
        raise ValueError("Rapor icin simulasyon sonucu gerekli")

    if report_path is None:
        report_dir = os.path.join(_resolve_project_root(), "CAD", "FreeCAD", "07_Exports", "Reports")
        os.makedirs(report_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(result["nc_path"]))[0]
        report_path = os.path.join(report_dir, f"{base_name}_simulation_report.json")
    else:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

    payload = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "nc_path": result["nc_path"],
        "moves": result["moves"],
        "cut_moves": result["cut_moves"],
        "rapid_moves": result["rapid_moves"],
        "arc_moves": result["arc_moves"],
        "total_path_mm": result["total_path_mm"],
        "total_cut_length_mm": result["total_cut_length_mm"],
        "total_rapid_length_mm": result["total_rapid_length_mm"],
        "estimated_duration_s": result["estimated_duration_s"],
        "estimated_cut_duration_s": result["estimated_cut_duration_s"],
        "estimated_rapid_duration_s": result["estimated_rapid_duration_s"],
        "final_position": result["final_position"],
        "event_log": result["event_log"],
    }

    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=True, indent=2)

    print(f"NC simulasyon raporu yazildi: {report_path}")
    return report_path


def run_nc300_lamine_cycle(doc=None, duration_sec=25.0, update_period_s=0.05):
    """
    NC300 orta seviye simulatörünü FreeCAD modeliyle senkron calistirir.
    """
    if doc is None:
        doc = App.ActiveDocument
    if doc is None:
        raise RuntimeError("Aktif FreeCAD dokumani bulunamadi")

    simulator = create_nc300_bridge(doc)
    simulator.update_period_s = update_period_s
    simulator.write_register(simulator.REG_START_LAMINE, 1)

    steps = max(1, int(duration_sec / update_period_s))
    print("=" * 60)
    print("NC300 -> FreeCAD CANLI KOPRU BASLATILIYOR")
    print("=" * 60)
    print(f"Adim sayisi: {steps}")
    print(f"Guncelleme periyodu: {update_period_s:.3f}s")
    print("-" * 60)

    last_state = None
    for step in range(steps):
        simulator.tick(update_period_s)
        snapshot = simulator.get_snapshot()
        state = snapshot["lamine_state"]
        if state != last_state:
            print(f"[NC300] State -> {state} | {snapshot['lamine_message']}")
            last_state = state

        if step % max(1, steps // 10) == 0 or state in ("COMPLETE", "ERROR"):
            pos = snapshot["positions_mm"]
            print(
                f"Adim {step:3d}/{steps} | "
                f"X:{pos['X']:6.0f} Y:{pos['Y']:6.0f} Z:{pos['Z']:6.0f} V:{pos['V']:6.0f} | "
                f"State:{state}"
            )

        if state in ("COMPLETE", "ERROR"):
            break

        time.sleep(update_period_s * 0.2)

    print("-" * 60)
    print(f"NC300 kopru tamamlandi | Son state: {simulator.get_snapshot()['lamine_state']}")
    print("=" * 60)
    return simulator


# =============================================================================
# VB-MODUL LAMİNE KESİM SİMÜLASYONU
# =============================================================================

def run_lamine_cutting_simulation(doc, params, duration_sec=45):
    """
    Lamine cam kesim süreci simülasyonu
    
    Süreç adımları:
    1. Cam yükleme ve vakum
    2. Isıtma (Heizstab)
    3. Üst kesim (Z ekseni)
    4. Alt kesim (V ekseni - senkronize)
    5. Ayırma (Trennklinge)
    6. Kırma (Brechleiste)
    7. Cam boşaltma
    """
    print("=" * 60)
    print("LAMİNE CAM KESİM SİMÜLASYONU BAŞLATILIYOR")
    print("=" * 60)
    
    ss = doc.getObject("Variables")
    if ss is None:
        raise RuntimeError("Variables spreadsheet bulunamadi")

    phase_sequence = build_lamine_phase_sequence(params)
    populate_lamine_phase_sheet(doc, phase_sequence)

    default_inputs = {signal: False for signal in LAMINE_INPUT_DESCRIPTIONS}
    default_outputs = {signal: False for signal in LAMINE_OUTPUT_DESCRIPTIONS}
    default_inputs["ESTOP_OK"] = True
    default_inputs["DOOR_CLOSED"] = True
    default_inputs["AIR_PRESSURE_OK"] = True

    steps = 160
    step_time = duration_sec / steps

    print(f"Simülasyon: {steps} adım, {step_time:.2f}s/adım")
    print(f"Toplam süre: {duration_sec}s")
    print(f"Faz sayısı: {len(phase_sequence)}")
    print("-" * 60)

    segments = len(phase_sequence) - 1
    last_phase_name = None

    for step in range(steps + 1):
        progress = step / steps
        phase_progress = progress * segments
        segment = min(int(phase_progress), segments - 1)
        segment_t = phase_progress - segment

        current_phase = phase_sequence[segment]
        next_phase = phase_sequence[segment + 1]
        current_target = _interpolate_phase_targets(
            current_phase["target"],
            next_phase["target"],
            segment_t,
        )

        x_pos = current_target["x"]
        y_pos = current_target["y"]
        z_pos = current_target["z"]
        v_pos = current_target["v"]

        inputs, outputs = _merge_io_states(
            default_inputs,
            default_outputs,
            current_phase["inputs"],
            current_phase["outputs"],
        )

        if step == steps:
            final_phase = phase_sequence[-1]
            x_pos = final_phase["target"]["x"]
            y_pos = final_phase["target"]["y"]
            z_pos = final_phase["target"]["z"]
            v_pos = final_phase["target"]["v"]
            inputs, outputs = _merge_io_states(
                default_inputs,
                default_outputs,
                final_phase["inputs"],
                final_phase["outputs"],
            )
            current_phase = final_phase

        ss.set('A1', f'{x_pos} mm')
        ss.set('B1', f'{y_pos} mm')
        ss.set('C1', f'{params.Z_HOME - z_pos} mm')
        ss.set('D1', f'{v_pos} mm')

        update_lamine_io_sheet(doc, inputs, outputs)
        doc.recompute()

        if current_phase["phase"] != last_phase_name:
            print(f"[FAZ] {current_phase['phase']} -> sartlar: {', '.join(current_phase['guards'])}")
            print(f"      cikislar: {', '.join(sorted(current_phase['outputs'].keys()))}")
            last_phase_name = current_phase["phase"]

        if step % 16 == 0 or step == steps:
            active_inputs = [name for name, state in inputs.items() if state]
            active_outputs = [name for name, state in outputs.items() if state]
            print(
                f"Adım {step}/{steps} | Faz: {current_phase['phase']:18s} | "
                f"X: {x_pos:6.0f} | Y: {y_pos:6.0f} | Z: {z_pos:6.0f} | V: {v_pos:6.0f}"
            )
            print(f"      DI : {', '.join(active_inputs)}")
            print(f"      DO : {', '.join(active_outputs)}")

        time.sleep(step_time * 0.05)
    
    print("-" * 60)
    print("LAMİNE CAM KESİM SİMÜLASYONU TAMAMLANDI")
    print("=" * 60)


# =============================================================================
# TAM MAKİNE MONTAJI
# =============================================================================

def create_complete_machine():
    """
    GFB-60/30RE-S tam hibrit sistem montajını oluştur
    """
    print("=" * 60)
    print("LiSEC GFB-60/30RE-S - HİBRİT SİSTEM MONTAJI")
    print("(Düz Cam + Lamine Cam VB-Modul)")
    print("=" * 60)
    
    # Parametreler
    params = MachineParameters()
    
    # Document oluştur
    doc_name = "GFB_60_30RE_S_Complete"
    if App.ActiveDocument and App.ActiveDocument.Name != doc_name:
        App.closeDocument(App.ActiveDocument.Name)
    
    doc = App.newDocument(doc_name)
    doc.Label = "GFB-60/30RE-S Hibrit Sistem"
    print(f"Document: {doc.Label}")

    # Montaj gruplari
    loading_group = create_group(doc, "LoadingModule", "ATH / BSK Yukleme")
    main_group = create_group(doc, "MainMachine", "GFB Ana Makine")
    vb_group = create_group(doc, "VBModule", "VB Lamine Modul")
    breakout_group = create_group(doc, "BreakoutModule", "BTS Cikis Masasi")
    control_group = create_group(doc, "ControlLayer", "Kontrol ve Spreadsheetler")
    
    # Parçaları oluştur
    print("\nParçalar oluşturuluyor...")
    
    # Ana şase
    frame = create_frame_assembly(doc, params)

    # Hat modulleri
    loading_station = create_loading_station(doc, params)
    
    # Portal köprüsü (X ekseni)
    portal = create_portal_assembly(doc, frame, params)
    
    # Y ekseni
    y_axis = create_y_axis_assembly(doc, portal, params)
    
    # Z ekseni (üst kesim kafası)
    z_axis = create_z_axis_assembly(doc, y_axis)
    
    # VB-Modul bileşenleri
    vb_lower = create_vb_lower_cutter(doc, frame)
    vb_heater = create_vb_heater(doc, frame)
    vb_vacuum = create_vb_vacuum(doc, frame)
    vb_breaking = create_vb_breaking_bar(doc, frame)
    vb_separating = create_vb_separating_blade(doc, frame)
    vb_roller = create_vb_pressure_roller(doc, frame)
    breakout_table = create_breaking_table_module(doc, params)
    
    # Kablo tankları
    cables = create_cable_tracks(doc, params)
    
    # Değişken tablosu
    print("\nDeğişken tablosu oluşturuluyor...")
    ss = create_variables_spreadsheet(doc, params)
    io_sheet = create_lamine_io_spreadsheet(doc)
    phase_sheet = create_lamine_phase_spreadsheet(doc)
    populate_lamine_phase_sheet(doc, build_lamine_phase_sequence(params))

    # Grup hiyerarsisi
    add_objects_to_group(loading_group, loading_station)
    add_objects_to_group(main_group, [frame, portal, y_axis, z_axis, cables])
    add_objects_to_group(vb_group, [vb_lower, vb_heater, vb_vacuum, vb_breaking, vb_separating, vb_roller])
    add_objects_to_group(breakout_group, breakout_table)
    add_objects_to_group(control_group, [ss, io_sheet, phase_sheet])
    
    # Kinematik bağlantılar
    print("\nKinematik bağlantılar kuruluyor...")
    setup_kinematics(doc, params)
    
    # Güncelle
    doc.recompute()
    
    if Gui and Gui.ActiveDocument:
        Gui.SendMsgToActiveView("ViewFit")
    
    print("\n" + "=" * 60)
    print("GFB-60/30RE-S MONTAJI TAMAMLANDI!")
    print("=" * 60)
    print("\nEKSENLER:")
    print("  X Ekseni (Portal): 6000mm strok")
    print("  Y Ekseni (Kafa Yatay): 3000mm strok")
    print("  Z Ekseni (Üst Kesim): 300mm strok")
    print("  V Ekseni (Alt Kesici): 300mm strok (Y ile senkronize)")
    print("\nVB-MODUL BİLEŞENLERİ:")
    print("  - Alt kesici ünitesi")
    print("\nHAT MODULLERI:")
    print("  - ATH/BSK yukleme istasyonu")
    print("  - BTS kirma/bosaltma masasi")
    print("  - Isıtıcı çubuk (Heizstab)")
    print("  - Vakum vantuz sistemi")
    print("  - Kırma çıtası (Brechleiste)")
    print("  - Ayırma bıçağı (Trennklinge)")
    print("  - Basınç rollesi (Andrückrolle)")
    print("\nKONTROL KATMANI:")
    print("  - Lamine_IO spreadsheet: DI/DO durumları")
    print("  - Lamine_Phases spreadsheet: faz-geçiş kuralları")
    print("\nSİMÜLASYON İÇİN:")
    print("  run_lamine_cutting_simulation(App.ActiveDocument, MachineParameters())")
    print("\nNC300 KOPRUSU İÇİN:")
    print("  run_nc300_lamine_cycle(App.ActiveDocument, 25.0)")
    print("\nMANUEL HAREKET İÇİN:")
    print("  set_axis_positions(App.ActiveDocument, x=1000, y=500, z=150, v=100)")
    print("=" * 60)
    
    return doc


def export_machine_outputs(doc=None, export_root=None):
    """
    Modeli FCStd ve STEP olarak disa aktarir.
    """
    if doc is None:
        doc = App.ActiveDocument
    if doc is None:
        raise RuntimeError("Export icin aktif FreeCAD dokumani bulunamadi")

    if export_root is None:
        export_root = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/07_Exports"

    fcstd_dir = os.path.join(export_root, "FCStd")
    step_dir = os.path.join(export_root, "STEP", "Assembly")
    os.makedirs(fcstd_dir, exist_ok=True)
    os.makedirs(step_dir, exist_ok=True)

    fcstd_path = os.path.join(fcstd_dir, "GFB_60_30RE_S_Hybrid_Line.FCStd")
    step_path = os.path.join(step_dir, "GFB_60_30RE_S_Hybrid_Line.stp")

    doc.saveAs(fcstd_path)

    export_objects = []
    for obj in doc.Objects:
        if getattr(obj, "TypeId", "").startswith("Part::") and hasattr(obj, "Shape"):
            try:
                if not obj.Shape.isNull():
                    export_objects.append(obj)
            except Exception:
                pass

    if not export_objects:
        raise RuntimeError("STEP export icin uygun geometri bulunamadi")

    if Import is not None:
        Import.export(export_objects, step_path)
    else:
        Part.export(export_objects, step_path)

    print("=" * 60)
    print("EXPORT TAMAMLANDI")
    print("=" * 60)
    print(f"FCStd : {fcstd_path}")
    print(f"STEP  : {step_path}")
    print(f"Export edilen geometri sayisi: {len(export_objects)}")
    print("=" * 60)
    return {
        "fcstd": fcstd_path,
        "step": step_path,
        "count": len(export_objects),
    }


def parse_cli_args(argv=None):
    """Komut satiri seceneklerini cozumle."""
    parser = argparse.ArgumentParser(
        description="GFB-60/30RE-S hibrit hat modeli olusturur, simule eder ve export alir."
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Model kurulumundan sonra lamine kesim simulasyonunu calistir.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=30.0,
        help="Simulasyon suresi (saniye). Varsayilan: 30",
    )
    parser.add_argument(
        "--export",
        dest="do_export",
        action="store_true",
        help="Model kurulumundan sonra FCStd ve STEP export al.",
    )
    parser.add_argument(
        "--export-root",
        default=None,
        help="Export kok klasoru. Varsayilan repo icindeki 07_Exports yoludur.",
    )
    parser.add_argument(
        "--nc-file",
        default=None,
        help="Verilen NC dosyasini FreeCAD modeli uzerinde oynat.",
    )
    parser.add_argument(
        "--generate-current-orders-nc",
        action="store_true",
        help="AI/GlassCuttingProgram/data/runtime/current_orders.json dosyasindan yeni NC uret.",
    )
    parser.add_argument(
        "--current-orders-path",
        default=None,
        help="Siparis durum dosyasi yolu. Varsayilan current_orders.json yoludur.",
    )
    parser.add_argument(
        "--generate-shape-trial-nc",
        action="store_true",
        help="is_shape=true siparislerden temsilci sekilli kesim NC dosyasi uret.",
    )
    parser.add_argument(
        "--generate-real-shape-nc",
        action="store_true",
        help="is_shape=true siparisler icin ShapeBaseString veya DXF verisinden gercek shape NC uret.",
    )
    parser.add_argument(
        "--nc-report",
        action="store_true",
        help="NC simulasyon sonucunu JSON raporu olarak yaz.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Script giris noktasi."""
    args = parse_cli_args(argv)
    doc = create_complete_machine()
    params = MachineParameters()

    if args.simulate:
        run_lamine_cutting_simulation(doc, params, duration_sec=args.duration)

    generated_nc_result = None
    if args.generate_current_orders_nc:
        generated_nc_result = generate_nc_from_current_orders(
            order_state_path=args.current_orders_path,
        )
        print(f"Current orders NC uretildi: {generated_nc_result['gcode_file']}")
    elif args.generate_real_shape_nc:
        generated_nc_result = generate_real_shape_nc_from_current_orders(
            order_state_path=args.current_orders_path,
        )
        print(f"Real shape NC uretildi: {generated_nc_result['gcode_file']}")
    elif args.generate_shape_trial_nc:
        generated_nc_result = generate_shape_trial_nc_from_current_orders(
            order_state_path=args.current_orders_path,
        )
        print(f"Shape trial NC uretildi: {generated_nc_result['gcode_file']}")

    if args.nc_file:
        nc_result = run_nc_file_simulation(doc, args.nc_file)
        if args.nc_report:
            export_nc_simulation_report(nc_result)
    elif generated_nc_result is not None:
        nc_result = run_nc_file_simulation(doc, generated_nc_result["gcode_file"])
        if args.nc_report:
            export_nc_simulation_report(nc_result)

    if args.do_export:
        export_machine_outputs(doc, export_root=args.export_root)

    return doc


# =============================================================================
# KOMUT SATIRI ÇALIŞTIRMA
# =============================================================================

if __name__ == "__main__":
    main()
