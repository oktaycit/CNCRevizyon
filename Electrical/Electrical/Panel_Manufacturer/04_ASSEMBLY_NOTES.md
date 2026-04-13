# GFB60-30RE-S Pano Montaj Talimatları

**Proje:** LiSEC GFB-60/30RE CNC Revizyon
**Belge No:** ELEC-INST-001
**Revizyon:** 4.2
**Tarih:** 2026-04-12

---

## 1. Montaj Sırası

### 1.1 Pano Hazırlığı (Adım 1-5)

1. **Pano govde kontrolu**
   - IP65 koruma kontrolü
   - Montaj plakası temizliği
   - Kablo giriş bölgeleri hazırlığı

2. **DIN ray montaji**
   - 4 adet 35mm DIN ray (NSYSDR2)
   - Konum: Y = 1750mm, 1700mm, 1650mm, 1600mm
   - Ray aralığı: 50mm
   - Her ray için end block takılması

3. **Kablo kanali montaji**
   - WT1 (60x40): Üst kenar, orta, Y = 1850mm, 1600mm
   - WT2 (40x40): Alt bölge, Y = 1350mm
   - Dikey kanal: Sağ kenar, X = 1150mm

4. **PE bara montaji**
   - Konum: DIN Ray 1 sağ taraf
   - 10 adet GNYE terminal
   - Pano gövdesi ile bağlantı

5. **Kablo gland plakalari**
   - Ana giriş: Alt sol (100-200mm x 100-300mm)
   - Saha kabloları: Alt sağ (800-1100mm x 100-500mm)

### 1.2 Büyük Bileşenler (Adım 6-10)

6. **Parafudr (F0)**
   - Konum: Üst, X = 150mm, Y = 1900mm
   - Montaj: Gövdeye direkt
   - PE bağlantısı zorunlu

7. **EMC Filtre (EMC1)**
   - Konum: Üst, X = 300mm, Y = 1900mm
   - AC giriş tarafı
   - PE bağlantısı

8. **Ana şalter (Q1)**
   - DIN Ray 1, X = 50mm
   - OFF pozisyonunda monte edin
   - Handle açık pozisyonda

9. **Ana kontaktör (K1)**
   - DIN Ray 1, Q1 yanında
   - Coil bağlantısı sonra yapılacak

10. **24VDC Power Supply (PS1)**
    - DIN Ray 1, K1 yanında
    - Output sigortalı
    - PE bağlantısı

### 1.3 Servo Sürücüler (Adım 11-15)

11. **X Servo (U41) - 4.5kW**
    - DIN Ray 2, sol başlangıç
    - En büyük sürücü, fazla alan
    - CN1, CN2, CN3 konumları kontrol edin

12. **Y Servo (U42) - 2.0kW**
    - DIN Ray 2, U41 yanında
    - EtherCAT bağlantısı planlaması

13. **Alt Servo (U43) - 2.0kW**
    - DIN Ray 2, U42 yanında

14. **Z Servo (U44) - 1.0kW**
    - DIN Ray 2, U43 yanında
    - Fren kontrol bağlantısı

15. **CNC Servo (U45) - 1.5kW**
    - DIN Ray 2, U44 yanında
    - EtherCAT son sürücü

### 1.4 I/O Sistemi (Adım 16-20)

16. **R1-EC01 Bus Coupler (U50)**
    - DIN Ray 2, U45 yanında
    - EtherCAT IN/OUT konumları

17. **DI Modül #1 (U51)**
    - DIN Ray 2, U50 yanında
    - 32-channel digital input

18. **DI Modül #2 (U52)**
    - DIN Ray 2, U51 yanında
    - Spare inputs

19. **DO Modül (U53)**
    - DIN Ray 2, U52 yanında
    - 32-channel relay output

20. **NC300 Controller (U1)**
    - Konum: PS1 altı veya ayrı alan
    - HMI Ethernet bağlantısı
    - EtherCAT master portları

20A. **Uzak HMI (U2)**
    - Ana pano icine veya pano kapagina monte ETMEYIN
    - Koprunun home noktalarina yakin saha operator pozisyonuna monte edin
    - 24VDC besleme ve Ethernet kablolarini pano cikisindan sahaya tasiyin

### 1.5 Terminaller ve Safety (Adım 21-25)

21. **24VDC Terminal (X2)**
    - DIN Ray 1, sigortalar yanında
    - Jumper bağlantıları hazırlayın

22. **Safety Input Terminal (X10)**
    - DIN Ray 1, X2 yanında
    - SARI renk - safety标识

23. **STO Output Terminal (X11)**
    - DIN Ray 1, X10 yanında
    - SARI renk

24. **DI Terminal Strips (X20, X30)**
    - DIN Ray 3
    - X20: U51 için, X30: U52 için

25. **DO Terminal Strip (X40)**
    - DIN Ray 3, X30 yanında
    - U53 için

### 1.6 Safety Relay (Adım 26-28)

26. **PILZ PNOZ X2.8P (K10)**
    - DIN Ray 3
    - Safety标识 etiketi

27. **Faz Kontrol (FK1)**
    - DIN Ray 3, K10 yanında

28. **Reset Buton (S2) ve E-STOP (S0)**
    - Panel kapak montajı
    - S2: Yeşil LED, S0: Mantar kırmızı

29. **HMI saha montaji**
    - DOP-110CS uzak operator terminali olarak uygulanacak
    - Ana pano kapaginda HMI kesiti acilmayacak
    - Konum: koprunun home noktalarina yakin, operatorun referans/home islemini rahat gorecegi nokta

---

## 2. Kablolama Sırası

### 2.1 AC Güç Kabloları

```
SIRA: Ana Giriş -> Q1 -> K1 -> Servo Sürücüler

1. X1 AC giriş terminalini bağlayın
2. Q1 giriş (busbar veya rigid cable)
3. Q1 çıkış -> K1 giriş
4. K1 çıkış -> Servo sürücü P1 portları
   - U41: 6mm2 (X ekseni)
   - U42: 4mm2 (Y ekseni)
   - U43: 4mm2 (Alt ekseni)
   - U44: 2.5mm2 (Z ekseni)
   - U45: 2.5mm2 (CNC ekseni)
```

### 2.2 24VDC Besleme

```
SIRA: PS1 -> Sigortalar -> Terminaller -> Cihazlar

1. PS1 +24V OUT -> F2 (NC300)
2. PS1 +24V OUT -> F3 (R1-EC)
3. PS1 +24V OUT -> F4 (Sensors/AUX)
4. PS1 +24V OUT -> F5 (Safety)
5. PS1 +24V OUT -> F6 (HMI)
6. X2 terminalini sigorta cikislarindan besleyin
   - X2.1: F2 cikisi (NC300)
   - X2.3: F6 cikisi (HMI)
   - X2.5: F3 cikisi (R1-EC)
   - X2.7: F4 cikisi (AUX/Sensor)
7. 0V common bus'u X2.2 / X2.4 / X2.6 / X2.8'e dagitin
8. NC300 ve R1-EC beslemelerini pano icinde tamamlayin
9. HMI icin X2.3 (+24V) ve X2.4 (0V) cikislarini saha kablosuna ayirin
```

### 2.3 EtherCAT Network

```
SIRA: NC300 -> Servo 1-5 -> R1-EC -> Return

     U1 NC300
         |
       [CN1] -----> U41 CN3 (X servo)
                    U41 CN6 -----> U42 CN3 (Y servo)
                                  U42 CN6 -----> U43 CN3 (Alt)
                                                U43 CN6 -----> U44 CN3 (Z)
                                                              U44 CN6 -----> U45 CN3 (CNC)
                                                                            U45 CN6 -----> U50 IN (R1-EC)
                                                                                          U50 OUT -----> U1 CN2 (Return)

ETHERCAT KABLOSU: CAT6 STP (Shielded Twisted Pair)
Kablo uzunlukları: 0.3-0.5m (pano içi)

HMI ETHERNET: U1 NC300 CN3 -> U2 DOP-110CS
Kablo uzunluğu: saha rotasina gore yaklasik 12 m
Konum: kopru home noktalarina yakin operator terminali
```

### 2.4 Safety Kablolar

```
KRİTİK: Safety kablolama hataları sistemin çalışmasını engeller

1. E-STOP bağlantısı
   - K10 S11 -> S0 CH1 (W203)
   - K10 S12 -> S0 CH2 (W203A)

2. Door Switch
   - K10 -> S1 (W204)

3. Reset Button
   - K10 S52 -> S2 (W205)

4. STO Outputs (SARI kablo)
   - X11.1-2 -> U41 CN1-29/30 (X STO)
   - X11.3-4 -> U42 CN1-29/30 (Y STO)
   - X11.5-6 -> U43 CN1-29/30 (Alt STO)
   - X11.7-8 -> U44 CN1-29/30 (Z STO)
   - X11.9-10 -> U45 CN1-29/30 (CNC STO)

5. STO Common (CN1-43)
   - 0V bağlantısı tüm sürücülere (W211)
```

### 2.5 I/O Signal Kabloları

```
DI bağlantıları (X20 terminal):

1. Limit ve Home sensörleri
   - X20.1-12: X, Y, Z, Alt limit/home

2. Safety feedback
   - X20.13-14: E-STOP feedback
   - X20.15: Door open

3. Process sensörleri
   - X20.16: Vacuum OK
   - X20.17-18: Glass detect

DO bağlantıları (X40 terminal):

1. Kontrol çıkışları
   - X40.1: Servo enable
   - X40.2: Vacuum pump
   - X40.3: Oil pump
   - X40.4: Cooling fan
   - X40.5: Warning light
   - X40.6: Buzzer
   - X40.8: Breaker enable
   - X40.11: Conveyor fwd
   - X40.12: Conveyor rev
```

---

## 3. Kablo İpuçları

### 3.1 Ferrule (Krimp) Kullanımı

```
Tüm kablo uçları ferrule ile bitirilmeli:

0.5mm2  -> Beyaz ferrule
0.75mm2 -> Beyaz ferrule
1.5mm2  -> Siyah ferrule
2.5mm2  -> Mavi ferrule
4mm2    -> Gri ferrule
6mm2    -> Sarı ferrule

NOT: Ferrule boyu terminal derinliğine uygun seçin
```

### 3.2 Etiketleme

```
Kablo etiketleri:
- Wire ID (örn: W101, W206)
- Her iki uçta etiket
- Gland yakınında

Terminal etiketleri:
- Pin no + Signal (orn: "X2.1 +24V NC", "X2.3 +24V HMI")
- Renk kodlaması:
  RED: +24V
  BLU: 0V
  YEL: Safety
  GNYE: PE
```

### 3.3 Kablo Kanalı Yerleşimi

```
Üst Kanal (60x40): AC güç, motor
Orta Kanal (60x40): 24VDC, EtherCAT
Alt Kanal (40x40): Sensor, I/O
Sağ Kanal (40x40): Saha kablo çıkışları

KANAL DOLULUK: Max 70% doluluk
Kablo bağı: HellermannTyton S2F
```

---

## 4. Test Protokolü

### 4.1 Pano İçi Testler (Fabrikada)

| Test | Metod | Kriter | Notlar |
|------|-------|--------|--------|
| Görsel Kontrol | İnceleme | Tüm bileşenler monte edilmiş | Fotoğraf |
| PE Devamlılık | Ohm metre | < 0.1 Ohm | PE bara tüm bileşenler |
| AC İzolasyon | 500V DC | > 1 MOhm | Q1 OFF |
| DC İzolasyon | 500V DC | > 1 MOhm | PS1 OFF |
| Terminal Kontrol | Çekme testi | Kablo çıkmıyor | Her terminal |
| EtherCAT Loop | Network analyzer | Topology OK | Ping test |
| Safety Test | Manual | E-STOP = STO aktif | K10 çıkışları |
| Hipot Test | 2.5kV AC 1min | No breakdown | AC güç |

### 4.2 Saha Bağlantı Testleri (Montajda)

| Test | Metod | Kriter |
|------|-------|--------|
| Motor yön | Jog test | Doğru yön |
| Encoder | Position read | OK feedback |
| Sensörler | Manual trigger | DI active |
| STO | E-STOP press | Motor stop |
| HMI | Display | OK connection |

---

## 5. Kritik Noktalar

### 5.1 Safety Devresi

```
!!! KRİTİK !!!
- Safety kablosı SARI renk OLMALI
- STO bağlantıları dokunmadan önce E-STOP aktif
- K10 relay test edilmeden sistem enerjilendirilmez
- E-STOP mushroom buton 40mm diameter
```

### 5.2 EtherCAT

```
!!! KRİTİK !!!
- CAT6 STP kablo kullanın
- RJ45 connector shielded
- Loop topology: NC300 -> Servo -> R1-EC -> NC300
- Network cycle: 1ms
- Connector sequence: CN3 (IN), CN6 (OUT)
```

### 5.3 Servo Güç

```
!!! KRİTİK !!!
- Motor power cable SHIELDED
- Shield PE'ye bağlanmalı
- U, V, W sequence doğru
- Encoder cable ayrı kanal
```

---

## 6. Sorun Giderme

| Sorun | Sebep | Çözüm |
|-------|-------|-------|
| Servo enable yok | STO devrede | E-STOP release |
| EtherCAT fault | Cable/port | Loop test, connector |
| NC300 comm error | HMI Ethernet | CN3 cable |
| DI signal yok | Sensor wire | X20 terminal check |
| DO output yok | Relay stuck | U53 DO module |

---

## 7. Teslimat Checklist

### 7.1 Pano İçi

- [ ] Tüm bileşenler monte edilmiş
- [ ] DIN raylar sabitlenmiş
- [ ] Kablo kanalları monte edilmiş
- [ ] PE bara bağlantısı tamam
- [ ] Gland plakaları hazır
- [ ] İç kablo bağlantıları tamam
- [ ] Etiketler takılmış
- [ ] Test raporu hazır

### 7.2 Saha Hazırlığı

- [ ] Motor kablo glandları
- [ ] Encoder kablo glandları
- [ ] Sensor kablo glandları
- [ ] E-STOP panel montajı
- [ ] Reset buton montajı
- [ ] Door switch montajı

### 7.3 Belgeler

- [ ] Title page
- [ ] Panel layout
- [ ] Terminal diagrams
- [ ] Cable schedule
- [ ] Assembly notes
- [ ] BOM
- [ ] Schematic pages
- [ ] Wire list

---

## 8. İletişim

**Sorular için:**
- Teknik destek: CNCRevizyon
- Belge kontrol: Title page contact info

**Teslimat:**
- Pano fiziksel teslim
- Belgeler PDF + Markdown
- Test raporu

---

**Belge Durumu:** FINAL
**Onaylayan:** ___________________
**Tarih:** ___________________
