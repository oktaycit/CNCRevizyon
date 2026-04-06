# Cline Model Seçim Rehberi

Bu rehber, Cline için en uygun model ID'yi seçmenize yardımcı olur.

## 📋 Hızlı Seçim Tablosu

| Kullanım Amacı | Önerilen Model | Alternatif |
|---------------|----------------|------------|
| **Genel Kodlama** | `qwen3.5-plus` | `qwen3-coder-plus` |
| **Kod Üretme (Expert)** | `qwen3-coder-next` | - |
| **Karmaşık Problemler** | `qwen3-max-2026-01-23` | `glm-5` |
| **Görsel Analiz** | `qwen3.5-plus` | `kimi-k2.5` |
| **Hızlı Yanıtlar** | `glm-4.7` | `MiniMax-M2.5` |

## 🤖 Model Detayları

### Qwen Serisi (DashScope)

#### `qwen3.5-plus` ✅ ÖNERİLEN
- **Güçlü Yönler**: Dengeli performans, hızlı yanıt
- **Kullanım**: Genel kodlama, dokümantasyon, basit analiz
- **Token Limiti**: Yüksek
- **Maliyet**: Orta
- **Ne zaman seçmeli**: Günlük kullanım için en iyi seçim

#### `qwen3-max-2026-01-23`
- **Güçlü Yönler**: En yüksek akıl yürütme kapasitesi, deep thinking
- **Kullanım**: Karmaşık algoritma optimizasyonu, matematiksel problemler
- **Token Limiti**: Çok yüksek
- **Maliyet**: Yüksek
- **Ne zaman seçmeli**: Zor problemler için

#### `qwen3-coder-next`
- **Güçlü Yönler**: Kod üretme, refactoring, debug
- **Kullanım**: Sadece kodlama görevleri
- **Token Limiti**: Yüksek
- **Maliyet**: Orta-Yüksek
- **Ne zaman seçmeli**: Yoğun kod yazma işleri için

#### `qwen3-coder-plus`
- **Güçlü Yönler**: Kod analizi ve üretme
- **Kullanım**: Kod review, test yazma
- **Token Limiti**: Yüksek
- **Maliyet**: Orta
- **Ne zaman seçmeli**: Kod odaklı görevler için

### Zhipu Serisi

#### `glm-5`
- **Güçlü Yönler**: Deep thinking, çok adımlı akıl yürütme
- **Kullanım**: Karmaşık problem çözme
- **Maliyet**: Orta-Yüksek

#### `glm-4.7`
- **Güçlü Yönler**: Hızlı yanıt, iyi fiyat/performans
- **Kullanım**: Basit görevler, hızlı iterasyon
- **Maliyet**: Düşük

### Kimi Serisi

#### `kimi-k2.5`
- **Güçlü Yönler**: Uzun context, görsel analiz
- **Kullanım**: Büyük dosyalar, görsel+içerik analizi
- **Maliyet**: Orta

### MiniMax Serisi

#### `MiniMax-M2.5`
- **Güçlü Yönler**: Hızlı yanıt süresi
- **Kullanım**: Basit metin görevleri
- **Maliyet**: Düşük

## ⚙️ Hızlı Ayar Değiştirme

### Yöntem 1: Cline UI
1. VS Code'da Cline extension'ı açın
2. Settings (⚙️) > Model Settings
3. "Model ID" alanına istediğiniz modeli yazın

### Yöntem 2: JSON Dosyası
`cline-dashscope-settings.json` dosyasını düzenleyin:
```json
{
  "cline.modelId": "qwen3.5-plus"
}
```

### Yöntem 3: Environment Variable
`.env` dosyasını düzenleyin:
```bash
DASHSCOPE_MODEL=qwen3.5-plus
```

## 💡 Öneriler

### CNC Projesi İçin Önerilen Setup
```json
{
  "cline.apiProvider": "openai-compatible",
  "cline.apiEndpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
  "cline.modelId": "qwen3.5-plus"
}
```

**Neden qwen3.5-plus?**
- ✅ CAD/CAM kod üretimi için yeterli
- ✅ Python scriptleri yazabilme
- ✅ Dokümantasyon oluşturma
- ✅ Dengeli hız/kalite oranı
- ✅ Maliyet etkin

### Görev Bazlı Model Değiştirme

| Görev | Model |
|-------|-------|
| FreeCAD Python Script | `qwen3.5-plus` |
| Cutting Optimization AI | `qwen3-max-2026-01-23` |
| Hızlı Kod Düzeltme | `glm-4.7` |
| Teknik Dokümantasyon | `qwen3.5-plus` |
| Vision/AI Geliştirme | `kimi-k2.5` |

## 🔍 Model Test Etme

Yeni bir model denemek için bu komutu kullanabilirsiniz:

```bash
curl -X POST "https://coding-intl.dashscope.aliyuncs.com/v1/chat/completions" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3.5-plus",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## 📊 Performans Karşılaştırması

| Model | Kod Kalitesi | Hız | Fiyat | Genel |
|-------|-------------|-----|-------|-------|
| qwen3.5-plus | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| qwen3-max | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| qwen3-coder-next | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| glm-5 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| glm-4.7 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## 🆘 Sorun Giderme

### Model Bulunamadı Hatası
- API endpoint'in doğru olduğundan emin olun
- Model ID'yi doğru yazdığınızı kontrol edin

### Yanıt Çok Yavaş
- Daha hafif model deneyin (glm-4.7, MiniMax-M2.5)
- Network bağlantınızı kontrol edin

### Kalite Düşük
- qwen3-max veya qwen3-coder-next deneyin
- Prompt'unuzu daha detaylı yazın

---

**Son Güncelleme**: 2026-04-03
**Proje**: CNC Revizyon