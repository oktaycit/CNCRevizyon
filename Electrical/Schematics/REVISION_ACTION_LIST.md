# GFB60-30RE-S Elektrik Şeması Revizyon Aksiyon Listesi

**Tarih:** 2026-04-07  
**Hedef:** Revizyon 4.1 Tamamlama  
**Öncelik:** Yüksek

---

## 📋 Revizyon 4.1 - Kritik Aksiyonlar

### ✅ TAMAMLANDI

- [x] WIRING_REFERENCE.md oluşturuldu
- [x] SCHEMATIC_COMPLETION_SUMMARY.md oluşturuldu
- [x] Sensor_Mounting_Details.md oluşturuldu
- [x] DrawIO Sayfa 01-02 taslakları oluşturuldu
- [x] Comparison Report oluşturuldu
- [x] Tüm user manual'ler indirildi

---

### 🔴 YÜKSENC ÖNCELİK (Bu Hafta)

#### 1. Sayfa 01 Revizyonu - Ana Güç ve 24VDC

**EMC Filtre Ekleme**
- [ ] DrawIO'da EMC filtre bloğu çiz
- [ ] Model: Delta EMI-F400V-10A
- [ ] Bağlantı: X1 → EMC → Q1
- [ ] L1/L2/L3/N → L1'/L2'/L3'/N'
- [ ] PE bağlantısını göster

**Faz Kontrol Rölesi Ekleme**
- [ ] Pilz PNOZ EF Phase Monitor ekle
- [ ] 3-faz giriş (L1/L2/L3/N)
- [ ] Alarm çıkışı (NC/NO)
- [ ] NC300 DI girişine bağla
- [ ] LED durumlarını göster

**Parafudr Ekleme**
- [ ] Phoenix Contact VAL-MS 400/3+1 ekle
- [ ] L1/L2/L3/N → PE koruması
- [ ] Paralel bağlantı göster
- [ ] PE bar bağlantısını detaylandır

**Kablo Kesiti Güncelleme**
- [ ] AC Ana Giriş: 6mm² → 10mm²
- [ ] DC Ana Dağıtım: 2.5mm² → 4mm²
- [ ] AC Servo X: 4mm² → 6mm²
- [ ] AC Servo Y/ALT: 2.5mm² → 4mm²
- [ ] Tüm kesitleri şemada işaretle

**DC-DC Izole Converter (Opsiyonel)**
- [ ] Delta DPS-24V-5A ekle
- [ ] Critical loads için
- [ ] Safety circuit beslemesi
- [ ] I/O beslemesi

**Güncellenecek Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 01)

---

#### 2. Sayfa 02 Revizyonu - Emniyet ve STO

**E-STOP Buton Detayı**
- [ ] Schneider XB4-BS542 modeli ekle
- [ ] 2NC kontak göster
- [ ] Mushroom head sembolü
- [ ] Kırmızı/Sarı renk kodu
- [ ] Mekanik kilit işaretle

**Safety Door Switch Detayı**
- [ ] Omron D4GS-NK2 ekle
- [ ] 2NC + 1NO kontak
- [ ] Mekanik kilit işaretle
- [ ] Mıknatıs sembolü

**STO Dağıtım Revizyonu**
- [ ] Her eksen için ayrı çift hat
- [ ] X11.1-2 → X axis STO1/STO2
- [ ] X11.3-4 → Y axis STO1/STO2
- [ ] X11.5-6 → ALT axis STO1/STO2
- [ ] X11.7-8 → Z axis STO1/STO2
- [ ] X11.9-10 → CNC axis STO1/STO2
- [ ] Shielded twisted pair notu

**STO Feedback Ekleme**
- [ ] Her servo DO_1 (ALM) → NC300 DI
- [ ] Feedback monitoring devresi
- [ ] HMI alarm sayfası referansı
- [ ] LED status indicator

**Reset Logic Diyagramı**
- [ ] Akış diyagramı ekle
- [ ] Koşullar:
  - Tüm E-STOP çekili
  - Kapı kapalı
  - 3 saniye bekleme
  - Alarm yok
- [ ] Manual reset vurgusu

**Güncellenecek Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 02)

---

#### 3. Sayfa 03 Oluşturma - NC300 ve EtherCAT

**NC300 Ana Blok**
- [ ] 24VDC besleme (2A)
- [ ] F2 sigorta (3A)
- [ ] FG topraklama
- [ ] Status LED'leri

**CN1/CN2 EtherCAT**
- [ ] RJ45 konnektör sembolü
- [ ] CN1: OUT → X ekseni
- [ ] CN2: IN ← CNC ekseni
- [ ] CAT6 shielded notu
- [ ] Topraklama detayı

**CN3 HMI Ethernet**
- [ ] RJ45 → DOP-110CS
- [ ] IP adresleri:
  - NC300: 192.168.1.10
  - HMI: 192.168.1.11
- [ ] TCP/IP notu

**CN5 50-pin I/O**
- [ ] D-Sub 50-pin sembolü
- [ ] DI_0 - DI_4 pinout
- [ ] DO_0 - DO_2 pinout
- [ ] +24V_EXT (500mA)
- [ ] GND_I/O
- [ ] Shield sonlandırma

**EtherCAT Topolojisi**
- [ ] Daisy-chain diyagramı
- [ ] Node adresleri:
  - 0: NC300 (Master)
  - 1: X ekseni
  - 2: Y ekseni
  - 3: ALT ekseni
  - 4: Z ekseni
  - 5: CNC ekseni
  - 6: R1-EC
- [ ] Cycle time: 1ms

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 03 - yeni)

---

#### 4. Sayfa 04 Oluşturma - Servo Sürücüler (5 Alt Sayfa)

**Sayfa 04-A: X Ekseni (4.5kW)**
- [ ] ASD-A3-4523-E sembolü
- [ ] ECMA-L11845 motor
- [ ] P1: R/S/T (3F 400VAC, 25A)
- [ ] P2: U/V/W (4mm²)
- [ ] CN1: 50-pin I/O
- [ ] CN2: 6-pin encoder
- [ ] CN3/CN6: EtherCAT RJ45
- [ ] STO1/STO2 (X11.1-2)
- [ ] Rejeneratif: 60Ω/100W
- [ ] Kablo kesitleri

**Sayfa 04-B: Y Ekseni (2.0kW)**
- [ ] ASD-A3-2023-E sembolü
- [ ] ECMA-E11320 motor
- [ ] P1: R/S/T (3F 400VAC, 16A)
- [ ] P2: U/V/W (2.5mm²)
- [ ] CN1/CN2/CN3/CN6
- [ ] STO1/STO2 (X11.3-4)
- [ ] Rejeneratif: 60Ω/50W

**Sayfa 04-C: ALT Ekseni (2.0kW)**
- [ ] Y ekseni ile aynı
- [ ] STO1/STO2 (X11.5-6)

**Sayfa 04-D: Z Ekseni (1.0kW, FRENLİ)**
- [ ] ASD-A3-1023-E sembolü
- [ ] ECMA-C11010FS motor (frenli)
- [ ] P1: R/L1, S/L2 (1F 230VAC, 10A)
- [ ] P2: U/V/W
- [ ] Fren: 24VDC, 0.35A
- [ ] DO_5 → BRK kontrol
- [ ] STO1/STO2 (X11.7-8)
- [ ] Rejeneratif: 120Ω/50W

**Sayfa 04-E: CNC Ekseni (1.5kW)**
- [ ] ASD-A3-1523-E sembolü
- [ ] ECMA-E11315 motor
- [ ] P1: R/L1, S/L2 (1F 230VAC, 10A)
- [ ] P2: U/V/W
- [ ] CN1/CN2/CN3/CN6
- [ ] STO1/STO2 (X11.9-10)
- [ ] Rejeneratif: 80Ω/50W

**Ortak Notlar (Tüm Sayfalar):**
- [ ] Shielded motor kablosu
- [ ] Max 20m mesafe
- [ ] Encoder: 24-bit absolute
- [ ] EtherCAT cycle time: 1ms

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 04-A/B/C/D/E - yeni)

---

#### 5. Sayfa 05 Oluşturma - R1-EC I/O Modülleri

**R1-EC01 Bus Coupler**
- [ ] EtherCAT IN/OUT (RJ45)
- [ ] 24VDC besleme (150mA)
- [ ] V_IO besleme (harici)
- [ ] GND_IO
- [ ] Status LED'leri (RUN, ERR, I/O)
- [ ] Node adresi: 6

**R1-EC0902D #1 (32-CH DI - X/Y Sensörleri)**
- [ ] %IX0.0 - %IX1.15 adresleme
- [ ] Terminal block 1 (DI_0 - DI_15)
- [ ] Terminal block 2 (DI_16 - DI_31)
- [ ] X/Y/Z/ALT limit ve home
- [ ] COM 0V bağlantısı
- [ ] 24VDC besleme (100mA)

**R1-EC0902D #2 (32-CH DI - Diğer Sensörler)**
- [ ] %IX2.0 - %IX3.15 adresleme
- [ ] Cam, vakum, kapı sensörleri
- [ ] Terminal block 1-2
- [ ] COM 0V bağlantısı

**R1-EC0902O (32-CH DO Relay)**
- [ ] %QX0.0 - %QX1.15 adresleme
- [ ] Röle kontakları (SPST, 2A, 250VAC)
- [ ] Flyback diyot (indüktif yük)
- [ ] Terminal block 1-2
- [ ] V_IO besleme

**I/O Adres Tablosu**
- [ ] Tüm I/O listesi
- [ ] Fonksiyon açıklaması
- [ ] Kaynak/hedef bilgisi

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 05 - yeni)

---

### 🟡 ORTA ÖNCELİK (Gelecek Hafta)

#### 6. Sayfa 06 Oluşturma - Sensör Detayları

**Leuze IS 218 Sembolü**
- [ ] M18 sensör sembolü
- [ ] M12 4-pin konnektör
- [ ] LED göstergeleri (PWR, OUT)
- [ ] NO/NC select input

**Kablo Routing**
- [ ] 4x0.34mm² shielded
- [ ] Renk kodu: Brown/White/Blue/Black
- [ ] Kablo kanalı routing
- [ ] Drag chain detayı
- [ ] Min bending radius: 6x cable diameter

**Shield Sonlandırma**
- [ ] 360° shield clamp
- [ ] PE bar bağlantısı
- [ ] Pigtail yasak

**Test Noktaları**
- [ ] Test point ekleme
- [ ] LED durum tablosu
- [ ] HMI diagnostic sayfası referansı

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 06 - yeni)

---

#### 7. Sayfa 07 Oluşturma - Aktüatör Detayları

**Valf Çıkışları**
- [ ] %QX0.0 - %QX0.7 adresleme
- [ ] Röle çıkışları (SPST)
- [ ] Flyback diyot
- [ ] Sigorta (F7-F10, 2A)
- [ ] 24VDC besleme

**Uyarı Lambası**
- [ ] 24VDC, 21W
- [ ] Kablo: 1.5mm²
- [ ] Sigorta: 2A
- [ ] %QX0.4 kontrol

**Buzzer**
- [ ] 24VDC, 85dB
- [ ] Kontrol rölesi
- [ ] %QX0.5 kontrol

**Vakum Pompa Kontaktörü**
- [ ] K2 kontaktör
- [ ] Termik röle
- [ ] Sigorta (10A)
- [ ] Aux kontak feedback
- [ ] %QX0.1 kontrol

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 07 - yeni)

---

#### 8. Sayfa 08 Oluşturma - Terminal Planı

**Terminal Blok Yerleşimi**
- [ ] X1: AC Giriş (L1/L2/L3/N/PE)
- [ ] X2: 24V DC Dağıtım (8 çıkış)
- [ ] X10: Safety Inputs
- [ ] X11: STO Outputs
- [ ] X20: DI Terminals (R1-EC)
- [ ] X30: EtherCAT
- [ ] X31: Network

**Terminal Tip Detayları**
- [ ] Phoenix Contact modelleri
- [ ] Screw vs spring
- [ ] Torque değerleri
- [ ] Kablo kesiti aralığı

**Wire Marker Şeması**
- [ ] Her kablo için marker
- [ ] Kaynak → Hedef formatı
- [ ] Renk kodları

**Kablo Pabuçları**
- [ ] Lug tip ve boyutları
- [ ] Crimping tool referansı
- [ ] Heat shrink detayları

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 08 - yeni)

---

#### 9. Sayfa 09 Oluşturma - Pin Planı

**M12 4-pin Sensör**
- [ ] Pinout: 1(+24V), 2(OUT), 3(0V), 4(NO/NC)
- [ ] Housing modeli
- [ ] Locking mechanism
- [ ] IP67 koruma

**RJ45 EtherCAT**
- [ ] Pinout: 1,2(TX), 3,6(RX)
- [ ] Endüstriyel kilitli
- [ ] CAT6 shielded

**D-Sub 50-pin (CN1)**
- [ ] Tüm pinout detayı
- [ ] Shield sonlandırma
- [ ] Screw lock

**6-pin Encoder (CN2)**
- [ ] Pinout: 1(+5V), 2-6(A, /A, B, /B, Z)
- [ ] Hirose HR10A-7P-6S

**Kablo Renk Kodları**
- [ ] AC: Kahverengi/Siyah/Gri/Mavi/Yeşil-Sarı
- [ ] DC: Kırmızı(+24V), Siyah(0V)
- [ ] Safety: Sarı
- [ ] Sensor: Mavi

**Oluşturulacak Dosya:**
`Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical.drawio` (Sayfa 09 - yeni)

---

### 🟢 DÜŞÜK ÖNCELİK (Revizyon 5.0)

#### 10. BOM Oluşturma

**Component Listesi**
- [ ] Tüm component'lar
- [ ] Model numaraları
- [ ] Üretici bilgisi
- [ ] Tedarikçi referansı
- [ ] Miktar ve birim
- [ ] Tahmini fiyat

**Kablo Listesi**
- [ ] Kablo tipleri
- [ ] Kesitler
- [ ] Renkler
- [ ] Uzunluklar
- [ ] Üretici

**Konnektör Listesi**
- [ ] Tüm konnektörler
- [ ] Housing modelleri
- [ ] Crimp terminaler
- [ ] Aksesuarlar

**Oluşturulacak Dosya:**
`Electrical/BOM/GFB60-30RE-S_BOM.xlsx`

---

#### 11. KiCad Migration

**Proje Kurulumu**
- [ ] KiCad proje oluştur
- [ ] Library'leri yükle
- [ ] Template ayarla

**Şema Aktarımı**
- [ ] Her sayfayı KiCad'e aktar
- [ ] Component footprint'leri
- [ ] Wire bağlantıları
- [ ] Net labels

**ERC/DRC Check**
- [ ] Electrical Rule Check
- [ ] Design Rule Check
- [ ] Hata düzeltmeleri

**BOM Export**
- [ ] KiCad BOM export
- [ ] CSV format
- [ ] Digikey/Mouser format

**PDF Export**
- [ ] Her sayfa PDF
- [ ] BOM PDF
- [ ] Plot settings

---

#### 12. 3D Panel Layout

**Component Yerleşimi**
- [ ] 3D model import
- [ ] Panel yerleşimi
- [ ] Clearance check
- [ ] Thermal analysis

**Kablo Yönlendirme**
- [ ] Kablo kanalı 3D
- [ ] Drag chain path
- [ ] Bend radius check

---

## 📊 İlerleme Takibi

### Haftalık Hedefler

**Hafta 1 (2026-04-07 - 2026-04-13):**
- [ ] Sayfa 01 revizyonu tamamlandı
- [ ] Sayfa 02 revizyonu tamamlandı
- [ ] Sayfa 03 oluşturuldu
- [ ] BOM template hazır

**Hafta 2 (2026-04-14 - 2026-04-20):**
- [ ] Sayfa 04 (A/B/C/D/E) tamamlandı
- [ ] Sayfa 05 oluşturuldu
- [ ] Component araştırması bitti

**Hafta 3 (2026-04-21 - 2026-04-27):**
- [ ] Sayfa 06 oluşturuldu
- [ ] Sayfa 07 oluşturuldu
- [ ] Sayfa 08 oluşturuldu
- [ ] Sayfa 09 oluşturuldu

**Hafta 4 (2026-04-28 - 2026-05-04):**
- [ ] Final validasyon
- [ ] PDF export
- [ ] Review meeting
- [ ] Approval

---

## 📝 Günlük Çalışma Logu

### 2026-04-07
- [x] Comparison Report oluşturuldu
- [x] Action List oluşturuldu
- [ ] Sayfa 01 revizyonu başlatıldı

**Yapılan:**
- Mevcut durum analizi
- Eksiklik tespiti
- Önceliklendirme

**Sonraki:**
- EMC filtre ekleme
- Faz kontrol ekleme
- Parafudr ekleme

### 2026-04-08
- [ ] Sayfa 01 revizyonu devam
- [ ] Sayfa 02 revizyonu başlat

### 2026-04-09
- [ ] Sayfa 01 tamamla
- [ ] Sayfa 02 devam

### 2026-04-10
- [ ] Sayfa 02 tamamla
- [ ] Sayfa 03 başlat

### 2026-04-11
- [ ] Sayfa 03 tamamla
- [ ] Haftalık review

---

## 🎯 Başarı Kriterleri

### Revizyon 4.1 Tamamlama Kriterleri

**Sayfa 01-02:**
- ✅ EMC filtre eklendi
- ✅ Faz kontrol eklendi
- ✅ Parafudr eklendi
- ✅ Kablo kesitleri güncel
- ✅ STO dağıtım detaylı
- ✅ E-STOP model detaylı
- ✅ Reset logic eklendi

**Sayfa 03-09:**
- ✅ Tüm sayfalar oluşturuldu
- ✅ Tüm pinout'lar doğru
- ✅ I/O adresleme tamam
- ✅ Grounding detaylı
- ✅ BOM hazır

**Kalite:**
- ✅ GFB standartlarına uygun
- ✅ Delta referanslarına uygun
- ✅ Safety normlarına uygun (PL e, SIL 3)
- ✅ EMC uyumlu

---

**Son Güncelleme:** 2026-04-07  
**Hazırlayan:** CNCRevizyon Elektrik Revizyon Ekibi  
**Versiyon:** 1.0  
**Durum:** 🔄 DEVAM EDİYOR
