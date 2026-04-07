# 🚀 HIZLI BAŞLANGIÇ - AI Model Paralel Kullanımı

## ⚡ 30 Saniyede Başla

```bash
cd /Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration

# Test çalıştır
python3 quick_test.py --mode parallel
```

## 📌 5 Ana Kullanım Yöntemi

### 1️⃣ VS Code Cline ile (En Kolay)

Cline penceresinde MCP Tools otomatik görünür:

```
/ai_ask_parallel question="Servo motor alarm kodu 13.0 nedir?"
```

**Diğer Cline komutları:**
```
/ai_code task="Python PID kontrolcü yaz" language="python"
/ai_debug error_code="AL013" axis="X"
/ai_optimize task="Kesim yolu optimizasyonu"
/ai_list_models
```

---

### 2️⃣ Paralel Sorgu (Tüm Modeller)

```bash
python3 ai_orchestrator.py --mode parallel \
  --prompt "EtherCAT iletişim hatası nasıl çözülür?"
```

**Çıktı:** 3 model aynı anda yanıt verir, karşılaştırabilirsiniz.

---

### 3️⃣ Tek Model (Hızlı Yanıt)

```bash
python3 ai_orchestrator.py --mode single \
  --models "qwen3.5-plus" \
  --prompt "Servo parametreleri nasıl ayarlanır?"
```

---

### 4️⃣ Kod Yazdırma (Uzman Model)

```bash
python3 ai_orchestrator.py --mode single \
  --models "qwen3-coder-plus" \
  --prompt "Delta NC300 için E-Cam profili yaz"
```

---

### 5️⃣ Karşılaştırma Tablosu

```bash
python3 ai_orchestrator.py --mode aggregate \
  --aggregate-method compare \
  --prompt "5 eksenli CNC sistem mimarisi"
```

**Çıktı:**
```
| Model | Yanıt (Özet) | Latency |
|-------|--------------|---------|
| qwen3.5-plus | ... | 1200ms |
| qwen3-max-2026-01-23 | ... | 2300ms |
```

---

## 🎯 Görev Bazlı Model Seçimi

| Görev | Komut |
|------|-------|
| **Hızlı soru** | `--models qwen3.5-plus` |
| **Kod yazma** | `--models qwen3-coder-plus` |
| **Debug** | `--models qwen3-coder-plus,qwen3-max-2026-01-23` |
| **Analiz** | `--models qwen3-max-2026-01-23` |
| **Dokümantasyon** | `--models kimi-k2.5` |
| **Validasyon** | `--models glm-4.7,kimi-k2.5` |

---

## 📊 Model Performans Tablosu

| Model | Hız | Kalite | Token Limit | Kullanım |
|-------|-----|--------|-------------|----------|
| qwen3.5-plus | ⚡⚡⚡ | ⭐⭐⭐ | 2K | Günlük |
| qwen3-max | ⚡⚡ | ⭐⭐⭐⭐⭐ | 4K | Kritik |
| qwen3-coder-plus | ⚡⚡ | ⭐⭐⭐⭐⭐ | 8K | Kod |
| glm-4.7 | ⚡⚡⚡ | ⭐⭐⭐ | 2K | Backup |
| kimi-k2.5 | ⚡⚡ | ⭐⭐⭐⭐ | 4K | Döküman |

---

## 🔧 Etkin Kullanım İpuçları

### ✅ Doğru
```bash
# Basit soru → tek model, hızlı
python3 ai_orchestrator.py -m single --models qwen3.5-plus -p "Parametre nedir?"

# Kritik kod → 2 model paralel, karşılaştır
python3 ai_orchestrator.py -m parallel --models "qwen3-coder-plus,qwen3-max" -p "STO güvenlik kodu"

# Token tasarrufu → basit sorularda kısa yanıt
# orchestrator_config.json: max_tokens: 1024
```

### ❌ Yanlış
```bash
# Her soruda tüm modelleri çalıştırma (rate limit!)
# Basit soruda max model kullanma (token israfı)
# Timeout olmadan uzun task çalıştırma
```

---

## 🚨 Rate Limit Yönetimi (Lite Plan)

```
⚠️ Limitler:
- Dakikada 60 istek
- Maksimum 3 eşzamanlı istek
- Token/dakika limiti

✅ Çözümler:
1. Basit sorularda tek model kullan
2. Paralel istekleri max 3 modelde tut
3. Rate limit hatası → 1 dakika bekle
4. Fallback model otomatik devreye girer
```

---

## 📁 Dosya Yapısı

```
AI/orchestration/
├── ai_orchestrator.py      # Ana orchestrator
├── mcp_server.py           # VS Code Cline entegrasyonu
├── quick_test.py           # Hızlı test script
├── ai_quick_start.sh       # Menü tabanlı başlatıcı
├── orchestrator_config.json # Model ayarları
├── USAGE.md                # Detaylı kılavuz
└── requirements.txt        # Bağımlılıklar
```

---

## 🎓 Örnek Senaryolar

### Senaryo 1: Servo Alarm Çözümü
```bash
python3 quick_test.py \
  --mode parallel \
  --models "qwen3-coder-plus,qwen3-max-2026-01-23" \
  --prompt "ASDA-A3-E AL013 (Position Error)如何解决?"
```

### Senaryo 2: E-Cam Profili
```bash
python3 ai_orchestrator.py \
  --mode single \
  --models "qwen3-coder-plus" \
  --prompt "Lamine cam kesim E-Cam profili. 24-bit encoder, 100μs cycle time"
```

### Senaryo 3: Sistem Validasyonu
```bash
python3 ai_orchestrator.py \
  --mode aggregate \
  --aggregate-method compare \
  --models "qwen3-max-2026-01-23,g lm-4.7,kimi-k2.5" \
  --prompt "5 eksen EtherCAT kontrol sistemi doğru tasarlandı mı?"
```

---

## 🔄 Günlük Workflow

```
1. Sabah ilk test:
   ./ai_quick_start.sh → Option 2 (Hızlı Test)

2. Gün içinde kod yazma:
   Cline: /ai_code task="..." language="python"

3. Debug sırasında:
   Cline: /ai_debug error_code="AL013" axis="X"

4. Kompleks analiz:
   python3 ai_orchestrator.py -m parallel -p "Analiz..."

5. Gün sonu validasyon:
   python3 ai_orchestrator.py -m voting -p "Bugün yazılan kodları review et"
```

---

## 📞 Yardım

```bash
# Menü tabanlı başlatıcı
./ai_quick_start.sh

# Komut satırı yardımı
python3 ai_orchestrator.py --help

# Detaylı kılavuz
cat USAGE.md
```

---

**🎯 Özet:** Lite Plan'da etkin kullanım = **Doğru model + Doğru zamanda + Minimum token**
