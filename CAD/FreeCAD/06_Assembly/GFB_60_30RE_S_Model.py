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
import math
import os
import sys
import time

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
    FRAME_LENGTH = 6500.0  # mm
    FRAME_WIDTH = 3500.0   # mm
    FRAME_HEIGHT = 800.0   # mm
    
    # Portal boyutları
    PORTAL_WIDTH = 3200.0  # mm (X köprüsü)
    PORTAL_HEIGHT = 500.0  # mm
    
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


# =============================================================================
# ANA ŞASE MONTAJI
# =============================================================================

def create_frame_assembly(doc):
    """
    Ana şase/profil assembly'si
    """
    print("  - Şase oluşturuluyor...")
    
    # Ana uzun profiller (X ekseni boyunca)
    left_rail = create_box(
        doc, "Frame_Left_Rail",
        width=100, height=100, depth=6500,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 0, 0)
    )
    
    right_rail = create_box(
        doc, "Frame_Right_Rail",
        width=100, height=100, depth=6500,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 3400, 0)
    )
    
    # Ön ve arka profiller (Y ekseni boyunca)
    front_beam = create_box(
        doc, "Frame_Front_Beam",
        width=3400, height=100, depth=100,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 0, 0)
    )
    
    back_beam = create_box(
        doc, "Frame_Back_Beam",
        width=3400, height=100, depth=100,
        color=(0.5, 0.5, 0.5),
        position=App.Vector(0, 0, 6400)
    )
    
    # Destek ayakları
    for i in range(4):
        leg = create_box(
            doc, f"Frame_Leg_{i+1}",
            width=150, height=700, depth=150,
            color=(0.3, 0.3, 0.3),
            position=App.Vector(
                100 if i % 2 == 0 else 6300,
                100 if i < 2 else 3250,
                0
            )
        )
    
    # Masa üstü ızgarası (cam destek)
    table_grid = create_box(
        doc, "Table_Grid",
        width=3300, height=50, depth=6300,
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

def create_portal_assembly(doc, frame):
    """
    Portal köprüsü (X ekseni gantry)
    """
    print("  - Portal oluşturuluyor...")
    
    # X ekseni köprüsü
    bridge = create_box(
        doc, "Portal_Bridge",
        width=3200, height=150, depth=200,
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
        position=App.Vector(150, 3150, 100)
    )
    
    # X ekseni lineer rayları
    rail_left = create_box(
        doc, "X_Rail_Left",
        width=50, height=30, depth=6500,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(50, 150, 100)
    )
    
    rail_right = create_box(
        doc, "X_Rail_Right",
        width=50, height=30, depth=6500,
        color=(0.7, 0.7, 0.7),
        position=App.Vector(50, 3250, 100)
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
        position=App.Vector(50, 3300, 50)
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

def create_y_axis_assembly(doc, portal):
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
        width=50, height=30, depth=3200,
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
    
    # Parçaları oluştur
    print("\nParçalar oluşturuluyor...")
    
    # Ana şase
    frame = create_frame_assembly(doc)
    
    # Portal köprüsü (X ekseni)
    portal = create_portal_assembly(doc, frame)
    
    # Y ekseni
    y_axis = create_y_axis_assembly(doc, portal)
    
    # Z ekseni (üst kesim kafası)
    z_axis = create_z_axis_assembly(doc, y_axis)
    
    # VB-Modul bileşenleri
    vb_lower = create_vb_lower_cutter(doc, frame)
    vb_heater = create_vb_heater(doc, frame)
    vb_vacuum = create_vb_vacuum(doc, frame)
    vb_breaking = create_vb_breaking_bar(doc, frame)
    vb_separating = create_vb_separating_blade(doc, frame)
    vb_roller = create_vb_pressure_roller(doc, frame)
    
    # Kablo tankları
    cables = create_cable_tracks(doc, params)
    
    # Değişken tablosu
    print("\nDeğişken tablosu oluşturuluyor...")
    ss = create_variables_spreadsheet(doc, params)
    io_sheet = create_lamine_io_spreadsheet(doc)
    phase_sheet = create_lamine_phase_spreadsheet(doc)
    populate_lamine_phase_sheet(doc, build_lamine_phase_sequence(params))
    
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


# =============================================================================
# KOMUT SATIRI ÇALIŞTIRMA
# =============================================================================

if __name__ == "__main__":
    doc = create_complete_machine()
    params = MachineParameters()
    # Lamine kesim simülasyonunu çalıştır
    run_lamine_cutting_simulation(doc, params, duration_sec=30)
