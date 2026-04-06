# -*- coding: utf-8 -*-
"""
FreeCAD Çalışma Dizini Kurulum Scripti
CNCRevizyon Projesi için

Kullanım:
    FreeCAD Python Console'da:
    exec(open("CAD/FreeCAD/00_Common/Setup_WorkingDirectory.py").read())
    setup_working_directory()
    add_library_paths()
"""

import FreeCAD as App
import os
import sys

# =============================================================================
# PROJE YAPILANDIRMASI
# =============================================================================

# Proje kök dizini
PROJECT_ROOT = "/Users/oktaycit/Projeler/CNCRevizyon"
FREECAD_DIR = os.path.join(PROJECT_ROOT, "CAD", "FreeCAD")

# Alt klasörler (kütüphane yolları)
SUBDIRS = [
    "00_Common",
    "01_Motors",
    "02_Frame",
    "03_LinearGuides",
    "04_CuttingHead",
    "05_Electronics",
    "06_Assembly",
    "07_Exports/STEP",
    "07_Exports/DXF",
    "07_Exports/STL",
]

# =============================================================================
# FONKSİYONLAR
# =============================================================================

def setup_working_directory():
    """
    Çalışma dizinini ayarla
    
    Not: FreeCAD'de doğrudan working directory ayarı yoktur.
    Bunun yerine os.chdir() ile Python çalışma dizinini değiştiriyoruz.
    
    Returns:
        str: Ayarlanan çalışma dizini
    """
    
    # Dizin var mı kontrol et
    if not os.path.exists(FREECAD_DIR):
        print(f"⚠️  Dizin bulunamadı: {FREECAD_DIR}")
        print("📁 Dizin oluşturuluyor...")
        os.makedirs(FREECAD_DIR)
        
        # Alt klasörleri de oluştur
        for subdir in SUBDIRS:
            subdir_path = os.path.join(FREECAD_DIR, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)
                print(f"   ✅ Oluşturuldu: {subdir}/")
    
    # Python çalışma dizinini değiştir
    os.chdir(FREECAD_DIR)
    
    # FreeCAD Config'e de yaz (kalıcı olması için)
    # Not: FreeCAD'de doğrudan setWorkingDirectory yok, os.chdir kullanıyoruz
    cfg_path = os.path.join(App.getUserAppDataDir(), "user.cfg")
    
    # Görsel çıktı
    print("=" * 70)
    print("  FREECAD ÇALIŞMA DİZİNİ AYARLANDI")
    print("=" * 70)
    print(f"  📁 Dizin: {FREECAD_DIR}")
    print(f"  📂 Alt klasörler:")
    
    # Alt klasörleri listele
    for item in sorted(os.listdir(FREECAD_DIR)):
        item_path = os.path.join(FREECAD_DIR, item)
        if os.path.isdir(item_path):
            print(f"      └── {item}/")
    
    print("=" * 70)
    
    return FREECAD_DIR


def add_library_paths():
    """
    FreeCAD kütüphane yollarını ekle
    
    Returns:
        list: Eklenen yollar listesi
    """
    
    added_paths = []
    
    for subdir in SUBDIRS:
        path = os.path.join(FREECAD_DIR, subdir)
        if os.path.exists(path):
            if path not in App.getSearchPaths():
                App.addSearchPath(path)
                added_paths.append(path)
                print(f"  ✅ Eklendi: {path}")
            else:
                print(f"  ℹ️  Zaten ekli: {subdir}/")
        else:
            print(f"  ⚠️  Dizin yok: {subdir}/")
    
    print(f"\n  Toplam {len(added_paths)} yol eklendi.")
    return added_paths


def load_recent_document():
    """
    Son açılan .FCStd dosyasını yükle
    
    Returns:
        str or None: Yüklenen dosya yolu veya None
    """
    
    recent_file = None
    
    # En son değiştirilen .FCStd dosyasını bul
    latest_time = 0
    for root, dirs, files in os.walk(FREECAD_DIR):
        # .FCBak dosyalarını atla
        for file in files:
            if file.endswith(".FCStd") and not file.endswith(".FCBak"):
                file_path = os.path.join(root, file)
                mtime = os.path.getmtime(file_path)
                if mtime > latest_time:
                    latest_time = mtime
                    recent_file = file_path
    
    if recent_file:
        print(f"  📄 Son dosya: {recent_file}")
        try:
            App.openDocument(recent_file)
            print(f"  ✅ Yüklendi: {os.path.basename(recent_file)}")
            return recent_file
        except Exception as e:
            print(f"  ❌ Hata: {e}")
            return None
    else:
        print("  📄 Hiçbir .FCStd dosyası bulunamadı.")
        print("  📝 Yeni document oluşturuluyor...")
        doc = App.newDocument("CNCRevizyon_Assembly")
        doc.Label = "CNC Revizyon Montajı"
        return None


def check_freecad_version():
    """
    FreeCAD versiyonunu kontrol et
    
    Returns:
        tuple: (major, minor, patch) versiyon numarası
    """
    
    version = App.Version()
    major = int(version[0])
    minor = int(version[1])
    patch = int(version[2].split('.')[0]) if '.' in version[2] else int(version[2])
    
    print(f"  🔧 FreeCAD Versiyonu: {major}.{minor}.{patch}")
    
    # Assembly4 için minimum versiyon kontrolü
    if major < 0 or (major == 0 and minor < 19):
        print("  ⚠️  Uyarı: Assembly4 için FreeCAD 0.19+ önerilir!")
    else:
        print("  ✅ Versiyon uygun")
    
    return (major, minor, patch)


def check_assembly4():
    """
    Assembly4 Workbench kurulu mu kontrol et
    
    Returns:
        bool: Assembly4 kurulu mu?
    """
    
    try:
        import Asm4
        print("  ✅ Assembly4 Workbench bulundu")
        return True
    except ImportError:
        print("  ❌ Assembly4 Workbench bulunamadı!")
        print("\n  Kurulum için:")
        print("  1. Tools → Addon Manager menüsüne gidin")
        print("  2. 'Assembly4' arayın ve yükleyin")
        print("  3. FreeCAD'i yeniden başlatın")
        return False


def run_all_checks():
    """
    Tüm kontrolleri ve kurulumları çalıştır
    """
    
    print("\n" + "=" * 70)
    print("  CNCRevizyon FreeCAD Kurulum Kontrolü")
    print("=" * 70 + "\n")
    
    # 1. Versiyon kontrolü
    print("1️⃣  FreeCAD Versiyon Kontrolü")
    print("-" * 70)
    check_freecad_version()
    print()
    
    # 2. Assembly4 kontrolü
    print("2️⃣  Assembly4 Workbench Kontrolü")
    print("-" * 70)
    has_assembly4 = check_assembly4()
    print()
    
    # 3. Çalışma dizini ayarlama
    print("3️⃣  Çalışma Dizini Ayarlama")
    print("-" * 70)
    setup_working_directory()
    print()
    
    # 4. Kütüphane yolları ekleme
    print("4️⃣  Kütüphane Yolları Ekleme")
    print("-" * 70)
    add_library_paths()
    print()
    
    # 5. Son dosyayı yükle (isteğe bağlı)
    print("5️⃣  Son Dosya Yükleme")
    print("-" * 70)
    # Otomatik yükleme istenmezse bu satırı yorum satırı yapın
    # load_recent_document()
    print("  ℹ️  Otomatik yükleme atlandı (manuel açın)")
    print()
    
    print("=" * 70)
    print("  ✅ KURULUM TAMAMLANDI")
    print("=" * 70)
    
    # Özet
    print("\n  Hızlı Başlangıç:")
    print("  ----------------")
    print(f"  1. Lamine cam montajı:")
    print(f"     exec(open('{FREECAD_DIR}/06_Assembly/Assembly4_LamineCam_ECam.py').read())")
    print(f"     create_lamine_assembly()")
    print()
    print(f"  2. Ana montaj:")
    print(f"     App.openDocument('{FREECAD_DIR}/30RE CNC Assembly4.FCStd')")
    print()


# =============================================================================
# HIZLI KOMUTLAR (Console için)
# =============================================================================

"""
FreeCAD Python Console'da hızlı kullanım:

# Tüm kurulumu çalıştır
exec(open("CAD/FreeCAD/00_Common/Setup_WorkingDirectory.py").read())
run_all_checks()

# Sadece çalışma dizinini ayarla
setup_working_directory()

# Kütüphane yollarını ekle
add_library_paths()

# Son dosyayı yükle
load_recent_document()

# Versiyon kontrolü
check_freecad_version()

# Assembly4 kontrolü
check_assembly4()
"""

# =============================================================================
# ANA PROGRAM
# =============================================================================

if __name__ == "__main__":
    run_all_checks()