# 🎉 Alibaba Cloud Lite Plan - Paralel Model Kullanım Kılavuzu

## ✅ Yapılan Değişiklikler

### 1. Güncellenmiş Dosyalar

#### `orchestrator_config.json`
- **6 model** yapılandırması eklendi
- Lite plan optimizasyonları eklendi
- Görev bazlı model routing tablosu
- Paralel ayarlar (max 3 eşzamanlı)

#### `mcp_server.py`
- **8 yeni MCP tool** eklendi
- Akıllı görev yönlendirme (smart routing)
- Paralel model desteği (max 6 model)
- Semaphore ile rate limit koruması
- Gelişmiş hata yönetimi ve fallback

#### `README.md`
- AI orkestrasyon bölümü eklendi
- Model listesi ve kullanım örnekleri
- Hızlı başlangıç kılavuzu

### 2. Yeni Dosyalar

#### `USAGE.md` (Türkçe)
- Detaylı kullanım kılavuzu
- 8 MCP tool açıklaması
- 6 kullanım senaryosu
- Performans ipuçları
- Sorun giderme

#### `README_PARALLEL.md` (İngilizce)
- İngilizce dokümantasyon
- Komut satırı örnekleri
- MCP tool referansı
- Yapılandırma seçenekleri

#### `test_parallel_models.py`
- 5 farklı test senaryosu
- Tek model testi
- Paralel model testi
- Voting mode testi
- Karşılaştırma mode testi
- Bireysel model testi

#### `QUICK_REFERENCE.md`
- Hızlı referans kartı
- Model kısaltmaları
- Görev → Model eşleme
- Örnek senaryolar
- Performans tablosu

---

## 🚀 Kullanılabilir Modeller

| # | Model | Kullanım | Temp | Max Tokens |
|---|-------|----------|------|------------|
| 1 | **qwen3.5-plus** | Genel amaçlı | 0.7 | 2048 |
| 2 | **qwen3-max-2026-01-23** | Karmaşık analiz | 0.5 | 4096 |
| 3 | **qwen3-coder-plus** | Kod yazma | 0.2 | 8192 |
| 4 | **qwen3-coder-next** | İleri kod | 0.3 | 4096 |
| 5 | **glm-4.7** (Zhipu) | Alternatif | 0.6 | 2048 |
| 6 | **kimi-k2.5** (MiniMax) | Dokümantasyon | 0.5 | 4096 |

---

## 🎯 8 Yeni MCP Tool

### 1. `ai_ask` - Tek Model
**Kullanım:** Hızlı, basit sorular
```json
{
  "tool": "ai_ask",
  "params": {
    "question": "EtherCAT nedir?",
    "model": "qwen3.5-plus"
  }
}
```

### 2. `ai_ask_parallel` - Paralel Modeller ⭐
**Kullanım:** Kritik kararlar, karşılaştırma
```json
{
  "tool": "ai_ask_parallel",
  "params": {
    "question": "Servo tuning parametreleri",
    "max_parallel": 3
  }
}
```

### 3. `ai_ask_smart` - Akıllı Seçim ⭐⭐
**Kullanım:** Görev tipine göre otomatik model
```json
{
  "tool": "ai_ask_smart",
  "params": {
    "question": "E-Cam profili nasıl yazılır?",
    "task_type": "complex"  // general, code, debug, optimize, design, documentation, complex, validation
  }
}
```

### 4. `ai_code` - Kod Yazma ⭐⭐
**Kullanım:** Python, FreeCAD, G-code, PLC, ST
```json
{
  "tool": "ai_code",
  "params": {
    "task": "2 eksenli interpolasyon",
    "language": "python"  // python, freecad, gcode, plc, stir
  }
}
```
**Özellik:** 2 model paralel (coder-plus + coder-next)

### 5. `ai_debug` - Hata Ayıklama
**Kullanım:** Servo alarm, EtherCAT hatası
```json
{
  "tool": "ai_debug",
  "params": {
    "error_code": "AL013 Overcurrent",
    "axis": "Y"
  }
}
```
**Özellik:** 2 model paralel analiz (coder + max)

### 6. `ai_optimize` - Optimizasyon
**Kullanım:** Nesting, kesim yolu, hız optimizasyonu
```json
{
  "tool": "ai_optimize",
  "params": {
    "task": "Plaka yerleşim optimizasyonu",
    "material_size": "6000x3000",
    "part_sizes": "500x400,300x300"
  }
}
```
**Özellik:** 2 model paralel (coder + max)

### 7. `ai_compare` - Karşılaştırma
**Kullanım:** Model karşılaştırma tablosu
```json
{
  "tool": "ai_compare",
  "params": {
    "question": "EtherCAT vs Profinet"
  }
}
```
**Özellik:** Tüm modelleri karşılaştır

### 8. `ai_list_models` - Model Listesi
**Kullanım:** Kullanılabilir modelleri listele
```json
{
  "tool": "ai_list_models"
}
```

---

## 📊 Görev Tipine Göre Model Seçimi

| Görev Tipi | Kullanılan Modeller | Tool |
|------------|---------------------|------|
| `general` | qwen3.5-plus | ai_ask |
| `code` | qwen3-coder-plus, qwen3-coder-next | ai_code |
| `debug` | qwen3-coder-plus, qwen3-max | ai_debug |
| `optimize` | qwen3-coder-plus, qwen3-max | ai_optimize |
| `design` | qwen3.5-plus, qwen3-max | ai_ask_smart |
| `documentation` | kimi-k2.5, qwen3.5-plus | ai_ask_smart |
| `complex` | qwen3-max, qwen3.5-plus | ai_ask_smart |
| `validation` | glm-4.7, kimi-k2.5 | ai_ask_smart |

---

## 💡 Kullanım Örnekleri

### Örnek 1: Basit Soru (Tek Model)
**Senaryo:** Hızlı bilgi alma
```
Tool: ai_ask
Question: "Delta NC300'de G01 komutu nasıl kullanılır?"
Model: qwen3.5-plus
```
**Süre:** ~1s | **Token:** ~500

### Örnek 2: Kod Yazdırma (2 Model Paralel)
**Senaryo:** FreeCAD scripti
```
Tool: ai_code
Task: "Assembly4 için LCS oluşturma scripti"
Language: freecad
```
**Süre:** ~2s | **Token:** ~1000 | **Modeller:** coder-plus + coder-next

### Örnek 3: Servo Alarm Debug (2 Model Paralel)
**Senaryo:** AL013 overcurrent hatası
```
Tool: ai_debug
Error: "AL013 Overcurrent"
Axis: "Y"
```
**Süre:** ~2s | **Token:** ~1000 | **Modeller:** coder-plus + max

### Örnek 4: Karmaşık Analiz (3 Model Paralel)
**Senaryo:** E-Cam profili tasarımı
```
Tool: ai_ask_smart
Question: "E-Cam profili ile mekanik kam farkları"
Task Type: complex
```
**Süre:** ~2.5s | **Token:** ~1500 | **Modeller:** max + plus + coder

### Örnek 5: Model Karşılaştırması (6 Model)
**Senaryo:** Kapsamlı analiz
```
Tool: ai_compare
Question: "EtherCAT cycle time optimizasyonu"
```
**Süre:** ~4s | **Token:** ~3000 | **Modeller:** Tümü (6)

---

## ⚡ Lite Plan Optimizasyonları

### Rate Limit Koruması
- **Max eşzamanlı:** 3 istek
- **Semaphore:** Async limit koruması
- **Retry logic:** Başarısız isteklerde otomatik tekrar

### Token Optimizasyonu
- **Routine sorular:** Tek model (qwen3.5-plus)
- **Kod görevleri:** 2 model (coder-plus + coder-next)
- **Kritik kararlar:** 3 model (plus + max + coder)
- **Kapsamlı analiz:** 6 model (tümü)

### Fallback Mekanizması
- Birincil model başarısız → Yedek model
- Timeout koruması (120s)
- Detaylı hata raporlama

---

## 🧪 Test Etme

### 1. Test Scriptini Çalıştır
```bash
cd AI/orchestration
python test_parallel_models.py
```

### 2. Komut Satırı Testi
```bash
# Tek model
python ai_orchestrator.py --mode single \
  --prompt "Python decorator nedir?"

# 3 model paralel
python ai_orchestrator.py --parallel \
  --models qwen3.5-plus,qwen3-max-2026-01-23,qwen3-coder-plus \
  --prompt "EtherCAT cycle time optimizasyonu"

# Karşılaştırma tablosu
python ai_orchestrator.py --mode aggregate \
  --aggregate-method compare \
  --prompt "Servo motor tuning teknikleri"
```

### 3. Cline'da Test
VS Code → Cline Extension → MCP Tools
```
Tool: ai_list_models
```

---

## 📈 Performans Metrikleri

| Konfigürasyon | Ortalama Süre | Token Tüketimi | Önerilen Kullanım |
|---------------|---------------|----------------|-------------------|
| 1 model | ~1s | 300-800 | Basit sorular |
| 2 model paralel | ~1.5-2s | 600-1600 | Kod, debug |
| 3 model paralel | ~2-2.5s | 900-2400 | Kritik kararlar |
| 6 model paralel | ~3.5-4s | 1800-4800 | Kapsamlı analiz |

---

## 📁 Dosya Yapısı

```
AI/orchestration/
├── mcp_server.py              # MCP server (8 tool)
├── ai_orchestrator.py         # Paralel model çalıştırıcı
├── orchestrator_config.json   # Yapılandırma (6 model)
├── test_parallel_models.py    # Test scripti
├── requirements.txt           # Bağımlılıklar
├── USAGE.md                   # Türkçe kılavuz
├── README_PARALLEL.md         # İngilizce kılavuz
├── QUICK_REFERENCE.md         # Hızlı referans
└── CHANGES.md                 # Bu dosya
```

---

## 🎯 Sonraki Adımlar

1. **Test et:** `python test_parallel_models.py`
2. **Cline'da dene:** MCP tools kullan
3. **Dokümantasyonu oku:** USAGE.md
4. **Kendi senaryolarını oluştur:** Görev tiplerini kullan

---

## 📞 Sorun Giderme

### MCP Server Bağlanmıyor
```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Server'ı test et
python mcp_server.py
```

### API Hatası
- API anahtarını kontrol et
- Rate limit'e dikkat et (60/dakika)
- `max_parallel` değerini düşür (3 → 2)

### Timeout
- `timeout_seconds` artır (90 → 120)
- `max_parallel_models` azalt (3 → 2)

---

**Versiyon:** 2.0  
**Tarih:** 2026-04-07  
**Plan:** Alibaba Cloud Lite Basic  
**Modeller:** 6 paralel  
**Optimizasyon:** Rate limit, token, performans
