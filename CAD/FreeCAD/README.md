# FreeCAD CAD Modelleri - GFB-60/30RE CNC Cam Kesme Makinesi

Delta ECMA Servo Motorları ile donatılmış CNC cam kesme makinesi için FreeCAD parametrik modelleme dosyaları.

## 📁 Dizin Yapısı

```
CAD/FreeCAD/
├── 00_Common/              # Ortak bileşenler, standart parçalar
├── 01_Motors/              # ECMA Servo Motor modelleri
│   ├── ECMA_Motor_Generator.py
│   ├── ECMA_Motor_STEP_Export.py
│   └── README.md
├── 02_Frame/               # Şase (Frame) modelleri
│   └── Frame_Generator.py
├── 03_LinearGuides/        # Lineer raylar (HIWIN HGH25CA)
│   └── HIWIN_HGH25CA_Generator.py
├── 04_CuttingHead/         # Kesim kafası (Z ekseni)
│   └── CuttingHead_Generator.py
├── 05_Electronics/         # Elektronik parçalar
│   └── Electronics_Generator.py
├── 06_Assembly/            # Ana montaj dosyaları
│   └── Main_Assembly.py
└── 07_Exports/
    ├── STEP/
    │   ├── Motors/         # Motor STEP dosyaları
    │   ├── Frame/          # Şase STEP dosyaları
    │   ├── LinearGuides/   # Lineer ray STEP dosyaları
    │   ├── CuttingHead/    # Kesim kafası STEP dosyaları
    │   ├── Electronics/    # Elektronik STEP dosyaları
    │   └── Assembly/       # Montaj STEP dosyaları
    ├── STL/                # 3D yazıcı için STL dosyaları
    └── DXF/                # Lazer kesim için DXF dosyaları
```

## 🚀 Hızlı Başlangıç

### FreeCAD'de Script Çalıştırma

**Yöntem 1: Python Console (Önerilen)**

1. FreeCAD'i açın
2. View → Panels → Python Console (eğer görünmüyorsa)
3. Aşağıdaki komutu yapıştırın:

```python
# Örnek: Motorları oluştur
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/01_Motors/ECMA_Motor_STEP_Export.py").read())
```

**Yöntem 2: Macro Editörü**

1. FreeCAD'de **Macro → Macros...** seçin
2. **Create** butonuna tıklayın
3. Dosya adı girin (örn: `Motorlar`)
4. **Edit** ile açın ve script içeriğini kopyalayıp yapıştırın
5. **Run** butonuna basın

## 📦 Script Dosyaları

### 01_Motors - ECMA Servo Motorlar

| Dosya | Açıklama |
|-------|----------|
| `ECMA_Motor_Generator.py` | Tüm motorları tek FreeCAD dosyasında oluşturur |
| `ECMA_Motor_STEP_Export.py` | Her motoru ayrı STEP dosyası olarak export eder |

**Motor Modelleri:**
- ECMA-L11845 (4.5kW X Ekseni)
- ECMA-E11320 (2.0kW Y Ekseni)
- ECMA-C11010 (1.0kW Frenli Z Ekseni)
- ECMA-E11315 (1.5kW IP67)

### 02_Frame - Şase (Frame)

| Dosya | Açıklama |
|-------|----------|
| `Frame_Generator.py` | 6000x3000 mm şase profilleri, destek ayakları, köşe takviyeleri |

**Çıktılar:**
- MainFrame_Profiles.stp
- SupportLeg.stp
- CornerBracket.stp
- PortalFrame.stp
- Frame_Assembly.stp

### 03_LinearGuides - Lineer Raylar

| Dosya | Açıklama |
|-------|----------|
| `HIWIN_HGH25CA_Generator.py` | HIWIN HGH25CA lineer ray ve kızak modelleri |

**Çıktılar:**
- HIWIN_HGH25_X_Rail.stp (6000 mm)
- HIWIN_HGH25_Y_Rail.stp (3000 mm)
- HIWIN_HGH25_Block.stp
- HIWIN_HGH25_Assembly.stp

### 04_CuttingHead - Kesim Kafası

| Dosya | Açıklama |
|-------|----------|
| `CuttingHead_Generator.py` | Z ekseni, kesim tekeri, kaplaj |

**Çıktılar:**
- ZAxis_Housing.stp
- ZAxis_Slide.stp
- Cutting_Wheel.stp
- Wheel_Mount.stp
- Motor_Coupling.stp
- Cutting_Head_Assembly.stp

### 05_Electronics - Elektronik Parçalar

| Dosya | Açıklama |
|-------|----------|
| `Electronics_Generator.py` | R1-EC modül, sensör braketleri, kablo kanalı |

**Çıktılar:**
- R1-EC_Housing.stp
- R1-EC_Lid.stp
- Sensor_Bracket_Proximity.stp
- Encoder_Bracket.stp
- Cable_Carrier.stp
- Control_Panel_Box.stp
- Junction_Box.stp

### 06_Assembly - Ana Montaj

| Dosya | Açıklama |
|-------|----------|
| `Main_Assembly.py` | Tam makine montajı |

**Çıktılar:**
- XAxis_Assembly.stp
- YAxis_Assembly.stp
- ZAxis_Assembly.stp
- Full_Machine_Assembly.stp

## 🔧 Parametrik Değişiklikler

Her script'teki parametreleri değiştirerek özel modeller oluşturabilirsiniz:

```python
# Örnek: Şase boyutlarını değiştir
FRAME_LENGTH = 8000  # 8 metre
FRAME_WIDTH = 4000   # 4 metre
```

## 📊 Makine Özellikleri

| Özellik | Değer |
|---------|-------|
| Çalışma Alanı | 6000 x 3000 mm |
| X Ekseni Motor | ECMA-L11845 (4.5kW) |
| Y Ekseni Motor | ECMA-E11320 (2.0kW) |
| Z Ekseni Motor | ECMA-C11010 (1.0kW frenli) |
| Lineer Ray | HIWIN HGH25CA |
| Şase Yüksekliği | 800 mm |

## 📝 Notlar

- Tüm ölçüler mm birimindedir
- STEP dosyaları AP214 formatında export edilir
- Montaj delikleri standart metrik cıvatalar için tasarlanmıştır
- Scriptler FreeCAD 1.0+ ile test edilmiştir

## 🔗 Kaynaklar

- [FreeCAD Dokümantasyon](https://wiki.freecad.org/)
- [Delta ECMA Motor Datasheetleri](https://www.delta-automation.com/tr/products/detail/ECMA/)
- [HIWIN Lineer Ray Katalog](https://www.hiwin.com/)