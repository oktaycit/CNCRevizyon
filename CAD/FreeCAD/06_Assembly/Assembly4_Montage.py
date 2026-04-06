# FreeCAD Assembly4 Montaj ve Simülasyon
# CNC Revizyon Projesi - GFB-60/30RE
# Assembly4 Workbench için Montaj Dosyası

import FreeCAD as App
import Part
import math
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly"

# Assembly4 Montaj Parametreleri
MACHINE_LENGTH = 6000
MACHINE_WIDTH = 3000
MACHINE_HEIGHT = 800

def create_box(width, height, depth, position=(0, 0, 0)):
    """Kutu oluştur"""
    return Part.makeBox(width, height, depth, App.Vector(position))

def create_cylinder(radius, height, position=(0, 0, 0)):
    """Silindir oluştur"""
    return Part.makeCylinder(radius, height, App.Vector(position), App.Vector(0, 0, 1))

def create_hollow_profile(size, thickness, length, position=(0, 0, 0)):
    """İçi boş kare profil oluştur"""
    outer = create_box(size, size, length, (-size/2, -size/2, 0))
    inner_size = size - 2 * thickness
    inner = create_box(inner_size, inner_size, length + 2, (-inner_size/2, -inner_size/2, -1))
    hollow = outer.cut(inner)
    moved = hollow.copy()
    moved.translate(App.Vector(position))
    return moved

def setup_assembly4_document():
    """Assembly4 montaj dosyası hazırla"""
    doc = App.newDocument("GFB-60-30RE_Assembly")
    doc.Label = "GFB-60/30RE CNC Assembly"
    
    # Assembly4 varsayılan Body oluştur
    body = doc.addObject("PartDesign::Body", "Body")
    doc.addObject("PartDesign::Feature", "BaseFeature")
    
    # LCS (Local Coordinate System) ekle
    lcs_origin = doc.addObject("PartDesign::CoordinateSystem", "LCS_Origin")
    lcs_origin.MapMode = "Deactivated"
    
    doc.recompute()
    
    print("Assembly4 dokümanı hazırlandı!")
    print("Assembly4 Workbench'e geçin: View → Workbench → Assembly4")
    
    return doc

def create_variable_table(doc):
    """Assembly4 değişken tablosu oluştur"""
    spread = doc.addObject("Spreadsheet::Sheet", "Variables")
    
    variables = {
        "A0_Machine_Length": str(MACHINE_LENGTH),
        "A0_Machine_Width": str(MACHINE_WIDTH),
        "A0_Machine_Height": str(MACHINE_HEIGHT),
        "A0_Profile_Size": "80",
        "A0_Profile_Thickness": "4",
        "A0_X_Rail_Length": str(MACHINE_LENGTH),
        "A0_Y_Rail_Length": str(MACHINE_WIDTH),
        "A0_Z_Travel": "300",
    }
    
    row = 1
    for name, value in variables.items():
        cell = f"A{row}"
        spread.set(cell, name)
        cell = f"B{row}"
        spread.set(cell, f"{value} mm")
        row += 1
    
    spread.Label = "Assembly_Variables"
    doc.recompute()
    
    print("Değişken tablosu oluşturuldu!")
    return spread

def create_lcs(doc, name, position=(0, 0, 0), rotation=(0, 0, 0)):
    """Local Coordinate System oluştur"""
    lcs = doc.addObject("PartDesign::CoordinateSystem", name)
    lcs.Label = name
    
    lcs.Placement = App.Placement(
        App.Vector(position[0], position[1], position[2]),
        App.Rotation(rotation[0], rotation[1], rotation[2])
    )
    
    doc.recompute()
    return lcs

def import_part_from_file(doc, filepath, part_name):
    """Harici dosyadan parça import et"""
    if not os.path.exists(filepath):
        print(f"Uyarı: {filepath} bulunamadı")
        return None
    
    import Import
    shapes = Import.insert(filepath, doc.Name)
    
    if shapes:
        shape = shapes[0]
        shape.Label = part_name
        doc.recompute()
        print(f"  → {part_name} import edildi")
        return shape
    
    return None

def create_x_axis_lcs_positions(doc):
    """X ekseni için LCS pozisyonları oluştur"""
    lcs_positions = [
        ("LCS_X_Rail_Left", (100, 0, 0)),
        ("LCS_X_Rail_Right", (MACHINE_WIDTH - 100, 0, 0)),
        ("LCS_X_Motor", (MACHINE_LENGTH - 200, 100, 50)),
        ("LCS_X_Block_Front_Left", (100, 40, 500)),
        ("LCS_X_Block_Front_Right", (MACHINE_WIDTH - 100, 40, 500)),
        ("LCS_X_Block_Rear_Left", (100, 40, MACHINE_LENGTH - 500)),
        ("LCS_X_Block_Rear_Right", (MACHINE_WIDTH - 100, 40, MACHINE_LENGTH - 500)),
    ]
    
    lcs_list = []
    for name, pos in lcs_positions:
        lcs = create_lcs(doc, name, pos)
        lcs_list.append(lcs)
    
    return lcs_list

def create_y_axis_lcs_positions(doc):
    """Y ekseni için LCS pozisyonları oluştur"""
    lcs_positions = [
        ("LCS_Y_Rail", (MACHINE_LENGTH/2, 400, MACHINE_WIDTH/2)),
        ("LCS_Y_Motor", (MACHINE_LENGTH - 200, 450, 100)),
        ("LCS_Y_Block_1", (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2 - 100)),
        ("LCS_Y_Block_2", (MACHINE_LENGTH/2, 440, MACHINE_WIDTH/2 + 100)),
    ]
    
    lcs_list = []
    for name, pos in lcs_positions:
        lcs = create_lcs(doc, name, pos)
        lcs_list.append(lcs)
    
    return lcs_list

def create_z_axis_lcs_positions(doc):
    """Z ekseni için LCS pozisyonları oluştur"""
    lcs_positions = [
        ("LCS_Z_Motor", (MACHINE_LENGTH/2, 500, MACHINE_WIDTH - 100)),
        ("LCS_Z_Housing", (MACHINE_LENGTH/2 - 75, 300, MACHINE_WIDTH - 180)),
        ("LCS_Z_Wheel", (MACHINE_LENGTH/2, 250, MACHINE_WIDTH - 50)),
    ]
    
    lcs_list = []
    for name, pos in lcs_positions:
        lcs = create_lcs(doc, name, pos)
        lcs_list.append(lcs)
    
    return lcs_list

def create_motion_simulation(doc):
    """Hareket simülasyonu için animation setup"""
    animation = doc.addObject("App::DocumentObjectGroup", "Animation")
    animation.Label = "Motion_Simulation"
    
    x_motion = doc.addObject("App::FeaturePython", "X_Axis_Motion")
    x_motion.addProperty("App::PropertyFloat", "Start").Start = 0
    x_motion.addProperty("App::PropertyFloat", "End").End = MACHINE_LENGTH
    x_motion.addProperty("App::PropertyFloat", "Duration").Duration = 10.0
    x_motion.Label = "X_Axis_Linear_Motion"
    animation.addObject(x_motion)
    
    y_motion = doc.addObject("App::FeaturePython", "Y_Axis_Motion")
    y_motion.addProperty("App::PropertyFloat", "Start").Start = 0
    y_motion.addProperty("App::PropertyFloat", "End").End = MACHINE_WIDTH
    y_motion.addProperty("App::PropertyFloat", "Duration").Duration = 8.0
    y_motion.Label = "Y_Axis_Linear_Motion"
    animation.addObject(y_motion)
    
    z_motion = doc.addObject("App::FeaturePython", "Z_Axis_Motion")
    z_motion.addProperty("App::PropertyFloat", "Start").Start = 0
    z_motion.addProperty("App::PropertyFloat", "End").End = 300
    z_motion.addProperty("App::PropertyFloat", "Duration").Duration = 5.0
    z_motion.Label = "Z_Axis_Linear_Motion"
    animation.addObject(z_motion)
    
    doc.recompute()
    print("Hareket simülasyonu setup'ı oluşturuldu!")
    return animation

def create_assembly_instructions(doc):
    """Montaj talimatları ekle (Spreadsheet olarak)"""
    spread = doc.addObject("Spreadsheet::Sheet", "Assembly_Instructions")
    spread.Label = "Montaj_Talimatlari"
    
    instructions = [
        "GFB-60/30RE CNC Cam Kesme Makinesi",
        "Assembly4 Montaj Talimatlari",
        "",
        "1. SASE MONTAJI",
        "1.1 Ana sase profillerini yerlestirin",
        "1.2 Destek ayaklarini monte edin",
        "1.3 Kose takviyelerini sikin",
        "1.4 Duzgunluk kontrolu yapin",
        "",
        "2. X EKSENI MONTAJI",
        "2.1 Lineer raylari saseye sabitleyin",
        "2.2 Kizaklari raylara takin",
        "2.3 Portal koprulu monte edin",
        "2.4 X ekseni motorunu yerlestirin",
        "2.5 Kaplaj baglantisini yapin",
        "",
        "3. Y EKSENI MONTAJI",
        "3.1 Y ekseni rayini portale monte edin",
        "3.2 Y ekseni kizaklarini takin",
        "3.3 Y ekseni motorunu yerlestirin",
        "3.4 Kaplaj baglantisini yapin",
        "",
        "4. Z EKSENI MONTAJI",
        "4.1 Z ekseni yuvasini monte edin",
        "4.2 Z ekseni motorunu takin",
        "4.3 Kesim tekerini monte edin",
        "4.4 Koruyucu kapagi takin",
        "",
        "5. ELEKTRONIK MONTAJI",
        "5.1 R1-EC modullerini yerlestirin",
        "5.2 Sensorleri monte edin",
        "5.3 Kablo kanallarini doseyin",
        "5.4 Baglantilari yapin",
        "",
        "6. KONTROLLER",
        "6.1 Tum baglantilari kontrol edin",
        "6.2 Hareket testleri yapin",
        "6.3 Acil durdurma testini yapin",
        "6.4 Ilk calistirmayi yapin",
    ]
    
    for row, text in enumerate(instructions, 1):
        cell = f"A{row}"
        spread.set(cell, text)
    
    doc.recompute()
    print("Montaj talimatlari eklendi!")
    return spread

def create_bom_table(doc):
    """Malzeme listesi (BOM) oluştur"""
    spread = doc.addObject("Spreadsheet::Sheet", "BOM")
    spread.Label = "Bill_of_Materials"
    
    headers = ["Parca No", "Parca Adi", "Aciklama", "Adet", "Malzeme"]
    for col, header in enumerate(headers):
        cell = chr(ord('A') + col) + "1"
        spread.set(cell, header)
    
    parts = [
        ("001", "Ana Sase Profili", "80x80x4 mm, 6000 mm", "4", "S235JR"),
        ("002", "Enlem Profili", "80x80x4 mm, 3000 mm", "4", "S235JR"),
        ("003", "Destek Ayagi", "100x100x5 mm, ayarlanabilir", "4", "Celik"),
        ("004", "Lineer Ray X", "HIWIN HGH25CA, 6000 mm", "2", "Celik"),
        ("005", "Lineer Ray Y", "HIWIN HGH25CA, 3000 mm", "1", "Celik"),
        ("006", "Kizak", "HIWIN HGH25CA", "6", "Celik"),
        ("007", "Servo Motor X", "ECMA-L11845, 4.5kW", "1", "Aluminyum"),
        ("008", "Servo Motor Y", "ECMA-E11320, 2.0kW", "1", "Aluminyum"),
        ("009", "Servo Motor Z", "ECMA-C11010, 1.0kW frenli", "1", "Aluminyum"),
        ("010", "Kesim Tekeri", "O80 mm, elmas kaplama", "1", "Elmas"),
        ("011", "R1-EC Modul", "EtherCAT servo surucu", "3", "Plastik"),
        ("012", "Kablo Kanali", "80x40 mm", "20 m", "Plastik"),
    ]
    
    row = 2
    for part in parts:
        for col, value in enumerate(part):
            cell = chr(ord('A') + col) + str(row)
            spread.set(cell, value)
        row += 1
    
    doc.recompute()
    print("Malzeme listesi (BOM) olusturuldu!")
    return spread

def run_assembly4_setup():
    """Assembly4 montaj kurulumunu çalıştır"""
    print("=" * 60)
    print("Assembly4 Montaj ve Simulasyon Kurulumu")
    print("GFB-60/30RE CNC Cam Kesme Makinesi")
    print("=" * 60)
    print()
    
    doc = setup_assembly4_document()
    create_variable_table(doc)
    
    print("LCS pozisyonlari olusturuluyor...")
    create_x_axis_lcs_positions(doc)
    create_y_axis_lcs_positions(doc)
    create_z_axis_lcs_positions(doc)
    
    print("Hareket simulasyonu setup'i...")
    create_motion_simulation(doc)
    
    print("Montaj talimatlari ekleniyor...")
    create_assembly_instructions(doc)
    
    print("Malzeme listesi olusturuluyor...")
    create_bom_table(doc)
    
    doc.recompute()
    
    print()
    print("=" * 60)
    print("Assembly4 kurulumu tamamlandi!")
    print("=" * 60)
    print()
    print("SONRAKI ADIMLAR:")
    print("1. Assembly4 Workbench'e gecin")
    print("2. STEP dosyalarini import edin:")
    print("   - 07_Exports/STEP/ dizinindeki dosyalari kullanin")
    print("3. LCS'lere gore parcalari yerlestirin")
    print("4. Constraint'leri tanimlayin:")
    print("   - Fixed: Sabit baglantilar")
    print("   - Slider: Lineer hareketler")
    print("5. Animation workbench ile simulasyon yapin")
    print()
    
    return doc

if __name__ == "__main__":
    run_assembly4_setup()