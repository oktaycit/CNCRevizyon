# Operatör Terminal Kutusu - GFB-60/30RE

**DOP-110CS HMI + R1-EC Uzak I/O Entegrasyonu**

**Doküman Versiyonu:** 2.0  
**Güncelleme:** ✅ Elektriksel Bağlantılar Eklendi

---

## 📋 Genel Bilgi

Bu FreeCAD modeli, LiSEC GFB-60/30RE cam kesim makinesinin operatör kontrol terminali için tasarlanmıştır. Terminal kutusu, Delta Electronics DOP-110CS HMI paneli ve R1-EC EtherCAT I/O modüllerini barındırır.

### 🎯 Tasarım Hedefleri

- **DOP-110CS HMI** güvenli ve erişilebilir montaj
- **R1-EC modülleri** için DIN ray montajı
- **IP65 koruma sınıfı** (toz ve su sıçramasına karşı)
- **20 metre kablo mesafesi** için optimize edilmiş kablo girişleri
- **Kolay bakım** için açılabilir kapak sistemi

---

## 📐 Teknik Özellikler

### Ana Kutu

| Özellik | Değer |
|---------|-------|
| Dış Ölçüler | 400 x 500 x 250 mm (G x Y x D) |
| Duvar Kalınlığı | 5 mm |
| Malzeme | Boyalı sac çelik / Paslanmaz çelik |
| Koruma Sınıfı | IP65 |
| Ağırlık (tahmini) | ~8 kg |

### DOP-110CS HMI Montajı

| Özellik | Değer |
|---------|-------|
| Panel Cutout | 271 x 211 mm (G x Y) |
| Dış Çerçeve | 286 x 226 mm |
| Derinlik | 58 mm |
| Panel Kalınlığı | 2-6 mm uyumlu |
| Montaj Tipi | 4 nokta klips montajı |

### R1-EC Modül Yerleşimi

| Modül | Adet | Konum |
|-------|------|-------|
| R1-EC01 (Bus Coupler) | 1 | DIN Ray, sol taraf |
| R1-EC0902D (32-CH DI) | 1-2 | DIN Ray, orta |
| R1-EC0902O (32-CH DO) | 1 | DIN Ray, sağ taraf |

### Kablo Girişleri

| Konum | Boyut | Tip | Amaç |
|-------|-------|-----|------|
| Alt | 3x M40 | IP65 Rakor | Ana güç, EtherCAT, I/O |
| Üst | 1x M32 | IP65 Rakor | HMI Ethernet |
| Yan | 2x M25 | IP65 Rakor | Opsiyonel I/O |

### Havalandırma

| Özellik | Değer |
|---------|-------|
| Filtre Tipi | IP65 labirent tipi |
| Havalandırma Alanı | 2x 120x120 mm |
| Konum | Yan duvarlar (sol/sağ) |
| Filtre Elemanı | Değiştirilebilir |

---

## 📁 Dosya Listesi

### FreeCAD Python Script

| Dosya | Açıklama |
|-------|----------|
| `Operator_Terminal_Generator.py` | Ana modelleme scripti |

### STEP Export Dosyaları

| Dosya | Açıklama | Boyut (tahmini) |
|-------|----------|-----------------|
| `DOP-110CS_Housing.stp` | DOP-110CS HMI dış gövde | ~50 KB |
| `DOP-110CS_Panel_Cutout.stp` | Panel kesim şablonu | ~30 KB |
| `Operator_Terminal_Enclosure.stp` | Terminal ana kutu | ~150 KB |
| `Operator_Terminal_Door.stp` | Terminal kapağı | ~120 KB |
| `R1-EC_Mounting_Plate.stp` | R1-EC DIN ray plakası | ~80 KB |
| `Cable_Gland_M40.stp` | M40 kablo giriş rakoru | ~40 KB |
| `IP65_Vent_Filter.stp` | Havalandırma filtresi | ~60 KB |
| `Operator_Terminal_Complete.stp` | Tam montaj | ~300 KB |

### Elektriksel Export Dosyaları (CSV + JSON)

| Dosya | Açıklama | İçerik |
|-------|----------|--------|
| `Wire_Connections.csv` | Tüm kablo bağlantıları | Wire ID, From, To, Cable Type, Kesit, Renk, Uzunluk |
| `Terminal_Blocks.csv` | Terminal blokları | Terminal ID, Tip, Kutup, Voltaj, Akım, Tork |
| `Device_List.csv` | Cihaz listesi | Device ID, Tip, Model, Güç, Voltaj, Lokasyon |
| `BOM.csv` | Malzeme listesi | Cihazlar, Terminaller, Kablolar (toplu) |
| `Electrical_Data.json` | Tüm veriler | JSON formatında tüm elektriksel data |
| `Connection_Matrix.csv` | From/To matrisi | Bağlantı matrisi (kablo bazlı) |
| `Cable_Schedule.csv` | Kablo programı | Güzergah bazında kablo özeti |

---

## 🔧 Montaj Talimatları

### 1. Panel Hazırlığı (Sac Kesim)

**DOP-110CS Panel Cutout:**

```
┌─────────────────────────────────────────┐
│                                         │
│    ┌─────────────────────────────┐     │
│    │                             │     │
│    │      271 mm (cutout)        │     │
│    │    ┌─────────────────┐     │     │
│    │    │   220x140 mm    │     │ 211│
│    │    │   Ekran Penceresi│    │ mm │
│    │    │                 │     │     │
│    │    └─────────────────┘     │     │
│    │                             │     │
│    └─────────────────────────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

**Kesim Toleransları:**

- Cutout: +0.5/-0 mm (HMI sıkı oturmalı)
- Montaj delikleri: Ø4.5 ±0.1 mm
- Köşe radyusları: R3 max

### 2. DIN Ray Montajı

**R1-EC Modül Yerleşimi:**

```
    ┌─────────────────────────────────────────────┐
    │  Terminal Kutu İçi (400 x 250 mm)          │
    │                                             │
    │  ┌─────────────────────────────────────┐   │
    │  │  R1-EC01  │  R1-EC0902D  │  R1-EC0902O│   │
    │  │  [EtherCAT]│  [32 DI]    │  [32 DO]   │   │
    │  │   120mm   │    120mm     │    120mm   │   │
    │  └─────────────────────────────────────┘   │
    │         TS 35 DIN Ray (350 mm)             │
    └─────────────────────────────────────────────┘
```

**Montaj Adımları:**

1. DIN ray plakasını kutu tabanına 4x M5 vida ile sabitle
2. R1-EC01 Bus Coupler'ı DIN rayın sol tarafına tak
3. R1-EC0902D (DI modülü) ve R1-EC0902O (DO modülü) ekle
4. Modül arası bağlantıları oturt (backplane)
5. Topraklama kablosunu PE baraya bağla

### 3. DOP-110CS HMI Montajı

**Ön Panel Montajı:**

```
    ┌─────────────────────────────────────────────┐
    │         DOP-110CS Ön Görünüş               │
    │                                             │
    │  ╔═══════════════════════════════════════╗ │
    │  ║  ┌───────────────────────────────┐   ║ │
    │  ║  │                               │   ║ │
    │  ║  │      10.1" TFT Ekran          │   ║ │
    │  ║  │      (800x480 pixel)          │   ║ │
    │  ║  │                               │   ║ │
    │  ║  └───────────────────────────────┘   ║ │
    │  ║                                       ║ │
    │  ║   [LED Status]  [USB Port]           ║ │
    │  ╚═══════════════════════════════════════╝ │
    │                                             │
    │  Montaj Klipsleri: 4 köşe (M5)             │
    └─────────────────────────────────────────────┘
```

**Montaj Adımları:**

1. HMI'yi panel cutout'a ön taraftan yerleştir
2. 4 montaj klipsini köşelere tak ve sık
3. Panel kalınlığını 2-6 mm arasında ayarla
4. IP65 conta sıkılığını kontrol et

### 4. Kablo Girişleri

**Kablo Giriş Planı:**

```
         ┌─────────────────────────────┐
         │        Terminal Kutu        │
         │         (Alt Görüş)         │
         │                             │
         │   ○ M40    ○ M32   ○ M40   │
         │    GND     HMI     ETH     │
         │                             │
         │            ○ M40            │
         │           POWER             │
         └─────────────────────────────┘

Kablo Giriş Listesi:
┌──────┬──────┬─────────────────────────┬──────────────┐
│ Poz  │ Boyut│ Kablo Tipi              │ Amaç         │
├──────┼──────┼─────────────────────────┼──────────────┤
│ 1    │ M40  │ 5x4mm² + shield         │ 24V DC Güç   │
│ 2    │ M32  │ CAT6 SF/UTP             │ HMI Ethernet │
│ 3    │ M40  │ CAT6 SF/UTP + 2x1mm²    │ EtherCAT+I/O │
│ 4    │ M40  │ 2x2.5mm² + shield       │ 24V DC Yedek │
└──────┴──────┴─────────────────────────┴──────────────┘
```

**Kablo Giriş Montajı:**

1. Kablo giriş deliklerini matkapla aç (Ø40, Ø32, Ø25)
2. IP65 rakorları tak ve sık
3. Kabloları rakorlardan geçir
4. Rakorları sıkarak IP65 sızdırmazlık sağla
5. Shield bağlantılarını PE baraya yap

### 5. IP65 Havalandırma Filtreleri

**Montaj Konumu:**

```
    ┌─────────────────────────────────────────┐
    │  Sol Yan Duvar                        │
    │                                       │
    │  ┌─────┐         ┌─────┐              │
    │  │Filtre│        │Filtre│             │
    │  │  #1  │        │  #2  │             │
    │  │120x120│       │120x120│            │
    │  └─────┘         └─────┘              │
    │                                       │
    └─────────────────────────────────────────┘
```

**Filtre Değişimi:**

1. Filtre kapağını 4 vidadan sökün
2. Eski filtre elemanını çıkarın
3. Yeni filtre elemanını takın
4. Kapağı IP65 conta ile kapatın

---

## ⚡ Elektrik Bağlantıları

### Terminal Dağılımı

**R1-EC01 Bus Coupler:**

```
┌─────────────────────────────────────┐
│ R1-EC01 EtherCAT Bus Coupler       │
├─────────────────────────────────────┤
│ ECAT IN  → NC300 (ana pano)        │
│ ECAT OUT → R1-EC0902D              │
│ +24V     → X2:2 (ana pano)         │
│ 0V       → X2:6 (ana pano)         │
│ PE       → PE Bara                 │
└─────────────────────────────────────┘
```

**R1-EC0902D (32-CH DI):**

```
┌─────────────────────────────────────┐
│ R1-EC0902D 32-Channel Digital In   │
├─────────────────────────────────────┤
│ DI_0-15  → Terminal butonları      │
│   - START (Yeşil)                  │
│   - STOP (Kırmızı)                 │
│   - E-STOP (Sarı)                  │
│   - RESET (Mavi)                   │
│ DI_16-31 → Sensör girişleri        │
│   - Door Safe                      │
│   - Glass Detect                   │
│   - Vacuum FB                      │
└─────────────────────────────────────┘
```

**R1-EC0902O (32-CH DO Relay):**

```
┌─────────────────────────────────────┐
│ R1-EC0902O 32-Channel Relay Out    │
├─────────────────────────────────────┤
│ DO_0-15  → İndikatörler            │
│   - RUN LED (Yeşil)                │
│   - FAULT LED (Kırmızı)            │
│   - ALARM (Sarı)                   │
│ DO_16-31 → Röle çıkışları          │
│   - Horn                           │
│   - Tower Light                    │
└─────────────────────────────────────┘
```

### Güç Dağıtımı

**24V DC Besleme:**

```
Ana Pano (24V/10A PSU)
    │
    ├─ X2:1 → NC300 (ana pano)
    │
    ├─ X2:2 → R1-EC01 (terminal kutu)
    │
    ├─ X2:3 → Sensörler (ana pano)
    │
    ├─ X2:4 → Safety Circuit
    │
    └─ X2:5 → DOP-110CS (terminal kutu)

Kablo Kesiti: 1.5-2.5 mm²
Sigorta: 5A (her dal için)
```

---

## 🔩 Mekanik Montaj

### Terminal Kutu Sabitleme

**Ayaklı Terminal Montajı:**

```
    ┌─────────────────────────────┐
    │   Terminal Kutu             │
    │   (400x500x250 mm)          │
    │                             │
    │      [Montaj Ayağı]         │
    │         │                   │
    │         │ 800 mm            │
    │         │                   │
    │      [Taban Plakası]        │
    │         │││                 │
    │         ┴┴┴                 │
    │      Zemine Ankraj          │
    └─────────────────────────────┘
```

**Montaj Adımları:**

1. Taban plakasını zemine 4x M12 kimyasal dübel ile sabitle
2. Montaj ayaklarını taban plakasına kaynak yap veya cıvata ile sabitle
3. Terminal kutusunu ayaklara 4x M8 vida ile monte et
4. Su terazisi ile dikliği kontrol et (±2°)
5. Titreşim için rubber takoz kullan

### Ergonomik Konumlandırma

**Operatör Açısı:**

```
        Operatör Göz Seviyesi
              👁
              │
              │ 15° aşağı bakış
              ↓
    ┌─────────────────┐
    │  DOP-110CS HMI  │  ← 1100-1200 mm zemin
    └─────────────────┘
    
Önerilen HMI Yüksekliği: 1100-1200 mm (zemin-den)
Operatör Mesafesi: 500-800 mm
```

---

## 🛡️ Koruma Sınıfı

### IP65 Gereksinimleri

| Bileşen | Gereksinim | Kontrol |
|---------|------------|---------|
| Panel Cutout | IP65 conta | Sıkılık testi |
| Kablo Girişleri | IP65 rakor | Tork kontrolü |
| Kapı Contası | EPDM profil | Görsel kontrol |
| Havalandırma | IP65 filtre | Basınç testi |
| Montaj Delikleri | IP65 tapa | Varlık kontrolü |

### IP65 Test Prosedürü

1. **Görsel Kontrol:**
   - Tüm contalar yerinde mi?
   - Rakorlar sıkı mı?
   - Kapı contası hasarsız mı?

2. **Su Testi:**
   - 12.5 L/dk su basıncı (30 kPa)
   - 3 dakika tüm yönlerden
   - İçeride su girişi olmamalı

3. **Toz Testi:**
   - Talk pudrası testi (1 saat)
   - İçeride toz birikintisi olmamalı

---

## 🔧 Bakım Talimatları

### Günlük Kontrol

- [ ] HMI ekranı temizliği (yumuşak bez)
- [ ] Status LED kontrolü
- [ ] Kablo girişlerinde gevşeklik yok

### Haftalık Kontrol

- [ ] Kapı contası kontrolü
- [ ] Havalandırma filtreleri kontrolü
- [ ] Terminal sıkılıkları kontrolü

### Aylık Bakım

- [ ] Havalandırma filtrelerini temizle/değiştir
- [ ] Kablo pabuçları oksidasyon kontrolü
- [ ] Topraklama direnci ölçümü (<100Ω)

### Yıllık Bakım

- [ ] Tüm contaları değiştir
- [ ] Kablo giriş rakorlarını yenile
- [ ] İç temizlik (basınçlı hava)
- [ ] Boya hasarları rötuşla

---

## 📐 CAD Kullanım Talimatları

### FreeCAD'de Modelleme

```bash
# 1. FreeCAD'i aç
# 2. Python Console'da çalıştır:
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/05_Electronics/Operator_Terminal_Generator.py").read())
create_all_terminal_parts()
```

### STEP Dosyalarını İçe Aktarma

1. FreeCAD → File → Import
2. `Operator_Terminal_Complete.stp` seç
3. Part Workbench'e geç
4. Parçaları inceleyin

### Assembly4 ile Montaj

1. Assembly4 Workbench'i yükle
2. Yeni assembly oluştur
3. STEP parçalarını import et
4. LCS (Local Coordinate System) ile konumlandır
5. Constraint'leri tanımla

---

## 📎 Referans Dokümanlar

| Doküman | Konum |
|---------|-------|
| DOP-110CS Manual | `Documentation/Manuals/DOP-110CS_Manual.pdf` |
| R1-EC Manual | `Documentation/Manuals/Delta_R1-EC_Manual.pdf` |
| Wiring Reference | `Electrical/WIRING_REFERENCE.md` |
| Terminal Plan | `Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical_Rev4.1_Page08.drawio` |

---

## 🎯 Sonraki Adımlar

### Tamamlanması Gerekenler

- [ ] STEP dosyalarını FreeCAD'ten export et
- [ ] Tam montaj resimleri render al
- [ ] 2D teknik çizimler oluştur (DXF)
- [ ] Sac gelişim ölçülerini hesapla
- [ ] BOM listesini oluştur

### Entegrasyon

- [ ] Ana makine montajına ekle (`30RE Tam Makine.FCStd`)
- [ ] Kablo yolu modellemesi yap
- [ ] EtherCAT kablo uzunluğu hesapla (20m)
- [ ] Montaj talimatı dokümanı oluştur

---

**Hazırlayan:** CNCRevizyon CAD Ekibi  
**Tarih:** 2026-04-07  
**Versiyon:** 1.0  
**Durum:** ✅ Model Tamamlandı, ⏳ Export Bekliyor
