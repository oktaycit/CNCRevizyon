# GFB60-30RE-S Wire List

**Proje:** LiSEC GFB-60/30RE CNC Revizyon  
**Tarih:** 2026-04-09  
**Amac:** Kablo numaralandirma ve saha cekim listesi

---

## 1. Guc ve Besleme Kablolari

| Wire ID | Nereden | Nereye | Sinyal/Gerilim | Kablo |
|---------|---------|--------|----------------|-------|
| W001 | Ana giris L1/L2/L3/N/PE | Q1 ana salter | 3F AC giris | 4G10 mm2 |
| W002 | Q1 | K1 kontaktor | 3F AC hat | 4G10 mm2 |
| W003 | K1 | PS1 AC input | AC besleme | 3G2.5 mm2 |
| W004 | F2 | X2.1 | 24VDC NC300 dagitimi | 2G2.5 mm2 |
| W005 | X2.1 | U1 NC300 +24V | 24VDC | 2G2.5 mm2 |
| W006 | 0V BUS | X2.2 | 0VDC ortak dagitim | 2G2.5 mm2 |
| W006A | X2.2 | U1 NC300 0V | 0VDC | 2G2.5 mm2 |
| W007 | PS1 +24V | F6 | 24VDC HMI fuse besleme | 2G1.5 mm2 |
| W008 | F6 | X2.3 | 24VDC HMI dagitimi | 2G1.5 mm2 |
| W009 | X2.4 | U2 DOP-110CS -V | 0VDC | 2G1.5 mm2 |
| W010 | PS1 +24V | F3 | 24VDC R1-EC fuse besleme | 2G1.5 mm2 |
| W011 | F3 | X2.5 | 24VDC R1-EC dagitimi | 2G1.5 mm2 |
| W012 | X2.6 | U50 R1-EC01 GND | 0VDC | 2G1.5 mm2 |
| W016 | F4 | X2.7 | 24VDC AUX/Sensor dagitimi | 2G1.5 mm2 |
| W017 | X2.8 | X12.2 | 0VDC AUX dagitimi | 2G1.5 mm2 |
| W013 | PE bara | U1 FG | Koruma topragi | 1x2.5 mm2 GNYE |
| W014 | PE bara | U2 FG | Koruma topragi | 1x2.5 mm2 GNYE |
| W015 | PE bara | U50 PE | Koruma topragi | 1x2.5 mm2 GNYE |

---

## 2. Servo Besleme ve Motor Kablolari

| Wire ID | Nereden | Nereye | Sinyal/Gerilim | Kablo |
|---------|---------|--------|----------------|-------|
| W101 | K1 | U41 P1 R/S/T | X servo AC | 4G6 mm2 |
| W102 | U41 P2 U/V/W/FG | M41 | X motor gucu | 4G4 shielded |
| W103 | K1 | U42 P1 R/S/T | Y servo AC | 4G4 mm2 |
| W104 | U42 P2 U/V/W/FG | M42 | Y motor gucu | 4G2.5 shielded |
| W105 | K1 | U43 P1 R/S/T | Alt servo AC | 4G4 mm2 |
| W106 | U43 P2 U/V/W/FG | M43 | Alt motor gucu | 4G2.5 shielded |
| W107 | K1 | U44 P1 R/L1-S/L2 | Z servo AC | 3G2.5 mm2 |
| W108 | U44 P2 U/V/W/FG | M44 | Z motor gucu | 4G1.5 shielded |
| W109 | K1 | U45 P1 R/L1-S/L2 | CNC servo AC | 3G2.5 mm2 |
| W110 | U45 P2 U/V/W/FG | M45 | CNC motor gucu | 4G1.5 shielded |
| W111 | +24VDC | Z motor fren + | Fren besleme + | 2x0.75 mm2 |
| W112 | U44 CN1 DO_5 BRK | Z motor fren - | Fren kontrol | 2x0.75 mm2 |

---

## 3. Safety ve STO Kablolari

| Wire ID | Nereden | Nereye | Sinyal | Kablo |
|---------|---------|--------|--------|-------|
| W201 | PS1 +24V | K10 A1 | Safety besleme + | 2x1.5 mm2 |
| W202 | PS1 0V | K10 A2 | Safety besleme - | 2x1.5 mm2 |
| W203 | K10 S11/S12 | S0 E-STOP | E-STOP CH1/CH2 | 2x2x0.75 |
| W204 | K10 | S1 door switch | Door safety | 2x2x0.75 |
| W205 | K10 S52 | S2 reset | Reset | 2x0.75 |
| W206 | X11.1-2 | U41 CN1-29/30 | X STO1/STO2 | 2x2x0.75 shielded |
| W207 | X11.3-4 | U42 CN1-29/30 | Y STO1/STO2 | 2x2x0.75 shielded |
| W208 | X11.5-6 | U43 CN1-29/30 | Alt STO1/STO2 | 2x2x0.75 shielded |
| W209 | X11.7-8 | U44 CN1-29/30 | Z STO1/STO2 | 2x2x0.75 shielded |
| W210 | X11.9-10 | U45 CN1-29/30 | CNC STO1/STO2 | 2x2x0.75 shielded |
| W211 | 0V common | U41/U42/U43/U44/U45 CN1-43 | STO_COM | 1x0.75 mm2 |

---

## 4. EtherCAT ve Network Kablolari

| Wire ID | Nereden | Nereye | Sinyal | Kablo |
|---------|---------|--------|--------|-------|
| W301 | U1 NC300 CN1 | U41 CN3 | EtherCAT OUT | CAT6 STP |
| W302 | U41 CN6 | U42 CN3 | EtherCAT | CAT6 STP |
| W303 | U42 CN6 | U43 CN3 | EtherCAT | CAT6 STP |
| W304 | U43 CN6 | U44 CN3 | EtherCAT | CAT6 STP |
| W305 | U44 CN6 | U45 CN3 | EtherCAT | CAT6 STP |
| W306 | U45 CN6 | U50 R1-EC IN | EtherCAT | CAT6 STP |
| W307 | U50 R1-EC OUT | U1 NC300 CN2 | EtherCAT loop | CAT6 STP |
| W308 | U1 NC300 CN3 | U2 DOP-110CS ETH | HMI Ethernet | CAT5e/CAT6 |

---

## 5. Sensor ve I/O Kablolari

| Wire ID | Nereden | Nereye | Sinyal | Kablo |
|---------|---------|--------|--------|-------|
| W401 | S11 | U51 DI_0 | X+LIMIT | 4x0.34 shielded |
| W402 | S12 | U51 DI_1 | X-LIMIT | 4x0.34 shielded |
| W403 | S10 | U51 DI_2 | X-HOME | 4x0.34 shielded |
| W404 | S21 | U51 DI_3 | Y+LIMIT | 4x0.34 shielded |
| W405 | S22 | U51 DI_4 | Y-LIMIT | 4x0.34 shielded |
| W406 | S20 | U51 DI_5 | Y-HOME | 4x0.34 shielded |
| W407 | S31 | U51 DI_6 | Z+LIMIT | 4x0.34 shielded |
| W408 | Z- limit sensor | U51 DI_7 | Z-LIMIT | 4x0.34 shielded |
| W409 | S30 | U51 DI_8 | Z-HOME | 4x0.34 shielded |
| W410 | S41 | U51 DI_9 | ALT+LIMIT | 4x0.34 shielded |
| W411 | S42 | U51 DI_10 | ALT-LIMIT | 4x0.34 shielded |
| W412 | S40 | U51 DI_11 | ALT-HOME | 4x0.34 shielded |
| W413 | K10 aux fb | U51 DI_12 | E-STOP1 | 2x0.75 |
| W414 | K10 aux fb | U51 DI_13 | E-STOP2 | 2x0.75 |
| W415 | S1 aux | U51 DI_14 | DOOR_OPEN | 2x0.75 |
| W416 | S51 | U51 DI_15 | VACUUM_OK | 4x0.34 shielded |
| W417 | S50 #1 | U51 DI_16 / X20.17 | GLASS_DETECT1 | 4x0.34 shielded |
| W417A | S50 #2 | U51 DI_17 / X20.18 | GLASS_DETECT2 | 4x0.34 shielded |
| W451 | U53 DO_0 | Servo enable role/klemens | SERVO_ENABLE | 2x0.75 |
| W452 | U53 DO_1 | Vakum pompa kontaktoru | VACUUM_PUMP | 2x0.75 |
| W453 | U53 DO_2 | Yag pompa kontaktoru | OIL_PUMP | 2x0.75 |
| W454 | U53 DO_3 | Fan kontaktoru | COOLING_FAN | 2x0.75 |
| W455 | U53 DO_4 | Uyari lambasi | WARNING_LIGHT | 2x0.75 |
| W456 | U53 DO_5 | Buzzer | BUZZER | 2x0.75 |
| W457 | U53 DO_7 / X40.8 | Kirici enable | BREAKER_ENABLE | 2x0.75 |
| W458 | U53 DO_10 / X40.11 | Konveyor ileri | CONVEYOR_FWD | 2x0.75 |
| W459 | U53 DO_11 / X40.12 | Konveyor geri | CONVEYOR_REV | 2x0.75 |

---

## 6. Etiketleme Kurali

- Guc kablolari: `W1xx`
- Safety kablolari: `W2xx`
- Haberlesme kablolari: `W3xx`
- Sensor kablolari: `W4xx`

Her kablo iki ucunda da ayni `Wire ID` ile etiketlenmelidir.
