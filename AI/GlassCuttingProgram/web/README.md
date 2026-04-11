# Glass Cutting Program - Web Interface
# LiSEC GFB-60/30RE Cam Kesme Makinesi

## Offline Mode

Bu uygulama **internet bağlantısı olmadan** da çalışır!

### Offline Özellikler:
- ✅ Sipariş girişi ve yönetimi
- ✅ Nesting optimizasyonu (Guillotine algorithm)
- ✅ Path optimizasyonu (TSP 2-opt)
- ✅ G-Code üretimi (NC300 uyumlu)
- ✅ Lamine cam parametre hesaplama (local formulas)
- ✅ Kusur tespiti (simulated)
- ✅ Canvas visualization

### Online Özellikler (AI API gerekli):
- 🤖 AI destekli optimizasyon (qwen3-max)
- 🤖 AI kod validation (qwen3-coder-plus)
- 🤖 AI lamine parametre tuning (qwen3.5-plus)

---

## Başlatma

### 1. Flask Server

```bash
cd AI/GlassCuttingProgram/web/backend
python3 app.py
```

Server: http://localhost:5001

### 2. Browser

Aç: http://localhost:5001

---

## API Endpoints

| Endpoint | Offline | Online | Description |
|----------|---------|--------|-------------|
| `/api/orders` | ✅ | ✅ | Sipariş CRUD |
| `/api/optimize/local` | ✅ | ✅ | **Offline optimizasyon** |
| `/api/optimize` | ❌ | ✅ | AI optimizasyon |
| `/api/optimize/nesting` | ✅ | ✅ | Nesting only |
| `/api/gcode` | ✅ | ✅ | G-Code output |
| `/api/lamine/calculate` | ✅ | ✅ | Lamine params (local) |
| `/api/machine/info` | ✅ | ✅ | Machine specs |

---

## Offline Detection

Web arayüzü otomatik olarak internet durumunu algılar:

- **Online:** AI modelleri aktif
- **Offline:** Local algorithms kullanılır

Banner gösterir:
```
📡 Offline Mode - Local algoritmalar çalışıyor
```

---

## Local Algorithms

### Nesting
- **Guillotine BestFit** - Optimal parça yerleşimi
- **Maximal Rectangles** - Alternatif algoritma

### Path
- **Nearest Neighbor** - Hızlı çözüm
- **2-opt** - Local search improvement
- **3-opt** - Daha iyi sonuçlar

### G-Code
- NC300 komut seti
- Float/Laminated/Tempered glass modes
- E-Cam profile generation

---

## Directory Structure

```
web/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Flask + CORS
├── frontend/
│   ├── index.html          # Dashboard
│   ├── orders.html         # Order management
│   ├── visualization.html  # Nesting canvas
│   ├── gcode.html          # G-Code viewer
│   ├── lamine.html         # Laminated glass
│   └── static/
│       ├── css/style.css   # Dark theme
│       └── js/
│           ├── app.js      # API + Offline
│           └── visualization.js  # Canvas
```

---

## Requirements

```bash
# Backend
pip install flask flask-cors

# Optional (for AI)
pip install aiohttp
```

---

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers

---

## Tips

1. **Offline çalışma:** Internet bağlantısı kapatın, uygulama yerel algoritmaları kullanır
2. **Sipariş yükle:** "Örnek Sipariş Yükle" butonu ile test
3. **Optimization:** "Optimizasyon Çalıştır" ile nesting + G-code
4. **G-Code:** G-code sekmesinden .nc dosyasını indirin
5. **Canvas:** Visualization sekmesinde yerleşimi görüntüle

---

**Version:** 1.0
**Machine:** LiSEC GFB-60/30RE
**Controller:** Delta NC300