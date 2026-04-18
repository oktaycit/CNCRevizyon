# 🚀 AI Model Parallel Kullanım - Hızlı Referans

## 📋 Model Listesi

| Kısa Ad | Tam Ad | Kullanım | En İyi For |
|---------|--------|----------|------------|
| `plus` | qwen3.5-plus | Genel | Hızlı yanıtlar |
| `max` | qwen3-max-2026-01-23 | Analiz | Karmaşık problemler |
| `coder` | qwen3-coder-plus | Kod | Python, FreeCAD, G-code, PLC |
| `next` | qwen3-coder-next | İleri Kod | Advanced patterns |
| `glm` | glm-5 | Review | Cross-validation |
| `kimi` | kimi-k2.5 | Doküman | Long context |
| `minimax` | MiniMax-M2.5 | Alternatif | Second opinion |

## 🎯 Görev → Model Eşleme

| Görev | Kullanılacak Model(ler) | Tool |
|-------|------------------------|------|
| Genel soru | `plus` | `ai_ask` |
| Kod yaz | `coder` + `next` | `ai_code` |
| Debug | `coder` + `max` | `ai_debug` |
| Optimizasyon | `coder` + `max` | `ai_optimize` |
| Karmaşık analiz | `max` + `glm` | `ai_ask_smart` (complex) |
| Dokümantasyon | `kimi` + `plus` | `ai_ask_smart` (documentation) |
| Karşılaştırma | Tümü | `ai_compare` |
| Validation | `glm` + `minimax` | `ai_ask_smart` (validation) |

## 💬 Cline MCP Komutları

### 1. Tek Model - Hızlı Soru
```json
{
  "tool": "ai_ask",
  "params": {
    "question": "EtherCAT cycle time nedir?",
    "model": "qwen3.5-plus"
  }
}
```

### 2. Paralel - 3 Model
```json
{
  "tool": "ai_ask_parallel",
  "params": {
    "question": "Servo motor tuning nasıl yapılır?",
    "max_parallel": 3
  }
}
```

### 3. Akıllı Seçim - Kod
```json
{
  "tool": "ai_code",
  "params": {
    "task": "2 eksenli interpolasyon fonksiyonu",
    "language": "python"
  }
}
```

### 4. Akıllı Seçim - Debug
```json
{
  "tool": "ai_debug",
  "params": {
    "error_code": "AL013 Overcurrent",
    "axis": "Y"
  }
}
```

### 5. Akıllı Seçim - Genel
```json
{
  "tool": "ai_ask_smart",
  "params": {
    "question": "E-Cam profili nasıl yazılır?",
    "task_type": "complex"
  }
}
```

## 🔧 Komut Satırı

### Paralel (3 model)
```bash
python ai_orchestrator.py --parallel \
  --models qwen3.5-plus,qwen3-max-2026-01-23,qwen3-coder-plus \
  --prompt "Delta NC300 G-code örnekleri"
```

### Voting (En hızlı kazanır)
```bash
python ai_orchestrator.py --mode voting \
  --prompt "Python decorator örneği"
```

### Karşılaştırma Tablosu
```bash
python ai_orchestrator.py --mode aggregate \
  --aggregate-method compare \
  --prompt "EtherCAT vs Profinet"
```

### Dosyaya Kaydet
```bash
python ai_orchestrator.py --parallel \
  --prompt "G53 G54 farkı" \
  --output results.json
```

## 📊 Performans

| Konfigürasyon | Süre | Token | Kullanım |
|---------------|------|-------|----------|
| Tek model | ~1s | 500 | Basit sorular |
| 2 model paralel | ~2s | 1000 | Kod, debug |
| 3 model paralel | ~2.5s | 1500 | Kritik kararlar |
| 7 model paralel | ~4s | 3000 | Kapsamlı analiz |

## ⚡ Lite Plan Limitleri

- **İstek/dakika:** 60
- **Eşzamanlı:** 3 (önerilen)
- **Token/gün:** Planınıza göre

### Optimizasyon

✅ **Yap:**
- Routine sorular → Tek model
- Kod → 2 model (coder + next)
- Kritik → 3 model (max + coder + glm)

❌ **Yapma:**
- Her soruda 7 model paralel
- Gereksiz yere max kullanımı
- Rate limit'i aşmak

## 🎯 Örnek Senaryolar

### Senaryo 1: G-code Hatası
```
Tool: ai_debug
error_code: "G53 coordinate system error"
axis: "X"
→ coder + max paralel analiz
```

### Senaryo 2: FreeCAD Script
```
Tool: ai_code
task: "LCS oluşturma scripti"
language: "freecad"
→ coder + next paralel kod
```

### Senaryo 3: Servo Parametre
```
Tool: ai_ask_smart
question: "ASDA-A3-E gain tuning"
task_type: "complex"
→ max + plus paralel analiz
```

### Senaryo 4: Nesting Optimizasyon
```
Tool: ai_optimize
task: "6000x3000 plaka optimizasyonu"
part_sizes: "500x400,300x300"
→ coder + max paralel
```

## 🧪 Test

```bash
# Tüm testleri çalıştır
python test_parallel_models.py

# Tek model test
python ai_orchestrator.py --mode single \
  --prompt "Test sorusu"

# 3 model paralel test
python ai_orchestrator.py --parallel \
  --models qwen3.5-plus,qwen3-max,qwen3-coder \
  --prompt "Test"
```

## 📖 Detaylı Dokümantasyon

- [USAGE.md](USAGE.md) - Tam kullanım kılavuzu
- [README_PARALLEL.md](README_PARALLEL.md) - İngilizce döküman
- [orchestrator_config.json](orchestrator_config.json) - Yapılandırma

---

**Versiyon:** 2.0  
**Güncelleme:** 2026-04-07
