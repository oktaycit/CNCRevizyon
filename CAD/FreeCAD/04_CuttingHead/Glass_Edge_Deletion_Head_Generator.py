# -*- coding: utf-8 -*-
"""
Glass Edge Deletion Head - LiSEC GFB Style
Cam Kenar Silme / Rodaj Kafası Parametrik Modeli

FreeCAD Python API kullanılarak oluşturuldu.
Tüm geometriler parametrik olarak tanımlanmıştır.

Kullanım:
    1. FreeCAD'i açın
    2. View → Panels → Python Console
    3. Bu script'i kopyalayıp yapıştırın
    4. create_glass_edge_deletion_head() fonksiyonunu çağırın

Yazar: CNC Revizyon Projesi
Tarih: 2026-04-19
"""

import FreeCAD as App
import Part
import math

# =============================================================================
# PARAMETRELER (Değiştirilebilir Değişkenler)
# =============================================================================

# Taşlama Tezgağı Parametreleri
wheel_diameter = 150.0    # mm - Taşlama çarkı çapı
wheel_width = 20.0        # mm - Taşlama çarkı kalınlığı
wheel_grit = 120          # Grain size (belgelendirme için)

# Motor Parametreleri
motor_diameter = 180.0    # mm - Motor gövde çapı
motor_height = 220.0      # mm - Motor yüksekliği
motor_power = 2.2         # kW (belgelendirme için)
motor_rpm = 3000          # dev/dk (belgelendirme için)

# Vakum Koruyucu Parametreleri
shroud_thickness = 8.0    # mm - Koruyucu sac kalınlığı
shroud_radius = 85.0      # mm - Koruyucu yarıçap (tekerlekten biraz büyük)
vacuum_port_diameter = 40 # mm - Toz emiş portu çapı
vacuum_port_length = 100  # mm - Toz emiş borusu uzunluğu

# Taban Plakası Parametreleri
base_length = 200.0       # mm - Taban plakası uzunluğu (X ekseni)
base_width = 150.0        # mm - Taban plakası genişliği (Y ekseni)
base_thickness = 15.0     # mm - Taban plakası kalınlığı

# Ayarlama Mekanizması
offset_angle = 45.0       # derece - Taşlama açısı (cam kenarına göre)
adjustment_travel = 50.0  # mm - Ayarlama stroku

# Renk Tanımları (RGB, 0-1 aralığında)
COLOR_WHEEL = (0.75, 0.70, 0.65)      # Grinding wheel - gri/bej
COLOR_MOTOR = (0.15, 0.15, 0.20)      # Motor housing - koyu gri
COLOR_SHROUD = (0.85, 0.35, 0.10)     # Vacuum shroud - turuncu (güvenlik)
COLOR_BASE = (0.60, 0.60, 0.65)       # Base plate - açık gri
COLOR_GUARD = (0.90, 0.90, 0.90)      # Protective guard - beyaz


# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def create_document(name="GlassEdgeDeletionHead"):
    """Yeni FreeCAD belgesi oluştur veya mevcut olanı temizle"""
    import FreeCAD as App
    
    # Mevcut belgeyi kontrol et (listDocuments() string listesi döner)
    existing_name = None
    for doc_name in App.listDocuments():
        doc = App.getDocument(doc_name)
        if doc and (doc.Label == name or doc.Name == name):
            existing_name = doc_name
            break
    
    if existing_name:
        App.closeDocument(existing_name)
    
    return App.newDocument(name)


def create_group(doc, name):
    """Belge içinde grup oluştur"""
    group = doc.addObject("App::DocumentObjectGroup", name)
    group.Label = name
    return group


def set_color(obj, color):
    """Objeye renk ata"""
    if hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.ShapeColor = color


def set_transparency(obj, transparency=0):
    """Objeye şeffaflık ata"""
    if hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.Transparency = transparency


# =============================================================================
# ANA BİLEŞEN FONKSİYONLARI
# =============================================================================

def create_grinding_wheel(doc, wheel_diameter, wheel_width, position=App.Vector(0, 0, 0)):
    """
    Taşlama çarkı oluştur
    Peripheral grinding wheel - silindirik geometri
    """
    print(f"  - Taşlama çarkı oluşturuluyor (Ø{wheel_diameter}mm x {wheel_width}mm)...")
    
    radius = wheel_diameter / 2.0
    
    # Ana taşlama çarkı
    wheel = Part.makeCylinder(
        radius,           # Radius
        wheel_width,      # Height (thickness)
        App.Vector(0, 0, 0),  # Center
        App.Vector(0, 1, 0)   # Direction (Y ekseni boyunca)
    )
    
    # Merkez mil deliği (motor mili için)
    shaft_hole = Part.makeCylinder(
        12.5,             # Radius (25mm mil için)
        wheel_width + 2,  # Height
        App.Vector(0, 0, 0),
        App.Vector(0, 1, 0)
    )
    
    # Delik ile çarkı birleştir (cut operation)
    wheel = wheel.cut(shaft_hole)
    
    # Flanş bağlantı noktaları (4 adet)
    bolt_positions = [
        (radius * 0.6, 0, radius * 0.6),
        (-radius * 0.6, 0, radius * 0.6),
        (radius * 0.6, 0, -radius * 0.6),
        (-radius * 0.6, 0, -radius * 0.6),
    ]
    
    for pos in bolt_positions:
        bolt_hole = Part.makeCylinder(
            4.5,            # M8 cıvata için
            wheel_width + 4,
            App.Vector(*pos),
            App.Vector(0, 1, 0)
        )
        wheel = wheel.cut(bolt_hole)
    
    # Part Feature olarak belgeye ekle
    wheel_feature = doc.addObject("Part::Feature", "Grinding_Wheel")
    wheel_feature.Shape = wheel
    wheel_feature.Placement.Base = position
    set_color(wheel_feature, COLOR_WHEEL)
    
    return wheel_feature


def create_motor_housing(doc, motor_diameter, motor_height, position=App.Vector(0, 0, 0)):
    """
    Motor gövdesi oluştur
    Dikey silindirik motor housing
    """
    print(f"  - Motor gövdesi oluşturuluyor (Ø{motor_diameter}mm x {motor_height}mm)...")
    
    radius = motor_diameter / 2.0
    
    # Ana motor gövdesi
    housing = Part.makeCylinder(
        radius,
        motor_height,
        App.Vector(0, 0, 0),
        App.Vector(0, 0, 1)  # Dikey (Z ekseni)
    )
    
    # Soğutma kanatları (8 adet)
    cooling_fins = []
    for i in range(8):
        angle = (360.0 / 8.0) * i * math.pi / 180.0
        fin_x = radius * math.cos(angle)
        fin_z = radius * math.sin(angle)
        
        fin = Part.makeBox(
            15,             # Width
            motor_height * 0.7,  # Height
            8               # Thickness
        )
        fin.translate(App.Vector(fin_x - 7.5, 0, fin_z - 4))
        fin.rotate(App.Vector(0, 0, 0), App.Vector(0, 0, 1), angle * 180.0 / math.pi)
        cooling_fins.append(fin)
    
    # Kanatları birleştir
    for fin in cooling_fins:
        housing = housing.fuse(fin)
    
    # Üst kapak
    top_cap = Part.makeCylinder(
        radius + 10,
        15,
        App.Vector(0, 0, motor_height),
        App.Vector(0, 0, 1)
    )
    housing = housing.fuse(top_cap)
    
    # Konektör kutusu
    connector_box = Part.makeBox(
        60, 40, 50,
        App.Vector(-30, radius - 5, motor_height * 0.6)
    )
    housing = housing.fuse(connector_box)
    
    # Part Feature olarak belgeye ekle
    housing_feature = doc.addObject("Part::Feature", "Motor_Housing")
    housing_feature.Shape = housing
    housing_feature.Placement.Base = position
    set_color(housing_feature, COLOR_MOTOR)
    
    return housing_feature


def create_vacuum_shroud(doc, wheel_diameter, shroud_radius, shroud_thickness, 
                         vacuum_port_diameter, vacuum_port_length, 
                         wheel_position=App.Vector(0, 0, 0)):
    """
    Vakum koruyucu oluştur
    Semi-circular protective guard with dust extraction port
    """
    print(f"  - Vakum koruyucu oluşturuluyor (Ø{vacuum_port_diameter}mm port)...")
    
    wheel_radius = wheel_diameter / 2.0
    
    # Yarım daire koruyucu (üst 180 derece)
    shroud_angle = 180.0  # degrees
    
    # Ana koruyucu gövde - silindirik segment
    shroud = Part.makeCylinder(
        shroud_radius,
        wheel_width + 20,  # Tezgahtan biraz geniş
        App.Vector(0, 0, 0),
        App.Vector(0, 1, 0),
        shroud_angle
    )
    
    # İç boşluk (tezgah için clearance)
    inner_clearance = Part.makeCylinder(
        wheel_radius + 15,  # Tezgahtan 15mm boşluk
        wheel_width + 24,
        App.Vector(0, 0, 0),
        App.Vector(0, 1, 0),
        shroud_angle
    )
    
    # İç boşluğu çıkar
    shroud = shroud.cut(inner_clearance)
    
    # Vakum emiş portu (silindirik boru)
    port_radius = vacuum_port_diameter / 2.0
    vacuum_port = Part.makeCylinder(
        port_radius,
        vacuum_port_length,
        App.Vector(0, shroud_radius + vacuum_port_length/2, shroud_radius),  # Üst kısımda
        App.Vector(0, 1, 0)
    )
    
    # Port bağlantı flansı
    port_flange = Part.makeCylinder(
        port_radius + 15,
        10,
        App.Vector(0, shroud_radius, shroud_radius),
        App.Vector(0, 1, 0)
    )
    
    # Port'u koruyucuya birleştir
    shroud = shroud.fuse(vacuum_port)
    shroud = shroud.fuse(port_flange)
    
    # Montaj braketleri (2 adet)
    bracket_positions = [
        (shroud_radius * 0.7, 0, shroud_radius * 0.5),
        (-shroud_radius * 0.7, 0, shroud_radius * 0.5),
    ]
    
    for pos in bracket_positions:
        bracket = Part.makeBox(30, 10, 40)
        bracket.translate(App.Vector(pos[0] - 15, pos[1] - 5, pos[2] - 20))
        shroud = shroud.fuse(bracket)
    
    # Part Feature olarak belgeye ekle
    shroud_feature = doc.addObject("Part::Feature", "Vacuum_Shroud")
    shroud_feature.Shape = shroud
    shroud_feature.Placement.Base = wheel_position
    set_color(shroud_feature, COLOR_SHROUD)
    
    return shroud_feature


def create_base_plate(doc, base_length, base_width, base_thickness, position=App.Vector(0, 0, 0)):
    """
    Taban plakası oluştur
    Rectangular mounting plate
    """
    print(f"  - Taban plakası oluşturuluyor ({base_length}mm x {base_width}mm x {base_thickness}mm)...")
    
    # Ana plaka
    base = Part.makeBox(
        base_length,
        base_width,
        base_thickness,
        App.Vector(-base_length/2, 0, -base_thickness)  # Z=0'da başlasın
    )
    
    # Montaj delikleri (4 köşe)
    hole_positions = [
        (base_length/2 - 15, base_width/2 - 15),
        (base_length/2 - 15, -base_width/2 + 15),
        (-base_length/2 + 15, base_width/2 - 15),
        (-base_length/2 + 15, -base_width/2 + 15),
    ]
    
    for pos in hole_positions:
        hole = Part.makeCylinder(
            5.5,            # M10 cıvata için
            base_thickness + 4,
            App.Vector(pos[0], pos[1], -base_thickness - 2),
            App.Vector(0, 0, 1)
        )
        base = base.cut(hole)
    
    # Motor montaj yüzeyi (yükseltilmiş platform)
    motor_platform = Part.makeCylinder(
        motor_diameter/2 + 20,
        10,
        App.Vector(0, 0, 0),
        App.Vector(0, 0, 1)
    )
    base = base.fuse(motor_platform)
    
    # Ayarlama rayı montaj yüzeyleri
    rail_mount_left = Part.makeBox(
        base_length,
        30,
        8,
        App.Vector(-base_length/2, -base_width/2, -base_thickness + 8)
    )
    rail_mount_right = Part.makeBox(
        base_length,
        30,
        8,
        App.Vector(-base_length/2, base_width/2 - 30, -base_thickness + 8)
    )
    base = base.fuse(rail_mount_left)
    base = base.fuse(rail_mount_right)
    
    # Part Feature olarak belgeye ekle
    base_feature = doc.addObject("Part::Feature", "Base_Plate")
    base_feature.Shape = base
    base_feature.Placement.Base = position
    set_color(base_feature, COLOR_BASE)
    
    return base_feature


def create_adjustment_mechanism(doc, adjustment_travel, base_length, position=App.Vector(0, 0, 0)):
    """
    Ayarlama mekanizması oluştur
    Linear adjustment slide for wheel position
    """
    print(f"  - Ayarlama mekanizması oluşturuluyor ({adjustment_travel}mm strok)...")
    
    # Lineer ray kılavuzu
    guide_rail = Part.makeBox(
        adjustment_travel + 50,
        40,
        20,
        App.Vector(-(adjustment_travel + 50)/2, 0, 0)
    )
    
    # Kayar blok
    slide_block = Part.makeBox(
        80,
        50,
        25,
        App.Vector(-40, 0, 20)
    )
    
    # Ayarlama vidası (leadscrew)
    leadscrew = Part.makeCylinder(
        8,                # M16 leadscrew
        adjustment_travel + 100,
        App.Vector(0, -50, 35),
        App.Vector(0, 1, 0)
    )
    
    # Ayarlama handwheel'i
    handwheel = Part.makeCylinder(
        50,
        20,
        App.Vector(0, adjustment_travel/2 + 60, 35),
        App.Vector(0, 1, 0)
    )
    
    # Handle
    handle = Part.makeBox(
        10,
        80,
        10,
        App.Vector(-5, adjustment_travel/2 + 70, 30)
    )
    
    # Tüm parçaları birleştir
    mechanism = guide_rail.fuse(slide_block)
    mechanism = mechanism.fuse(leadscrew)
    mechanism = mechanism.fuse(handwheel)
    mechanism = mechanism.fuse(handle)
    
    # Part Feature olarak belgeye ekle
    mechanism_feature = doc.addObject("Part::Feature", "Adjustment_Mechanism")
    mechanism_feature.Shape = mechanism
    mechanism_feature.Placement.Base = position
    set_color(mechanism_feature, COLOR_GUARD)
    
    return mechanism_feature


def create_protective_guard(doc, wheel_diameter, position=App.Vector(0, 0, 0)):
    """
    Koruyucu siper oluştur
    Additional safety guard for operator protection
    """
    print("  - Koruyucu siper oluşturuluyor...")
    
    wheel_radius = wheel_diameter / 2.0
    
    # Şeffaf koruyucu panel (polycarbonate temsil)
    guard_panel = Part.makeBox(
        wheel_diameter + 40,
        10,
        wheel_diameter * 0.6,
        App.Vector(-(wheel_diameter + 40)/2, 0, wheel_radius)
    )
    
    # Panel destek braketleri
    bracket_left = Part.makeBox(
        20,
        30,
        wheel_diameter * 0.3,
        App.Vector(-(wheel_diameter/2 + 30), 0, wheel_radius * 0.5)
    )
    bracket_right = Part.makeBox(
        20,
        30,
        wheel_diameter * 0.3,
        App.Vector((wheel_diameter/2 + 10), 0, wheel_radius * 0.5)
    )
    
    guard = guard_panel.fuse(bracket_left)
    guard = guard.fuse(bracket_right)
    
    # Part Feature olarak belgeye ekle
    guard_feature = doc.addObject("Part::Feature", "Protective_Guard")
    guard_feature.Shape = guard
    guard_feature.Placement.Base = position
    set_color(guard_feature, COLOR_GUARD)
    set_transparency(guard_feature, 60)  # Şeffaf
    
    return guard_feature


# =============================================================================
# ANA MONTAJ FONKSİYONU
# =============================================================================

def create_glass_edge_deletion_head():
    """
    Ana fonksiyon - Tüm bileşenleri oluşturur ve monte eder
    
    Montaj Mantığı:
    1. Taban plakası Z=0'da başlar
    2. Taşlama çarkı taban üzerinde, alt kenarı Z=0'da (cam yüzeyi)
    3. Motor dikey olarak üstte
    4. Vakum koruyucu tekerlek etrafında
    5. Ayarlama mekanizması taban altında
    6. Koruyucu siper operatör tarafında
    """
    print("=" * 60)
    print("GLASS EDGE DELETION HEAD - LiSEC GFB STYLE")
    print("=" * 60)
    print(f"\nParametreler:")
    print(f"  Taşlama Çarkı: Ø{wheel_diameter}mm x {wheel_width}mm")
    print(f"  Motor: Ø{motor_diameter}mm x {motor_height}mm, {motor_power}kW")
    print(f"  Vakum Portu: Ø{vacuum_port_diameter}mm")
    print(f"  Taban Plakası: {base_length}mm x {base_width}mm x {base_thickness}mm")
    print(f"  Ayarlama Açısı: {offset_angle}°")
    print()
    
    # Yeni belge oluştur
    doc = create_document("GlassEdgeDeletionHead")
    print("✓ FreeCAD belgesi oluşturuldu\n")
    
    # Gruplar oluştur (ağaç yapısı için)
    assembly_group = create_group(doc, "Edge_Deletion_Assembly")
    motion_group = create_group(doc, "Motion_Components")
    safety_group = create_group(doc, "Safety_Components")
    
    print("Bileşenler oluşturuluyor...\n")
    
    # ==========================================================================
    # 1. TABAN PLAKASI (Base Plate)
    # ==========================================================================
    # Z=0 cam yüzeyi referansı, taban Z<0'da başlar
    base_z = -base_thickness
    base_plate = create_base_plate(
        doc, 
        base_length, 
        base_width, 
        base_thickness,
        position=App.Vector(0, 0, base_z)
    )
    
    # ==========================================================================
    # 2. AYARLAMA MEKANİZMASI (Adjustment Mechanism)
    # ==========================================================================
    adjustment = create_adjustment_mechanism(
        doc,
        adjustment_travel,
        base_length,
        position=App.Vector(0, -base_width/2 - 20, base_z)
    )
    
    # ==========================================================================
    # 3. TAŞLAMA ÇARKI (Grinding Wheel)
    # ==========================================================================
    # ÖNEMLİ: Taşlama çarkının alt kenarı Z=0'da olmalı (cam yüzeyi)
    # Çark merkezi: wheel_radius kadar yukarıda
    wheel_center_z = wheel_diameter / 2.0  # Alt kenar Z=0'da olacak
    wheel_center_y = base_width / 2 - 30   # Taban ortasına yakın
    
    grinding_wheel = create_grinding_wheel(
        doc,
        wheel_diameter,
        wheel_width,
        position=App.Vector(0, wheel_center_y, wheel_center_z)
    )
    
    # Çarkı offset_angle kadar döndür (cam kenarına göre açı)
    grinding_wheel.Placement.Rotation = App.Rotation(
        App.Vector(1, 0, 0),  # X ekseni etrafında
        offset_angle
    )
    
    # ==========================================================================
    # 4. MOTOR GÖVDESİ (Motor Housing)
    # ==========================================================================
    # Motor dikey olarak çarkın üstünde
    motor_z = wheel_center_z + wheel_width + 10  # Çarkın hemen üstü
    
    motor_housing = create_motor_housing(
        doc,
        motor_diameter,
        motor_height,
        position=App.Vector(0, wheel_center_y, motor_z)
    )
    
    # ==========================================================================
    # 5. VAKUM KORUYUCU (Vacuum Shroud)
    # ==========================================================================
    vacuum_shroud = create_vacuum_shroud(
        doc,
        wheel_diameter,
        shroud_radius,
        shroud_thickness,
        vacuum_port_diameter,
        vacuum_port_length,
        position=App.Vector(0, wheel_center_y, wheel_center_z)
    )
    
    # ==========================================================================
    # 6. KORUYUCU SİPER (Protective Guard)
    # ==========================================================================
    # Operatör tarafında, şeffaf polycarbonate
    guard_y = wheel_center_y + base_width/2 + 20  # Ön tarafta
    
    protective_guard = create_protective_guard(
        doc,
        wheel_diameter,
        position=App.Vector(0, guard_y, base_z)
    )
    
    # ==========================================================================
    # GRUPLARA EKLE
    # ==========================================================================
    assembly_group.addObject(base_plate)
    assembly_group.addObject(grinding_wheel)
    assembly_group.addObject(motor_housing)
    assembly_group.addObject(vacuum_shroud)
    
    motion_group.addObject(adjustment)
    
    safety_group.addObject(protective_guard)
    
    # ==========================================================================
    # BELGEYİ GÜNCELLE
    # ==========================================================================
    doc.recompute()
    
    print("\n" + "=" * 60)
    print("✓ TAMAMLANDI - Tüm bileşenler oluşturuldu")
    print("=" * 60)
    print(f"\nOluşturulan Objeler:")
    print(f"  - Base_Plate: Taban plakası")
    print(f"  - Grinding_Wheel: Taşlama çarkı ({offset_angle}° açıyla)")
    print(f"  - Motor_Housing: Motor gövdesi")
    print(f"  - Vacuum_Shroud: Vakum koruyucu (Ø{vacuum_port_diameter}mm port)")
    print(f"  - Adjustment_Mechanism: Ayarlama mekanizması")
    print(f"  - Protective_Guard: Koruyucu siper (şeffaf)")
    print()
    print("Kullanım İpuçları:")
    print(f"  1. Variables spreadsheet'inden offset_angle'ı değiştirerek açıyı ayarlayın")
    print(f"  2. wheel_diameter ve wheel_width parametrelerini değiştirerek tezgağı özelleştirin")
    print(f"  3. View → Fit All (veya 'V' tuşu) ile tüm modeli görün")
    print()
    print("Dışa Aktarma:")
    print(f"  STEP: Part → Export → Edge_Deletion_Assembly.step")
    print(f"  STL: Mesh Design → Create mesh from shape → Export")
    print()
    
    return doc


# =============================================================================
# EK FONKSİYON: DEĞİŞKEN TABLOSU OLUŞTURMA
# =============================================================================

def create_variables_sheet(doc):
    """
    Parametrik kontrol için Variables spreadsheet'i oluştur
    """
    sheet = doc.addObject("Spreadsheet::Sheet", "Variables")
    
    # Değişkenleri yaz
    variables = {
        'A1': ('wheel_diameter', str(wheel_diameter) + ' mm', 'Taşlama çarkı çapı'),
        'A2': ('wheel_width', str(wheel_width) + ' mm', 'Taşlama çarkı kalınlığı'),
        'A3': ('offset_angle', str(offset_angle) + ' deg', 'Taşlama açısı'),
        'A4': ('motor_power', str(motor_power) + ' kW', 'Motor gücü'),
        'A5': ('vacuum_port_dia', str(vacuum_port_diameter) + ' mm', 'Vakum portu çapı'),
    }
    
    for cell, (name, value, comment) in variables.items():
        sheet.set(cell, value)
        sheet.setAlias(cell, name)
        # Comment satırı
        row = int(cell[1:])
        sheet.set(f'C{row}', comment)
    
    doc.recompute()
    return sheet


# =============================================================================
# SCRIPT ÇALIŞTIRMA
# =============================================================================

if __name__ == "__main__":
    # Ana fonksiyonu çalıştır
    doc = create_glass_edge_deletion_head()
    
    # Variables sheet'i oluştur
    create_variables_sheet(doc)
    
    print("✓ Variables spreadsheet'i oluşturuldu")
    print("\nModel hazır! FreeCAD ağaç görünümünden bileşenleri inceleyebilirsiniz.")
