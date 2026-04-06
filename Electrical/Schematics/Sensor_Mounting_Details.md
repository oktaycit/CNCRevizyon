# Leuze IS 218 Sensör Montaj Detayları
## Lisec GFB-60/30RE Cam Kesme Makinesi

## 1. Sensör Teknik Özellikleri

### Leuze IS 218 Serisi
| Özellik | Değer |
|---------|-------|
| Model | IS 218 MM / IS 218 AM |
| Boyut | M18 x 1 x 75 mm |
| Algılama Mesafesi | 8 mm (nominal), 10 mm (maks) |
| Çıkış Tipi | PNP NO/NC (seçilebilir) |
| Besleme | 10-30V DC |
| Akım Tüketimi | 20 mA (max) |
| Koruma Sınıfı | IP67, IP68, IP69K |
| Çalışma Sıcaklığı | -25°C ... +70°C |
| Bağlantı | M12 Konnektör (4-pin) |
| Kirlenme Toleransı | Yüksek (cam tozu ortamı için uygun) |

### M12 Konnektör Pinout
```
      1
    ┌───┐
  4 │   │ 2
    └───┘
      3

Pin 1: +24V DC (Brown)
Pin 2: Output PNP (White)
Pin 3: 0V DC (Blue)
Pin 4: NO/NC Select (Black)
```

## 2. Sensör Yerleşim Planı

### 2.1 X Ekseni Sensörleri
```
┌─────────────────────────────────────────────────────────┐
│                    X Ekseni (6000mm)                    │
│                                                         │
│  [X+LIMIT]                              [X-HOME]        │
│     │                                      │            │
│     ▼                                      ▼            │
│  ◄─────────────────────────────────────────►            │
│           5800 mm                                         │
│                                                         │
│  [X-LIMIT]                                              │
│     │                                                   │
│     ▼                                                   │
└─────────────────────────────────────────────────────────┘

Konumlar:
- X+LIMIT: X = 5950 mm (sağ uç)
- X-LIMIT: X = -50 mm (sol uç)
- X-HOME: X = 0 mm (referans noktası)
```

### 2.2 Y Ekseni Sensörleri
```
┌─────────────────────────────────────────┐
│          Y Ekseni (3000mm)              │
│                                         │
│  [Y+LIMIT]                              │
│     │                                   │
│     ▼                                   │
│  ◄───────────────────────────►          │
│           2900 mm                       │
│                                         │
│  [Y-HOME]           [Y-LIMIT]           │
│     │                   │               │
│     ▼                   ▼               │
└─────────────────────────────────────────┘

Konumlar:
- Y+LIMIT: Y = 2950 mm (ön uç)
- Y-LIMIT: Y = -50 mm (arka uç)
- Y-HOME: Y = 0 mm (referans noktası)
```

### 2.3 Z Ekseni Sensörü
```
        ┌─────────────┐
        │ Z Motor     │
        │ (Frenli)    │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │ Z+LIMIT     │
        │ (Yukarı)    │
        └─────────────┘
               │
        ═══════════════  Z = +100 mm (üst limit)
               │
        ┌──────▼──────┐
        │ Z-HOME      │
        │ (Referans)  │
        └─────────────┘
               │
        ═══════════════  Z = 0 mm (home pozisyonu)
               │
        ┌──────▼──────┐
        │ Kesim Kafası│
        └─────────────┘
```

## 3. Montaj Braketi Tasarımı

### 3.1 X/Y Ekseni Limit Switch Braketi

```
                    ┌────────────────────┐
                    │   Sensör (M18)     │
                    │   ┌──────────┐     │
                    │   │  Leuze   │     │
                    │   │  IS 218  │     │
                    │   └──────────┘     │
                    └─────────┬──────────┘
                              │ M18 x 1
        ┌─────────────────────┴─────────────────────┐
        │              Ayar Vidaları                │
        │    ┌───┐              ┌───┐              │
        │    │ M5│              │ M5│              │
        │    └───┘              └───┘              │
        │      │                  │                │
        ├──────┴──────────────────┴────────────────┤
        │                                         │
        │         L-Şekilli Braket                │
        │         (Alüminyum 6061-T6)             │
        │         Kalınlık: 6 mm                  │
        │                                         │
        │    ┌───────┐                            │
        │    │ M6    │  (Profil bağlantı)         │
        │    └───────┘                            │
        └─────────────────────────────────────────┘

Özellikler:
- Malzeme: Alüminyum 6061-T6
- Kalınlık: 6 mm
- Yüzey işlem: Anodize (doğal)
- Ayar aralığı: ±5 mm (ileri-geri)
- Montaj: M6 T-slot cıvata
```

### 3.2 Z Ekseni Sensör Braketi

```
        ┌─────────────────────────────────┐
        │         Z Ekseni Braketi        │
        │                                 │
        │    ┌───────────────────────┐   │
        │    │  Sensör Yuvası (M18)  │   │
        │    │  ┌──────────────┐     │   │
        │    │  │  Leuze IS218 │     │   │
        │    │  └──────────────┘     │   │
        │    └───────────┬───────────┘   │
        │                │               │
        │        ┌───────┴───────┐       │
        │        │  Ayar Somunu  │       │
        │        │    (M18 x 1)  │       │
        │        └───────┬───────┘       │
        │                │               │
        │    ┌───────────┴───────────┐   │
        │    │   U-Şekilli Kavrama   │   │
        │    │   (Lineer Ray'e)     │   │
        │    │                       │   │
        │    │  ┌───┐         ┌───┐ │   │
        │    │  │M5 │         │M5 │ │   │
        │    │  └───┘         └───┘ │   │
        │    └─────────────────────┘   │
        └─────────────────────────────┘

Özellikler:
- Malzeme: Paslanmaz Çelik 304
- Kalınlık: 4 mm
- Lineer ray profiline direkt montaj
- Hassas ayar için somun sistemi
```

## 4. Kablolama Detayları

### 4.1 Kablo Özellikleri
| Özellik | Değer |
|---------|-------|
| Kablo Tipi | Shielded Sensor Cable |
| İletken Sayısı | 4 x 0.34 mm² |
| Dış Çap | 6.0 mm |
| Renk Kodu | Brown, White, Blue, Black |
| Koruma | IP67, Yağa Dayanıklı |
| Sıcaklık Aralığı | -40°C ... +90°C |

### 4.2 Kablo Renk Kodu ve Bağlantı

```
Sensör Tarafı (M12)          Pano Tarafı (R1-EC0902D)
─────────────────          ─────────────────────────

    Brown ────────────────────────► +24V (Terminal 1)
    White ────────────────────────► Sinyal (Terminal 2)
    Blue  ────────────────────────► 0V (Terminal 3)
    Black ────────────────────────► NO/NC Select (Terminal 4)

M12 Konnektör (Sensör)         Terminal Bloğu (Pano)
    ┌───────┐                    ┌───────┐
    │  ● 1  │ Brown (+24V)       │  ● 1  │ +24V
    │  ● 2  │ White (Sinyal)     │  ● 2  │ Sinyal → PLC Input
    │  ● 3  │ Blue (0V)          │  ● 3  │ 0V
    │  ● 4  │ Black (NO/NC)      │  ● 4  │ +24V (NC seçimi için)
    └───────┘                    └───────┘
```

### 4.3 R1-EC0902D Giriş Modülü Bağlantıları

```
R1-EC0902D Modül #1 (X Ekseni)
────────────────────────────────
Terminal 1 (X+LIMIT):  Pin 2 (White) → IX0.0
Terminal 2 (X-LIMIT):  Pin 2 (White) → IX0.1
Terminal 3 (X-HOME):   Pin 2 (White) → IX0.2
Terminal 4 (Y+LIMIT):  Pin 2 (White) → IX0.3
Terminal 5 (Y-LIMIT):  Pin 2 (White) → IX0.4
Terminal 6 (Y-HOME):   Pin 2 (White) → IX0.5
Terminal 7 (Z+LIMIT):  Pin 2 (White) → IX0.6
Terminal 8 (Z-LIMIT):  Pin 2 (White) → IX0.7
Terminal 9 (Z-HOME):   Pin 2 (White) → IX0.8
Terminal 10 (ALT+LIM): Pin 2 (White) → IX0.9
Terminal 11 (ALT-LIM): Pin 2 (White) → IX0.10
Terminal 12 (ALT-HOM): Pin 2 (White) → IX0.11
Terminal 13 (E-STOP1): Pin 2 (White) → IX0.12
Terminal 14 (E-STOP2): Pin 2 (White) → IX0.13
Terminal 15 (DOOR):    Pin 2 (White) → IX0.14
Terminal 16 (VACUUM):  Pin 2 (White) → IX0.15

Ortak 0V: Tüm sensörlerin Blue kabloları terminal bloğunda birleştirilir.
```

## 5. Ayar ve Kalibrasyon

### 5.1 Sensör Pozisyon Ayarı

**X/Y Ekseni Limit Switch Ayarı:**
1. Ekseni manuel olarak limit pozisyonuna yakın bir yere hareket ettirin
2. Sensörü brakete gevşek olarak monte edin
3. Ekseni yavaşça limit pozisyonuna doğru hareket ettirin
4. Sensör algılama LED'i yandığında durun
5. Sensörü 2-3 mm geri çekin (algılama mesafesi %50'si)
6. Ayar vidalarını sıkın
7. Test: Ekseni geri çekip tekrar ileri gönderin, algılama doğrulayın

**Z Ekseni Home Sensör Ayarı:**
1. Z eksenini manuel olarak home pozisyonuna yakın yere getirin
2. Sensörü brakete monte edin
3. Z eksenini yavaşça aşağı indirin
4. Sensör algıladığında durun
5. Bu pozisyonu Z=0 olarak ayarlayın
6. Sensörü sabitleyin

### 5.2 NO/NC Seçimi

| Uygulama | Ayar | Açıklama |
|----------|------|----------|
| Limit Switch | NC | Güvenlik için normalde kapalı |
| Home Switch | NO | Referans kenar tespiti |
| E-Stop | NC | Güvenlik için normalde kapalı |
| Glass Detect | NO | Cam var/yok tespiti |

### 5.3 Test Prosedürü

```
1. Görsel Kontrol:
   □ Tüm kablolar doğru bağlandı
   □ Konnektörler tam oturdu
   □ Sensör LED'leri görünebilir durumda

2. Güç Testi:
   □ 24V DC uygulayın
   □ PWR LED yanmalı
   □ Sensör ısınmamalı

3. Algılama Testi:
   □ Metal parçayı sensöre yaklaştırın
   □ OUT LED yanmalı
   □ PLC girişini kontrol edin (HMI'den)
   □ Algılama mesafesini ölçün (8±2mm)

4. Fonksiyon Testi:
   □ Her ekseni yavaşça limite doğru hareket ettirin
   □ Limit algılandığında eksen durmalı
   □ HMI'de alarm görünmeli
```

## 6. Kirlenme Koruması

### 6.1 Cam Tozu Koruması
```
┌─────────────────────────────────────────┐
│     Sensör Koruma Kapağı                │
│                                         │
│    ┌─────────────────────────────┐     │
│    │  Şeffaf Polikarbonat        │     │
│    │  (Kalınlık: 3mm)            │     │
│    │                             │     │
│    │    ┌───────────────┐       │     │
│    │    │  Leuze IS218  │       │     │
│    │    │  Sensör       │       │     │
│    │    └───────────────┘       │     │
│    │         ▲                  │     │
│    │         │ Algılama         │     │
│    │         │ Yönü             │     │
│    └─────────┴──────────────────┘     │
│                                       │
│    Hava Üfleme Nozulu (Opsiyonel)     │
│    ─────────────────────────          │
│    Temiz hava üfleyerek cam tozunu    │
│    sensör yüzeyinden uzak tutar       │
└───────────────────────────────────────┘
```

### 6.2 Periyodik Temizlik
| Periyot | İşlem |
|---------|-------|
| Günlük | Sensör yüzeyini temiz bezle sil |
| Haftalık | Koruyucu kapağı çıkar, içini temizle |
| Aylık | Sensör fonksiyon testini tekrarla |
| 6 Ay | Sensörü değiştir (yıpranma kontrolü) |

## 7. Arıza Giderme

| Problem | Olası Neden | Çözüm |
|---------|-------------|-------|
| Sensör LED yanmıyor | Güç yok | 24V beslemeyi kontrol et |
| Sürekli algılama | Sensör kirli | Temizle, koruyucu kapak tak |
| Algılama mesafesi düşük | Sensör eskidi | Sensörü değiştir |
| PLC girişi okumuyor | Kablo kopuk | Continuity test yap |
| Yanlış algılama | Metal parça yakın | Sensör konumunu değiştir |

## 8. Yedek Parça Listesi

| No | Parça | Model | Miktar |
|----|-------|-------|--------|
| 1 | Indüktif Sensör | Leuze IS 218 MM | 10 |
| 2 | M12 Konnektör | 4-pin, Dişi | 20 |
| 3 | Sensör Kablosu | 4x0.34mm², Shielded | 50 m |
| 4 | Montaj Braketi | X/Y Limit (Alüminyum) | 8 |
| 5 | Montaj Braketi | Z Home (Paslanmaz) | 2 |
| 6 | Ayar Somunu | M18 x 1 (Pirinç) | 20 |
| 7 | Koruyucu Kapak | Polikarbonat | 10 |