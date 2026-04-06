# -*- coding: utf-8 -*-
"""
LiSEC GFB-60/30RE - Tam Makine Simülasyonu
FreeCAD Assembly4 Workbench için Python Script

Özellikler:
- X Ekseni (Gantry) - 6000mm hareket
- Y Ekseni (Portal) - 3000mm hareket  
- Z Ekseni (Kesim Kafası) - 300mm strok
- E-Cam profili simülasyonu
- Koordineli eksen hareketi

Yazar: CNC AI Orchestrator
Tarih: 2026-04-04
"""

import FreeCAD as App
import Part
import math
import time

try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None

# =============================================================================
# MAKİNE PARAMETRELERİ
# =============================================================================

class MachineParameters:
    """GFB-60/30RE makine parametreleri"""
    
    # Eksen limitleri
    X_MAX = 6000.0  # mm
    Y_MAX = 3000.0  # mm
    Z_MAX = 300.0   # mm
    
    # Hız parametreleri
    X_HIZ_MAX = 80000.0   # mm/dk (80 m/dk)
    Y_HIZ_MAX = 60000.0   # mm/dk
    Z_HIZ_MAX = 5000.0    # mm/dk
    
    # Başlangıç pozisyonları (Home)
    X_HOME = 0.0
    Y_HOME = 0.0
    Z_HOME = 300.0  # Üst pozisyon (güvenli)
    
    # Şase boyutları
    FRAME_LENGTH = 6500.0  # mm
    FRAME_WIDTH = 3500.0   # mm
    FRAME_HEIGHT = 800.0   # mm
    
    # Portal boyutları
    PORTAL_WIDTH = 3200.0  # mm (X köprüsü)
    PORTAL_HEIGHT = 500.0  # mm
    
    # Kesim parametreleri
    CAM_KALINLIGI = 16.0  # mm
    KESIM_BASINCI = 0.4   # MPa


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
    if hasattr(box, "ViewObject") and box.ViewObject:
        box.ViewObject.ShapeColor = color
    return box


def create_cylinder(doc, name, radius, height, color, position=App.Vector(0,0,0)):
    """Silindir geometrisi oluştur"""
    cyl = doc.addObject("Part::Cylinder", name)
    cyl.Radius = radius
    cyl.Height = height
    cyl.Label = name
    cyl.Placement.Base = position
    if hasattr(cyl, "ViewObject") and cyl.ViewObject:
        cyl.ViewObject.ShapeColor = color
    return cyl


def create_frame_assembly(doc):
    """
    Ana şase/profil assembly'si
    """
    print("  - Şase oluşturuluyor...")
    
    # Ana uzun profiller (X ekseni boyunca)
    left_rail = create_box(
        doc, "Frame_Left_Rail",
        width=100, height=100, depth=6500,
        color=(0.5, 0.5, 0.5),  # Gri
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
    
    return {
        'left_rail': left_rail,
        'right_rail': right_rail,
        'front_beam': front_beam,
        'back_beam': back_beam
    }


def create_portal_assembly(doc, frame):
    """
    Portal köprüsü (X ekseni gantry)
    """
    print("  - Portal oluşturuluyor...")
    
    # X ekseni köprüsü
    bridge = create_box(
        doc, "Portal_Bridge",
        width=3200, height=150, depth=200,
        color=(0.2, 0.4, 0.6),  # Mavi
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
    
    # X ekseni motorları
    motor_x_left = create_cylinder(
        doc, "Motor_X_Left",
        radius=60, height=150,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(50, 50, 50)
    )
    
    motor_x_right = create_cylinder(
        doc, "Motor_X_Right",
        radius=60, height=150,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(50, 3300, 50)
    )
    
    return {
        'bridge': bridge,
        'left_support': left_support,
        'right_support': right_support,
        'motor_left': motor_x_left,
        'motor_right': motor_x_right
    }


def create_y_axis_assembly(doc, portal):
    """
    Y ekseni (Portal üzerinde hareket)
    """
    print("  - Y ekseni oluşturuluyor...")
    
    # Y ekseni kızak
    carriage = create_box(
        doc, "Y_Carriage",
        width=400, height=200, depth=250,
        color=(0.8, 0.2, 0.2),  # Kırmızı
        position=App.Vector(
            portal['bridge'].Placement.Base.x + 1500,
            portal['bridge'].Placement.Base.y,
            portal['bridge'].Placement.Base.z + 150
        )
    )
    
    # Y ekseni motoru
    motor_y = create_cylinder(
        doc, "Motor_Y",
        radius=50, height=120,
        color=(0.1, 0.1, 0.1),
        position=App.Vector(
            carriage.Placement.Base.x - 50,
            carriage.Placement.Base.y - 50,
            carriage.Placement.Base.z + 100
        )
    )
    
    return {
        'carriage': carriage,
        'motor': motor_y
    }


def create_z_axis_assembly(doc, y_axis):
    """
    Z ekseni (Kesim kafası assembly'si)
    """
    print("  - Z ekseni (kesim kafası) oluşturuluyor...")
    
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
    
    # Kesim kafası
    head_body = create_box(
        doc, "Cutting_Head",
        width=80, height=150, depth=80,
        color=(1.0, 0.5, 0.0),  # Turuncu
        position=App.Vector(
            z_carriage.Placement.Base.x,
            z_carriage.Placement.Base.y - 100,
            z_carriage.Placement.Base.z
        )
    )
    
    # Kesim tekeri
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
    
    return {
        'column': column,
        'carriage': z_carriage,
        'head': head_body,
        'wheel': wheel,
        'motor': motor_z
    }


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
    
    return {
        'x': cable_x,
        'y': cable_y,
        'z': cable_z
    }


def create_variables_spreadsheet(doc, params):
    """
    Assembly4 değişken tablosu
    """
    ss = doc.addObject('Spreadsheet::Sheet', 'Variables')
    
    # Hücreleri birimli olarak ayarla (FreeCAD birimli değer bekliyor)
    ss.set('A1', f'{params.X_HOME} mm')  # X_Position
    ss.set('B1', f'{params.Y_HOME} mm')  # Y_Position
    ss.set('C1', f'{params.Z_HOME} mm')  # Z_Position
    ss.set('D1', f'{params.X_MAX} mm')   # X_Max
    ss.set('E1', f'{params.Y_MAX} mm')   # Y_Max
    ss.set('F1', f'{params.Z_MAX} mm')   # Z_Max
    ss.set('G1', f'{params.CAM_KALINLIGI} mm')  # Cam kalınlığı
    ss.set('H1', f'{params.KESIM_BASINCI} MPa') # Kesim basıncı
    
    ss.Label = 'Variables'
    
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
    # X (gantry) -> FreeCAD Z, Y (araba) -> FreeCAD X, Z (kafa) -> FreeCAD Y
    doc.Portal_Bridge.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Portal_Left_Support.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Portal_Right_Support.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Motor_X_Left.setExpression('Placement.Base.z', 'Variables.A1')
    doc.Motor_X_Right.setExpression('Placement.Base.z', 'Variables.A1')
    
    # Y ekseni araci portal ile birlikte X hareketini takip eder, kendi stroku FreeCAD X'tedir
    doc.Y_Carriage.setExpression('Placement.Base.x', '150 mm + Variables.B1')
    doc.Y_Carriage.setExpression('Placement.Base.z', '150 mm + Variables.A1')
    doc.Motor_Y.setExpression('Placement.Base.x', 'Y_Carriage.Placement.Base.x - 50 mm')
    doc.Motor_Y.setExpression('Placement.Base.y', 'Y_Carriage.Placement.Base.y - 50 mm')
    doc.Motor_Y.setExpression('Placement.Base.z', 'Y_Carriage.Placement.Base.z + 100 mm')
    
    # Z ekseni kafasi Y arabasini X/Z duzleminde takip eder, dikey strok FreeCAD Y'dedir
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
    
    # Kablo tanklari ana eksenlerle birlikte konum gunceller
    doc.Cable_Track_X.setExpression('Placement.Base.z', 'Variables.A1 / 6')
    doc.Cable_Track_Y.setExpression('Placement.Base.x', 'Y_Carriage.Placement.Base.x')
    doc.Cable_Track_Y.setExpression('Placement.Base.z', 'Y_Carriage.Placement.Base.z + 100 mm')


# =============================================================================
# YARDIMCI KONTROL FONKSIYONLARI
# =============================================================================

def _clamp(value, min_value, max_value):
    return max(min_value, min(max_value, value))


def set_axis_positions(doc, x=None, y=None, z=None):
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

    doc.recompute()
    return ss


# =============================================================================
# TAM MAKİNE SİMÜLASYONU
# =============================================================================

def run_machine_simulation(doc, params, duration_sec=30):
    """
    Tam makine koordineli hareket simülasyonu
    
    Args:
        doc: FreeCAD document
        params: MachineParameters objesi
        duration_sec: Simülasyon süresi (saniye)
    """
    print("=" * 60)
    print("TAM MAKİNE SİMÜLASYONU BAŞLATILIYOR")
    print("=" * 60)
    
    # Spreadsheet'i al
    ss = doc.getObject("Variables")
    
    # Parçaları bul (hata toleranslı)
    cutting_wheel = doc.getObject("Cutting_Wheel")
    if cutting_wheel is None:
        print("HATA: Cutting_Wheel bulunamadı!")
        return
    
    # Simülasyon adımları
    steps = 100
    step_time = duration_sec / steps
    
    print(f"Simülasyon: {steps} adım, {step_time:.2f}s/adım")
    print(f"Toplam süre: {duration_sec}s")
    print("-" * 60)
    
    # Kesim yolu (dikdörtgen)
    path = [
        # Köşe 1: Başlangıç
        (0, 0, 300),
        # Köşe 2: X+ hareket
        (1000, 0, 300),
        # Köşe 3: Y+ hareket (kesim başlar)
        (1000, 500, 284),  # 16mm cam için
        # Köşe 4: X- hareket
        (0, 500, 284),
        # Köşe 5: Y- hareket (kesim biter)
        (0, 0, 300),
        # Köşe 6: Başlangıca dönüş
        (0, 0, 300),
    ]
    
    for step in range(steps + 1):
        progress = step / steps
        path_progress = progress * (len(path) - 1)
        segment = int(path_progress)
        segment_t = path_progress - segment
        
        if segment < len(path) - 1:
            x1, y1, z1 = path[segment]
            x2, y2, z2 = path[segment + 1]
            
            x_pos = x1 + (x2 - x1) * segment_t
            y_pos = y1 + (y2 - y1) * segment_t
            z_pos = z1 + (z2 - z1) * segment_t
        else:
            x_pos, y_pos, z_pos = path[-1]
        
        # Eksenleri hareket ettir (Spreadsheet hücrelerini birimli string olarak güncelle)
        ss.set('A1', f'{x_pos} mm')
        ss.set('B1', f'{y_pos} mm')
        ss.set('C1', f'{params.Z_HOME - z_pos} mm')  # Z ters yönde
        
        # Kesim tekeri rotasyonu (hata toleranslı)
        try:
            wheel_rotation = progress * 720  # 2 tam tur
            cutting_wheel.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), wheel_rotation)
        except Exception as e:
            print(f"Teker rotasyon hatası: {e}")
        
        doc.recompute()
        
        # Durum bilgisi (her 10 adımda)
        if step % 10 == 0:
            print(f"Adım {step}/{steps} | X: {x_pos:6.0f}mm | Y: {y_pos:6.0f}mm | Z: {z_pos:6.0f}mm")
        
        time.sleep(step_time * 0.05)  # Hızlandırılmış
    
    print("-" * 60)
    print("TAM MAKİNE SİMÜLASYONU TAMAMLANDI")
    print("=" * 60)


# =============================================================================
# ANA MONTAJ FONKSİYONU
# =============================================================================

def create_complete_machine():
    """
    Tam CNC makinesi montajını oluştur
    """
    print("=" * 60)
    print("LiSEC GFB-60/30RE - TAM MAKİNE MONTAJI")
    print("=" * 60)
    
    # Parametreler
    params = MachineParameters()
    
    # Document oluştur
    doc_name = "GFB_60_30RE_Complete"
    if App.ActiveDocument and App.ActiveDocument.Name != doc_name:
        App.closeDocument(App.ActiveDocument.Name)
    
    doc = App.newDocument(doc_name)
    doc.Label = "GFB-60/30RE Tam Makine"
    print(f"Document: {doc.Label}")
    
    # Parçaları oluştur
    print("\nParçalar oluşturuluyor...")
    frame = create_frame_assembly(doc)
    portal = create_portal_assembly(doc, frame)
    y_axis = create_y_axis_assembly(doc, portal)
    z_axis = create_z_axis_assembly(doc, y_axis)
    cables = create_cable_tracks(doc, params)
    
    # Değişken tablosu
    print("\nDeğişken tablosu oluşturuluyor...")
    ss = create_variables_spreadsheet(doc, params)
    
    # Kinematik bağlantılar
    print("\nKinematik bağlantılar kuruluyor...")
    setup_kinematics(doc, params)
    
    # Güncelle
    doc.recompute()
    
    if Gui and Gui.ActiveDocument:
        Gui.SendMsgToActiveView("ViewFit")
    
    print("\n" + "=" * 60)
    print("TAM MAKİNE MONTAJI TAMAMLANDI!")
    print("=" * 60)
    print("\nSİMÜLASYON İÇİN:")
    print("  run_machine_simulation(App.ActiveDocument, MachineParameters())")
    print("\nMANUEL HAREKET İÇİN:")
    print("  set_axis_positions(App.ActiveDocument, x=1000, y=500, z=150)")
    print("=" * 60)
    
    return doc


# =============================================================================
# KOMUT SATIRI ÇALIŞTIRMA
# =============================================================================

if __name__ == "__main__":
    doc = create_complete_machine()
    params = MachineParameters()
    run_machine_simulation(doc, params, duration_sec=20)
