# Alibaba Cloud Lite Plan - AI Model Kullanım Kılavuzu

## 📋 Model Listesi ve Kullanım Alanları

| Model | Kullanım Alanı | Temperature | Max Tokens | Öncelik |
|-------|---------------|-------------|------------|---------|
| **qwen3.5-plus** | Genel sorular, hızlı yanıtlar | 0.7 | 2048 | 1 |
| **qwen3-max-2026-01-23** | Karmaşık analiz, problem çözme | 0.5 | 4096 | 2 |
| **qwen3-coder-plus** | Kod yazma, debug, optimizasyon | 0.2 | 8192 | 3 |
| **qwen3-coder-next** | İleri düzey kod üretimi | 0.3 | 4096 | 4 |
| **glm-4.7** | Alternatif model, çapraz doğrulama | 0.6 | 2048 | 5 |
| **kimi-k2.5** | Uzun doküman, teknik dokümantasyon | 0.5 | 4096 | 6 |

## 🚀 Kullanım Yöntemleri

### 1. VS Code Cline Entegrasyonu (ÖNERİLEN)

MCP Server otomatik olarak çalışır. Cline'da şu komutları kullanın:

#### Tek Model Kullanımı

```
/ai_ask question="Servo motor alarm kodu 13.0 ne anlama gelir?" model="qwen3.5-plus"
```

#### Paralel Kullanım (Tüm Modeller)

```
/ai_ask_parallel question="EtherCAT iletişim hatası nasıl çözülür?"
```

#### Kod Yazdırma

```
/ai_code task="Delta NC300 için E-Cam profili yaz" language="gcode"
```

#### Hata Ayıklama

```
/ai_debug error_code="AL013" axis="X"
```

#### Optimizasyon

```
/ai_optimize task="Kesim yolu optimizasyonu" material_size="6000x3000" part_sizes="500x400,300x300"
```

#### Model Listesi

```
/ai_list_models
```

### 2. Komut Satırı Kullanımı

#### Temel Kullanım

```bash
cd /Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration

# Tek model
python ai_orchestrator.py --prompt "Servo parametreleri nasıl ayarlanır?"

# Paralel (tüm modeller)
python ai_orchestrator.py --mode parallel --prompt "EtherCAT cycle time optimizasyonu"

# Sıralı (her model öncekinin çıktısını görür)
python ai_orchestrator.py --mode sequential --prompt "G-kod programı yaz"

# Voting (en hızlı başarılı yanıt)
python ai_orchestrator.py --mode voting --prompt "STO güvenlik devresi açıklaması"

# Karşılaştırma tablosu
python ai_orchestrator.py --mode aggregate --aggregate-method compare --prompt "Delta A3-E parametreleri"
```

#### Belirli Modeller

```bash
# Sadece coder modelleri
python ai_orchestrator.py --mode parallel --models "qwen3-coder-plus,qwen3-coder-next" --prompt "Python fonksiyonu yaz"

# Sadece analiz modelleri
python ai_orchestrator.py --mode parallel --models "qwen3-max-2026-01-23,g lm-4.7" --prompt "Sistem mimarisi analizi"
```

#### Config Dosyası ile

```bash
python ai_orchestrator.py --config orchestrator_config.json --prompt "Soru"
```

### 3. Görev Bazlı Otomatik Yönlendirme

Sistem görev tipine göre otomatik model seçer:

| Görev Tipi | Kullanılan Modeller |
|-----------|-------------------|
| `general_question` | qwen3.5-plus |
| `code_generation` | qwen3-coder-plus, qwen3-coder-next |
| `debug` | qwen3-coder-plus, qwen3-max-2026-01-23 |
| `optimization` | qwen3-coder-plus, qwen3-max-2026-01-23 |
| `design` | qwen3.5-plus, qwen3-max-2026-01-23 |
| `documentation` | kimi-k2.5, qwen3.5-plus |
| `complex_analysis` | qwen3-max-2026-01-23, qwen3.5-plus |
| `validation` | glm-4.7, kimi-k2.5 |

## ⚡ Lite Plan Optimizasyonları

### Rate Limiting

- **Maksimum eşzamanlı istek:** 3
- **Dakika başına limit:** 60 istek
- **Timeout:** 90 saniye

### Otomatik Fallback

```json
{
  "retry_on_failure": true,
  "max_retries": 2,
  "fallback_model": "qwen3.5-plus"
}
```

### Token Yönetimi

- Genel sorular: 2048 token (hızlı)
- Kod yazma: 8192 token (detaylı)
- Analiz: 4096 token (orta)

## 📊 Örnek Kullanım Senaryoları

### Senaryo 1: Servo Alarm Çözümü

```bash
# Paralel sorgu - en hızlı çözümü bul
python ai_orchestrator.py --mode parallel \
  --models "qwen3-coder-plus,qwen3-max-2026-01-23" \
  --prompt "ASDA-A3-E AL013 (Position Error) hatası如何解决?"
```

### Senaryo 2: E-Cam Profili Geliştirme

```bash
# Kod yazdırma - uzman model
python ai_orchestrator.py --mode single \
  --models "qwen3-coder-plus" \
  --prompt "Lamine cam kesim için E-Cam profili yaz. 24-bit encoder, 100μs cycle."
```

### Senaryo 3: Sistem Tasarımı Validasyonu

```bash
# Çapraz doğrulama - farklı modeller
python ai_orchestrator.py --mode aggregate \
  --aggregate-method compare \
  --models "qwen3-max-2026-01-23,g lm-4.7,kimi-k2.5" \
  --prompt "5 eksen EtherCAT kontrol sistemi tasarımı doğru mu?"
```

### Senaryo 4: Dokümantasyon

```bash
# Uzun bağlam - dokümantasyon modeli
python ai_orchestrator.py --mode single \
  --models "kimi-k2.5" \
  --prompt "NC300 CNC kontrolör programlama kılavuzu özetle"
```

## 🔧 İpuçları

1. **Hızlı yanıtlar için:** `qwen3.5-plus` kullanın (en hızlı)
2. **Kod kalitesi için:** `qwen3-coder-plus` + `qwen3-coder-next` paralel
3. **Kritik kararlar için:** En az 2 model paralel, karşılaştırma yapın
4. **Token tasarrufu:** Basit sorularda max_tokens değerini düşürün
5. **Rate limit aşımı:** 1 dakika bekleyin veya tek model moduna geçin

## 🚨 Sorun Giderme

### "Rate limit exceeded" hatası

```bash
# Tek model moduna geç
python ai_orchestrator.py --mode single --prompt "Soru"
```

### Timeout hatası

```bash
# Timeout'u artır
# orchestrator_config.json: timeout_seconds: 120
```

### Model yanıt vermiyor

```bash
# Fallback modeli kullan
# Sistem otomatik qwen3.5-plus'a geçer
```

## 📈 Performans Metrikleri

Her yanıtta şu bilgiler gösterilir:

- ✅ **Durum:** success/error/timeout
- ⏱️ **Latency:** ms cinsinden yanıt süresi
- 📊 **Token kullanımı:** Input/Output

## 🔗 Hızlı Başlangıç

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. Test çalıştırması
python ai_orchestrator.py --mode parallel --prompt "Merhaba"

# 3. Cline'da kullan
# VS Code > Cline > MCP Tools > ai_ask_parallel
```
