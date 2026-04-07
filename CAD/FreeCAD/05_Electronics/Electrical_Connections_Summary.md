# Operatör Terminal Kutusu - Elektriksel Bağlantılar Özeti

**Proje:** GFB-60/30RE CNC Revizyon  
**Doküman:** Terminal Electrical Connection Summary  
**Tarih:** 2026-04-07  
**Versiyon:** 1.0

---

## 📊 Bağlantı Özeti

| Kategori | Açıklama | Adet |
|----------|----------|------|
| **Cihaz** | Terminal kutusu içi | 4 |
| **Cihaz** | Ana pano (bağlanan) | 2 |
| **Terminal Bloğu** | X1-X6 | 6 |
| **Elektriksel Bağlantı** | Toplam kablo | 22 |
| **Kablo Girişi** | M40 + M32 | 4 |

---

## 🔌 Cihaz Listesi

### Terminal Kutusu İçinde

| Device ID | Tip | Model | Voltaj | Güç |
|-----------|-----|-------|--------|-----|
| U2 | HMI Panel | DOP-110CS | 24VDC | 15W |
| U3 | EtherCAT Bus Coupler | R1-EC01 | 24VDC | 5W |
| U4 | 32-CH Digital Input | R1-EC0902D | 24VDC | 3W |
| U5 | 32-CH Relay Output | R1-EC0902O | 24VDC/250VAC | 5W |

### Ana Pano (Terminal'den Bağlanan)

| Device ID | Tip | Model | Voltaj | Güç | Lokasyon |
|-----------|-----|-------|--------|------|----------|
| U1 | CNC Controller | NC300 | 24VDC | 50W | Main Cabinet |
| PS1 | Power Supply | DVP-PS02 | 24VDC/10A | 240W | Main Cabinet |

---

## 🔋 Güç Dağıtımı

### 24V DC Ana Besleme (Ana Pano → Terminal)

```
Ana Pano (PS1)
    │
    ├─ +24V ──[W001, 2.5mm², Red, 20m]──→ X1:1
    ├─ 0V   ──[W002, 2.5mm², Black, 20m]─→ X1:2
    └─ PE   ──[W003, 4.0mm², Grn/Yel, 20m]─→ X6:1
```

### Terminal İçi Güç Dağıtımı

```
X1 Terminal Bloğu (8-pole)
    │
    ├─ 3 ──[W004, 1.5mm², Red]──→ U2 (DOP-110CS) +24V
    ├─ 4 ──[W005, 1.5mm², Black]─→ U2 (DOP-110CS) 0V
    ├─ 5 ──[W006, 1.5mm², Red]──→ U3 (R1-EC01) V+
    └─ 6 ──[W007, 1.5mm², Black]─→ U3 (R1-EC01) 0V

X6 PE Bara (10-pole)
    │
    ├─ 2 ──[W008, 1.5mm², Grn/Yel]─→ U2 (DOP-110CS) PE
    └─ 3 ──[W009, 1.5mm², Grn/Yel]─→ U3 (R1-EC01) PE
```

---

## 🌐 Network Bağlantıları

### EtherCAT (NC300 → R1-EC01)

```
NC300 (U1) CN1
    │
    └─[W010, CAT6 SF/UTP, Blue, 20m]─→ X2 (RJ45)
                                          │
                                          └─[W011, CAT6 SF/UTP, Blue, 0.5m]─→ R1-EC01 ECAT IN
```

### Ethernet (NC300 → DOP-110CS)

```
NC300 (U1) CN3
    │
    └─[W012, CAT5e UTP, Gray, 20m]─→ X3 (RJ45)
                                       │
                                       └─[W013, CAT5e UTP, Gray, 0.5m]─→ DOP-110CS ETH
```

---

## 🔘 Dijital Girişler (Operatör Butonları)

### Buton Bağlantıları

| Buton | Renk | Terminal | R1-EC DI | Fonksiyon |
|-------|------|----------|----------|-----------|
| START | Yeşil | X4:1-2 | DI_0 | Sistem Başlat |
| STOP | Kırmızı | X4:3-4 | DI_1 | Sistem Durdur |
| E-STOP | Sarı | X4:5-6 | DI_2 | Acil Durdur |
| RESET | Mavi | X4:7-8 | DI_3 | Hata Sıfırla |

### Şema

```
+24V (X1:7)
    │
    ├─[X4:1]── START (NO) ──[X4:2]──[W015]──→ DI_0 (U4)
    ├─[X4:3]── STOP  (NC) ──[X4:4]──[W017]──→ DI_1 (U4)
    ├─[X4:5]── E-STOP (NC)─[X4:6]──[W019]──→ DI_2 (U4)
    └─[X4:7]── RESET (NO) ──[X4:8]──[W021]──→ DI_3 (U4)

0V (X1:8)
    │
    └─[Ortak, tüm butonlar için]
```

---

## 💡 Dijital Çıkışlar (İndikatörler)

### LED Bağlantıları

| İndikatör | Renk | Terminal | R1-EC DO | Fonksiyon |
|-----------|------|----------|----------|-----------|
| RUN | Yeşil | X5:1-2 | DO_0 | Sistem Çalışıyor |
| FAULT | Kırmızı | X5:3-4 | DO_1 | Sistem Hatası |

### Şema

```
DO_0 (U5) ──[W023]── X5:1 ── RUN LED (+) ── X5:2 ──[W024]── +24V (X1:7)
DO_1 (U5) ──[W025]── X5:3 ── FAULT LED (+) ── X5:4 ──[W026]── +24V (X1:7)
```

---

## 📋 Terminal Blokları

### X1: 24V DC Power Distribution

| Pin | Sinyal | Bağlantı | Wire ID |
|-----|--------|----------|---------|
| 1 | +24V_In | PS1 → X1 | W001 |
| 2 | 0V_In | PS1 → X1 | W002 |
| 3 | +24V_HMI | X1 → DOP-110CS | W004 |
| 4 | 0V_HMI | X1 → DOP-110CS | W005 |
| 5 | +24V_R1EC | X1 → R1-EC01 | W006 |
| 6 | 0V_R1EC | X1 → R1-EC01 | W007 |
| 7 | +24V_COM | Butonlar/LED ortak | W014, W024, W026 |
| 8 | 0V_COM | Buton ortak | W020 |

**Spesifikasyon:**
- Tip: Phoenix Contact MSTB 2.5/8-ST
- Voltaj: 48VDC
- Akım: 24A
- Kesit: 0.5-4.0 mm²
- Tork: 0.6 Nm

### X2: EtherCAT Network (RJ45)

| Pin | Sinyal | Bağlantı |
|-----|--------|----------|
| 1 | TX+ | NC300 → R1-EC01 |
| 2 | TX- | NC300 → R1-EC01 |
| 3 | RX+ | NC300 → R1-EC01 |
| 6 | RX- | NC300 → R1-EC01 |

**Spesifikasyon:**
- Tip: Phoenix Contact VS-RJ45-RJ45-945/5m
- Kablo: CAT6 SF/UTP
- Cycle Time: 1ms

### X3: HMI Ethernet (RJ45)

| Pin | Sinyal | Bağlantı |
|-----|--------|----------|
| 1 | TX+ | NC300 → DOP-110CS |
| 2 | TX- | NC300 → DOP-110CS |
| 3 | RX+ | NC300 → DOP-110CS |
| 6 | RX- | NC300 → DOP-110CS |

**Spesifikasyon:**
- Tip: Phoenix Contact VS-RJ45-RJ45-945/5m
- Kablo: CAT5e UTP
- IP Adres: 192.168.1.10 (NC300), 192.168.1.11 (HMI)

### X4: Digital Inputs (16-pole)

| Pin | Sinyal | Wire ID | Bağlantı |
|-----|--------|---------|----------|
| 1 | BTN_START_P | W014 | +24V |
| 2 | DI_0 | W015 | START → DI_0 |
| 3 | BTN_STOP_P | W016 | +24V |
| 4 | DI_1 | W017 | STOP → DI_1 |
| 5 | BTN_ESTOP_P | W018 | +24V |
| 6 | DI_2 | W019 | E-STOP → DI_2 |
| 7 | BTN_RESET_P | W020 | +24V |
| 8 | DI_3 | W021 | RESET → DI_3 |

**Spesifikasyon:**
- Tip: Phoenix Contact MSTB 2.5/16-ST
- Voltaj: 48VDC
- Akım: 2A
- Kesit: 0.25-1.5 mm²
- Tork: 0.5 Nm

### X5: Digital Outputs (12-pole)

| Pin | Sinyal | Wire ID | Bağlantı |
|-----|--------|---------|----------|
| 1 | DO_0_RUN | W023 | RUN LED + |
| 2 | DO_0_COM | W024 | +24V |
| 3 | DO_1_FAULT | W025 | FAULT LED + |
| 4 | DO_1_COM | W026 | +24V |

**Spesifikasyon:**
- Tip: Phoenix Contact MSTB 2.5/12-ST
- Voltaj: 250VAC
- Akım: 2A
- Kesit: 0.25-1.5 mm²
- Tork: 0.5 Nm

### X6: PE Ground Bar (10-pole)

| Pin | Bağlantı | Wire ID |
|-----|----------|---------|
| 1 | PS1 PE | W003 |
| 2 | DOP-110CS PE | W008 |
| 3 | R1-EC01 PE | W009 |
| 4-10 | Yedek | - |

**Spesifikasyon:**
- Tip: Phoenix Contact PTTB 2.5-PE
- Akım: 100A
- Kesit: 1.5-6.0 mm²
- Tork: 1.5 Nm

---

## 🔌 Kablo Girişleri

### Alt Taraf (IP65 Rakorlar)

| Pozisyon | Boyut | Kablo Tipi | İçerik | Uzunluk |
|----------|-------|------------|--------|---------|
| 1 | M40 | H07V-K | 3x4mm² (+24V, 0V, PE) | 20m |
| 2 | M32 | CAT6 SF/UTP | EtherCAT | 20m |
| 3 | M40 | CAT5e UTP | HMI Ethernet | 20m |
| 4 | M25 | H07V-K | Yedek 24V | 20m |

---

## 📊 Kablo Özeti

### Güç Kabloları

| Tip | Kesit | Renk | Toplam Uzunluk |
|-----|-------|------|----------------|
| H07V-K | 4.0 mm² | Green/Yellow | 20 m |
| H07V-K | 2.5 mm² | Red | 20 m |
| H07V-K | 2.5 mm² | Black | 20 m |
| H07V-K | 1.5 mm² | Red | 1.1 m |
| H07V-K | 1.5 mm² | Black | 1.1 m |
| H07V-K | 1.5 mm² | Green/Yellow | 1.0 m |
| H07V-K | 0.5 mm² | Green | 1.5 m |
| H07V-K | 0.5 mm² | Blue | 0.9 m |
| H07V-K | 0.5 mm² | Yellow | 0.5 m |
| H07V-K | 0.5 mm² | Red | 0.3 m |

### Network Kabloları

| Tip | Kesit | Renk | Toplam Uzunluk |
|-----|-------|------|----------------|
| CAT6 SF/UTP | 0.14 mm² | Blue | 20.5 m |
| CAT5e UTP | 0.14 mm² | Gray | 20.5 m |

---

## 🔧 Sıkma Torkları

| Terminal Tip | Vida | Tork (Nm) |
|--------------|------|-----------|
| MSTB 2.5/2-16 | M3 | 0.5 - 0.6 |
| PTTB 2.5-PE | M4 | 1.2 - 1.5 |
| RJ45 (shield) | M3 | 0.4 - 0.5 |
| Cable Gland M40 | - | 5.0 - 6.0 |
| Cable Gland M32 | - | 4.0 - 5.0 |

---

## ✅ Test Prosedürü

### Görsel Kontrol

- [ ] Tüm terminal sıkılıkları kontrol edildi (0.6 Nm)
- [ ] Wire marker'lar takıldı (kaynak→hedef)
- [ ] Kablo kesitleri doğrulandı
- [ ] Ferrule'ler tam oturdu
- [ ] PE bağlantısı direnç testi (< 100Ω)

### Süreklilik Testi

- [ ] +24V bağlantıları (X1:1,3,5,7)
- [ ] 0V bağlantıları (X1:2,4,6)
- [ ] PE bağlantıları (X6:1,2,3)
- [ ] EtherCAT süreklilik (NC300 ↔ R1-EC01)
- [ ] Ethernet süreklilik (NC300 ↔ DOP-110CS)

### Fonksiyon Testi

- [ ] START butonu → DI_0 aktif
- [ ] STOP butonu → DI_1 aktif
- [ ] E-STOP butonu → DI_2 aktif
- [ ] RESET butonu → DI_3 aktif
- [ ] RUN LED → DO_0 ile kontrol
- [ ] FAULT LED → DO_1 ile kontrol

---

## 📎 İlgili Dokümanlar

| Doküman | Konum |
|---------|-------|
| Wire Connections CSV | `../07_Exports/Electrical/Wire_Connections.csv` |
| Terminal Blocks CSV | `../07_Exports/Electrical/Terminal_Blocks.csv` |
| Device List CSV | `../07_Exports/Electrical/Device_List.csv` |
| BOM CSV | `../07_Exports/Electrical/BOM.csv` |
| Electrical Data JSON | `../07_Exports/Electrical/Electrical_Data.json` |
| Connection Matrix CSV | `../07_Exports/Electrical/Connection_Matrix.csv` |
| Cable Schedule CSV | `../07_Exports/Electrical/Cable_Schedule.csv` |
| Terminal Plan (DrawIO) | `../../Electrical/Schematics/DrawIO_Project/GFB60_30RE_S_Electrical_Rev4.1_Page08.drawio` |
| Wiring Reference | `../../Electrical/WIRING_REFERENCE.md` |

---

**Hazırlayan:** CNCRevizyon Elektrik Tasarım Ekibi  
**Son Güncelleme:** 2026-04-07  
**Durum:** ✅ Tamamlandı
