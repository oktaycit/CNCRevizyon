# GFB60-30RE-S Pano Yerlesim Plani

**Proje:** LiSEC GFB-60/30RE CNC Revizyon
**Belge No:** ELEC-PNL-001
**Revizyon:** 4.2
**Tarih:** 2026-04-12
**Cizim Olcegi:** 1:10

---

## 1. Pano Boyutlari

| Parametre | Deger | Notlar |
|-----------|-------|--------|
| Pano Tipi | IP65 Endustriyel | Metal, tozsuz ortam icin |
| Genislik | 1200 mm | Standard 19" rack uyumlu |
| Yukseklik | 2000 mm | Ayakli montaj |
| Derinlik | 600 mm | Kapakli, on/acilir |
| Montaj Plakasi | 1000 x 1800 mm | Celik, topraklanmis |
| DIN Ray Kapasitesi | 6700 mm | 35mm tipi, toplam |

**Not:** `U2 / DOP-110CS` operator terminali ana pano icinde veya pano kapaginda degildir. Uzak operatör terminali olarak, koprunun home noktalarina yakin saha tasiyici/ayak uzerine monte edilecektir.

---

## 2. Montaj Plakasi Yerlesimi (On Gorunus)

```
+============================================================================+
|                       MONTAJ PLAKASI - 1000 x 1800 mm                        |
|                                                                            |
|   +---+  +------------------+  +------------------+  +---+                  |
|   |PE |  |    F0 PARAFUDR   |  |    EMC1 FILTRE   |  |X1 |   <-- UST SEVIYE |
|   |   |  |    VAL-MS 400    |  |    EMI-F400V     |  |AC |       1900 mm   |
|   +---+  +------------------+  +------------------+  +---+                  |
|                                                                            |
|   +------------------------------------------------------------------+     |
|   |                        DIN RAY 1 (1750 mm)                       |     |
|   +------------------------------------------------------------------+     |
|   | Q1  | K1  | PS1 | F2  | F3  | F4  | F5  | F6  | X2  | X10 | X11 |     |
|   | ANA | ANA | 24V | NC  | R1  | SNS | SAF | HMI | 24V | SAF | STO |     |
|   | SWT | KNT | DC  | 300 | -EC |     |     |     | DIS | IN  | OUT |     |
|   +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+     |
|                                                                            |
|   +------------------------------------------------------------------+     |
|   |                        DIN RAY 2 (1700 mm)                       |     |
|   +------------------------------------------------------------------+     |
|   | U41  | U42  | U43  | U44  | U45  | U50  | U51  | U52  | U53  |         |
|   | X    | Y    | ALT  | Z    | CNC  | R1   | DI   | DI   | DO   |         |
|   | SERVO| SERVO| SERVO| SERVO| SERVO| EC01 | MOD1 | MOD2 | MOD  |         |
|   | 4.5kW| 2.0kW| 2.0kW| 1.0kW| 1.5kW| COUP | 32DI | 32DI | 32DO |         |
|   +------+------|------+------|------+------+------+------+------+         |
|                                                                            |
|   +------------------------------------------------------------------+     |
|   |                        DIN RAY 3 (1650 mm)                       |     |
|   +------------------------------------------------------------------+     |
|   | X20 (DI-1) | X30 (DI-2) | X40 (DO) | K10      | FK1       |           |
|   | 16-pin x2  | 16-pin x2  | 16-pin x2| PILZ     | FAZ KONT  |           |
|   | TERMINAL   | TERMINAL   | TERMINAL | PNOZ X2.8|           |           |
|   +------------------------------------------------------------------+     |
|                                                                            |
|   +------------------------------------------------------------------+     |
|   |                        DIN RAY 4 (1600 mm)                       |     |
|   +------------------------------------------------------------------+     |
|   |   X12 (AUX)    |   S2 (RESET)   |   S0 E-STOP   |   X1 AC IN    |     |
|   |   5-pin AUX    |   NO + LED      |   PANEL MT    |   5-pin AC    |     |
|   +------------------------------------------------------------------+     |
|                                                                            |
+============================================================================+
```

---

## 3. Bilesen Konum Tablosu

| Ref | Bilesen | Konum (X, Y) | Boyutlar (WxHxD) | DIN Ray | Notlar |
|-----|---------|--------------|------------------|---------|--------|
| **GUC DAGITIM** |
| X1 | AC Giris Terminali | (50, 1900) | 50x80x60 | - | Besleme giris |
| F0 | Parafudr VAL-MS 400 | (150, 1900) | 90x90x70 | - | Montaj plakasi |
| EMC1 | EMC Filtre EMI-F400V | (300, 1900) | 120x100x80 | - | Montaj plakasi |
| Q1 | Ana Salter T5S 320 | (50, 1750) | 80x120x70 | DIN-1 | 32A MCB |
| K1 | Kontaktor LC1D32A3 | (150, 1750) | 60x120x80 | DIN-1 | 32A 3P |
| PS1 | Power Supply 24V/20A | (220, 1750) | 100x150x120 | DIN-1 | 480W |
| F2 | Sigorta 4A NC300 | (330, 1750) | 18x80x70 | DIN-1 | Fuse holder |
| F3 | Sigorta 5A R1-EC | (360, 1750) | 18x80x70 | DIN-1 | Fuse holder |
| F4 | Sigorta 3A Sensor | (390, 1750) | 18x80x70 | DIN-1 | Fuse holder |
| F5 | Sigorta 2A Safety | (420, 1750) | 18x80x70 | DIN-1 | Fuse holder |
| F6 | Sigorta 2A HMI | (450, 1750) | 18x80x70 | DIN-1 | Fuse holder |
| **SERVO SURUCULER** |
| U41 | ASD-A3-4523-E (X) | (50, 1500) | 85x280x200 | DIN-2 | 4.5kW |
| U42 | ASD-A3-2023-E (Y) | (150, 1500) | 65x280x180 | DIN-2 | 2.0kW |
| U43 | ASD-A3-2023-E (Alt) | (230, 1500) | 65x280x180 | DIN-2 | 2.0kW |
| U44 | ASD-A3-1023-E (Z) | (310, 1500) | 50x280x160 | DIN-2 | 1.0kW |
| U45 | ASD-A3-1523-E (CNC) | (370, 1500) | 50x280x160 | DIN-2 | 1.5kW |
| **I/O SISTEMI** |
| U50 | R1-EC01 Coupler | (500, 1500) | 50x100x75 | DIN-2 | EtherCAT |
| U51 | R1-EC0902D DI #1 | (560, 1500) | 50x100x75 | DIN-2 | 32 DI |
| U52 | R1-EC0902D DI #2 | (620, 1500) | 50x100x75 | DIN-2 | 32 DI |
| U53 | R1-EC0902O DO | (680, 1500) | 50x100x75 | DIN-2 | 32 DO |
| **TERMINALLER** |
| X2 | 24VDC Dagitim | (480, 1750) | 80x60x45 | DIN-1 | 8-pin |
| X10 | Safety Input | (580, 1750) | 60x60x45 | DIN-1 | 6-pin |
| X11 | STO Output | (660, 1750) | 100x60x45 | DIN-1 | 10-pin |
| X20 | DI Terminal #1 | (50, 1250) | 160x60x45 | DIN-3 | 32-pin |
| X30 | DI Terminal #2 | (220, 1250) | 160x60x45 | DIN-3 | 32-pin |
| X40 | DO Terminal | (390, 1250) | 160x60x45 | DIN-3 | 32-pin |
| **SAFETY** |
| K10 | PILZ PNOZ X2.8P | (550, 1250) | 45x100x120 | DIN-3 | Safety relay |
| FK1 | Faz Kontrol | (620, 1250) | 35x90x100 | DIN-3 | Phase monitor |
| **DIGER** |
| X12 | AUX Terminal | (50, 1100) | 50x60x45 | DIN-4 | 5-pin |
| S2 | Reset Buton | (120, 1100) | 22mm | Panel | Yesil LED |
| S0 | E-STOP Panel | (200, 1100) | 40mm | Panel | Mantar kirmizi |
| PE1 | PE Bara | (900, 1750) | 200x30x25 | - | Topraklama |

### Saha Montajli Bilesen

| Ref | Bilesen | Konum | Boyutlar | Montaj | Notlar |
|-----|---------|-------|----------|--------|--------|
| U2 | DOP-110CS Operator Terminali | Kopru home noktalarina yakin saha pozisyonu | 10.1" HMI | Uzak konsol / ayak | Ana panoya Ethernet + 24VDC ile baglanacak |

---

## 4. Kablo Kanallari

### Ust Kablo Kanali (WT1)
- **Konum:** Ust kenar, Y = 1850 mm
- **Tip:** NSYVDCA60X40 (60x40mm)
- **Uzunluk:** 1100 mm
- **Icerik:** AC guc kablolari, motor kablolari

### Orta Kablo Kanali (WT1)
- **Konum:** DIN Ray 1 ve 2 arasi, Y = 1600 mm
- **Tip:** NSYVDCA60X40 (60x40mm)
- **Uzunluk:** 1100 mm
- **Icerik:** 24VDC dagitim, EtherCAT, signal

### Alt Kablo Kanali (WT2)
- **Konum:** DIN Ray 3 ve 4 arasi, Y = 1350 mm
- **Tip:** NSYVDCA40X40 (40x40mm)
- **Uzunluk:** 1000 mm
- **Icerik:** Sensor, I/O signal kablolari

### Sag Kablo Kanali (WT2)
- **Konum:** Sag kenar, X = 1150 mm
- **Tip:** NSYVDCA40X40 (40x40mm)
- **Uzunluk:** 1800 mm (dikey)
- **Icerik:** Saha kablo cikislari

---

## 5. Kablo Giris Bolgeleri

### Ana Giris (Alt Sol)
- **Konum:** X = 100-200 mm, Y = 100-300 mm
- **Gland Plaka:** 200x150 mm
- **Kablo Adedi:** 5 adet (3F AC, PE, N)
- **Gland Tipi:** PG21, PG16
- **Kabollar:**
  - 4G10 mm2 (Ana guc)
  - PE 10 mm2 (Toprak)

### Saha Kablolari (Alt Sag)
- **Konum:** X = 800-1100 mm, Y = 100-500 mm
- **Gland Plaka:** 300x400 mm
- **Kablo Adedi:** 30 adet
- **Gland Tipi:** PG11 (sensor), PG16 (motor), PG21 (guc)
- **Kabollar:**
  - Motor guc (5 adet)
  - Encoder (5 adet)
  - Sensor (15 adet)
  - Diger (5 adet)

---

## 6. Havalandirma ve Ortam

| Parametre | Deger | Notlar |
|-----------|-------|--------|
| Ortam Sicakligi | -10C ~ +50C | Isletme |
| Depolama Sicakligi | -20C ~ +60C | |
| Nem | 5-95% RH | Kondenzasyonsuz |
| Koruma Sinifi | IP65 | Pano govdesi |
| Fan | 1x 120mm | Pano ustu, asiri isida calisir |
| Filtre | 1x 120mm | Fan onunde, degistirilebilir |

### Fan Kontrolu
- **Kaynak:** U53 DO_3 (Cooling Fan)
- **Sart:** Pano sicakligi > 40C (termostat ile)
- **Fan Model:** Ebm-Papst 4600N veya esdeger

---

## 7. Etiketleme Kurallari

### Bilesen Etiketleri
- **Format:** Ref + Aciklama (orn: "U41 - X SERVO")
- **Renk:** Beyaz uzerine siyah
- **Boyut:** 30x10 mm (kucuk), 50x15 mm (buyuk)
- **Malzeme:** Polyester, yapiskanli

### Terminal Etiketleri
- **Format:** Terminal no + Sinyal (orn: "X2.1 - +24V")
- **Renk:** Kirmizi (+24V), Mavi (0V), Sari (Safety), Gri (Diger)
- **Malzeme:** Phoenix Contact ZB serisi

### Kablo Etiketleri
- **Format:** Wire ID (orn: "W101")
- **Yer:** Her iki uc, kablo glandina yakin
- **Malzeme:** HellermannTyton etiket

---

## 8. Onemli Notlar

### Montaj Sirasi
1. DIN raylari monte et (4 ray)
2. Kablo kanallarini monte et
3. Buyuk bilesenleri monte et (PS1, Servo suruculer)
4. Kucuk bilesenleri monte et (sigortalar, terminaller)
5. PE barayi monte et
6. Kablo gland plakalarini hazirla

### Guvenlik Uyarilari
- **Yuksek Gerilim:** AC 400V bogulmadan once gucu kesin
- **STO Baglantisi:** Safety kablolarini SARI renk ile isaretleyin
- **Topraklama:** Tum metal kofreler ve bilesenler PE baraya baglanmali
- **HMI Montaji:** Ana pano kapaginda HMI kesiti acilmayacak; uzak operator terminali saha montaj detayina gore uygulanacak

### Test Noktalari
- **Hipot Test:** 2.5kV AC, 1 dakika (guc devreleri)
- **Izolasyon:** Min 1 MOhm (500V DC)
- **Devamlilik:** PE baglantilari < 0.1 Ohm

---

## 9. Revizyon Gecmisi

| Rev | Tarih | Aciklama | Hazirlayan |
|-----|-------|----------|------------|
| 4.0 | 2026-04-05 | Ilk yayin | CNCRevizyon |
| 4.1 | 2026-04-11 | Pano yerlesim guncellemesi | CNCRevizyon |

---

**Belge Durumu:** FINAL
**Onaylayan:** ___________________
**Tarih:** ___________________
