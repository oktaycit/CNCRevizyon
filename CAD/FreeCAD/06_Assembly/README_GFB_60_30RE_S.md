# GFB-60/30RE-S Hibrit Sistem Modeli

## Genel Bakış

Bu FreeCAD modeli, LiSEC GFB-60/30RE-S hibrit cam kesim makinesinin tam montajını içerir. Model, hem düz cam hem de lamine cam (VB-Modul) kesim yeteneklerine sahiptir.

Makine modeli internet ve yerel referanslarla butunlendiginde bu montaj su hat yapisini temsil eder:

- Yukleme: `ATH-60/30D` veya `BSK-60/30 RE-S`
- Ana kesim masasi: `GFB-60/30RE-S`
- Lamine kesim modulu: `VB-45` veya `VB-60`
- Hat sonu: `BTS-60/30`

Bu README'de `GFB-60/30RE-S hibrit sistem` kisa adi, yukaridaki komple hattin merkez kesim modulu uzerinden kullanilmaktadir.

## Özellikler

### Eksenler

| Eksen | Açıklama | Strok | Maks. Hız |
|-------|----------|-------|-----------|
| X | Portal Köprüsü | 6000 mm | 80 m/dk |
| Y | Kafa Yatay Hareket | 3000 mm | 60 m/dk |
| Z | Üst Kesim Kafası | 300 mm | 5 m/dk |
| V | Alt Kesici (VB-Modul) | 300 mm | 60 m/dk |
| C | Rodaj Ekseni | - | - |

### VB-Modul Bileşenleri

1. **Alt Kesici Ünitesi** - Lamine camın alt katmanını keser
2. **Isıtıcı Çubuk (Heizstab)** - PVB filmini yumuşatır (135°C)
3. **Vakum Vantuz Sistemi** - Camı sabitler
4. **Kırma Çıtası (Brechleiste)** - Camı kırar
5. **Ayırma Bıçağı (Trennklinge)** - Cam katmanlarını ayırır
6. **Basınç Rollesi (Andrückrolle)** - Kesim sırasında camı sabitler

## Kurulum

### Gereksinimler

- FreeCAD 1.0+ (Assembly4 Workbench yüklü)
- Python 3.8+

### Modeli Açma

#### Yöntem 1: FreeCAD GUI ile

1. FreeCAD'i açın
2. `Tools → Macro → Macros...` menüsüne gidin
3. `GFB_60_30RE_S_Model.py` dosyasını seçin
4. `Execute` butonuna tıklayın

#### Yöntem 2: CLI ile (Önerilen)

Terminal'den doğrudan çalıştırma:

```bash
# Script ile çalıştır
./CAD/FreeCAD/06_Assembly/run_gfb_60_30re_s.sh

# Veya doğrudan FreeCAD CLI ile
FreeCAD -c "exec(open('CAD/FreeCAD/06_Assembly/GFB_60_30RE_S_Model.py').read()); create_complete_machine()"
```

#### Yöntem 3: Python Konsolundan

FreeCAD Python konsolunda:

```python
exec(open("/path/to/GFB_60_30RE_S_Model.py").read())
create_complete_machine()
```

## Kullanım

### Manuel Hareket

Variables spreadsheet'ini kullanarak eksenleri manuel hareket ettirebilirsiniz:

```python
# X ekseni pozisyonu (0-6000 mm)
Variables.A1 = 1000  # mm

# Y ekseni pozisyonu (0-3000 mm)
Variables.B1 = 500  # mm

# Z ekseni pozisyonu (0-300 mm, ters yönde)
Variables.C1 = 150  # mm

# V ekseni pozisyonu (0-300 mm, alt kesici)
Variables.D1 = 100  # mm
```

Daha guvenli manuel kontrol icin:

```python
set_axis_positions(App.ActiveDocument, x=1000, y=500, z=150, v=100)
```

### Simülasyon Çalıştırma

Lamine cam kesim simülasyonu:

```python
from GFB_60_30RE_S_Model import *
doc = App.ActiveDocument
params = MachineParameters()
run_lamine_cutting_simulation(doc, params, duration_sec=30)
```

NC300 orta seviye simülatörü ile canlı sürmek için:

```python
doc = App.ActiveDocument
run_nc300_lamine_cycle(doc, 25.0)
```

NC dosyasını doğrudan model üzerinde oynatmak için:

```python
doc = App.ActiveDocument
run_nc_file_simulation(
    doc,
    "/Users/oktaycit/Projeler/CNCRevizyon/Firmware/NC300/GCode/Standard_Cut.nc",
)
```

Kesim programinin urettigi son NC dosyasini otomatik bulup oynatmak icin:

```python
doc = App.ActiveDocument
run_nc_file_simulation(doc)
```

Runtime siparislerinden yeni NC uretmek icin:

```python
result = generate_nc_from_current_orders()
print(result["gcode_file"])
run_nc_file_simulation(App.ActiveDocument, result["gcode_file"])
```

Sekilli siparisler icin deneme konturu uretmek icin:

```python
shape_result = generate_shape_trial_nc_from_current_orders()
print(shape_result["gcode_file"])
run_nc_file_simulation(App.ActiveDocument, shape_result["gcode_file"])
```

Gercek kontur verisi varsa shape NC uretmek icin:

```python
real_shape_result = generate_real_shape_nc_from_current_orders()
print(real_shape_result["gcode_file"])
run_nc_file_simulation(App.ActiveDocument, real_shape_result["gcode_file"])
```

Komut satırından:

```python
main([
    "--nc-file",
    "/Users/oktaycit/Projeler/CNCRevizyon/Firmware/NC300/GCode/Standard_Cut.nc",
])
```

JSON raporu ile birlikte:

```python
main([
    "--generate-current-orders-nc",
    "--nc-report",
])
```

Sekilli deneme NC akisi:

```python
main([
    "--generate-shape-trial-nc",
    "--nc-report",
])
```

Gercek shape NC akisi:

```python
main([
    "--generate-real-shape-nc",
    "--nc-report",
])
```

Siparis dosyasini acikca vermek istersen:

```python
main([
    "--generate-current-orders-nc",
    "--current-orders-path",
    "/Users/oktaycit/Projeler/CNCRevizyon/AI/GlassCuttingProgram/data/runtime/current_orders.json",
    "--nc-report",
])
```

Not:
- Script artık GUI olmayan `FreeCAD -c` çalıştırmalarında da güvenli şekilde açılır.
- Kinematik eşleme FreeCAD eksenlerinde şu şekilde uygulanır: makine `X -> FreeCAD Z`, makine `Y -> FreeCAD X`, makine `Z/V -> FreeCAD Y`.
- Model açıldığında `Lamine_IO` ve `Lamine_Phases` spreadsheet'leri de oluşur.
- `parse_nc_file()` temel NC çözümleyicisidir; `run_nc_file_simulation()` bunu FreeCAD oynatımına çevirir.
- `run_nc_file_simulation(doc)` parametresiz cagrildiginda once `AI/GlassCuttingProgram/output/gcode` altindaki son uretilen NC dosyasini arar.
- `generate_nc_from_current_orders()` runtime siparislerini yerel nesting + 2-opt yol optimizasyonu + NC300 G-code jenerasyonu ile `.nc` dosyasina cevirir.
- `generate_real_shape_nc_from_current_orders()` `ShapeBaseString` veya son DXF importundan gelen gercek konturu kullanmayi dener.
- `generate_shape_trial_nc_from_current_orders()` ise `is_shape=true` satirlar icin temsilci polygon kontur uretir; gercek kontur koordinati olmadiginda deneme amaclidir.
- Şu anda `G00`, `G01`, `G02`, `G03`, `G28`, `G90`, `G91`, `F`, `M03`, `M05`, `M08`, `M09` desteklenir.
- NC oynatımında çıkarım olarak `Z0 -> güvenli yükseklik`, `Z-5 -> kesim yüksekliği` eşlemesi kullanılır.
- `--nc-report` ile yazılan JSON raporu tahmini çevrim süresi, toplam kesim uzunluğu ve spindle/vakum olay kaydı da içerir.

NC raporunda bulunan ana alanlar:

| Alan | Açıklama |
|------|----------|
| `estimated_duration_s` | Toplam tahmini çevrim süresi |
| `estimated_cut_duration_s` | Kesim/yay hareketlerinin tahmini süresi |
| `estimated_rapid_duration_s` | Rapid/home hareketlerinin tahmini süresi |
| `total_cut_length_mm` | NC uzayında toplam kesim uzunluğu |
| `total_rapid_length_mm` | NC uzayında toplam hızlı hareket uzunluğu |
| `event_log` | `spindle_on/off`, `vacuum_on/off`, `cycle_complete` zaman çizelgesi |

### Faz ve I/O Mantığı

Simülasyon artık yalnızca eksen animasyonu değil, faz bazlı proses akışı da içerir.

Oluşturulan spreadsheet'ler:

- `Lamine_IO`: dijital giriş ve çıkışların anlık 0/1 durumu
- `Lamine_Phases`: her fazın giriş şartları, aktif çıkışları ve bir sonraki fazı

Temel faz akışı:

| Faz | Giriş Şartı | Aktif Çıkışlar | Sonraki Faz |
|-----|-------------|----------------|-------------|
| Bekleme | START_CMD, ESTOP_OK, DOOR_CLOSED, AIR_PRESSURE_OK | Servo enable'lar | Yükleme |
| Yükleme | GLASS_DETECT, VACUUM_OK | VACUUM_PUMP, PRESSURE_ROLLER | Isıtıcı İniş |
| Isıtıcı İniş | HEATER_DOWN_OK | HEATER_DOWN | Isıtma |
| Isıtma | HEATER_DOWN_OK, TEMP_READY | HEATER_ENABLE, VACUUM_PUMP | Isıtıcı Kalkış |
| Üst Kesim Hazırlık | UPPER_HEAD_READY | UPPER_CUT_ENABLE | Üst Kesim |
| Alt Kesici Hazırlık | LOWER_HEAD_READY | LOWER_CUT_ENABLE | Senkronize Kesim |
| Senkronize Kesim | UPPER_CUT_OK, LOWER_CUT_OK | UPPER_CUT_ENABLE, LOWER_CUT_ENABLE | Kafalar Yukarı |
| Ayırma | SEPARATION_OK | SEPARATING_BLADE | Kırma |
| Kırma | BREAK_OK | BREAKING_BAR, PRESSURE_ROLLER | Boşaltma |
| Boşaltma | UNLOAD_READY | CYCLE_COMPLETE | Tamamlandı |

### NC Dosyası ve I/O Eşlemesi

NC oynatımı sadece eksenleri değil, temel proses çıkışlarını da `Lamine_IO` sheet'ine yazar.

Varsayılan eşlemeler:

| NC Komutu | Model Çıkışı |
|-----------|--------------|
| `M03` | `UPPER_CUT_ENABLE=1`, `PRESSURE_ROLLER=1` |
| `M05` | `UPPER_CUT_ENABLE=0`, `PRESSURE_ROLLER=0` |
| `M08` | `VACUUM_PUMP=1` |
| `M09` | `VACUUM_PUMP=0` |
| Kesim hareketi (`G01`) | spindle açıksa `UPPER_CUT_ENABLE=1` korunur |
| Program sonu | `CYCLE_COMPLETE=1` |

Not:
- Bu eşleme proses mantığından türetilmiş görsel/senaryo amaçlı bir modeldir.
- NC dosyası gerçek NC300 register çevrimine değil, FreeCAD playback katmanına bağlanır.

## Model Parametreleri

### Kesim Parametreleri

| Parametre | Değer | Birim |
|-----------|-------|-------|
| Düz Cam Kalınlığı | 16 | mm |
| Lamine Cam Kalınlığı | 8.76 (4+0.76+4) | mm |
| Kesim Basıncı | 0.4 | MPa |
| Isıtma Sıcaklığı | 135 | °C |
| Isıtma Süresi | 4 | sn |
| Vakum Basıncı | 0.8 | bar |
| Ayırma Basıncı | 2.8 | bar |
| Kırma Basıncı | 4.0 | bar |

## Lamine Kesim Süreci

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lamine Kesim Döngüsü                         │
│                                                                 │
│  1. Cam Yükleme                                                 │
│     └─ Vakum aktif, cam sabitlenir                              │
│                                                                 │
│  2. Isıtma Fazı (Heizstab)                                      │
│     ├─ Isıtıcı aşağı (2 sn)                                     │
│     ├─ Isıtma (3-5 sn, 135°C)                                   │
│     └─ Isıtıcı yukarı (1 sn)                                    │
│                                                                 │
│  3. Üst Kesim (Z Ekseni)                                        │
│     ├─ Kesim kafası aşağı                                       │
│     ├─ Çizim (G01, F=2000 mm/dk)                                │
│     └─ Kesim kafası yukarı                                      │
│                                                                 │
│  4. Alt Kesim (V Ekseni) - Senkronize                           │
│     ├─ V ekseni Y ile aynı pozisyona                            │
│     ├─ Alt kesici yukarı (temas)                                │
│     ├─ Çizim (senkronize Y ile)                                 │
│     └─ Alt kesici aşağı                                         │
│                                                                 │
│  5. Ayırma (Trennklinge)                                        │
│     ├─ Ayırma bıçağı cam altına                                 │
│     ├─ Hafif yukarı basınç                                      │
│     └─ Y ekseni hareketi ile ayırma                             │
│                                                                 │
│  6. Kırma (Brechleiste)                                         │
│     ├─ Kırma çıtası aşağı                                       │
│     ├─ Cam kenarından yukarı basınç                             │
│     └─ Cam kırılır                                              │
│                                                                 │
│  7. Cam Boşaltma                                                │
│     └─ Vakum pasif, cam alınır                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Dosya Yapısı

```
CAD/FreeCAD/
├── 06_Assembly/
│   ├── GFB_60_30RE_S_Model.py    # Ana model script
│   ├── README_GFB_60_30RE_S.md   # Bu dosya
│   ├── Complete_Machine_Simulation.py  # Orijinal simülasyon
│   └── Assembly4_LamineCam_ECam.py     # E-Cam profili
├── 07_Exports/
│   └── STEP/
│       └── Assembly/           # STEP dışa aktarımları
└── 00_Common/
    └── Setup_WorkingDirectory.py
```

## Servo Motor Konfigürasyonu

### X Ekseni (Portal)

- **Motor:** Delta ECMA-E11320 (2.0kW)
- **Sürücü:** Delta ASD-A3-2023-E
- **Kodlayıcı:** 24-bit absolute

### Y Ekseni (Kafa Yatay)

- **Motor:** Delta ECMA-E11315 (1.5kW)
- **Sürücü:** Delta ASD-A3-1523-E
- **Kodlayıcı:** 24-bit absolute

### Z Ekseni (Üst Kesim)

- **Motor:** Delta ECMA-C11010 (1.0kW)
- **Sürücü:** Delta ASD-A3-1023-E

### V Ekseni (Alt Kesici)

- **Motor:** Delta ECMA-E11315 (1.5kW, IP67)
- **Sürücü:** Delta ASD-A3-1523-E
- **Kodlayıcı:** 24-bit absolute

## I/O Dağılımı

FreeCAD simülasyonunda kullanılan proses sinyalleri, firmware tasarımındaki adlandırmaya yakın tutulmuştur.

### Dijital Girişler (DI)

| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %IX0.0-15 | Düz Cam Sensörleri | Ana sistem |
| %IX1.0-15 | Limit Switches | Eksen limitleri |
| %IX2.0-15 | VB-Modul Sensörleri | Lamine modül |

### Dijital Çıkışlar (DO)

| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %QX0.0-15 | Düz Cam Çıkışlar | Ana sistem |
| %QX1.0-15 | Servo Kontrol | Eksen enable |
| %QX2.0-15 | VB-Modul Çıkışlar | Lamine modül |

## Sorun Giderme

### Model Görünmüyor

- FreeCAD'de `View → Fit All` yapın
- Assembly4 Workbench'in yüklü olduğundan emin olun

### Kinematik Bağlantılar Çalışmıyor

- Variables spreadsheet'inin varlığını kontrol edin
- Expression'ların doğru hücrelere atandığını doğrulayın

### Simülasyon Hatası

- Python konsolunda hata mesajlarını kontrol edin
- FreeCAD sürümünüzün 1.0+ olduğunu doğrulayın

## Kaynaklar

- [FreeCAD Assembly4 Dokümantasyonu](https://wiki.freecad.org/Assembly4)
- [Delta ASD-A3-E Manuel](https://www.delta-automation.com)
- [LiSEC GFB-60/30RE-S Teknik Dokümanı](../../../Documentation/Manuals/)

## Yazar

CNC AI Orchestrator  
Tarih: 2026-04-04
