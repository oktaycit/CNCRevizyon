# Lisec GFB-60/30RE-S Hibrit Sistem Revizyonu
## Düz Cam + Lamine Cam Kesim Modülü (VB-Modul) Entegrasyonu

**Doküman Versiyonu:** 3.0  
**Tarih:** 03.04.2026  
**Durum:** Planlama Aşaması

---

## 1. Sistem Mimarisi Güncellemesi

### 1.1 GFB-60/30RE-S Hibrit Sistem

Orijinal GFB-60/30RE düz cam kesim makinesine **VB-Modul (Verbundglas-Schneidemodul)** entegrasyonu ile sistem artık **hibrit** yapıdadır:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    GFB-60/30RE-S Hibrit Sistem                      │
│                                                                     │
│  ┌─────────────────────────┐    ┌─────────────────────────────────┐│
│  │  Düz Cam Kesim          │    │  Lamine Cam Kesim (VB-Modul)   ││
│  │  (Standard GFB)         │    │  - Alt kesici ünitesi          ││
│  │  - X/Y/Z eksenleri      │    │  - Isıtıcı çubuk (Heizstab)    ││
│  │  - Üst kesim kafası     │    │  - Kırma çıtaları              ││
│  │                         │    │  - Vakum vantuz sistemi        ││
│  │                         │    │  - Ayırma bıçağı               ││
│  └─────────────────────────┘    └─────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 Eksen Sayısı Artışı

| Eksen | Fonksiyon | Orijinal | Yeni (VB-Modul) |
|-------|-----------|----------|-----------------|
| 1 | X Ekseni (Köprü) | ✓ | ✓ |
| 2 | Y Ekseni (Kafa Yatay) | ✓ | ✓ |
| 3 | Z Ekseni (Kafa Dikey) | ✓ | ✓ |
| 4 | C Ekseni (Rodaj/CNC) | ✓ | ✓ |
| 5 | **V Ekseni (VB-Kesici)** | ✗ | **✓ YENİ** |

---

## 2. 5. Eksen: Lamine Kesim Modülü (VB-Modul)

### 2.1 Mekanik Yapı

**VB-Modul Bileşenleri:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    VB-Modul Alt Ünitesi                         │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │ Alt Kesici  │  │ Isıtıcı     │  │ Vakum       │            │
│   │ Schneider   │  │ Heizstab    │  │ Sauger      │            │
│   │ unten       │  │             │  │             │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │ Kırma Çıtası│  │ Ayırma      │  │ Basınç     │            │
│   │ Brechleiste │  │ Trennklinge │  │ Andrückrolle│           │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Hareket Mekanizması

**VB-Kesici Ekseni (V Ekseni):**
- **Hareket Tipi:** Lineer (masa altında, Y ekseni ile senkronize)
- **Sürücü Tipi:** Kramayer veya Dişli kayış
- **Konumlandırma:** Y ekseni ile aynı koordinatta (alttan kesim)
- **Offset Kalibrasyonu:** Üst kesici ile alt kesici rotası milimetrik örtüşmeli

### 2.3 Servo Motor Seçimi (5. Eksen)

**Orijinal Sistem (Lenze):**
- Model: Lenze EVS9322-EP
- Güç: 1.5 kW
- Besleme: 3x400VAC

**Delta Revizyon Önerisi:**

| Özellik | Değer |
|---------|-------|
| Sürücü | Delta ASD-A3-1523-E (1.5kW, EtherCAT) |
| Motor | Delta ECMA-E11315 (1.5kW, 2000rpm) |
| Flanş | 130 mm |
| Mil Çapı | 38 mm |
| Encoder | 24-bit绝对值 |
| Koruma | IP67 (masa altı için) |

**Alternatif (Daha Yüksek Tork):**
- Motor: Delta ECMA-E11320 (2.0kW)
- Sürücü: Delta ASD-A3-2023-E (2.0kW)

---

## 3. Genişletilmiş I/O Sistemi

### 3.1 Lamine Modül I/O Listesi

#### Dijital Girişler (DI) - Ekstra 24 Kanal
| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %IX2.0 | HEIZUNG_IN | Isıtıcı giriş pozisyonu |
| %IX2.1 | HEIZUNG_OUT | Isıtıcı çıkış pozisyonu |
| %IX2.2 | BRECH_IN | Kırma çıtası giriş |
| %IX2.3 | BRECH_OUT | Kırma çıtası çıkış |
| %IX2.4 | TRENN_IN | Ayırma bıçağı giriş |
| %IX2.5 | TRENN_OUT | Ayırma bıçağı çıkış |
| %IX2.6 | VAKUUM_OK | Vakum basıncı yeterli |
| %IX2.7 | VAKUUM_ALARM | Vakum hatası |
| %IX2.8 | ANDRUCK_IN | Basınç rollesi giriş |
| %IX2.9 | ANDRUCK_OUT | Basınç rollesi çıkış |
| %IX2.10 | LASER_ACTIVE | Lazer aktif |
| %IX2.11 | HEIZUNG_TEMP_OK | Isıtıcı sıcaklık OK |
| %IX2.12 | HEIZUNG_TEMP_ALARM | Isıtıcı sıcaklık hatası |
| %IX2.13 | VB_HOME | VB modül home pozisyonu |
| %IX2.14 | VB_LIMIT_PLUS | VB modül +limit |
| %IX2.15 | VB_LIMIT_MINUS | VB modül -limit |
| %IX3.0-15 | REZERV | Yedek (32 kanal) |

#### Dijital Çıkışlar (DO) - Ekstra 24 Kanal
| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %QX2.0 | HEIZUNG_ENABLE | Isıtıcı enable |
| %QX2.1 | HEIZUNG_POWER | Isıtıcı güç kontrol |
| %QX2.2 | BRECH_UP | Kırma çıtası yukarı |
| %QX2.3 | BRECH_DOWN | Kırma çıtası aşağı |
| %QX2.4 | TRENN_UP | Ayırma bıçağı yukarı |
| %QX2.5 | TRENN_DOWN | Ayırma bıçağı aşağı |
| %QX2.6 | VAKUUM_PUMP_1 | Vakum pompa 1 |
| %QX2.7 | VAKUUM_PUMP_2 | Vakum pompa 2 |
| %QX2.8 | ANDRUCK_UP | Basınç rollesi yukarı |
| %QX2.9 | ANDRUCK_DOWN | Basınç rollesi aşağı |
| %QX2.10 | LASER_ENABLE | Lazer enable |
| %QX2.11 | VB_SERVO_ENABLE | VB servo enable |
| %QX2.12-15 | REZERV | Yedek |

### 3.2 Analog Girişler (AI) - Ekstra 8 Kanal
| Adres | Sinyal | Açıklama |
|-------|--------|----------|
| %IW0 | HEIZUNG_TEMP | Isıtıcı sıcaklık (°C) |
| %IW2 | VAKUUM_PRESSURE | Vakum basıncı (mbar) |
| %IW4 | PNEU_PRESSURE | Pnömatik basınç (bar) |
| %IW6 | VB_CURRENT | VB servo akım (A) |

### 3.3 R1-EC Modül Genişletmesi

**Mevcut Sistem:** 3x DI + 3x DO (48+48 I/O)
**Yeni Gereksinim:** +3x DI + 3x DO (ekstra 48+48 I/O)

**Toplam Konfigürasyon:**
```
Slave 6: R1-EC Bus Coupler
  ├─ R1-EC0902D #1 (DI 1-16)   → Düz cam sensörleri
  ├─ R1-EC0902D #2 (DI 17-32)  → Düz cam limitler
  ├─ R1-EC0902D #3 (DI 33-48)  → Düz cam güvenlik
  ├─ R1-EC0902O #1 (DO 1-16)   → Düz cam çıkışlar
  ├─ R1-EC0902O #2 (DO 17-32)  → Düz cam valfler
  ├─ R1-EC0902O #3 (DO 33-48)  → Düz cam röleler
  │
Slave 7: R1-EC Bus Coupler #2 (YENİ - Lamine Modül)
  ├─ R1-EC0902D #4 (DI 49-64)   → Lamine sensörler
  ├─ R1-EC0902D #5 (DI 65-80)   → Lamine limitler
  ├─ R1-EC0902D #6 (DI 81-96)   → Lamine güvenlik
  ├─ R1-EC0902O #4 (DO 49-64)   → Lamine çıkışlar
  ├─ R1-EC0902O #5 (DO 65-80)   → Lamine valfler
  ├─ R1-EC0902O #6 (DO 81-96)   → Lamine röleler
```

---

## 4. Lamine Kesim Süreci ve Zamanlama

### 4.1 Kesim Döngüsü (Lamine Cam 4+4mm)

```
┌─────────────────────────────────────────────────────────────────┐
│                    Lamine Kesim Zaman Diyagramı                 │
│                                                                 │
│  Cam Yükleme                                                    │
│  ├─ Vakum aktif                                                 │
│  └─ Konumlandırma (X/Y)                                         │
│                                                                 │
│  Isıtma Fazı (Heizstab)                                         │
│  ├─ Isıtıcı aşağı (2 sn)                                        │
│  ├─ Isıtma (3-5 sn, 120-150°C)                                  │
│  └─ Isıtıcı yukarı (1 sn)                                       │
│                                                                 │
│  Üst Kesim (Z Ekseni)                                           │
│  ├─ Kesim kafası aşağı                                          │
│  ├─ Çizim (G01, F=2000 mm/dk)                                   │
│  └─ Kesim kafası yukarı                                         │
│                                                                 │
│  Alt Kesim (V Ekseni) - Senkronize                              │
│  ├─ V ekseni Y ile aynı pozisyona                               │
│  ├─ Alt kesici yukarı (temas)                                   │
│  ├─ Çizim (senkronize Y ile)                                    │
│  └─ Alt kesici aşağı                                            │
│                                                                 │
│  Ayırma (Trennklinge)                                           │
│  ├─ Ayırma bıçağı cam altına                                    │
│  ├─ Hafif yukarı basınç                                         │
│  └─ Y ekseni hareketi ile ayırma                                │
│                                                                 │
│  Kırma (Brechleiste)                                            │
│  ├─ Kırma çıtası aşağı                                          │
│  ├─ Cam kenarından yukarı basınç                                │
│  └─ Cam kırılır                                                 │
│                                                                 │
│  Cam Boşaltma                                                   │
│  └─ Vakum pasif, cam alınır                                     │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Kritik Süre Parametreleri

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| Isıtma Süresi | 3-5 sn | PVB film kalınlığına bağlı |
| Isıtma Sıcaklığı | 120-150°C | Film yumuşama noktası |
| Üst Kesim Hızı | 2000 mm/dk | Standart cam için |
| Alt Kesim Offset | ±0.05 mm | Üst/alt çizgi örtüşme toleransı |
| Ayırma Basıncı | 2-4 bar | Pnömatik basınç |
| Kırma Basıncı | 3-5 bar | Cam kalınlığına bağlı |

---

## 5. Yapay Zeka (Qwen) Entegrasyonu

### 5.1 Uzman Sistem: Otomatik Parametre Hesaplama

**Girdi:**
```json
{
  "cam_tipi": "lamine",
  "ust_kalinlik": 4,    // mm
  "film_kalinlik": 0.76, // mm (PVB)
  "alt_kalinlik": 4,    // mm
  "cam_boyut_x": 2000,  // mm
  "cam_boyut_y": 1500   // mm
}
```

**Qwen Çıktısı:**
```json
{
  "isitma_suresi": 4.2,        // sn
  "isitma_sicaklik": 135,      // °C
  "ust_kesim_basinc": 3.5,     // bar
  "alt_kesim_basinc": 3.2,     // bar
  "ayirma_basinc": 2.8,        // bar
  "kirma_basinc": 4.0,         // bar
  "kesim_hizi": 1800,          // mm/dk
  "ust_alt_offset_x": 0.02,    // mm (kalibrasyon)
  "ust_alt_offset_y": -0.01    // mm (kalibrasyon)
}
```

### 5.2 Python Uzman Sistem Örneği

```python
# lamine_expert_system.py
from dataclasses import dataclass
from typing import Dict

@dataclass
class LamineCamParametreleri:
    ust_kalinlik: float
    film_kalinlik: float
    alt_kalinlik: float
    cam_tipi: str  # 'PVB', 'EVA', 'SGP'
    
class LamineKesimUzmanSistemi:
    """Lamine cam kesim parametrelerini hesaplayan uzman sistem"""
    
    def __init__(self):
        # Deneyimsel katsayılar
        self.isitma_katsayisi = {
            'PVB': 1.0,
            'EVA': 1.2,
            'SGP': 0.8
        }
        
    def hesapla(self, params: LamineCamParametreleri) -> Dict:
        """Tüm kesim parametrelerini hesapla"""
        toplam_kalinlik = (params.ust_kalinlik + 
                          params.film_kalinlik + 
                          params.alt_kalinlik)
        
        # Isıtma parametreleri
        isitma_suresi = self._isitma_suresi(params)
        isitma_sicaklik = self._isitma_sicaklik(params)
        
        # Kesim parametreleri
        ust_basinc = self._ust_kesim_basinc(params)
        alt_basinc = self._alt_kesim_basinc(params)
        kesim_hizi = self._kesim_hizi(params)
        
        # Ayırma ve kırma
        ayirma_basinc = self._ayirma_basinc(params)
        kirma_basinc = self._kirma_basinc(params)
        
        return {
            'isitma_suresi': isitma_suresi,
            'isitma_sicaklik': isitma_sicaklik,
            'ust_kesim_basinc': ust_basinc,
            'alt_kesim_basinc': alt_basinc,
            'kesim_hizi': kesim_hizi,
            'ayirma_basinc': ayirma_basinc,
            'kirma_basinc': kirma_basinc,
            'toplam_kalinlik': toplam_kalinlik
        }
    
    def _isitma_suresi(self, p: LamineCamParametreleri) -> float:
        """Isıtma süresini hesapla (sn)"""
        base_sure = 3.0  # Baz süre
        kalinlik_faktor = (p.ust_kalinlik + p.alt_kalinlik) / 8.0
        film_faktor = self.isitma_katsayisi.get(p.cam_tipi, 1.0)
        return base_sure * kalinlik_faktor * film_faktor
    
    def _isitma_sicaklik(self, p: LamineCamParametreleri) -> int:
        """Isıtma sıcaklığını hesapla (°C)"""
        base_temp = 130  # Baz sıcaklık
        film_temp = {
            'PVB': 135,
            'EVA': 120,
            'SGP': 145
        }
        return film_temp.get(p.cam_tipi, base_temp)
    
    def _ust_kesim_basinc(self, p: LamineCamParametreleri) -> float:
        """Üst kesim basıncını hesapla (bar)"""
        # Cam kalınlığına göre lineer interpolasyon
        if p.ust_kalinlik <= 4:
            return 3.0
        elif p.ust_kalinlik <= 6:
            return 3.5
        else:
            return 4.0
    
    def _alt_kesim_basinc(self, p: LamineCamParametreleri) -> float:
        """Alt kesim basıncını hesapla (bar)"""
        # Üst basınçtan biraz daha düşük
        ust_basinc = self._ust_kesim_basinc(p)
        return ust_basinc * 0.9
    
    def _kesim_hizi(self, p: LamineCamParametreleri) -> int:
        """Kesim hızını hesapla (mm/dk)"""
        base_hiz = 2000
        kalinlik_faktor = 8.0 / (p.ust_kalinlik + p.alt_kalinlik)
        return int(base_hiz * min(kalinlik_faktor, 1.5))
    
    def _ayirma_basinc(self, p: LamineCamParametreleri) -> float:
        """Ayırma basıncını hesapla (bar)"""
        return 2.5 + (p.ust_kalinlik * 0.1)
    
    def _kirma_basinc(self, p: LamineCamParametreleri) -> float:
        """Kırma basıncını hesapla (bar)"""
        return 3.5 + (p.ust_kalinlik * 0.15)


# Kullanım örneği
if __name__ == '__main__':
    uzman = LamineKesimUzmanSistemi()
    
    param = LamineCamParametreleri(
        ust_kalinlik=4,
        film_kalinlik=0.76,
        alt_kalinlik=4,
        cam_tipi='PVB'
    )
    
    sonuc = uzman.hesapla(param)
    
    print("Lamine Kesim Parametreleri:")
    print(f"  Isıtma: {sonuc['isitma_suresi']:.1f} sn @ {sonuc['isitma_sicaklik']}°C")
    print(f"  Üst Kesim: {sonuc['ust_kesim_basinc']} bar")
    print(f"  Alt Kesim: {sonuc['alt_kesim_basinc']} bar")
    print(f"  Kesim Hızı: {sonuc['kesim_hizi']} mm/dk")
    print(f"  Ayırma: {sonuc['ayirma_basinc']} bar")
    print(f"  Kırma: {sonuc['kirma_basinc']} bar")
```

### 5.3 Üst/Alt Kesim Offset Kalibrasyonu

```python
# offset_calibration.py
import numpy as np
from scipy.optimize import minimize

class KesimOffsetKalibrasyon:
    """
    Üst ve alt kesim rotalarını kalibre eder
    Vizyon sistemi veya ölçüm verisi kullanır
    """
    
    def __init__(self):
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.rotation_error = 0.0
        
    def kalibre(self, ust_noktalar, alt_noktalar):
        """
        Üst ve alt kesim noktalarını karşılaştırarak
        optimal offset hesapla
        
        ust_noktalar: [(x1,y1), (x2,y2), ...] - Üst kesim ölçülen
        alt_noktalar: [(x1,y1), (x2,y2), ...] - Alt kesim ölçülen
        """
        def hata_fonksiyonu(params):
            ox, oy, rot = params
            
            # Alt noktaları transform et
            transform = []
            for x, y in alt_noktalar:
                # Rotasyon
                xr = x * np.cos(rot) - y * np.sin(rot)
                yr = x * np.sin(rot) + y * np.cos(rot)
                # Offset
                xr += ox
                yr += oy
                transform.append((xr, yr))
            
            # Hata hesapla (RMSE)
            hatalar = []
            for (ux, uy), (tx, ty) in zip(ust_noktalar, transform):
                hata = np.sqrt((ux-tx)**2 + (uy-ty)**2)
                hatalar.append(hata)
            
            return np.sqrt(np.mean(np.array(hatalar)**2))
        
        # Optimizasyon
        sonuc = minimize(
            hata_fonksiyonu,
            x0=[0, 0, 0],  # Başlangıç: offset yok
            method='Nelder-Mead'
        )
        
        self.offset_x = sonuc.x[0]
        self.offset_y = sonuc.x[1]
        self.rotation_error = sonuc.x[2]
        
        return {
            'offset_x': self.offset_x,
            'offset_y': self.offset_y,
            'rotation_error': self.rotation_error,
            'rmse': sonuc.fun
        }
    
    def duzelt(self, alt_koordinat):
        """Alt kesim koordinatını düzelt"""
        x, y = alt_koordinat
        
        # Rotasyon düzeltmesi
        xr = x * np.cos(self.rotation_error) - y * np.sin(self.rotation_error)
        yr = x * np.sin(self.rotation_error) + y * np.cos(self.rotation_error)
        
        # Offset düzeltmesi
        xr += self.offset_x
        yr += self.offset_y
        
        return (xr, yr)
```

---

## 6. STM32 Firmware Güncellemesi

### 6.1 Lamine Modül State Machine

```c
// lamine_state_machine.c
typedef enum {
    LAMINE_IDLE,
    LAMINE_LOADING,
    LAMINE_HEATING,
    LAMINE_UPPER_CUT,
    LAMINE_LOWER_CUT,
    LAMINE_SEPARATING,
    LAMINE_BREAKING,
    LAMINE_UNLOADING,
    LAMINE_ERROR
} LamineState_t;

typedef struct {
    LamineState_t state;
    uint32_t state_timer;
    float heating_temp;
    uint32_t heating_time;
    float upper_pressure;
    float lower_pressure;
    float breaking_pressure;
    bool vacuum_active;
    bool heater_active;
} LamineProcess_t;

void Lamine_StateMachine(void) {
    static LamineProcess_t process = {0};
    
    switch (process.state) {
        case LAMINE_IDLE:
            // Bekle, başlatma komutu bekle
            if (start_command) {
                process.state = LAMINE_LOADING;
                process.state_timer = HAL_GetTick();
            }
            break;
            
        case LAMINE_LOADING:
            // Cam yüklendi, vakum aktif
            if (glass_loaded && vacuum_ok) {
                process.vacuum_active = true;
                process.state = LAMINE_HEATING;
                process.state_timer = HAL_GetTick();
            }
            break;
            
        case LAMINE_HEATING:
            // Isıtıcı aşağı, ısıtma başlat
            if (process.state_timer == 0) {
                Heater_Down();
                Heater_Enable();
                process.state_timer = HAL_GetTick();
            }
            
            // Isıtma süresi doldu mu?
            if (HAL_GetTick() - process.state_timer >= process.heating_time) {
                Heater_Up();
                Heater_Disable();
                process.state = LAMINE_UPPER_CUT;
            }
            break;
            
        case LAMINE_UPPER_CUT:
            // Üst kesim
            if (UpperCut_Complete()) {
                process.state = LAMINE_LOWER_CUT;
            }
            break;
            
        case LAMINE_LOWER_CUT:
            // Alt kesim (V ekseni ile senkronize)
            if (LowerCut_Complete()) {
                process.state = LAMINE_SEPARATING;
            }
            break;
            
        case LAMINE_SEPARATING:
            // Ayırma bıçağı aktif
            if (Separating_Complete()) {
                process.state = LAMINE_BREAKING;
            }
            break;
            
        case LAMINE_BREAKING:
            // Kırma çıtası aktif
            if (Breaking_Complete()) {
                process.state = LAMINE_UNLOADING;
            }
            break;
            
        case LAMINE_UNLOADING:
            // Vakum pasif, cam alındı
            if (!glass_present) {
                process.vacuum_active = false;
                process.state = LAMINE_IDLE;
                process_complete = true;
            }
            break;
            
        case LAMINE_ERROR:
            // Hata durumu
            if (error_reset) {
                Lamine_Reset();
                process.state = LAMINE_IDLE;
            }
            break;
    }
}
```

### 6.2 EtherCAT Haberleşme - NC300 ↔ STM32

```c
// ethercat_bridge.c
// NC300'dan lamine parametreleri al, STM32'ye gönder

typedef struct {
    float heating_temp;
    uint32_t heating_time;
    float upper_pressure;
    float lower_pressure;
    float breaking_pressure;
    float cutting_speed;
    float offset_x;
    float offset_y;
} LamineParams_t;

volatile LamineParams_t lamine_params;

// NC300'dan veri al (Modbus TCP veya shared memory)
void NC300_ReadLamineParams(void) {
    // Parametreleri oku
    lamine_params.heating_temp = NC300_ReadRegister(40100);
    lamine_params.heating_time = NC300_ReadRegister(40101);
    lamine_params.upper_pressure = NC300_ReadRegister(40102);
    lamine_params.lower_pressure = NC300_ReadRegister(40103);
    lamine_params.breaking_pressure = NC300_ReadRegister(40104);
    lamine_params.cutting_speed = NC300_ReadRegister(40105);
    lamine_params.offset_x = NC300_ReadRegister(40106);
    lamine_params.offset_y = NC300_ReadRegister(40107);
}

// STM32'ye gönder (UART veya SPI)
void STM32_SendLamineParams(void) {
    UART_SendCommand("SET_LAMINE_PARAMS");
    UART_SendFloat(lamine_params.heating_temp);
    UART_SendUint32(lamine_params.heating_time);
    UART_SendFloat(lamine_params.upper_pressure);
    UART_SendFloat(lamine_params.lower_pressure);
    UART_SendFloat(lamine_params.breaking_pressure);
    UART_SendFloat(lamine_params.cutting_speed);
    UART_SendFloat(lamine_params.offset_x);
    UART_SendFloat(lamine_params.offset_y);
}
```

---

## 7. FreeCAD Modelleme Stratejisi

### 7.1 VB-Modul Bileşenleri

**Modelleme Sırası:**
1. **Alt Kesici Ünitesi**
   - Kesici teker montajı
   - Pneumatik silindir bağlantısı
   - V ekseni servo bağlantısı

2. **Isıtıcı Çubuk (Heizstab)**
   - Isıtıcı eleman
   - Hareket mekanizması
   - Termokupl montajı

3. **Vakum Vantuz Sistemi**
   - Vantuz pedleri
   - Vakum kanalları
   - Basınç sensörü bağlantısı

4. **Kırma Çıtası (Brechleiste)**
   - Çıta profili
   - Kaldırma mekanizması
   - Pnömatik silindir

5. **Ayırma Bıçağı (Trennklinge)**
   - Bıçak montajı
   - Hassas ayar mekanizması

### 7.2 Assembly4 Montaj Sırası

```
1. Ana şase (Ground)
2. Düz cam kesim bileşenleri
   ├─ X ekseni rayları
   ├─ Y ekseni portalı
   ├─ Z ekseni kafası
   └─ Motorlar
3. VB-Modul bileşenleri
   ├─ Alt kesici ünitesi (masa altı)
   ├─ Isıtıcı çubuk
   ├─ Vakum vantuzlar
   ├─ Kırma çıtaları
   └─ Ayırma bıçağı
4. Sensörler
5. Kablo kanalları
```

---

## 8. Güncellenmiş Malzeme Listesi

### 8.1 Ekstra Bileşenler (VB-Modul)

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | Delta Servo Sürücü 1.5kW | ASD-A3-1523-E | 1 |
| 2 | Delta Servo Motor 1.5kW | ECMA-E11315 (IP67) | 1 |
| 3 | R1-EC Bus Coupler | R1-EC | 1 (ekstra) |
| 4 | R1-EC Dijital Giriş | R1-EC0902D | 3 (ekstra) |
| 5 | R1-EC Dijital Çıkış | R1-EC0902O | 3 (ekstra) |
| 6 | Isıtıcı Çubuk | Heizstab 2kW | 1 |
| 7 | Termokupl | K-Tip | 2 |
| 8 | Vakum Pompası | 2.2kW | 2 |
| 9 | Pnömatik Valf Adası | Festo MPA-L | 2 |
| 10 | Basınç Sensörü | 0-10 bar | 3 |
| 11 | Lamine Kesici Teker | Bohle/Diamant | 2 |
| 12 | Kırma Çıtası | Özel profil | 2 |
| 13 | Ayırma Bıçağı | Özel tasarım | 1 |

### 8.2 Güncellenmiş Toplam BOM

| Kategori | Orijinal | Yeni (VB-Modul) |
|----------|----------|-----------------|
| Servo Sürücü | 5 adet | 6 adet (+1) |
| Servo Motor | 5 adet | 6 adet (+1) |
| R1-EC DI Modül | 3 adet | 6 adet (+3) |
| R1-EC DO Modül | 3 adet | 6 adet (+3) |
| Dijital Giriş | 48 kanal | 96 kanal |
| Dijital Çıkış | 48 kanal | 96 kanal |

---

## 9. Güncellenmiş Zaman Çizelgesi

| Aşama | Süre | Başlangıç | Bitiş |
|-------|------|-----------|-------|
| CAD Modelleme (VB-Modul dahil) | 6 hafta | Hafta 1 | Hafta 6 |
| Elektrik Tasarımı (ekstra I/O) | 4 hafta | Hafta 3 | Hafta 6 |
| Malzeme Temini | 6 hafta | Hafta 4 | Hafta 9 |
| Pano İmalatı | 3 hafta | Hafta 8 | Hafta 10 |
| Mekanik Montaj | 4 hafta | Hafta 10 | Hafta 13 |
| Elektrik Montajı | 3 hafta | Hafta 13 | Hafta 15 |
| Yazılım Geliştirme | 6 hafta | Hafta 10 | Hafta 15 |
| Test ve Komisyon | 3 hafta | Hafta 15 | Hafta 17 |

**Toplam Tahmini Süre:** 17 hafta (~4 ay)

---

## 10. Sonraki Adımlar

1. **FreeCAD VB-Modul Modelleme**
   - Alt kesici ünitesi tasarımı
   - Isıtıcı çubuk montajı
   - Vakum sistemi modelleme
   - Kırma ve ayırma mekanizmaları

2. **Delta 5. Eksen Konfigürasyonu**
   - V ekseni servo parametreleri
   - Y ekseni ile elektronik kam (E-Cam)
   - Offset kalibrasyon fonksiyonu

3. **STM32 Lamine Firmware**
   - State machine implementasyonu
   - I/O genişletme (ekstra R1-EC)
   - Isıtıcı PID kontrolü
   - Vakum yönetimi

4. **Qwen Uzman Sistem**
   - Lamine parametre hesaplama
   - Offset kalibrasyon algoritması
   - NC300 ↔ STM32 haberleşme

5. **Güvenlik Fonksiyonları**
   - Isıtıcı sıcaklık izleme
   - Vakum hatası yönetimi
   - Lamine modül interlock'ları

---

**Kaynaklar:**
- LiSEC GFB-60/30RE-S Teknik Dokümanı
- Delta ASD-A3-E EtherCAT Manuel
- FreeCAD Assembly4 Tutorial
- Lamine Cam İşleme Teknolojisi