# 🚀 GlassCutting Pro - Kurulum Kılavuzu

## ✅ Adım Adım Kurulum

### 1️⃣ Chrome Extensions Sayfasını Aç
```
1. Google Chrome'u aç
2. Adres çubuğuna yaz: chrome://extensions/
3. Enter'a bas
```

### 2️⃣ Geliştirici Modunu Aç
```
- Sağ üst köşede "Geliştirici modu" anahtarını bul
- Anahtara tıkla (mavi renk olacak)
```

### 3️⃣ Extension'ı Yükle
```
1. "Paketlenmemiş öğe yükle" butonuna tıkla
2. Klasör seçme penceresi açılacak
3. Şu klasöre git: AI/GlassCuttingProgram/web/
4. Klasörü seç ve "Klasörü Seç" butonuna tıkla
```

### 4️⃣ Extension'ı Sabitle
```
1. Chrome araç çubuğunda puzzle parçası ikonuna tıkla
2. "GlassCutting Pro" bul
3. Yanındaki raptiye ikonuna tıkla (sabitlenmiş olacak)
```

### 5️⃣ Kullanmaya Başla!
```
- Araç çubuğunda GlassCutting Pro ikonuna tıkla
- Veya kısayolu kullan
```

---

## 📁 Klasör Yapısı

```
AI/GlassCuttingProgram/web/
├── manifest.json         ✅ Extension ayarları
├── app.html              ✅ Ana arayüz
├── app.css               ✅ Tasarım
├── app.js                ✅ Uygulama mantığı
├── app.background.js     ✅ Arka plan servisi
└── icons/
    ├── icon16.png        ✅ 16x16 ikon
    ├── icon48.png        ✅ 48x48 ikon
    ├── icon128.png       ✅ 128x128 ikon
    └── icon256.png       ✅ 256x256 ikon
```

---

## ⚙️ Özellikler

### G-Kod Editörü
- 📝 Yeni G-kod oluştur
- 📂 Dosya yükle (.nc, .gcode, .txt)
- 💾 Dosya kaydet
- ▶ Simülasyonda çalıştır

### Parametreler
- 📦 Cam özellikleri (boyut, kalınlık, tip)
- ✂️ Kesim ayarları (hız, basınç, açı)
- 📐 Eksen ayarları (X/Y/Z hız)
- 🔷 E-Cam (lamine cam senkronizasyonu)

### Simülasyon
- 🎯 Gerçek zamanlı görselleştirme
- 📊 Konum takibi (X, Y)
- ⏱️ Mesafe ve süre
- 🎚️ Hız kontrolü (1x-10x)

### Makine Durumu
- 🖥️ Servo pozisyonları (5 eksen)
- 💡 I/O LED göstergeleri
- ⚠️ Alarm listesi
- 🔗 Bağlantı durumu

---

## 🔧 Sorun Giderme

### Extension görünmüyor
❓ **Çözüm:** 
- chrome://extensions/ sayfasında etkinleştirin
- Chrome'u yeniden başlatın

### İkonlar yüklenmedi
❓ **Çözüm:**
- icons klasörünün varlığını kontrol edin
- PNG dosyalarının bozuk olmadığını kontrol edin

### G-Kod yüklenemiyor
❓ **Çözüm:**
- Dosya uzantısının .nc, .gcode, .ngc veya .txt olduğundan emin olun
- Dosya izinlerini kontrol edin

### Simülasyon çalışmıyor
❓ **Çözüm:**
- G-kod formatını kontrol edin
- Örnek G-kod ile test edin

---

## 📝 Kullanım Örnekleri

### Örnek G-Kod
```gcode
; Lisec GFB-60/30RE - Örnek Program
G21 ; Metrik birimler
G90 ; Mutlak konum

G0 Z50 ; Güvenlik pozisyonu
G0 X0 Y0 ; Başlangıç

G1 Z5 F500 ; Kesim derinliği
G1 X2000 F3000 ; X ekseni kesim
G1 Y1500 ; Y ekseni kesim

G0 Z50 ; Güvenlik pozisyonu
M30 ; Program sonu
```

---

## ⌨️ Kısayollar

| İşlem | Yöntem |
|-------|--------|
| Extension'ı aç | İkona tıkla |
| Yeni sekmede aç | Ctrl + Tık |
| Sayfayı yenile | F5 |

---

## 🔐 İzinler

Bu extension şunları gerektirir:
- **storage**: Ayarları kaydetmek için
- **tabs**: Sekme yönetimi için
- **downloads**: Dosya kaydetmek için

---

## 📞 Destek

### Dökümanlar
- `README.md` - Detaylı döküman
- `QUICKSTART.md` - Hızlı başlangıç
- `test.html` - Test sayfası

### Yardım
1. Extension içindeki `?` butonuna tıkla
2. README.md dosyasını oku
3. Test sayfasını çalıştır

---

## ✨ Sürüm Bilgisi

**Sürüm**: 2.0.0  
**Tarih**: Nisan 2026  
**Tip**: Chrome Extension  
**Ekip**: CNC Revizyon Team  

---

## 🎉 Hazır!

Extension başarıyla kuruldu. Kullanmaya başlayabilirsiniz!

**GlassCutting Pro** ile cam kesim programlarınızı kolayca yönetin. 🚀
