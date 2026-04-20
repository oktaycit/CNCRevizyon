# LiSEC GFB 60/30RE-S Görsel Referans Kılavuzu

## 🎯 Özet

LiSEC GFB 60/30RE-S cam kesme makinesi için FreeCAD modellemenizde kullanabileceğiniz referans görselleri bulma ve organize etme kılavuzu.

---

## 📂 Oluşturulan Klasör Yapısı

```
CAD/Reference_Images/
├── README.md                    # Bu dosya
├── download_images.sh           # Bash indirme scripti
├── download_reference_images.py # Python indirme scripti
├── 01_Overall/                  # Genel makine görünümü
├── 02_CuttingHead/              # Kesim kafası detayları
├── 03_Frame/                    # Şase detayları
├── 04_LinearGuides/             # Lineer kılavuzlar
├── 05_Motors/                   # Motorlar
├── 06_Electronics/              # Elektronik
└── 07_Conveyor/                 # Konveyör sistemi
```

---

## 🔍 Görsel Bulma Kaynakları

### 1. Resmi LiSEC Kaynakları

**LiSEC Web Sitesi:**
```
https://www.lisec.com/
```

**Ürün Sayfaları:**
- GFB Serisi: `https://www.lisec.com/en/products/systems/cnc-cutting-bridges`
- Tüm Ürünler: `https://www.lisec.com/en/products`

**LiSEC YouTube:**
```
https://www.youtube.com/user/LiSECGmbH
```

### 2. Ürün Kataloğu Siteleri

**DirectIndustry:**
```
https://www.directindustry.com/industrial-supplier/lisec-glass-cutting-machine-261686.html
```

**ArchExpo:**
```
https://www.archiexpo.com/architecture-design-manufacturer/glass-cutting-machine-4369.html
```

### 3. İkinci El Makine Siteleri

**MachineSeeker:**
```
https://www.machineseeker.com/msearch?query=LiSEC+GFB
```

**Exapro:**
```
https://www.exapro.com/glass-cutting-machines-c276/
```

**Machinio:**
```
https://www.machinio.com/listings/glass-cutting-machine
```

### 4. Video Platformları

**YouTube Arama:**
```
https://www.youtube.com/results?search_query=LiSEC+GFB+60+30RE
https://www.youtube.com/results?search_query=LiSEC+glass+cutting
https://www.youtube.com/results?search_query=CNC+glass+cutting+bridge
```

**Vimeo:**
```
https://vimeo.com/search?q=LiSEC+glass+cutting
```

### 5. Görsel Arama Motorları

**Google Görseller:**
```
https://www.google.com/search?q=LiSEC+GFB+60+30RE+glass+cutting+machine&tbm=isch
```

**Bing Görseller:**
```
https://www.bing.com/images/search?q=LiSEC+GFB+glass+cutting
```

**Yandex Görseller:**
```
https://yandex.com/images/search?text=LiSEC+GFB+glass+cutting+machine
```

---

## 📋 Arama Anahtar Kelimeleri

### İngilizce
- `LiSEC GFB 60/30RE`
- `LiSEC GFB 6030 RE`
- `LiSEC CNC cutting bridge`
- `LiSEC vertical glass cutter`
- `LiSEC laminated glass cutting`
- `LiSEC GFB-S series`
- `glass cutting gantry machine`
- `CNC glass cutting system`

### Türkçe
- `LiSEC cam kesme makinesi`
- `dikey cam kesme`
- `CNC cam kesme köprüsü`
- `lamine cam kesme makinesi`

### Almanca (LiSEC Avusturya menşeili)
- `LiSEC Glasbrücke`
- `LiSEC Glasschneidemaschine`
- `GFB 60/30RE Glas`

---

## 📷 Hangi Görselleri Toplamalıyınız?

### 01_Overall/ - Genel Görünüm
- [ ] İzometrik genel görünüm
- [ ] Ön görünüş
- [ ] Yan görünüş
- [ ] Üst görünüş
- [ ] Makine çalışırken (aksiyon çekimi)

### 02_CuttingHead/ - Kesim Kafası
- [ ] Üst kesim kafası (VB) yakın çekim
- [ ] Alt kesim kafası (NB) yakın çekim
- [ ] Z ekseni mekanizması
- [ ] Kesim tekeri holder
- [ ] Pnömatik baskı ünitesi
- [ ] Motor bağlantısı

### 03_Frame/ - Şase
- [ ] Köprü konstrüksiyonu
- [ ] Köşe takviyeleri
- [ ] Ayarlanabilir ayaklar
- [ ] Profil bağlantıları
- [ ] Kaynak dikişleri

### 04_LinearGuides/ - Lineer Kılavuzlar
- [ ] X ekseni lineer ray
- [ ] Y ekseni lineer ray
- [ ] Lineer buşing/kızak
- [ ] Ray montaj detayı
- [ ] Koruyör kapaklar

### 05_Motors/ - Motorlar
- [ ] X ekseni servo motor
- [ ] Y ekseni servo motor
- [ ] Z ekseni servo motor
- [ ] Motor kuplajı
- [ ] Redüktör/şanzıman

### 06_Electronics/ - Elektronik
- [ ] Kontrol paneli (HMI)
- [ ] Elektrik kabinetı
- [ ] PLC ünitesi
- [ ] Sensörler (proximity, encoder)
- [ ] Kablo kanalları

### 07_Conveyor/ - Konveyör
- [ ] Rulo konveyör
- [ ] Cam destek profilleri
- [ ] Vakum emme sistemi
- [ ] Konveyör tahrik ünitesi

---

## 🛠️ Kullanım Talimatları

### Yöntem 1: Manuel İndirme (Önerilen)

1. **Yukarıdaki kaynaklardan birini açın**
2. **İlgili görselleri bulun**
3. **Sağ tık → Resmi farklı kaydet**
4. **Uygun klasöre kaydedin:**
   ```
   CAD/Reference_Images/01_Overall/image_name.jpg
   ```

### Yöntem 2: Python Script

1. **Script'i düzenleyin:**
   ```bash
   # download_reference_images.py dosyasını açın
   # IMAGE_URLS sözlüğüne URL'leri ekleyin
   ```

2. **Çalıştırın:**
   ```bash
   cd /Users/oktaycit/Projeler/CNCRevizyon/CAD/Reference_Images
   python3 download_reference_images.py
   ```

### Yöntem 3: Bash Script

1. **Script'i çalıştırın:**
   ```bash
   ./download_images.sh
   ```

2. **Çıkan kaynaklardan manuel indirin**

---

## 📐 FreeCAD Modelleme İçin İpuçları

### Ölçek Referansı Olarak Kullanın

1. **Görseli FreeCAD'e import edin:**
   - Image Workbench → Create image
   - Görseli seçin
   - Ölçek referansı verin (örn: 6000 mm çalışma alanı)

2. **Üzerinden geçin (trace):**
   - Sketcher Workbench
   - Görsel üzerine profile çizin
   - Boyutlandırın

3. **3D model oluşturun:**
   - Part Design Workbench
   - Sketch'i pad/extrude edin

### Görünüşlere Ayırın

- **Ön görünüş:** Şase yüksekliği, köprü yapısı
- **Yan görünüş:** X ekseni hareketi, motor yerleşimi
- **Üst görünüş:** Çalışma alanı, Y ekseni hareketi

---

## ⚠️ Telif Hakkı Uyarısı

- Görseller sadece **referans amaçlı** kullanılmalıdır
- Ticari kullanım için görsel sahiplerinden izin alın
- LiSEC marka görselleri LiSEC GmbH'nin mülkiyetindedir
- FreeCAD modelinizde doğrudan kullanmayın, sadece modelleme referansı olarak kullanın

---

## 📞 LiSEC İletişim (Yüksek Çözünürlüklü Görseller İçin)

**LiSEC Glass GmbH**
- Web: https://www.lisec.com/
- Email: info@lisec.com
- Telefon: +43 2176 2001-0
- Adres: Josef-List-Straße 1, 2100 Korneuburg, Austria

**Türkiye Distribütörü:**
- Firma: [Distribütör bilgisi web sitesinden kontrol edin]
- Email: [İletişim formu doldurun]

---

## 🔗 Faydalı Bağlantılar

- [FreeCAD Image Workbench](https://wiki.freecad.org/Image_Workbench)
- [FreeCAD Sketcher](https://wiki.freecad.org/Sketcher_Workbench)
- [FreeCAD Part Design](https://wiki.freecad.org/PartDesign_Workbench)
- [HIWIN Lineer Ray Katalog](https://www.hiwin.com/products/linear-guideway)
- [Delta ECMA Motor Datasheetleri](https://www.delta-automation.com/tr/products/detail/ECMA/)

---

**Oluşturma Tarihi:** 2026-04-19
**Proje:** CNC Revizyon - GFB 60/30RE-S Modelleme
**Yazar:** CNC Revizyon Proje Ekibi
