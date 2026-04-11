# GFB60-30RE-S Terminalden Terminale Baglanti Listesi

**Proje:** LiSEC GFB-60/30RE CNC Revizyon  
**Tarih:** 2026-04-09  
**Amac:** Terminal, klemens ve cihaz ucu bazli baglanti kontrolu

---

## 1. 24VDC Dagitim

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `PS1 +24V` | `X2.1` | W004 | 24V ana dagitim girisi |
| `PS1 0V` | `X2.2` | W006 | 0V ana dagitim girisi |
| `X2.3` | `U1 NC300 +24V` | W005 | NC300 besleme |
| `X2.4` | `U1 NC300 0V` | W006A | NC300 0V |
| `X2.5` | `U2 DOP +V` | W008 | HMI besleme |
| `X2.6` | `U2 DOP -V` | W009 | HMI 0V |
| `X2.7` | `U50 R1-EC V+` | W011 | R1-EC besleme |
| `X2.8` | `U50 R1-EC GND` | W012 | R1-EC 0V |

---

## 2. Safety Terminal Plani

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `PS1 +24V` | `X10.1` | W201 | Safety besleme |
| `PS1 0V` | `X10.2` | W202 | Safety 0V |
| `X10.1` | `K10 A1` | W201A | Pilz besleme + |
| `X10.2` | `K10 A2` | W202A | Pilz besleme - |
| `K10 S11` | `S0 CH1` | W203 | E-STOP kanal 1 |
| `K10 S12` | `S0 CH2` | W203A | E-STOP kanal 2 |
| `K10 S52` | `S2 NO` | W205 | Reset butonu |
| `K10 13-14` | `X11.1-2` | W206A | STO grup 1 |
| `K10 23-24` | `X11.3-4` | W207A | STO grup 2 |
| `K10 33-34` | `X11.5-10` | W208A | STO grup 3 dagitim |

---

## 3. STO Cikis Dagitimi

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `X11.1` | `U41 CN1-29` | W206 | X STO1 |
| `X11.2` | `U41 CN1-30` | W206B | X STO2 |
| `X11.3` | `U42 CN1-29` | W207 | Y STO1 |
| `X11.4` | `U42 CN1-30` | W207B | Y STO2 |
| `X11.5` | `U43 CN1-29` | W208 | Alt STO1 |
| `X11.6` | `U43 CN1-30` | W208B | Alt STO2 |
| `X11.7` | `U44 CN1-29` | W209 | Z STO1 |
| `X11.8` | `U44 CN1-30` | W209B | Z STO2 |
| `X11.9` | `U45 CN1-29` | W210 | CNC STO1 |
| `X11.10` | `U45 CN1-30` | W210B | CNC STO2 |

---

## 4. EtherCAT ve Ethernet

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `U1 CN1` | `U41 CN3` | W301 | EtherCAT master out |
| `U41 CN6` | `U42 CN3` | W302 | X -> Y |
| `U42 CN6` | `U43 CN3` | W303 | Y -> Alt |
| `U43 CN6` | `U44 CN3` | W304 | Alt -> Z |
| `U44 CN6` | `U45 CN3` | W305 | Z -> CNC |
| `U45 CN6` | `U50 IN` | W306 | CNC -> R1-EC |
| `U50 OUT` | `U1 CN2` | W307 | EtherCAT geri donus |
| `U1 CN3` | `U2 ETH` | W308 | HMI Ethernet |

---

## 5. Servo ve Motor Baglantilari

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `K1 cikis` | `U41 P1` | W101 | X servo AC giris |
| `U41 P2` | `M41` | W102 | X motor |
| `K1 cikis` | `U42 P1` | W103 | Y servo AC giris |
| `U42 P2` | `M42` | W104 | Y motor |
| `K1 cikis` | `U43 P1` | W105 | Alt servo AC giris |
| `U43 P2` | `M43` | W106 | Alt motor |
| `K1 cikis` | `U44 P1` | W107 | Z servo AC giris |
| `U44 P2` | `M44` | W108 | Z motor |
| `K1 cikis` | `U45 P1` | W109 | CNC servo AC giris |
| `U45 P2` | `M45` | W110 | CNC motor |
| `+24VDC` | `Z brake +` | W111 | Z fren + |
| `U44 BRK` | `Z brake -` | W112 | Z fren - |

---

## 6. DI Terminal Baglantilari

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `S11 X+` | `X20.1 / U51 DI_0` | W401 | X+ limit |
| `S12 X-` | `X20.2 / U51 DI_1` | W402 | X- limit |
| `S10 XH` | `X20.3 / U51 DI_2` | W403 | X home |
| `S21 Y+` | `X20.4 / U51 DI_3` | W404 | Y+ limit |
| `S22 Y-` | `X20.5 / U51 DI_4` | W405 | Y- limit |
| `S20 YH` | `X20.6 / U51 DI_5` | W406 | Y home |
| `S31 Z+` | `X20.7 / U51 DI_6` | W407 | Z+ limit |
| `Z- sensor` | `X20.8 / U51 DI_7` | W408 | Z- limit |
| `S30 ZH` | `X20.9 / U51 DI_8` | W409 | Z home |
| `S41 Alt+` | `X20.10 / U51 DI_9` | W410 | Alt+ limit |
| `S42 Alt-` | `X20.11 / U51 DI_10` | W411 | Alt- limit |
| `S40 AltH` | `X20.12 / U51 DI_11` | W412 | Alt home |

---

## 7. DO Terminal Baglantilari

| Kaynak | Hedef | Wire ID | Aciklama |
|--------|-------|---------|----------|
| `U53 DO_0` | `X40.1` | W451 | Servo enable |
| `U53 DO_1` | `X40.2` | W452 | Vakum pompasi |
| `U53 DO_2` | `X40.3` | W453 | Yag pompasi |
| `U53 DO_3` | `X40.4` | W454 | Fan |
| `U53 DO_4` | `X40.5` | W455 | Uyari lambasi |
| `U53 DO_5` | `X40.6` | W456 | Buzzer |
| `U53 DO_7` | `X40.7` | W457 | Kirici enable |
| `U53 DO_11` | `X40.8` | W458 | Konveyor ileri |
| `U53 DO_12` | `X40.9` | W459 | Konveyor geri |

