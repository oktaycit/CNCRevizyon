# FreeCAD Assembly4 - Tam Montaj ve Simülasyon
# CNC Revizyon Projesi - GFB-60/30RE
# Assembly4 Workbench için LCS Hizalama, Constraint ve Simülasyon

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly"

STEP_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP")

# Makine Parametreleri
MACHINE_LENGTH = 6000  # X ekseni
MACHINE_WIDTH = 3000   # Y ekseni
MACHINE_HEIGHT = 800   # Şase yüksekliği

# ============================================================================
# BÖLÜM 1: ASSEMBLY4 DOKÜMAN VE MODEL HİYERARŞİSİ
# ============================================================================

def create_assembly4_model_structure(doc):
    """
    Assembly4 Model Hiyerarşisi Oluştur
    
    Assembly4 workbench, PartDesign::Body ve Model hiyerarşisi kullanır.
    """
    print("\n" + "="*60)
    print("ADIM 1: Assembly4 Model Hiyerarşisi Oluşturuluyor")
    print("="*60)
    
    # Ana Model klasörü
    model = doc.addObject("App::DocumentObjectGroup", "Model")
    model.Label = "Model"
    
    # Alt montajlar
    x_axis_group = doc.addObject("App::DocumentObjectGroup", "X_Axis")
    x_axis_group.Label = "X Ekseni"
    model.addObject(x_axis_group)
    
    y_axis_group = doc.addObject("App::DocumentObjectGroup", "Y_Axis")
    y_axis_group.Label = "Y Ekseni"
    model.addObject(y_axis_group)
    
    z_axis_group = doc.addObject("App::DocumentObjectGroup", "Z_Axis")
    z_axis_group.Label = "Z Ekseni"
    model.addObject(z_axis_group)
    
    frame_group = doc.addObject("App::DocumentObjectGroup", "Frame")
    frame_group.Label = "Şase"
    model.addObject(frame_group)
    
    electronics_group = doc.addObject("App::DocumentObjectGroup", "Electronics")
    electronics_group.Label = "Elektronik"
    model.addObject(electronics_group)
    
    doc.recompute()
    print("✓ Model hiyerarşisi oluşturuldu")
    return model, x_axis_group, y_axis_group, z_axis_group, frame_group, electronics_group

# ============================================================================
# BÖLÜM 2: DEĞİŞKEN TABLOSU (SPREADSHEET)
# ============================================================================

def create_variable_table(doc):
    """
    Assembly4 Değişken Tablosu Oluştur
    
    Assembly4, parametreleri Spreadsheet ile yönetir.
    """
    print("\n" + "="*60)
    print("ADIM 2: Değişken Tablosu Oluşturuluyor")
    print("="*60)
    
    spread = doc.addObject("Spreadsheet::Sheet", "Variables")
    spread.Label = "Assembly_Variables"
    
    # Başlıklar
    spread.set("A1", "Parametre")
    spread.set("B1", "Değer")
    spread.set("C1", "Birim")
    
    variables = {
        "A0_Machine_Length": MACHINE_LENGTH,
        "A0_Machine_Width": MACHINE_WIDTH,
        "A0_Machine_Height": MACHINE_HEIGHT,
        "A0_Profile_Size": 80,
        "A0_Profile_Thickness": 4,
        "A0_X_Rail_Length": MACHINE_LENGTH,
        "A0_Y_Rail_Length": MACHINE_WIDTH - 200,
        "A0_Z_Travel": 300,
        "A0_X_Speed": 500,
        "A0_Y_Speed": 400,
        "A0_Z_Speed": 300,
        "A0_X_Home": 0,
        "A0_Y_Home": 0,
        "A0_Z_Home": 0,
    }
    
    row = 2
    for name, value in variables.items():
        spread.set(f"A{row}", name)
        spread.set(f"B{row}", str(value))
        spread.set(f"C{row}", "mm" if "Speed" not in name else "mm/s")
        row += 1
    
    doc.recompute()
    print("✓ Değişken tablosu oluşturuldu")
    print(f"  Toplam parametre: {len(variables)}")
    return spread

# ============================================================================
# BÖLÜM 3: LCS (LOCAL COORDINATE SYSTEM) OLUŞTURMA
# ============================================================================

def create_lcs(doc, name, position=(0, 0, 0), rotation=(0, 0, 0), parent=None):
    """
    Assembly4 LCS (Local Coordinate System) Oluştur
    
    LCS'ler parçaların hizalanması için referans noktalarıdır.
    
    Args:
        name: LCS adı
        position: (x, y, z) pozisyon
        rotation: (rx, ry, rz) Euler açıları (derece)
        parent: Üst obje (isteğe bağlı)
    """
    lcs = doc.addObject("PartDesign::CoordinateSystem", name)
    lcs.Label = name
    
    placement = App.Placement(
        App.Vector(position[0], position[1], position[2]),
        App.Rotation(rotation[0], rotation[1], rotation[2])
    )
    lcs.Placement = placement
    
    if parent:
        parent.addObject(lcs)
    
    doc.recompute()
    return lcs

def create_all_lcs_positions(doc, model_group):
    """
    Tüm eksenler için LCS pozisyonları oluştur
    """
    print("\n" + "="*60)
    print("ADIM 3: LCS (Koordinat Sistemleri) Oluşturuluyor")
    print("="*60)
    
    # Şase LCS'leri
    frame_lcs = doc.addObject("App::DocumentObjectGroup", "LCS_Frame")
    frame_lcs.Label = "Şase LCS"
    model_group.addObject(frame_lcs)
    
    lcs_frame_positions = [
        ("LCS_Frame_Origin", (0, 0, 0)),
        ("LCS_Frame_Center", (MACHINE_LENGTH/2, MACHINE_WIDTH/2, 0)),
        ("LCS_Frame_Corner_FL", (0, 0, 0)),
        ("LCS_Frame_Corner_FR", (MACHINE_LENGTH, 0, 0)),
        ("LCS_Frame_Corner_RL", (0, MACHINE_WIDTH, 0)),
        ("LCS_Frame_Corner_RR", (MACHINE_LENGTH, MACHINE_WIDTH, 0)),
        ("LCS_Leg_FL", (0, 0, -MACHINE_HEIGHT)),
        ("LCS_Leg_FR", (MACHINE_LENGTH, 0, -MACHINE_HEIGHT)),
        ("LCS_Leg_RL", (0, MACHINE_WIDTH, -MACHINE_HEIGHT)),
        ("LCS_Leg_RR", (MACHINE_LENGTH, MACHINE_WIDTH, -MACHINE_HEIGHT)),
    ]
    
    for name, pos in lcs_frame_positions:
        create_lcs(doc, name, pos, parent=frame_lcs)
    print(f"  ✓ Şase LCS'leri: {len(lcs_frame_positions)} adet")
    
    # X Ekseni LCS'leri
    x_lcs = doc.addObject("App::DocumentObjectGroup", "LCS_X_Axis")
    x_lcs.Label = "X Ekseni LCS"
    model_group.addObject(x_lcs)
    
    lcs_x_positions = [
        ("LCS_X_Rail_Left", (100, 0, 0)),
        ("LCS_X_Rail_Right", (MACHINE_WIDTH - 100, 0, 0)),
        ("LCS_X_Motor", (MACHINE_LENGTH - 200, 100, 50)),
        ("LCS_X_Block_Front_Left", (100, 40, 500)),
        ("LCS_X_Block_Front_Right", (MACHINE_WIDTH - 100, 40, 500)),
        ("LCS_X_Block_Rear_Left", (100, 40, MACHINE_LENGTH - 500)),
        ("LCS_X_Block_Rear_Right", (MACHINE_WIDTH - 100, 40, MACHINE_LENGTH - 500)),
        ("LCS_X_Gantry", (MACHINE_LENGTH/2, MACHINE_WIDTH/2, 400)),
    ]
    
    for name, pos in lcs_x_positions:
        create_lcs(doc, name, pos, parent=x_lcs)
    print(f"  ✓ X Ekseni LCS'leri: {len(lcs_x_positions)} adet")
    
    # Y Ekseni LCS'leri
    y_lcs = doc.addObject("App::DocumentObjectGroup", "LCS_Y_Axis")
    y_lcs.Label = "Y Ekseni LCS"
    model_group.addObject(y_lcs)
    
    lcs_y_positions = [
        ("LCS_Y_Rail", (MACHINE_LENGTH/2, 400, MACHINE_WIDTH/2)),
        ("LCS_Y_Rail_Start", (MACHINE_LENGTH/2, 400, 100)),
        ("LCS_Y_Rail_End", (MACHINE_LENGTH/2, 400, MACHINE_WIDTH - 100)),
        ("LCS_Y_Motor", (MACHINE_LENGTH - 200, 450, 100)),
        ("LCS_Y_Block_1", (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2 - 100)),
        ("LCS_Y_Block_2", (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2 + 100)),
        ("LCS_Y_Gantry", (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2)),
    ]
    
    for name, pos in lcs_y_positions:
        create_lcs(doc, name, pos, parent=y_lcs)
    print(f"  ✓ Y Ekseni LCS'leri: {len(lcs_y_positions)} adet")
    
    # Z Ekseni LCS'leri
    z_lcs = doc.addObject("App::DocumentObjectGroup", "LCS_Z_Axis")
    z_lcs.Label = "Z Ekseni LCS"
    model_group.addObject(z_lcs)
    
    lcs_z_positions = [
        ("LCS_Z_Motor", (MACHINE_LENGTH/2, 500, MACHINE_WIDTH - 100)),
        ("LCS_Z_Housing", (MACHINE_LENGTH/2 - 75, 300, MACHINE_WIDTH - 180)),
        ("LCS_Z_Wheel", (MACHINE_LENGTH/2, 250, MACHINE_WIDTH - 50)),
        ("LCS_Z_Top", (MACHINE_LENGTH/2, 300, MACHINE_WIDTH)),
        ("LCS_Z_Bottom", (MACHINE_LENGTH/2, 300, MACHINE_WIDTH - 300)),
    ]
    
    for name, pos in lcs_z_positions:
        create_lcs(doc, name, pos, parent=z_lcs)
    print(f"  ✓ Z Ekseni LCS'leri: {len(lcs_z_positions)} adet")
    
    doc.recompute()
    total_lcs = len(lcs_frame_positions) + len(lcs_x_positions) + len(lcs_y_positions) + len(lcs_z_positions)
    print(f"\n✓ Toplam LCS oluşturuldu: {total_lcs}")
    return frame_lcs, x_lcs, y_lcs, z_lcs

# ============================================================================
# BÖLÜM 4: PARÇALARI LCS'LERE GÖRE HİZALAMA
# ============================================================================

def align_part_to_lcs(doc, part_obj, lcs_obj, alignment_type="coincident"):
    """
    Parçayı LCS'ye göre hizala
    
    Assembly4'te parçalar LCS'lere "Expression" kullanarak bağlanır.
    
    Args:
        doc: Doküman
        part_obj: Hizalanacak parça
        lcs_obj: Referans LCS
        alignment_type: Hizalama tipi ("coincident", "offset", "angle")
    """
    # Parçanın Placement'ını LCS'nin Placement'ına bağla
    # Assembly4'te bu genellikle Expression ile yapılır
    
    expression = f"<<{lcs_obj.Name}>>.Placement"
    
    if hasattr(part_obj, "Placement"):
        part_obj.setExpression("Placement", expression)
    
    doc.recompute()
    print(f"  → {part_obj.Label} → {lcs_obj.Label} hizalandı")
    return part_obj

def create_linked_part(doc, name, lcs_name, position_offset=(0, 0, 0)):
    """
    LCS'ye bağlı parça oluştur
    
    Bu fonksiyon, parçanın LCS'ye göre pozisyonunu Expression ile bağlar.
    """
    # Basit bir kutu parçası oluştur (temsili)
    part = doc.addObject("Part::Feature", name)
    part.Label = name
    part.Shape = Part.makeBox(50, 50, 50)
    
    # LCS'ye bağla
    if lcs_name in doc.Objects:
        lcs = doc.getObject(lcs_name)
        expression = f"<<{lcs_name}>>.Placement"
        part.setExpression("Placement", expression)
    
    doc.recompute()
    return part

# ============================================================================
# BÖLÜM 5: CONSTRAINT TANIMLAMALARI
# ============================================================================

def create_fixed_constraint(doc, name, part1, part2=None):
    """
    FIXED Constraint Oluştur
    
    Sabit bağlantı - parçalar birbirine göre hareket edemez.
    
    Args:
        name: Constraint adı
        part1: Birinci parça
        part2: İkinci parça (opsiyonel, None ise sabitlenmiş)
    """
    print(f"\n  → Fixed Constraint: {name}")
    
    constraint = doc.addObject("App::FeaturePython", name)
    constraint.Label = name
    constraint.addProperty("App::PropertyLink", "Parent", "Constraint").Parent = part1
    
    if part2:
        constraint.addProperty("App::PropertyLink", "Target", "Constraint").Target = part2
    
    # Constraint tipini işaretle
    constraint.addProperty("App::PropertyEnumeration", "ConstraintType", "Constraint")
    constraint.ConstraintType = ["Fixed", "Coincident", "Parallel", "Perpendicular", "Angle", "Distance"]
    constraint.ConstraintType = "Fixed"
    
    doc.recompute()
    return constraint

def create_slider_constraint(doc, name, part, direction=(1, 0, 0), min_limit=0, max_limit=1000):
    """
    SLIDER Constraint Oluştur
    
    Lineer hareket - parça bir eksen boyunca hareket edebilir.
    
    Args:
        name: Constraint adı
        part: Hareketli parça
        direction: Hareket yönü vektörü (örn: (1,0,0) = X ekseni)
        min_limit: Minimum pozisyon
        max_limit: Maksimum pozisyon
    """
    print(f"\n  → Slider Constraint: {name}")
    
    constraint = doc.addObject("App::FeaturePython", name)
    constraint.Label = name
    constraint.addProperty("App::PropertyLink", "Parent", "Constraint").Parent = part
    
    # Hareket yönü
    constraint.addProperty("App::PropertyVector", "Direction", "Constraint")
    constraint.Direction = App.Vector(direction)
    
    # Limitler
    constraint.addProperty("App::PropertyFloat", "MinLimit", "Constraint")
    constraint.addProperty("App::PropertyFloat", "MaxLimit", "Constraint")
    constraint.addProperty("App::PropertyFloat", "CurrentPosition", "Constraint")
    
    constraint.MinLimit = min_limit
    constraint.MaxLimit = max_limit
    constraint.CurrentPosition = (min_limit + max_limit) / 2
    
    # Constraint tipi
    constraint.addProperty("App::PropertyEnumeration", "ConstraintType", "Constraint")
    constraint.ConstraintType = ["Fixed", "Slider", "Rotator", "Custom"]
    constraint.ConstraintType = "Slider"
    
    doc.recompute()
    return constraint

def create_rotator_constraint(doc, name, part, axis=(0, 0, 1), min_angle=0, max_angle=360):
    """
    ROTATOR Constraint Oluştur
    
    Döner hareket - parça bir eksen etrafında dönebilir.
    
    Args:
        name: Constraint adı
        part: Dönebilen parça
        axis: Dönme ekseni
        min_angle: Minimum açı (derece)
        max_angle: Maksimum açı (derece)
    """
    print(f"\n  → Rotator Constraint: {name}")
    
    constraint = doc.addObject("App::FeaturePython", name)
    constraint.Label = name
    constraint.addProperty("App::PropertyLink", "Parent", "Constraint").Parent = part
    
    # Dönme ekseni
    constraint.addProperty("App::PropertyVector", "Axis", "Constraint")
    constraint.Axis = App.Vector(axis)
    
    # Açı limitleri
    constraint.addProperty("App::PropertyAngle", "MinAngle", "Constraint")
    constraint.addProperty("App::PropertyAngle", "MaxAngle", "Constraint")
    constraint.addProperty("App::PropertyAngle", "CurrentAngle", "Constraint")
    
    constraint.MinAngle = min_angle
    constraint.MaxAngle = max_angle
    constraint.CurrentAngle = (min_angle + max_angle) / 2
    
    # Constraint tipi
    constraint.addProperty("App::PropertyEnumeration", "ConstraintType", "Constraint")
    constraint.ConstraintType = ["Fixed", "Slider", "Rotator", "Custom"]
    constraint.ConstraintType = "Rotator"
    
    doc.recompute()
    return constraint

def create_all_constraints(doc, model_group):
    """
    Tüm montaj için constraint'leri oluştur
    """
    print("\n" + "="*60)
    print("ADIM 4: Constraint Tanımlamaları")
    print("="*60)
    
    constraints_group = doc.addObject("App::DocumentObjectGroup", "Constraints")
    constraints_group.Label = "Montaj_Constraintleri"
    model_group.addObject(constraints_group)
    
    # Şase parçaları - FIXED (sabit)
    print("\n--- Şase Constraint'leri (Fixed) ---")
    fixed_frame = create_fixed_constraint(doc, "Fixed_Frame_Base", doc.getObject("Main_Frame"))
    constraints_group.addObject(fixed_frame)
    
    # X Ekseni - SLIDER (lineer hareket)
    print("\n--- X Ekseni Constraint'leri (Slider) ---")
    slider_x = create_slider_constraint(
        doc, "Slider_X_Gantry", 
        doc.getObject("X_Gantry") if doc.getObject("X_Gantry") else doc.Objects[0],
        direction=(1, 0, 0),  # X ekseni boyunca
        min_limit=0,
        max_limit=MACHINE_LENGTH
    )
    constraints_group.addObject(slider_x)
    
    # Y Ekseni - SLIDER (lineer hareket)
    print("\n--- Y Ekseni Constraint'leri (Slider) ---")
    slider_y = create_slider_constraint(
        doc, "Slider_Y_Carriage",
        doc.getObject("Y_Carriage") if doc.getObject("Y_Carriage") else doc.Objects[0],
        direction=(0, 0, 1),  # Z ekseni boyunca (portal üzerinde)
        min_limit=100,
        max_limit=MACHINE_WIDTH - 100
    )
    constraints_group.addObject(slider_y)
    
    # Z Ekseni - SLIDER (lineer hareket)
    print("\n--- Z Ekseni Constraint'leri (Slider) ---")
    slider_z = create_slider_constraint(
        doc, "Slider_Z_Head",
        doc.getObject("Z_Head") if doc.getObject("Z_Head") else doc.Objects[0],
        direction=(0, 1, 0),  # Y ekseni boyunca (dikey)
        min_limit=0,
        max_limit=300
    )
    constraints_group.addObject(slider_z)
    
    # Motorlar - FIXED (sabit montaj)
    print("\n--- Motor Constraint'leri (Fixed) ---")
    fixed_motor_x = create_fixed_constraint(doc, "Fixed_Motor_X", doc.getObject("Motor_X_4_5kW") if doc.getObject("Motor_X_4_5kW") else doc.Objects[0])
    constraints_group.addObject(fixed_motor_x)
    
    doc.recompute()
    print(f"\n✓ Toplam constraint oluşturuldu")
    return constraints_group

# ============================================================================
# BÖLÜM 6: SİMÜLASYON / ANİMASYON SETUP
# ============================================================================

def create_animation_table(doc):
    """
    Assembly4 Animation Table Oluştur
    
    Hareket simülasyonu için zaman-pozisyon tablosu
    """
    print("\n" + "="*60)
    print("ADIM 5: Animasyon Tablosu Oluşturuluyor")
    print("="*60)
    
    animation = doc.addObject("Spreadsheet::Sheet", "Animation")
    animation.Label = "Motion_Simulation"
    
    # Başlıklar
    headers = ["Zaman (s)", "X Pozisyon (mm)", "Y Pozisyon (mm)", "Z Pozisyon (mm)"]
    for col, header in enumerate(headers):
        cell = chr(ord('A') + col) + "1"
        animation.set(cell, header)
    
    # Simülasyon adımları (0-10 saniye)
    duration = 10
    steps = 20
    step_time = duration / steps
    
    for i in range(steps + 1):
        row = i + 2
        time = i * step_time
        
        # Sinüs dalgası hareketi
        x_pos = (MACHINE_LENGTH / 2) + (MACHINE_LENGTH / 3) * math.sin(2 * math.pi * time / duration)
        y_pos = (MACHINE_WIDTH / 2) + (MACHINE_WIDTH / 3) * math.cos(2 * math.pi * time / duration)
        z_pos = 150 + 100 * math.sin(4 * math.pi * time / duration)
        
        animation.set(f"A{row}", str(round(time, 1)))
        animation.set(f"B{row}", str(round(x_pos, 2)))
        animation.set(f"C{row}", str(round(y_pos, 2)))
        animation.set(f"D{row}", str(round(z_pos, 2)))
    
    doc.recompute()
    print(f"✓ Animasyon tablosu oluşturuldu ({steps + 1} adım)")
    return animation

def create_simulation_group(doc, model_group):
    """
    Simülasyon grubu oluştur
    """
    print("\n" + "="*60)
    print("ADIM 6: Simülasyon Grubu Oluşturuluyor")
    print("="*60)
    
    simulation = doc.addObject("App::DocumentObjectGroup", "Simulation")
    simulation.Label = "Simülasyon"
    model_group.addObject(simulation)
    
    # X Ekseni Hareketi
    x_motion = doc.addObject("App::FeaturePython", "X_Axis_Motion")
    x_motion.Label = "X_Ekseni_Hareketi"
    x_motion.addProperty("App::PropertyFloat", "Start").Start = 0
    x_motion.addProperty("App::PropertyFloat", "End").End = MACHINE_LENGTH
    x_motion.addProperty("App::PropertyFloat", "Duration").Duration = 10.0
    x_motion.addProperty("App::PropertyBool", "Enabled").Enabled = True
    simulation.addObject(x_motion)
    
    # Y Ekseni Hareketi
    y_motion = doc.addObject("App::FeaturePython", "Y_Axis_Motion")
    y_motion.Label = "Y_Ekseni_Hareketi"
    y_motion.addProperty("App::PropertyFloat", "Start").Start = 0
    y_motion.addProperty("App::PropertyFloat", "End").End = MACHINE_WIDTH
    y_motion.addProperty("App::PropertyFloat", "Duration").Duration = 8.0
    y_motion.addProperty("App::PropertyBool", "Enabled").Enabled = True
    simulation.addObject(y_motion)
    
    # Z Ekseni Hareketi
    z_motion = doc.addObject("App::FeaturePython", "Z_Axis_Motion")
    z_motion.Label = "Z_Ekseni_Hareketi"
    z_motion.addProperty("App::PropertyFloat", "Start").Start = 0
    z_motion.addProperty("App::PropertyFloat", "End").End = 300
    z_motion.addProperty("App::PropertyFloat", "Duration").Duration = 5.0
    z_motion.addProperty("App::PropertyBool", "Enabled").Enabled = True
    simulation.addObject(z_motion)
    
    doc.recompute()
    print("✓ Simülasyon grubu oluşturuldu")
    print("  - X Ekseni: 0 - 6000 mm (10 saniye)")
    print("  - Y Ekseni: 0 - 3000 mm (8 saniye)")
    print("  - Z Ekseni: 0 - 300 mm (5 saniye)")
    return simulation

# ============================================================================
# BÖLÜM 7: MONTAJ TALİMATLARI
# ============================================================================

def create_assembly_instructions(doc):
    """
    Montaj talimatları oluştur (Spreadsheet)
    """
    print("\n" + "="*60)
    print("ADIM 7: Montaj Talimatları Oluşturuluyor")
    print("="*60)
    
    spread = doc.addObject("Spreadsheet::Sheet", "Assembly_Instructions")
    spread.Label = "Montaj_Talimatlari"
    
    instructions = [
        ("", "GFB-60/30RE CNC Cam Kesme Makinesi"),
        ("", "Assembly4 Montaj ve Hizalama Talimatları"),
        ("", ""),
        ("ADIM 1:", "Assembly4 Workbench'e geçin"),
        ("", "View → Workbench → Assembly4"),
        ("", ""),
        ("ADIM 2:", "Parçaları Import Edin"),
        ("2.1", "File → Import → STEP ile STEP dosyalarını yükleyin"),
        ("2.2", "07_Exports/STEP/ dizinindeki dosyaları kullanın"),
        ("", ""),
        ("ADIM 3:", "Parçaları LCS'lere Göre Hizalayın"),
        ("3.1", "Model ağacında parçayı seçin"),
        ("3.2", "Assembly → Place Part menüsüne gidin"),
        ("3.3", "Hedef LCS'yi seçin (örn: LCS_X_Rail_Left)"),
        ("3.4", "Attachment modunu 'Coincident' olarak ayarlayın"),
        ("3.5", "OK butonuna tıklayın"),
        ("", ""),
        ("ADIM 4:", "Constraint'leri Tanımlayın"),
        ("4.1 FIXED (Sabit Bağlantılar):", ""),
        ("", "  - Şase parçaları → Fixed_Frame_Base"),
        ("", "  - Motorlar → Fixed_Motor_X/Y/Z"),
        ("4.2 SLIDER (Lineer Hareket):", ""),
        ("", "  - X Ekseni Portal → Slider_X_Gantry (0-6000mm)"),
        ("", "  - Y Ekseni Taşıyıcı → Slider_Y_Carriage (0-3000mm)"),
        ("", "  - Z Ekseni Kafa → Slider_Z_Head (0-300mm)"),
        ("", ""),
        ("ADIM 5:", "Simülasyon Yapın"),
        ("5.1", "Assembly → Animation menüsüne gidin"),
        ("5.2", "Animation Table'ı seçin"),
        ("5.3", "Play butonuna basarak simülasyonu başlatın"),
        ("5.4", "Hız ayarını Time Scale ile değiştirin"),
        ("", ""),
        ("ADIM 6:", "Kontrol ve Export"),
        ("6.1", "Tüm constraint'leri kontrol edin"),
        ("6.2", "Çakışma analizi yapın"),
        ("6.3", "Assembly → Export ile STEP/PDF export alın"),
    ]
    
    for row, (col, text) in enumerate(instructions, 1):
        cell = f"A{row}"
        spread.set(cell, col)
        cell = f"B{row}"
        spread.set(cell, text)
    
    doc.recompute()
    print("✓ Montaj talimatları oluşturuldu")
    return spread

# ============================================================================
# BÖLÜM 8: BOM (BILL OF MATERIALS)
# ============================================================================

def create_bom_table(doc):
    """Malzeme listesi (BOM) oluştur"""
    print("\n" + "="*60)
    print("ADIM 8: Malzeme Listesi (BOM) Oluşturuluyor")
    print("="*60)
    
    spread = doc.addObject("Spreadsheet::Sheet", "BOM")
    spread.Label = "Bill_of_Materials"
    
    headers = ["No", "Parça Adı", "Açıklama", "Adet", "Malzeme"]
    for col, header in enumerate(headers):
        cell = chr(ord('A') + col) + "1"
        spread.set(cell, header)
    
    parts = [
        ("001", "Ana Şase Profili", "80x80x4 mm, 6000 mm", "4", "S235JR"),
        ("002", "Enlem Profili", "80x80x4 mm, 3000 mm", "4", "S235JR"),
        ("003", "Destek Ayağı", "100x100x5 mm, ayarlanabilir", "4", "Çelik"),
        ("004", "Lineer Ray X", "HIWIN HGH25CA, 6000 mm", "2", "Çelik"),
        ("005", "Lineer Ray Y", "HIWIN HGH25CA, 3000 mm", "1", "Çelik"),
        ("006", "Kızak", "HIWIN HGH25CA", "6", "Çelik"),
        ("007", "Servo Motor X", "ECMA-L11845, 4.5kW", "1", "Alüminyum"),
        ("008", "Servo Motor Y", "ECMA-E11320, 2.0kW", "1", "Alüminyum"),
        ("009", "Servo Motor Z", "ECMA-C11010, 1.0kW frenli", "1", "Alüminyum"),
        ("010", "Kesim Tekeri", "Ø80 mm, elmas kaplama", "1", "Elmas"),
        ("011", "R1-EC Modül", "EtherCAT servo sürücü", "3", "Plastik"),
        ("012", "Kablo Kanalı", "80x40 mm", "20 m", "Plastik"),
    ]
    
    row = 2
    for part in parts:
        for col, value in enumerate(part):
            cell = chr(ord('A') + col) + str(row)
            spread.set(cell, value)
        row += 1
    
    doc.recompute()
    print("✓ Malzeme listesi (BOM) oluşturuldu")
    return spread

# ============================================================================
# ANA FONKSİYON
# ============================================================================

def run_assembly4_complete():
    """
    Assembly4 Tam Montaj Kurulumunu Çalıştır
    
    Bu fonksiyon:
    1. Assembly4 model hiyerarşisi oluşturur
    2. Değişken tablosu oluşturur
    3. LCS (Koordinat Sistemleri) oluşturur
    4. Parçaları LCS'lere göre hizalar
    5. Constraint'leri tanımlar (Fixed, Slider)
    6. Simülasyon setup'ı yapar
    """
    print("\n" + "="*70)
    print("  FreeCAD Assembly4 - Tam Montaj ve Simülasyon")
    print("  CNC Revizyon Projesi - GFB-60/30RE")
    print("="*70)
    
    # Yeni doküman oluştur
    doc = App.newDocument("GFB-60-30RE_Assembly4")
    doc.Label = "GFB-60/30RE CNC Assembly4"
    
    # Adım 1: Model hiyerarşisi
    model, x_group, y_group, z_group, frame_group, electronics_group = create_assembly4_model_structure(doc)
    
    # Adım 2: Değişken tablosu
    create_variable_table(doc)
    
    # Adım 3: LCS pozisyonları
    frame_lcs, x_lcs, y_lcs, z_lcs = create_all_lcs_positions(doc, model)
    
    # Adım 4: Constraint'ler
    constraints_group = create_all_constraints(doc, model)
    
    # Adım 5: Animasyon tablosu
    create_animation_table(doc)
    
    # Adım 6: Simülasyon grubu
    create_simulation_group(doc, model)
    
    # Adım 7: Montaj talimatları
    create_assembly_instructions(doc)
    
    # Adım 8: BOM tablosu
    create_bom_table(doc)
    
    doc.recompute()
    
    print("\n" + "="*70)
    print("  Assembly4 Kurulumu Tamamlandı!")
    print("="*70)
    print("""
  SONRAKI ADIMLAR:
  
  1. Assembly4 Workbench'e geçin:
     → View → Workbench → Assembly4
  
  2. STEP dosyalarını import edin:
     → File → Import → STEP
     → 07_Exports/STEP/ dizinindeki dosyaları seçin
  
  3. Parçaları LCS'lere göre hizalayın:
     → Model ağacında parçayı seçin
     → Assembly → Place Part
     → Hedef LCS'yi seçin
     → Attachment modunu 'Coincident' yapın
  
  4. Constraint'leri tanımlayın:
     → Assembly → Add Constraint → Fixed (sabit parçalar için)
     → Assembly → Add Constraint → Slider (lineer hareket için)
  
  5. Simülasyon yapın:
     → Assembly → Animation
     → Play butonuna basın
  
  6. Export alın:
     → File → Export → STEP/PDF
  """)
    
    return doc


if __name__ == "__main__":
    run_assembly4_complete()