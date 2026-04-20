# LiSEC GFB 60/30RE-S Referans Görseller

## Makine Özellikleri

**Model:** LiSEC GFB 60/30RE-S CNC Cam Kesme Köprüsü

### Teknik Spesifikasyonlar

| Özellik | Değer |
|---------|-------|
| **Maksimum Cam Boyutu** | 6000 x 3000 mm |
| **Minimum Cam Boyutu** | 300 x 200 mm |
| **Cam Kalınlığı** | 2-25 mm (monolitik), 2-25+2-25 mm (lamine) |
| **Kesim Hızı** | 0-80 m/dk |
| **Konumlandırma Hassasiyeti** | ±0.05 mm |
| **Eksen Sayısı** | 5 (X, Y, Z, Alt Kafa, Rodaj) |
| **Çalışma Gerilimi** | 400V 3N+PE 50Hz |
| **Toplam Güç** | ~15 kW |

### Ana Bileşenler

1. **Gantry (Köprü) Sistemi**
   - Hareketli köprü yapısı
   - X ekseni: 6000 mm hareket
   - Y ekseni: 3000 mm hareket
   - Lineer kılavuzlar (HIWIN HGH25CA veya eşdeğer)

2. **Kesim Kafaları**
   - **Üst Kafa (VB):** Sabit kesim kafası
   - **Alt Kafa (NB):** Mekanik bağlı takip eden kafa
   - **Z Ekseni:** Pnömatik baskı ve kesim derinliği kontrolü
   - **Rodaj Ünitesi:** Opsiyonel cam kenar rodajı

3. **Şase (Frame)**
   - Kaynaklı çelik konstrüksiyon
   - Stress giderme işlemi uygulanmış
   - Ayarlanabilir ayaklar
   - Profil taşıma sistemi

4. **Elektronik**
   - Servo motorlar (X, Y, Z eksenleri)
   - PLC kontrol ünitesi
   - HMI dokunmatik panel
   - Sensörler (proximity, encoder)

5. **Konveyör Sistemi**
   - Rulo konveyör
   - Cam destek profilleri
   - Vakum emme sistemi (opsiyonel)

## Görsel Kaynakları

### 1. Resmi LiSEC Kaynakları

- **Ana Sayfa:** https://www.lisec.com/
- **Ürünler:** https://www.lisec.com/en/products/systems/cnc-cutting-bridges
- **GFB Serisi:** https://www.lisec.com/en/products/systems/cnc-cutting-bridges/gfb

### 2. Alternatif Kaynaklar

- **DirectIndustry:** https://www.directindustry.com/
- **Glass Magazine:** https://www.glassmagazine.com/
- **YouTube:** https://www.youtube.com/results?search_query=LiSEC+GFB+cutting

### 3. Arama Anahtar Kelimeleri

```
"LiSEC GFB 60/30RE"
"LiSEC CNC cutting bridge"
"LiSEC vertical glass cutter"
"LiSEC laminated glass cutting"
"LiSEC GFB-S series"
"cam kesme makinesi dikey"
"CNC cam kesme köprüsü"
```

## FreeCAD Modelleme İçin Referanslar

### 1. Genel Görünüm (Isometric)
- Köprü yapısı gantry tipinde
- Üst kafa (VB) köprü üzerinde hareket eder
- Alt kafa (NB) köprü altında senkronize hareket eder
- Konveyör sistemi tabanda

### 2. Kesim Kafası Detayları
- **Üst Kafa:**
  - Kesim tekeri holder
  - Pnömatik baskı silindiri
  - Z ekseni lineer hareket
  - Motor bağlantısı (servo/stepper)
  
- **Alt Kafa:**
  - Mekanik takip sistemi
  - Manyetik veya mekanik bağlantı
  - Kesim tekeri yatağı

### 3. Şase Yapısı
- Dikdörtgen profil borular (80x80x4 mm veya 100x100x5 mm)
- Köşe takviye plakaları
- Ayarlanabilir montaj ayakları
- Lineer ray montaj yüzeyleri

### 4. Lineer Hareket Sistemi
- X ekseni: 6000 mm HIWIN HGH25CA veya eşdeğer
- Y ekseni: 3000 mm HIWIN HGH25CA veya eşdeğer
- Z ekseni: 500-800 mm strok lineer buşing veya ray

### 5. Motor Yerleşimleri
- **X Ekseni:** Köprü ortasında veya yanlarda
- **Y Ekseni:** Köprü üzerinde
- **Z Ekseni:** Kesim kafası üzerinde

## Görsel Toplama Talimatları

### Manuel İndirme

1. **Google Görseller:**
   ```
   https://www.google.com/search?q=LiSEC+GFB+60+30RE&tbm=isch
   ```

2. **Bing Görseller:**
   ```
   https://www.bing.com/images/search?q=LiSEC+GFB+glass+cutting
   ```

3. **YouTube Video Thumbnail'ları:**
   - Video'lardan ekran görüntüleri alın
   
### İndirilen Görsellerin Düzenlenmesi

```
CAD/Reference_Images/
├── 01_Overall/           # Genel makine görünümü
│   ├── isometric_view.jpg
│   ├── front_view.jpg
│   ├── side_view.jpg
│   └── top_view.jpg
├── 02_CuttingHead/       # Kesim kafası detayları
│   ├── upper_head.jpg
│   ├── lower_head.jpg
│   ├── Z_axis.jpg
│   └── wheel_holder.jpg
├── 03_Frame/             # Şase detayları
│   ├── frame_structure.jpg
│   ├── corner_bracket.jpg
│   ├── support_legs.jpg
│   └── profile_mounting.jpg
├── 04_LinearGuides/      # Lineer kılavuzlar
│   ├── X_axis_rail.jpg
│   ├── Y_axis_rail.jpg
│   ├── linear_block.jpg
│   └── rail_mounting.jpg
├── 05_Motors/            # Motorlar ve aktarma
│   ├── servo_motor_X.jpg
│   ├── servo_motor_Y.jpg
│   ├── coupling.jpg
│   └── gearbox.jpg
├── 06_Electronics/       # Elektronik
│   ├── control_panel.jpg
│   ├── electrical_cabinet.jpg
│   ├── sensors.jpg
│   └── cable_carrier.jpg
└── 07_Conveyor/          # Konveyör sistemi
    ├── roller_conveyor.jpg
    ├── support_profiles.jpg
    └── vacuum_system.jpg
```

## Ölçek Referansları

FreeCAD modelinizde kullanmak üzere:

| Bileşen | Ölçü |
|---------|------|
| Çalışma alanı | 6000 x 3000 mm |
| Köprü yüksekliği | ~800-1000 mm (zeminden) |
| Köprü genişliği | ~600-800 mm |
| Kesim kafası boyutu | ~300x300x400 mm |
| Lineer ray profili | HGH25CA (25 mm ray genişliği) |
| Profil kesiti | 80x80x4 mm veya 100x100x5 mm |

## Notlar

- Görseller telif hakkına tabi olabilir, sadece referans amaçlı kullanın
- LiSEC resmi görselleri için distribütör ile iletişime geçin
- Teknik çizimler için STEP dosyalarını üreticiden talep edin

---

**Oluşturma Tarihi:** 2026-04-19
**Proje:** CNC Revizyon - GFB 60/30RE-S Modelleme
