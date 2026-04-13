# GFB60-30RE-S Kablo Listesi ve Uzunluk Tahminleri

**Proje:** LiSEC GFB-60/30RE CNC Revizyon
**Belge No:** ELEC-CBL-001
**Revizyon:** 4.2
**Tarih:** 2026-04-12

---

## 1. Pano Ici Kablolar (Internal Wiring)

Bu kablolar pano icinde bilesenler arasi baglantilar icindir. Uzunluklar pano yerlesim planina gore hesaplanmistir.

### 1.1 Ana Guc Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Pano Ici (m) | Notlar |
|---------|------|-----|--------|------------|--------------|--------|
| W001-A | X1.1 L1 | Q1 L1 | L1 | 10mm2 rigid | 0.5 | Busbar |
| W001-B | X1.2 L2 | Q1 L2 | L2 | 10mm2 rigid | 0.5 | Busbar |
| W001-C | X1.3 L3 | Q1 L3 | L3 | 10mm2 rigid | 0.5 | Busbar |
| W001-D | X1.4 N | Q1 N | N | 10mm2 rigid | 0.5 | Busbar |
| W001-E | X1.5 PE | PE Bara.1 | PE | 10mm2 GNYE | 0.8 | Ground |
| W002-A | Q1 Out L1 | K1 L1 | L1 | 10mm2 rigid | 0.3 | MCB -> Kontaktor |
| W002-B | Q1 Out L2 | K1 L2 | L2 | 10mm2 rigid | 0.3 | |
| W002-C | Q1 Out L3 | K1 L3 | L3 | 10mm2 rigid | 0.3 | |
| W003-A | K1 Out L1 | U41 P1 R | AC X | 6mm2 flex | 0.5 | X servo |
| W003-B | K1 Out L2 | U41 P1 S | AC X | 6mm2 flex | 0.5 | |
| W003-C | K1 Out L3 | U41 P1 T | AC X | 6mm2 flex | 0.5 | |
| W003-D | K1 Out L1 | U42 P1 R | AC Y | 4mm2 flex | 0.5 | Y servo |
| W003-E | K1 Out L2 | U42 P1 S | AC Y | 4mm2 flex | 0.5 | |
| W003-F | K1 Out L3 | U42 P1 T | AC Y | 4mm2 flex | 0.5 | |
| W003-G | K1 Out L1 | U43 P1 R | AC Alt | 4mm2 flex | 0.5 | Alt servo |
| W003-H | K1 Out L2 | U43 P1 S | AC Alt | 4mm2 flex | 0.5 | |
| W003-I | K1 Out L3 | U43 P1 T | AC Alt | 4mm2 flex | 0.5 | |
| W003-J | K1 Out L1 | U44 P1 R | AC Z | 2.5mm2 flex | 0.5 | Z servo 1F |
| W003-K | K1 Out L2 | U44 P1 S | AC Z | 2.5mm2 flex | 0.5 | |
| W003-L | K1 Out L1 | U45 P1 R | AC CNC | 2.5mm2 flex | 0.5 | CNC servo |
| W003-M | K1 Out L2 | U45 P1 S | AC CNC | 2.5mm2 flex | 0.5 | |

**Pano Ici Guc Kablo Toplami:** ~8.0 m

### 1.2 24VDC Besleme Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Pano Ici (m) | Notlar |
|---------|------|-----|--------|------------|--------------|--------|
| W004 | F2 OUT | X2.1 | +24V NC | 2.5mm2 RED | 0.4 | NC300 fuse cikisi |
| W006 | 0V BUS | X2.2 | 0V COM | 2.5mm2 BLU | 0.4 | Ortak 0V dagitimi |
| W005 | X2.1 | U1 NC300 +24V | +24V NC | 2.5mm2 RED | 0.3 | NC300 besleme |
| W006A | X2.2 | U1 NC300 0V | 0V NC | 2.5mm2 BLU | 0.3 | |
| W008 | F6 OUT | X2.3 | +24V HMI | 1.5mm2 RED | 0.3 | HMI saha beslemesi icin panel cikisi |
| W006B | 0V BUS | X2.4 | 0V HMI | 1.5mm2 BLU | 0.3 | HMI saha 0V panel cikisi |
| W011 | F3 OUT | X2.5 | +24V R1 | 1.5mm2 RED | 0.3 | I/O fuse cikisi |
| W012 | X2.6 | U50 R1-EC GND | 0V R1 | 1.5mm2 BLU | 0.4 | |
| W016 | F4 OUT | X2.7 | +24V AUX/SNS | 1.5mm2 RED | 0.3 | Sensor/Aux dagitimi |
| W017 | X2.8 | X12.2 | 0V AUX | 1.5mm2 BLU | 0.4 | Aux ortak 0V |
| W013 | PE Bara.2 | PS1 FG | PE | 2.5mm2 GNYE | 0.3 | |
| W015 | PE Bara.5 | U50 R1-EC PE | PE | 2.5mm2 GNYE | 0.4 | |

**Pano Ici DC Kablo Toplami:** ~4.1 m

### 1.3 Safety Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Pano Ici (m) | Notlar |
|---------|------|-----|--------|------------|--------------|--------|
| W201 | PS1 +24V | K10 A1 | +24V SAF | 1.5mm2 YEL | 0.4 | Safety besleme |
| W202 | PS1 0V | K10 A2 | 0V SAF | 1.5mm2 YEL | 0.4 | |
| W206 | X11.1 | U41 CN1-29 | X STO1 | 0.75mm2 YEL | 0.3 | STO X |
| W206B | X11.2 | U41 CN1-30 | X STO2 | 0.75mm2 YEL | 0.3 | |
| W207 | X11.3 | U42 CN1-29 | Y STO1 | 0.75mm2 YEL | 0.3 | STO Y |
| W207B | X11.4 | U42 CN1-30 | Y STO2 | 0.75mm2 YEL | 0.3 | |
| W208 | X11.5 | U43 CN1-29 | Alt STO1 | 0.75mm2 YEL | 0.4 | STO Alt |
| W208B | X11.6 | U43 CN1-30 | Alt STO2 | 0.75mm2 YEL | 0.4 | |
| W209 | X11.7 | U44 CN1-29 | Z STO1 | 0.75mm2 YEL | 0.5 | STO Z |
| W209B | X11.8 | U44 CN1-30 | Z STO2 | 0.75mm2 YEL | 0.5 | |
| W210 | X11.9 | U45 CN1-29 | CNC STO1 | 0.75mm2 YEL | 0.6 | STO CNC |
| W210B | X11.10 | U45 CN1-30 | CNC STO2 | 0.75mm2 YEL | 0.6 | |
| W211 | 0V Common | All CN1-43 | STO COM | 0.75mm2 BLU | 2.0 | Daisy chain |

**Pano Ici Safety Kablo Toplami:** ~6.0 m

### 1.4 EtherCAT Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Pano Ici (m) | Notlar |
|---------|------|-----|--------|------------|--------------|--------|
| W301 | U1 NC300 CN1 | U41 CN3 | EtherCAT | CAT6 STP | 0.5 | Master -> X |
| W302 | U41 CN6 | U42 CN3 | EtherCAT | CAT6 STP | 0.3 | X -> Y |
| W303 | U42 CN6 | U43 CN3 | EtherCAT | CAT6 STP | 0.3 | Y -> Alt |
| W304 | U43 CN6 | U44 CN3 | EtherCAT | CAT6 STP | 0.4 | Alt -> Z |
| W305 | U44 CN6 | U45 CN3 | EtherCAT | CAT6 STP | 0.3 | Z -> CNC |
| W306 | U45 CN6 | U50 IN | EtherCAT | CAT6 STP | 0.4 | CNC -> R1-EC |
| W307 | U50 OUT | U1 NC300 CN2 | EtherCAT | CAT6 STP | 0.5 | Return loop |

**Pano Ici EtherCAT Kablo Toplami:** ~2.7 m

### 1.5 I/O Signal Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Pano Ici (m) | Notlar |
|---------|------|-----|--------|------------|--------------|--------|
| W413 | K10 Aux | X20.13 | E-STOP FB1 | 0.75mm2 | 0.3 | Safety FB |
| W414 | K10 Aux | X20.14 | E-STOP FB2 | 0.75mm2 | 0.3 | |
| W415 | S1 Aux | X20.15 | DOOR_OPEN | 0.75mm2 | 0.3 | Door status |
| W451 | U53 DO_0 | X40.1 | SERVO_EN | 0.75mm2 | 0.5 | Enable relay |
| W452 | U53 DO_1 | X40.2 | VACUUM | 0.75mm2 | 0.3 | Vacuum pump |
| W453 | U53 DO_2 | X40.3 | OIL | 0.75mm2 | 0.3 | Oil pump |
| W454 | U53 DO_3 | X40.4 | FAN | 0.75mm2 | 0.3 | Cooling fan |
| W455 | U53 DO_4 | X40.5 | WARN | 0.75mm2 | 0.3 | Warning light |
| W456 | U53 DO_5 | X40.6 | BUZZER | 0.75mm2 | 0.3 | Buzzer |
| W457 | U53 DO_7 | X40.8 | BRK_EN | 0.75mm2 | 0.3 | Breaker |
| W458 | U53 DO_10 | X40.11 | CNV_F | 0.75mm2 | 0.3 | Conveyor fwd |
| W459 | U53 DO_11 | X40.12 | CNV_R | 0.75mm2 | 0.3 | Conveyor rev |

**Pano Ici I/O Kablo Toplami:** ~4.0 m

---

## 2. Saha Kablolari (Field Wiring)

Bu kablolar pano ile saha bilesenleri (motorlar, sensorler) arasindadir.

### 2.1 Servo Motor Guc Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Saha (m) | Notlar |
|---------|------|-----|--------|------------|----------|--------|
| W102 | U41 P2 U/V/W/FG | M41 X Motor | Power | DELTACAB-PWR-4G4 shielded | 15 | X ekseni motor |
| W104 | U42 P2 U/V/W/FG | M42 Y Motor | Power | DELTACAB-PWR-4G2.5 shielded | 12 | Y ekseni motor |
| W106 | U43 P2 U/V/W/FG | M43 Alt Motor | Power | DELTACAB-PWR-4G2.5 shielded | 10 | Alt ekseni motor |
| W108 | U44 P2 U/V/W/FG | M44 Z Motor | Power | DELTACAB-PWR-4G1.5 shielded | 8 | Z ekseni motor |
| W110 | U45 P2 U/V/W/FG | M45 CNC Motor | Power | DELTACAB-PWR-4G1.5 shielded | 8 | CNC motor |

**Motor Guc Kablo Toplami:** 53 m (extra 3m per cable for service loop)

### 2.2 Encoder Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Saha (m) | Notlar |
|---------|------|-----|--------|------------|----------|--------|
| W102-ENC | M41 Encoder | U41 CN2 | Encoder X | DELTACAB-ENC-6x0.14 | 15 | X encoder |
| W104-ENC | M42 Encoder | U42 CN2 | Encoder Y | DELTACAB-ENC-6x0.14 | 12 | Y encoder |
| W106-ENC | M43 Encoder | U43 CN2 | Encoder Alt | DELTACAB-ENC-6x0.14 | 10 | Alt encoder |
| W108-ENC | M44 Encoder | U44 CN2 | Encoder Z | DELTACAB-ENC-6x0.14 | 8 | Z encoder |
| W110-ENC | M45 Encoder | U45 CN2 | Encoder CNC | DELTACAB-ENC-6x0.14 | 8 | CNC encoder |

**Encoder Kablo Toplami:** 53 m

### 2.3 Z Fren Kablo

| Wire ID | From | To | Signal | Kablo Tipi | Saha (m) | Notlar |
|---------|------|-----|--------|------------|----------|--------|
| W111 | +24VDC | Z Brake + | Brake + | 2x0.75mm2 | 8 | Z fren besleme |
| W112 | U44 CN1 DO_5 | Z Brake - | Brake ctrl | 2x0.75mm2 | 8 | Z fren kontrol |

**Fren Kablo Toplami:** 16 m

### 2.4 Sensor Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Saha (m) | Notlar |
|---------|------|-----|--------|------------|----------|--------|
| W401 | S11 X+ Limit | X20.1 | X+ LIMIT | UNITRONIC Li2YCY 4x0.34 | 18 | X+ limit sensor |
| W402 | S12 X- Limit | X20.2 | X- LIMIT | UNITRONIC Li2YCY 4x0.34 | 18 | X- limit sensor |
| W403 | S10 X Home | X20.3 | X HOME | UNITRONIC Li2YCY 4x0.34 | 18 | X home sensor |
| W404 | S21 Y+ Limit | X20.4 | Y+ LIMIT | UNITRONIC Li2YCY 4x0.34 | 14 | Y+ limit sensor |
| W405 | S22 Y- Limit | X20.5 | Y- LIMIT | UNITRONIC Li2YCY 4x0.34 | 14 | Y- limit sensor |
| W406 | S20 Y Home | X20.6 | Y HOME | UNITRONIC Li2YCY 4x0.34 | 14 | Y home sensor |
| W407 | S31 Z+ Limit | X20.7 | Z+ LIMIT | UNITRONIC Li2YCY 4x0.34 | 10 | Z+ limit sensor |
| W408 | Z- Sensor | X20.8 | Z- LIMIT | UNITRONIC Li2YCY 4x0.34 | 10 | Z- limit sensor |
| W409 | S30 Z Home | X20.9 | Z HOME | UNITRONIC Li2YCY 4x0.34 | 10 | Z home sensor |
| W410 | S41 Alt+ Limit | X20.10 | ALT+ LIMIT | UNITRONIC Li2YCY 4x0.34 | 12 | Alt+ limit |
| W411 | S42 Alt- Limit | X20.11 | ALT- LIMIT | UNITRONIC Li2YCY 4x0.34 | 12 | Alt- limit |
| W412 | S40 Alt Home | X20.12 | ALT HOME | UNITRONIC Li2YCY 4x0.34 | 12 | Alt home |
| W416 | S51 Vacuum FB | X20.16 | VACUUM OK | UNITRONIC Li2YCY 4x0.34 | 6 | Vacuum sensor |
| W417 | S50 Glass Det #1 | X20.17 | GLASS_DET1 | UNITRONIC Li2YCY 4x0.34 | 8 | Glass detect |
| W417A | S50 Glass Det #2 | X20.18 | GLASS_DET2 | UNITRONIC Li2YCY 4x0.34 | 8 | Glass detect |

**Sensor Kablo Toplami:** 174 m

### 2.5 Safety Saha Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Saha (m) | Notlar |
|---------|------|-----|--------|------------|----------|--------|
| W203 | K10 S11/S12 | S0 E-STOP Panel | E-STOP CH1/2 | 2x2x0.75 shielded | 5 | Panel E-STOP |
| W204 | K10 | S1 Door Switch | DOOR SW | 2x2x0.75 shielded | 6 | Door safety |
| W205 | K10 S52 | S2 Reset Button | RESET | 2x0.75 | 5 | Reset button |

**Safety Saha Kablo Toplami:** 16 m

### 2.6 Uzak HMI Kablolari

| Wire ID | From | To | Signal | Kablo Tipi | Saha (m) | Notlar |
|---------|------|-----|--------|------------|----------|--------|
| W008A | X2.3 | U2 DOP +V | +24V HMI | 2x1.5mm2 | 12 | Uzak operator terminali beslemesi |
| W009 | X2.4 | U2 DOP -V | 0V HMI | 2x1.5mm2 | 12 | Uzak operator terminali 0V |
| W014 | PE Bara.4 | U2 DOP FG | PE | 1x2.5mm2 GNYE | 12 | HMI saha PE baglantisi |
| W308 | U1 NC300 CN3 | U2 DOP ETH | Ethernet | CAT6 UTP | 12 | Kopru home noktalarina yakin HMI |

**Uzak HMI Kablo Toplami:** 48 m

---

## 3. Kablo Tipi Ozet Tablosu

| Kablo Tipi | Kod | Cap | Uygulama | Adet | Toplam (m) |
|------------|-----|-----|----------|------|------------|
| **PANO ICI** |
| 10mm2 rigid | CU10 | 10mm2 | AC busbar | 5 | 2.5 |
| 6mm2 flex | CU6-F | 6mm2 | Servo AC | 3 | 1.5 |
| 4mm2 flex | CU4-F | 4mm2 | Servo AC | 6 | 3.0 |
| 2.5mm2 flex | CU2.5-F | 2.5mm2 | Servo AC | 4 | 2.0 |
| 2.5mm2 DC | CU2.5-DC | 2.5mm2 | 24VDC | 11 | 4.0 |
| 1.5mm2 DC | CU1.5-DC | 1.5mm2 | 24VDC | 4 | 2.0 |
| 0.75mm2 signal | CU0.75 | 0.75mm2 | Safety/IO | 20 | 10.0 |
| CAT6 STP | CAT6-STP | - | EtherCAT | 8 | 3.2 |
| **SAHA KABLARI** |
| DELTACAB-PWR-4G4 | MOT-P4 | 4x4mm2 | X motor | 1 | 15 |
| DELTACAB-PWR-4G2.5 | MOT-P2.5 | 4x2.5mm2 | Y/Alt motor | 2 | 22 |
| DELTACAB-PWR-4G1.5 | MOT-P1.5 | 4x1.5mm2 | Z/CNC motor | 2 | 16 |
| DELTACAB-ENC-6x0.14 | ENC-6 | 6x0.14mm2 | Encoder | 5 | 53 |
| UNITRONIC Li2YCY 4x0.34 | SNS-4 | 4x0.34mm2 | Sensor | 15 | 174 |
| 2x0.75 flex | BRK | 2x0.75 | Brake | 2 | 16 |
| 2x2x0.75 shielded | SAF-2x2 | 2x2x0.75 | Safety | 2 | 11 |

---

## 4. Kablo Alim Listesi (Tedbirce)

| Kablo Tipi | Uretici | Part No | Toplam (m) | Tavsiye Edilen | Birim |
|------------|---------|---------|-------------|----------------|-------|
| **PANO ICI** (hepsi rigid veya semi-rigid) |
| H05V-K 10mm2 (RED/BLU/YEL/GNYE) | Lapp | - | 8 | 10 m | Set |
| H05V-K 6mm2 (BLK) | Lapp | - | 2 | 3 m | rol |
| H05V-K 4mm2 (BLK) | Lapp | - | 4 | 5 m | rol |
| H05V-K 2.5mm2 (RED/BLU/YEL) | Lapp | - | 10 | 12 m | Set |
| H05V-K 1.5mm2 (RED/BLU) | Lapp | - | 5 | 6 m | rol |
| H05V-K 0.75mm2 (RED/BLU/YEL) | Lapp | - | 15 | 20 m | rol |
| **ETHERCAT** |
| CAT6 SF/UTP Patch Cable 0.5m | Belden | 10GXS12-0.5M | 8 | 10 adet | pcs |
| CAT6 SF/UTP Bulk Cable | Belden | 10GXS12 | 5 | 10 m | rol |
| **SAHA KABLARI** |
| DELTACAB-PWR-4G4 shielded | Delta | - | 15 | 20 m | rol |
| DELTACAB-PWR-4G2.5 shielded | Delta | - | 22 | 30 m | rol |
| DELTACAB-PWR-4G1.5 shielded | Delta | - | 16 | 20 m | rol |
| DELTACAB-ENC-6x0.14 shielded | Delta | - | 53 | 60 m | rol |
| UNITRONIC Li2YCY 4x0.34 | Lapp | - | 166 | 200 m | rol |
| H05V-K 2x0.75 (BLK/RED) | Lapp | - | 16 | 20 m | rol |
| Safety Cable 2x2x0.75 YEL | Lapp | - | 11 | 15 m | rol |

---

## 5. Gland ve Fitting Listesi

### Ana Giris (Alt Sol)

| Gland Tipi | Kablo Cap | Adet | Uretici | Part No |
|------------|-----------|------|---------|---------|
| PG21 | 10-14mm | 2 | Wieland | RST21 |
| PG16 | 8-12mm | 3 | Wieland | RST16 |

### Saha Giris (Alt Sag)

| Gland Tipi | Kablo Cap | Adet | Uretici | Part No |
|------------|-----------|------|---------|---------|
| PG21 | 10-14mm | 5 | Wieland | RST21 | Motor power |
| PG16 | 8-12mm | 10 | Wieland | RST16 | Encoder |
| PG11 | 5-8mm | 15 | Wieland | RST11 | Sensor |
| PG9 | 4-6mm | 5 | Wieland | RST9 | Signal |
| PG7 | 3-5mm | 3 | Wieland | RST7 | Safety |

**Toplam Gland:** 40 adet

---

## 6. Ferrule (Krimp Terminal) Listesi

| Cap | Renk | Adet | Uretici | Part No |
|-----|------|------|---------|---------|
| 0.5mm2 | Beyaz | 50 | Phoenix | AI 0.5-10 WH |
| 0.75mm2 | Beyaz | 100 | Phoenix | AI 0.75-10 WH |
| 1.0mm2 | Kirmizi | 50 | Phoenix | AI 1.0-10 RD |
| 1.5mm2 | Siyah | 50 | Phoenix | AI 1.5-10 BK |
| 2.5mm2 | Mavi | 100 | Phoenix | AI 2.5-10 BU |
| 4.0mm2 | Gri | 50 | Phoenix | AI 4.0-12 GY |
| 6.0mm2 | Sari | 30 | Phoenix | AI 6.0-12 YE |
| 10mm2 | Sari | 20 | Phoenix | AI 10.0-12 YE |

**Toplam Ferrule:** 400 adet

---

## 7. Kablo Etiketleme Malzemesi

| Malzeme | Uretici | Part No | Miktar |
|---------|---------|---------|--------|
| Etiket Printer | Weidmuller | TOPMARK NEO | 1 adet |
| Etiket Kartusu | Weidmuller | TOPMARK-HS | 5 rol |
| Cable Tie Mount | HellermannTyton | T50ROEHS | 50 adet |
| Cable Tie 4.6x185 | HellermannTyton | S2F | 200 adet |
| Marker Tag 5mm | Phoenix | ZB 5 | 100 adet |

---

## 8. Notlar

1. **Service Loop:** Her saha kablosu icin 3m ekstra uzunluk (service loop) tavsiye edilir
2. **Spare:** Her kablo tipinden 10-20% yedek alinmasi tavsiye edilir
3. **Color Coding:** 
   - RED: +24VDC
   - BLU: 0VDC
   - BLK: AC power
   - YEL: Safety
   - GNYE: PE/Ground
4. **Shielding:** Motor power ve encoder kablolari shielded olmalidir
5. **Safety Cable:** Safety kablolari sari renkli ve ozel etiketli olmalidir

---

**Belge Durumu:** FINAL
**Hazirlayan:** CNCRevizyon
**Onaylayan:** ___________________
**Tarih:** ___________________
