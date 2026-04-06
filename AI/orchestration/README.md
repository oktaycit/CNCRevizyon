# AI Model Orchestrator - Alibaba Cloud DashScope

## 📋 Genel Bakış

Bu proje, Alibaba Cloud DashScope AI modellerini paralel olarak kullanmanızı sağlayan kapsamlı bir çözüm sunar:

| Dosya | Açıklama | Kullanım |
|-------|----------|----------|
| `ai_orchestrator.py` | Genel amaçlı orkestrasyon | Herhangi bir prompt için |
| `cnc_orchestrator.py` | CNC projesine özel | 8 görev tipi ile |
| `mcp_server.py` | VS Code Cline entegrasyonu | MCP tool olarak |

## Özellikler

- **Paralel Çalıştırma**: Birden fazla modeli aynı anda çalıştırın
- **Sıralı Çalıştırma**: Modelleri birbirinin çıktısını kullanarak çalıştırın
- **Voting Mekanizması**: En hızlı/hangi yanıtı otomatik seçin
- **Yanıt Birleştirme**: Farklı modellerin yanıtlarını birleştirin
- **Yapılandırılabilir**: Her model için farklı parametreler ayarlayın

---

## 🛠️ Kurulum

### 1. Bağımlılıkları Yükle

```bash
cd AI/orchestration
python3 -m pip install -r requirements.txt
```

Bu şunları yükler:

- `aiohttp` - Async HTTP istekleri için
- `mcp[cli]` - VS Code Cline entegrasyonu için

### 2. VS Code Tasks Kullanımı (Hızlı Başlangıç)

---

VS Code'da şu şekilde kullanın:

1. **Tasks menüsünden seçin:**
   - `Terminal` → `Run Task...` → `AI: ...` görevlerinden birini seçin

2. **Klavye kısayolu ekleyin** (`keybindings.json`):

```json
{
    "key": "ctrl+shift+a",
    "command": "workbench.action.tasks.runTask",
    "args": "AI: Kod Yazdır (CNC)"
}
```

1. **Komut paleti ile:**
   - `Ctrl+Shift+P` → `Tasks: Run Task` → AI görevi seçin

### 3. Terminal Kullanımı

### 3.1 Genel Amaçlı Kullanım (`ai_orchestrator.py`)

#### 1. Tek Model ile Çalıştırma

```bash
python3 ai_orchestrator.py -p "Merhaba, nasılsın?" -m single
```

### 2. Paralel Çalıştırma (Tüm Modeller)

```bash
python3 ai_orchestrator.py -p "REST API nedir?" -m parallel
```

### 3. Belirli Modellerle Paralel Çalıştırma

```bash
python3 ai_orchestrator.py -p "Docker container nedir?" \
    -m parallel \
    --models qwen3.5-plus,qwen3-max-2026-01-23
```

### 4. Sıralı Çalıştırma (Chain-of-Thought)

```bash
python3 ai_orchestrator.py -p "Bir Python web scraper yaz" -m sequential
```

### 5. Voting (En İyi Yanıtı Seç)

```bash
python3 ai_orchestrator.py -p "En iyi Python web framework hangisi?" -m voting
```

### 6. Yanıtları Birleştirme

```bash
# Yan yana karşılaştırma
python3 ai_orchestrator.py -p "Async/await nedir?" -m aggregate --aggregate-method compare

# JSON formatında birleştirme
python3 ai_orchestrator.py -p "FastAPI vs Flask" -m aggregate --aggregate-method json_merge

# Basit birleştirme (concat)
python3 ai_orchestrator.py -p "TypeScript avantajları" -m aggregate --aggregate-method concat
```

### 7. Özel Yapılandırma ile Çalıştırma

```bash
python3 ai_orchestrator.py -c orchestrator_config.json -p "Soru" -m parallel
```

### 8. Sonuçları Dosyaya Kaydetme

```bash
python3 ai_orchestrator.py -p "Karmaşık soru" -m parallel -o sonuc.json
```

## Yapılandırma Dosyası

`orchestrator_config.json` örneği:

```json
{
  "api_key": "sk-sp-1dfff295506a4cbba9c3745dd54e5796",
  "api_endpoint": "https://coding-intl.dashscope.aliyuncs.com/v1",
  "models": [
    {
      "model_id": "qwen3.5-plus",
      "temperature": 0.7,
      "max_tokens": 2048,
      "system_prompt": "Sen yardımsever bir AI asistansısın."
    },
    {
      "model_id": "qwen3-max-2026-01-23",
      "temperature": 0.7,
      "max_tokens": 2048,
      "system_prompt": "Sen yardımsever bir AI asistansısın."
    },
    {
      "model_id": "qwen3-coder-plus",
      "temperature": 0.3,
      "max_tokens": 4096,
      "system_prompt": "Sen uzman bir yazılım geliştirme asistanısın."
    }
  ],
  "default_mode": "parallel",
  "timeout_seconds": 60
}
```

## Komut Satırı Parametreleri

| Parametre | Kısa | Açıklama |
|-----------|------|----------|
| `--prompt` | `-p` | AI modellerine gönderilecek prompt (zorunlu) |
| `--config` | `-c` | Yapılandırma dosyası yolu |
| `--mode` | `-m` | Çalışma modu: single, parallel, sequential, voting, aggregate |
| `--models` | | Kullanılacak modeller (virgülle ayrılmış) |
| `--aggregate-method` | | Yanıt birleştirme yöntemi: concat, compare, json_merge |
| `--create-config` | | Varsayılan yapılandırma dosyası oluştur |
| `--output` | `-o` | Sonuçları kaydetmek için dosya yolu |

---

### 3.2 CNC Projesi için Kullanım (`cnc_orchestrator.py`)

Bu script, LiSEC GFB-60/30RE cam kesme makinesi projesi için özelleştirilmiştir.

#### Görev Tipleri

| Görev | Açıklama | Örnek Kullanım |
|-------|----------|----------------|
| `code` | Python/FreeCAD/NC kod yazma | `--task code --custom "FreeCAD motor montaj scripti"` |
| `design` | Mekanik tasarım önerileri | `--task design --custom "Kesim kafası montajı"` |
| `optimize` | Kesim optimizasyonu | `--task optimize --custom "Cam yerleşimi"` |
| `debug` | Hata ayıklama | `--task debug --custom "Servo alarm Err 13.1"` |
| `plc` | PLC/EtherCAT konfigürasyonu | `--task plc --custom "R1-EC PDO mapping"` |
| `cam` | E-Cam profili tasarımı | `--task cam --custom "12mm lamine cam profili"` |
| `gcode` | G-kod programı | `--task gcode --custom "Dikdörtgen kesim"` |
| `safety` | Güvenlik sistemi analizi | `--task safety --custom "STO analizi"` |

#### Çalışma Modları

```bash
# Uzmanlaşmış mod - her görev için en uygun model otomatik seçilir
python3 cnc_orchestrator.py --task code --custom "X ekseni limit switch kontrolü"

# Paralel mod - tüm modeller aynı görevi yapar
python3 cnc_orchestrator.py --task plc --mode parallel --custom "EtherCAT ayarları"

# Karşılaştırma modu - modeller arası karşılaştırma tablosu
python3 cnc_orchestrator.py --task debug --mode compare --custom "Servo hata analizi"

# En iyi yanıt modu - en hızlı/kaliteli yanıt seçilir
python3 cnc_orchestrator.py --task optimize --mode best --custom "Kesim yolu optimizasyonu"

# Demo görev ile test (custom belirtilmezse)
python3 cnc_orchestrator.py --task cam
```

#### Görev Tiplerini Listeleme

```bash
python3 cnc_orchestrator.py --list-tasks
```

#### Örnek Çıktı (Specialized Mode)

```
GÖREV: Kod Yazma
Soru: X ekseni için limit switch kontrolü

--------------------------------------------------
Model: qwen3-coder-plus
Durum: success | Latency: 1523ms

def check_x_axis_limit(switch_state: bool) -> bool:
    """
    X ekseni limit switch kontrolü
    ...
```

---

## 🔌 Cline Entegrasyonu

### Yöntem 1: Shell Wrapper Script (Önerilen)

`cline_ai_tool.sh` script'i Cline ile kullanım için optimize edilmiştir.

#### Kullanım

```bash
# Help
./cline_ai_tool.sh --help

# Kod yazdır
./cline_ai_tool.sh code "X ekseni limit switch fonksiyonu"

# Hata ayıkla
./cline_ai_tool.sh debug "Err 13.1 position deviation"

# Optimizasyon
./cline_ai_tool.sh optimize "6000x3000 cam yerleşimi"
```

#### Cline'dan Kullanım

Cline'a şu komutları verebilirsiniz:

```
AI/orchestration/cline_ai_tool.sh code "Python fonksiyonu yaz"
```

### Yöntem 2: MCP Server (mcp_server.py)

> **Not:** MCP kütüphanesi Python 3.10+ gerektirir. Python 3.9 kullanıyorsanız shell wrapper'ı kullanın.

#### Kurulum (Python 3.10+)

```bash
pip install mcp[cli]
```

#### Cline MCP Ayarları

`cline_mcp_settings.json` dosyası proje kök dizininde oluşturulmuştur:

```json
{
    "mcpServers": {
        "cnc-ai-orchestrator": {
            "command": "python3",
            "args": [
                "/Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration/mcp_server.py"
            ],
            "cwd": "/Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration",
            "env": {},
            "disabled": false,
            "autoApprove": []
        }
    }
}
```

#### Cline MCP Tool'ları

| Tool | Açıklama |
|------|----------|
| `ai_ask` | Tek modele soru sor |
| `ai_ask_parallel` | Tüm modellere paralel sor |
| `ai_code` | Kod yazdır |
| `ai_debug` | Hata ayıklama |
| `ai_optimize` | Optimizasyon |
| `ai_list_models` | Modelleri listele |

---

## 📦 Python'dan Kullanım

```python
from ai_orchestrator import AIOrchestrator, ModelConfig
import asyncio

async def main():
    # Model yapılandırmaları
    configs = [
        ModelConfig(
            model_id="qwen3.5-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            system_prompt="Sen yardımsever bir asistansın."
        ),
        ModelConfig(
            model_id="qwen3-coder-plus",
            api_key="sk-sp-1dfff295506a4cbba9c3745dd54e5796",
            temperature=0.3,
            system_prompt="Sen uzman bir yazılımcısın."
        )
    ]
    
    orchestrator = AIOrchestrator(configs)
    
    # Paralel çalıştır
    responses = await orchestrator.run_parallel("Python'da decorator nedir?")
    
    for response in responses:
        print(f"{response.model_id}: {response.content[:100]}...")
    
    # Voting ile en iyiyi seç
    result = await orchestrator.run_with_voting("En iyi Python IDE hangisi?")
    print(f"Kazanan: {result['winner']}")

asyncio.run(main())
```

## Çalışma Modları

### 1. Single

Tek bir model ile çalışır. Varsayılan olarak ilk model kullanılır.

### 2. Parallel

Tüm modeller aynı prompt ile paralel çalıştırılır. Hız karşılaştırması için idealdir.

### 3. Sequential

Modeller sırayla çalıştırılır, her model bir önceki modelin çıktısını görür.
Chain-of-thought reasoning için kullanışlıdır.

### 4. Voting

Tüm modeller paralel çalıştırılır ve en hızlı başarılı yanıt seçilir.

### 5. Aggregate

Tüm modellerin yanıtları birleştirilir:

- `concat`: Yanıtları alt alta ekler
- `compare`: Karşılaştırma tablosu oluşturur
- `json_merge`: JSON formatında birleştirir

## Örnek Çıktılar

### Parallel Mode Çıktısı

```
Çalıştırılıyor: parallel modu
Prompt: Python'da decorator nedir?...
==================================================

Model: qwen3.5-plus
Durum: success
Latency: 1234ms
İçerik:
Decorator'lar Python'da fonksiyonların davranışını değiştirmek için kullanılır...

==================================================

Model: qwen3-coder-plus
Durum: success
Latency: 1567ms
İçerik:
@decorator syntax is syntactic sugar for function wrapping...
```

### Voting Mode Çıktısı

```
Kazanan Model: qwen3.5-plus
Kazanan İçerik:
Decorator'lar Python'da fonksiyonların davranışını değiştirmek için kullanılır...
```

### Aggregate Mode (compare) Çıktısı

```
| Model | Yanıt (Özet) | Latency |
|-------|--------------|---------|
| qwen3.5-plus | Decorator'lar Python'da fonksiyonların davranışını değiştirmek... | 1234ms |
| qwen3-coder-plus | @decorator syntax is syntactic sugar for function wrapping... | 1567ms |
```

## Hata Yönetimi

Script, aşağıdaki hata durumlarını yönetir:

- API timeout
- HTTP hataları
- Ağ bağlantı hataları
- Geçersiz API key

Her model için hata durumu `status` alanında raporlanır.

## Rate Limiting

DashScope API rate limitlerine dikkat edin. Paralel çalıştırmalar daha fazla API çağrısı yapar.

## Güvenlik

- API key'lerinizi `.env` dosyasında veya güvenli bir yerde saklayın
- `orchestrator_config.json` dosyasını git'e eklemeyin
- `.gitignore` dosyasına `*.json` (hassas config'ler için) ekleyin

## Lisans

MIT License
