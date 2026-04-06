# Fusion 360 Modelleme Kılavuzu
## Lisec GFB 60-30 Cam Kesme Makinesi

## 1. Fusion 360 Proje Kurulumu

### 1.1 Yeni Tasarım Başlatma
1. Fusion 360'ı açın
2. **File** → **New Design** seçin
3. Units: **Millimeters** olarak ayarlayın
4. Design'i `CAD/Assembly/GFB60-30_MainAssembly.f3d` olarak kaydedin

### 1.2 Design Grid Ayarları
```
Grid Type: Rectangular
Grid Spacing: 100 mm
Snap Spacing: 10 mm
```

## 2. Modelleme Sırası (Önerilen)

### 2.1 Ana Şase (Frame)
**Dosya:** `CAD/Parts/Frame/MainFrame.f3d`

| Parça | Malzeme | Kalınlık | Açıklama |
|-------|---------|----------|----------|
| Ana Profil | Çelik Profil | 80x80x4 mm | Uzunlamasına taşıyıcı |
| Enlem Profil | Çelik Profil | 60x60x4 mm | Enlem destek |
| Ayaklar | Çelik Levha | 10 mm | Seviye ayakları |
| Köşe Takviyeleri | Çelik Levha | 8 mm | Köşe güçlendirme |

**Modelleme Adımları:**
1. Sketch → Rectangle ile ana profil kesitini çizin (80x80 mm)
2. Extrude ile 6000 mm uzunluğunda profil oluşturun
3. Pattern → Rectangular Pattern ile 4 adet ana profil oluşturun
4. Benzer şekilde enlem profilleri ekleyin (3000 mm)
5. Köşe takviyelerini ekleyin
6. Ayak montaj noktalarını oluşturun

### 2.2 X Ekseni Portalı
**Dosya:** `CAD/Parts/Frame/XAxisPortal.f3d`

| Özellik | Değer |
|---------|-------|
| Uzunluk | 3200 mm |
| Yükseklik | 800 mm |
| Malzeme | Alüminyum Profil 100x100 mm |

### 2.3 Y Ekseni Kızak
**Dosya:** `CAD/Parts/CuttingHead/YAxisCarriage.f3d`

| Özellik | Değer |
|---------|-------|
| Genişlik | 600 mm |
| Yükseklik | 200 mm |
| Lineer Ray | HIWIN HGH25CA |

### 2.4 Kesim Kafası (Cutting Head)
**Dosya:** `CAD/Parts/CuttingHead/CuttingHeadAssembly.f3d`

**Bileşenler:**
- Kesim tekeri montajı
- Z ekseni aktüatör
- Presyon ayağı
- Yağlama sistemi bağlantısı

| Özellik | Değer |
|---------|-------|
| Z Ekseni Stroku | 100 mm |
| Kesim Basıncı | 0-500 N |
| Teker Çapı | 25 mm |

## 3. Standart Parçalar

### 3.1 Delta Servo Motorlar
**X Ekseni:** Delta ECMA-C13090 (750W, 3000 rpm)
**Y Ekseni:** Delta ECMA-C11805 (400W, 3000 rpm)
**Z Ekseni:** Delta ECMA-C10602 (200W, 3000 rpm)

**Model Indirme:**
- Delta 3D CAD modelleri: https://www.delta-automation.com/contactus/02_download_center/03_servo_system/ECMA.htm

### 3.2 Lineer Raylar
| Eksen | Model | Uzunluk |
|-------|-------|---------|
| X1 | HIWIN HGH25CA | 6000 mm |
| X2 | HIWIN HGH25CA | 6000 mm |
| Y | HIWIN HGH25CA | 3000 mm |

### 3.3 Bilyalı Vidası (Ball Screw)
| Eksen | Çap | Adım | Uzunluk |
|-------|-----|------|---------|
| X | 25 mm | 10 mm | 6200 mm |
| Y | 20 mm | 5 mm | 3200 mm |
| Z | 16 mm | 5 mm | 200 mm |

## 4. Montaj İpuçları

### 4.1 Joints Kullanımı
1. **Rigid Joint:** Sabit bağlantılar için
2. **Revolute Joint:** Döner eklemler için
3. **Slider Joint:** Lineer hareketler için
4. **Cylinder Joint:** Döner + lineer hareketler için

### 4.2 Motion Study
- X Ekseni: 0-6000 mm, hız 60 m/dk
- Y Ekseni: 0-3000 mm, hız 40 m/dk
- Z Ekseni: 0-100 mm, hız 20 m/dk

## 5. Export Ayarları

### 5.1 STEP Export (Üretim için)
```
File → Export
Type: STEP (*.stp, *.step)
Version: AP214
```

### 5.2 STL Export (3D Yazıcı için)
```
File → Export
Type: STL (*.stl)
Resolution: High
```

### 5.3 DXF Export (Lazer kesim için)
```
File → Export
Type: DXF (*.dxf)
Version: AutoCAD 2018
```

## 6. Teknik Çizim (Drawing)

### 6.1 Drawing Sheet Ayarları
```
Sheet Size: A1 (594 x 841 mm)
Scale: 1:10 (ana görünüm)
Units: mm
Tolerance: ISO 2768-m
```

### 6.2 Görünüşler
- Isometric View
- Front View
- Top View
- Right Side View
- Section Views (gerekli yerlerde)

## 7. Malzeme Listesi (BOM)

Fusion 360'da otomatik BOM oluşturma:
1. Manage → Bill of Materials
2. Tüm parçaları ekleyin
3. Malzeme bilgilerini doldurun
4. Export to Excel

## 8. Dosya Yönetimi

### 8.1 Fusion 360 Cloud Storage
- Tasarımı Fusion 360 cloud'a kaydedin
- Version history aktif tutun
- Team collaboration için share edin

### 8.2 Local Backup
```
CAD/Assembly/          - Ana montaj dosyaları
CAD/Parts/             - Parça dosyaları
CAD/Exports/           - STEP, STL, DXF dosyaları
CAD/Drawings/          - Teknik çizimler (.pdf, .dwg)
```

## 9. Sonraki Adımlar Checklist

- [ ] Ana şase modellemesi tamamlandı
- [ ] X ekseni portalı modellemesi tamamlandı
- [ ] Y ekseni kızak modellemesi tamamlandı
- [ ] Kesim kafası modellemesi tamamlandı
- [ ] Servo motor modelleri indirildi ve yerleştirildi
- [ ] Lineer ray modelleri indirildi ve yerleştirildi
- [ ] Ana montaj (assembly) tamamlandı
- [ ] Hareket simülasyonu yapıldı
- [ ] Teknik çizimler oluşturuldu
- [ ] BOM listesi oluşturuldu
- [ ] STEP dosyaları export edildi