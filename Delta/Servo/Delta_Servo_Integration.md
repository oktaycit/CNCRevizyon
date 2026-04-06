# Delta ASDA-A3-E EtherCAT Servo Entegrasyonu
## Lisec GFB-60/30RE Cam Kesme Makinesi

## 1. Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Delta NC300 (EtherCAT Master)                    │
│                    - G-Kod İşleme                                   │
│                    - 100μs EtherCAT Cycle Time                      │
│                    - E-Cam Desteği                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ ASDA-A3-E       │  │ ASDA-A3-E       │  │ ASDA-A3-E       │
│ 4.5kW           │  │ 2.0kW           │  │ 2.0kW           │
│ X Ekseni        │  │ Y Ekseni        │  │ Alt Ekseni      │
│ ECMA-L11845     │  │ ECMA-E11320     │  │ ECMA-E11320     │
└─────────────────┘  └─────────────────┘  └─────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ ASDA-A3-E       │  │ ASDA-A3-E       │  │ R1-EC           │
│ 1.0kW           │  │ 1.5kW           │  │ Bus Coupler     │
│ Z Ekseni        │  │ CNC/Rodaj       │  │ EtherCAT Slave  │
│ ECMA-C11010     │  │ ECMA-E11315     │  │                 │
│ (Frenli)        │  │ (IP67)          │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          ┌─────────────────┐  ┌─────────────────┐
          │ R1-EC0902D x3   │  │ R1-EC0902O x3   │
          │ 16 DI x3 = 48   │  │ 16 DO x3 = 48   │
          │ (Sensörler)     │  │ (Valfler)       │
          └─────────────────┘  └─────────────────┘
```

## 2. ASDA-A3-E Serisi Özellikler

### 2.1 Teknik Spesifikasyonlar
| Özellik | Değer |
|---------|-------|
| Haberleşme | EtherCAT (CoE - CAN over EtherCAT) |
| Cycle Time | 100 μs (minimum) |
| Bant Genişliği | 3.1 kHz |
| Encoder Çözünürlüğü | 24-bit (16,777,216 pulse/rev) |
| STO | Safe Torque Off (IEC 61800-5-2) |
| Kazanım Ayarı | Auto-tuning II |

### 2.2 Sürücü Seçimi

| Eksen | Sürücü Model | Motor Model | Güç | Voltaj | Fren |
|-------|--------------|-------------|-----|--------|------|
| X | ASD-A3-4523-E | ECMA-L11845 | 4.5kW | 400VAC | Hayır |
| Y | ASD-A3-2023-E | ECMA-E11320 | 2.0kW | 220VAC | Hayır |
| Alt | ASD-A3-2023-E | ECMA-E11320 | 2.0kW | 220VAC | Hayır |
| Z | ASD-A3-1023-E | ECMA-C11010 | 1.0kW | 220VAC | **Evet** |
| CNC/Rodaj | ASD-A3-1523-E | ECMA-E11315 | 1.5kW | 220VAC | Hayır |

### 2.3 Motor Özellikleri

#### ECMA-L11845 (X Ekseni - Yüksek Atalet)
| Özellik | Değer |
|---------|-------|
| Güç | 4.5 kW |
| Hız | 2000 rpm |
| Tork | 21.5 Nm |
| Flanş | 180 mm |
| Mil Çapı | 48 mm |
| Atalet Oranı | Yüksek (L serisi) |
| Encoder | 24-bit绝对值 |

#### ECMA-E11320 (Y/Alt Ekseni - Orta Atalet)
| Özellik | Değer |
|---------|-------|
| Güç | 2.0 kW |
| Hız | 2000 rpm |
| Tork | 9.55 Nm |
| Flanş | 130 mm |
| Mil Çapı | 38 mm |
| Atalet Oranı | Orta (E serisi) |
| Encoder | 24-bit绝对值 |

#### ECMA-C11010 (Z Ekseni - Düşük Atalet, Frenli)
| Özellik | Değer |
|---------|-------|
| Güç | 1.0 kW |
| Hız | 2000 rpm |
| Tork | 4.77 Nm |
| Flanş | 100 mm |
| Mil Çapı | 24 mm |
| Fren | 24V DC Fren (dahili) |
| Atalet Oranı | Düşük (C serisi) |
| Encoder | 24-bit绝对值 |

#### ECMA-E11315 (CNC/Rodaj - IP67)
| Özellik | Değer |
|---------|-------|
| Güç | 1.5 kW |
| Hız | 2000 rpm |
| Tork | 7.16 Nm |
| Flanş | 130 mm |
| Mil Çapı | 38 mm |
| Koruma | IP67 |
| Encoder | 24-bit绝对值 |

## 3. EtherCAT Konfigürasyonu

### 3.1 NC300 EtherCAT Ayarları
```
Master Ayarları:
- Cycle Time: 100 μs
- Sync Mode: DC (Distributed Clock)
- Watchdog: 10 ms

Slave Adresleme:
- Slave 1: ASD-A3-E X (4.5kW)
- Slave 2: ASD-A3-E Y (2.0kW)
- Slave 3: ASD-A3-E Alt (2.0kW)
- Slave 4: ASD-A3-E Z (1.0kW)
- Slave 5: ASD-A3-E CNC (1.5kW)
- Slave 6: R1-EC Bus Coupler
  ├─ R1-EC0902D #1 (DI 1-16)
  ├─ R1-EC0902D #2 (DI 17-32)
  ├─ R1-EC0902D #3 (DI 33-48)
  ├─ R1-EC0902O #1 (DO 1-16)
  ├─ R1-EC0902O #2 (DO 17-32)
  └─ R1-EC0902O #3 (DO 33-48)
```

### 3.2 PDO Mapping (Process Data Objects)

#### RxPDO (NC300 → Sürücü)
```
0x1600 - Control Word
0x1601 - Target Position
0x1602 - Target Velocity
0x1603 - Torque Offset
```

#### TxPDO (Sürücü → NC300)
```
0x1A00 - Status Word
0x1A01 - Actual Position
0x1A02 - Actual Velocity
0x1A03 - Actual Torque
0x1A04 - Following Error
```

### 3.3 CoE Parametreleri (Object Dictionary)

| Index | Sub | Ad | Tip | Açıklama |
|-------|-----|----|-----|----------|
| 0x6040 | 0 | Control Word | UINT16 | Servo kontrol |
| 0x6041 | 0 | Status Word | UINT16 | Servo durumu |
| 0x6060 | 0 | Modes of Operation | INT8 | 8=CSP, 9=CSV, 10=CST |
| 0x607A | 0 | Target Position | INT32 | Hedef pozisyon |
| 0x607C | 0 | Home Offset | INT32 | Referans offset |
| 0x6081 | 0 | Velocity | UDINT | Hız limiti |
| 0x6098 | 0 | Homing Method | INT8 | Referans metodu |
| 0x60B0 | 0 | Position Offset | INT32 | Pozisyon offset |
| 0x60B8 | 0 | Touch Probe Function | UINT16 | Probe fonksiyonu |
| 0x60B9 | 0 | Touch Probe Status | UINT16 | Probe durumu |
| 0x60BA | 0 | Touch Probe Value 1 | INT32 | Probe değer 1 |
| 0x60BB | 0 | Touch Probe Value 2 | INT32 | Probe değer 2 |

## 4. Sürücü Parametre Ayarları (ASDA-Soft)

### 4.1 Temel Parametreler
```
P1-00: Kontrol Modu = 0x000B (EtherCAT CoE)
P1-01: Maksimum Hız = Motor nominal hızı
P1-02: Maksimum Tork = %150 (X), %120 (Y/Z)
P1-44: Electronic Gear Numerator = 10
P1-45: Electronic Gear Denominator = 1
```

### 4.2 EtherCAT Parametreleri
```
P3-00: EtherCAT Node ID = 1 (X), 2 (Y), 3 (Alt), 4 (Z), 5 (CNC)
P3-01: EtherCAT Cycle Time = 100 (μs)
P3-02: DC Sync Mode = 1 (Enable)
P3-03: Watchdog Time = 10 (ms)
```

### 4.3 Homing Parametreleri
```
P2-10: Home Mode = 17 (Z-sensor + rising edge)
P2-11: Home Velocity = 500 rpm
P2-12: Home Acceleration = 1000 rpm/s
P2-13: Home Offset = 0
P2-14: Home Direction = 0 (Positive)
```

### 4.4 Gain Ayarları (Auto-tuning II)
```
P2-30: Auto-tuning Mode = 2 (Real-time)
P2-31: Rigidity = 10 (Orta sertlik)
P2-32: Speed Loop Gain = Auto
P2-33: Speed Loop Integral = Auto
P2-34: Position Loop Gain = Auto
```

## 5. STO (Safe Torque Off) Bağlantısı

### 5.1 Güvenlik Devresi
```
                    ┌─────────────────┐
E-Stop Butonu ─────►│ Pilz PNOZ X2.8P │
                    │ Güvenlik Rölesi │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ STO+ / STO-     │ │ STO+ / STO-     │ │ STO+ / STO-     │
│ ASD-A3-E (X)    │ │ ASD-A3-E (Y)    │ │ ASD-A3-E (Z)    │
│ Pin: ST1, ST2   │ │ Pin: ST1, ST2   │ │ Pin: ST1, ST2   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 5.2 STO Teknik Özellikler
| Özellik | Değer |
|---------|-------|
| Giriş Voltajı | 24V DC (±20%) |
| Giriş Akımı | 10 mA (tipik) |
| Response Time | <10 ms |
| SIL Seviyesi | SIL 3 (IEC 61508) |
| PL Seviyesi | PL e (ISO 13849) |
| Kategori | Cat. 4 |

## 6. R1-EC Uzak I/O Sistemi

### 6.1 Modül Özellikleri

#### R1-EC0902D (16 Kanal Dijital Giriş)
| Özellik | Değer |
|---------|-------|
| Giriş Sayısı | 16 |
| Giriş Voltajı | 24V DC |
| Giriş Akımı | 7 mA (tipik) |
| İzolasyon | 500V AC, 1 dakika |
| Response Time | 0.5 ms / 3 ms (seçilebilir) |

#### R1-EC0902O (16 Kanal Dijital Çıkış)
| Özellik | Değer |
|---------|-------|
| Çıkış Sayısı | 16 |
| Çıkış Tipi | Sink (NPN) |
| Maks. Akım | 0.5 A / kanal |
| Toplam Akım | 4 A / modül |
| Kısa Devre Koruması | Var |

### 6.2 I/O Adresleme

#### Dijital Girişler (R1-EC0902D)
| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %IX0.0 | X+LIMIT | X ekseni + limit |
| %IX0.1 | X-LIMIT | X ekseni - limit |
| %IX0.2 | X-HOME | X ekseni referans |
| %IX0.3 | Y+LIMIT | Y ekseni + limit |
| %IX0.4 | Y-LIMIT | Y ekseni - limit |
| %IX0.5 | Y-HOME | Y ekseni referans |
| %IX0.6 | Z+LIMIT | Z ekseni + limit |
| %IX0.7 | Z-LIMIT | Z ekseni - limit |
| %IX0.8 | Z-HOME | Z ekseni referans |
| %IX0.9 | ALT+LIMIT | Alt ekseni + limit |
| %IX0.10 | ALT-LIMIT | Alt ekseni - limit |
| %IX0.11 | ALT-HOME | Alt ekseni referans |
| %IX0.12 | E-STOP1 | Acil durdurma 1 |
| %IX0.13 | E-STOP2 | Acil durdurma 2 |
| %IX0.14 | DOOR_OPEN | Güvenlik kapısı |
| %IX0.15 | VACUUM_OK | Vakum sensörü |
| %IX1.0 | GLASS_DETECT | Cam algılama |
| %IX1.1 | OIL_LEVEL | Yağ seviyesi |
| %IX1.2 | AIR_PRESSURE | Hava basıncı |
| %IX1.3 | BREAKER_OK | Kırıcı hazır |
| %IX1.4-15 | RESERVED | Yedek |

#### Dijital Çıkışlar (R1-EC0902O)
| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %QX0.0 | SERVO_ENABLE | Tüm servo enable |
| %QX0.1 | VACUUM_PUMP | Vakum pompası |
| %QX0.2 | OIL_PUMP | Yağ pompası |
| %QX0.3 | COOLING_FAN | Soğutma fanı |
| %QX0.4 | WARNING_LIGHT | Uyarı lambası |
| %QX0.5 | BUZZER | Zil |
| %QX0.6 | MARKER | İşaretleme |
| %QX0.7 | BREAKER_ENABLE | Kırıcı enable |
| %QX0.8 | HEATER_ZONE1 | Isıtıcı bölge 1 |
| %QX0.9 | HEATER_ZONE2 | Isıtıcı bölge 2 |
| %QX0.10 | HEATER_ZONE3 | Isıtıcı bölge 3 |
| %QX0.11 | CONVEYOR_FWD | Konveyör ileri |
| %QX0.12 | CONVEYOR_REV | Konveyör geri |
| %QX0.13 | SPRAY_VALVE | Sprey valfi |
| %QX0.14 | CLEAN_VALVE | Temizlik valfi |
| %QX0.15 | LIGHT_CURTAIN | Işık perdesi reset |

## 7. Delta MS300 Konveyör Sürücü

### 7.1 Konfigürasyon
| Özellik | Değer |
|---------|-------|
| Sürücü Model | MS300-xxx |
| EtherCAT Kart | CMM-EC01 |
| Motor Gücü | 0.75 kW |
| Kontrol Modu | V/F veya SLV |

### 7.2 Parametre Ayarları
```
00-00: Kontrol Modu = 0 (V/F)
00-10: Maksimum Frekans = 60 Hz
01-00: Motor Gücü = 0.75 kW
01-01: Motor Voltajı = 220 V
01-02: Motor Akımı = 3.5 A
05-00: EtherCAT Node ID = 7
```

## 8. Leuze IS 218 Sensörler

### 8.1 Teknik Özellikler
| Özellik | Değer |
|---------|-------|
| Model | IS 218 Series |
| Boyut | M18 x 1 |
| Algılama Mesafesi | 8 mm (nominal) |
| Çıkış | PNP NO/NC (seçilebilir) |
| Koruma | IP67 |
| Kirlenme Toleransı | Yüksek |
| Bağlantı | M12 Konnektör (4-pin) |

### 8.2 Sensör Yerleşimi
| Konum | Sensör | Fonksiyon |
|-------|--------|-----------|
| X+ | IS 218 | X +limit |
| X- | IS 218 | X -limit |
| X-H | IS 218 | X home |
| Y+ | IS 218 | Y +limit |
| Y- | IS 218 | Y -limit |
| Y-H | IS 218 | Y home |
| Z+ | IS 218 | Z +limit |
| Z-H | IS 218 | Z home |

## 9. Kablolama

### 9.1 EtherCAT Kablolama
| Özellik | Değer |
|---------|-------|
| Kablo Tipi | CAT5e Shielded (STP) |
| Bağlayıcı | RJ45 |
| Maks. Uzunluk | 100 m (node arası) |
| Topoloji | Line (Daisy-chain) |

### 9.2 Güç Kablolama
| Eksen | Kablo Kesiti | Maks. Uzunluk |
|-------|--------------|---------------|
| X (4.5kW) | 4 mm² | 15 m |
| Y (2.0kW) | 2.5 mm² | 12 m |
| Z (1.0kW) | 1.5 mm² | 10 m |

### 9.3 Encoder Kablolama
**Kablo Tipi:** Shielded twisted pair (STP)  
**Maks. Uzunluk:** 20 m

## 10. Konfigürasyon Yazılımı

### 10.1 Delta ISPSoft (NC300 Programlama)
1. ISPSoft'u açın
2. Yeni proje oluşturun (NC300 seçin)
3. EtherCAT konfigürasyonunu ekleyin
4. Eksen parametrelerini ayarlayın
5. G-kod yorumlayıcıyı yapılandırın
6. Programı derleyip yükleyin

### 10.2 ASDA-Soft (Servo Ayarlama)
1. ASDA-Soft'u açın
2. USB ile sürücüye bağlanın
3. Parametreleri yükleyin
4. Auto-tuning II çalıştırın
5. Parametreleri EEPROM'a kaydedin

### 10.3 DiaDesigner (HMI Tasarımı)
1. DiaDesigner'ı açın
2. DOP-110CS şablonunu seçin
3. NC300 ile haberleşmeyi ayarlayın (Ethernet)
4. Ekranları tasarlayın
5. Projeyi HMI'ye yükleyin

## 11. Test Prosedürü

### 11.1 Ön Testler
- [ ] Tüm EtherCAT bağlantılarını kontrol edin
- [ ] Güç kaynağı gerilimini ölçün (220/400VAC)
- [ ] Topraklamayı kontrol edin (<10Ω)
- [ ] STO devresini test edin

### 11.2 EtherCAT Başlangıç
- [ ] NC300'u açın
- [ ] EtherCAT slave'leri otomatik tanıma
- [ ] Tüm slave'lerin "OP" durumunda olduğunu doğrulayın
- [ ] Cycle time'ı kontrol edin (100μs)

### 11.3 Servo Testi
- [ ] Servo ON komutu gönderin
- [ ] Jog modunda her ekseni test edin
- [ ] Auto-tuning II çalıştırın
- [ ] Referans noktasına gönderin (homing)

### 11.4 E-Cam Testi (Lamine Kesim)
- [ ] E-Cam profilini yükleyin
- [ ] Alt ve üst eksen senkronizasyonunu test edin
- [ ] Kesim kalitesini kontrol edin

### 11.5 I/O Testi
- [ ] Tüm limit switch'leri test edin
- [ ] Dijital çıkışları tek tek aktifleştirin
- [ ] Sensör okumalarını doğrulayın

## 12. Malzeme Listesi (BOM)

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | Delta NC300 | NC300-XXX | 1 |
| 2 | Delta HMI | DOP-110CS | 1 |
| 3 | Delta Servo Sürücü 4.5kW | ASD-A3-4523-E | 1 |
| 4 | Delta Servo Motor 4.5kW | ECMA-L11845 | 1 |
| 5 | Delta Servo Sürücü 2.0kW | ASD-A3-2023-E | 2 |
| 6 | Delta Servo Motor 2.0kW | ECMA-E11320 | 2 |
| 7 | Delta Servo Sürücü 1.0kW | ASD-A3-1023-E | 1 |
| 8 | Delta Servo Motor 1.0kW Frenli | ECMA-C11010 | 1 |
| 9 | Delta Servo Sürücü 1.5kW | ASD-A3-1523-E | 1 |
| 10 | Delta Servo Motor 1.5kW IP67 | ECMA-E11315 | 1 |
| 11 | Delta R1-EC Bus Coupler | R1-EC | 1 |
| 12 | Delta R1-EC Dijital Giriş | R1-EC0902D | 3 |
| 13 | Delta R1-EC Dijital Çıkış | R1-EC0902O | 3 |
| 14 | Delta MS300 AC Sürücü | MS300-xxx | 1 |
| 15 | Delta EtherCAT Kart | CMM-EC01 | 1 |
| 16 | Leuze Sensör | IS 218 Series | 8 |
| 17 | Pilz Güvenlik Rölesi | PNOZ X2.8P | 1 |
| 18 | EtherCAT Kablo | CAT5e STP | 20 m |
| 19 | E-Stop Butonu | Schneider XB4 | 2 |