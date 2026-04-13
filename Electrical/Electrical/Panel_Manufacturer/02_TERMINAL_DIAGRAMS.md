# GFB60-30RE-S Klemens ve Terminal Strip Semalari

**Proje:** LiSEC GFB-60/30RE CNC Revizyon
**Belge No:** ELEC-TERM-001
**Revizyon:** 4.1
**Tarih:** 2026-04-11

---

## 1. Terminal Strip Genel Plan

```
                    PANO ICI TERMINAL YERLESIMI
                    
+--------+   +--------+   +--------+   +--------+   +--------+   +--------+
|   X1   |   |   X2   |   |   X10  |   |   X11  |   |   X12  |   |   PE   |
| AC IN  |   | 24VDC  |   | SAF IN |   | STO OUT|   |  AUX   |   |  BARA  |
| 5-pin  |   | 8-pin  |   | 6-pin  |   | 10-pin |   | 5-pin  |   | 10-pin |
+--------+   +--------+   +--------+   +--------+   +--------+   +--------+

+-------------+   +-------------+   +-------------+
|     X20     |   |     X30     |   |     X40     |
|   DI #1     |   |   DI #2     |   |     DO      |
|   32-pin    |   |   32-pin    |   |   32-pin    |
|   (U51)     |   |   (U52)     |   |   (U53)     |
+-------------+   +-------------+   +-------------+
```

---

## 2. X1 - AC Giris Terminal Strip

**Tip:** Phoenix Contact MSTB 2.5/5-STF-5.08
**Konum:** Pano alt sol, gland plakasi yaninda
**Renk:** Gri

```
    X1 - AC GIRIS TERMINAL
    ======================
    
    +-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   |
    +-----+-----+-----+-----+-----+
    | L1  | L2  | L3  | N   | PE  |
    +-----+-----+-----+-----+-----+
    
    | Pin | Signal | From       | To           | Wire  | Notes       |
    |-----|---------|------------|--------------|-------|-------------|
    | 1   | L1      | Grid       | Q1 L1        | W001  | 10mm2       |
    | 2   | L2      | Grid       | Q1 L2        | W001  | 10mm2       |
    | 3   | L3      | Grid       | Q1 L3        | W001  | 10mm2       |
    | 4   | N       | Grid       | Q1 N         | W001  | 10mm2       |
    | 5   | PE      | Grid PE    | PE Bara      | W001  | 10mm2 GNYE  |
```

---

## 3. X2 - 24VDC Dagitim Terminal Strip

**Tip:** Phoenix Contact MSTB 2.5/8-STF-5.08
**Konum:** DIN Ray 1, sigortalardan sonra
**Renk:** Mavi bazli

```
    X2 - 24VDC DAGITIM TERMINAL
    ===========================
    
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | +24 |  0V | +24 |  0V | +24 |  0V | +24 |  0V |
    | NC  | COM | HMI | COM | R1  | COM | AUX | COM |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    [RED] [BLU] [RED] [BLU] [RED] [BLU] [RED] [BLU]
    
    | Pin | Signal   | From         | To             | Wire  | Notes    |
    |-----|----------|--------------|----------------|-------|----------|
    | 1   | +24V NC  | F2 OUT       | U1 NC300 +24V  | W005  | 2.5mm2   |
    | 2   | 0V COM   | 0V BUS       | U1 NC300 0V    | W006A | 2.5mm2   |
    | 3   | +24V HMI | F6 OUT       | U2 DOP +V      | W008A | saha cikisi |
    | 4   | 0V COM   | 0V BUS       | U2 DOP -V      | W009  | saha cikisi |
    | 5   | +24V R1  | F3 OUT       | U50 R1-EC V+   | W011  | 1.5mm2   |
    | 6   | 0V COM   | 0V BUS       | U50 R1-EC GND  | W012  | 1.5mm2   |
    | 7   | +24V AUX | F4 OUT       | X12.1 / Aux    | W016  | 1.5mm2   |
    | 8   | 0V COM   | 0V BUS       | X12.2 / Aux    | W017  | 1.5mm2   |
```

---

## 4. X10 - Safety Input Terminal Strip

**Tip:** Phoenix Contact MSTB 2.5/6-STF-5.08
**Konum:** DIN Ray 1, X2 yaninda
**Renk:** Sari (safety)

```
    X10 - SAFETY INPUT TERMINAL
    ============================
    
    +-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   |
    +-----+-----+-----+-----+-----+-----+
    | +24 |  0V | E-S | E-S | DOOR| RES |
    | SAF | SAF | CH1 | CH2 | SW  | ET  |
    +-----+-----+-----+-----+-----+-----+
    [YEL] [YEL] [YEL] [YEL] [YEL] [YEL]
    
    | Pin | Signal    | From          | To             | Wire  | Notes     |
    |-----|-----------|---------------|----------------|-------|-----------|
    | 1   | +24V SAF  | PS1 +24V      | K10 A1         | W201  | Safety    |
    | 2   | 0V SAF    | PS1 0V        | K10 A2         | W202  | Safety    |
    | 3   | E-STOP CH1| K10 S11       | S0 E-STOP CH1  | W203  | Safety    |
    | 4   | E-STOP CH2| K10 S12       | S0 E-STOP CH2  | W203A | Safety    |
    | 5   | DOOR SW   | K10           | S1 Door Switch | W204  | Safety    |
    | 6   | RESET     | K10 S52       | S2 Reset NO    | W205  | Safety    |
```

---

## 5. X11 - STO Output Terminal Strip

**Tip:** Phoenix Contact MSTB 2.5/10-STF-5.08
**Konum:** DIN Ray 1, X10 yaninda
**Renk:** Sari (safety)

```
    X11 - STO OUTPUT TERMINAL
    =========================
    
    +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | 10  |
    +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    |STO1 |STO2 |STO1 |STO2 |STO1 |STO2 |STO1 |STO2 |STO1 |STO2 |
    | X   | X   | Y   | Y   | ALT | ALT | Z   | Z   | CNC | CNC |
    +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    [YEL] [YEL] [YEL] [YEL] [YEL] [YEL] [YEL] [YEL] [YEL] [YEL]
    
    | Pin | Signal    | From         | To              | Wire  | Notes      |
    |-----|-----------|--------------|-----------------|-------|------------|
    | 1   | X STO1    | K10 13       | U41 CN1-29      | W206  | STO X-1    |
    | 2   | X STO2    | K10 14       | U41 CN1-30      | W206B | STO X-2    |
    | 3   | Y STO1    | K10 23       | U42 CN1-29      | W207  | STO Y-1    |
    | 4   | Y STO2    | K10 24       | U42 CN1-30      | W207B | STO Y-2    |
    | 5   | ALT STO1  | K10 33       | U43 CN1-29      | W208  | STO Alt-1  |
    | 6   | ALT STO2  | K10 34       | U43 CN1-30      | W208B | STO Alt-2  |
    | 7   | Z STO1    | K10 13       | U44 CN1-29      | W209  | STO Z-1    |
    | 8   | Z STO2    | K10 14       | U44 CN1-30      | W209B | STO Z-2    |
    | 9   | CNC STO1  | K10 23       | U45 CN1-29      | W210  | STO CNC-1  |
    | 10  | CNC STO2  | K10 24       | U45 CN1-30      | W210B | STO CNC-2  |
```

---

## 6. X20 - DI Terminal Strip #1 (U51)

**Tip:** Phoenix Contact MSTB 2.5/16-STF-5.08 x 2 (32-pin toplam)
**Konum:** DIN Ray 3
**Renk:** Gri (standart)
**Bagli Modul:** U51 R1-EC0902D

```
    X20 - DIGITAL INPUT TERMINAL #1 (U51)
    =====================================
    
    BLOK 1 (DI_0 - DI_15):
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |X+LM |X-LM |X-HM |Y+LM |Y-LM |Y-HM |Z+LM |Z-LM |
    |DI0  |DI1  |DI2  |DI3  |DI4  |DI5  |DI6  |DI7  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 9   | 10  | 11  | 12  | 13  | 14  | 15  | 16  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |Z-HM |ALT+ |ALT- |ALT-H|ES1  |ES2  |DOOR |VAC  |
    |DI8  |DI9  |DI10 |DI11 |DI12 |DI13 |DI14 |DI15 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    
    BLOK 2 (DI_16 - DI_31):
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 17  | 18  | 19  | 20  | 21  | 22  | 23  | 24  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |GLS1 |GLS2 |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DI16 |DI17 |DI18 |DI19 |DI20 |DI21 |DI22 |DI23 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 25  | 26  | 27  | 28  | 29  | 30  | 31  | 32  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DI24 |DI25 |DI26 |DI27 |DI28 |DI29 |DI30 |DI31 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    
    | Pin | Signal     | From          | Wire  | Notes          |
    |-----|------------|---------------|-------|----------------|
    | 1   | X+ LIMIT   | S11           | W401  | Leuze IS218    |
    | 2   | X- LIMIT   | S12           | W402  | Leuze IS218    |
    | 3   | X HOME     | S10           | W403  | Leuze IS218    |
    | 4   | Y+ LIMIT   | S21           | W404  | Leuze IS218    |
    | 5   | Y- LIMIT   | S22           | W405  | Leuze IS218    |
    | 6   | Y HOME     | S20           | W406  | Leuze IS218    |
    | 7   | Z+ LIMIT   | S31           | W407  | Leuze IS218    |
    | 8   | Z- LIMIT   | Z- Sensor     | W408  | Leuze IS218    |
    | 9   | Z HOME     | S30           | W409  | Leuze IS218    |
    | 10  | ALT+ LIMIT | S41           | W410  | Leuze IS218    |
    | 11  | ALT- LIMIT | S42           | W411  | Leuze IS218    |
    | 12  | ALT HOME   | S40           | W412  | Leuze IS218    |
    | 13  | E-STOP FB1 | K10 Aux       | W413  | Safety feedback|
    | 14  | E-STOP FB2 | K10 Aux       | W414  | Safety feedback|
    | 15  | DOOR OPEN  | S1 Aux        | W415  | Door status    |
    | 16  | VACUUM OK  | S51           | W416  | Vacuum sensor  |
    | 17  | GLASS DET1 | S50 #1        | W417  | Glass detect   |
    | 18  | GLASS DET2 | S50 #2        | W417A | Glass detect   |
    | 19-32| SPARE     | -             | -     | Reserved       |
```

---

## 7. X30 - DI Terminal Strip #2 (U52)

**Tip:** Phoenix Contact MSTB 2.5/16-STF-5.08 x 2 (32-pin toplam)
**Konum:** DIN Ray 3
**Renk:** Gri
**Bagli Modul:** U52 R1-EC0902D

```
    X30 - DIGITAL INPUT TERMINAL #2 (U52)
    =====================================
    
    BLOK 1 (DI_0 - DI_15):
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DI0  |DI1  |DI2  |DI3  |DI4  |DI5  |DI6  |DI7  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 9   | 10  | 11  | 12  | 13  | 14  | 15  | 16  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DI8  |DI9  |DI10 |DI11 |DI12 |DI13 |DI14 |DI15 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    
    BLOK 2 (DI_16 - DI_31):
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 17  | 18  | 19  | 20  | 21  | 22  | 23  | 24  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DI16 |DI17 |DI18 |DI19 |DI20 |DI21 |DI22 |DI23 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 25  | 26  | 27  | 28  | 29  | 30  | 31  | 32  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DI24 |DI25 |DI26 |DI27 |DI28 |DI29 |DI30 |DI31 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    
    NOT: Tum pinler SPARE - gelecekteki genisleme icin reserve edilmistir.
```

---

## 8. X40 - DO Terminal Strip (U53)

**Tip:** Phoenix Contact MSTB 2.5/16-STF-5.08 x 2 (32-pin toplam)
**Konum:** DIN Ray 3
**Renk:** Gri
**Bagli Modul:** U53 R1-EC0902O (Relay Output)

```
    X40 - DIGITAL OUTPUT TERMINAL (U53)
    ====================================
    
    BLOK 1 (DO_0 - DO_15):
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SERVO|VACUM| OIL | FAN |WARN |BUZZ |SPARE|BRK_ |
    | EN  | PMP | PMP |     |LAMP |ER   |     | EN  |
    |DO0  |DO1  |DO2  |DO3  |DO4  |DO5  |DO6  |DO7  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 9   | 10  | 11  | 12  | 13  | 14  | 15  | 16  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|CNV_F|CNV_R|SPARE|SPARE|SPARE|SPARE|
    |DO8  |DO9  |DO10 |DO11 |DO12 |DO13 |DO14 |DO15 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    
    BLOK 2 (DO_16 - DO_31):
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 17  | 18  | 19  | 20  | 21  | 22  | 23  | 24  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DO16 |DO17 |DO18 |DO19 |DO20 |DO21 |DO22 |DO23 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    | 25  | 26  | 27  | 28  | 29  | 30  | 31  | 32  |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    |SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|SPARE|
    |DO24 |DO25 |DO26 |DO27 |DO28 |DO29 |DO30 |DO31 |
    +-----+-----+-----+-----+-----+-----+-----+-----+
    
    | Pin | Signal     | To               | Wire  | Notes           |
    |-----|------------|------------------|-------|-----------------|
    | 1   | SERVO_EN   | Enable relay     | W451  | All servos      |
    | 2   | VACUUM_PMP  | Vacuum pump K    | W452  | Kontaktor       |
    | 3   | OIL_PUMP    | Oil pump K       | W453  | Kontaktor       |
    | 4   | COOLING_FAN | Fan contactor    | W454  | Pano fan        |
    | 5   | WARN_LIGHT  | Warning light    | W455  | Tower light     |
    | 6   | BUZZER      | Buzzer           | W456  | Audio alarm     |
    | 7   | SPARE       | -                | -     | Reserved        |
    | 8   | BREAKER_EN  | Breaker relay    | W457  | Glass breaker   |
    | 9   | SPARE       | -                | -     | Reserved        |
    | 10  | SPARE       | -                | -     | Reserved        |
    | 11  | CNV_FWD     | Conveyor fwd K   | W458  | MS300 drive     |
    | 12  | CNV_REV     | Conveyor rev K   | W459  | MS300 drive     |
    | 13-32| SPARE     | -                | -     | Reserved        |
```

---

## 9. X12 - AUX Terminal Strip

**Tip:** Phoenix Contact MSTB 2.5/5-STF-5.08
**Konum:** DIN Ray 4
**Renk:** Gri

```
    X12 - AUX TERMINAL
    ==================
    
    +-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   |
    +-----+-----+-----+-----+-----+
    | +24 |  0V | PE  |SPARE|SPARE|
    | AUX | AUX |     |     |     |
    +-----+-----+-----+-----+-----+
    
    | Pin | Signal    | From      | Notes              |
    |-----|-----------|-----------|--------------------|
    | 1   | +24V AUX  | X2.1      | Auxiliary power    |
    | 2   | 0V AUX    | X2.2      | Auxiliary common   |
    | 3   | PE        | PE Bara   | Ground             |
    | 4   | SPARE     | -         | Reserved           |
    | 5   | SPARE     | -         | Reserved           |
```

---

## 10. PE Bara - Topraklama Terminal

**Tip:** Phoenix Contact UK 2.5 B x 10
**Konum:** DIN Ray 1 sag taraf
**Renk:** Yesil-Sari (GNYE)

```
    PE BARA - TOPRAKLAMA
    ====================
    
    +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   | 9   | 10  |
    +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    | PE  | PE  | PE  | PE  | PE  | PE  | PE  | PE  | PE  | PE  |
    |IN   |PS1  |NC   |DOP  |R1EC |X41  |X42  |X43  |X44  |X45  |
    +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
    [GRN-YEL] All pins
    
    | Pin | To            | Wire  | Notes              |
    |-----|---------------|-------|--------------------|
    | 1   | X1.5 (Grid)   | W013  | Ana giris PE       |
    | 2   | PS1 FG        | W013A | Power supply       |
    | 3   | U1 NC300 FG   | W013B | CNC controller     |
    | 4   | U2 DOP FG     | W014  | HMI                |
    | 5   | U50 R1-EC PE  | W015  | I/O coupler        |
    | 6   | U41 PE        | W102  | X servo PE         |
    | 7   | U42 PE        | W104  | Y servo PE         |
    | 8   | U43 PE        | W106  | Alt servo PE       |
    | 9   | U44 PE        | W108  | Z servo PE         |
    | 10  | U45 PE        | W110  | CNC servo PE       |
```

---

## 11. Terminal Malzeme Listesi

| Ref | Tip | Uretici | Miktar | Renk |
|-----|-----|---------|--------|------|
| X1 | MSTB 2.5/5-STF-5.08 | Phoenix Contact | 1 | Gri |
| X2 | MSTB 2.5/8-STF-5.08 | Phoenix Contact | 1 | Gri |
| X10 | MSTB 2.5/6-STF-5.08 | Phoenix Contact | 1 | Sari |
| X11 | MSTB 2.5/10-STF-5.08 | Phoenix Contact | 1 | Sari |
| X12 | MSTB 2.5/5-STF-5.08 | Phoenix Contact | 1 | Gri |
| X20 | MSTB 2.5/16-STF-5.08 | Phoenix Contact | 2 | Gri |
| X30 | MSTB 2.5/16-STF-5.08 | Phoenix Contact | 2 | Gri |
| X40 | MSTB 2.5/16-STF-5.08 | Phoenix Contact | 2 | Gri |
| PE1 | UK 2.5 B | Phoenix Contact | 10 | GNYE |

---

## 12. Klemens Montaj Notlari

1. **DIN Ray Tipi:** 35mm x 7.5mm NSYSDR2 (Schneider)
2. **Klemens Araligi:** 5.08mm standart
3. **End Block:** Her strip'in basina ve sonuna end block
4. **Jumper:** X2'de 0V ortak pinleri (2-4-6-8) jumper ile birbirine bagli
5. **Safety Klemensler:** X10 ve X11 sari renk, safety semasi uyari etiketi

---

**Belge Durumu:** FINAL
**Onaylayan:** ___________________
**Tarih:** ___________________
