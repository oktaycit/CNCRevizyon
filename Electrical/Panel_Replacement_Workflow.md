# GFB-60/30RE Pano Değişimi ve Revizyon İş Akışı

**Proje:** LiSEC GFB-60/30RE CNC Revizyon  
**Tarih:** 2026-04-11  
**Versiyon:** 1.0  
**Durum:** FINAL - Sahada Uygulanabilir

---

## 📋 Genel Bakış

Bu doküman, mevcut elektrik panosunun sökülmesi ve yeni Delta Electronics tabanlı revizyon panosunun montajı için adım adım iş akışını içerir.

### Kapsam
- Eski pano sökümü
- Yeni pano montajı
- Saha kablolarının bağlanması
- Devreye alma testleri
- Home/Limit sensör bağlantıları

### Sorumluluklar
| Rol | Sorumluluk | İmza |
|-----|------------|------|
| Proje Yöneticisi | Genel koordinasyon, güvenlik | _________ |
| Elektrik Teknisyeni | Pano söküm/montaj, kablolama | _________ |
| Otomasyon Mühendisi | PLC, servo, devreye alma | _________ |
| Kalite Kontrol | Test ve doğrulama | _________ |

---

## 🛑 Faz 0: Hazırlık (Önceki Gün)

### 0.1 Güvenlik Ön Hazırlığı

| # | Kontrol Maddesi | ✅ | Notlar |
|---|-----------------|----|--------|
| 0.1.1 | ELO (Enerji Nakil Hattı) kesme planı hazırlandı mı? | ☐ | |
| 0.1.2 | LOTO (Lock-Out Tag-Out) ekipmanı hazır mı? | ☐ | Kilit, etiket, tehlike kartı |
| 0.1.3 | Kişisel koruyucu donanım (KKD) kontrol edildi mi? | ☐ | Baret, izolasyon eldiveni, güvenlik ayakkabısı, gözlük |
| 0.1.4 | Acil durum prosedürleri ekibe açıklandı mı? | ☐ | |
| 0.1.5 | Çalışma alanı bariyer ile izole edildi mi? | ☐ | |

### 0.2 Ekipman ve Malzeme Hazırlığı

| # | Kontrol Maddesi | ✅ | Notlar |
|---|-----------------|----|--------|
| 0.2.1 | Yeni pano fabrikadan teslim alındı mı? | ☐ | Görsel hasar kontrolü |
| 0.2.2 | Pano içi ekipman montajı tamamlandı mı? | ☐ | NC300, R1-EC, Pilz, sürücüler |
| 0.2.3 | Kablo etiketleri hazır mı? | ☐ | Lazer yazıcı veya etiket makinesi |
| 0.2.4 | Kablo pabuçları ve terminaller hazır mı? | ☐ | Çeşitli kesitler |
| 0.2.5 | El aletleri hazır mı? | ☐ | Tornavida seti, kablo pensesi, crimper |
| 0.2.6 | Ölçüm cihazları hazır mı? | ☐ | Multimetre, izolasyon test cihazı |
| 0.2.7 | Laptop ve PLC yazılımı yüklü mü? | ☐ | Delta ISPSoft, DiaDesigner |
| 0.2.8 | Yedek sigorta ve röleler hazır mı? | ☐ | |

### 0.3 Dokümantasyon Hazırlığı

| # | Kontrol Maddesi | ✅ | Notlar |
|---|-----------------|----|--------|
| 0.3.1 | Elektrik şeması (DrawIO/KiCad) yazdırıldı mı? | ☐ | A3 boyut, laminasyon |
| 0.3.2 | I/O adres listesi hazır mı? | ☐ | |
| 0.3.3 | Kablo listesi (Wire List) hazır mı? | ☐ | |
| 0.3.4 | Terminal diyagramı hazır mı? | ☐ | |
| 0.3.5 | Eski pano şeması (mevcut ise) hazır mı? | ☐ | Referans için |

---

## 🔧 Faz 1: Eski Pano Sökümü

### 1.1 Enerji Kesme ve Güvenlik

| # | İşlem Adımı | ✅ | Tarih/Saat | İmza |
|---|-------------|----|------------|------|
| 1.1.1 | Makine operatörü ile son çalışma durumu teyit edildi | ☐ | __/__ __:__ | _________ |
| 1.1.2 | Ana şalter (Q1) OFF pozisyonuna alındı | ☐ | __/__ __:__ | _________ |
| 1.1.3 | LOTO kilidi ve etiketi takıldı | ☐ | __/__ __:__ | _________ |
| 1.1.4 | Gerilim yok kontrolü yapıldı (3F AC) | ☐ | __/__ __:__ | _________ |
| 1.1.5 | 24VDC besleme kesildi | ☐ | __/__ __:__ | _________ |
| 1.1.6 | Kondansatör deşarjı beklendi (min. 5 dakika) | ☐ | __/__ __:__ | _________ |
| 1.1.7 | Gerilim yok kontrolü tekrarlandı | ☐ | __/__ __:__ | _________ |

### 1.2 Saha Kablolarının Etiketlenmesi

> ⚠️ **KRİTİK:** Her kablo her iki ucundan da etiketlenmelidir!

| # | Kablo Grubu | ✅ | Etiket Formatı | Notlar |
|---|-------------|----|----------------|--------|
| 1.2.1 | X Ekseni Sensörleri | ☐ | `DI-X+-01`, `DI-X--01`, `DI-XH-01` | |
| 1.2.2 | Y Ekseni Sensörleri | ☐ | `DI-Y+-01`, `DI-Y--01`, `DI-YH-01` | |
| 1.2.3 | Z Ekseni Sensörleri | ☐ | `DI-Z+-01`, `DI-ZH-01` | |
| 1.2.4 | Alt Ekseni Sensörleri | ☐ | `DI-ALT+-01`, `DI-ALT--01`, `DI-ALTH-01` | |
| 1.2.5 | Servo Motor Güç (X) | ☐ | `PWR-X-01` (4G6mm²) | |
| 1.2.6 | Servo Motor Güç (Y) | ☐ | `PWR-Y-01` (4G4mm²) | |
| 1.2.7 | Servo Motor Güç (Alt) | ☐ | `PWR-ALT-01` (4G4mm²) | |
| 1.2.8 | Servo Motor Güç (Z) | ☐ | `PWR-Z-01` (3G2.5mm²) | |
| 1.2.9 | E-STOP Butonları | ☐ | `SAFE-EST-01/02` | |
| 1.2.10 | Safety Door Switch | ☐ | `SAFE-DOOR-01` | |
| 1.2.11 | Valfler (Vakum, Yağ) | ☐ | `DO-VAC-01`, `DO-OIL-01` | |
| 1.2.12 | AC Giriş (3F) | ☐ | `AC-IN-L1/2/3` (4G10mm²) | |

### 1.3 Kablo Bağlantılarının Çıkarılması

| # | İşlem Adımı | ✅ | Notlar |
|---|-------------|----|--------|
| 1.3.1 | Saha kabloları terminal bloklarından söküldü | ☐ | Etiketler kontrol edildi |
| 1.3.2 | Kablolar demetlendi ve geçici olarak sabitlendi | ☐ | Zemine temas etmemeli |
| 1.3.3 | Motor kabloları söküldü | ☐ | U/V/W faz sırası fotoğraflandı |
| 1.3.4 | EtherCAT/Ethernet kabloları söküldü | ☐ | RJ45 kapakları takıldı |
| 1.3.5 | Topraklama iletkenleri söküldü | ☐ | Son olarak sökülecek |
| 1.3.6 | Eski pano gövde bağlantıları kesildi | ☐ | |

### 1.4 Eski Pano Sökümü

| # | İşlem Adımı | ✅ | Notlar |
|---|-------------|----|--------|
| 1.4.1 | Pano kapakları söküldü | ☐ | Vidalar kaybedilmemeli |
| 1.4.2 | Pano gövde montaj cıvataları söküldü | ☐ | Genellikle M10-M12 |
| 1.4.3 | Pano kaldırma ekipmanı hazırlandı | ☐ | Transpalet veya vinç |
| 1.4.4 | Pano güvenli şekilde yerinden kaldırıldı | ☐ | 2-3 kişi ile çalışılmalı |
| 1.4.5 | Pano depolama alanına taşındı | ☐ | Devrilmeye karşı emniyete alınmalı |
| 1.4.6 | Pano montaj zemini temizlendi | ☐ | Yeni pano için hazır |

---

## 📦 Faz 2: Yeni Pano Montajı

### 2.1 Pano Yerleştirme

| # | İşlem Adımı | ✅ | Tarih/Saat | İmza |
|---|-------------|----|------------|------|
| 2.1.1 | Pano taşıma ekipmanı hazır edildi | ☐ | __/__ __:__ | _________ |
| 2.1.2 | Pano montaj alanına taşındı | ☐ | __/__ __:__ | _________ |
| 2.1.3 | Pano gövde terazisi ile nivolarlandı | ☐ | __/__ __:__ | _________ |
| 2.1.4 | Pano montaj cıvataları takıldı (M10-M12) | ☐ | __/__ __:__ | _________ |
| 2.1.5 | Cıvata tork değerleri kontrol edildi | ☐ | __/__ __:__ | _________ |
| 2.1.6 | Pano gövde topraklaması yapıldı | ☐ | __/__ __:__ | _________ |

### 2.2 Ana Güç Bağlantıları

| # | Bağlantı | Kablo Tipi | Tork (Nm) | ✅ | İmza |
|---|----------|------------|-----------|----|------|
| 2.2.1 | AC Giriş L1 → Q1 Giriş | 4G10mm² | 2.5-3.0 | ☐ | _________ |
| 2.2.2 | AC Giriş L2 → Q1 Giriş | 4G10mm² | 2.5-3.0 | ☐ | _________ |
| 2.2.3 | AC Giriş L3 → Q1 Giriş | 4G10mm² | 2.5-3.0 | ☐ | _________ |
| 2.2.4 | PE → Toprak Barası | 10mm² | 2.0-2.5 | ☐ | _________ |
| 2.2.5 | Q1 Çıkış → K1 Kontaktör | 4G6mm² | 2.0-2.5 | ☐ | _________ |
| 2.2.6 | K1 Çıkış → X Servo (U41) | 4G6mm² | 2.0-2.5 | ☐ | _________ |
| 2.2.7 | K1 Çıkış → Y Servo (U42) | 4G4mm² | 1.5-2.0 | ☐ | _________ |
| 2.2.8 | K1 Çıkış → Alt Servo (U43) | 4G4mm² | 1.5-2.0 | ☐ | _________ |
| 2.2.9 | PS1 AC Giriş → F1 Sigorta | 3G2.5mm² | 1.2-1.5 | ☐ | _________ |

### 2.3 24VDC Dağıtımı

| # | Bağlantı | Kablo Tipi | ✅ | İmza |
|---|----------|------------|----|------|
| 2.3.1 | PS1 +24V → X1 Terminal (Ana dağıtım) | 2G2.5mm² | ☐ | _________ |
| 2.3.2 | PS1 0V → X1 Terminal (Ana dağıtım) | 2G2.5mm² | ☐ | _________ |
| 2.3.3 | X1 → NC300 U1 (24VDC) | 2G1.5mm² | ☐ | _________ |
| 2.3.4 | X1 → HMI U2 (24VDC) | 2G1.5mm² | ☐ | _________ |
| 2.3.5 | X1 → R1-EC01 U50 (24VDC) | 2G1.5mm² | ☐ | _________ |
| 2.3.6 | X1 → Pilz K10 (24VDC) | 2G1.5mm² | ☐ | _________ |
| 2.3.7 | X1 → Sensör dağıtım | 2G1.5mm² | ☐ | _________ |

---

## 🔌 Faz 3: Saha Sensör Bağlantıları

### 3.1 X Ekseni Sensörleri (Leuze IS 218)

| # | Sensör | Terminal | PLC Adres | Kablo | ✅ |
|---|--------|----------|-----------|-------|----|
| 3.1.1 | X+ Limit (S11) | X20.1 | %IX0.0 | W401 | ☐ |
| 3.1.2 | X- Limit (S12) | X20.2 | %IX0.1 | W402 | ☐ |
| 3.1.3 | X Home (S10) | X20.3 | %IX0.2 | W403 | ☐ |

**Kablo Detayı:**
```
S10 X Home (Leuze IS 218)
├── Pin 1 (Brown)  → +24V (X2 Terminal)
├── Pin 2 (White)  → X20.3 (DI_2)
├── Pin 3 (Blue)   → 0V (X2 Terminal)
└── Pin 4 (Black)  → +24V (NO seçimi için)
```

### 3.2 Y Ekseni Sensörleri (Leuze IS 218)

| # | Sensör | Terminal | PLC Adres | Kablo | ✅ |
|---|--------|----------|-----------|-------|----|
| 3.2.1 | Y+ Limit (S21) | X20.4 | %IX0.3 | W404 | ☐ |
| 3.2.2 | Y- Limit (S22) | X20.5 | %IX0.4 | W405 | ☐ |
| 3.2.3 | Y Home (S20) | X20.6 | %IX0.5 | W406 | ☐ |

### 3.3 Z Ekseni Sensörleri (Leuze IS 218)

| # | Sensör | Terminal | PLC Adres | Kablo | ✅ |
|---|--------|----------|-----------|-------|----|
| 3.3.1 | Z+ Limit (S31) | X20.7 | %IX0.6 | W407 | ☐ |
| 3.3.2 | Z- Limit | X20.8 | %IX0.7 | W408 | ☐ |
| 3.3.3 | Z Home (S30) | X20.9 | %IX0.8 | W409 | ☐ |

### 3.4 Alt Ekseni Sensörleri (Leuze IS 218)

| # | Sensör | Terminal | PLC Adres | Kablo | ✅ |
|---|--------|----------|-----------|-------|----|
| 3.4.1 | Alt+ Limit (S41) | X20.10 | %IX0.9 | W410 | ☐ |
| 3.4.2 | Alt- Limit (S42) | X20.11 | %IX0.10 | W411 | ☐ |
| 3.4.3 | Alt Home (S40) | X20.12 | %IX0.11 | W412 | ☐ |

### 3.5 Güvenlik Sinyalleri

| # | Sinyal | Terminal | PLC Adres | Kablo | ✅ |
|---|--------|----------|-----------|-------|----|
| 3.5.1 | E-STOP Kanal 1 | X10.1 | %IX0.12 | W420 | ☐ |
| 3.5.2 | E-STOP Kanal 2 | X10.2 | %IX0.13 | W421 | ☐ |
| 3.5.3 | Safety Door | X10.3 | %IX0.14 | W422 | ☐ |
| 3.5.4 | Vakum OK | X10.4 | %IX0.15 | W423 | ☐ |

---

## 🌐 Faz 4: EtherCAT ve Network Bağlantıları

### 4.1 EtherCAT Hattı (Daisy Chain)

| # | Bağlantı | Port | Kablo | ✅ |
|---|----------|------|-------|----|
| 4.1.1 | NC300 CN1 (OUT) → X Servo U41 CN3 (IN) | CAT6 STP | ETH-01 | ☐ |
| 4.1.2 | X Servo U41 CN6 (OUT) → Y Servo U42 CN3 (IN) | CAT6 STP | ETH-02 | ☐ |
| 4.1.3 | Y Servo U42 CN6 (OUT) → Alt Servo U43 CN3 (IN) | CAT6 STP | ETH-03 | ☐ |
| 4.1.4 | Alt Servo U43 CN6 (OUT) → Z Servo U44 CN3 (IN) | CAT6 STP | ETH-04 | ☐ |
| 4.1.5 | Z Servo U44 CN6 (OUT) → C Servo U45 CN3 (IN) | CAT6 STP | ETH-05 | ☐ |
| 4.1.6 | C Servo U45 CN6 (OUT) → R1-EC01 U50 IN | CAT6 STP | ETH-06 | ☐ |
| 4.1.7 | R1-EC01 U50 OUT → NC300 CN2 (IN) | CAT6 STP | ETH-07 | ☐ |

### 4.2 Ethernet (HMI)

| # | Bağlantı | Port | Kablo | ✅ |
|---|----------|------|-------|----|
| 4.2.1 | NC300 CN3 → HMI U2 ETH | CAT5e/6 | NET-01 | ☐ |

**IP Ayarları:**
| Cihaz | IP Adres | Subnet Mask | Gateway |
|-------|----------|-------------|---------|
| NC300 | 192.168.1.10 | 255.255.255.0 | - |
| HMI | 192.168.1.11 | 255.255.255.0 | 192.168.1.10 |

---

## ⚡ Faz 5: Dijital Çıkış Bağlantıları (DO)

### 5.1 R1-EC0902O Çıkışları

| # | Çıkış | Terminal | Yük | Kablo | ✅ |
|---|-------|----------|-----|-------|----|
| 5.1.1 | %QX0.0 | X40.1 | SERVO_ENABLE | W501 | ☐ |
| 5.1.2 | %QX0.1 | X40.2 | VACUUM_PUMP | W502 | ☐ |
| 5.1.3 | %QX0.2 | X40.3 | OIL_PUMP | W503 | ☐ |
| 5.1.4 | %QX0.3 | X40.4 | COOLING_FAN | W504 | ☐ |
| 5.1.5 | %QX0.4 | X40.5 | WARNING_LIGHT | W505 | ☐ |
| 5.1.6 | %QX0.5 | X40.6 | BUZZER | W506 | ☐ |
| 5.1.7 | %QX0.6 | X40.7 | MARKER | W507 | ☐ |
| 5.1.8 | %QX0.7 | X40.8 | BREAKER_ENABLE | W508 | ☐ |
| 5.1.9 | %QX0.8 | X40.9 | HEATER_ZONE1 | W509 | ☐ |
| 5.1.10 | %QX0.9 | X40.10 | HEATER_ZONE2 | W510 | ☐ |
| 5.1.11 | %QX0.10 | X40.11 | HEATER_ZONE3 | W511 | ☐ |
| 5.1.12 | %QX0.11 | X40.12 | CONVEYOR_FWD | W512 | ☐ |
| 5.1.13 | %QX0.12 | X40.13 | CONVEYOR_REV | W513 | ☐ |
| 5.1.14 | %QX0.13 | X40.14 | SPRAY_VALVE | W514 | ☐ |
| 5.1.15 | %QX0.14 | X40.15 | CLEAN_VALVE | W515 | ☐ |
| 5.1.16 | %QX0.15 | X40.16 | LIGHT_CURTAIN | W516 | ☐ |

---

## 🧪 Faz 6: Devreye Alma Testleri

### 6.1 Görsel ve Mekanik Kontrol

| # | Kontrol Maddesi | ✅ | Notlar |
|---|-----------------|----|--------|
| 6.1.1 | Tüm kablo bağlantıları sıkı mı? | ☐ | Tork kontrolü randomize |
| 6.1.2 | Kablo etiketleri doğru ve okunabilir mi? | ☐ | |
| 6.1.3 | Pano içi yabancı cisim yok mu? | ☐ | Vida, pul, kablo ucu vb. |
| 6.1.4 | Topraklama bağlantıları sağlam mı? | ☐ | |
| 6.1.5 | Tüm ekipman montajı sağlam mı? | ☐ | |
| 6.1.6 | Soğutma kanalları açık mı? | ☐ | |
| 6.1.7 | Pano kapakları contaları doğru yerleştirildi mi? | ☐ | IP65 bütünlüğü |

### 6.2 Süreklilik Testleri (Güç YOK)

| # | Test | Beklenen | Ölçülen | ✅ |
|---|------|----------|---------|----|
| 6.2.1 | L1 → Q1 Giriş | < 1Ω | _____ Ω | ☐ |
| 6.2.2 | L2 → Q1 Giriş | < 1Ω | _____ Ω | ☐ |
| 6.2.3 | L3 → Q1 Giriş | < 1Ω | _____ Ω | ☐ |
| 6.2.4 | PE → Pano Gövde | < 0.1Ω | _____ Ω | ☐ |
| 6.2.5 | +24V → 0V (Kısa devre yok) | > 1MΩ | _____ Ω | ☐ |
| 6.2.6 | X20 DI terminalleri → R1-EC | < 1Ω | _____ Ω | ☐ |

### 6.3 İlk Güç Verme (24VDC)

| # | Test | Beklenen | Ölçülen | ✅ |
|---|------|----------|---------|----|
| 6.3.1 | PS1 +24V çıkış | 24.0 ± 0.5V | _____ V | ☐ |
| 6.3.2 | NC300 24V girişi | 24.0 ± 0.5V | _____ V | ☐ |
| 6.3.3 | R1-EC 24V girişi | 24.0 ± 0.5V | _____ V | ☐ |
| 6.3.4 | Pilz 24V girişi | 24.0 ± 0.5V | _____ V | ☐ |
| 6.3.5 | Toplam 24VDC akım tüketimi | < 5A (boşta) | _____ A | ☐ |
| 6.3.6 | PS1 sıcaklık artışı | < 40°C | _____ °C | ☐ |

### 6.4 PLC ve I/O Testi

| # | Test | Beklenen | Sonuç | ✅ |
|---|------|----------|-------|----|
| 6.4.1 | NC300 güç LED | YEŞİL | _____ | ☐ |
| 6.4.2 | NC300 RUN LED | YEŞİL (yanıp sönmez) | _____ | ☐ |
| 6.4.3 | R1-EC01 PWR LED | YEŞİL | _____ | ☐ |
| 6.4.4 | R1-EC01 ERR LED | KAPALI | _____ | ☐ |
| 6.4.5 | R1-EC01 NET LED | YEŞİL (yanıp sönmez) | _____ | ☐ |
| 6.4.6 | EtherCAT slave sayısı | 7 (5 servo + 1 R1-EC + 1 NC300) | _____ | ☐ |
| 6.4.7 | Tüm DI girişleri okunuyor | HMI'den doğrula | _____ | ☐ |
| 6.4.8 | Tüm DO çıkışları test | Manuel tetikleme | _____ | ☐ |

### 6.5 Safety Sistemi Testi (Pilz PNOZ)

| # | Test | Beklenen | Sonuç | ✅ |
|---|------|----------|-------|----|
| 6.5.1 | Pilz PWR LED | YEŞİL | _____ | ☐ |
| 6.5.2 | E-STOP Kanal 1 | Pilz IN1 OK | _____ | ☐ |
| 6.5.3 | E-STOP Kanal 2 | Pilz IN2 OK | _____ | ☐ |
| 6.5.4 | Safety Door | Pilz IN3 OK | _____ | ☐ |
| 6.5.5 | E-STOP basıldığında | Pilz OUT1/OUT2 OFF | _____ | ☐ |
| 6.5.6 | E-STOP basıldığında | Tüm servo STO aktif | _____ | ☐ |
| 6.5.7 | E-STOP reset | Pilz OUT1/OUT2 ON | _____ | ☐ |
| 6.5.8 | Reset sonrası | Servo enable mümkün | _____ | ☐ |

### 6.6 STO Güvenlik Testi

| Eksen | STO Testi | Beklenen | Sonuç | ✅ |
|-------|-----------|----------|-------|----|
| X | STO aktif | Motor serbest (tork yok) | _____ | ☐ |
| Y | STO aktif | Motor serbest (tork yok) | _____ | ☐ |
| Z | STO aktif | Motor serbest + Fren aktif | _____ | ☐ |
| Alt | STO aktif | Motor serbest (tork yok) | _____ | ☐ |
| C | STO aktif | Motor serbest (tork yok) | _____ | ☐ |

### 6.7 EtherCAT Network Testi

| # | Test | Beklenen | Sonuç | ✅ |
|---|------|----------|-------|----|
| 6.7.1 | EtherCAT State → OP | Tüm slave'ler OP | _____ | ☐ |
| 6.7.2 | Cycle Time | 100 μs | _____ μs | ☐ |
| 6.7.3 | Sync Error | 0 | _____ | ☐ |
| 6.7.4 | PDO mapping | Doğru | _____ | ☐ |
| 6.7.5 | SDO communication | OK | _____ | ☐ |

---

## 🏠 Faz 7: Home Sequence Testi

### 7.1 Manuel Eksen Hareketi (JOG)

> ⚠️ **DİKKAT:** İlk hareket öncesi tüm personelin makine alanından uzakta olduğundan emin olun!

| # | Test | Beklenen | Sonuç | ✅ |
|---|------|----------|-------|----|
| 7.1.1 | X+ JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.2 | X- JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.3 | Y+ JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.4 | Y- JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.5 | Z+ JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.6 | Z- JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.7 | Alt+ JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.8 | Alt- JOG | Eksen hareket eder | _____ | ☐ |
| 7.1.9 | Limit switch tetiklendiğinde | Eksen durur | _____ | ☐ |

### 7.2 Home Sequence Testi

| # | Eksen | Test Adımı | Beklenen | Sonuç | ✅ |
|---|-------|------------|----------|-------|----|
| 7.2.1 | X | Home start | Eksen geri yönde hareket | _____ | ☐ |
| 7.2.2 | X | Home switch algılama | Hız düşürülür | _____ | ☐ |
| 7.2.3 | X | Switch'ten çıkış | Pozitif yönde hareket | _____ | ☐ |
| 7.2.4 | X | Rising edge | Pozisyon = 0 | _____ | ☐ |
| 7.2.5 | Y | Home sequence | X ile aynı | _____ | ☐ |
| 7.2.6 | Z | Home sequence | Pozisyon = 0 | _____ | ☐ |
| 7.2.7 | Alt | Home sequence | Pozisyon = 0 | _____ | ☐ |
| 7.2.8 | Tüm eksenler | Home tamamlandı | HMI'de "Home OK" | _____ | ☐ |

### 7.3 Pozisyon Doğrulama

| # | Test | Beklenen | Ölçülen | ✅ |
|---|------|----------|---------|----|
| 7.3.1 | X Home pozisyonu | X = 0.00 mm | _____ mm | ☐ |
| 7.3.2 | Y Home pozisyonu | Y = 0.00 mm | _____ mm | ☐ |
| 7.3.3 | Z Home pozisyonu | Z = 0.00 mm | _____ mm | ☐ |
| 7.3.4 | Alt Home pozisyonu | Alt = 0.00 mm | _____ mm | ☐ |
| 7.3.5 | X+ Limit pozisyonu | X ≈ 5950 mm | _____ mm | ☐ |
| 7.3.6 | Y+ Limit pozisyonu | Y ≈ 2950 mm | _____ mm | ☐ |

---

## 📝 Faz 8: Final Dokümantasyon ve Teslim

### 8.1 As-Built Dokümantasyon

| # | Doküman | ✅ | Notlar |
|---|---------|----|--------|
| 8.1.1 | Güncellenmiş elektrik şeması | ☐ | Değişiklikler işlendi |
| 8.1.2 | Güncellenmiş kablo listesi | ☐ | Gerçeklen kablo numaraları |
|