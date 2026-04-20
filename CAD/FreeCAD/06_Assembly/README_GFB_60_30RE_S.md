# GFB-60/30RE-S Hibrit Sistem Modeli

## Genel Bakış

Bu FreeCAD modeli, LiSEC GFB-60/30RE-S hibrit cam kesim makinesinin tam montajını içerir. Model, hem düz cam hem de lamine cam (VB-Modul) kesim yeteneklerine sahiptir.

Makine modeli internet ve yerel referanslarla butunlendiginde bu montaj su hat yapisini temsil eder:

- Yukleme: `ATH-60/30D` veya `BSK-60/30 RE-S`
- Ana kesim masasi: `GFB-60/30RE-S`
- Lamine kesim modulu: `VB-45` veya `VB-60`
- Hat sonu: `BTS-60/30`

Bu README'de `GFB-60/30RE-S hibrit sistem` kisa adi, yukaridaki komple hattin merkez kesim modulu uzerinden kullanilmaktadir.

Revize model mimarisi iki farkli kopruyu ayri ayri gosterir:

- Beyaz kartezyen kopru: `X/Y/Z` ile calisir, uzerinde vakum ve lama silme servisi vardir.
- Lila VB ust koprusu: sabit `X` hattinda duran dar lamine kesim unitesidir; yalniz `Y` yonunde calisir ve alt kafa ile mekanik bagli kabul edilir.

## Özellikler

### Dual Bridge (Çifte Köprü) Sistemi

Makinede **iki farklı köprü** bulunmaktadir:

1. **Kartezyen Köprü (Beyaz Boyalı)**:
   - X, Y, Z eksenleri ile kontrol edilir
   - Vakum ve lama silme servisi bulunur
   - Düz cam kesiminde kullanılır
   - Lamine kesimde park pozisyonuna çekilir (kullanılmaz)

2. **VB Ünitesi (Lila Boyalı, Dar Ünite)**:
   - Sadece Y yönünde hareket eder
   - X yönünde hareket edemez (sabit X konumu)
   - Alt kafa servo, üst kafaya **mekanik bağlı**
   - Lamine kesim için kullanılır
   - **E-Cam gerektirmez** - mekanik bağlantı yeterli

### Eksenler

| Eksen | Açıklama | Strok | Maks. Hız | Köprü |
|-------|----------|-------|-----------|-------|
| X | Kartezyen Portal Köprüsü | 6000 mm | 80 m/dk | Beyaz |
| Y | Kartezyen Üst Kafa Hareketi | 3000 mm | 60 m/dk | Beyaz |
| Z | Üst Kesim Kafası | 300 mm | 5 m/dk | Beyaz |
| VB-Y | VB üst/alt bağlı lamine kesim ekseni | 3000 mm | 60 m/dk | Lila |
| V | Alt Kesici dikey stroku (VB-Modul) | 300 mm | 60 m/dk | Lila |
| C | Rodaj Ekseni | - | - | - |

**ÖNEMLI NOT:** Lamine kesim sırasında:

- Kartezyen köprünün Y ekseni **kullanılmaz** (parkta)
- VB ünitesi Y ekseni **doğrudan hareket** eder (E-Cam gereksiz)
- VB ünitesinde alt kafa servo, üst kafaya **mekanik bağlı**

### VB-Modul Bileşenleri

1. **Dar Lila VB Üst Köprüsü** - Sabit `X` hattında, yalnız `Y` yönünde çalışan üst lamine kesim ünitesi
2. **Alt Kesici Ünitesi** - Lamine camın alt katmanını üst kafa ile tam hizalı olarak skorlar ve aynı `Y` çizgisini izler
3. **SIR Isıtıcı Çubuk (Heizstab)** - PVB folyoyu alttan, yaklaşık `1 mm` standoff ile seçici olarak ısıtır
4. **Vakum Vantuz Sistemi** - Camı sabitler ve gap açma fazında levhaları kontrollü gerer
5. **Kırma Çıtası / Kırma Mekanizması (Brechleiste)** - Skor hattı boyunca camı kırar
6. **Folyo Kesme Bıçağı (Trennklinge)** - Açılan gap içine girerek PVB folyoyu boydan boya keser
7. **Basınç Rollesi / Crush Roller (Andrückrolle)** - Kırma fazında üstten baskı uygular

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

Acik bir belgeyi yeni iki koprulu geometriye yukseltmek icin:

```python
upgrade_existing_document_to_dual_bridge_layout(App.ActiveDocument)
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
- Lamine modunda kartezyen `Y` kafasi parkta tutulur; `Variables.B1` bu durumda VB ust/alt bagli `Y` eksenini surer.
- VB lamine ust koprusu sabit `X` hattindadir; lamine kesimde `E-Cam` yerine mekanik bagli ortak `Y` ekseni varsayimi kullanilir.
- `run_nc_file_simulation()` icinde `#2000` legacy bayragi `E-Cam` olarak degil, `VB_Y_LINK_ENABLE` yani ortak VB-Y kesim linki olarak yorumlanir.
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
| Bekleme | START_CMD, ESTOP_OK, DOOR_CLOSED, AIR_PRESSURE_OK | Servo enable'lar | Cam Yakalama ve Orijinleme |
| Cam Yakalama ve Orijinleme | GLASS_DETECT, VACUUM_OK, SAFE_TO_MOVE_X | VACUUM_PUMP, LOADING_VACUUM_ENABLE | Kenar Probu |
| Kenar Probu | G31_PROBE_INPUT, EDGE_PROBE_OK, SAFE_TO_MOVE_X | VACUUM_PUMP, LOADING_VACUUM_ENABLE, EDGE_PROBE_ENABLE | Kesim Hattina Konumlandirma |
| Kesim Hattina Konumlandirma | VACUUM_OK, SAFE_TO_MOVE_X | VACUUM_PUMP, LOADING_VACUUM_ENABLE | Simetrik Scoring Hazirlik |
| Simetrik Scoring Hazirlik | VACUUM_OK | VB_Y_LINK_ENABLE, VACUUM_PUMP, LOADING_VACUUM_ENABLE, X_AXIS_LOCK | Simetrik Scoring |
| Simetrik Scoring | UPPER_CUT_OK, LOWER_CUT_OK | UPPER_CUT_ENABLE, LOWER_CUT_ENABLE, VB_Y_LINK_ENABLE, VACUUM_PUMP, LOADING_VACUUM_ENABLE | Cam Kirma |
| Cam Kirma | BREAK_OK | BREAKING_BAR, PRESSURE_ROLLER, VACUUM_PUMP, LOADING_VACUUM_ENABLE | PVB Isitma |
| PVB Isitma | HEATER_DOWN_OK, TEMP_READY | HEATER_DOWN, HEATER_ENABLE, HEATER_ZONE_1, HEATER_ZONE_2, HEATER_SAFETY_ENABLE | Gap Acma |
| Gap Acma | TENSION_OK, VACUUM_OK | TENSION_RETRACT_ENABLE, VACUUM_PUMP, LOADING_VACUUM_ENABLE | Folyo Kesme ve Ayirma |
| Folyo Kesme ve Ayirma | SEPARATION_OK | SEPARATING_BLADE, VACUUM_PUMP, LOADING_VACUUM_ENABLE | Boşaltma |
| Boşaltma | UNLOAD_READY | CYCLE_COMPLETE | Tamamlandı |

### NC Dosyası ve I/O Eşlemesi

NC oynatımı sadece eksenleri değil, temel proses çıkışlarını da `Lamine_IO` sheet'ine yazar.

Varsayılan eşlemeler:

| NC Komutu | Model Çıkışı |
|-----------|--------------|
| `M03` | `Cutting_Head` (`Top_Cutter` varsa o) ve `Lower_Cutter_Head` cam üst yüzeyine sabitlenir; başarısızsa `ALARM=1` ile kesim bloke edilir |
| `M05` | `UPPER_CUT_ENABLE=0`, `PRESSURE_ROLLER=0` |
| `M08` | `VACUUM_PUMP=1` |
| `M09` | `VACUUM_PUMP=0` |
| Kesim hareketi (`G01`) | spindle açıksa `UPPER_CUT_ENABLE=1` korunur |
| Program sonu | `CYCLE_COMPLETE=1` |

Not:

- Bu eşleme proses mantığından türetilmiş görsel/senaryo amaçlı bir modeldir.
- NC dosyası gerçek NC300 register çevrimine değil, FreeCAD playback katmanına bağlanır.
- `M03` interlock'u aktifken cam yüzeyi referansı bulunamaz veya kafa Z konumu tolerans icinde esitlenemezse playback `ALARM` durumuna gecer.

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
│  1. Konumlandırma ve Sabitleme                                  │
│     ├─ Gantry camı X ekseni ile VB hattına taşır                │
│     ├─ Kartezyen Y ve Z parkta kalır                            │
│     └─ Vakum vantuzları camı sabitler                           │
│                                                                 │
│  2. Simetrik Scoring                                            │
│     ├─ VB üst/alt kafa ortak Y ekseninde ilerler                │
│     ├─ Üst ve alt kesici tekerler aynı hat üstünde çalışır      │
│     └─ Camın iki yüzü eş zamanlı skorlanır                      │
│                                                                 │
│  3. Cam Kırma                                                   │
│     ├─ Alt kırma barı ve üst crush roller devreye girer         │
│     ├─ Skor hattı boyunca iki cam tabakası kırılır              │
│     └─ PVB folyo henüz bütündür                                 │
│                                                                 │
│  4. PVB Isıtma                                                  │
│     ├─ SIR ısıtıcı alttan seçici olarak folyoyu ısıtır          │
│     ├─ Nominal standoff yaklaşık 1 mm'dir                       │
│     └─ Amaç camı değil, doğrudan folyoyu yumuşatmaktır          │
│                                                                 │
│  5. Gap Açma                                                    │
│     ├─ Vakum sistemi levhaları çok hafif aralar                 │
│     ├─ PVB esner ve kesim için kontrollü boşluk oluşur          │
│     └─ Cam kenarında delaminasyon riski azaltılır               │
│                                                                 │
│  6. Folyo Kesme ve Ayırma (Trennklinge)                         │
│     ├─ Folyo kesme bıçağı açılan gap içine girer                │
│     ├─ PVB boydan boya kesilir                                  │
│     └─ İki lamine parça birbirinden tamamen ayrılır             │
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
│   ├── GFB_60_30RE_S_Stage3_VB_Y_Sync.FCMacro  # Yeni Stage 3 makrosu
│   └── Assembly4_LamineCam_ECam.py     # Legacy E-Cam denemesi
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

## Önemli Notlar - Dual Bridge Sistemi

**Kartezyen Köprü (Beyaz) vs VB Ünitesi (Lila):**

1. **Lamine Kesimde E-Cam Gereksiz:**
   - VB ünitesinde alt kafa servo, üst kafaya **mekanik bağlı**
   - Doğrudan Y ekseni hareketi yeterli
   - X ekseni sabit kalır (kilitli)

2. **Kartezyen Köprü Kullanımı:**
   - Düz cam kesiminde: X, Y, Z eksenleri aktif
   - Lamine kesimde: Park pozisyonunda (kullanılmaz)

3. **VB Ünitesi Kullanımı:**
   - Sadece lamine kesimde kullanılır
   - Sadece Y yönünde hareket eder
   - X yönünde hareket edemez (sabit konum)

## Kaynaklar

- [FreeCAD Assembly4 Dokümantasyonu](https://wiki.freecad.org/Assembly4)
- [Delta ASD-A3-E Manuel](https://www.delta-automation.com)
- [LiSEC GFB-60/30RE-S Teknik Dokümanı](../../../Documentation/Manuals/)

## Yazar

CNC AI Orchestrator  
Tarih: 2026-04-04
