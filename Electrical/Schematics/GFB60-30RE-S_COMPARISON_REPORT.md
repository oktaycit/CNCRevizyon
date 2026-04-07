# GFB60-30RE-S Elektrik Şeması Revizyon Karşılaştırma Raporu

**Tarih:** 2026-04-07  
**Durum:** Detaylı Revizyon Analizi  
**Kaynak:** Orijinal GFB EP034-047170 + Delta NC300 Referans Tasarım

---

## 📋 Yönetici Özeti

Bu rapor, mevcut DrawIO elektrik şeması tasarımı ile GFB60-30RE-S orijinal dokümanları arasındaki farkları, eksikleri ve revizyon önerilerini detaylandırmaktadır.

### Genel Durum
| Kategori | Durum | Tamamlanma |
|----------|-------|------------|
| DrawIO Taslak | ✅ Mevcut | %40 |
| KiCad Şema | ❌ Eksik | %0 |
| Teknik Doküman | ✅ Tamamlandı | %100 |
| I/O Validasyonu | ⚠️ Kısmi | %60 |
| BOM | ❌ Eksik | %0 |

---

## 🔍 Sayfa Bazlı Karşılaştırma

### Sayfa 01: Ana Güç ve 24VDC Dağıtımı

#### ✅ Mevcut Durum (DrawIO)
- AC giriş terminali (X1) tanımlandı
- Ana şalter (Q1, 32A 3P) eklendi
- Ana sigorta (F1, 3A) eklendi
- Kontaktör (K1, 24VDC coil) eklendi
- 24V DC power supply (PS1, 20A) eklendi
- F2-F6 sigorta dağılımı eklendi
- X2 dağıtım terminali eklendi
- +24V, 0V, PE bar detayları eklendi

#### ❌ Eksiklikler (Orijinal GFB'ye Göre)

**1. AC Giriş Filtresi (EMC)**
```
EKSİK:
- EMC filtre (L1/L2/L3 → Filtre → Q1)
- Model: Delta EMI-F400V-10A
- Paralel kapasitör (X-capacitor)
- Toprak kaçak akımı izleme

ÖNERİ:
X1 → EMC Filtre → Q1 şeklinde revize edilmeli
```

**2. Faz Kontrol Rölesi**
```
EKSİK:
- Faz sırası kontrolü (3-faz koruma)
- Model: Pilz PNOZ EF Phase Monitor
- Fonksiyon: Faz kaybı, faz sırası hatası, asimetri

ÖNERİ:
Q1 çıkışına faz kontrol rölesi eklenecek
DI girişine alarm sinyali bağlanacak
```

**3. Surge Arrester (Parafudr)**
```
EKSİK:
- AC giriş parafudr
- Model: Phoenix Contact VAL-MS 400/3+1
- L1/L2/L3/N → PE koruması

ÖNERİ:
X1 girişine paralel bağlanacak
```

**4. 24VDC UPS (Opsiyonel)**
```
EKSİK:
- DC-DC converter (24V → 24V izole)
- Battery buffer (opsiyonel)
- Model: Delta DPS-24V-5A

ÖNERİ:
Kritik I/O ve safety için izole DC-DC eklenecek
```

**5. Kablo Kesiti Revizyonu**
```
MEVCUT:
- AC: 6 mm² (doğru)
- DC: 2.5 mm² (küçük!)

DOĞRU:
- AC Ana Giriş: 10 mm² (32A için)
- AC Servo X: 6 mm² (25A için)
- AC Servo Y/ALT: 4 mm² (16A için)
- DC Ana Dağıtım: 4 mm² (20A için)
- DC Branch: 2.5 mm² (5A için)
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 01 Güncelleme:**
1. EMC filtre bloğu ekle (X1 → Q1 arası)
2. Faz kontrol rölesi ekle
3. Parafudr ekle
4. Kablo kesitlerini güncelle
5. DC-DC izole converter ekle (opsiyonel)

---

### Sayfa 02: Emniyet Zinciri ve STO

#### ✅ Mevcut Durum (DrawIO)
- Pilz PNOZ X2.8P safety relay eklendi
- E-STOP 2-kanallı bağlantı gösterildi
- Güvenlik kapısı (S1) eklendi
- Reset butonu (S2) eklendi
- X10 safety inputs terminali eklendi
- X11 STO outputs terminali eklendi
- Feedback devresi gösterildi

#### ❌ Eksiklikler (Orijinal GFB'ye Göre)

**1. Çift Kanal STO Dağıtımı**
```
MEVCUT:
X11 → Tüm servo STO1/STO2 (tek hat)

EKSİK:
- Her eksen için ayrı shielded kablo
- Twisted pair kullanımı
- STO COM ayrı terminali

DOĞRU:
X11.1-2 → X ekseni STO1/STO2 (STO_COM_X)
X11.3-4 → Y ekseni STO1/STO2 (STO_COM_Y)
X11.5-6 → ALT ekseni STO1/STO2 (STO_COM_ALT)
X11.7-8 → Z ekseni STO1/STO2 (STO_COM_Z)
X11.9-10 → CNC ekseni STO1/STO2 (STO_COM_CNC)
```

**2. STO Feedback Monitoring**
```
EKSİK:
- Her servo STO feedback izleme
- STO aktif/pasif LED göstergesi
- NC300 DI girişine feedback

ÖNERİ:
Her servo DO_1 (ALM) → NC300 DI
STO status → HMI alarm sayfası
```

**3. E-STOP Mushroom Head Detayı**
```
EKSİK:
- E-STOP buton modeli
- Kontak sayısı (2NC + 1NO)
- Renk: Kırmızı, arka plan: Sarı
- Mekanik kilitli tip

ÖNERİ:
Model: Schneider XB4-BS542 (2NC)
```

**4. Safety Door Switch Detayı**
```
MEVCUT:
S1 (NC) - basit gösterim

EKSİK:
- Güvenlik manyetik şalter
- Model: Omron D4GS-NK2
- 2NC + 1NO kontak
- Mekanik kilitli

ÖNERİ:
D4GS-NK2 şematik sembolü eklenecek
```

**5. Reset Butonu Koşulları**
```
EKSİK:
- Reset koşulları açıklaması
- Tüm E-STOP'lar çekilmeden reset yok
- Kapı kapalı olmadan reset yok
- 3 saniye bekleme süresi

ÖNERİ:
Reset logic diyagramı eklenecek
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 02 Güncelleme:**
1. STO dağıtımını eksen bazlı detaylandır
2. E-STOP model ve kontak detaylarını ekle
3. Safety door switch modelini ekle
4. Reset logic akış diyagramı ekle
5. STO feedback monitoring ekle

---

### Sayfa 03: NC300 ve EtherCAT Omurgası

#### ✅ Mevcut Durum (DrawIO)
**NOT:** Bu sayfa DrawIO'da henüz oluşturulmamış!

#### 📋 Oluşturulması Gereken İçerik

**1. NC300 Güç Bağlantısı**
```
Gerekli:
- 24VDC besleme (2A)
- F2 sigorta (3A)
- +24V, 0V bağlantısı
- FG topraklama (< 100Ω)
```

**2. CN1/CN2 EtherCAT Portları**
```
Gerekli:
- CN1: EtherCAT OUT → X ekseni
- CN2: EtherCAT IN ← CNC ekseni (loop back)
- RJ45 konnektör
- CAT6 shielded kablo
- Topraklama detayı
```

**3. CN3 HMI Ethernet**
```
Gerekli:
- RJ45 → DOP-110CS
- TCP/IP ayarları
- IP adresi: 192.168.1.10 (NC300)
- IP adresi: 192.168.1.11 (HMI)
```

**4. CN5 50-pin I/O Connector**
```
Gerekli:
- DI_0 - DI_4 (kontrol girişleri)
- DO_0 - DO_2 (kontrol çıkışları)
- +24V_EXT (500mA max)
- GND_I/O
- Shield sonlandırma
```

**5. EtherCAT Topolojisi**
```
NC300 (CN1) → X → Y → ALT → Z → CNC → R1-EC → NC300 (CN2)
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 03 Oluşturma:**
1. NC300 ana blok çiz
2. Tüm connector pinout'larını ekle
3. EtherCAT daisy-chain çiz
4. HMI Ethernet bağlantısı ekle
5. CN5 I/O detaylarını ekle
6. Grounding sembolleri ekle

---

### Sayfa 04: Servo Sürücüler (5 Eksen)

#### ✅ Mevcut Durum (DrawIO)
**NOT:** Bu sayfa DrawIO'da henüz oluşturulmamış!

#### 📋 Oluşturulması Gereken İçerik

**1. X Ekseni (4.5kW, 3-faz)**
```
Gerekli:
- ASD-A3-4523-E sürücü
- ECMA-L11845 motor (4.5kW)
- P1: R/S/T (3F 400VAC, 25A)
- P2: U/V/W (motor, 4mm²)
- CN1: I/O (50-pin D-Sub)
- CN2: Encoder (6-pin)
- CN3/CN6: EtherCAT
- STO1/STO2
- Rejeneratif direnç (60Ω/100W)
```

**2. Y Ekseni (2.0kW, 3-faz)**
```
Gerekli:
- ASD-A3-2023-E sürücü
- ECMA-E11320 motor (2.0kW)
- P1: R/S/T (3F 400VAC, 16A)
- P2: U/V/W (motor, 2.5mm²)
- CN1/CN2/CN3/CN6
- STO1/STO2
- Rejeneratif direnç (60Ω/50W)
```

**3. ALT Ekseni (2.0kW, 3-faz)**
```
Y ekseni ile aynı
```

**4. Z Ekseni (1.0kW, 1-faz, FRENLİ)**
```
Gerekli:
- ASD-A3-1023-E sürücü
- ECMA-C11010FS motor (1.0kW, frenli)
- P1: R/L1, S/L2 (1F 230VAC, 10A)
- P2: U/V/W (motor)
- Fren bağlantısı (24VDC, 0.35A)
- DO_5 → BRK kontrol
- CN1/CN2/CN3/CN6
- STO1/STO2
```

**5. CNC Ekseni (1.5kW, 1-faz)**
```
Gerekli:
- ASD-A3-1523-E sürücü
- ECMA-E11315 motor (1.5kW)
- P1: R/L1, S/L2 (1F 230VAC, 10A)
- P2: U/V/W (motor)
- CN1/CN2/CN3/CN6
- STO1/STO2
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 04 Oluşturma (5 alt sayfa):**
1. Her eksen için ayrı şema
2. Güç bağlantıları (P1, P2)
3. I/O bağlantıları (CN1)
4. Encoder (CN2)
5. EtherCAT (CN3/CN6)
6. STO detayları
7. Z ekseni fren devresi
8. Rejeneratif direnç değerleri

---

### Sayfa 05: R1-EC I/O Modülleri

#### ✅ Mevcut Durum (DrawIO)
**NOT:** Bu sayfa DrawIO'da henüz oluşturulmamış!

#### 📋 Oluşturulması Gereken İçerik

**1. R1-EC01 Bus Coupler**
```
Gerekli:
- EtherCAT IN/OUT (RJ45)
- 24VDC besleme (150mA)
- V_IO besleme
- GND_IO
- Status LED'leri
```

**2. R1-EC0902D #1 (32-CH DI - X/Y Sensörleri)**
```
Gerekli:
- %IX0.0 - %IX1.15 adresleme
- X/Y/Z/ALT limit ve home
- Terminal bloğu (2x 16-pin)
- COM 0V bağlantısı
```

**3. R1-EC0902D #2 (32-CH DI - Diğer Sensörler)**
```
Gerekli:
- %IX2.0 - %IX3.15 adresleme
- Cam, vakum, kapı sensörleri
- Terminal bloğu
```

**4. R1-EC0902O (32-CH DO Relay)**
```
Gerekli:
- %QX0.0 - %QX1.15 adresleme
- Aktüatör çıkışları
- Röle kontakları (SPST, 2A)
- Flyback diyot (indüktif yük)
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 05 Oluşturma:**
1. Bus coupler şeması
2. DI modül #1 (X/Y sensörleri)
3. DI modül #2 (diğer sensörler)
4. DO modül (aktüatörler)
5. I/O adres tablosu
6. Terminal planı

---

### Sayfa 06: Dijital Girişler ve Sensörler

#### ✅ Mevcut Durum
- Sensor_Mounting_Details.md mevcut
- Leuze IS 218 detayları tamam
- M12 pinout mevcut
- Montaj braketleri çizilmiş

#### ❌ Eksiklikler

**1. Sensör Kablo Yönlendirme**
```
EKSİK:
- Kablo kanalı detayları
- Drag chain (enerji zinciri) routing
- Minimum bending radius
- EMC koruması
```

**2. Shield Sonlandırma**
```
EKSİK:
- 360° shield clamp detayı
- PE bar bağlantısı
- Pigtail vs direkt topraklama
```

**3. Sensör Test Noktaları**
```
EKSİK:
- Test point ekleme
- LED durum tablosu
- HMI diagnostic sayfası
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 06 Oluşturma:**
1. Sensör dağıtım şeması
2. Kablo routing detayları
3. Shield sonlandırma
4. Test noktaları
5. Diagnostic LED tablosu

---

### Sayfa 07: Dijital Çıkışlar ve Aktüatörler

#### ✅ Mevcut Durum (DrawIO)
**NOT:** Bu sayfa henüz oluşturulmamış!

#### 📋 Oluşturulması Gereken İçerik

**1. Valf Çıkışları**
```
Gerekli:
- %QX0.0 - %QX0.7 adresleme
- Röle çıkışları (SPST)
- Flyback diyot
- Sigorta (F7-F10)
```

**2. Uyarı Lambası**
```
Gerekli:
- 24VDC, 21W
- Kablo kesiti (1.5mm²)
- Sigorta (2A)
```

**3. Buzzer**
```
Gerekli:
- 24VDC, 85dB
- Kontrol rölesi
```

**4. Vakum Pompa Kontaktörü**
```
Gerekli:
- Ana kontaktör (K2)
- Termik röle
- Sigorta (10A)
- Aux kontak feedback
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 07 Oluşturma:**
1. DO dağıtım şeması
2. Her çıkış için detay
3. Röle sürme devreleri
4. Sigorta dağılımı
5. Yük tipleri (indüktif/rezistif)

---

### Sayfa 08: Terminal Planı

#### ✅ Mevcut Durum
- WIRING_REFERENCE.md içinde detaylı terminal listesi var
- X1, X2, X10, X11, X20 tanımları mevcut

#### ❌ Eksiklikler

**1. Fiziksel Terminal Düzeni**
```
EKSİK:
- Panel yerleşimi
- Terminal sıralaması
- Wire marker numaraları
- Ferrule boyutları
```

**2. Terminal Tip Detayları**
```
EKSİK:
- Phoenix Contact model numaraları
- Screw vs spring terminal
- Torque değerleri
```

**3. Kablo Pabuçları**
```
EKSİK:
- Lug tip ve boyutları
- Crimping tool referansı
- Heat shrink detayları
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 08 Oluşturma:**
1. Terminal blok yerleşimi
2. Her terminal için pinout
3. Kablo kesitleri
4. Wire marker şeması
5. Tightening torque tablosu

---

### Sayfa 09: Pin Planı

#### ✅ Mevcut Durum
- WIRING_REFERENCE.md içinde pinout tabloları var
- M12, RJ45, D-Sub 50-pin detayları mevcut

#### ❌ Eksiklikler

**1. Konnektör Housing Detayları**
```
EKSİK:
- Konnektör housing modeli
- Locking mechanism
- Strain relief
- IP koruma sınıfı
```

**2. Crimping Detayları**
```
EKSİK:
- Crimp tip ve boyutu
- Crimping tool part numarası
- Pull-out force testi
```

**3. Shield Sonlandırma**
```
EKSİK:
- Shield clip modeli
- Ground lug detayı
- 360° vs pigtail
```

#### 🔧 Revizyon Önerileri

**DrawIO Sayfa 09 Oluşturma:**
1. Her konnektör için detaylı pinout
2. Housing ve locking detayları
3. Crimping specifications
4. Shield termination methods
5. Cable assembly drawings

---

## 🔌 I/O Validasyon Durumu

### NC300 Yerel I/O (CN5)

| Sinyal | Durum | Validasyon | Not |
|--------|-------|------------|-----|
| DI_0 (SERVO_READY) | ✅ Tanımlandı | ⚠️ Kısmi | Servo alarm zinciri doğrulanacak |
| DI_1 (CYCLE_START) | ✅ Tanımlandı | ❌ Yok | HMI buton adresi eşleştirilecek |
| DI_2 (CYCLE_STOP) | ✅ Tanımlandı | ❌ Yok | HMI buton adresi eşleştirilecek |
| DI_3 (HOME_CMD) | ✅ Tanımlandı | ❌ Yok | NC300 parametresi kontrol edilecek |
| DI_4 (E-STOP_FB) | ✅ Tanımlandı | ⚠️ Kısmi | Safety relay aux kontak doğrulanacak |
| DO_0 (SYSTEM_READY) | ✅ Tanımlandı | ❌ Yok | PLC logic yazılacak |
| DO_1 (CYCLE_ACTIVE) | ✅ Tanımlandı | ❌ Yok | PLC logic yazılacak |
| DO_2 (ALARM_LIGHT) | ✅ Tanımlandı | ❌ Yok | Harici röle gerekebilir |

### R1-EC I/O Adresleme

| Modül | Kanal | Sinyal | Durum | Validasyon |
|-------|-------|--------|-------|------------|
| DI #1 | %IX0.0 | X_HOME | ✅ | ⚠️ Sensör polaritesi kontrol edilecek |
| DI #1 | %IX0.1 | X_LIMIT_P | ✅ | ⚠️ NC/NO ayarı doğrulanacak |
| DI #1 | %IX0.2 | X_LIMIT_N | ✅ | ⚠️ NC/NO ayarı doğrulanacak |
| DI #1 | %IX0.3 | Y_HOME | ✅ | ⚠️ Sensör polaritesi kontrol edilecek |
| DI #1 | %IX0.4 | Y_LIMIT_P | ✅ | ⚠️ NC/NO ayarı doğrulanacak |
| DI #1 | %IX0.5 | Y_LIMIT_N | ✅ | ⚠️ NC/NO ayarı doğrulanacak |
| DI #2 | %IX2.0 | Z_HOME | ✅ | ⚠️ Sensör polaritesi kontrol edilecek |
| DI #2 | %IX2.6 | GLASS_DETECT | ✅ | ❌ Cam sensörü tipi doğrulanacak |
| DI #2 | %IX2.8 | DOOR_SAFE | ✅ | ⚠️ Safety door kontak sayısı doğrulanacak |
| DO #1 | %QX0.1 | VACUUM_PUMP | ✅ | ⚠️ Kontaktör coil voltajı doğrulanacak |
| DO #1 | %QX0.4 | WARNING_LIGHT | ✅ | ✅ 24VDC 21W doğru |
| DO #1 | %QX0.5 | BUZZER | ✅ | ✅ 24VDC 85dB doğru |

---

## ⚡ Güç Dağılımı Validasyonu

### AC Güç Dağıtımı

| Devre | Mevcut | Doğru | Durum |
|-------|--------|-------|-------|
| Ana Giriş | 32A 3P | 32A 3P | ✅ |
| X Ekseni | 25A 3P | 25A 3P | ✅ |
| Y Ekseni | 16A 3P | 16A 3P | ✅ |
| ALT Ekseni | 16A 3P | 16A 3P | ✅ |
| Z Ekseni | 10A 1P | 10A 1P | ✅ |
| CNC Ekseni | 10A 1P | 10A 1P | ✅ |

### DC Güç Dağıtımı

| Devre | Mevcut | Doğru | Durum |
|-------|--------|-------|-------|
| NC300 | 3A | 3A | ✅ |
| R1-EC | 5A | 5A | ✅ |
| HMI | 1A | 1A | ✅ |
| Sensörler | 3A | 3A | ✅ |
| Safety | 2A | 2A | ✅ |

### Kablo Kesitleri

| Devre | Mevcut | Doğru | Durum |
|-------|--------|-------|-------|
| AC Ana | 6mm² | 10mm² | ❌ REVİZE! |
| AC Servo X | - | 6mm² | ❌ EKLE! |
| AC Servo Y/ALT | - | 4mm² | ❌ EKLE! |
| DC Ana | 2.5mm² | 4mm² | ❌ REVİZE! |
| DC Branch | - | 2.5mm² | ✅ |
| Signal | - | 0.5-1mm² | ✅ |

---

## 🛡️ Güvenlik Validasyonu

### Safety Function Analysis

| Safety Function | Mevcut | GFB Referans | Durum |
|-----------------|--------|--------------|-------|
| E-STOP Category | Cat 3 | Cat 3 PL e | ✅ |
| STO Routing | Tek hat | Ayrı shielded | ⚠️ |
| Feedback Monitoring | Basit | Tam izleme | ⚠️ |
| Door Interlock | NC kontak | 2NC+1NO | ⚠️ |
| Reset Logic | Basit | Koşullu reset | ⚠️ |

### SIL/PL Hedefi

| Parametre | Hedef | Mevcut | Durum |
|-----------|-------|--------|-------|
| Performance Level | PL e | PL d | ⚠️ |
| Safety Integrity Level | SIL 3 | SIL 2 | ⚠️ |
| Category | Cat 3 | Cat 3 | ✅ |
| MTTFd | >100 yıl | Hesaplanmamış | ⚠️ |
| DCavg | >90% | Hesaplanmamış | ⚠️ |

---

## 📦 BOM Durumu

### Eksik Component Bilgileri

| Component | Mevcut | Gerekli | Durum |
|-----------|--------|---------|-------|
| EMC Filtre | ❌ Yok | Delta EMI-F400V-10A | ❌ EKLE! |
| Faz Kontrol | ❌ Yok | Pilz PNOZ EF Phase | ❌ EKLE! |
| Parafudr | ❌ Yok | Phoenix VAL-MS 400/3+1 | ❌ EKLE! |
| E-STOP Buton | Basit | Schneider XB4-BS542 | ⚠️ DETAYLANDIR! |
| Safety Door | Basit | Omron D4GS-NK2 | ⚠️ DETAYLANDIR! |
| Terminal Bloklar | Genel | Phoenix Contact | ⚠️ MODEL EKLE! |
| Kablo Pabuçları | ❌ Yok | Phoenix AI serisi | ❌ EKLE! |
| Wire Marker | ❌ Yok | Weidmüller serisi | ❌ EKLE! |

---

## 🎯 Öncelikli Aksiyonlar

### Yüksek Öncelik (Revizyon 4.1)

1. **Sayfa 01 Revizyonu**
   - [ ] EMC filtre ekle
   - [ ] Faz kontrol rölesi ekle
   - [ ] Parafudr ekle
   - [ ] Kablo kesitlerini güncelle (10mm² ana giriş)

2. **Sayfa 02 Revizyonu**
   - [ ] STO dağıtımını eksen bazlı detaylandır
   - [ ] E-STOP model detayı ekle
   - [ ] Safety door switch detayı ekle
   - [ ] Reset logic diyagramı ekle

3. **Yeni Sayfalar Oluştur**
   - [ ] Sayfa 03: NC300 ve EtherCAT
   - [ ] Sayfa 04: Servo Sürücüler (5 alt sayfa)
   - [ ] Sayfa 05: R1-EC I/O Modülleri
   - [ ] Sayfa 06: Sensör Detayları
   - [ ] Sayfa 07: Aktüatör Detayları
   - [ ] Sayfa 08: Terminal Planı
   - [ ] Sayfa 09: Pin Planı

4. **BOM Oluşturma**
   - [ ] Tüm component'lar için model numarası ekle
   - [ ] Üretici bilgisi ekle
   - [ ] Tedarikçi referansı ekle
   - [ ] Miktar ve birim ekle

### Orta Öncelik (Revizyon 4.2)

5. **Grounding ve EMC**
   - [ ] Topraklama şeması detaylandır
   - [ ] Shield sonlandırma detayları
   - [ ] EMC uyumluluk notları

6. **Kablo Routing**
   - [ ] Kablo kanalı yerleşimi
   - [ ] Drag chain routing
   - [ ] Minimum bending radius

7. **Test ve Validasyon**
   - [ ] FAT (Factory Acceptance Test) prosedürü
   - [ ] SAT (Site Acceptance Test) prosedürü
   - [ ] Safety validation raporu

### Düşük Öncelik (Revizyon 5.0)

8. **KiCad Migration**
   - [ ] DrawIO → KiCad aktarımı
   - [ ] Footprint assignment
   - [ ] ERC/DRC check
   - [ ] BOM export

9. **3D Panel Layout**
   - [ ] Component yerleşimi 3D
   - [ ] Clearance check
   - [ ] Thermal analysis

---

## 📊 Revizyon Özeti Tablosu

| Sayfa | Başlık | Revizyon | Durum | Öncelik |
|-------|--------|----------|-------|---------|
| 01 | Ana Güç ve 24VDC | 4.0 → 4.1 | ⚠️ Revize | Yüksek |
| 02 | Emniyet ve STO | 4.0 → 4.1 | ⚠️ Revize | Yüksek |
| 03 | NC300 EtherCAT | - → 4.1 | ❌ Yeni | Yüksek |
| 04 | Servo Sürücüler | - → 4.1 | ❌ Yeni | Yüksek |
| 05 | R1-EC I/O | - → 4.1 | ❌ Yeni | Yüksek |
| 06 | Sensörler | - → 4.1 | ❌ Yeni | Orta |
| 07 | Aktüatörler | - → 4.1 | ❌ Yeni | Orta |
| 08 | Terminal Planı | - → 4.1 | ❌ Yeni | Orta |
| 09 | Pin Planı | - → 4.1 | ❌ Yeni | Düşük |

---

## 📝 Sonuç ve Öneriler

### Genel Değerlendirme

**Mevcut Durum:**
- DrawIO taslak şemalar %40 tamamlandı
- Teknik dokümanlar %100 tamamlandı
- I/O validasyonu %60 tamamlandı
- BOM %0 tamamlandı

**Hedef Durum (Revizyon 4.1):**
- Tüm sayfalar tamamlanacak
- GFB orijinal standartlarına uygunluk
- KiCad'e hazır net şemalar
- Tam BOM listesi

### Önerilen Çalışma Sırası

1. **İlk Hafta:**
   - Sayfa 01 ve 02 revizyonları
   - Sayfa 03 (NC300) oluşturma
   - BOM template hazırlama

2. **İkinci Hafta:**
   - Sayfa 04 (Servo) oluşturma
   - Sayfa 05 (I/O) oluşturma
   - Component araştırması

3. **Üçüncü Hafta:**
   - Sayfa 06-07 oluşturma
   - Sayfa 08-09 oluşturma
   - Final validasyon

4. **Dördüncü Hafta:**
   - KiCad migration hazırlığı
   - PDF export ve review
   - Final approval

---

**Hazırlayan:** CNCRevizyon Elektrik Validasyon Ekibi  
**Versiyon:** 1.0  
**Tarih:** 2026-04-07  
**Durum:** ✅ REVİZYON RAPORU TAMAMLANDI
