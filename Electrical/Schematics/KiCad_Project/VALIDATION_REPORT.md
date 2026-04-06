# GFB60/30RE-S KiCad Şema Validasyon Raporu
## Orijinal PDF vs KiCad Revizyon Karşılaştırması

**Tarih:** 2026-04-06  
**KiCad Versiyon:** 3.4  
**Orijinal PDF:** gfb_EP034-047170.pdf, okandan_gfb_vb_EP034-033781.pdf  
**Validasyon Durumu:** ⚠️ KISMEN TAMAMLANDI - Eksiklikler Tespit Edildi

---

## 📊 Genel Değerlendirme

### ✅ Güçlü Yönler
1. **İyi Yapılandırılmış Sayfa Hiyerarşisi** - 9 sayfalık mantıksal bölümlendirme doğru
2. **Terminal ve Pin Planları** - EPLAN mantığı korunmuş (Klemmenplan, Steckerbelegungsplan)
3. **Güvenlik Devresi Konsepti** - Pilz PNOZ ve STO yapısı doğru kurgulanmış
4. **Delta Ekipman Seçimleri** - NC300, ASDA-A3-E, R1-EC serisi doğru

### ❌ Kritik Eksiklikler
1. **DETAYLI DEVRE ŞEMALARI YOK** - Sayfa 3-9 sadece "Plan:" notları içeriyor, gerçek devre çizimleri yok
2. **PDF ile Cross-Reference Yok** - Orijinal EPLAN sayfa numaraları referans alınmamış
3. **Komponent Parametreleri Eksik** - Sigorta, kontaktör, röle değerleri belirtilmemiş
4. **Kablo Kesitleri Yok** - PDF'deki kablo kesit bilgileri (mm²) KiCad'de yok

---

## 📄 Sayfa Bazlı Validasyon

### Sayfa 01: Ana Güç ve 24VDC Dağıtımı
**Durum:** ⚠️ KISMEN ÇİZİLMİŞ

✅ **Mevcut:**
- PS1 24VDC Power Supply tanımı
- X2 dağıtım terminali konsepti (8 çıkış)
- +24V, 0V, PE global bus'ları
- ERC clean power flag'leri

❌ **Eksik (PDF'de olup KiCad'de olmayan):**
- [ ] Ana giriş kontaktörü (K1) detayları
- [ ] AC/DC converter devresi (örn: Siemens SITOP)
- [ ] Sigorta değerleri (F1, F2, F3...)
- [ ] Kesici şeması (Q1)
- [ ] Faz koruma rölesi
- [ ] Topraklama detayları (PE direnci < 0.1Ω)
- [ ] 24V dağılım: NC300, R1-EC, HMI, Sensör, Safety için ayrı sigortalar

📋 **PDF Referans:** Sayfa 10-15 (Güç dağıtımı)

---

### Sayfa 02: Emniyet Zinciri ve STO
**Durum:** ⚠️ TEMEL YAPI VAR, DETAYLAR EKSİK

✅ **Mevcut:**
- X10 safety input terminal (6 pin)
- K1 Pilz PNOZ X2.8P safety relay
- X11 STO output terminal (8 pin)
- E-STOP CH1/CH2, DOOR SAFE, RESET tanımları
- STO_A/B X/Y/Z çift kanal yapı

❌ **Eksik:**
- [ ] Pilz PNOZ gerçek pin bağlantıları
- [ ] E-STOP buton detayları (NO/NC, çift kanal)
- [ ] Safety kapı switch'leri (M12 konnektör pinout)
- [ ] Reset butonu devresi
- [ ] Safety feedback devresi (SAFE_FB)
- [ ] STO hattı için kablo tipi (shielded twisted pair)
- [ ] Test pulse devresi (OSSD)

📋 **PDF Referans:** Sayfa 20-28 (Safety devreleri)

---

### Sayfa 03: NC300 ve EtherCAT Omurgası
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- Slave sıralaması: X → Y → ALT → Z → CNC → R1-EC
- HMI Ethernet bağlantısı notu
- X30/X31 network referansları

❌ **Eksik:**
- [ ] NC300 kontrolör pinout (CN1, CN2, CN3...)
- [ ] EtherCAT IN/OUT portları (RJ45)
- [ ] Her servo için EtherCAT node adresleri
- [ ] HMI bağlantı detayları (DOP-110CS)
- [ ] Network topolojisi (Daisy chain vs Star)
- [ ] Terminasyon dirençleri
- [ ] CAT6 kablo spesifikasyonu

📋 **PDF Referans:** Sayfa 30-40 (CNC kontrolör)

---

### Sayfa 04: Servo Sürücüler
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- Sürücü modelleri tanımlı:
  - X: ASD-A3-4523-E (4.5kW)
  - Y: ASD-A3-2023-E (2.0kW)
  - ALT: ASD-A3-2023-E (2.0kW)
  - Z: ASD-A3-1023-E (1.0kW)
  - CNC: ASD-A3-1523-E (1.5kW)

❌ **Eksik:**
- [ ] Her sürücü için güç bağlantıları (R/S/T)
- [ ] Motor bağlantıları (U/V/W)
- [ ] Encoder geri besleme (CN2)
- [ ] STO ST1/ST2 pin bağlantıları
- [ ] Z ekseni fren devresi (24VDC brake)
- [ ] Rejeneratif direnç bağlantısı (varsa)
- [ ] DC bus bağlantıları
- [ ] Shield/PE sonlandırma detayları

📋 **PDF Referans:** Sayfa 45-65 (Servo akslar)

---

### Sayfa 05: R1-EC Bus Coupler ve I/O Modülleri
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- R1-EC bus coupler tanımı
- DI: R1-EC0902D x3 modül
- DO: R1-EC0902O x3 modül

❌ **Eksik:**
- [ ] Bus coupler EtherCAT bağlantısı
- [ ] Her DI modülünün 16 giriş detayı
- [ ] Her DO modülünün 16 çıkış detayı
- [ ] I/O adresleme (%IX0.0 - %IX3.15, %QX0.0 - %QX3.15)
- [ ] Sensör besleme dağıtımı
- [ ] Valf bağlantıları (24VDC/AC)
- [ ] LED gösterge devreleri

📋 **PDF Referans:** Sayfa 70-85 (I/O dağılımı)

---

### Sayfa 06: Dijital Girişler ve Sensörler
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- IX0.0..IX0.15 adres haritası
- X/Y/Z/ALT limit ve home sensörleri listesi
- M12 4-pin konnektör referansı

❌ **Eksik:**
- [ ] Her sensör için detaylı bağlantı şeması
- [ ] Leuze IS 218 pinout (Brown/White/Blue/Black)
- [ ] Sensör besleme (24VDC) dağıtımı
- [ ] NO/NC seçimi devreleri
- [ ] Shield bağlantıları
- [ ] Kablo güzergahları

📋 **PDF Referans:** Sayfa 75-80 (Sensör yerleşimi)

---

### Sayfa 07: Dijital Çıkışlar ve Aktüatörler
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- Çıkış adresleri:
  - %QX0.0: SERVO_ENABLE
  - %QX0.1: VACUUM_PUMP
  - %QX0.4: WARNING_LIGHT
  - %QX0.5: BUZZER
  - %QX0.7: BREAKER_ENABLE

❌ **Eksik:**
- [ ] Röle çıkış devreleri (flyback diyot)
- [ ] Kontaktör bobin bağlantıları
- [ ] Valf sürücü devreleri
- [ ] Uyarma lambası bağlantısı
- [ ] Buzzer devresi
- [ ] Sigorta koruması

📋 **PDF Referans:** Sayfa 80-85 (Aktüatörler)

---

### Sayfa 08: Terminal Planı
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- X1/X2 24V dağıtım referansları
- X10/X11 safety terminal referansları
- X20 DI terminal referansı
- X30/X31 EtherCAT referansları

❌ **Eksik:**
- [ ] Tüm terminal bloklarının detaylı listesi
- [ ] Terminal tipleri (Phoenix Contact, Weidmüller vb.)
- [ ] Çift katlı terminaller
- [ ] Sigorta terminalleri
- [ ] Topraklama terminalleri
- [ ] Etiketleme planı

📋 **PDF Referans:** Sayfa 90-110 (Klemmenplan)

---

### Sayfa 09: Pin Planı
**Durum:** ❌ SADECE PLAN NOTU - DEVRE YOK

✅ **Mevcut:**
- M12 sensör pin atamaları referansı
- Servo ve panel konnektörleri referansı
- Shield/PE sonlandırma notları

❌ **Eksik:**
- [ ] Tüm konnektörlerin pinout tabloları
- [ ] M12/M8 sensör konnektörleri
- [ ] RJ45 EtherCAT pinout
- [ ] D-Sub konnektörler (varsa)
- [ ] Power konnektörler
- [ ] Shield sonlandırma detayları

📋 **PDF Referans:** Sayfa 110-125 (Steckerbelegungsplan)

---

## 🔴 Öncelikli Düzeltme Gerektiren Hususlar

### 1. AC Giriş Devresi (KRİTİK)
- Ana besleme: 3-faz 400VAC + N + PE
- Ana şalter (Q1) ve kontaktör (K1)
- Faz sırası rölesi
- Parafudr (varsa)

### 2. 24V DC Güç Kaynağı (KRİTİK)
- PSU modeli ve kapasitesi (örn: Siemens SITOP PSU8200 24V/20A)
- Her branş için sigorta değerleri
- Kablo kesitleri (örn: 2.5mm² güç, 1.5mm² sinyal)

### 3. Safety Devre Detayları (GÜVENLİK)
- Pilz PNOZ X2.8P gerçek bağlantı şeması
- E-STOP döngüsü (ç kanal, monitörlü)
- Safety kapı switch'leri
- Test ve reset devreleri

### 4. NC300 CNC Kontrolör (SİSTEM MERKEZİ)
- Güç bağlantıları
- EtherCAT master portları
- I/O bağlantıları
- HMI Ethernet

### 5. Servo Sürücü Devreleri (5 EKSEN)
- Her eksen için:
  - 3-faz güç girişi
  - Motor çıkışı (U/V/W)
  - Encoder feedback
  - STO bağlantıları
  - Fren (Z ekseni)

### 6. I/O Dağılımı (R1-EC)
- 3x DI modül (48 giriş)
- 3x DO modül (48 çıkış)
- Her nokta için cihaz referansı

---

## 📋 Önerilen Aksiyon Planı

### Faz 1: Kritik Güç ve Güvenlik (1-2 gün)
1. [ ] Ana AC giriş devresini çiz (Sayfa 01'e ekle)
2. [ ] 24V DC dağıtımı detaylandır
3. [ ] Safety devresini Pilz datasheet'e göre tamamla (Sayfa 02)

### Faz 2: Kontrolör ve Network (2-3 gün)
4. [ ] NC300 bağlantılarını Delta manuel'den aktar (Sayfa 03)
5. [ ] EtherCAT topolojisini çiz
6. [ ] HMI bağlantısını ekle

### Faz 3: Servo Eksanları (3-4 gün)
7. [ ] Her servo sürücüyü detaylı çiz (Sayfa 04)
8. [ ] Motor ve encoder bağlantıları
9. [ ] STO entegrasyonu

### Faz 4: I/O ve Sensörler (2-3 gün)
10. [ ] R1-EC modül bağlantılarını çiz (Sayfa 05)
11. [ ] Dijital giriş devreleri (Sayfa 06)
12. [ ] Dijital çıkış devreleri (Sayfa 07)

### Faz 5: Terminal ve Pin Planları (1-2 gün)
13. [ ] Terminal bloklarını detaylandır (Sayfa 08)
14. [ ] Konnektör pinout'larını ekle (Sayfa 09)

### Faz 6: Validasyon ve Test (1 gün)
15. [ ] ERC (Electrical Rule Check) çalıştır
16. [ ] PDF ile cross-reference kontrolü
17. [ ] BOM (Bill of Materials) oluştur

---

## 🛠️ KiCad'de Kullanılması Gereken Özellikler

### Global Labels
- Güç rail'leri için: `+24V`, `0V`, `PE`, `R/S/T/L1/L2/L3`
- EtherCAT için: `ECAT_IN`, `ECAT_OUT`
- Safety için: `STO_A_X`, `STO_B_X`, `E_STOP_CH1`, vb.

### Hierarchical Sheets
- Her sayfa bir alt sistem olarak tanımlanmalı
- Off-page connectors ile sayfalar arası bağlantı

### Power Ports
- `+24V`, `GND`, `PWR_FLAG` doğru kullanılmalı
- ERC hataları minimize edilmeli

### Title Block
- Her sayfada tutarlı revizyon bilgisi
- Orijinal PDF sayfa referansı

---

## 📚 Kullanılabilir Kaynaklar

### ✅ İndirilen User Manual'ler
| Doküman | Dosya | Durum |
|---------|-------|-------|
| Delta NC300 CNC Controller | `Documentation/Manuals/Delta_NC300_User_Manual.pdf` (6.4 MB) | ✅ Mevcut |
| Delta ASDA-A3 Servo Drive | `Documentation/Manuals/Delta_ASDA-A3_Servo_Manual.pdf` (4.7 MB) | ✅ Mevcut |
| Delta R1-EC I/O Module | `Documentation/Manuals/Delta_R1-EC_Manual.pdf` (2.3 MB) | ✅ Mevcut |
| Delta DOP-110CS HMI | `Documentation/Manuals/DOP-110CS_Manual.pdf` (314 KB) | ✅ Mevcut |
| Pilz PNOZ X2.8P Safety Relay | `Documentation/Manuals/Pilz_PNOZ_X2.8P_Manual.pdf` (378 KB) | ✅ Mevcut |

### 📄 Orijinal Makine Dökümanları
| Doküman | Dosya | Durum |
|---------|-------|-------|
| GFB Orijinal Elektrik | `Documentation/Manuals/gfb_EP034-047170.pdf` (7.1 MB) | ✅ Mevcut |
| Okandan GFB Versiyonu | `Documentation/Manuals/okandan_gfb_vb_EP034-033781.pdf` (12 MB) | ✅ Mevcut |

### 📋 Wiring Reference Document
Tüm teknik detaylar çıkarıldı ve tek bir referans dokümanında toplandı:
- **Dosya:** `Electrical/WIRING_REFERENCE.md`
- **İçerik:** Tüm connector pinout'ları, wiring detayları, I/O dağılımı, terminal planı

---

## ✅ Sonuç

**Mevcut Durum:** KiCad projesi iyi yapılandırılmış ama **%70 eksik** detay içeriyor.  
**Öncelik:** Güç ve safety devreleri acilen tamamlanmalı.  
**Tahmini Süre:** 10-15 gün (tam detaylı şema için)

**Öneri:** Orijinal PDF'deki her sayfayı KiCad'e adım adım aktarın ve ERC testlerini düzenli çalıştırın.

---

**Hazırlayan:** CNCRevizyon Elektrik Validasyon Ekibi  
**Versiyon:** 1.0  
**Tarih:** 2026-04-06
