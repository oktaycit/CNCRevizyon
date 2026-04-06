# FreeCAD Assembly4 Workbench - Montaj ve Simülasyon Rehberi

## Genel Bakış

Bu rehber, **GFB-60/30RE CNC Cam Kesme Makinesi** projesi için FreeCAD Assembly4 Workbench kullanarak:
- Parçaları LCS'lere göre hizalamayı
- Constraint'leri (Fixed, Slider) tanımlamayı
- Simülasyon yapmayı

için adım adım talimatlar içerir.

---

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `Assembly4_Complete.py` | Ana montaj scripti - LCS, Constraint, Simülasyon |
| `Assembly4_Montage.py` | Temel Assembly4 kurulum scripti |
| `Assembly4_Import_STEP.py` | STEP dosyalarını import etme scripti |
| `Main_Assembly.py` | Part workbench ile basitleştirilmiş montaj |

---

## Kurulum

### 1. Assembly4 Workbench'i Yükleyin

```
1. FreeCAD'i açın
2. Tools → Addon Manager'a gidin
3. "Assembly4" arayın ve yükleyin
4. FreeCAD'i yeniden başlatın
```

### 2. Script'i Çalıştırın

FreeCAD Python Console'da:

```python
# Ana montaj scriptini çalıştır
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/Assembly4_Complete.py").read())
run_assembly4_complete()
```

Veya FreeCAD'i komut satırından:

```bash
freecad -c "exec(open('CAD/FreeCAD/06_Assembly/Assembly4_Complete.py').read()); run_assembly4_complete()"
```

---

## Adım Adım Montaj İşlemi

### ADIM 1: Assembly4 Workbench'e Geçin

```
View → Workbench → Assembly4
```

### ADIM 2: Model Hiyerarşisi

Script otomatik olarak şu yapıyı oluşturur:

```
Model
├── X Ekseni
│   └── LCS_X_Axis
│       ├── LCS_X_Rail_Left
│       ├── LCS_X_Rail_Right
│       ├── LCS_X_Motor
│       └── ...
├── Y Ekseni
│   └── LCS_Y_Axis
│       └── ...
├── Z Ekseni
│   └── LCS_Z_Axis
│       └── ...
├── Şase
│   └── LCS_Frame
│       └── ...
├── Constraints
│   ├── Fixed_Frame_Base
│   ├── Slider_X_Gantry
│   ├── Slider_Y_Carriage
│   └── Slider_Z_Head
├── Simulation
│   ├── X_Ekseni_Hareketi
│   ├── Y_Ekseni_Hareketi
│   └── Z_Ekseni_Hareketi
├── Variables (Spreadsheet)
├── Animation (Spreadsheet)
├── Assembly_Instructions (Spreadsheet)
└── BOM (Spreadsheet)
```

### ADIM 3: STEP Dosyalarını Import Edin

```
File → Import → STEP
```

İçe aktarılacak dosyalar:

```
07_Exports/STEP/
├── Frame/
│   ├── MainFrame_Profiles.stp
│   └── SupportLeg.stp
├── LinearGuides/
│   ├── HIWIN_HGH25_X_Rail.stp
│   ├── HIWIN_HGH25_Y_Rail.stp
│   └── HIWIN_HGH25_Block.stp
├── Motors/
│   ├── ECMA-L11845.stp (X ekseni)
│   ├── ECMA-E11320.stp (Y ekseni)
│   └── ECMA-C11010.stp (Z ekseni)
├── CuttingHead/
│   ├── ZAxis_Housing.stp
│   ├── ZAxis_Slide.stp
│   └── Cutting_Wheel.stp
└── Electronics/
    ├── R1-EC_Housing.stp
    └── Cable_Carrier.stp
```

### ADIM 4: Parçaları LCS'lere Göre Hizalayın

#### Assembly4'te Hizalama Yöntemi:

1. **Model ağacında parçayı seçin**
2. **Assembly → Place Part** menüsüne gidin
3. **Hedef LCS'yi seçin**
4. **Attachment modunu ayarlayın:**
   - `Coincident` - İki yüzey/eks çakışık
   - `Offset` - Belirli mesafe ile
   - `Angle` - Açısal hizalama

#### Örnek Hizalamalar:

| Parça | Hedef LCS | Attachment |
|-------|-----------|------------|
| X_Rail_Left | LCS_X_Rail_Left | Coincident |
| X_Rail_Right | LCS_X_Rail_Right | Coincident |
| Motor_X | LCS_X_Motor | Coincident |
| Y_Rail | LCS_Y_Rail | Coincident |
| Z_Housing | LCS_Z_Housing | Coincident |

### ADIM 5: Constraint'leri Tanımlayın

#### FIXED Constraint (Sabit Bağlantılar)

Şase parçaları ve motorlar gibi **hareket etmeyen** parçalar için:

```
Assembly → Add Constraint → Fixed
```

**Kullanım:**
- Şase profilleri → `Fixed_Frame_Base`
- Motorlar → `Fixed_Motor_X`, `Fixed_Motor_Y`, `Fixed_Motor_Z`
- Lineer raylar → `Fixed_X_Rail`

#### SLIDER Constraint (Lineer Hareket)

X, Y, Z eksenleri gibi **lineer hareket eden** parçalar için:

```
Assembly → Add Constraint → Slider
```

**Ayarlar:**
| Constraint | Yön | Min Limit | Max Limit |
|------------|-----|-----------|-----------|
| Slider_X_Gantry | (1, 0, 0) X | 0 mm | 6000 mm |
| Slider_Y_Carriage | (0, 0, 1) Z | 100 mm | 2900 mm |
| Slider_Z_Head | (0, 1, 0) Y | 0 mm | 300 mm |

#### ROTATOR Constraint (Döner Hareket)

Kesim tekeri gibi **dönen** parçalar için:

```
Assembly → Add Constraint → Rotator
```

**Ayarlar:**
| Constraint | Eksen | Min Açı | Max Açı |
|------------|-------|---------|---------|
| Rotator_Wheel | (1, 0, 0) X | 0° | 360° |

### ADIM 6: Simülasyon Yapın

#### Animation Table Kullanımı:

1. **Assembly → Animation** menüsüne gidin
2. **Animation Table'ı seçin** (`Motion_Simulation` spreadsheet)
3. **Play** butonuna basın

#### Animasyon Parametreleri:

| Eksen | Başlangıç | Bitiş | Süre |
|-------|-----------|-------|------|
| X | 0 mm | 6000 mm | 10 saniye |
| Y | 0 mm | 3000 mm | 8 saniye |
| Z | 0 mm | 300 mm | 5 saniye |

#### Manuel Simülasyon:

```python
# Python Console'da manuel simülasyon
import math

doc = App.getDocument("GFB-60-30RE_Assembly4")

# X ekseni pozisyonu
for t in range(0, 101, 5):
    x_pos = 3000 + 2000 * math.sin(2 * math.pi * t / 100)
    doc.getObject("X_Gantry").Placement.Base.x = x_pos
    doc.recompute()
```

---

## Değişken Tablosu (Variables)

Assembly4, parametreleri Spreadsheet ile yönetir. `Variables` spreadsheet'ini düzenleyerek:

- Makine boyutlarını
- Hız parametrelerini
- Home pozisyonlarını

değiştirebilirsiniz.

### Önemli Parametreler:

| Parametre | Değer | Birim | Açıklama |
|-----------|-------|-------|----------|
| A0_Machine_Length | 6000 | mm | X ekseni uzunluğu |
| A0_Machine_Width | 3000 | mm | Y ekseni genişliği |
| A0_Machine_Height | 800 | mm | Şase yüksekliği |
| A0_X_Travel | 6000 | mm | X ekseni hareket mesafesi |
| A0_Y_Travel | 3000 | mm | Y ekseni hareket mesafesi |
| A0_Z_Travel | 300 | mm | Z ekseni hareket mesafesi |

---

## Sorun Giderme

### Parçalar Hizalanmıyor

1. LCS'nin doğru pozisyonda olduğundan emin olun
2. Attachment modunu kontrol edin
3. `Placement` expression'ını kontrol edin

### Constraint Çalışmıyor

1. Constraint tipinin doğru olduğundan emin olun
2. Parent/Target bağlantılarını kontrol edin
3. Limit değerlerini gözden geçirin

### Simülasyon Hatası

1. Animation Table'ın doğru formüllere sahip olduğunu kontrol edin
2. Tüm parçaların constraint'lerinin tanımlı olduğundan emin olun
3. FreeCAD konsolundaki hata mesajlarını kontrol edin

---

## Export

### STEP Export:

```
File → Export → STEP
```

### PDF Export (Çizim):

```
File → Export → PDF
```

### BOM Export:

```
1. BOM spreadsheet'ini açın
2. File → Export → CSV
```

---

## Faydalı İpuçları

1. **LCS Renkleri:** Farklı eksenler için farklı LCS renkleri kullanın
2. **Gruplama:** Benzer parçaları gruplarda toplayın
3. **Yedekleme:** Her önemli değişiklikten sonra kaydedin
4. **Test:** Constraint ekledikten sonra hareketi test edin

---

## Kaynaklar

- [Assembly4 Dokümantasyonu](https://github.com/Zolko-123/FreeCAD_Assembly4)
- [FreeCAD Python API](https://wiki.freecad.org/FreeCAD_API)
- [Assembly4 Tutorial](https://wiki.freecad.org/Assembly4_Workbench)

---

**Son Güncelleme:** 2026-04-03
**Proje:** GFB-60/30RE CNC Cam Kesme Makinesi