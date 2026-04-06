# FreeCAD Çalışma Dizini Ayarlama Rehberi

## CNCRevizyon Projesi için FreeCAD Kurulumu

---

## 1. FreeCAD'de Çalışma Dizini Ayarlama

### Yöntem 1: Tercihler (Preferences) Üzerinden

1. **FreeCAD'i açın**
2. **Edit → Preferences** menüsüne gidin (macOS: **FreeCAD → Preferences**)
3. **General** kategorisini seçin
4. **File** sekmesine gidin
5. **Working directory** alanına proje yolunu girin:

   ```
   /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD
   ```

6. **✓ Open dialog in this directory** seçeneğini işaretleyin
7. **OK** ile kaydedin

### Yöntem 2: Komut Satırı ile Başlatma

```bash
# FreeCAD'i proje dizini ile başlat
freecad /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD

# Veya belirli bir dosya ile
freecad /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/30RE\ CNC\ Assembly4.FCStd
```

### Yöntem 3: Python Console'dan Ayarlama

FreeCAD Python Console'da:

```python
import FreeCAD as App
import os

# Python çalışma dizinini ayarla (os.chdir ile)
os.chdir("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD")

# Mevcut çalışma dizinini kontrol et
current_dir = os.getcwd()
print(f"Mevcut dizin: {current_dir}")

# FreeCAD kullanıcı dizini
user_dir = App.getUserAppDataDir()
print(f"FreeCAD kullanıcı dizini: {user_dir}")
```

---

## 2. Proje Klasör Yapısı

```
CNCRevizyon/
└── CAD/FreeCAD/
    ├── 00_Common/           # Ortak parametreler
    ├── 01_Motors/           # Motor modelleri
    ├── 02_Frame/            # Şase/profil
    ├── 03_LinearGuides/     # Lineer kılavuzlar
    ├── 04_CuttingHead/      # Kesim kafası
    ├── 05_Electronics/      # Elektronik
    ├── 06_Assembly/         # Ana montaj (Assembly4)
    ├── 07_Exports/
    │   ├── STEP/           # STEP export
    │   ├── DXF/            # DXF export
    │   └── STL/            # STL export
    └── README.md
```

---

## 3. FreeCAD Config Dosyası

FreeCAD config dosyasını düzenleyerek varsayılan dizin ayarlayın:

### macOS

```
~/Library/Preferences/FreeCAD/user.cfg
```

**XML düzenlemesi:**

```xml
<FCPreferences>
    <UserAppData value="/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD"/>
    <WorkingDir value="/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD"/>
</FCPreferences>
```

---

## 4. Python Script ile Otomatik Ayarlama

`CAD/FreeCAD/00_Common/Setup_WorkingDirectory.py` oluşturun:

```python
# -*- coding: utf-8 -*-
"""
FreeCAD Çalışma Dizini Kurulum Scripti
CNCRevizyon Projesi için
"""

import FreeCAD as App
import os

# Proje kök dizini
PROJECT_ROOT = "/Users/oktaycit/Projeler/CNCRevizyon"
FREECAD_DIR = os.path.join(PROJECT_ROOT, "CAD", "FreeCAD")

def setup_working_directory():
    """Çalışma dizinini ayarla"""
    
    # Dizin var mı kontrol et
    if not os.path.exists(FREECAD_DIR):
        print(f"⚠️ Dizin bulunamadı: {FREECAD_DIR}")
        print("Dizin oluşturuluyor...")
        os.makedirs(FREECAD_DIR)
    
    # Çalışma dizinini ayarla
    App.setWorkingDirectory(FREECAD_DIR)
    
    print("=" * 60)
    print("FREECAD ÇALIŞMA DİZİNİ AYARLANDI")
    print("=" * 60)
    print(f"📁 Dizin: {FREECAD_DIR}")
    print(f"📂 Alt klasörler:")
    
    # Alt klasörleri listele
    for item in os.listdir(FREECAD_DIR):
        item_path = os.path.join(FREECAD_DIR, item)
        if os.path.isdir(item_path):
            print(f"   └── {item}/")
    
    print("=" * 60)
    
    return FREECAD_DIR

def add_library_paths():
    """FreeCAD kütüphane yollarını ekle"""
    
    library_paths = [
        os.path.join(FREECAD_DIR, "00_Common"),
        os.path.join(FREECAD_DIR, "01_Motors"),
        os.path.join(FREECAD_DIR, "02_Frame"),
        os.path.join(FREECAD_DIR, "03_LinearGuides"),
        os.path.join(FREECAD_DIR, "04_CuttingHead"),
        os.path.join(FREECAD_DIR, "05_Electronics"),
        os.path.join(FREECAD_DIR, "06_Assembly"),
    ]
    
    for path in library_paths:
        if path not in App.getSearchPaths():
            App.addSearchPath(path)
            print(f"✅ Eklendi: {path}")
    
    return library_paths

def load_recent_document():
    """Son açılan dosyayı yükle"""
    
    recent_dir = FREECAD_DIR
    recent_file = None
    
    # En son .FCStd dosyasını bul
    for root, dirs, files in os.walk(recent_dir):
        for file in files:
            if file.endswith(".FCStd") and not file.endswith(".FCBak"):
                recent_file = os.path.join(root, file)
                break
        if recent_file:
            break
    
    if recent_file:
        print(f"📄 Son dosya: {recent_file}")
        App.openDocument(recent_file)
        return recent_file
    else:
        print("📄 Yeni document oluşturuluyor...")
        return App.newDocument("CNCRevizyon_Assembly")

# Ana kurulum
if __name__ == "__main__":
    # Çalışma dizinini ayarla
    setup_working_directory()
    
    # Kütüphane yollarını ekle
    add_library_paths()
    
    # İsteğe bağlı: Son dosyayı yükle
    # load_recent_document()
```

### Kullanım

FreeCAD Python Console'da:

```python
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/00_Common/Setup_WorkingDirectory.py").read())
setup_working_directory()
add_library_paths()
```

---

## 5. Assembly4 Workbench için Özel Ayarlar

Assembly4 kullanıyorsanız:

1. **Assembly4 → Settings** menüsüne gidin
2. **Default Assembly Location** ayarlayın:

   ```
   /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly
   ```

3. **Default LCS** ayarlarını yapılandırın

---

## 6. Hızlı Erişim için Keyboard Shortcut

FreeCAD'te kısayol ataması:

1. **Tools → Customize** menüsüne gidin
2. **Keyboard** sekmesini seçin
3. **File → Open** komutuna kısayol atayın (örn: `Ctrl+O`)
4. **Macro → Run Macro** komutuna kısayol atayın (örn: `Ctrl+M`)

---

## 7. Macro Klasörü Ayarlama

FreeCAD Macro klasörünü proje dizinine yönlendirin:

1. **Edit → Preferences → General**
2. **Macro** sekmesine gidin
3. **Macro directory** ayarlayın:

   ```
   /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly
   ```

---

## 8. Komut Satırı Kısayolları (Alias)

`~/.zshrc` dosyasına ekleyin:

```bash
# FreeCAD CNC Projesi kısayolları
alias freecad-cnc="freecad /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD"
alias freecad-assembly="freecad /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly"
alias freecad-lamine="freecad /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/Assembly4_LamineCam_ECam.py"
```

Sonra terminal'de:

```bash
source ~/.zshrc

# Kısayolları kullan
freecad-cnc
freecad-lamine
```

---

## 9. VS Code Entegrasyonu

`.vscode/settings.json` dosyasına ekleyin:

```json
{
    "files.associations": {
        "*.FCStd": "xml",
        "*.fcmacro": "python",
        "*.pyc": "python"
    },
    "python.autoComplete.extraPaths": [
        "/Applications/FreeCAD.app/Contents/Frameworks/FreeCADPython.framework/Versions/Current/lib/python3.9/site-packages"
    ],
    "python.analysis.extraPaths": [
        "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD"
    ]
}
```

---

## 10. Hata Ayıklama

### Sorun: "Cannot find module" hatası

**Çözüm:**

```python
# Python Console'da yolları kontrol et
import sys
print(sys.path)

# Eksik yolu ekle
sys.path.append("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly")
```

### Sorun: "File not found" hatası

**Çözüm:**

```python
# Mutlak yol kullan
import os
abs_path = os.path.abspath("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/Assembly4_LamineCam_ECam.py")
exec(open(abs_path).read())
```

### Sorun: Assembly4 Workbench bulunamadı

**Çözüm:**

1. FreeCAD'de **Addon Manager**'ı açın
2. **Assembly4** arayın ve yükleyin
3. FreeCAD'i yeniden başlatın

---

## 11. Hızlı Başlangıç Komutları

FreeCAD Python Console'da hızlı başlangıç:

```python
import os

# 1. Çalışma dizinini ayarla (os.chdir ile)
os.chdir("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD")

# 2. Lamine cam montajını yükle
exec(open("06_Assembly/Assembly4_LamineCam_ECam.py").read())
create_lamine_assembly()

# 3. E-Cam simülasyonunu çalıştır
run_ecam_simulation(App.ActiveDocument, LamineCamParametreleri())

# 4. STEP export
import Part
Part.export(App.ActiveDocument.getObject("Cutting_Head_Body"), 
            "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/07_Exports/STEP/CuttingHead/Cutting_Head_Body.stp")
```

---

## 12. Kaynaklar

- [FreeCAD Working Directory Wiki](https://wiki.freecad.org/Preferences#General)
- [FreeCAD Python API](https://wiki.freecad.org/FreeCAD_API)
- [Assembly4 Documentation](https://github.com/Zolko-123/FreeCAD_Assembly4)
- [FreeCAD Macro Recipes](https://wiki.freecad.org/Macro_recipes)

---

**Son Güncelleme:** 2026-04-04  
**Proje:** LiSEC GFB-60/30RE CNC Cam Kesme Makinesi
