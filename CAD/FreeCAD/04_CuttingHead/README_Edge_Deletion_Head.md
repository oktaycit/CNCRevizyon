# Glass Edge Deletion Head - LiSEC GFB Style

## Genel Bakış

Cam kenar silme / rodaj kafası parametrik FreeCAD modeli. LiSEC GFB serisi cam kesme makineleri için tasarlanmıştır.

## Özellikler

### Teknik Spesifikasyonlar

| Bileşen | Parametre | Değer |
|---------|-----------|-------|
| **Taşlama Çarkı** | Çap | Ø150 mm |
| | Kalınlık | 20 mm |
| | Grain Size | 120 |
| **Motor** | Güç | 2.2 kW |
| | Devir | 3000 rpm |
| | Gövde Çapı | Ø180 mm |
| **Vakum Sistemi** | Port Çapı | Ø40 mm |
| | Port Uzunluğu | 100 mm |
| **Taban Plakası** | Uzunluk | 200 mm |
| | Genişlik | 150 mm |
| | Kalınlık | 15 mm |
| **Ayarlama** | Açı | 0-90° (parametrik) |
| | Strok | 50 mm |

### Bileşenler

1. **Grinding_Wheel** - Taşlama çarkı (peripheral grinding)
2. **Motor_Housing** - Dikey mil motor gövdesi
3. **Vacuum_Shroud** - Yarım daire koruyucu + toz emiş
4. **Base_Plate** - Dikdörtgen montaj plakası
5. **Adjustment_Mechanism** - Lineer ayarlama mekanizması
6. **Protective_Guard** - Şeffaf koruyucu siper

## Kurulum

### Gereksinimler

- FreeCAD 1.0+
- Python 3.8+

### Modeli Açma

#### Yöntem 1: Python Console (Önerilen)

1. FreeCAD'i açın
2. **View → Panels → Python Console** seçin
3. Script'i kopyalayıp yapıştırın:

```python
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/04_CuttingHead/Glass_Edge_Deletion_Head_Generator.py").read())
create_glass_edge_deletion_head()
```

#### Yöntem 2: Macro Editörü

1. FreeCAD'de **Macro → Macros...** seçin
2. **Create** → `EdgeDeletionHead`
3. **Edit** → Script içeriğini kopyalayıp yapıştırın
4. **Run** → Çalıştır

#### Yöntem 3: CLI

```bash
FreeCAD -c "exec(open('CAD/FreeCAD/04_CuttingHead/Glass_Edge_Deletion_Head_Generator.py').read()); create_glass_edge_deletion_head()"
```

## Kullanım

### Parametrik Değişiklikler

Script başındaki değişkenleri düzenleyin:

```python
# Taşlama çarkı
wheel_diameter = 150.0    # mm
wheel_width = 20.0        # mm

# Motor
motor_diameter = 180.0    # mm
motor_height = 220.0      # mm
motor_power = 2.2         # kW

# Vakum
vacuum_port_diameter = 40 # mm
vacuum_port_length = 100  # mm

# Ayarlama
offset_angle = 45.0       # derece
adjustment_travel = 50.0  # mm
```

### Variables Spreadsheet

Model oluşturulduktan sonra `Variables` spreadsheet'inden parametreleri değiştirebilirsiniz:

| Hücre | Alias | Açıklama |
|-------|-------|----------|
| A1 | `wheel_diameter` | Taşlama çarkı çapı |
| A2 | `wheel_width` | Taşlama çarkı kalınlığı |
| A3 | `offset_angle` | Taşlama açısı |
| A4 | `motor_power` | Motor gücü |
| A5 | `vacuum_port_dia` | Vakum portu çapı |

### Montaj Koordinatları

```
Z Ekseni (Dikey):
  ↑
  |  Motor Housing (Ø180 x 220mm)
  |  │
  |  ├─────────────────────┐
  |  │ Vacuum Shroud       │
  |  │  (Ø40mm port)       │
  |  │    ╭─────╮          │
  |  │    │Wheel│ ← Z=0 (cam yüzeyi)
  |  │    ╰─────╯          │
  |  └─────────────────────┘
  |─────────────────────────────→ Y Ekseni
  │  Base Plate (200x150x15mm)
  │
  Z=0 (Cam yüzeyi referansı)
```

**Önemli:** Taşlama çarkının alt kenarı **Z=0**'da konumlandırılmıştır (cam yüzeyi temas noktası).

## Dışa Aktarma

### STEP Formatı

```python
import Part
doc = App.ActiveDocument
Part.export(
    [
        doc.getObject("Base_Plate"),
        doc.getObject("Grinding_Wheel"),
        doc.getObject("Motor_Housing"),
        doc.getObject("Vacuum_Shroud"),
        doc.getObject("Adjustment_Mechanism"),
        doc.getObject("Protective_Guard"),
    ],
    "/path/to/Edge_Deletion_Head.step"
)
```

### STL Formatı (3D Yazıcı)

1. **Mesh Design** Workbench'e geçin
2. **Part → Create mesh from shape**
3. Deviation value: `0.1` (yüksek çözünürlük)
4. **File → Export mesh** → STL seçin

## Render

### Görünüm Ayarları

```python
# Vakum koruyucu şeffaflık
doc.getObject("Vacuum_Shroud").ViewObject.Transparency = 20

# Koruyucu siper şeffaflık (polycarbonate)
doc.getObject("Protective_Guard").ViewObject.Transparency = 60

# Taşlama çarkı materyal
doc.getObject("Grinding_Wheel").ViewObject.ShapeColor = (0.75, 0.70, 0.65)
```

### View Referansları

İzometrik görünüm için:
- **View → Standard Views → Isometric** (veya `0` tuşu)
- **View → Fit All** (veya `V` tuşu)

## Mekanik Tasarım Detayları

### Taşlama Çarkı Montajı

```
        ┌─────────────────┐
        │   Motor Shaft   │ ← Dikey mil (Z ekseni)
        └────────┬────────┘
                 │
        ┌────────▼────────┐
        │   Flange (4xM8) │ ← Çark bağlantısı
        └────────┬────────┘
                 │
        ╭────────┴────────╮
        │  Grinding Wheel │ ← Ø150 x 20mm
        │    (120 grit)   │
        ╰────────┬────────╯
                 │
                 ▼ Z=0 (Cam yüzeyi)
```

### Vakum Sistemi

- **Port Çapı:** Ø40mm (standart endüstriyel)
- **Konum:** Koruyucu üst kısmında (toz yerçekimi ile düşer)
- **Flanş:** Ø70mm (hızlı bağlantı için)

### Ayarlama Mekanizması

- **Tip:** Lineer ray + leadscrew (M16)
- **Strok:** 50mm
- **Açı:** 0-90° (manuel ayar)
- **Handwheel:** Ø50mm (ergonomik)

## Sorun Giderme

### Model Görünmüyor

```python
# View → Fit All yapın veya:
Gui.SendMsgToActiveView("ViewFit")

# Tüm objeleri görünür yapın:
for obj in App.ActiveDocument.Objects:
    if hasattr(obj, "ViewObject"):
        obj.ViewObject.Visibility = True
```

### Parametreler Değişmiyor

1. Script'i tekrar çalıştırın
2. Veya Variables spreadsheet'inden manuel değiştirin
3. **Document → Refresh** (F5)

### Boolean Operation Hatası

```python
# Shape doğrulama:
shape = doc.getObject("Grinding_Wheel").Shape
if shape.isNull():
    print("Shape hatası - script'i tekrar çalıştırın")
else:
    print(f"✓ Shape valid: {shape.Volume} mm³")
```

## Kaynaklar

- [FreeCAD Part Workbench](https://wiki.freecad.org/Part_Workbench)
- [FreeCAD Spreadsheet](https://wiki.freecad.org/Spreadsheet_Workbench)
- [LiSEC GFB Teknik Dokümanı](../../../Documentation/Manuals/GFB_Technical_Specs.md)

## Yazar

CNC Revizyon Projesi
Tarih: 2026-04-19
