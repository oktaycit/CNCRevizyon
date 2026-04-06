# -*- coding: utf-8 -*-
"""
LiSEC GFB-60/30RE - Lamine Cam Kesim Kafası ve E-Cam Simülasyonu
FreeCAD Assembly4 Workbench için Python Script

Özellikler:
- Z ekseni kesim kafası montajı (12-24mm lamine cam için)
- Kesim tekeri montajı ve açılır/kapanır mekanizma
- E-Cam (Elektronik Kam) profili simülasyonu
- Delta NC300 uyumlu kinematik zincir

Yazar: CNC AI Orchestrator (qwen3-coder-plus)
Tarih: 2026-04-04
"""

import FreeCAD as App
import FreeCADGui as Gui
import Part
import math
import time

# =============================================================================
# DOKÜMANTASYON VE GÜVENLİK NOTLARI
# =============================================================================
"""
GÜVENLİK UYARILARI:
1. Bu script çalıştırılmadan önce FreeCAD Assembly4 Workbench kurulmalıdır
2. Gerçek parçalar STEP dosyası olarak import edilmelidir
3. Simülasyon sırasında hareket sınırlarını aşmayın
4. Lamine cam kesimi için kesim basıncı 0.3-0.5 MPa arası olmalıdır

TEKNİK ÖZELLİKLER:
- Z Ekseni Stroku: 0-300 mm
- Kesim Hızı: 0-80 m/dk
- Cam Kalınlığı: 12-24 mm (lamine)
- Tekrarlanabilirlik: ±0.05 mm
- Encoder Çözünürlüğü: 24-bit (16,777,216 count/devir)
"""

# =============================================================================
# 1. DEĞİŞKENLER VE PARAMETRELER
# =============================================================================

class LamineCamParametreleri:
    """Lamine cam kesim parametreleri"""
    
    # Cam özellikleri
    CAM_KALINLIGI_MIN = 12.0  # mm
    CAM_KALINLIGI_MAX = 24.0  # mm
    PVB_KALINLIGI = 0.38  # mm (Polyvinyl Butyral katmanı)
    
    # Kesim parametreleri
    KESIM_HIZI = 80.0  # m/dk
    KESIM_DERINLIGI_FAZLA = 0.5  # mm (cam kalınlığı + fazla)
    
    # E-Cam profili
    E_CAM_ACISI_MAX = 15.0  # derece
    E_CAM_OFFSET = 50.0  # mm (tetiklenme yüksekliği)
    
    # Z ekseni
    Z_STROK_MAX = 300.0  # mm
    Z_HIZ_MAX = 5000.0  # mm/dk
    
    # Güvenlik
    GUVENLIK_FAKTORU = 1.5
    ACIL_DURDURMA_Z = 100.0  # mm (acil durumda kalkış yüksekliği)


# =============================================================================
# 2. FREECAD DOCUMENT OLUŞTURMA
# =============================================================================

def create_document():
    """Yeni FreeCAD document oluştur"""
    doc_name = "LiSEC_GFB60_30RE_Lamine_ECam"
    
    # Eğer document varsa kullan, yoksa yeni oluştur
    if App.ActiveDocument is None:
        doc = App.newDocument(doc_name)
    else:
        doc = App.ActiveDocument
        if doc.Name != doc_name:
            doc = App.newDocument(doc_name)
    
    doc.Label = "Lamine Cam Kesim Kafası - E-Cam"
    return doc


# =============================================================================
# 3. TEMSİLİ PARÇA OLUŞTURMA (Placeholder Geometry)
# =============================================================================

def create_box(doc, name, width, height, depth, color, position=App.Vector(0,0,0)):
    """Basit kutu geometrisi oluştur (temsili parça)"""
    box = doc.addObject("Part::Box", name)
    box.Width = width
    box.Height = height
    box.Length = depth
    box.Label = name
    box.Placement.Base = position
    box.ViewObject.ShapeColor = color
    return box


def create_cylinder(doc, name, radius, height, color, position=App.Vector(0,0,0)):
    """Silindir geometrisi oluştur"""
    cyl = doc.addObject("Part::Cylinder", name)
    cyl.Radius = radius
    cyl.Height = height
    cyl.Label = name
    cyl.Placement.Base = position
    cyl.ViewObject.ShapeColor = color
    return cyl


def create_lcs(doc, name, position=App.Vector(0,0,0), rotation=App.Rotation(0,0,0)):
    """Local Coordinate System (LCS) oluştur"""
    lcs = doc.addObject("PartDesign::CoordinateSystem", name)
    lcs.Label = name
    lcs.Placement.Base = position
    lcs.Placement.Rotation = rotation
    return lcs


# =============================================================================
# 4. PARÇA OLUŞTURMA FONKSİYONLARI
# =============================================================================

def create_portal_base(doc):
    """Portal köprüsü (X ekseni taşıyıcı)"""
    # 80x80 mm alüminyum profil temsili
    base = create_box(
        doc, "Portal_Base", 
        width=200, height=50, depth=300, 
        color=(0.7, 0.7, 0.7),  # Gri
        position=App.Vector(0, 0, 0)
    )
    return base


def create_z_column(doc, portal):
    """Z ekseni dik mili (sabit)"""
    # 60x60 mm profil
    column = create_box(
        doc, "Z_Column",
        width=60, height=400, depth=60,
        color=(0.4, 0.4, 0.4),  # Koyu gri
        position=App.Vector(portal.Width.Value/2 - 30, 0, 0)
    )
    return column


def create_z_carriage(doc, column):
    """Z ekseni hareketli kızak"""
    # HIWIN HGH25CA lineer rehber temsili
    carriage = create_box(
        doc, "Z_Carriage",
        width=80, height=100, depth=70,
        color=(0.2, 0.5, 0.8),  # Mavi
        position=App.Vector(column.Placement.Base.x - 10, 250, 0)
    )
    return carriage


def create_cutting_head(doc, carriage):
    """
    Lamine cam kesim kafası
    12-24mm cam kalınlığı için ayarlanabilir
    """
    # Ana gövde
    head_body = create_box(
        doc, "Cutting_Head_Body",
        width=60, height=120, depth=60,
        color=(1.0, 0.5, 0.0),  # Turuncu (güvenlik rengi)
        position=App.Vector(carriage.Placement.Base.x, carriage.Placement.Base.y - 80, 0)
    )
    
    # Kesim tekeri (silindir)
    wheel = create_cylinder(
        doc, "Cutting_Wheel",
        radius=15, height=10,
        color=(0.8, 0.8, 0.8),  # Metalik gri
        position=App.Vector(head_body.Placement.Base.x, head_body.Placement.Base.y - 60, head_body.Length.Value/2 + 5)
    )
    
    # Pnömatik silindir (teker kaldırma)
    pneumatic = create_cylinder(
        doc, "Pneumatic_Cylinder",
        radius=10, height=40,
        color=(0.1, 0.3, 0.6),  # Mavi
        position=App.Vector(head_body.Placement.Base.x + 20, head_body.Placement.Base.y - 30, head_body.Length.Value/2)
    )
    
    # Encoder (pozisyon sensörü)
    encoder = create_cylinder(
        doc, "Position_Encoder",
        radius=8, height=20,
        color=(0.2, 0.2, 0.2),  # Siyah
        position=App.Vector(head_body.Placement.Base.x - 20, head_body.Placement.Base.y - 30, head_body.Length.Value/2)
    )
    
    return {
        'body': head_body,
        'wheel': wheel,
        'pneumatic': pneumatic,
        'encoder': encoder
    }


def create_alt_axis_cam(doc, head):
    """
    E-Cam (Elektronik Kam) ekseni
    Lamine cam için özel kesim profili
    """
    # E-Cam mekanizması (rotasyonel)
    cam_mechanism = create_box(
        doc, "Alt_Axis_Cam",
        width=40, height=40, depth=40,
        color=(0.8, 0.1, 0.1),  # Kırmızı
        position=App.Vector(
            head['body'].Placement.Base.x,
            head['body'].Placement.Base.y - 20,
            head['body'].Placement.Base.z + 30
        )
    )
    return cam_mechanism


def create_cable_track(doc, carriage):
    """Kablo tankı izleyici"""
    track = create_box(
        doc, "Cable_Track",
        width=20, height=10, depth=200,
        color=(0.1, 0.1, 0.1),  # Siyah
        position=App.Vector(
            carriage.Placement.Base.x + 60,
            carriage.Placement.Base.y + 50,
            carriage.Placement.Base.z
        )
    )
    return track


# =============================================================================
# 5. ASSEMBLY4 KİNEMATİK BAĞLANTILAR
# =============================================================================

def setup_kinematic_links(doc, params):
    """
    Assembly4 kinematik bağlantılarını kurar
    Expression engine ile eksenler arası ilişki
    """
    
    # Z Carriage hareketi (Y ekseninde)
    # Variables.Z_Depth değişkenine bağlı
    doc.Z_Carriage.setExpression('Placement.Position.y', f'{params.Z_STROK_MAX} - Variables.Z_Depth')
    doc.Z_Carriage.setExpression('Placement.Position.x', f'{doc.Z_Column.Placement.Base.x}')
    
    # Cutting Head, Carriage'a bağlı
    doc.Cutting_Head_Body.setExpression('Placement.Position.y', 'Z_Carriage.Placement.Position.y - 80')
    doc.Cutting_Head_Body.setExpression('Placement.Position.x', 'Z_Carriage.Placement.Position.x')
    
    # Kesim tekeri, Head'e bağlı
    doc.Cutting_Wheel.setExpression('Placement.Position.y', 'Cutting_Head_Body.Placement.Position.y - 60')
    doc.Cutting_Wheel.setExpression('Placement.Position.x', 'Cutting_Head_Body.Placement.Position.x')
    
    # E-Cam simülasyonu (Z pozisyonuna bağlı)
    # Lamine cam için özel formül
    cam_formula = f"""
    (Variables.Z_Depth > {params.E_CAM_OFFSET}) ? 
    ({params.E_CAM_ACISI_MAX} * sin((Variables.Z_Depth - {params.E_CAM_OFFSET}) * 0.1)) 
    : 0
    """
    doc.Alt_Axis_Cam.setExpression('Placement.RotationAxis.y', '1')
    doc.Alt_Axis_Cam.setExpression('Placement.Angle', cam_formula)
    
    # Kablo tankı takibi
    doc.Cable_Track.setExpression('Placement.Position.y', 'Z_Carriage.Placement.Position.y + 50')
    doc.Cable_Track.setExpression('Placement.Position.x', f'{doc.Z_Carriage.Placement.Base.x + 60}')


# =============================================================================
# 6. DEĞİŞKEN TABLOSU (Spreadsheet)
# =============================================================================

def create_variables_spreadsheet(doc, params):
    """Assembly4 değişken tablosu oluştur"""
    
    # Spreadsheet oluştur
    ss = doc.addObject('Spreadsheet::Sheet', 'Variables')
    
    # Parametreleri ekle
    variables = {
        'A0_Z_Depth': ('Z ekseni kesim derinliği', 0.0, 'mm'),
        'A0_Z_Max': ('Z ekseni maksimum strok', params.Z_STROK_MAX, 'mm'),
        'A0_Cam_Phase': ('E-Cam faz açısı', 0.0, '°'),
        'A0_Cam_Amp': ('E-Cam genlik', params.E_CAM_ACISI_MAX, '°'),
        'A0_Cam_Offset': ('E-Cam tetikleme', params.E_CAM_OFFSET, 'mm'),
        'A0_Cam_Speed': ('E-Cam hız', params.KESIM_HIZI, 'm/dk'),
        'A0_Cam_Thickness': ('Cam kalınlığı', 16.0, 'mm'),  # Varsayılan 16mm lamine
        'A0_PVB_Thickness': ('PVB katmanı', params.PVB_KALINLIGI, 'mm'),
        'A0_Cutting_Pressure': ('Kesim basıncı', 0.4, 'MPa'),
        'A0_Safety_Z': ('Güvenlik Z', params.ACIL_DURDURMA_Z, 'mm'),
    }
    
    row = 0
    for key, (desc, value, unit) in variables.items():
        # Değer
        ss.set(f'A{row}', key)
        ss.set(f'B{row}', desc)
        ss.set(f'C{row}', value)
        ss.set(f'D{row}', unit)
        row += 1
    
    # Variables objesi olarak etiketle
    ss.Label = 'Variables'
    ss.Alias = 'Variables'
    
    return ss


# =============================================================================
# 7. E-CAM PROFİL SİMÜLASYONU
# =============================================================================

def e_cam_profile_interpolate(angle, profile):
    """
    E-Cam profili için enterpolasyon
    
    Args:
        angle: Mevcut açı (derece)
        profile: [(açı, z_pozisyon), ...] liste
    
    Returns:
        z_pozisyon: Enterpole edilmiş Z pozisyonu
    """
    for i in range(len(profile) - 1):
        if profile[i][0] <= angle < profile[i+1][0]:
            a1, z1 = profile[i]
            a2, z2 = profile[i+1]
            ratio = (angle - a1) / (a2 - a1)
            return z1 + (z2 - z1) * ratio
    return profile[-1][1]


def get_lamine_cam_profile(cam_thickness_mm):
    """
    Lamine cam için E-Cam profili oluştur
    
    Lamine cam kesiminde:
    1. Yavaş basınç artışı (cam yüzeyi çizilmesini önler)
    2. Sabit yüksek basınç (kesim)
    3. Kademeli basınç azaltma (PVB yırtılmayı engeller)
    
    Args:
        cam_thickness_mm: Cam kalınlığı (12-24mm)
    
    Returns:
        profile: [(açı, z_pozisyon), ...] liste
    """
    # Cam kalınlığına göre penetrasyon
    penetration = cam_thickness_mm + 0.5  # 0.5mm fazla
    
    # Lamine cam için özel profil (PVB katmanı dikkate alınarak)
    profile = [
        (0, 0),                    # Başlangıç pozisyonu
        (30, penetration * 0.2),   # Yavaş giriş (PVB koruma)
        (60, penetration * 0.6),   # Basınç artışı
        (90, penetration),         # Tam kesim derinliği
        (180, penetration),        # Sabit kesim
        (240, penetration * 0.8),  # Çıkış başlangıcı
        (270, penetration * 0.4),  # Basınç azaltma
        (300, penetration * 0.1),  # Son çıkış
        (330, 0),                  # Başlangıca dönüş
        (360, 0),                  # Tam döngü
    ]
    
    return profile


def run_ecam_simulation(doc, params, duration_sec=10):
    """
    E-Cam simülasyonunu çalıştır
    
    Args:
        doc: FreeCAD document
        params: LamineCamParametreleri objesi
        duration_sec: Simülasyon süresi (saniye)
    """
    print("=" * 60)
    print("E-CAM SİMÜLASYONU BAŞLATILIYOR")
    print("=" * 60)
    
    # E-Cam profilini al
    profile = get_lamine_cam_profile(params.CAM_KALINLIGI_MIN)  # 12mm için
    
    # Hareketli parçaları bul
    try:
        z_carriage = doc.getObject("Z_Carriage")
        alt_axis = doc.getObject("Alt_Axis_Cam")
        cutting_wheel = doc.getObject("Cutting_Wheel")
    except AttributeError as e:
        print(f"HATA: Parça bulunamadı - {e}")
        print("Lütfen önce create_lamine_assembly() fonksiyonunu çalıştırın")
        return
    
    # Simülasyon parametreleri
    steps = 72  # 5 derece adımlarla 360 derece
    step_time = duration_sec / steps  # Her adım için süre
    
    print(f"Simülasyon: {steps} adım, {step_time:.2f}s/adım")
    print(f"Toplam süre: {duration_sec}s")
    print("-" * 60)
    
    # Simülasyon döngüsü
    for step in range(steps + 1):
        angle = step * 5  # 5 derece adımlar
        
        # E-Cam profilinden Z pozisyonu al
        target_z = e_cam_profile_interpolate(angle, profile)
        
        # Alt eksen rotasyonu
        alt_axis.Placement.Rotation = App.Rotation(App.Vector(0, 1, 0), angle)
        
        # Z ekseni pozisyonu (E-Cam profiline göre)
        z_carriage.Placement.Base.y = params.Z_STROK_MAX - target_z
        
        # Kesim tekeri rotasyonu (kesim hareketi simülasyonu)
        wheel_rotation = angle * 2  # Teker daha hızlı döner
        cutting_wheel.Placement.Rotation = App.Rotation(App.Vector(0, 0, 1), wheel_rotation)
        
        # Document'i güncelle
        doc.recompute()
        
        # Durum bilgisi (her 10 adımda bir)
        if step % 10 == 0:
            print(f"Adım {step}/{steps} | Açı: {angle:3.0f}° | Z: {target_z:6.2f}mm")
        
        # Kısa bekleme (simülasyon hızı)
        time.sleep(step_time * 0.1)  # Hızlandırılmış simülasyon
    
    print("-" * 60)
    print("E-CAM SİMÜLASYONU TAMAMLANDI")
    print("=" * 60)


# =============================================================================
# 8. ANA MONTAJ FONKSİYONU
# =============================================================================

def create_lamine_assembly():
    """
    Lamine cam kesim kafası montajını oluştur
    
    Bu fonksiyon:
    1. Yeni FreeCAD document oluşturur
    2. Tüm parçaları oluşturur
    3. Assembly4 kinematik bağlantılarını kurar
    4. Değişken tablosu oluşturur
    """
    print("=" * 60)
    print("LiSEC GFB-60/30RE - LAMİNE CAM KESİM KAFASI")
    print("Assembly4 Montaj Scripti")
    print("=" * 60)
    
    # Parametreler
    params = LamineCamParametreleri()
    
    # Document oluştur
    doc = create_document()
    print(f"Document: {doc.Label}")
    
    # Parçaları oluştur
    print("Parçalar oluşturuluyor...")
    portal = create_portal_base(doc)
    column = create_z_column(doc, portal)
    carriage = create_z_carriage(doc, column)
    head = create_cutting_head(doc, carriage)
    alt_axis = create_alt_axis_cam(doc, head)
    cable_track = create_cable_track(doc, carriage)
    
    print(f"  - Portal Base: {portal.Label}")
    print(f"  - Z Column: {column.Label}")
    print(f"  - Z Carriage: {carriage.Label}")
    print(f"  - Cutting Head: {head['body'].Label}")
    print(f"  - Alt Axis Cam: {alt_axis.Label}")
    print(f"  - Cable Track: {cable_track.Label}")
    
    # Kinematik bağlantıları kur
    print("Kinematik bağlantılar kuruluyor...")
    setup_kinematic_links(doc, params)
    
    # Değişken tablosu oluştur
    print("Değişken tablosu oluşturuluyor...")
    ss = create_variables_spreadsheet(doc, params)
    
    # Document'i güncelle
    doc.recompute()
    
    # View fit
    if Gui.ActiveDocument:
        Gui.SendMsgToActiveView("ViewFit")
    
    print("=" * 60)
    print("MONTAJ TAMAMLANDI!")
    print("=" * 60)
    print("\nKULLANIM TALİMATLARI:")
    print("1. Variables spreadsheet'ini açın")
    print("2. 'A0_Z_Depth' değerini 0-300mm arası değiştirin")
    print("3. Z ekseni hareketini ve E-Cam simülasyonunu gözlemleyin")
    print("\nSİMÜLASYON İÇİN:")
    print("  run_ecam_simulation(App.ActiveDocument, LamineCamParametreleri())")
    print("=" * 60)
    
    return doc


# =============================================================================
# 9. GÜVENLİK VE HATA YÖNETİMİ
# =============================================================================

def safety_check(doc, params):
    """
    Güvenlik kontrolleri yap
    
    Returns:
        bool: Güvenlik durumu (True = güvenli)
    """
    errors = []
    
    # Z ekseni limit kontrolü
    try:
        z_carriage = doc.getObject("Z_Carriage")
        z_pos = z_carriage.Placement.Base.y
        
        if z_pos < 0 or z_pos > params.Z_STROK_MAX:
            errors.append(f"Z ekseni limit dışı: {z_pos}mm (0-{params.Z_STROK_MAX}mm)")
    except:
        errors.append("Z_Carriage bulunamadı")
    
    # E-Cam açı kontrolü
    try:
        alt_axis = doc.getObject("Alt_Axis_Cam")
        cam_angle = alt_axis.Placement.Rotation.Angle
    
        if cam_angle > math.radians(params.E_CAM_ACISI_MAX * 2):
            errors.append(f"E-Cam açı limit dışı: {math.degrees(cam_angle):.1f}°")
    except:
        errors.append("Alt_Axis_Cam bulunamadı")
    
    # Hata raporu
    if errors:
        print("⚠️ GÜVENLİK UYARILARI:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Güvenlik kontrolleri başarılı")
    return True


# =============================================================================
# 10. KOMUT SATIRI ÇALIŞTIRMA
# =============================================================================

if __name__ == "__main__":
    # Ana montajı oluştur
    doc = create_lamine_assembly()
    
    # Güvenlik kontrolü
    params = LamineCamParametreleri()
    safety_check(doc, params)
    
    print("\nMontaj tamamlandı. Simülasyon için:")
    print("  run_ecam_simulation(App.ActiveDocument, LamineCamParametreleri())")


# =============================================================================
# 11. FREECAD CONSOLE İÇİN KISA KOMUTLAR
# =============================================================================

"""
FreeCAD Python Console'da kullanılabilecek komutlar:

# Montajı oluştur
exec(open("CAD/FreeCAD/06_Assembly/Assembly4_LamineCam_ECam.py").read())
create_lamine_assembly()

# Simülasyon çalıştır
run_ecam_simulation(App.ActiveDocument, LamineCamParametreleri())

# Değişkenleri manuel ayarla
App.ActiveDocument.Variables.A0_Z_Depth = 150.0
App.ActiveDocument.Variables.A0_Cam_Thickness = 16.0
App.ActiveDocument.recompute()

# Güvenlik kontrolü
safety_check(App.ActiveDocument, LamineCamParametreleri())

# E-Cam profili görüntüle
profile = get_lamine_cam_profile(16.0)
print(profile)
"""