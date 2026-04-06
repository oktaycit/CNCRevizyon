# Lisec GFB-60/30RE Cam Kesme Makinesi Revizyon Projesi

## Proje Özeti
LiSEC GFB-60/30RE cam kesme makinasının tam revizyonu. Delta Electronics ASDA-A3-E EtherCAT servo sistemleri, NC300 CNC kontrolör ve R1-EC uzak I/O modülleri ile modernize edilmiş, lamine ve cam kesim yetenekli endüstriyel sistem.

## Proje Hedefleri
- ✅ Delta ASDA-A3-E EtherCAT servo sistemleri ile tam eksen kontrolü
- ✅ Delta NC300 CNC kontrolör (G-kod işleme, EtherCAT master)
- ✅ Delta DOP-110CS HMI entegrasyonu
- ✅ R1-EC uzak I/O modülleri ile sensör/aktüatör yönetimi
- ✅ STO (Safe Torque Off) güvenlik sistemi
- ✅ E-Cam (Elektronik Kam) ile lamine kesim senkronizasyonu
- ✅ 24-bit encoder ile yüksek çözünürlüklü konumlandırma
- ✅ Yapay zeka destekli kesim optimizasyonu

## Kullanılan Teknolojiler
| Kategori | Teknoloji | Model |
|----------|-----------|-------|
| CAD Yazılımı | FreeCAD | v1.0 (Açık kaynak) |
| CNC Kontrol | Delta NC300 Serisi | NC300-XXX |
| HMI | Delta DOP-110CS | 10.1" Touch |
| Servo Sürücü | Delta ASDA-A3-E | EtherCAT, 100μs cycle |
| Servo Motor X | Delta ECMA-L11845 | 4.5kW Yüksek Atalet |
| Servo Motor Y | Delta ECMA-E11320 | 2.0kW Orta Atalet |
| Servo Motor Z | Delta ECMA-C11010 | 1.0kW Frenli |
| Uzak I/O | Delta R1-EC | EtherCAT Slave |
| AC Sürücü | Delta MS300 + CMM-EC01 | Konveyör |
| Sensörler | Leuze IS 218 Series | M18, IP67 |

## Makine Spesifikasyonları (Lisec GFB-60/30RE)
| Özellik | Değer |
|---------|-------|
| Model | LiSEC GFB-60/30RE |
| Maksimum Cam Boyutu | 6000 x 3000 mm |
| Minimum Cam Boyutu | 300 x 200 mm |
| Cam Kalınlığı | 2-25 mm |
| Kesim Hızı | 0-80 m/dk |
| Konumlandırma Hassasiyeti | ±0.05 mm (24-bit encoder) |
| Eksen Sayısı | 5 (X, Y, Z, Alt, CNC/Rodaj) |
| EtherCAT Cycle Time | 100 μs |

## Sistem Mimarisi
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Delta NC300 (EtherCAT Master)                    │
│                         CNC Kontrolör                               │
└─────────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ASDA-A3-E     │    │ ASDA-A3-E     │    │ ASDA-A3-E     │
│ 4.5kW (X)     │    │ 2.0kW (Y)     │    │ 2.0kW (Alt)   │
│ ECMA-L11845   │    │ ECMA-E11320   │    │ ECMA-E11320   │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│ ASDA-A3-E     │    │ ASDA-A3-E     │    │ R1-EC         │
│ 1.0kW (Z)     │    │ 1.5kW (CNC)   │    │ Bus Coupler   │
│ ECMA-C11010   │    │ ECMA-E11315   │    │               │
│ (Frenli)      │    │ (IP67)        │    │               │
└───────────────┘    └───────────────┘    └───────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
          ┌───────────────┐    ┌───────────────┐
          │ R1-EC0902D x3 │    │ R1-EC0902O x3 │
          │ Digital Input │    │ Digital Output│
          │ (Sensörler)   │    │ (Valfler)     │
          └───────────────┘    └───────────────┘
```

## Güvenlik Sistemi (STO)
```
Acil Durdurma ──► Pilz PNOZ ──► STO Hattı ──► Tüm Sürücüler
                                          (Safe Torque Off)
```

## Proje Klasör Yapısı
```
CNCRevizyon/
├── README.md
├── CAD/
│   ├── Assembly/
│   ├── Parts/
│   │   ├── Frame/
│   │   ├── CuttingHead/
│   │   ├── Motors/          # ECMA-L/E/C serisi modeller
│   │   └── Electronics/     # R1-EC, NC300 yerleşim
│   ├── Drawings/
│   └── Exports/
├── Electrical/
│   ├── Schematics/          # EtherCAT şeması
│   ├── Wiring/              # Kablaj planları
│   ├── STO_Circuit/         # Güvenlik devresi
│   └── BOM/
├── Firmware/
│   ├── NC300/               # Delta NC programları
│   │   ├── GCode/
│   │   ├── E-Cam/           # Lamine kesim profili
│   │   └── PLC/
│   └── Tools/
├── Delta/
│   ├── Servo/
│   │   ├── ASD-A3-E/        # EtherCAT parametreleri
│   │   └── ECMA-Motors/     # Motor datasheet
│   ├── NC300/
│   └── R1-EC/               # Uzak I/O konfigürasyonu
├── AI/
│   ├── Optimization/
│   └── Vision/
├── Documentation/
│   ├── Manuals/
│   ├── Specifications/
│   └── Reports/
└── Tests/
```

## Sonraki Adımlar
1. [ ] FreeCAD kurulumu ve Assembly4 eklentisi
2. [ ] ECMA-L11845 (4.5kW) motor modelleme
3. [ ] ECMA-C11010 (frenli) Z ekseni montajı
4. [ ] R1-EC modül kutu yerleşim tasarımı
5. [ ] Leuze IS 218 sensör montaj braketleri
6. [ ] EtherCAT kablolama şeması
7. [ ] NC300 E-Cam profili programlama
8. [ ] STO güvenlik devresi testi

## Kaynaklar
- **Delta NC300:** https://www.delta-automation.com/tr/products/industrial-automation/plc-based-control
- **ASDA-A3-E:** https://www.delta-automation.com/tr/products/industrial-automation/servo-systems
- **DOP-110CS:** https://www.delta-automation.com/tr/products/industrial-automation/hmi

**Proje Başlangıç:** 03.04.2026  
**Versiyon:** 2.0 (EtherCAT Revizyon)