# FreeCAD MCP Entegrasyonu

CNC Revizyon projesi için FreeCAD kontrolü via Model Context Protocol (MCP).

## 📋 Genel Bakış

Bu entegrasyon ile VS Code'taki Cline üzerinden FreeCAD'i kontrol edebilirsiniz:

- **FreeCAD CLI**: Komut satırı üzerinden Python script çalıştırma
- **FreeCAD Python API**: Doğrudan modelleme ve assembly işlemleri
- **Assembly4 Desteği**: Montaj işlemleri
- **Export**: STEP, DXF, STL, PNG formatları

## 🛠️ Kurulum

### 1. Bağımlılıkları Yükleyin

```bash
cd /Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration
pip install -r requirements.txt
```

### 2. FreeCAD Kurulumunu Kontrol Edin

```bash
# macOS'ta FreeCAD CLI'nin yolunu kontrol edin
which FreeCAD

# Eğer bulunamazsa, tam yol kullanın:
# /Applications/FreeCAD.app/Contents/MacOS/FreeCAD
```

### 3. MCP Sunucusunu Başlatın

MCP sunucusu otomatik olarak VS Code/Cline tarafından başlatılır. Manuel test için:

```bash
cd /Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration
python3 mcp_server.py
```

## 🔧 Kullanılabilir FreeCAD Tool'ları

### 1. `freecad_run_script`
FreeCAD CLI ile özel Python script çalıştırır.

**Parametreler:**
- `script`: Çalıştırılacak Python kodu
- `script_name`: Script adı (varsayılan: "temp_script")
- `timeout`: Maksimum çalışma süresi (saniye, varsayılan: 120)

**Örnek:**
```python
script = """
import FreeCAD as App
import Part

doc = App.newDocument("Test")
box = Part.makeBox(100, 50, 30)
obj = doc.addObject("Part::Feature", "Box")
obj.Shape = box
doc.recompute()
print("Kutu oluşturuldu!")
"""
```

### 2. `freecad_open`
FreeCAD dosyası açar ve içeriğini listeler.

**Parametreler:**
- `file_path`: Açılacak .FCStd dosya yolu
- `readonly`: Salt okunur aç (varsayılan: False)

**Örnek:**
```
file_path: "30RE CNC Assembly4.FCStd"
```

### 3. `freecad_create_part`
Yeni 3D parça oluşturur.

**Parametreler:**
- `part_type`: box, cylinder, sphere, cone
- `parameters`: Boyut parametreleri
- `output_file`: Çıktı dosya adı

**Örnek:**
```json
{
  "part_type": "box",
  "parameters": {"length": 100, "width": 50, "height": 30},
  "output_file": "test_box.stp"
}
```

### 4. `freecad_export`
FreeCAD dosyasını export eder.

**Parametreler:**
- `input_file`: Kaynak .FCStd dosyası
- `output_format`: STEP, DXF, STL, PNG
- `output_file`: Çıktı dosya adı (opsiyonel)

**Örnek:**
```json
{
  "input_file": "30RE CNC Assembly4.FCStd",
  "output_format": "STEP",
  "output_file": "full_assembly.stp"
}
```

### 5. `freecad_list_documents`
FreeCAD dizinindeki tüm .FCStd dosyalarını listeler.

**Parametreler:** Yok

### 6. `freecad_assembly_info`
Assembly4 dosyasından bilgi alır.

**Parametreler:**
- `assembly_file`: Assembly4 .FCStd dosya yolu

**Örnek:**
```
assembly_file: "06_Assembly/30RE CNC Assembly4.FCStd"
```

### 7. `freecad_assembly4_add_part`
Assembly4 montajına yeni parça ekler.

**Parametreler:**
- `part_name`: Parça adı
- `part_type`: box, cylinder
- `parameters`: Boyut parametreleri
- `assembly_file`: Hedef Assembly4 dosyası

**Örnek:**
```json
{
  "part_name": "Motor_Mount",
  "part_type": "box",
  "parameters": {"length": 100, "width": 80, "height": 20},
  "assembly_file": "06_Assembly/30RE CNC Assembly4.FCStd"
}
```

## 📁 Makro Klasörü

Proje dizininde kullanıma hazır makro scriptleri:

```
CAD/FreeCAD/
├── 00_Common/
│   ├── Setup_WorkingDirectory.py    # Çalışma dizini kurulumu
│   ├── Macro_Box.py                 # Parametrik kutu
│   └── Macro_Cylinder.py            # Parametrik silindir
├── 06_Assembly/
│   └── Macro_Assembly4.py           # Assembly4 işlemleri
└── 07_Exports/
    └── Macro_Export.py              # STEP/DXF/STL/PNG export
```

### Makro Kullanımı

FreeCAD Python Console'da:

```python
# Kutu oluştur
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/00_Common/Macro_Box.py").read())
create_parametric_box(100, 50, 30)

# Assembly4 yapısı oluştur
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/Macro_Assembly4.py").read())
create_assembly4_structure()

# Export
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/07_Exports/Macro_Export.py").read())
export_all_objects(App.ActiveDocument, "my_assembly")
```

## 🧪 Test

MCP entegrasyonunu test etmek için:

```bash
cd /Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration
python3 test_freecad_mcp.py
```

## 📊 Cline Kullanımı

VS Code'ta Cline ile kullanım örnekleri:

### Örnek 1: Basit Parça Oluşturma

```
FreeCAD ile 100x50x30 mm boyutlarında bir kutu oluştur ve STEP formatında kaydet.
```

### Örnek 2: Assembly Dosyasını Açma

```
30RE CNC Assembly4.FCStd dosyasını aç ve içindeki objeleri listele.
```

### Örnek 3: Export İşlemi

```
Tüm assembly'yi STEP formatında export et.
```

### Örnek 4: Özel Script Çalıştırma

```
FreeCAD'te çalışan bir Python script ile dişli silindir oluştur.
```

## 🔧 Sorun Giderme

### FreeCAD Bulunamadı Hatası

```bash
# FreeCAD yolunu kontrol edin
which FreeCAD

# Tam yol ile test edin
/Applications/FreeCAD.app/Contents/MacOS/FreeCAD --console --script test.py
```

### Assembly4 Workbench Bulunamadı

1. FreeCAD'i açın
2. **Tools → Addon Manager** menüsüne gidin
3. **Assembly4** arayın ve yükleyin
4. FreeCAD'i yeniden başlatın

### Script Timeout

Script çalıştırma 120 saniyeyi aşarsa timeout hatası alırsınız. `timeout` parametresi ile bu süreyi artırabilirsiniz:

```json
{
  "script": "...",
  "timeout": 300
}
```

## 📚 Kaynaklar

- [FreeCAD Python API](https://wiki.freecad.org/FreeCAD_API)
- [FreeCAD Part Workbench](https://wiki.freecad.org/Part_Workbench)
- [Assembly4 Documentation](https://github.com/Zolko-123/FreeCAD_Assembly4)
- [MCP Protocol](https://modelcontextprotocol.io/)

---

**Son Güncelleme:** 2026-04-13
**Proje:** LiSEC GFB-60/30RE CNC Cam Kesme Makinesi Revizyonu
