# Lisec GFB-60/30RE Cam Kesme Makinesi Revizyon Projesi

## Proje Özeti

LiSEC GFB-60/30RE cam kesme makinasının tam revizyonu. Delta Electronics ASDA-A3-E EtherCAT servo sistemleri, NC300 CNC kontrolör ve R1-EC uzak I/O modülleri ile modernize edilmiş, lamine ve cam kesim yetenekli endüstriyel sistem.

## Proje Hedefleri

- ✅ Delta ASDA-A3-E EtherCAT servo sistemleri ile tam eksen kontrolü
- ✅ Delta NC300 CNC kontrolör (G-kod işleme, EtherCAT master)
- ✅ Delta DOP-110CS HMI entegrasyonu
- ✅ R1-EC uzak I/O modülleri ile sensör/aktüatör yönetimi
- ✅ STO (Safe Torque Off) güvenlik sistemi
- ✅ VB ünitesinde mekanik bağlı üst-alt kafa ile lamine kesim senkronizasyonu
- ✅ 24-bit encoder ile yüksek çözünürlüklü konumlandırma
- ✅ Yapay zeka destekli kesim optimizasyonu
- ✅ **6 AI modeli paralel kullanım** (Alibaba Cloud Lite Plan optimize)

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
│   │   ├── E-Cam/           # Legacy lamine profil denemeleri
│   │   └── PLC/
│   └── Tools/
├── Delta/
│   ├── Servo/
│   │   ├── ASD-A3-E/        # EtherCAT parametreleri
│   │   └── ECMA-Motors/     # Motor datasheet
│   ├── NC300/
│   └── R1-EC/               # Uzak I/O konfigürasyonu
├── AI/
│   ├── Optimization/        # Kesim optimizasyonu
│   ├── Vision/             # Görüntü işleme
│   └── orchestration/      # AI Model orkestrasyonu (6 model paralel)
│       ├── mcp_server.py   # MCP server (Cline entegrasyonu)
│       ├── ai_orchestrator.py  # Paralel model çalıştırma
│       ├── orchestrator_config.json  # Model yapılandırması
│       ├── test_parallel_models.py  # Test scripti
│       ├── USAGE.md        # Detaylı kullanım kılavuzu
│       └── requirements.txt
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
7. [ ] NC300 VB mekanik bağlı lamine çevrimi programlama
8. [ ] STO güvenlik devresi testi

---

## 🤖 AI Model Orkestrasyonu (YENİ!)

### Kullanılabilir Modeller (Alibaba Cloud Lite Plan)

| Model | Kullanım Alanı | Temp | Max Tokens |
|-------|----------------|------|------------|
| **qwen3.5-plus** | Genel amaçlı, hızlı yanıtlar | 0.7 | 2048 |
| **qwen3-max-2026-01-23** | Karmaşık analiz, problem çözme | 0.5 | 4096 |
| **qwen3-coder-plus** | Kod yazma (Python, FreeCAD, G-code, PLC) | 0.2 | 8192 |
| **qwen3-coder-next** | İleri düzey kod üretimi | 0.3 | 4096 |
| **glm-4.7** (Zhipu) | Alternatif model, çapraz doğrulama | 0.6 | 2048 |
| **kimi-k2.5** (MiniMax) | Uzun doküman, teknik dokümantasyon | 0.5 | 4096 |

### MCP Tool'ları (Cline içinde)

- **`ai_ask`** - Tek model ile hızlı soru-cevap
- **`ai_ask_parallel`** - 3 modele aynı anda sor (max 6)
- **`ai_ask_smart`** - Görev tipine göre otomatik model seçimi
- **`ai_code`** - Kod yazdırma (2 model paralel)
- **`ai_debug`** - Hata ayıklama (2 model paralel analiz)
- **`ai_optimize`** - Kesim optimizasyonu (2 model paralel)
- **`ai_compare`** - Model karşılaştırma tablosu
- **`ai_list_models`** - Kullanılabilir modelleri listele

### Hızlı Başlangıç

```bash
# Test parallel model usage
cd AI/orchestration
python test_parallel_models.py

# Command line usage
python ai_orchestrator.py --parallel \
  --models qwen3.5-plus,qwen3-max,qwen3-coder-plus \
  --prompt "EtherCAT cycle time nedir?"
```

### Detaylı Dokümantasyon

- 📖 [Kullanım Kılavuzu](AI/orchestration/USAGE.md)
- 📖 [README_PARALLEL.md](AI/orchestration/README_PARALLEL.md)
- 🧪 [Test Scripti](AI/orchestration/test_parallel_models.py)

---

**Proje Başlangıç:** 03.04.2026  
**Versiyon:** 2.0 (EtherCAT Revizyon + AI Orchestration)  
**AI Models:** 6 parallel models (Alibaba Cloud Lite Plan)
