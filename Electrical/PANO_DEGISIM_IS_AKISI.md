# Pano Değişimi İş Akışı ve Kontrol Formu

**Proje:** LiSEC GFB-60/30RE CNC Revizyon  
**Tarih:** 2026-04-11  
**Doküman Tipi:** İş Akışı + Kontrol Formu  
**Versiyon:** 1.0

---

## 📋 Genel Bakış

Bu doküman, eski elektrik panosunun sökülmesi ve yeni Delta Electronics tabanlı revizyon panosunun montajı için adım adım iş akışını ve kontrol formunu içerir.

### Kapsam
- Eski pano sökülmesi
- Yeni pano montajı
- Saha kablolarının bağlanması
- Devreye alma testleri

### Sorumlular
| Rol | Sorumluluk | İmza |
|-----|------------|------|
| Proje Yöneticisi | Genel koordinasyon, izinler | _________ |
| Elektrik Teknikeri | Pano sökülmesi/montajı | _________ |
| Otomasyon Mühendisi | PLC, servo, devreye alma | _________ |
| Güvenlik Sorumlusu | LOTO, iş güvenliği denetimi | _________ |

---

## 🔧 1. Hazırlık Aşaması

### 1.1 Güvenlik Ön Hazırlıkları

| # | Kontrol Itemi | ✓ | Açıklama |
|---|---------------|---|----------|
| 1.1.1 | LOTO ekipmanları hazır | □ | Kilit, etiket, haspet |
| 1.1.2 | E-Stop test edildi | □ | Ana E-Stop çalışıyor |
| 1.1.3 | Kapasitör deşarj kontrolü | □ | DC bus 0V |
| 1.1.4 | Kişisel koruyucular | □ | Eldiven, gözlük, ayakkabı |
| 1.1.5 | Çalışma izni alındı | □ | Üretim durduruldu |

### 1.2 Ekipman ve Malzeme Hazırlığı

| # | Malzeme | Miktar | ✓ |
|---|---------|--------|---|
| 1.2.1 | Yeni pano (tam imalat) | 1 adet | □ |
| 1.2.2 | Kablo etiketleri | 1 set | □ |
| 1.2.3 | Terminal etiketleri | 1 set | □ |
| 1.2.4 | Kablo bağı | 50 adet | □ |
| 1.2.5 | Isı büzüşmeli makaron | 1 set | □ |
| 1.2.6 | Pano anahtarı | 1 set | □ |
| 1.2.7 | Multimeter | 2 adet | □ |
| 1.2.8 | İzolasyon test cihazı | 1 adet | □ |
| 1.2.9 | Tork anahtarı | 1 adet | □ |
| 1.2.10 | Laptop (Delta ISPSoft) | 1 adet | □ |

### 1.3 Dokümantasyon Hazırlığı

| # | Doküman | ✓ |
|---|---------|---|
| 1.3.1 | Elektrik şeması (01-05 sayfalar) | □ |
| 1.3.2 | Terminal diyagramı | □ |
| 1.3.3 | Wire list (kablo listesi) | □ |
| 1.3.4 | I/O adres listesi | □ |
| 1.3.5 | Pano yerleşim planı | □ |
| 1.3.6 | BOM (Malzeme listesi) | □ |

---

## 🔌 2. Eski Pano Sökümü

### 2.1 Enerji Kesme ve Güvenlik

| # | İşlem | ✓ | Açıklama |
|---|-------|---|----------|
| 2.1.1 | Ana şalteri OFF pozisyonuna getir | □ | Q1 = OFF |
| 2.1.2 | LOTO kilidini tak | □ | Her teknisyen kendi kilidi |
| 2.1.3 | Gerilim yok kontrolü | □ | L1/L2/L3 = 0V |
| 2.1.4 | DC bus deşarj | □ | DC+ / DC- = 0V |
| 2.1.5 | "ÇALIŞMA VAR" etiketi as | □ | Pano girişine |

### 2.2 Saha Kablolarının Etiketlenmesi

**ÖNEMLİ:** Her kablo sökülmeden önce etiketlenmelidir!

| Kablo Grubu | Etiket Formatı | Örnek | ✓ |
|-------------|----------------|-------|---|
| X Ekseni Sensör | `DI-X-XX` | `DI-XH-01` (X Home) | □ |
| Y Ekseni Sensör | `DI-Y-XX` | `DI-YH-01` (Y Home) | □ |
| Z Ekseni Sensör | `DI-Z-XX` | `DI-ZH-01` (Z Home) | □ |
| Alt Ekseni Sensör | `DI-A-XX` | `DI-AH-01` (Alt Home) | □ |
| X Servo Güç | `PWR-X-XX` | `PWR-X-01` | □ |
| Y Servo Güç | `PWR-Y-XX` | `PWR-Y-01` | □ |
| Z Servo Güç | `PWR-Z-XX` | `PWR-Z-01` | □ |
| Alt Servo Güç | `PWR-A-XX` | `PWR-A-01` | □ |
| E-STOP | `SAFE-XX` | `SAFE-01` | □ |
| Valfler | `DO-V-XX` | `DO-VAC-01` | □ |

### 2.3 Söküm Sırası

| # | İşlem | ✓ | Notlar |
|---|-------|---|--------|
| 2.3.1 | Saha kablolarını sökle | □ | Etiketleri kontrol et |
| 2.3.2 | Motor kablolarını sökle | □ | 4 adet servo |
| 2.3.3 | EtherCAT/Ethernet kablolarını sökle | □ | RJ45 koruyucu tak |
| 2.3.4 | AC güç kablolarını sökle | □ | L1/L2/L3 |
| 2.3.5 | Pano montaj cıvatalarını sökle | □ | 4 nokta |
| 2.3.6 | Eski panoyu yerinden kaldır | □ | 2 kişi, dikkatli |
| 2.3.7 | Pano tabanını temizle | □ | Bir sonraki montaj için |

---

## 📦 3. Yeni Pano Montajı

### 3.1 Pano Yerleşimi

| # | İşlem | ✓ | Ölçü/Tork |
|---|-------|---|-----------|
| 3.1.1 | Pano tabanını kontrol et | □ | Düzgün, temiz |
| 3.1.2 | Yeni panoyu yerine yerleştir | □ | 2 kişi |
| 3.1.3 | Pano ayaklarını ayarla | □ | Su terazisi ile |
| 3.1.4 | Montaj cıvatalarını sık | □ | M10, 25 Nm |
| 3.1.5 | Pano gövde toprağını bağla | □ | 16mm², PE1 |

### 3.2 Pano İçi Bileşen Kontrolü

| Bileşen | Model | Adet | ✓ | Konum |
|---------|-------|------|---|-------|
| NC300 CNC | NC300-E | 1 | □ | Üst sol |
| R1-EC01 | Bus Coupler | 1 | □ | DIN-1 |
| R1-EC0902D | 32-CH DI | 2 | □ | DIN-2,3 |
| R1-EC0902O | 32-CH DO | 1 | □ | DIN-4 |
| Pilz PNOZ | X2.8P | 1 | □ | Safety |
| 24V PSU | 20A | 1 | □ | Üst sağ |
| AC Şalter | 32A 3P | 1 | □ | Q1 |
| Kontaktör | 24VDC coil | 1 | □ | K1 |
| Sigortalar | 3A, 5A, 10A | 6 | □ | F1-F6 |

### 3.3 Pano İçi Ön Bağlantılar

| # | Bağlantı | ✓ | Kablo Kesiti |
|---|----------|---|--------------|
| 3.3.1 | X1 → Q1 (AC giriş) | □ | 10mm² |
| 3.3.2 | Q1 → K1 (Kontaktör) | □ | 6mm² |
| 3.3.3 | K1 → PS1 (24V PSU) | □ | 4mm² |
| 3.3.4 | PS1 → 24V bar | □ | 4mm² |
| 3.3.5 | 24V bar → NC300 | □ | 2.5mm² |
| 3.3.6 | 24V bar → R1-EC | □ | 2.5mm² |
| 3.3.7 | PE bar → Tüm cihazlar | □ | 4mm² |

---

## 🔗 4. Saha Kablolarının Bağlanması

### 4.1 Sensör Bağlantıları (X20 Terminal)

| Adres | Sinyal | Kablo No | Terminal | ✓ |
|-------|--------|----------|----------|---|
| %IX0.0 | X+LIMIT | DI-XPL-01 | X20.1 | □ |
| %IX0.1 | X-LIMIT | DI-XNL-01 | X20.2 | □ |
| %IX0.2 | X-HOME | DI-XH-01 | X20.3 | □ |
| %IX0.3 | Y+LIMIT | DI-YPL-01 | X20.4 | □ |
| %IX0.4 | Y-LIMIT | DI-YNL-01 | X20.5 | □ |
| %IX0.5 | Y-HOME | DI-YH-01 | X20.6 | □ |
| %IX0.6 | Z+LIMIT | DI-ZPL-01 | X20.7 | □ |
| %IX0.7 | Z-LIMIT | DI-ZNL-01 | X20.8 | □ |
| %IX0.8 | Z-HOME | DI-ZH-01 | X20.9 | □ |
| %IX0.9 | ALT+LIMIT | DI-APL-01 | X20.10 | □ |
| %IX0.10 | ALT-LIMIT | DI-ANL-01 | X20.11 | □ |
| %IX0.11 | ALT-HOME | DI-AH-01 | X20.12 | □ |
| %IX0.12 | E-STOP1 | SAFE-01 | X20.13 | □ |
| %IX0.13 | E-STOP2 | SAFE-02 | X20.14 | □ |
| %IX0.14 | DOOR_OPEN | SAFE-03 | X20.15 | □ |
| %IX0.15 | VACUUM_OK | DI-VAC-01 | X20.16 | □ |

**Kablo Tipi:** 4x0.34mm² shielded  
**Shield Bağlantısı:** Terminal bloğunda PE'ye

### 4.2 Servo Motor Bağlantıları

| Eksen | Sürücü | Güç Kablo | Encoder Kablo | ✓ |
|-------|--------|-----------|---------------|---|
| X | ASD-A3-4523-E | 4G6mm² | CAT6 STP | □ |
| Y | ASD-A3-2023-E | 4G4mm² | CAT6 STP | □ |
| Alt | ASD-A3-2023-E | 4G4mm² | CAT6 STP | □ |
| Z | ASD-A3-1023-E | 3G2.5mm² | CAT6 STP | □ |
| C/Rodaj | ASD-A3-1523-E | 3G2.5mm² | CAT6 STP | □ |

### 4.3 EtherCAT Bağlantıları (Sıralı)

| # | Bağlantı | Kablo Tipi | Uzunluk | ✓ |
|---|----------|------------|---------|---|
| 4.3.1 | NC300 CN1 → X Servo CN3 | CAT6 STP | 0.5m | □ |
| 4.3.2 | X Servo CN6 → Y Servo CN3 | CAT6 STP | 1.0m | □ |
| 4.3.3 | Y Servo CN6 → Alt Servo CN3 | CAT6 STP | 1.0m | □ |
| 4.3.4 | Alt Servo CN6 → Z Servo CN3 | CAT6 STP | 0.5m | □ |
| 4.3.5 | Z Servo CN6 → C Servo CN3 | CAT6 STP | 0.5m | □ |
| 4.3.6 | C Servo CN6 → R1-EC01 IN | CAT6 STP | 1.0m | □ |
| 4.3.7 | R1-EC01 OUT → NC300 CN2 | CAT6 STP | 0.5m | □ |

**⚠️ DİKKAT:** EtherCAT ring topolojisi kesinlikle ters bağlanmamalıdır!

### 4.4 Dijital Çıkışlar (Valfler, Röleler)

| Adres | Sinyal | Terminal | Kablo No | ✓ |
|-------|--------|----------|----------|---|
| %QX0.0 | SERVO_ENABLE | X40.1 | DO-SR-01 | □ |
| %QX0.1 | VACUUM_PUMP | X40.2 | DO-VAC-01 | □ |
| %QX0.2 | OIL_PUMP | X40.3 | DO-OIL-01 | □ |
| %QX0.3 | COOLING_FAN | X40.4 | DO-FAN-01 | □ |
| %QX0.4 | WARNING_LIGHT | X40.5 | DO-LIGHT-01 | □ |
| %QX0.5 | BUZZER | X40.6 | DO-BUZ-01 | □ |
| %QX0.6 | MARKER | X40.7 | DO-MARK-01 | □ |
| %QX0.7 | BREAKER_ENABLE | X40.8 | DO-BRK-01 | □ |
| %QX0.8 | HEATER_ZONE1 | X40.9 | DO-H1-01 | □ |
| %QX0.9 | HEATER_ZONE2 | X40.10 | DO-H2-01 | □ |
| %QX0.10 | HEATER_ZONE3 | X40.11 | DO-H3-01 | □ |

---

## ⚡ 5. Enerji Verme ve Test

### 5.1 İlk Enerji Öncesi Kontroller

| # | Kontrol | ✓ | Ölçüm |
|---|---------|---|-------|
| 5.1.1 | Tüm kablo bağlantıları sıkı | □ | Tork kontrolü |
| 5.1.2 | Kısa devre yok | □ | Multimeter |
| 5.1.3 | AC L1/L2/L3 süreklilik | □ | 0.1-0.5Ω |
| 5.1.4 | DC +24V / 0V kısa devre yok | □ | >1MΩ |
| 5.1.5 | PE süreklilik (gövde) | □ | <0.1Ω |
| 5.1.6 | İzolasyon testi (AC) | □ | >100MΩ @ 500V |
| 5.1.7 | Tüm sigortalar takılı | □ | Doğru akım değeri |
| 5.1.8 | E-Stop basılı değil | □ | Kontrol |

### 5.2 Kademeli Enerji Verme

#### Kademe 1: 24VDC Kontrol Gerilimi

| # | İşlem | ✓ | Ölçüm |
|---|-------|---|-------|
| 5.2.1 | F3 (5A) sigortayı tak | □ | - |
| 5.2.2 | PS1 24V PSU'yu enerjilendir | □ | - |
| 5.2.3 | 24V çıkış ölç | □ | 24.0±0.5V |
| 5.2.4 | NC300 24V giriş ölç | □ | 23.5-24.5V |
| 5.2.5 | R1-EC 24V giriş ölç | □ | 23.5-24.5V |
| 5.2.6 | 24V common bar ölç | □ | 23.5-24.5V |

#### Kademe 2: AC Ana Güç

| # | İşlem | ✓ | Ölçüm |
|---|-------|---|-------|
| 5.2.7 | Q1 şalterini ON yap | □ | - |
| 5.2.8 | L1-N ölç | □ | 230V±10% |
| 5.2.9 | L2-N ölç | □ | 230V±10% |
| 5.2.10 | L3-N ölç | □ | 230V±10% |
| 5.2.11 | L1-L2 ölç | □ | 400V±10% |
| 5.2.12 | L2-L3 ölç | □ | 400V±10% |
| 5.2.13 | L3-L1 ölç | □ | 400V±10% |

#### Kademe 3: Sürücü Enerjisi

| # | İşlem | ✓ | Ölçüm |
|---|-------|---|-------|
| 5.2.14 | K1 kontaktör ON | □ | Coil 24V |
| 5.2.15 | X servo DC bus ölç | □ | ~540V DC |
| 5.2.16 | Y servo DC bus ölç | □ | ~540V DC |
| 5.2.17 | Alt servo DC bus ölç | □ | ~540V DC |
| 5.2.18 | Z servo DC bus ölç | □ | ~320V DC |
| 5.2.19 | C servo DC bus ölç | □ | ~320V DC |

### 5.3 PLC ve EtherCAT Başlatma

| # | İşlem | ✓ | Durum |
|---|-------|---|-------|
| 5.3.1 | NC300 RUN anahtarı RUN'a al | □ | - |
| 5.3.2 | NC300 LED kontrol | □ | RUN = Yeşil |
| 5.3.3 | EtherCAT master başlat | □ | - |
| 5.3.4 | X servo EtherCAT durum | □ | OP (Operational) |
| 5.3.5 | Y servo EtherCAT durum | □ | OP |
| 5.3.6 | Alt servo EtherCAT durum | □ | OP |
| 5.3.7 | Z servo EtherCAT durum | □ | OP |
| 5.3.8 | C servo EtherCAT durum | □ | OP |
| 5.3.9 | R1-EC01 EtherCAT durum | □ | OP |
| 5.3.10 | HMI bağlantı kontrol | □ | 192.168.1.11 |

---

## 🧪 6. Fonksiyon Testleri

### 6.1 Dijital Giriş Testi (Sensörler)

| Adres | Sinyal | Test Yöntemi | Beklenen | ✓ |
|-------|--------|--------------|----------|---|
| %IX0.0 | X+LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.1 | X-LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.2 | X-HOME | Metal yaklaştır | 0→1 | □ |
| %IX0.3 | Y+LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.4 | Y-LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.5 | Y-HOME | Metal yaklaştır | 0→1 | □ |
| %IX0.6 | Z+LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.7 | Z-LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.8 | Z-HOME | Metal yaklaştır | 0→1 | □ |
| %IX0.9 | ALT+LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.10 | ALT-LIMIT | Metal yaklaştır | 0→1 | □ |
| %IX0.11 | ALT-HOME | Metal yaklaştır | 0→1 | □ |
| %IX0.12 | E-STOP1 | Buton bas/bırak | 1→0 | □ |
| %IX0.13 | E-STOP2 | Buton bas/bırak | 1→0 | □ |
| %IX0.14 | DOOR_OPEN | Kapı aç/kapa | 0→1 | □ |
| %IX0.15 | VACUUM_OK | Vakum aç/kapa | 0→1 | □ |

### 6.2 Dijital Çıkış Testi

| Adres | Sinyal | Test | Beklenen | ✓ |
|-------|--------|------|----------|---|
| %QX0.0 | SERVO_ENABLE | Manuel ON | Röle çekmeli | □ |
| %QX0.1 | VACUUM_PUMP | Manuel ON | Kontaktör | □ |
| %QX0.2 | OIL_PUMP | Manuel ON | Röle | □ |
| %QX0.3 | COOLING_FAN | Manuel ON | Fan dönmeli | □ |
| %QX0.4 | WARNING_LIGHT | Manuel ON | Işık yanmalı | □ |
| %QX0.5 | BUZZER | Manuel ON | Ses çıkmalı | □ |

### 6.3 Safety Testleri (KRİTİK)

| # | Test | Beklenen | ✓ |
|---|------|----------|---|
| 6.3.1 | E-STOP basılı → STO aktif | Tüm servo enable kesilmeli | □ |
| 6.3.2 | E-STOP bırak → Reset gerekli | Manuel reset olmadan başlamamalı | □ |
| 6.3.3 | Safety door aç → STO aktif | Tüm servo durmalı | □ |
| 6.3.4 | Pilz PNOZ LED durum | Hata yok = yeşil | □ |
| 6.3.5 | STO çıkış voltajı | 0V (aktif) / 24V (pasif) | □ |

### 6.4 Servo Jog Testi

**⚠️ UYARI:** Eksen hareketi için mekanik engelleri kaldırın!

| Eksen | Yön | Hız | Mesafe | ✓ |
|-------|-----|-----|--------|---|
| X | + | 10% | 100mm | □ |
| X | - | 10% | 100mm | □ |
| Y | + | 10% | 100mm | □ |
| Y | - | 10% | 100mm | □ |
| Z | + | 10% | 50mm | □ |
| Z | - | 10% | 50mm | □ |
| Alt | + | 10% | 100mm | □ |
| Alt | - | 10% | 100mm | □ |

### 6.5 Home Sequence Testi

| # | Eksen | Başlangıç | Son Pozisyon | Süre | ✓ |
|---|-------|-----------|--------------|------|---|
| 6.5.1 | X | Rastgele | X=0 | <30s | □ |
| 6.5.2 | Y | Rastgele | Y=0 | <30s | □ |
| 6.5.3 | Z | Rastgele | Z=0 | <20s | □ |
| 6.5.4 | Alt | Rastgele | Alt=0 | <30s | □ |
| 6.5.5 | Tüm eksenler | Sıralı | Hepsi 0 | <90s | □ |

**Test Prosedürü:**
1. Tüm eksenleri rastgele pozisyona hareket ettir
2. HMI'den "Home All" butonuna bas
3. Her eksenin home sensörünü tetikleyip pozisyonu 0'ladığını doğrula
4. HMI'de koordinatların (0, 0, 0, 0) olduğunu kontrol et

---

## 📊 7. Son Kontroller ve Teslim

### 7.1 Dokümantasyon Güncelleme

| # | Doküman | ✓ |
|---|---------|---|
| 7.1.1 | As-built şema güncellemesi | □ |
| 7.1.2 | Terminal bağlantı listesi | □ |
| 7.1.3 | Kablo listesi (wire list) | □ |
| 7.1.4 | PLC program yedek | □ |
| 7.1.5 | Servo parametre yedek | □ |
| 7.1.6 | HMI proje yedek | □ |

### 7.2 Temizlik ve Düzen

| # | İşlem | ✓ |
|---|-------|---|
| 7.2.1 | Pano içi temizlik | □ |
| 7.2.2 | Kablo düzeni (cable tie) | □ |
| 7.2.3 | Kullanılmayan kabloları izole et | □ |
| 7.2.4 | Pano kapaklarını kapat | □ |
| 7.2.5 | Çalışma alanını temizle | □ |

### 7.3 Eğitim ve Teslim

| # | Konu | Açıklama | ✓ |
|---|------|----------|---|
| 7.3.1 | Operatör eğitimi | HMI kullanımı, alarm yönetimi | □ |
| 7.3.2 | Bakım eğitimi | Filtre temizliği, periyodik kontrol | □ |
| 7.3.3 | Arıza giderme | Alarm kodları, hızlı müdahale | □ |
| 7.3.4 | Yedek parça | Kritik yedekler listesi | □ |
| 7.3.5 | Garanti belgeleri | Tedarikçi iletişim bilgileri | □ |

---

## ✅ İmza ve Onay

### Test Sonuçları Özeti

| Kategori | Test Sayısı | Geçti | Kaldı | Durum |
|----------|-------------|-------|-------|-------|
| Güvenlik | 5 | ___ | ___ | □ |
| Elektrik | 19 | ___ | ___ | □ |
| PLC/EtherCAT | 10 | ___ | ___ | □ |
| Dijital I/O | 22 | ___ | ___ | □ |
| Servo | 13 | ___ | ___ | □ |
| **TOPLAM** | **69** | ___ | ___ | **___%** |

### Proje Teslim Onayı

| Rol | İsim | İmza | Tarih |
|-----|------|------|-------|
| Proje Yöneticisi | _________________ | _________ | __/__/____ |
| Elektrik Teknikeri | _________________ | _________ | __/__/____ |
| Otomasyon Mühendisi | _________________ | _________ | __/__/____ |
| Güvenlik Sorumlusu | _________________ | _________ | __/__/____ |
| Müşteri Temsilcisi | _________________ | _________ | __/__/____ |

---

## 📝 Ek Notlar ve Gözlemler

### Tespit Edilen Sorunlar

| No | Sorun | Öncelik | Sorumlu | Çözüm | Tarih |
|----|-------|---------|---------|-------|-------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |

### Değişiklikler (Change Request)

| No | Değişiklik | Onaylayan | Tarih |
|----|------------|-----------|-------|
| 1 | | | |
| 2 | | | |

---

**Doküman Sonu**

*Bu form doldurulduktan sonra PDF olarak arşivlenmelidir.*
