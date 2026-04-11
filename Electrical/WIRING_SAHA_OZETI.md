# GFB60-30RE-S Wiring Saha Ozeti

**Proje:** LiSEC GFB-60/30RE CNC Revizyon  
**Tarih:** 2026-04-09  
**Amac:** Saha montaj, kablo cekimi, terminal kontrolu ve devreye alma sirasinda hizli referans

---

## 1. Sistem Ozeti

Bu projede ana kontrol yapisi asagidaki gibidir:

- `U1`: Delta `NC300-E` CNC kontrolor
- `U2`: Delta `DOP-110CS` HMI
- `U41`: X ekseni servo surucu `ASD-A3-4523-E` + motor `ECMA-L11845`
- `U42`: Y ekseni servo surucu `ASD-A3-2023-E` + motor `ECMA-E11320`
- `U43`: Alt ekseni servo surucu `ASD-A3-2023-E` + motor `ECMA-E11320`
- `U44`: Z ekseni servo surucu `ASD-A3-1023-E` + motor `ECMA-C11010FS`
- `U45`: CNC/Rodaj ekseni servo surucu `ASD-A3-1523-E` + motor `ECMA-E11315`
- `U50`: Delta `R1-EC01` EtherCAT coupler
- `U51-U52`: Delta `R1-EC0902D` dijital giris modulleri
- `U53`: Delta `R1-EC0902O` dijital cikis modulu
- `K10`: Pilz `PNOZ X2.8P` safety relay

Not: Bazi ust dokumanlarda `3 DI + 3 DO` modul bilgisi geciyor, ancak mevcut wiring ve BOM referanslarinda saha icin en tutarli yapi `2 x DI + 1 x DO` olarak gorunuyor. Bu ozet bu yapıya gore hazirlanmistir.

---

## 2. Ana Wiring Topolojisi

```text
3F AC Giris
  -> Q1 Ana Salter
  -> K1 Kontaktor
  -> PS1 24VDC Power Supply
      -> U1 NC300
      -> U2 DOP-110CS
      -> U50 R1-EC01
      -> Sensorler
      -> K10 Pilz Safety

NC300 EtherCAT OUT
  -> X Servo
  -> Y Servo
  -> Alt Servo
  -> Z Servo
  -> CNC Servo
  -> R1-EC Coupler
  -> NC300 EtherCAT IN

E-STOP + Door Safety
  -> K10 Pilz PNOZ
  -> STO dagitimi
  -> Tum servo STO1/STO2
```

---

## 3. Saha Kablosu Ozet Listesi

| Hat | Nereden | Nereye | Tip | Onerilen kablo |
|-----|---------|--------|-----|----------------|
| AC-01 | Ana giris | Q1 | 3F guc | 4G10 mm2 |
| AC-02 | Q1/K1 | X servo U41 P1 | 3F 400VAC | 4G6 mm2 |
| AC-03 | Q1/K1 | Y servo U42 P1 | 3F 400VAC | 4G4 mm2 |
| AC-04 | Q1/K1 | Alt servo U43 P1 | 3F 400VAC | 4G4 mm2 |
| AC-05 | Q1/K1 | Z servo U44 P1 | 1F 230VAC | 3G2.5 mm2 |
| AC-06 | Q1/K1 | CNC servo U45 P1 | 1F 230VAC | 3G2.5 mm2 |
| DC-01 | PS1 | NC300 U1 | 24VDC | 2G2.5 mm2 |
| DC-02 | PS1 | HMI U2 | 24VDC | 2G1.5 mm2 |
| DC-03 | PS1 | R1-EC U50 | 24VDC | 2G1.5 mm2 |
| DC-04 | PS1 | Sensor ortak dagitim | 24VDC | 2G1.5 mm2 |
| SAFE-01 | K10 | X STO | Safety | 2x2x0.75 shielded |
| SAFE-02 | K10 | Y STO | Safety | 2x2x0.75 shielded |
| SAFE-03 | K10 | Alt STO | Safety | 2x2x0.75 shielded |
| SAFE-04 | K10 | Z STO | Safety | 2x2x0.75 shielded |
| SAFE-05 | K10 | CNC STO | Safety | 2x2x0.75 shielded |
| ETH-01 | NC300 CN1 | U41 CN3 | EtherCAT | CAT6 STP |
| ETH-02 | U41 CN6 | U42 CN3 | EtherCAT | CAT6 STP |
| ETH-03 | U42 CN6 | U43 CN3 | EtherCAT | CAT6 STP |
| ETH-04 | U43 CN6 | U44 CN3 | EtherCAT | CAT6 STP |
| ETH-05 | U44 CN6 | U45 CN3 | EtherCAT | CAT6 STP |
| ETH-06 | U45 CN6 | U50 IN | EtherCAT | CAT6 STP |
| ETH-07 | U50 OUT | NC300 CN2 | EtherCAT loop | CAT6 STP |
| NET-01 | NC300 CN3 | DOP-110CS ETH | Ethernet | CAT5e/CAT6 |

---

## 4. Eksen Bazli Wiring Ozeti

### X Ekseni

| Baglanti | Terminal |
|----------|----------|
| Surucu modeli | `U41 ASD-A3-4523-E` |
| Motor modeli | `M41 ECMA-L11845` |
| AC giris | `P1: R/L1, S/L2, T/L3` |
| Motor cikisi | `P2: U, V, W, FG` |
| EtherCAT IN | `CN3` |
| EtherCAT OUT | `CN6` |
| STO | `CN1-29 STO1`, `CN1-30 STO2`, `CN1-43 STO_COM` |
| Kontrol besleme | `CN1-9 +24V`, `CN1-44 COM+` |

### Y Ekseni

| Baglanti | Terminal |
|----------|----------|
| Surucu modeli | `U42 ASD-A3-2023-E` |
| Motor modeli | `M42 ECMA-E11320` |
| AC giris | `P1: R/L1, S/L2, T/L3` |
| Motor cikisi | `P2: U, V, W, FG` |
| EtherCAT IN/OUT | `CN3 / CN6` |
| STO | `CN1-29`, `CN1-30`, `CN1-43` |

### Alt Ekseni

| Baglanti | Terminal |
|----------|----------|
| Surucu modeli | `U43 ASD-A3-2023-E` |
| Motor modeli | `M43 ECMA-E11320` |
| AC giris | `P1: R/L1, S/L2, T/L3` |
| Motor cikisi | `P2: U, V, W, FG` |
| EtherCAT IN/OUT | `CN3 / CN6` |
| STO | `CN1-29`, `CN1-30`, `CN1-43` |

### Z Ekseni

| Baglanti | Terminal |
|----------|----------|
| Surucu modeli | `U44 ASD-A3-1023-E` |
| Motor modeli | `M44 ECMA-C11010FS` |
| AC giris | `P1: R/L1, S/L2` |
| Motor cikisi | `P2: U, V, W, FG` |
| EtherCAT IN/OUT | `CN3 / CN6` |
| STO | `CN1-29`, `CN1-30`, `CN1-43` |
| Fren kontrolu | `DO_5 BRK` |
| Fren besleme | `+24V -> bobin +`, `BRK cikisi -> bobin -` |

### CNC/Rodaj Ekseni

| Baglanti | Terminal |
|----------|----------|
| Surucu modeli | `U45 ASD-A3-1523-E` |
| Motor modeli | `M45 ECMA-E11315` |
| AC giris | `P1: R/L1, S/L2` |
| Motor cikisi | `P2: U, V, W, FG` |
| EtherCAT IN/OUT | `CN3 / CN6` |
| STO | `CN1-29`, `CN1-30`, `CN1-43` |

---

## 5. Safety ve STO Dagitimi

### Safety girisleri

| Eleman | Tip | Not |
|--------|-----|-----|
| `S0` E-STOP | 2NC | Iki kanalli baglanti |
| `S1` Safety door | 2NC + 1NO | Emniyet kapisi |
| `S2` Reset | NO | Manual reset |

### Pilz baglantisi

| Pilz terminali | Fonksiyon |
|----------------|-----------|
| `A1 / A2` | 24VDC besleme |
| `S11 / S12` | E-STOP kanal girisleri |
| `S34` | Test pulse |
| `S52` | Reset girisi |
| `13-14` | Safety output 1 |
| `23-24` | Safety output 2 |
| `33-34` | Safety output 3 |
| `41-42` | Yardimci feedback |

### STO terminal dagitimi

| Terminal | Hedef |
|----------|-------|
| `X11.1-2` | X ekseni STO1/STO2 |
| `X11.3-4` | Y ekseni STO1/STO2 |
| `X11.5-6` | Alt ekseni STO1/STO2 |
| `X11.7-8` | Z ekseni STO1/STO2 |
| `X11.9-10` | CNC ekseni STO1/STO2 |

Not: STO hatlari shielded twisted pair kablo ile cekilmeli ve guc kablolarindan fiziksel olarak ayrilmalidir.

---

## 6. EtherCAT ve Network Sirasi

### EtherCAT halka/daisy-chain

```text
NC300 CN1
 -> U41 X CN3
 -> U41 CN6 / U42 CN3
 -> U42 CN6 / U43 CN3
 -> U43 CN6 / U44 CN3
 -> U44 CN6 / U45 CN3
 -> U45 CN6 / U50 R1-EC IN
 -> U50 R1-EC OUT
 -> NC300 CN2
```

### Ethernet

| Baglanti | Aciklama |
|----------|----------|
| `NC300 CN3 -> DOP-110CS ETH` | Operator panel haberlesmesi |
| `NC300` | `192.168.1.10` |
| `DOP-110CS` | `192.168.1.11` |

---

## 7. Saha I/O Esleme Tablosu

### Dijital girisler

| Adres | Sinyal | Saha cihazı |
|-------|--------|-------------|
| `%IX0.0` | X+LIMIT | X pozitif limit sensori |
| `%IX0.1` | X-LIMIT | X negatif limit sensori |
| `%IX0.2` | X-HOME | X home sensori |
| `%IX0.3` | Y+LIMIT | Y pozitif limit sensori |
| `%IX0.4` | Y-LIMIT | Y negatif limit sensori |
| `%IX0.5` | Y-HOME | Y home sensori |
| `%IX0.6` | Z+LIMIT | Z pozitif limit sensori |
| `%IX0.7` | Z-LIMIT | Z negatif limit sensori |
| `%IX0.8` | Z-HOME | Z home sensori |
| `%IX0.9` | ALT+LIMIT | Alt pozitif limit sensori |
| `%IX0.10` | ALT-LIMIT | Alt negatif limit sensori |
| `%IX0.11` | ALT-HOME | Alt home sensori |
| `%IX0.12` | E-STOP1 | Safety zinciri kanal 1 |
| `%IX0.13` | E-STOP2 | Safety zinciri kanal 2 |
| `%IX0.14` | DOOR_OPEN | Safety door durumu |
| `%IX0.15` | VACUUM_OK | Vakum geri bildirimi |
| `%IX1.0` | GLASS_DETECT | Cam algilama sensori |
| `%IX1.1` | OIL_LEVEL | Yag seviye bilgisi |
| `%IX1.2` | AIR_PRESSURE | Hava basinci OK |
| `%IX1.3` | BREAKER_OK | Kirici hazir bilgisi |

### Dijital cikislar

| Adres | Sinyal | Yük |
|-------|--------|-----|
| `%QX0.0` | SERVO_ENABLE | Servo enable mantigi |
| `%QX0.1` | VACUUM_PUMP | Vakum pompa kontaktoru |
| `%QX0.2` | OIL_PUMP | Yag pompa cikisi |
| `%QX0.3` | COOLING_FAN | Fan |
| `%QX0.4` | WARNING_LIGHT | Uyari lambasi |
| `%QX0.5` | BUZZER | Sesli ikaz |
| `%QX0.6` | MARKER | Isaretleme |
| `%QX0.7` | BREAKER_ENABLE | Kirici enable |
| `%QX0.8` | HEATER_ZONE1 | Isitici 1 |
| `%QX0.9` | HEATER_ZONE2 | Isitici 2 |
| `%QX0.10` | HEATER_ZONE3 | Isitici 3 |
| `%QX0.11` | CONVEYOR_FWD | Konveyor ileri |
| `%QX0.12` | CONVEYOR_REV | Konveyor geri |
| `%QX0.13` | SPRAY_VALVE | Sprey valfi |
| `%QX0.14` | CLEAN_VALVE | Temizlik valfi |
| `%QX0.15` | LIGHT_CURTAIN | Isik perdesi reset |

---

## 8. Terminal Kontrol Ozeti

| Terminal grubu | Islev |
|----------------|-------|
| `X1` | AC giris terminalleri |
| `X2` | 24VDC dagitim |
| `X10` | Safety input terminali |
| `X11` | STO output terminali |
| `X20` | DI terminal grubu 1 |
| `X30` | DI terminal grubu 2 |
| `X40` | DO terminal grubu |
| `X30/X31` | EtherCAT ve network gecisleri |
| `PE1 / X6` | Koruma topraklamasi |

Saha kontrolunde asagidaki sirayla ilerlenmesi onerilir:

1. PE ve govde topraklarini kontrol et.
2. 24VDC dagitimini sigorta cikislarindan olc.
3. Safety zincirini Pilz uzerinden dogrula.
4. STO cikislarini tum eksenlerde terminal bazinda kontrol et.
5. EtherCAT sirasini fiziksel kablo rotasina gore etiketle.
6. Sensor DI adreslerini tek tek aktive ederek dogrula.
7. Aktuator DO cikislarini yuk bagli degilken test et.

---

## 9. Saha Etiketleme Onerisi

Kablo etiketleri icin asagidaki formati kullan:

- `PWR-X-01`: guc hatti
- `ECAT-03`: EtherCAT hatti
- `STO-Z-01`: safety hatti
- `DI-XH-01`: X home sensori
- `DO-VAC-01`: vakum cikisi
- `BRK-Z-01`: Z freni

Her iki uc ayni kodla etiketlenmeli. Servo kablolarinda ayrica eksen adi, terminal ve gerilim bilgisi yazilmasi tavsiye edilir.

---

## 10. Referans Dokumanlar

- `Electrical/WIRING_REFERENCE.md`
- `Delta/Servo/Delta_Servo_Integration.md`
- `Electrical/BOM/GFB60-30RE-S_BOM.md`
- `Electrical/SCHEMATIC_COMPLETION_SUMMARY.md`
- `CAD/FreeCAD/05_Electronics/Electrical_Connections_Summary.md`
