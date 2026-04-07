# Lisec GFB-60/30RE Revizyon Projesi - Özet Rapor

**Proje Başlangıç Tarihi:** 03.04.2026  
**Durum:** Planlama ve Tasarım Aşaması (Tamamlandı)  
**Versiyon:** 2.0 (EtherCAT Revizyon)

---

## 1. Proje Tanımı

LiSEC GFB-60/30RE cam kesme makinesinin tam revizyonu. Delta Electronics EtherCAT tabanlı ASDA-A3-E servo sistemleri, NC300 CNC kontrolör ve R1-EC uzak I/O modülleri ile modernize edilmiş, cam ve lamine kesim yetenekli endüstriyel sistem.

### 1.1 Makine Özellikleri

| Özellik | Değer |
|---------|-------|
| Model | LiSEC GFB-60/30RE |
| Maksimum Cam Boyutu | 6000 x 3000 mm |
| Minimum Cam Boyutu | 300 x 200 mm |
| Cam Kalınlığı | 2-25 mm |
| Kesim Hızı | 0-80 m/dk |
| Konumlandırma Hassasiyeti | ±0.05 mm (24-bit encoder) |
| Eksen Sayısı | 5 (X, Y, Z, Alt, C/Rodaj) |
| EtherCAT Cycle Time | 100 μs |

---

## 2. Teknik Çözümler

### 2.1 Kontrol Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│              Delta NC300 (EtherCAT Master)                      │
│              - G-Kod İşleme                                     │
│              - 100μs EtherCAT Cycle                             │
│              - E-Cam Senkronizasyonu                            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ASDA-A3-E     │    │ ASDA-A3-E     │    │ ASDA-A3-E     │
│ 4.5kW (X)     │    │ 2.0kW (Y)     │    │ 2.0kW (Alt)   │
│ ECMA-L11845   │    │ ECMA-E11320   │    │ ECMA-E11320   │
│ Yüksek Atalet │    │ Orta Atalet   │    │ Orta Atalet   │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ASDA-A3-E     │    │ ASDA-A3-E     │    │ R1-EC         │
│ 1.0kW (Z)     │    │ 1.5kW (C)     │    │ Bus Coupler   │
│ ECMA-C11010   │    │ ECMA-E11315   │    │               │
│ Frenli        │    │ IP67          │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          ┌───────────────┐    ┌───────────────┐
          │ R1-EC0902D x3 │    │ R1-EC0902O x3 │
          │ 48 DI         │    │ 48 DO         │
          │ (Sensörler)   │    │ (Valfler)     │
          └───────────────┘    └───────────────┘
```

### 2.2 Delta Servo Sistemi

| Eksen | Sürücü | Motor | Güç | Özellik |
|-------|--------|-------|-----|---------|
| X | ASD-A3-4523-E | ECMA-L11845 | 4.5kW | Yüksek Atalet |
| Y | ASD-A3-2023-E | ECMA-E11320 | 2.0kW | Orta Atalet |
| Alt | ASD-A3-2023-E | ECMA-E11320 | 2.0kW | Orta Atalet |
| Z | ASD-A3-1023-E | ECMA-C11010 | 1.0kW | Frenli |
| C | ASD-A3-1523-E | ECMA-E11315 | 1.5kW | IP67 |

### 2.3 Güvenlik Sistemi (STO)

- **Pilz PNOZ X2.8P** güvenlik rölesi
- **STO (Safe Torque Off)** donanımsal güvenlik
- SIL 3, PL e, Cat. 4 sertifikalı
- Tüm sürücülere ortak STO hattı

### 2.4 Sensör Sistemi

- **Leuze IS 218 Series** indüktif sensörler (M18, IP67)
- 8 adet limit/home sensörü
- Cam tozu ortamına dayanıklı
- Kirlenme toleransı yüksek

---

## 3. Proje Klasör Yapısı

```
CNCRevizyon/
├── README.md                              # Proje ana dokümanı
│
├── CAD/
│   ├── FreeCAD/                           # FreeCAD modelleri
│   │   ├── 00_Common/                     # Ortak bileşenler
│   │   ├── 01_Motors/                     # ECMA-L/E/C motorlar
│   │   ├── 02_Frame/                      # Şase parçaları
│   │   ├── 03_LinearGuides/               # Lineer raylar
│   │   ├── 04_CuttingHead/                # Kesim kafası
│   │   ├── 05_Electronics/                # R1-EC, sensörler
│   │   ├── 06_Assembly/                   # Ana montaj
│   │   └── 07_Exports/                    # STEP, STL, DXF
│   ├── Drawings/                          # Teknik çizimler
│   └── Exports/                           # Export dosyaları
│
├── Electrical/                            # Elektrik projelendirme
│   ├── Schematics/                        # Şematik çizimler
│   │   └── Sensor_Mounting_Details.md     # Sensör montaj detayları
│   ├── Wiring/                            # Kablaj planları
│   ├── STO_Circuit/                       # Güvenlik devresi
│   └── BOM/                               # Malzeme listeleri
│
├── Firmware/
│   ├── NC300/                             # Delta NC programları
│   │   └── NC300_Programming_Guide.md     # Programlama kılavuzu
│   │   ├── Hardware/                      # EtherCAT konfigürasyon
│   │   ├── PLC/                           # ST programları
│   │   ├── GCode/                         # G-kod dosyaları
│   │   └── HMI/                           # DOP-110CS ekranları
│   └── Tools/                             # Konfigürasyon araçları
│
├── Delta/
│   ├── Servo/
│   │   └── Delta_Servo_Integration.md     # Servo entegrasyonu
│   │   ├── ASD-A3-E/                      # EtherCAT parametreleri
│   │   └── ECMA-Motors/                   # Motor datasheet
│   ├── NC300/                             # NC konfigürasyon
│   └── R1-EC/                             # Uzak I/O ayarları
│
├── AI/
│   ├── Optimization/                      # Kesim optimizasyonu
│   │   └── Cutting_Optimization_AI.md
│   └── Vision/                            # Görüntü işleme
│
├── Documentation/
│   ├── Manuals/                           # Kullanım kılavuzları
│   ├── Specifications/                    # Teknik spesifikasyonlar
│   │   └── Fusion360_Modeling_Guide.md
│   └── Reports/                           # Proje raporları
│       └── Project_Summary.md
│
└── Tests/                                 # Test prosedürleri
```

---

## 4. Tamamlanan Çalışmalar

### 4.1 Dokümantasyon

- [x] README.md (GFB-60/30RE, EtherCAT mimarisi)
- [x] Delta ASDA-A3-E servo entegrasyon kılavuzu
- [x] NC300 programlama kılavuzu (G-kod, E-Cam, PLC)
- [x] Leuze IS 218 sensör montaj detayları
- [x] FreeCAD modelleme kılavuzu
- [x] AI tabanlı kesim optimizasyonu algoritmaları
- [x] Proje klasör yapısı oluşturuldu

### 4.2 Teknik Spesifikasyonlar

- [x] EtherCAT mimarisi tanımlandı (100μs cycle)
- [x] Servo motor seçimi yapıldı (ECMA-L/E/C serisi)
- [x] R1-EC uzak I/O konfigürasyonu
- [x] STO güvenlik devresi tasarımı
- [x] Sensör yerleşim planı
- [x] PDO mapping ve CoE parametreleri
- [x] E-Cam lamine kesim senkronizasyonu

---

## 5. Devam Eden / Gelecek Çalışmalar

### 5.1 CAD Modelleme (FreeCAD)

- [ ] FreeCAD kurulumu ve Assembly4 eklentisi
- [ ] ECMA-L11845 (4.5kW) motor modeli - yüksek atalet flanş
- [ ] ECMA-C11010 (1kW frenli) Z ekseni montajı
- [ ] ECMA-E11320 (2kW) Y/Alt motor modelleri
- [x] R1-EC modül kutu yerleşimi
- [ ] Leuze IS 218 sensör montaj braketleri
- [ ] HIWIN HGH25 lineer ray modelleri
- [ ] Ana şase modellemesi
- [ ] X ekseni portalı tasarımı
- [ ] Kesim kafası montajı
- [ ] Assembly4 ile ana montaj
- [ ] Hareket simülasyonu
- [ ] TechDraw teknik çizimler
- [x] **DOP-110CS HMI montaj modeli** (286x226x58mm, cutout: 271x211mm)
- [x] **Operatör terminal kutusu** (400x500x250mm, IP65 koruma)
- [x] **R1-EC DIN ray montaj plakası** (350x200x5mm)
- [x] **IP65 kablo giriş rakorları ve havalandırma filtreleri**

### 5.2 Elektrik Tasarımı

- [ ] Tek hat şeması (Single Line Diagram)
- [ ] EtherCAT kablolama şeması
- [ ] STO güvenlik devresi çizimi
- [ ] R1-EC I/O bağlantı şeması
- [ ] Kablo kesit hesaplamaları
- [ ] Pano yerleşim planı
- [ ] Topraklama planı

### 5.3 Yazılım Geliştirme

- [ ] ISPSoft proje oluşturma
- [ ] EtherCAT konfigürasyon dosyası
- [ ] Eksen parametre ayarları
- [ ] PLC ana program (ST)
- [ ] Referans dönüş fonksiyonu
- [ ] E-Cam lamine kesim profili
- [ ] G-kod kesim programları
- [ ] DOP-110CS HMI ekranları
- [ ] Alarm ve hata yönetimi

### 5.4 Test ve Komisyon

- [ ] EtherCAT başlangıç testi
- [ ] Servo auto-tuning
- [ ] Limit switch testi
- [ ] STO güvenlik testi
- [ ] E-Cam senkronizasyon testi
- [ ] G-kod kesim testi
- [ ] Lamine kesim testi
- [ ] 72 saat sürekli çalışma testi

---

## 6. Malzeme Listesi (BOM)

### 6.1 Kontrol ve Sürücü Sistemi

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | Delta NC300 | NC300-XXX | 1 |
| 2 | Delta HMI | DOP-110CS (10.1") | 1 |
| 3 | Delta Servo Sürücü 4.5kW | ASD-A3-4523-E | 1 |
| 4 | Delta Servo Sürücü 2.0kW | ASD-A3-2023-E | 2 |
| 5 | Delta Servo Sürücü 1.0kW | ASD-A3-1023-E | 1 |
| 6 | Delta Servo Sürücü 1.5kW | ASD-A3-1523-E | 1 |

### 6.2 Servo Motorlar

| No | Ürün | Model | Miktar | Eksen |
|----|------|-------|--------|-------|
| 1 | Servo Motor 4.5kW | ECMA-L11845 | 1 | X |
| 2 | Servo Motor 2.0kW | ECMA-E11320 | 2 | Y, Alt |
| 3 | Servo Motor 1.0kW Frenli | ECMA-C11010 | 1 | Z |
| 4 | Servo Motor 1.5kW IP67 | ECMA-E11315 | 1 | C |

### 6.3 Uzak I/O Sistemi

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | R1-EC Bus Coupler | R1-EC | 1 |
| 2 | R1-EC Dijital Giriş | R1-EC0902D (16 DI) | 3 |
| 3 | R1-EC Dijital Çıkış | R1-EC0902O (16 DO) | 3 |

### 6.4 Konveyör Sürücüsü

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | Delta MS300 | MS300-xxx | 1 |
| 2 | EtherCAT Kart | CMM-EC01 | 1 |

### 6.5 Sensörler ve Güvenlik

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | Indüktif Sensör | Leuze IS 218 MM | 8 |
| 2 | Pilz Güvenlik Rölesi | PNOZ X2.8P | 1 |
| 3 | E-Stop Butonu | Schneider XB4 | 2 |
| 4 | M12 Konnektör | 4-pin Dişi | 20 |
| 5 | Sensör Kablosu | 4x0.34mm² Shielded | 50 m |

### 6.6 Kablolama

| No | Ürün | Özellik | Miktar |
|----|------|---------|--------|
| 1 | EtherCAT Kablo | CAT5e STP | 20 m |
| 2 | Güç Kablosu 4.5kW | 4 mm² | 15 m |
| 3 | Güç Kablosu 2.0kW | 2.5 mm² | 20 m |
| 4 | Güç Kablosu 1.0kW | 1.5 mm² | 10 m |
| 5 | Encoder Kablosu | Shielded STP | 30 m |

---

## 7. Riskler ve Önlemler

| Risk | Olasılık | Etki | Önlem |
|------|----------|------|-------|
| EtherCAT haberleşme hatası | Orta | Yüksek | Shielded kablo, doğru topraklama |
| E-Cam senkronizasyon kaybı | Düşük | Yüksek | DC sync ayarı, cycle time optimizasyonu |
| STO devresi hatalı çalışma | Düşük | Kritik | Pilz PNOZ test fonksiyonu |
| Sensör kirlenmesi (cam tozu) | Yüksek | Orta | Koruyucu kapak, hava üfleme |
| Z ekseni düşme (fren arızası) | Düşük | Yüksek | Frenli motor, mekanik dengeleme |
| Aşırı ısınma (4.5kW X motor) | Orta | Orta | Soğutma fanı, termal izleme |

---

## 8. Zaman Çizelgesi (Tahmini)

| Aşama | Süre | Başlangıç | Bitiş |
|-------|------|-----------|-------|
| CAD Modelleme | 4 hafta | Hafta 1 | Hafta 4 |
| Elektrik Tasarımı | 3 hafta | Hafta 2 | Hafta 4 |
| Malzeme Temini | 4 hafta | Hafta 3 | Hafta 6 |
| Pano İmalatı | 2 hafta | Hafta 6 | Hafta 7 |
| Mekanik Montaj | 3 hafta | Hafta 7 | Hafta 9 |
| Elektrik Montajı | 2 hafta | Hafta 9 | Hafta 10 |
| Yazılım Geliştirme | 4 hafta | Hafta 8 | Hafta 11 |
| Test ve Komisyon | 2 hafta | Hafta 11 | Hafta 12 |

**Toplam Tahmini Süre:** 12 hafta (3 ay)

---

## 9. Kritik Teknik Parametreler

### 9.1 EtherCAT Konfigürasyonu

```
Cycle Time: 100 μs
Sync Mode: DC (Distributed Clock)
Watchdog: 10 ms
PDO Mapping: Standard CoE
```

### 9.2 Servo Parametreleri

```
Encoder Çözünürlüğü: 24-bit (16,777,216 pulse/rev)
Auto-tuning: Mode II (Real-time)
Following Error Limit: 5.0 mm (X), 3.0 mm (Y/Z)
```

### 9.3 E-Cam Senkronizasyonu

```
Master Axis: Y (Üst)
Slave Axis: Alt (Alt)
Sync Accuracy: ±0.1 mm
Cycle Time: 100 μs
```

---

## 10. Sonraki Adımlar

1. **FreeCAD modellemeye başlama**
   - FreeCAD v1.0 kurulumu (<https://github.com/FreeCAD/FreeCAD-Bundle/releases>)
   - Assembly4 eklentisi kurulumu (Addon Manager)
   - Delta ECMA motor datasheet'lerini indir
   - Leuze IS 218 sensör ölçülerini al
   - R1-EC modül boyutlarını al
   - Ana şase sketch çizimine başla

2. **Elektrik projesi detaylandırma**
   - Tek hat şeması çizimi
   - EtherCAT topoloji planı
   - Pano yerleşim çizimi

3. **Yazılım ortamı hazırlığı**
   - ISPSoft kurulumu
   - ASDA-Soft kurulumu
   - DiaDesigner (HMI) kurulumu
   - Test projesi oluşturma

4. **Malzeme temini**
   - Delta distribütörü ile iletişim
   - Teslim süresi teyidi
   - Fiyat teklifi alma

---

## 11. Kaynaklar

### 11.1 Delta Elektronik

- **Delta Türkiye:** <https://www.delta-automation.com/tr/>
- **NC300:** <https://www.delta-automation.com/tr/products/industrial-automation/plc-based-control>
- **ASDA-A3-E:** <https://www.delta-automation.com/tr/products/industrial-automation/servo-systems>
- **ISPSoft:** Delta web sitesinden indirilebilir

### 11.2 Leuze Electronics

- **IS 218 Serisi:** <https://www.leuze.com/en-de/products/sensors/inductive-sensors>

### 11.3 FreeCAD

- **FreeCAD Resmi:** <https://www.freecad.org/>
- **Dokümantasyon:** <https://wiki.freecad.org/>
- **Türkçe Kaynaklar:** <https://wiki.freecad.org/Manual:Türkçe>
- **Forum:** <https://forum.freecad.org/>
- **Video Eğitim:** <https://www.youtube.com/c/FreeCAD>

---

**Doküman Versiyonu:** 2.0  
**Son Güncelleme:** 03.04.2026  
**Hazırlayan:** Proje Ekibi
