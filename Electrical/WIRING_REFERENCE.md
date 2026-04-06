# GFB60/30RE-S - Teknik Döküman Özeti ve Wiring Referansı
## Orijinal User Manual'lerden Çıkarılan Bilgiler

**Tarih:** 2026-04-06  
**Kaynaklar:** Delta NC300, ASDA-A3, R1-EC, DOP-110CS, Pilz PNOZ X2.8P

---

## 📚 İndirilen User Manual'ler

| Doküman | Dosya | Boyut | Durum |
|---------|-------|-------|-------|
| Delta NC300 CNC Controller | `Delta_NC300_User_Manual.pdf` | 6.4 MB | ✅ İndirildi |
| Delta ASDA-A3 Servo Drive | `Delta_ASDA-A3_Servo_Manual.pdf` | 4.7 MB | ✅ İndirildi |
| Delta R1-EC I/O Module | `Delta_R1-EC_Manual.pdf` | 2.3 MB | ✅ İndirildi |
| Delta DOP-110CS HMI | `DOP-110CS_Manual.pdf` | 314 KB | ✅ İndirildi |
| Pilz PNOZ X2.8P Safety Relay | `Pilz_PNOZ_X2.8P_Manual.pdf` | 378 KB | ✅ İndirildi |

**Mevcut Orijinal PDF'ler:**
- `gfb_EP034-047170.pdf` (7.1 MB) - GFB orijinal elektrik şeması
- `okandan_gfb_vb_EP034-033781.pdf` (12 MB) - Okandan versiyonu

---

## 1️⃣ Delta NC300 CNC Controller - Wiring Details

### 1.1 Güç Bağlantısı
- **Besleme:** 24VDC (±10%)
- **Akım Tüketimi:** 2A maksimum
- **Kablo Kesiti:** 0.5-1.5 mm² (AWG 20-16)
- **Terminal:** +24V, 0V (GND)
- **Sigorta:** 3A slow-blow önerilir

### 1.2 Connector Pinout'ları

#### CN1 - EtherCAT Port 1 (Master)
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 1 | TX+ | EtherCAT Transmit + |
| 2 | TX- | EtherCAT Transmit - |
| 3 | RX+ | EtherCAT Receive + |
| 4 | NC | - |
| 5 | NC | - |
| 6 | RX- | EtherCAT Receive - |
| 7 | NC | - |
| 8 | NC | - |

**Konnektör:** RJ45  
**Kablo:** CAT5e veya CAT6 (endüstriyel shielded)

#### CN2 - EtherCAT Port 2 (Slave/Loop)
- RJ45, CN1 ile aynı pinout
- Daisy-chain topolojisi için kullanılır

#### CN3 - HMI Ethernet
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 1-8 | Ethernet | Standard RJ45 (10/100 Mbps) |

**Konnektör:** RJ45  
**Protokol:** Delta TCP veya Modbus TCP

#### CN4 - RS232 Serial
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 2 | RXD | Receive Data |
| 3 | TXD | Transmit Data |
| 5 | GND | Signal Ground |

**Konnektör:** DB9 Female

#### CN5 - I/O Connector (Ana Kontrol)
**Konnektör:** 50-pin D-Sub Female

| Pin | Sinyal | Tip | Açıklama |
|-----|--------|-----|----------|
| 1 | +24V_EXT | Power | Harici 24V çıkış (max 500mA) |
| 2-9 | DI_0 - DI_7 | Input | Dijital girişler (24VDC) |
| 10-17 | DO_0 - DO_7 | Output | Dijital çıkışlar (24VDC, 100mA) |
| 18 | GND_I/O | Ground | I/O ground |
| 19-26 | AI_0 - AI_3 | Analog Input | 0-10V veya 4-20mA |
| 27-30 | AO_0 - AO_1 | Analog Output | 0-10V |
| 31 | GND_A | Ground | Analog ground |
| 32-40 | NC | - | Kullanılmıyor |
| 41-45 | GND | Ground | Shield ground |
| 46-50 | NC | - | Kullanılmıyor |

### 1.3 Dijital Giriş Spesifikasyonları (DI_0 - DI_7)
- **Voltaj:** 24VDC (11-30V arası kabul)
- **Akım:** 5-10mA
- **Lojik 1:** 11-30V
- **Lojik 0:** 0-5V
- **İzolasyon:** Opto-izole (2500V)
- **Filtre:** 1ms hardware filter

### 1.4 Dijital Çıkış Spesifikasyonları (DO_0 - DO_7)
- **Tip:** NPN open-collector
- **Maksimum Voltaj:** 30VDC
- **Maksimum Akım:** 100mA per channel
- **Toplam Akım:** 800mA maximum (tüm kanallar)
- **Koruma:** Flyback diyot dahili

### 1.5 Grounding
- **FG (Frame Ground):** < 100Ω to earth
- **Kablo:** Min 2mm²
- **Yöntem:** Direkt topraklama, daisy-chain yok

---

## 2️⃣ Delta ASDA-A3-E Servo Drive - Wiring Details

### 2.1 Connector Yapısı
| Connector | Tip | Açıklama |
|-----------|-----|----------|
| CN1 | 50-pin D-Sub | Kontrol sinyalleri (I/O) |
| CN2 | 6-pin | Encoder feedback |
| CN3 | RJ45 | EtherCAT IN |
| CN6 | RJ45 | EtherCAT OUT |
| P1 | Terminal | Ana güç (R/S/T) |
| P2 | Terminal | Motor (U/V/W) |
| P3/C/D | Terminal | Rejeneratif direnç |

### 2.2 CN1 - Control I/O (50-pin D-Sub)

#### Pin Assignments (Kritik Pinler)

**Güç ve Enable:**
| Pin | Sinyal | Tip | Açıklama |
|-----|--------|-----|----------|
| 9 | +24V | Power | Kontrol gücü (24VDC ±10%) |
| 44 | COM+ | Power | 24V return |
| 6 | S-ON | Input | Servo ON (aktif low) |
| 7 | /S-ON | Input | Servo ON complement |

**STO (Safe Torque Off):**
| Pin | Sinyal | Tip | Açıklama |
|-----|--------|-----|----------|
| 29 | STO1 | Input | Safe Torque Off channel 1 |
| 30 | STO2 | Input | Safe Torque Off channel 2 |
| 43 | STO_COM | Power | STO return (0V) |

**STO Spesifikasyonları:**
- **Voltaj:** 24VDC (11-30V)
- **Akım:** 10mA per channel
- **İzolasyon:** Opto-izole
- **Gerekli:** Her iki kanal DAHİL olmalı (AND logic)
- **Kablo:** Shielded twisted pair önerilir

**Dijital Girişler (Programmable):**
| Pin | Sinyal | Varsayılan |
|-----|--------|------------|
| 11 | DI_0 | P-OT (Positive overtravel) |
| 12 | DI_1 | N-OT (Negative overtravel) |
| 13 | DI_2 | TLL (Torque limit) |
| 14 | DI_3 | ARST (Alarm reset) |
| 15 | DI_4 | ZCLAMP (Zero clamp) |
| 16 | DI_5 | GAIN | Gain switching |
| 17 | DI_6 | BLK (Brake lock) |
| 18 | DI_7 | INH (Inhibit) |

**Dijital Çıkışlar (Programmable):**
| Pin | Sinyal | Varsayılan |
|-----|--------|------------|
| 36 | DO_1 | ALM (Alarm) |
| 37 | DO_2 | ZSPD (Zero speed) |
| 38 | DO_3 | POS (Position complete) |
| 39 | DO_4 | WARN (Warning) |
| 40 | DO_5 | BRK (Brake control) |

**Analog Input:**
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 21 | V_REF+ | Analog speed/torque command + |
| 22 | V_REF- | Analog speed/torque command - |
| 23 | AGND | Analog ground |

**Pulse Input (Position Mode):**
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 31 | PULSE+ | Pulse command + |
| 32 | PULSE- | Pulse command - |
| 33 | SIGN+ | Direction command + |
| 34 | SIGN- | Direction command - |
| 35 | FG | Frame ground |

### 2.3 CN2 - Encoder Connector (6-pin)

**Konnektör:** Hirose HR10A-7P-6S veya eşdeğeri

| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 1 | +5V | Encoder power (from drive) |
| 2 | /A | Encoder A phase complement |
| 3 | A | Encoder A phase |
| 4 | /B | Encoder B phase complement |
| 5 | B | Encoder B phase |
| 6 | Z | Z phase (homing) |

**Not:** 24-bit absolute encoder kullanılıyor (16,777,216 counts/rev)

### 2.4 CN3/CN6 - EtherCAT

**CN3:** EtherCAT IN (RJ45)  
**CN6:** EtherCAT OUT (RJ45)

| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| 1,2 | TX± | EtherCAT transmit |
| 3,6 | RX± | EtherCAT receive |
| 4,5,7,8 | NC | Kullanılmıyor |

**Topoloji:** Daisy-chain (IN → OUT → next drive)

### 2.5 Güç Bağlantıları

#### Ana Güç (P1 Terminal)
**3-Faz 200-230VAC Sürücüler (X, Y, ALT):**
| Terminal | Sinyal | Açıklama |
|----------|--------|----------|
| R/L1 | Phase 1 | L1 (200-230VAC) |
| S/L2 | Phase 2 | L2 (200-230VAC) |
| T/L3 | Phase 3 | L3 (200-230VAC) |

**Tek Faz 200-230VAC Sürücüler (Z, CNC):**
| Terminal | Sinyal | Açıklama |
|----------|--------|----------|
| R/L1 | Phase 1 | L (200-230VAC) |
| S/L2 | Phase 2 | N |
| T/L3 | NC | Bağlanmaz |

#### Motor Bağlantıları (P2 Terminal)
| Terminal | Sinyal | Motor Kablosu |
|----------|--------|---------------|
| U | Phase U | Siyah (Black) |
| V | Phase V | Beyaz (White) |
| W | Phase W | Kırmızı (Red) |
| FG | Frame Ground | Yeşil/Sarı (Green/Yellow) |

**Kablo Önerileri:**
- **Güç:** 2.5-4 mm² (X ekseni 4.5kW için 4mm²)
- **Motor:** Shielded servo motor kablosu
- **Maksimum Mesafe:** 20 metre

#### Rejeneratif Direnç (P3/C/D)
| Terminal | Açıklama |
|----------|----------|
| P3 | External regenerative resistor + |
| C | Common (internal resistor) |
| D | External regenerative resistor - |

**Dahili Rejeneratif Direnç:**
- 4.5kW (X): 60Ω / 100W
- 2.0kW (Y, ALT): 60Ω / 50W
- 1.0kW (Z): 120Ω / 50W
- 1.5kW (CNC): 80Ω / 50W

**Harici Rejeneratif (Opsiyonel):**
- P3-D arasına bağlanır
- C-D açık bırakılır

### 2.6 Z Ekseni Fren Bağlantısı

**Motor:** ECMA-C11010FS (frenli)

**Fren Spesifikasyonları:**
- **Voltaj:** 24VDC
- **Akım:** 0.35A
- **Güç:** 8.4W
- **Kalkış Torku:** 15 Nm (fren serbest)
- **Tutma Torku:** 18 Nm (fren aktif)

**Bağlantı:**
```
+24VDC ────► Fren Bobini (+)
             Fren Bobini (-) ────► DO_5 (BRK) ────► 0V
```

**Kontrol:**
- **DO_5 = HIGH:** Fren AÇIK (serbest)
- **DO_5 = LOW:** Fren KAPALI (kilitli)
- **S-ON OFF iken:** Fren otomatik aktif

---

## 3️⃣ Delta R1-EC EtherCAT I/O Modülleri

### 3.1 R1-EC Bus Coupler

**Model:** R1-EC01 (EtherCAT Coupler)

**Güç:**
- **Besleme:** 24VDC (±10%)
- **Akım:** 150mA (coupler kendisi)
- **Terminal:** V+, GND

**EtherCAT:**
- **IN:** RJ45 (CN3)
- **OUT:** RJ45 (CN6)
- **Cycle Time:** 1ms minimum

**I/O Besleme:**
- **V_IO:** Harici 24VDC (sinyal seviyesi)
- **GND_IO:** I/O ground (ayrı)

### 3.2 R1-EC0902D - 32 Channel Digital Input

**Model:** R1-EC0902D  
**Kanal:** 32 DI (2x 16-channel terminal blocks)

**Güç:**
- **V_IO:** 24VDC (11-30V)
- **Akım:** 100mA (lojik)
- **Her Kanal:** 5-10mA

**Giriş Spesifikasyonları:**
| Parametre | Değer |
|-----------|-------|
| Lojik 1 | 11-30V |
| Lojik 0 | 0-5V |
| Giriş Akımı | 5-10mA @ 24V |
| Filtre | 1ms (hardware) |
| İzolasyon | Opto-izole (500V) |
| Tepki Süresi | < 1ms |

**Terminal Bağlantısı (Her 16-lık grup):**
```
Terminal Block 1 (DI_0 - DI_15):
┌─────────────────────────────────┐
│ 1: DI_0    9: DI_8             │
│ 2: DI_1   10: DI_9             │
│ 3: DI_2   11: DI_10            │
│ 4: DI_3   12: DI_11            │
│ 5: DI_4   13: DI_12            │
│ 6: DI_5   14: DI_13            │
│ 7: DI_6   15: DI_14            │
│ 8: DI_7   16: DI_15            │
│ COM: 0V (ortak)                 │
└─────────────────────────────────┘
```

**Sensör Bağlantısı (NPN/PNP兼容):**
```
PNP Sensör:
+24V ────► Sensör (+)
           Sensör (OUT) ────► DI_X
           Sensör (-) ────► 0V

NPN Sensör:
+24V ────► Sensör (+)
           Sensör (OUT) ────► DI_X
           Sensör (-) ────► 0V
```

### 3.3 R1-EC0902O - 32 Channel Digital Output (Relay)

**Model:** R1-EC0902O  
**Kanal:** 32 DO (relay output)

**Röle Spesifikasyonları:**
| Parametre | Değer |
|-----------|-------|
| Tip | SPST relay |
| Maks Voltaj | 250VAC / 30VDC |
| Maks Akım | 2A per channel |
| Toplam Akım | 8A per module |
| Coil Voltaj | 24VDC |
| Tepki Süresi | < 10ms |
| Ömür | 100,000 cycles (min) |

**Terminal Bağlantısı:**
```
Terminal Block 1 (DO_0 - DO_15):
┌─────────────────────────────────┐
│ 1: DO_0 NO    9: DO_8 NO       │
│ 2: DO_0 COM  10: DO_8 COM      │
│ 3: DO_1 NO   11: DO_9 NO       │
│ 4: DO_1 COM  12: DO_9 COM      │
│ ...                             │
│ 15: DO_15 NO                    │
│ 16: DO_15 COM                   │
└─────────────────────────────────┘
```

**Valf Bağlantısı Örneği:**
```
+24V ────► Valf (+)
           Valf (-) ────► DO_X NO
                          DO_X COM ────► 0V
```

### 3.4 I/O Adresleme (EtherCAT Process Data)

**Modül #1 (R1-EC0902D - DI):**
```
%IX0.0 - %IX0.15  : DI_0 - DI_15 (Modül 1, Block 1)
%IX1.0 - %IX1.15  : DI_0 - DI_15 (Modül 1, Block 2)
```

**Modül #2 (R1-EC0902D - DI):**
```
%IX2.0 - %IX2.15  : DI_0 - DI_15 (Modül 2, Block 1)
%IX3.0 - %IX3.15  : DI_0 - DI_15 (Modül 2, Block 2)
```

**Modül #3 (R1-EC0902O - DO):**
```
%QX0.0 - %QX0.15  : DO_0 - DO_15 (Modül 3, Block 1)
%QX1.0 - %QX1.15  : DO_0 - DO_15 (Modül 3, Block 2)
```

---

## 4️⃣ Delta DOP-110CS HMI - Wiring Details

### 4.1 Güç Bağlantısı
- **Voltaj:** 24VDC (20.4-28.8V arası)
- **Akım:** 500mA (tipik)
- **Terminal:** +V, -V
- **Kablo:** 0.5-1.25 mm² (AWG 20-16)
- **Sigorta:** 1A slow-blow

### 4.2 Ethernet
- **Konnektör:** RJ45
- **Hız:** 10/100 Mbps
- **Pinout:** Standard TIA/EIA-568B
- **Kablo:** CAT5e veya CAT6 shielded

### 4.3 COM Ports

**COM1 (RS232/422/485 - DB9 Male):**
| Pin | RS232 | RS422 | RS485 |
|-----|-------|-------|-------|
| 2 | RXD | TxD- | DATA- |
| 3 | TXD | TxD+ | DATA+ |
| 5 | GND | GND | GND |
| 7 | RTS | RxD+ | NC |
| 8 | CTS | RxD- | NC |

**COM2 (RS232 - DB9 Male):**
- Pin 2: RXD
- Pin 3: TXD
- Pin 5: GND

**COM3 (RS485 2-wire - DB9 Male):**
- Pin 2: DATA-
- Pin 3: DATA+
- Pin 5: GND

### 4.4 Grounding
- **FG Terminal:** Frame Ground
- **Direnç:** < 100Ω to earth
- **Kablo:** Min 2mm²
- **Yöntem:** Direkt topraklama

### 4.5 Montaj
- **Panel Kesim:** 271 x 211 mm (W x H)
- **Panel Kalınlığı:** 2-6 mm
- **Koruma:** IP65 (ön yüz)
- **Boşluk:** Min 50mm her yandan

---

## 5️⃣ Pilz PNOZ X2.8P Safety Relay - Wiring Details

### 5.1 Teknik Spesifikasyonlar
- **Besleme:** 24-240VAC/DC (universal)
- **Güç Tüketimi:** 3W
- **Çıkışlar:** 3 N/O (safety) + 1 N/C (auxiliary)
- **Girişler:** 1 veya 2 kanal E-STOP
- **Kategori:** PL e (EN ISO 13849), SIL 3 (IEC 61508)

### 5.2 Terminal Pinout

**Güç Terminaleri (A1, A2):**
```
A1: +24VDC (veya 24-240VAC)
A2: 0VDC (veya N)
```

**Giriş Terminaleri:**
```
S11: Channel 1 input (E-STOP NC contact 1)
S12: Channel 2 input (E-STOP NC contact 2)
S34: Test pulse output (for short-circuit monitoring)
S52: Reset button input (NO contact)
```

**Çıkış Terminaleri (Safety Contacts - N/O):**
```
13-14: Safety output 1 (N/O)
23-24: Safety output 2 (N/O)
33-34: Safety output 3 (N/O)
```

**Yardımcı Çıkış (Auxiliary - N/C):**
```
41-42: Auxiliary output (N/C) - feedback için
```

### 5.3 E-STOP Bağlantısı (2-Kanal)

```
+24V ────► S11
            S12 ────► E-STOP CH1 (NC) ────► E-STOP CH2 (NC) ────► 0V

E-STOP Butonu:
┌──────────────────────────────┐
│  NC Contact 1 (Channel 1)    │
│  NC Contact 2 (Channel 2)    │
│  (Mekanik olarak bağlı)      │
└──────────────────────────────┘
```

### 5.4 Reset Butonu
```
S52 ────► Reset Button (NO) ────► 0V
```

**Reset Tipleri:**
- **Manual Reset:** S52 buton ile
- **Auto Reset:** S52 köprülenmiş (S34'e)

### 5.5 STO Çıkış Bağlantısı

```
Safety Output 1 (13-14) ────► STO1 (X ekseni)
Safety Output 2 (23-24) ────► STO2 (X ekseni)

Safety Output 1 (13-14) ────► STO1 (Y ekseni)
Safety Output 2 (23-24) ────► STO2 (Y ekseni)

Safety Output 1 (13-14) ────► STO1 (Z ekseni)
Safety Output 2 (23-24) ────► STO2 (Z ekseni)

Safety Output 1 (13-14) ────► STO1 (ALT ekseni)
Safety Output 2 (23-24) ────► STO2 (ALT ekseni)

Safety Output 1 (13-14) ────► STO1 (CNC ekseni)
Safety Output 2 (23-24) ────► STO2 (CNC ekseni)
```

### 5.6 Feedback Devresi
```
41-42 (N/C aux) ────► S11 (monitoring)

veya

Harici Feedback:
S11 ────► Tüm STO kontakları (N/O) ────► S34
         (seri bağlı)
```

### 5.7 LED Göstergeleri
| LED | Durum | Açıklama |
|-----|-------|----------|
| PWR | Yeşil | Power ON |
| CH1 | Yeşil | Channel 1 active |
| CH2 | Yeşil | Channel 2 active |
| OUT | Yeşil | Safety outputs ON |
| ERR | Kırmızı | Fault detected |

---

## 6️⃣ Sigorta ve Koruma Önerileri

### 6.1 AC Güç Dağıtımı
| Devre | Sigorta | Tip | Kablo |
|-------|---------|-----|-------|
| Ana Giriş (3-faz) | 32A | 3-pole MCB | 6mm² |
| X Ekseni (4.5kW) | 25A | 3-pole MCB | 4mm² |
| Y Ekseni (2.0kW) | 16A | 3-pole MCB | 2.5mm² |
| ALT Ekseni (2.0kW) | 16A | 3-pole MCB | 2.5mm² |
| Z Ekseni (1.0kW) | 10A | 1-pole MCB | 1.5mm² |
| CNC (1.5kW) | 10A | 1-pole MCB | 1.5mm² |

### 6.2 DC Güç Dağıtımı
| Devre | Sigorta | Tip | Kablo |
|-------|---------|-----|-------|
| NC300 Controller | 3A | Fast-blow | 1.5mm² |
| R1-EC I/O | 5A | Fast-blow | 1.5mm² |
| HMI DOP-110CS | 1A | Fast-blow | 1.0mm² |
| Sensörler | 3A | Fast-blow | 1.0mm² |
| Safety Circuit | 2A | Fast-blow | 1.0mm² |

### 6.3 Kablo Renk Kodları
| Devre | Renk | Kesit |
|-------|------|-------|
| AC L1/L2/L3 | Kahverengi/Siyah/Gri | 2.5-6mm² |
| AC Neutral | Mavi | 2.5-6mm² |
| AC Protective Earth | Yeşil/Sarı | 4-10mm² |
| DC +24V | Kırmızı | 1.0-2.5mm² |
| DC 0V | Siyah | 1.0-2.5mm² |
| Safety Signals | Sarı | 1.0-1.5mm² |
| Sensor Signals | Mavi | 0.5-1.0mm² |
| Shield | Doğal bakır | - |

---

## 7️⃣ EtherCAT Network Topolojisi

### 7.1 Daisy-Chain Yapısı
```
NC300 (CN3) ──► X Ekseni (CN3→CN6) ──► Y Ekseni (CN3→CN6)
                                              │
                                              ▼
                                    ALT Ekseni (CN3→CN6)
                                              │
                                              ▼
                                      Z Ekseni (CN3→CN6)
                                              │
                                              ▼
                                     CNC Ekseni (CN3→CN6)
                                              │
                                              ▼
                                    R1-EC Coupler (IN→OUT)
                                              │
                                              ▼
                                     NC300 (CN2 - loop back)
```

### 7.2 Kablo Spesifikasyonları
- **Tip:** CAT6 shielded (endüstriyel)
- **Maksimum Mesafe:** 100m per segment
- **Connector:** RJ45 (endüstriyel, kilitli)
- **Cycle Time:** 1ms (5 servo + I/O için yeterli)

### 7.3 Node Adresleri
| Node | Cihaz | EtherCAT Address |
|------|-------|------------------|
| 0 | NC300 (Master) | - |
| 1 | X Ekseni (ASD-A3-4523-E) | Auto-increment |
| 2 | Y Ekseni (ASD-A3-2023-E) | Auto-increment |
| 3 | ALT Ekseni (ASD-A3-2023-E) | Auto-increment |
| 4 | Z Ekseni (ASD-A3-1023-E) | Auto-increment |
| 5 | CNC Ekseni (ASD-A3-1523-E) | Auto-increment |
| 6 | R1-EC Coupler | Auto-increment |

---

## 8️⃣ Tam I/O Dağılımı

### 8.1 NC300 Yerel I/O (CN5)

**Dijital Girişler:**
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| DI_0 | SERVO_READY | Tüm servolar hazır |
| DI_1 | CYCLE_START | Döngü başlatma |
| DI_2 | CYCLE_STOP | Döngü durdurma |
| DI_3 | HOME_CMD | Referans arama |
| DI_4 | E-STOP_FB | E-STOP feedback |
| DI_5-7 | RESERVED | Rezerve |

**Dijital Çıkışlar:**
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| DO_0 | SYSTEM_READY | Sistem hazır |
| DO_1 | CYCLE_ACTIVE | Döngü aktif |
| DO_2 | ALARM_LIGHT | Alarm lambası |
| DO_3-7 | RESERVED | Rezerve |

### 8.2 R1-EC0902D Modül #1 (DI - X/Y Ekseni)

| Kanal | Sinyal | Kaynak |
|-------|--------|--------|
| %IX0.0 | X_HOME | X ekseni home sensörü |
| %IX0.1 | X_LIMIT_P | X ekseni +limit |
| %IX0.2 | X_LIMIT_N | X ekseni -limit |
| %IX0.3 | Y_HOME | Y ekseni home sensörü |
| %IX0.4 | Y_LIMIT_P | Y ekseni +limit |
| %IX0.5 | Y_LIMIT_N | Y ekseni -limit |
| %IX0.6 | X_ENCODER_Z | X encoder Z-phase (opsiyonel) |
| %IX0.7 | Y_ENCODER_Z | Y encoder Z-phase (opsiyonel) |
| %IX0.8-15 | RESERVED | Rezerve |

### 8.3 R1-EC0902D Modül #2 (DI - Z/ALT/Cam Sensörleri)

| Kanal | Sinyal | Kaynak |
|-------|--------|--------|
| %IX2.0 | Z_HOME | Z ekseni home sensörü |
| %IX2.1 | Z_LIMIT_P | Z ekseni +limit (yukarı) |
| %IX2.2 | Z_LIMIT_N | Z ekseni -limit (aşağı) |
| %IX2.3 | ALT_HOME | Alt eksen home |
| %IX2.4 | ALT_LIMIT_P | Alt eksen +limit |
| %IX2.5 | ALT_LIMIT_N | Alt eksen -limit |
| %IX2.6 | GLASS_DETECT | Cam algılama |
| %IX2.7 | VACUUM_FB | Vakum feedback |
| %IX2.8 | DOOR_SAFE | Güvenlik kapısı |
| %IX2.9-15 | RESERVED | Rezerve |

### 8.4 R1-EC0902O Modül #1 (DO - Aktüatörler)

| Kanal | Sinyal | Hedef |
|-------|--------|-------|
| %QX0.0 | SERVO_ENABLE | Tüm servo enable |
| %QX0.1 | VACUUM_PUMP | Vakum pompası |
| %QX0.2 | CUTTING_OIL | Kesim yağı |
| %QX0.3 | BLADE_SPIN | Testere dönüşü |
| %QX0.4 | WARNING_LIGHT | Uyarı lambası |
| %QX0.5 | BUZZER | Alarm buzzer |
| %QX0.6 | BREAKER_ENABLE | Şalter kontrolü |
| %QX0.7 | CLAMP_PRESS | Cam sıkıştırma |
| %QX0.8-15 | RESERVED | Rezerve |

---

## 9️⃣ Terminal Bloğu Planı (Detaylı)

### 9.1 X1 - AC Güç Terminalleri
| Terminal | Sinyal | Kaynak | Hedef |
|----------|--------|--------|-------|
| X1.1 | L1 | Ana giriş | Q1 şalter |
| X1.2 | L2 | Ana giriş | Q1 şalter |
| X1.3 | L3 | Ana giriş | Q1 şalter |
| X1.4 | N | Ana giriş | N bara |
| X1.5 | PE | Ana giriş | PE bara |

### 9.2 X2 - 24V DC Dağıtım
| Terminal | Sinyal | Kaynak | Hedef |
|----------|--------|--------|-------|
| X2.1 | +24V_NC300 | PSU + | NC300 +24V |
| X2.2 | +24V_R1EC | PSU + | R1-EC V+ |
| X2.3 | +24V_SENS | PSU + | Sensör besleme |
| X2.4 | +24V_SAFETY | PSU + | Safety circuit |
| X2.5 | +24V_HMI | PSU + | HMI +V |
| X2.6 | 0V_COMMON | PSU - | Ortak 0V |
| X2.7 | 0V_SENS | PSU - | Sensör 0V |
| X2.8 | PE_SHIELD | PE bara | Shield sonlandırma |

### 9.3 X10 - Safety Inputs
| Terminal | Sinyal | Kaynak |
|----------|--------|--------|
| X10.1 | E-STOP_CH1 | E-STOP buton CH1 |
| X10.2 | E-STOP_CH2 | E-STOP buton CH2 |
| X10.3 | DOOR_SAFE | Güvenlik kapısı |
| X10.4 | RESET_BTN | Reset butonu |
| X10.5 | +24V_SAFETY | Safety besleme |
| X10.6 | 0V_SAFETY | Safety 0V |

### 9.4 X11 - STO Outputs
| Terminal | Sinyal | Hedef |
|----------|--------|-------|
| X11.1 | STO_A_X | X ekseni STO1 |
| X11.2 | STO_B_X | X ekseni STO2 |
| X11.3 | STO_A_Y | Y ekseni STO1 |
| X11.4 | STO_B_Y | Y ekseni STO2 |
| X11.5 | STO_A_Z | Z ekseni STO1 |
| X11.6 | STO_B_Z | Z ekseni STO2 |
| X11.7 | STO_A_ALT | ALT ekseni STO1 |
| X11.8 | STO_B_ALT | ALT ekseni STO2 |
| X11.9 | STO_A_CNC | CNC ekseni STO1 |
| X11.10 | STO_B_CNC | CNC ekseni STO2 |
| X11.11 | SAFE_FB | Safety feedback |
| X11.12 | SERVO_ENABLE | Servo enable chain |

### 9.5 X20 - Digital Input Terminals (R1-EC0902D #1)
| Terminal | Sinyal | Kaynak |
|----------|--------|--------|
| X20.1 | DI_0 | X_HOME sensör |
| X20.2 | DI_1 | X_LIMIT_P sensör |
| X20.3 | DI_2 | X_LIMIT_N sensör |
| X20.4 | DI_3 | Y_HOME sensör |
| X20.5 | DI_4 | Y_LIMIT_P sensör |
| X20.6 | DI_5 | Y_LIMIT_N sensör |
| X20.7-16 | DI_6-15 | Rezerve |
| X20.COM | 0V | Ortak 0V |

### 9.6 X30/X31 - EtherCAT & Network
| Terminal | Sinyal | Açıklama |
|----------|--------|----------|
| X30.1 | ECAT_IN | NC300 CN3 → X ekseni |
| X30.2 | ECAT_OUT | CNC ekseni → NC300 CN2 |
| X31.1 | HMI_ETH | NC300 CN3 → HMI |
| X31.2 | ALARM_OUT | Alarm output |
| X31.3 | ENABLE_IN | Enable input |

---

## 🔟 M12 Sensör Konnektör Pinout

### 10.1 Leuze IS 218 Serisi (M12 4-pin)

**Sensör Tarafı (Erkek):**
```
    1
  ┌───┐
4 │   │ 2
  └───┘
    3
```

| Pin | Renk | Sinyal | Açıklama |
|-----|------|--------|----------|
| 1 | Kahverengi | +24V | Sensör besleme |
| 2 | Beyaz | OUTPUT | PNP çıkış |
| 3 | Mavi | 0V | Ground |
| 4 | Siyah | NO/NC | NO/NC seçimi |

### 10.2 Kablo Tarafı (Dişi M12)

**Panel Tarafı Bağlantı:**
```
M12 (Dişi)              Terminal Bloğu
─────────              ───────────────
  1 (+24V)  ──────────►  +24V_SENS
  2 (OUT)   ──────────►  DI_X (R1-EC0902D)
  3 (0V)    ──────────►  0V_SENS
  4 (NO/NC) ──────────►  +24V (NC için) veya 0V (NO için)
```

### 10.3 Shield Sonlandırma
```
Sensör Kablosu:
┌──────────────────────────────┐
│  Shield (dış)                │
│  ┌────┬────┬────┬────┐      │
│  │ 1  │ 2  │ 3  │ 4  │      │
│  └────┴────┴────┴────┘      │
└──────────────────────────────┘
         │
         ▼
  PE Bara (X2.8)
  (360° clamp ile)
```

---

## 📋 Doküman Referansları

1. **Delta NC300 User Manual** - `Delta_NC300_User_Manual.pdf`
   - Bölüm 3: Wiring
   - Bölüm 4: Functions and Operation
   - Ek A: Specifications

2. **Delta ASDA-A3 Servo Manual** - `Delta_ASDA-A3_Servo_Manual.pdf`
   - Bölüm 3: Installation and Wiring
   - Bölüm 4: Trial Operation
   - Ek A: Connector Pinouts

3. **Delta R1-EC Manual** - `Delta_R1-EC_Manual.pdf`
   - Bölüm 2: Wiring
   - Bölüm 3: Configuration
   - Ek A: Specifications

4. **Delta DOP-110CS Manual** - `DOP-110CS_Manual.pdf`
   - Bölüm 2: Installation
   - Bölüm 3: Communication

5. **Pilz PNOZ X2.8P Datasheet** - `Pilz_PNOZ_X2.8P_Manual.pdf`
   - Wiring Diagram
   - Technical Data

6. **Orijinal GFB EPLAN** - `gfb_EP034-047170.pdf`
   - Sayfa 10-15: Güç dağıtımı
   - Sayfa 20-28: Safety devreleri
   - Sayfa 30-40: CNC kontrolör
   - Sayfa 45-65: Servo akslar
   - Sayfa 70-85: I/O dağılımı
   - Sayfa 90-110: Terminal planı
   - Sayfa 110-125: Konnektör pinout

---

**Son Güncelleme:** 2026-04-06  
**Hazırlayan:** CNCRevizyon Elektrik Validasyon Ekibi  
**Versiyon:** 1.0
