# FreeCAD Assembly4 STEP Dosyalarını Import
# CNC Revizyon Projesi - GFB-60/30RE
# STEP dosyalarını Assembly4 montajına import eder

import FreeCAD as App
import Part
import os

# Base dizinini ayarla
try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly"

STEP_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP")

def get_step_filepath(subdir, filename):
    """STEP dosya yolunu oluştur"""
    return os.path.join(STEP_DIR, subdir, filename)

def import_step_to_assembly(assembly_doc, filepath, part_name, position=(0, 0, 0)):
    """
    STEP dosyasını Assembly4 montajına import et
    
    Args:
        assembly_doc: Assembly4 dokümanı
        filepath: STEP dosya yolu
        part_name: Parça adı
        position: Pozisyon vektörü
    """
    if not os.path.exists(filepath):
        print(f"  ⚠ {filepath} bulunamadı")
        return None
    
    # STEP dosyasını import et
    import Import
    shapes = Import.insert(filepath, assembly_doc.Name)
    
    if shapes:
        shape = shapes[0]
        shape.Label = part_name
        shape.Name = part_name.replace(" ", "_")
        
        # Pozisyonu ayarla
        shape.Placement = App.Placement(
            App.Vector(position),
            App.Rotation(0, 0, 0)
        )
        
        assembly_doc.recompute()
        print(f"  ✓ {part_name} import edildi")
        return shape
    
    return None

def import_all_motors(doc):
    """Tüm motorları import et"""
    print("\n📦 Motorlar import ediliyor...")
    
    motors = [
        ("ECMA-L11845.stp", "Motor_X_4_5kW", (5800, 100, 50)),
        ("ECMA-E11320.stp", "Motor_Y_2kW", (5800, 450, 100)),
        ("ECMA-C11010.stp", "Motor_Z_1kW", (3000, 500, 2900)),
    ]
    
    for filename, name, pos in motors:
        filepath = get_step_filepath("Motors", filename)
        import_step_to_assembly(doc, filepath, name, pos)

def import_linear_guides(doc):
    """Lineer rayları import et"""
    print("\n📐 Lineer Raylar import ediliyor...")
    
    # X ekseni rayları
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_X_Rail.stp"), 
                           "X_Rail_Left", (100, 0, 0))
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_X_Rail.stp"), 
                           "X_Rail_Right", (2900, 0, 0))
    
    # Y ekseni rayı
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_Y_Rail.stp"), 
                           "Y_Rail", (3000, 400, 1500))
    
    # Kızaklar
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_Block.stp"), 
                           "X_Block_FL", (100, 40, 500))
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_Block.stp"), 
                           "X_Block_FR", (2900, 40, 500))
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_Block.stp"), 
                           "X_Block_RL", (100, 40, 5500))
    import_step_to_assembly(doc, get_step_filepath("LinearGuides", "HIWIN_HGH25_Block.stp"), 
                           "X_Block_RR", (2900, 40, 5500))

def import_frame(doc):
    """Şase profillerini import et"""
    print("\n🏗️ Şase Profilleri import ediliyor...")
    
    import_step_to_assembly(doc, get_step_filepath("Frame", "MainFrame_Profiles.stp"), 
                           "Main_Frame", (3000, 1500, 0))
    import_step_to_assembly(doc, get_step_filepath("Frame", "SupportLeg.stp"), 
                           "Leg_FL", (0, 0, 0))
    import_step_to_assembly(doc, get_step_filepath("Frame", "SupportLeg.stp"), 
                           "Leg_FR", (6000, 0, 0))
    import_step_to_assembly(doc, get_step_filepath("Frame", "SupportLeg.stp"), 
                           "Leg_RL", (0, 3000, 0))
    import_step_to_assembly(doc, get_step_filepath("Frame", "SupportLeg.stp"), 
                           "Leg_RR", (6000, 3000, 0))

def import_cutting_head(doc):
    """Kesim kafasını import et"""
    print("\n🔧 Kesim Kafası import ediliyor...")
    
    import_step_to_assembly(doc, get_step_filepath("CuttingHead", "ZAxis_Housing.stp"), 
                           "Z_Housing", (3000, 300, 2820))
    import_step_to_assembly(doc, get_step_filepath("CuttingHead", "ZAxis_Slide.stp"), 
                           "Z_Slide", (3000, 300, 2870))
    import_step_to_assembly(doc, get_step_filepath("CuttingHead", "Cutting_Wheel.stp"), 
                           "Cutting_Wheel", (3000, 250, 2950))

def import_electronics(doc):
    """Elektronik parçaları import et"""
    print("\n🔌 Elektronik Parçalar import ediliyor...")
    
    import_step_to_assembly(doc, get_step_filepath("Electronics", "R1-EC_Housing.stp"), 
                           "R1-EC_X", (5700, 200, 100))
    import_step_to_assembly(doc, get_step_filepath("Electronics", "R1-EC_Housing.stp"), 
                           "R1-EC_Y", (5700, 300, 100))
    import_step_to_assembly(doc, get_step_filepath("Electronics", "R1-EC_Housing.stp"), 
                           "R1-EC_Z", (5700, 400, 100))
    import_step_to_assembly(doc, get_step_filepath("Electronics", "Cable_Carrier.stp"), 
                           "Cable_Carrier_X", (3000, 100, 100))

def run_import_to_assembly():
    """
    STEP dosyalarını Assembly4 montajına import et
    """
    print("=" * 60)
    print("STEP Dosyalarını Assembly4'e Import")
    print("GFB-60/30RE CNC Cam Kesme Makinesi")
    print("=" * 60)
    print()
    
    # Mevcut Assembly4 dokümanını bul veya yeni oluştur
    doc_names = ["GFB-60-30RE_Assembly", "GFB_60_30RE_Assembly"]
    
    # Önce aynı isimli doküman var mı kontrol et
    existing_doc = None
    for doc_name in doc_names:
        try:
            d = App.getDocument(doc_name)
            if d:
                existing_doc = d
                break
        except:
            pass
    
    # Eğer bulunamazsa, tüm dokümanları kontrol et
    if not existing_doc:
        for doc_name_check in App.listDocuments():
            d = App.getDocument(doc_name_check)
            if "Assembly" in d.Label or "Assembly" in d.Name:
                existing_doc = d
                break
    
    if existing_doc:
        doc = existing_doc
        print(f"📋 Mevcut doküman kullanılıyor: {doc.Label}")
    else:
        print("⚠ Assembly4 dokümanı bulunamadı!")
        print("Önce Assembly4_Montage.py scriptini çalıştırın:")
        print('exec(open("CAD/FreeCAD/06_Assembly/Assembly4_Montage.py").read())')
        return None
    
    # Assembly4 Workbench aktif mi kontrol et
    print("\n📌 NOT: Assembly4 Workbench'e geçmeyi unutmayın!")
    print("   View → Workbench → Assembly4")
    
    # STEP dosyalarını import et
    import_all_motors(doc)
    import_linear_guides(doc)
    import_frame(doc)
    import_cutting_head(doc)
    import_electronics(doc)
    
    doc.recompute()
    
    print()
    print("=" * 60)
    print("STEP Import işlemi tamamlandı!")
    print("=" * 60)
    print()
    print("SONRAKI ADIMLAR:")
    print("1. Assembly4 Workbench'de parçaları görün")
    print("2. LCS'lere göre parçaları hizalayın")
    print("3. Constraint'leri tanımlayın:")
    print("   - Assembly → Add Constraint → Fixed")
    print("   - Assembly → Add Constraint → Slider")
    print("4. Montajı tamamlayın")
    print()
    
    return doc

if __name__ == "__main__":
    run_import_to_assembly()