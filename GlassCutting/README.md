# GlassCutting Chrome Extension

Lisec GFB-60/30RE cam kesme makinesi için Chrome eklentisi. G-kod editörü, kesim parametreleri, simülasyon ve makine izleme özellikleri.

## Özellikler

### 📝 G-Kod Editörü
- Syntax highlighting (koyu tema)
- Satır numaraları
- Dosya yükleme/kaydetme
- Örnek G-kod şablonu
- Karakter ve satır sayacı

### ⚙️ Kesim Parametreleri
- **Cam Özellikleri**: Boyut, kalınlık, tip (Float, Lamine, Temperli, Reflekte)
- **Kesim Ayarları**: Hız, basınç, açı, kerteriz kompensasyonu
- **Eksen Ayarları**: X/Y/Z maksimum hız, referans noktaları
- **E-Cam**: Lamine kesim senkronizasyonu ve profil seçimi
- Preset kaydetme/yükleme

### 🎯 Simülasyon
- Gerçek zamanlı G-kod görselleştirme
- 2D kesim yolu simülasyonu
- Konum, mesafe ve süre takibi
- Hız ayarlı animasyon (1x-10x)
- Pause/Resume kontrolleri

### 🖥️ Makine Durumu
- 5 eksen servo pozisyonları (X, Y, Z, Alt, CNC)
- R1-EC I/O modülü LED göstergeleri
- Aktif alarmlar listesi
- EtherCAT bağlantı durumu

## Kurulum

### 1. İkonları Oluştur (İsteğe Bağlı)
```bash
cd GlassCutting/icons
python3 generate-icons.py
```

Veya tarayıcıda:
```
icons/generate-icons.html dosyasını Chrome'da açın
```

### 2. Chrome'a Yükle

1. Chrome'u açın
2. `chrome://extensions/` adresine gidin
3. Sağ üstte **"Geliştirici modu"** nu açın
4. **"Paketlenmemiş öğe yükle"** butonuna tıklayın
5. `GlassCutting` klasörünü seçin

### 3. Eklentiyi Kullanın

- Toolbar'da GlassCutting ikonuna tıklayın
- Veya `Ctrl+Shift+G` kısayolunu kullanın

## Kullanım

### G-Kod Editörü
1. **Yeni**: Boş editör aç
2. **Yükle**: .nc, .gcode, .txt dosyası seç
3. **Kaydet**: G-kod'u dosyaya kaydet
4. **Çalıştır**: Simülasyonu başlat

### Parametreler
1. Cam ve kesim ayarlarını yapılandır
2. **Uygula** butonuna tıkla
3. **Preset Kaydet**: Sık kullanılan ayarları kaydet

### Simülasyon
1. G-kod yazın veya yükleyin
2. **Çalıştır** butonuna basın
3. Simülasyon tab'ında kesim yolunu izleyin
4. Hız slider'ı ile animasyonu hızlandırın

### Makine İzleme
- Gerçek zamanlı servo pozisyonları
- I/O durumu (8 giriş, 8 çıkış LED)
- Alarm listesi
- EtherCAT bağlantı durumu

## Dosya Yapısı

```
GlassCutting/
├── manifest.json           # Extension manifest (v3)
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

## Teknik Detaylar

### İletişim Protokolleri
- **Modbus TCP**: Makine PLC iletişimi
- **EtherCAT**: Servo ve I/O kontrolü
- **Delta NC300**: CNC kontrolör API

### İzinler
- `storage`: Ayarlar ve presetler
- `tabs`: Web sayfa entegrasyonu
- `downloads`: G-kod dosya kaydetme
- `host_permissions`: Tüm URL'ler (drag&drop için)

### Kısayollar
- `Ctrl+Shift+G`: Eklentiyi aç
- Drag&Drop: G-kod dosyasını sayfaya sürükle

## Delta NC300 Entegrasyonu

### Bağlantı Ayarları
```
IP: 192.168.1.100 (varsayılan)
Port: 502 (Modbus TCP)
Polling: 100ms
```

### Desteklenen G-Kodlar
| Kod | Açıklama |
|-----|----------|
| G0  | Hızlı hareket |
| G1  | Doğrusal kesim |
| G21 | Metrik birimler |
| G90 | Mutlak konum |
| G91 | Bağıl konum |
| M30 | Program sonu |

## Gelecek Geliştirmeler

- [ ] 3D simülasyon (Three.js)
- [ ] Gerçek zamanlı makine bağlantısı (WebSocket)
- [ ] G-kod syntax highlighting (CodeMirror)
- [ ] Kesim optimizasyonu (AI)
- [ ] Bulut senkronizasyonu
- [ ] Multi-language support

## Sorun Giderme

### Eklenti görünmüyor
- `chrome://extensions/` sayfasında etkinleştirin
- Chrome'u yeniden başlatın

### Simülasyon çalışmıyor
- Console'da hata mesajlarını kontrol edin (`F12`)
- G-kod formatını kontrol edin

### Makine bağlanmıyor
- IP adresini kontrol edin
- Firewall ayarlarını gözden geçirin

## Lisans

MIT License - CNC Revizyon Team

## Versiyon

**1.0.0** - İlk sürüm
- G-kod editörü
- Parametre yönetimi
- 2D simülasyon
- Makine durumu izleme

---

**Proje**: Lisec GFB-60/30RE Cam Kesme Makinesi Revizyonu
**Tarih**: Nisan 2026
**Ekip**: CNC Revizyon Team
