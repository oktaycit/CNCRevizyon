# GlassCutting Chrome App - Kurulum Rehberi

## 📦 Chrome App Olarak Çalıştırma

GlassCutting artık **browser bağımsız Chrome uygulaması** olarak çalışabilir.

### Adım 1: İkonları Oluştur (İsteğe Bağlı)

Eğer ikonlar mevcut değilse:

```bash
cd GlassCutting/icons
python3 generate-icons.py
```

Veya tarayıcıda:
```
icons/generate-icons.html dosyasını Chrome'da açın
```

### Adım 2: Chrome'a Yükle

1. **Chrome'u açın**

2. **Extensions sayfasına gidin:**
   ```
   chrome://extensions/
   ```

3. **Geliştirici Modunu Açın:**
   - Sağ üst köşede "Geliştirici modu" anahtarını **AÇIK** konuma getirin

4. **Paketlenmemiş Öğeyi Yükle:**
   - "Paketlenmemiş öğe yükle" butonuna tıklayın
   - `GlassCutting` klasörünü seçin

### Adım 3: Chrome App Olarak Başlat

#### Yöntem A: Chrome App Launcher (Önerilen)

1. Chrome'da yeni sekme açın
2. Sol alt köşede **Uygulama Başlatıcı** (App Launcher) ikonuna tıklayın
3. **GlassCutting** uygulamasını bulun
4. Çift tıklayarak bağımsız uygulama olarak başlatın

#### Yöntem B: Doğrudan URL ile

Chrome'da şu adresi açın:
```
chrome://apps/
```
GlassCutting ikonuna tıklayın.

#### Yöntem C: Komut Satırı ile (macOS)

```bash
# Bağımsız pencere modu
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --app=chrome-extension://EXTENSION_ID/popup/popup.html

# Tam ekran kiosk modu
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --app=chrome-extension://EXTENSION_ID/popup/popup.html \
  --kiosk
```

> **Not:** `EXTENSION_ID` yerine Chrome extensions sayfasında görünen extension ID'yi yazın.

### Adım 4: Masaüstü Kısayolu Oluştur

1. `chrome://extensions/` sayfasına gidin
2. GlassCutting extension'ını bulun
3. **"Kısayol oluştur"** butonuna tıklayın
4. "Pencere olarak aç" seçeneğini işaretleyin
5. Masaüstünde çift tıklayarak başlatın

---

## 🖥️ Özellikler

### Chrome App Avantajları

- ✅ **Browser bağımsız** - Adres çubuğu, sekme yok
- ✅ **Tam ekran mod** - Kiosk modunda çalışabilir
- ✅ **Masaüstü kısayolu** - Tek tıkla başlatma
- ✅ **Sistem tepsisi** - Arka planda çalışabilir
- ✅ **Offline çalışma** - İnternet bağlantısı gerekmez

### Uygulama Özellikleri

| Özellik | Açıklama |
|---------|----------|
| 📝 G-Kod Editörü | Syntax highlighting, dosya yükleme/kaydetme |
| ⚙️ Kesim Parametreleri | Cam boyutu, hız, basınç, E-Cam senkronizasyonu |
| 🎯 Simülasyon | 2D kesim yolu görselleştirme, animasyon |
| 🖥️ Makine Durumu | Servo pozisyonları, I/O LED'leri, alarmlar |

---

## 🔧 Yapılandırma

### manifest.json Değişiklikleri

Chrome App için gerekli değişiklikler:

```json
{
  "manifest_version": 3,
  "app": {
    "background": {
      "scripts": ["app.background.js"]
    }
  },
  "permissions": [
    "storage",
    "tabs",
    "downloads",
    "appWindow"
  ]
}
```

### app.background.js

Bu dosya Chrome App başlatıldığında ana pencereyi açar:

```javascript
chrome.app.runtime.onLaunched.addListener(() => {
  chrome.app.window.create('popup/popup.html', {
    bounds: {
      width: 1024,
      height: 768
    },
    frame: 'chrome',
    resizable: true
  });
});
```

---

## 🌐 Çoklu Dil Desteği

### Mevcut Diller

- 🇹🇷 **Türkçe** (varsayılan)
- 🇬🇧 **English**

### Dil Değiştirme

Chrome App otomatik olarak sistem dilini kullanır. Dil değiştirmek için:

1. Chrome Ayarlar > Diller
2. Tercih edilen dili üst sıraya taşıyın
3. Uygulamayı yeniden başlatın

---

## 🐛 Sorun Giderme

### Uygulama görünmüyor

```bash
# Chrome'u yeniden başlatın
# Extensions sayfasında etkinleştirildiğinden emin olun
chrome://extensions/
```

### İkonlar görünmüyor

```bash
cd GlassCutting/icons
python3 generate-icons.py
```

### Pencere açılmıyor

1. `chrome://extensions/` sayfasında hata mesajlarını kontrol edin
2. Console'u açın (F12) ve hataları inceleyin
3. `app.background.js` dosyasının doğru yüklendiğinden emin olun

### Kiosk moddan çıkılamıyor

- **Windows/Linux:** `Alt + F4`
- **macOS:** `Cmd + Q`

---

## 📁 Dosya Yapısı

```
GlassCutting/
├── manifest.json           # Chrome App manifest (v3)
├── app.background.js       # App başlatma scripti
├── _locales/
│   ├── tr/
│   │   └── messages.json   # Türkçe çeviriler
│   └── en/
│       └── messages.json   # İngilizce çeviriler
├── icons/
│   ├── icon16.png
│   ├── icon48.png
│   ├── icon128.png
│   └── generate-icons.html
├── popup/
│   ├── popup.html          # Ana arayüz
│   ├── popup.css           # Stiller
│   └── popup.js            # UI mantığı
├── background/
│   └── background.js       # Service worker
├── content/
│   └── content.js          # Web sayfa entegrasyonu
└── simulation/
    └── simulation.js       # Simülasyon modülü
```

---

## 🚀 Komut Satırı Seçenekleri

### macOS

```bash
# Normal app modu
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --app="chrome-extension://EXTENSION_ID/popup/popup.html"

# Kiosk modu (tam ekran)
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --app="chrome-extension://EXTENSION_ID/popup/popup.html" \
  --kiosk

# Belirli boyutta pencere
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --app="chrome-extension://EXTENSION_ID/popup/popup.html" \
  --window-size=1280,720 \
  --window-position=100,100
```

### Windows

```batch
REM Normal app modu
chrome.exe --app="chrome-extension://EXTENSION_ID/popup/popup.html"

REM Kiosk modu
chrome.exe --app="chrome-extension://EXTENSION_ID/popup/popup.html" --kiosk
```

### Linux

```bash
# Normal app modu
google-chrome --app="chrome-extension://EXTENSION_ID/popup/popup.html"

REM Kiosk modu
google-chrome --app="chrome-extension://EXTENSION_ID/popup/popup.html" --kiosk
```

---

## 📊 Teknik Spesifikasyonlar

| Özellik | Değer |
|---------|-------|
| Manifest Version | 3 |
| Min Chrome Version | 88+ |
| App Type | Chrome Packaged App |
| Window Mode | Frame: chrome, Resizable: true |
| Default Size | 1024 x 768 |
| Min Size | 800 x 600 |
| Offline Support | ✅ Tam destek |
| i18n Support | ✅ TR/EN |

---

## 🎯 Sonraki Adımlar

1. ✅ Chrome App olarak çalıştır
2. [ ] Gerçek zamanlı makine bağlantısı (WebSocket/Modbus TCP)
3. [ ] 3D simülasyon (Three.js)
4. [ ] Kesim optimizasyonu (AI entegrasyonu)
5. [ ] Bulut senkronizasyonu

---

**Versiyon:** 1.0.0  
**Güncelleme:** Chrome App Desteği Eklendi  
**Tarih:** Nisan 2026

---

**Proje:** Lisec GFB-60/30RE Cam Kesme Makinesi Revizyonu  
**Ekip:** CNC Revizyon Team
