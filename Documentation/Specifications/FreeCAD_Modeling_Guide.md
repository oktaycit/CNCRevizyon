# FreeCAD Modelleme Kılavuzu
## Lisec GFB-60/30RE Cam Kesme Makinesi

## 1. FreeCAD Kurulumu

### 1.1 İndirme ve Kurulum
**macOS:**
```bash
# Homebrew ile kurulum
brew install --cask freecad

# veya DMG dosyasını indirin
# https://github.com/FreeCAD/FreeCAD-Bundle/releases
```

**Windows:**
```
https://github.com/FreeCAD/FreeCAD-Bundle/releases
→ FreeCAD-1.0.0-Windows-x86_64.7z indirin
```

**Linux:**
```bash
# Ubuntu/Debian
sudo add-apt-repository ppa:freecad-maintainers/freecad-stable
sudo apt update
sudo apt install freecad

# Fedora
sudo dnf install freecad
```

### 1.2 Workbench Kurulumu
FreeCAD ile birlikte gelen workbench'ler:
- **Part Design** - Katı modelleme
- **Part** - Boolean işlemleri
- **Assembly4** - Montaj (eklenti olarak kurulur)
- **TechDraw** - Teknik çizim
- **Path** - CAM işlemleri

### 1.3 Eklenti Kurulumu (Addon Manager)
1. **Tools → Addon Manager**
2. Kurulması önerilen eklentiler:
   - **Assembly4** (Montaj için)
   - **Fasteners** (Cıvata, somun modelleri)
   - **Bolt Hole Circle** (Delik deseni)
   - **SheetMetal** (Sac metal işlemleri)

## 2. Proje Dosya Yapısı

```
CAD/
├── FreeCAD/
│   ├── 00_Common/                    # Ortak bileşenler
│   │   ├── Standards.fcstd           # Standart parçalar
│   │   └── Materials.FCMat           # Malzeme tanımları
│   │
│   ├── 01_Motors/                    # Motor modelleri
│   │   ├── ECMA-L11845.fcstd         # 4.5kW X ekseni
│   │   ├── ECMA-E11320.fcstd         # 2.0kW Y/Alt ekseni
│   │   ├── ECMA-C11010.fcstd         # 1.0kW Z ekseni (frenli)
│   │   └── ECMA-E11315.fcstd         # 1.5kW C ekseni (IP67)
│   │
│   ├── 02_Frame/                     # Şase
│   │   ├── MainFrame.fcstd           # Ana şase
│   │   ├── XAxisPortal.fcstd         # X ekseni portalı
│   │   └── SupportLegs.fcstd         # Destek ayakları
│   │
│   ├── 03_LinearGuides/              # Lineer raylar
│   │   ├── HIWIN_HGH25_X.fcstd       # X ekseni rayları
│   │   └── HIWIN_HGH25_Y.fcstd       # Y ekseni rayı
│   │
│   ├── 04_CuttingHead/               # Kesim kafası
│   │   ├── HeadAssembly.fcstd        # Kafa montajı
│   │   ├── ZAxis.fcstd               # Z ekseni ünitesi
│   │   └── WheelMount.fcstd          # Kesim tekeri montajı
│   │
│   ├── 05_Electronics/               # Elektronik
│   │   ├── R1-EC_Housing.fcstd       # R1-EC kutu
│   │   ├── Sensor_Bracket.fcstd      # Sensör braketi
│   │   └── CableCarrier.fcstd        # Kablo kanalı
│   │
│   ├── 06_Assembly/                  # Ana montaj
│   │   └── GFB-60-30RE_Main.fcstd    # Tam montaj
│   │
│   └── 07_Exports/                   # Export dosyaları
│       ├── STEP/                     # .step dosyaları
│       ├── STL/                      # .stl dosyaları
│       └── DXF/                      # .dxf dosyaları
```

## 3. Delta ECMA Motor Modelleme

### 3.1 ECMA-L11845 (4.5kW X Ekseni)

**Motor Ölçüleri:**
```
Flanş: 180 mm
Mil Çapı: 48 mm
Mil Uzunluğu: 110 mm
Gövde Uzunluğu: 215 mm (frensiz)
Toplam Uzunluk: 340 mm (konektörlü)
```

**Modelleme Adımları:**

1. **Yeni Dosya Oluştur**
   - File → New
   - `ECMA-L11845.fcstd` olarak kaydet
   - Part Design Workbench'e geç

2. **Gövde Çizimi (Body)**
   ```
   - XY Plane seç → Create new sketch
   - Merkezde daire çiz (Ø180 mm flanş)
   - Konsantrik daire (Ø130 mm motor gövde)
   - Pad (Extrude): 215 mm
   ```

3. **Mil Çizimi**
   ```
   - Gövde ön yüzeyini seç → Create sketch
   - Merkezde daire (Ø48 mm)
   - Pad: 110 mm
   - Keyway (kama yuvası): 14x9 mm
   ```

4. **Montaj Delikleri**
   ```
   - Flanş yüzeyini seç → Create sketch
   - Bolt hole circle: 4x Ø14 mm
   - PCD (Pitch Circle Diameter): Ø215 mm
   ```

5. **Konektör Kabuğu**
   ```
   - Gövde üst kısmına sketch
   - Dikdörtgen: 60x40 mm
   - Pad: 50 mm
   - Shell: 2 mm duvar kalınlığı
   ```

### 3.2 ECMA-C11010 (1.0kW Frenli Z Ekseni)

**Motor Ölçüleri:**
```
Flanş: 100 mm
Mil Çapı: 24 mm
Mil Uzunluğu: 50 mm
Gövde Uzunluğu: 165 mm (frenli)
Fren Çapı: Ø90 mm
```

**Fren Modelleme:**
```
1. Motor arka yüzeyine sketch
2. Daire çiz (Ø90 mm)
3. Pad: 40 mm (fren gövdesi)
4. İçten boşalt (Shell): 3 mm
5. Kablo giriş deliği (Ø12 mm)
```

### 3.3 Motor STEP Dosyalarını Kullanma

Delta'nın sağladığı STEP dosyaları varsa:
1. **File → Import**
2. STEP dosyasını seçin
3. Part Workbench'e geçin
4. **Part → Create shape from mesh** (gerekirse)
5. Parçaları birleştirin: **Part → Boolean → Fuse**

## 4. Lineer Ray Modelleme (HIWIN HGH25CA)

### 4.1 Ray Modeli

**HIWIN HGH25CA Ölçüleri:**
```
Genişlik: 23 mm
Yükseklik: 40 mm
Delik Aralığı: 60 mm (standart)
Delik Çapı: Ø7 mm (M6 cıvata için)
```

**Modelleme:**
```
1. XY Plane → Sketch
2. Dikdörtgen: 23x40 mm
3. Pad: Ray uzunluğu (6000 mm X için)
4. Üst yüzey → Sketch
5. Delikler: Ø7 mm, 60 mm aralıklı
6. Linear Pattern: Delikleri çoğalt
```

### 4.2 Kızak (Block) Modeli

```
1. Sketch: 60x40 mm taban
2. Pad: 80 mm (kızak uzunluğu)
3. Üst kısmı şekillendir (eğimli yüzeyler)
4. Yağlama deliği (Ø4 mm)
5. Grease nipple mount
```

## 5. Şase (Frame) Modelleme

### 5.1 Ana Şase Profilleri

**Profil Seçimi:**
```
Ana Taşıyıcı: 80x80x4 mm çelik profil
Enlem Destek: 60x60x4 mm çelik profil
```

**Modelleme:**
```
1. Sketch → Rectangle: 80x80 mm
2. Pad: 6000 mm (X profili)
3. Shell: 4 mm duvar kalınlığı
4. MultiBody ile 4 adet profil oluştur
5. Enlem profilleri: 3000 mm
```

### 5.2 Köşe Takviyeleri

```
1. Sketch → Üçgen çizimi
2. Pad: 8 mm (levha kalınlığı)
3. Delikler: M8 cıvata için Ø9 mm
4. Pattern: Köşelere çoğalt
```

## 6. Assembly4 Montaj

### 6.1 Assembly4 Kurulumu
1. **Tools → Addon Manager**
2. **Assembly4** bul ve kur
3. FreeCAD'i yeniden başlat

### 6.2 Montaj Adımları

**Ana Montaj Dosyası Oluştur:**
1. File → New
2. `GFB-60-30RE_Main.fcstd` olarak kaydet
3. Assembly4 Workbench'e geç

** LCS (Local Coordinate System) Ekle:**
```
1. Her parçaya referans LCS ekle
2. Assembly → Create new LCS
3. Parça koordinat sistemini tanımla
```

**Parçaları Yerleştir:**
```
1. Assembly → Insert a part
2. Şase profillerini ekle
3. Lineer rayları ekle
4. Motorları ekle
5. Bağlantıları tanımla
```

**Bağlantı Türleri:**
```
- Fixed: Sabit bağlantı (ray-şase)
- Revolute: Döner bağlantı (mil-kaplaj)
- Slider: Lineer hareket (kızak-ray)
```

### 6.3 Montaj Sırası

```
1. Ana şase yerleştir (Ground)
2. X ekseni lineer raylarını monte et
3. X ekseni portalını yerleştir
4. Y ekseni rayını monte et
5. Y ekseni kızakı yerleştir
6. Z ekseni ünitesini monte et
7. Servo motorları yerleştir
8. Kaplajları ekle
```

## 7. Teknik Çizim (TechDraw)

### 7.1 Çizim Sayfası Oluştur

1. **TechDraw Workbench'e geç**
2. **Insert Default Page** (A1 format)
3. Sayfa özelliklerini ayarla:
   - Scale: 1:10 (ana görünüm)
   - Units: mm
   - Tolerance: ISO 2768-m

### 7.2 Görünüşler Ekle

```
1. View → Front (Ön görünüş)
2. View → Top (Üst görünüş)
3. View → Right (Sağ yan)
4. View → Isometric (İzometrik)
5. Section View (Kesit görünüş)
```

### 7.3 Ölçülendirme

```
1. Dimension tools kullanın
2. Kritik ölçüleri ekleyin:
   - Eksenler arası mesafe
   - Montaj delikleri
   - Toleranslar
3. Yüzey işleme sembolleri
4. Geometrik toleranslar
```

## 8. Export İşlemleri

### 8.1 STEP Export (Üretim için)

```
1. File → Export
2. Format: STEP (*.stp, *.step)
3. Options:
   - Schema: AP214
   - Unit: mm
   - Solid: Yes
```

### 8.2 STL Export (3D Yazıcı için)

```
1. File → Export
2. Format: STL (*.stl)
3. Options:
   - Mesh deviation: 0.1 mm
   - Binary format
```

### 8.3 DXF Export (Lazer kesim için)

```
1. TechDraw sayfasından
2. File → Export
3. Format: DXF (*.dxf)
4. Scale: 1:1
```

## 9. Malzeme Tanımlama

### 9.1 Malzeme Kütüphanesi

```
FreeCAD Material Workbench → Materials:
- Steel (Çelik): S235JR, S355
- Aluminum (Alüminyum): 6061-T6, 7075-T6
- Stainless Steel (Paslanmaz): 304, 316
- Cast Iron (Döküm Demir): GG25
```

### 9.2 Malzeme Atama

```
1. Part Design Workbench
2. Body seç
3. Material → Assign material
4. Malzeme seç
5. Properties otomatik doldurulur:
   - Density (Yoğunluk)
   - Young's Modulus
   - Yield Strength
```

## 10. Parametrik Modelleme

### 10.1 Spreadsheet Kullanımı

**Parametre Tablosu Oluştur:**
```
1. Spreadsheet Workbench'e geç
2. Create new spreadsheet
3. Parametreleri girin:

   | Name          | Value  | Unit |
   |---------------|--------|------|
   | Frame_Length  | 6000   | mm   |
   | Frame_Width   | 3000   | mm   |
   | Rail_Length_X | 6000   | mm   |
   | Rail_Length_Y | 3000   | mm   |
   | Motor_X_Power | 4500   | W    |
```

### 10.2 Parametre Bağlantısı

```
1. Sketch'e git
2. Constraint seç
3. Değer yerine: `=Spreadsheet.Frame_Length`
4. Parametre değiştiğinde model güncellenir
```

## 11. Makro Kaydetme

### 11.1 Standart İşlemler için Makro

**Örnek: Motor Montaj Delikleri**
```python
# FreeCAD Python Macro
import FreeCAD as App
import Part

def create_motor_bolt_circle(pcd, hole_diameter, num_holes):
    doc = App.ActiveDocument
    sketch = doc.ActiveObject
    
    # PCD: Pitch Circle Diameter
    # hole_diameter: Delik çapı
    # num_holes: Delik sayısı
    
    radius = pcd / 2
    for i in range(num_holes):
        angle = 360 / num_holes * i
        x = radius * math.cos(math.radians(angle))
        y = radius * math.sin(math.radians(angle))
        # Delik ekle...
```

### 11.2 Makro Kaydetme
```
1. Macro → Start recording
2. İşlemi yap
3. Macro → Stop recording
4. Macro → Save as...
```

## 12. Proje Yönetimi

### 12.1 Versiyon Kontrolü

```
CAD/FreeCAD/
├── v1.0/           # İlk versiyon
├── v1.1/           # Motor güncellemesi
├── v2.0/           # EtherCAT revizyon
└── Current/        # Güncel çalışma
```

### 12.2 Yedekleme

```
1. File → Save a copy...
2. Tarihli dosya adı: GFB-60-30RE_20260403.fcstd
3. Cloud storage (Git LFS, Dropbox, etc.)
```

## 13. Performans İpuçları

### 13.1 Büyük Montajlar

```
- Simplify parts: Detayları azalt
- Use LOD (Level of Detail): Basitleştirilmiş modeller
- Suppress features: Gereksiz özellikleri kapat
- Work in wireframe mode: Görsel yükü azalt
```

### 13.2 Dosya Boyutu

```
- Purge unused: Kullanılmayan öğeleri sil
- Reduce mesh density: STL export için
- Compress STEP: AP214 schema
```

## 14. Hata Ayıklama

### 14.1 Yaygın Hatalar

| Hata | Neden | Çözüm |
|------|-------|-------|
| Topological naming | Sketch referansı kayıp | Model tree'i kontrol et |
| Circular dependency | Döngüsel bağımlılık | Feature sırasını düzelt |
| Self-intersecting | Kendi içinde kesişim | Sketch'i düzelt |
| Export failure | Invalid geometry | Part → Refine shape |

## 15. Kaynaklar

### 15.1 FreeCAD Dokümantasyon
- **Resmi Dokümantasyon:** https://wiki.freecad.org/
- **Türkçe Kaynaklar:** https://wiki.freecad.org/Manual:Türkçe
- **Forum:** https://forum.freecad.org/

### 15.2 Video Eğitim
- **FreeCAD 1.0 Tutorial:** https://www.youtube.com/c/FreeCAD
- **Assembly4 Tutorial:** https://www.youtube.com/results?search_query=assembly4+freesad

### 15.3 Delta ECMA CAD Modelleri
- **Delta Download Center:** https://www.delta-automation.com/tr/support/download/
- Motor boyutları için datasheet'leri kullanın

## 16. Modelleme Checklist

### 16.1 Motor Modelleme
- [ ] ECMA-L11845 (4.5kW) modeli
- [ ] ECMA-E11320 (2.0kW) modeli
- [ ] ECMA-C11010 (1.0kW frenli) modeli
- [ ] ECMA-E11315 (1.5kW IP67) modeli
- [ ] Tüm ölçüler datasheet ile doğrulandı

### 16.2 Mekanik Parçalar
- [ ] Ana şase profilleri
- [ ] X ekseni portalı
- [ ] Lineer raylar (HIWIN HGH25)
- [ ] Kızaklar
- [ ] Kesim kafası montajı
- [ ] Z ekseni ünitesi
- [ ] Kaplaj ve mil bağlantıları

### 16.3 Elektronik
- [ ] R1-EC modül kutusu
- [ ] Sensör montaj braketleri
- [ ] Kablo kanalı/tela
- [ ] Pano yerleşimi

### 16.4 Montaj ve Çizim
- [ ] Assembly4 montaj tamamlandı
- [ ] Tüm hareketler simüle edildi
- [ ] Teknik çizimler oluşturuldu
- [ ] STEP export alındı
- [ ] BOM listesi çıkarıldı