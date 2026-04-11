# GFB60/30RE-S - Bill of Materials (BOM)

**Proje:** GFB60-30RE-S Elektrik Şeması Revizyon 4.1  
**Tarih:** 2026-04-11  
**Durum:** FINAL - Revizyon 4.1 pano imalat yayini

---

## 📋 İçindekiler

1. [Ana Güç Dağıtımı](#1-ana-güç-dağıtımı)
2. [Safety Devreleri](#2-safety-devreleri)
3. [CNC Kontrol Sistemi](#3-cnc-kontrol-sistemi)
4. [Servo Sürücüler ve Motorlar](#4-servo-sürücüler-ve-motorlar)
5. [I/O Sistemi](#5-io-sistemi)
6. [Sensörler](#6-sensörler)
7. [Konnektörler ve Kablolar](#7-konnektörler-ve-kablolar)
8. [Pano Malzemeleri](#8-pano-malzemeleri)

---

## 1. Ana Güç Dağıtımı

### AC Giriş ve Koruma

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| X1 | AC Giriş Terminali | MSTB 2.5/5-STF-5.08 | Phoenix Contact | 1 | Adet | 5-pin, 5.08mm |
| F0 | Parafudr | VAL-MS 400/3+1 | Phoenix Contact | 1 | Adet | 3-faz + N, 20kA |
| EMC1 | EMC Filtre | EMI-F400V-10A | Delta | 1 | Adet | 400VAC, 10A, 3-faz |
| Q1 | Ana Şalter | T5S 320 PR221DS-LSI | ABB | 1 | Adet | 32A, 3P, MCB |
| F1 | Ana Sigorta | 5ST3 3A | Siemens | 1 | Adet | 3A, slow-blow |
| K1 | Ana Kontaktör | LC1D32A3 | Schneider | 1 | Adet | 3P, 32A, 24VDC coil |
| PS1 | 24VDC Power Supply | VFD-24V-20A | Delta | 1 | Adet | 24VDC, 20A, 480W |

### DC Dağıtım Sigortaları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| F2 | NC300 Sigorta | 5ST1 4A | Siemens | 1 | Adet | 4A, fast-blow |
| F3 | R1-EC Sigorta | 5ST1 5A | Siemens | 1 | Adet | 5A, fast-blow |
| F4 | Sensors Sigorta | 5ST1 3A | Siemens | 1 | Adet | 3A, fast-blow |
| F5 | Safety Sigorta | 5ST1 2A | Siemens | 1 | Adet | 2A, fast-blow |
| F6 | HMI Sigorta | 5ST1 2A | Siemens | 1 | Adet | 2A, fast-blow |

### Terminal Blokları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| X2 | 24VDC Dağıtım | MSTB 2.5/8-STF-5.08 | Phoenix Contact | 1 | Adet | 8-pin, 5.08mm |
| PE1 | PE Bar | UK 2.5 B | Phoenix Contact | 1 | Adet | Ground terminal |

---

## 2. Safety Devreleri

### E-STOP ve Safety Devices

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| S0 | E-STOP Buton | XB4-BS542 | Schneider | 1 | Adet | 2NC, mushroom 40mm |
| S1 | Safety Door Switch | D4GS-NK2 | Omron | 1 | Adet | 2NC+1NO, manyetik |
| S2 | Reset Buton | XB4-BW33B5 | Schneider | 1 | Adet | NO, yeşil LED, 24V |

### Safety Relay

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| K10 | Safety Relay | PNOZ X2.8P | Pilz | 1 | Adet | 24-240VAC/DC, 3N/O+1N/C |
| FK1 | Faz Kontrol Rölesi | PNOZ EF Phase | Pilz | 1 | Adet | 3-faz monitor |

### Safety Terminal Blokları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| X10 | Safety Inputs | MSTB 2.5/6-STF-5.08 | Phoenix Contact | 1 | Adet | 6-pin, sarı |
| X11 | STO Outputs | MSTB 2.5/10-STF-5.08 | Phoenix Contact | 1 | Adet | 10-pin, sarı |
| X12 | Aux Signals | MSTB 2.5/5-STF-5.08 | Phoenix Contact | 1 | Adet | 5-pin, sarı |

---

## 3. CNC Kontrol Sistemi

### Ana Kontrolör

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U1 | NC300 CNC Controller | NC300-E | Delta | 1 | Adet | EtherCAT master |
| U2 | HMI | DOP-110CS | Delta | 1 | Adet | 10.1" TFT, 800x480 |

### NC300 Aksesuarlar

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| CN5 | D-Sub 50-pin Connector | 17JE-23500-02 | DDK | 1 | Adet | Female, solder type |
| CN3 | RJ45 Jack | JF-0014 | Jia Fei | 1 | Adet | Ethernet HMI |

---

## 4. Servo Sürücüler ve Motorlar

### X Ekseni (4.5kW)

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U41 | Servo Sürücü | ASD-A3-4523-E | Delta | 1 | Adet | 4.5kW, 3F 400VAC |
| M41 | Servo Motor | ECMA-L11845 | Delta | 1 | Adet | 4.5kW, 180mm frame |
| CN41_X1 | CN1 Connector | 17JE-23500-02 | DDK | 1 | Adet | 50-pin D-Sub |
| CN41_X2 | CN2 Connector | HR10A-7P-6S | Hirose | 1 | Adet | 6-pin encoder |
| CN41_X3 | CN3 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 IN |
| CN41_X6 | CN6 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 OUT |

### Y Ekseni (2.0kW)

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U42 | Servo Sürücü | ASD-A3-2023-E | Delta | 1 | Adet | 2.0kW, 3F 400VAC |
| M42 | Servo Motor | ECMA-E11320 | Delta | 1 | Adet | 2.0kW, 130mm frame |
| CN42_X1 | CN1 Connector | 17JE-23500-02 | DDK | 1 | Adet | 50-pin D-Sub |
| CN42_X2 | CN2 Connector | HR10A-7P-6S | Hirose | 1 | Adet | 6-pin encoder |
| CN42_X3 | CN3 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 IN |
| CN42_X6 | CN6 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 OUT |

### ALT Ekseni (2.0kW)

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U43 | Servo Sürücü | ASD-A3-2023-E | Delta | 1 | Adet | 2.0kW, 3F 400VAC |
| M43 | Servo Motor | ECMA-E11320 | Delta | 1 | Adet | 2.0kW, 130mm frame |
| CN43_X1 | CN1 Connector | 17JE-23500-02 | DDK | 1 | Adet | 50-pin D-Sub |
| CN43_X2 | CN2 Connector | HR10A-7P-6S | Hirose | 1 | Adet | 6-pin encoder |
| CN43_X3 | CN3 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 IN |
| CN43_X6 | CN6 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 OUT |

### Z Ekseni (1.0kW, Frenli)

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U44 | Servo Sürücü | ASD-A3-1023-E | Delta | 1 | Adet | 1.0kW, 1F 230VAC |
| M44 | Servo Motor | ECMA-C11010FS | Delta | 1 | Adet | 1.0kW, frenli, 100mm frame |
| CN44_X1 | CN1 Connector | 17JE-23500-02 | DDK | 1 | Adet | 50-pin D-Sub |
| CN44_X2 | CN2 Connector | HR10A-7P-6S | Hirose | 1 | Adet | 6-pin encoder |
| CN44_X3 | CN3 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 IN |
| CN44_X6 | CN6 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 OUT |

### CNC Ekseni (1.5kW)

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U45 | Servo Sürücü | ASD-A3-1523-E | Delta | 1 | Adet | 1.5kW, 1F 230VAC |
| M45 | Servo Motor | ECMA-E11315 | Delta | 1 | Adet | 1.5kW, 130mm frame |
| CN45_X1 | CN1 Connector | 17JE-23500-02 | DDK | 1 | Adet | 50-pin D-Sub |
| CN45_X2 | CN2 Connector | HR10A-7P-6S | Hirose | 1 | Adet | 6-pin encoder |
| CN45_X3 | CN3 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 IN |
| CN45_X6 | CN6 EtherCAT | RJH-0512 | JST | 1 | Adet | RJ45 OUT |

### Rejeneratif Dirençler

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| R41 | Rejeneratif Direnç | 60Ω / 100W | Delta | 1 | Adet | X ekseni (dahili) |
| R42 | Rejeneratif Direnç | 60Ω / 50W | Delta | 1 | Adet | Y ekseni (dahili) |
| R43 | Rejeneratif Direnç | 60Ω / 50W | Delta | 1 | Adet | ALT ekseni (dahili) |
| R44 | Rejeneratif Direnç | 120Ω / 50W | Delta | 1 | Adet | Z ekseni (dahili) |
| R45 | Rejeneratif Direnç | 80Ω / 50W | Delta | 1 | Adet | CNC ekseni (dahili) |

---

## 5. I/O Sistemi

### EtherCAT I/O Modülleri

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| U50 | Bus Coupler | R1-EC01 | Delta | 1 | Adet | EtherCAT coupler |
| U51 | DI Modül #1 | R1-EC0902D | Delta | 1 | Adet | 32-CH digital input |
| U52 | DI Modül #2 | R1-EC0902D | Delta | 1 | Adet | 32-CH digital input |
| U53 | DO Modül | R1-EC0902O | Delta | 1 | Adet | 32-CH relay output |

### I/O Terminal Blokları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| X20 | DI Terminal #1 | MSTB 2.5/16-STF-5.08 | Phoenix Contact | 2 | Adet | 16-pin x 2 |
| X30 | DI Terminal #2 | MSTB 2.5/16-STF-5.08 | Phoenix Contact | 2 | Adet | 16-pin x 2 |
| X40 | DO Terminal | MSTB 2.5/16-STF-5.08 | Phoenix Contact | 2 | Adet | 16-pin x 2 |

---

## 6. Sensörler

### Inductive Sensors (X/Y/Z/ALT)

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| S10 | X Home Sensor | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NO |
| S11 | X+ Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |
| S12 | X- Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |
| S20 | Y Home Sensor | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NO |
| S21 | Y+ Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |
| S22 | Y- Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |
| S30 | Z Home Sensor | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NO |
| S31 | Z+ Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |
| S40 | ALT Home Sensor | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NO |
| S41 | ALT+ Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |
| S42 | ALT- Limit | IS 218 MM | Leuze | 1 | Adet | M18, 8mm, PNP NC |

### Diğer Sensörler

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| S50 | Glass Detect | IS 218 AM | Leuze | 2 | Adet | M18, analog output |
| S51 | Vacuum FB | IS 218 MM | Leuze | 1 | Adet | M18, PNP NO |

### Sensör Aksesuarlar

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| CN_Sx | M12 Connector | NMEC-4S-LED | Ifm | 15 | Adet | 4-pin, female |
| BR_XY | L-Bracket | Custom 6mm Al | Local | 6 | Adet | X/Y limit sensors |
| BR_Z | U-Bracket | Custom 4mm SS | Local | 2 | Adet | Z axis sensors |

---

## 7. Konnektörler ve Kablolar

### Güç Kabloları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| W_AC10 | AC Ana Giriş | ÖLFLEX CLASSIC 110 4G10 | Lapp | 5 | m | 10mm², 4-core |
| W_AC6 | AC Servo X | ÖLFLEX CLASSIC 110 4G6 | Lapp | 5 | m | 6mm², 4-core |
| W_AC4 | AC Servo Y/ALT | ÖLFLEX CLASSIC 110 4G4 | Lapp | 10 | m | 4mm², 4-core |
| W_AC2.5 | AC Servo Z/CNC | ÖLFLEX CLASSIC 110 3G2.5 | Lapp | 10 | m | 2.5mm², 3-core |

### Kontrol Kabloları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| W_DC4 | 24VDC Ana | ÖLFLEX CLASSIC 110 2G4 | Lapp | 10 | m | 4mm², 2-core |
| W_DC2.5 | 24VDC Branch | ÖLFLEX CLASSIC 110 2G2.5 | Lapp | 20 | m | 2.5mm², 2-core |
| W_DC1.5 | Kontrol | ÖLFLEX CLASSIC 110 2G1.5 | Lapp | 30 | m | 1.5mm², 2-core |
| W_SAFE | Safety | ÖLFLEX CLASSIC 110 2G2.5 SW | Lapp | 15 | m | 2.5mm², sarı |

### Signal Kabloları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| W_SENS | Sensor Cable | UNITRONIC Li2YCY 4x0.34 | Lapp | 50 | m | 4x0.34mm², shielded |
| W_ENC | Encoder Cable | DELTACAB-ENC-6x0.14 | Delta | 10 | m | 6x0.14mm², shielded |
| W_ETH | EtherCAT Cable | CAT6 SF/UTP | Belden | 20 | m | CAT6, shielded |

### Servo Motor Kabloları

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| W_M41 | X Motor Power | DELTACAB-PWR-4G4 | Delta | 5 | m | 4x4mm², shielded |
| W_M42 | Y Motor Power | DELTACAB-PWR-4G2.5 | Delta | 5 | m | 4x2.5mm², shielded |
| W_M43 | ALT Motor Power | DELTACAB-PWR-4G2.5 | Delta | 5 | m | 4x2.5mm², shielded |
| W_M44 | Z Motor Power | DELTACAB-PWR-4G1.5 | Delta | 5 | m | 4x1.5mm², shielded |
| W_M45 | CNC Motor Power | DELTACAB-PWR-4G1.5 | Delta | 5 | m | 4x1.5mm², shielded |

---

## 8. Pano Malzemeleri

### DIN Ray ve Montaj

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| DR1 | DIN Ray 35mm | NSYSDR2 | Schneider | 2 | m | 2m length |
| MB1 | Mounting Plate | NSYMP1000 | Schneider | 1 | Adet | 1000x800mm |

### Kablo Kanalı

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| WT1 | Wire Duct 60x40 | NSYVDCA60X40 | Schneider | 10 | m | PVC, gray |
| WT2 | Wire Duct 40x40 | NSYVDCA40X40 | Schneider | 10 | m | PVC, gray |

### Kablo Bağı ve Fittingler

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| CB1 | Cable Tie | S2F | HellermannTyton | 100 | Adet | Nylon, 4.6x185mm |
| CB2 | Cable Tie Mount | T50ROEHS | HellermannTyton | 50 | Adet | Adhesive mount |
| GS1 | Grommet | 706-901 | WAGO | 20 | Adet | Cable entry |

### Wire Marker

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| WM1 | Wire Marker | TOPMARK NEO | Weidmüller | 1 | Set | Label printer |
| WM2 | Marker Strip | ZB 5 | Phoenix Contact | 10 | Adet | White, 5mm |

### Crimp Terminaler

| Ref | Açıklama | Model / Part No | Üretici | Miktar | Birim | Notlar |
|-----|----------|-----------------|---------|--------|-------|--------|
| CT1 | Ferrule 0.5mm² | AI 0.5-10 WH | Phoenix Contact | 200 | Adet | White |
| CT2 | Ferrule 1.0mm² | AI 1.0-10 BK | Phoenix Contact | 200 | Adet | Black |
| CT3 | Ferrule 1.5mm² | AI 1.5-10 BU | Phoenix Contact | 200 | Adet | Blue |
| CT4 | Ferrule 2.5mm² | AI 2.5-10 GY | Phoenix Contact | 100 | Adet | Gray |
| CT5 | Ferrule 4.0mm² | AI 4.0-12 RD | Phoenix Contact | 100 | Adet | Red |
| CT6 | Ferrule 6.0mm² | AI 6.0-12 YE | Phoenix Contact | 50 | Adet | Yellow |
| CT7 | Ferrule 10mm² | AI 10.0-12 GN | Phoenix Contact | 50 | Adet | Green |

---

## 📊 Toplam Maliyet Özeti

| Kategori | Tahmini Maliyet (EUR) |
|----------|----------------------|
| Ana Güç Dağıtımı | €2,500 - €3,000 |
| Safety Devreleri | €800 - €1,000 |
| CNC Kontrol Sistemi | €3,500 - €4,000 |
| Servo Sistem (5 eksen) | €15,000 - €18,000 |
| I/O Sistemi | €1,200 - €1,500 |
| Sensörler | €800 - €1,000 |
| Kablolar ve Konnektörler | €2,000 - €2,500 |
| Pano Malzemeleri | €500 - €700 |
| **TOPLAM** | **€26,300 - €31,700** |

---

## 📝 Notlar

### Tedarikçi Bilgileri

- **Delta:** Yetkili distribütörlerden temin edilmelidir
- **Phoenix Contact:** RS Components, Digikey
- **Schneider:** Yerel elektrik malzemesi tedarikçileri
- **Pilz:** Güvenlik otomasyon tedarikçileri
- **Leuze:** Sensör tedarikçileri

### Teslim Süreleri

| Kategori | Tahmini Teslim |
|----------|---------------|
| Delta Servo Sistem | 4-6 hafta |
| NC300 Controller | 3-4 hafta |
| Pilz Safety | 2-3 hafta |
| Phoenix Contact | 1-2 hafta |
| Kablolar | 1-2 hafta |
| Pano Malzemeleri | 1 hafta |

### Yedek Parça Önerileri

- Her eksenden 1 adet servo motor encoder kablosu
- 2 adet yedek sensör (M12 konnektörlü)
- 10 adet yedek ferrule seti
- 5 metre yedek sensor kablosu

---

**Son Güncelleme:** 2026-04-11  
**Hazırlayan:** CNCRevizyon BOM Ekibi  
**Versiyon:** 1.1 (Revizyon 4.1 yayini)  
**Durum:** FINAL
