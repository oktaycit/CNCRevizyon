# FreeCAD MCP Entegrasyonu - Kullanım Kılavuzu

## Genel Bakış

CNC Revizyon projesi, MCP (Model Context Protocol) üzerinden FreeCAD entegrasyonu sağlar. Bu sayede:

- ✅ AI modelleri ile FreeCAD modelleme
- ✅ Otomatik script çalıştırma
- ✅ Assembly4 desteği
- ✅ STEP/DXF/STL export

## Kurulum

### 1. FreeCAD Kurulumu (macOS)

**Homebrew ile (Önerilen):**
```bash
brew install --cask freecad
```

**Manuel İndirme:**
- https://www.freecad.org/downloads.php
- .dmg dosyasını indirip /Applications'a taşıyın

**PATH'e Ekleme:**
```bash
# ~/.zshrc dosyasına ekleyin
export PATH="/Applications/FreeCAD.app/Contents/MacOS:$PATH"

# Terminal'i yeniden başlatın
source ~/.zshrc
```

**Doğrulama:**
```bash
FreeCAD --version
# Output: FreeCAD 1.0.0 ...
```

### 2. MCP Kütüphanesi

```bash
cd /Users/oktaycit/Projeler/CNCRevizyon/AI/orchestration
pip install mcp[cli]
```

### 3. MCP Server Ayarları

VS Code Cline ayarlarında (`cline_mcp_settings.json`):

```json
{
    "mcpServers": {
        "cnc-ai-orchestrator": {
            "command": "python3.14",
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

## Kullanım

### Yöntem 1: Cline MCP Tool'ları (VS Code)

Cline'da aşağıdaki komutları kullanabilirsiniz:

#### FreeCAD Script Çalıştırma

```
/freecad_run_script path="CAD/FreeCAD/06_Assembly/update_vacuum_pads.py"
```

#### Vakum Padleri Güncelleme

```
Vakum padlerini kartezyen köprüye ekle - 4 adet 80mm aralıklı
```

#### FreeCAD Model Oluşturma

```
/freecad_create_part part_type="box" parameters='{"length": 100, "width": 50, "height": 30}'
```

#### Assembly4 Parça Ekleme

```
/freecad_assembly4_add_part part_name="Vakum_Pad_1" part_type="cylinder" parameters='{"radius": 26, "height": 28}'
```

### Yöntem 2: Manuel FreeCAD Python Console

FreeCAD'i açın ve Python Console'da çalıştırın:

#### Vakum Padleri Güncelleme

```python
# Script'i çalıştır
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/update_vacuum_pads.py").read())
update_vacuum_pads()

# Doğrulama
verify_vacuum_system()
```

#### GFB Modeli Açma

```python
import FreeCAD as App
doc = App.open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/GFB_60_30RE_S.FCStd")
```

### Yöntem 3: Komut Satırı (CLI)

```bash
# FreeCAD CLI ile script çalıştırma
FreeCAD --console --script /Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/update_vacuum_pads.py

# Veya Python ile
FreeCAD -c "exec(open('/path/to/script.py').read()); update_vacuum_pads()"
```

## Mevcut MCP Tool'ları

### AI Tools

| Tool | Açıklama |
|------|----------|
| `/ai_ask` | Tek model ile soru-cevap |
| `/ai_ask_parallel` | 3 modele aynı anda sor |
| `/ai_ask_smart` | Görev tipine göre otomatik model seçimi |
| `/ai_code` | Kod yazdırma (Python, FreeCAD, G-code, PLC) |
| `/ai_debug` | Hata ayıklama |
| `/ai_optimize` | Kesim optimizasyonu |
| `/ai_compare` | Model karşılaştırma tablosu |

### FreeCAD Tools

| Tool | Açıklama |
|------|----------|
| `/freecad_list_documents` | FreeCAD dosyalarını listele |
| `/freecad_open` | FreeCAD dosyası aç |
| `/freecad_create_part` | Parça oluştur (box, cylinder, sphere) |
| `/freecad_export` | STEP/DXF/STL export |
| `/freecad_assembly_info` | Assembly bilgisi |
| `/freecad_assembly4_add_part` | Assembly4'e parça ekle |
| `/freecad_run_script` | Python script çalıştır |

## Örnek Senaryolar

### Senaryo 1: Vakum Padleri Ekleme

**Cline Komutu:**
```
Kartezyen köprü üzerindeki vakum padlerini güncelle, 4 adet 80mm aralıklı
```

**Manuel Python:**
```python
exec(open("CAD/FreeCAD/06_Assembly/update_vacuum_pads.py").read())
update_vacuum_pads()
```

### Senaryo 2: Glass Edge Deletion Head Oluşturma

**Cline Komutu:**
```
/freecad_create_part part_type="assembly" parameters='{"wheel_diameter": 150, "wheel_width": 20}'
```

**Manuel Python:**
```python
exec(open("CAD/FreeCAD/04_CuttingHead/Glass_Edge_Deletion_Head_Generator.py").read())
create_glass_edge_deletion_head()
```

### Senaryo 3: Assembly4 Model Güncelleme

**Cline Komutu:**
```
GFB-60/30RE-S modelini aç ve lama sıyırma ünitesini Z kesim kafasına taşı
```

**Manuel Python:**
```python
# Modeli aç
doc = App.open("CAD/FreeCAD/06_Assembly/GFB_60_30RE_S.FCStd")

# Script'i çalıştır
exec(open("CAD/FreeCAD/06_Assembly/GFB_60_30RE_S_Model.py").read())

# Değişiklikleri kaydet
doc.save()
```

## Sorun Giderme

### "FreeCAD CLI Bulunamadı" Hatası

**Sebep:** FreeCAD sistem PATH'inde değil

**Çözüm 1 - Homebrew:**
```bash
brew install --cask freecad
```

**Çözüm 2 - PATH Ekleme:**
```bash
echo 'export PATH="/Applications/FreeCAD.app/Contents/MacOS:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Çözüm 3 - Manuel Kullanım:**
FreeCAD'i açıp Python Console'da script çalıştırın.

### "MCP kütüphanesi yüklü değil" Hatası

**Çözüm:**
```bash
pip install mcp[cli]
```

### "Script çalıştırılamadı" Hatası

**Kontrol:**
1. Script dosyası mevcut mu?
2. Python syntax hatası var mı?
3. FreeCAD versiyonu uyumlu mu? (1.0+)

**Debug:**
```bash
# Script'i test et
python3 -m py_compile CAD/FreeCAD/06_Assembly/update_vacuum_pads.py
```

### "Assembly4 çalışmıyor" Hatası

**Çözüm:**
1. FreeCAD'de **Addon Manager** → **Assembly4** yükleyin
2. FreeCAD'i yeniden başlatın

## Dosya Yapısı

```
AI/orchestration/
├── mcp_server.py              # MCP server (ana)
├── freecad_mcp.py             # FreeCAD controller
├── ai_orchestrator.py         # AI orchestrator
├── orchestrator_config.json   # Model ayarları
└── requirements.txt           # Python bağımlılıkları

CAD/FreeCAD/06_Assembly/
├── update_vacuum_pads.py      # Vakum padleri güncelleme
├── GFB_60_30RE_S_Model.py     # Ana model script
└── GFB_60_30RE_S.FCStd        # FreeCAD dosyası
```

## Kaynaklar

- [FreeCAD Dokümantasyon](https://wiki.freecad.org/)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Cline MCP](https://github.com/cline/cline)
- [Assembly4](https://wiki.freecad.org/Assembly4)

---

**Güncelleme:** 2026-04-19
**Proje:** CNC Revizyon - LiSEC GFB-60/30RE
