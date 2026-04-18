# Delta NC300 Programlama Kılavuzu
## Lisec GFB-60/30RE Cam Kesme Makinesi

## 1. Genel Bakış

Delta NC300, EtherCAT master olarak çalışan, G-kod işleme ve çok eksenli hareket kontrolü sağlayan CNC kontrolördür.

### 1.1 NC300 Özellikleri
| Özellik | Değer |
|---------|-------|
| Eksen Sayısı | 8 eksen (CSP/CSV/CST) |
| EtherCAT | 100μs cycle time |
| G-Kod | ISO 6983 uyumlu |
| PLC | IEC 61131-3 (LD, FBD, ST, IL, SFC) |
| HMI Entegrasyonu | Ethernet (Modbus TCP) |
| Program Belleği | 64 MB |

### 1.2 GFB-60/30RE Eksen Konfigürasyonu
```
Eksen 1: X (Köprü) - 4.5kW ECMA-L11845
Eksen 2: Y (Kafa Yatay) - 2.0kW ECMA-E11320
Eksen 3: Z (Kafa Dikey) - 1.0kW ECMA-C11010 (Frenli)
Eksen 4: ALT (Alt Kesim) - 2.0kW ECMA-E11320
Eksen 5: C (Rodaj) - 1.5kW ECMA-E11315 (IP67)
```

## 2. ISPSoft Kurulumu

### 2.1 Yazılım Kurulumu
1. **ISPSoft v3.xx** kurulum dosyasını çalıştırın
2. Lisans anlaşmasını kabul edin
3. Varsayılan dizine kurun (C:\Delta\ISPSoft)
4. USB dongle sürücülerini yükleyin (gerekliyse)
5. ISPSoft'u başlatın

### 2.2 Yeni Proje Oluşturma
1. **File → New**
2. **Device Type:** NC300 Series
3. **Project Name:** GFB60-30RE_CNC
4. **Author:** Proje Ekibi
5. **Comment:** Lisec GFB-60/30RE Cam Kesme

## 3. EtherCAT Konfigürasyonu

### 3.1 EtherCAT Master Ayarları
```pascal
// Hardware Configuration → EtherCAT Master
Master_Settings:
    CycleTime := 100;          // μs
    SyncMode := DC_SYNC;       // Distributed Clock
    WatchdogTime := 10000;     // μs (10ms)
    SM_SyncLimit := 500;       // μs
```

### 3.2 Slave Ekleme Sırası
1. **ASDA-A3-E 4.5kW** (X Ekseni) - Position 1
2. **ASDA-A3-E 2.0kW** (Y Ekseni) - Position 2
3. **ASDA-A3-E 2.0kW** (Alt Ekseni) - Position 3
4. **ASDA-A3-E 1.0kW** (Z Ekseni) - Position 4
5. **ASDA-A3-E 1.5kW** (C Ekseni) - Position 5
6. **R1-EC Bus Coupler** - Position 6
   - **R1-EC0902D** (DI 16x) - Subslot 1
   - **R1-EC0902D** (DI 16x) - Subslot 2
   - **R1-EC0902D** (DI 16x) - Subslot 3
   - **R1-EC0902O** (DO 16x) - Subslot 4
   - **R1-EC0902O** (DO 16x) - Subslot 5
   - **R1-EC0902O** (DO 16x) - Subslot 6
7. **MS300 + CMM-EC01** (Konveyör) - Position 7

### 3.3 PDO Mapping Konfigürasyonu

#### X Ekseni (Slave 1) PDO Ayarları
```
TxPDO (Sürücü → NC300):
    0x1A00: Status Word (2 bytes)
    0x1A01: Actual Position (4 bytes)
    0x1A02: Actual Velocity (4 bytes)
    0x1A03: Actual Torque (2 bytes)
    0x1A04: Following Error (4 bytes)
    0x1A05: Status Word Extended (2 bytes)

RxPDO (NC300 → Sürücü):
    0x1600: Control Word (2 bytes)
    0x1601: Target Position (4 bytes)
    0x1602: Target Velocity (4 bytes)
    0x1603: Torque Offset (2 bytes)
```

### 3.4 Eksen Parametreleri

```pascal
// Axis Configuration
Axis[1]:  // X Ekseni
    Name := "X_Axis";
    MotorType := ROTARY_MOTOR;
    LoadType := INERTIA_LOAD;
    MotorMass := 45.0;         // kg
    MotorInertia := 0.015;     // kg·m²
    LoadInertia := 0.020;      // kg·m²
    GearRatio := 1.0;
    BallScrewPitch := 10.0;    // mm
    MaxVelocity := 60000;      // mm/dk
    MaxAcceleration := 2000;   // mm/s²
    MaxDeceleration := 2000;   // mm/s²
    JerkLimit := 5000;         // mm/s³
    FollowingErrorLimit := 5.0; // mm
    PositionScale := 1.0;      // pulse/mm
    VelocityScale := 1.0;      // rpm/(mm/dk)
    
Axis[2]:  // Y Ekseni
    Name := "Y_Axis";
    MotorType := ROTARY_MOTOR;
    MaxVelocity := 40000;      // mm/dk
    MaxAcceleration := 1500;   // mm/s²
    BallScrewPitch := 5.0;     // mm
    
Axis[3]:  // Z Ekseni
    Name := "Z_Axis";
    MotorType := ROTARY_MOTOR;
    MaxVelocity := 20000;      // mm/dk
    MaxAcceleration := 1000;   // mm/s²
    BallScrewPitch := 5.0;     // mm
    GravityCompensation := TRUE;
    BrakeControl := TRUE;      // Fren kontrolü aktif
    
Axis[4]:  // Alt Ekseni
    Name := "Alt_Axis";
    MotorType := ROTARY_MOTOR;
    MaxVelocity := 40000;      // mm/dk
    MaxAcceleration := 1500;   // mm/s²
    BallScrewPitch := 5.0;     // mm
    SlaveAxis := TRUE;         // E-Cam için slave
    
Axis[5]:  // C Ekseni (Rodaj)
    Name := "C_Axis";
    MotorType := ROTARY_MOTOR;
    MaxVelocity := 30000;      // rpm
    MaxAcceleration := 1000;   // rpm/s
```

## 4. G-Kod Programlama

### 4.1 Desteklenen G-Kodlar

#### Hareket Komutları
| Kod | Açıklama | Format |
|-----|----------|--------|
| G00 | Hızlı konumlandırma | G00 X_Y_Z_ |
| G01 | Lineer interpolasyon | G01 X_Y_Z_F_ |
| G02 | Dairesel interpolasyon (CW) | G02 X_Y_I_J_F_ |
| G03 | Dairesel interpolasyon (CCW) | G03 X_Y_I_J_F_ |
| G04 | Dwell (bekleme) | G04 P_ |

#### Referans ve Koordinat
| Kod | Açıklama | Format |
|-----|----------|--------|
| G28 | Referans noktasına dönüş | G28 X_Y_Z_ |
| G90 | Mutlak konumlandırma | G90 |
| G91 | Artışlı konumlandırma | G91 |
| G54-G59 | İş koordinat sistemi seçimi | G54 |

#### Kesim Özel
| Kod | Açıklama | Format |
|-----|----------|--------|
| G71 | Metrik birimler | G71 |
| G72 | İnç birimler | G72 |
| G94 | Besleme hızı (mm/dk) | G94 |
| M03 | Kesim başlat | M03 |
| M05 | Kesim durdur | M05 |

### 4.2 Örnek G-Kod Programı

```gcode
%
O1000 (CAM KESME PROGRAMI)
(Material: 6000x3000x10mm)
(Tool: Diamond Wheel D25mm)

(Tüm eksenleri referansa gönder)
G28 X0 Y0 Z0

(Hızlı hareket başlangıç pozisyonuna)
G90 G00 X100 Y200
(Z ekseni aşağı - kesim pozisyonu)
G01 Z-5 F500
(Kesim başlat)
M03
(İlk kesim - X ekseni)
G01 X5900 F2000
(Z ekseni yukarı)
G00 Z50
M05
(Hızlı geri dönüş)
G00 Y400
(Tekrar aşağı)
G01 Z-5 F500
M03
(İkinci kesim - geri yön)
G01 X100 F2000
G00 Z50
M05
(Program sonu)
G28 X0 Y0
M30
%
```

## 5. E-Cam (Elektronik Kam) Programlama

### 5.1 E-Cam Tanımlama

Lamine kesim için alt ve üst eksen senkronizasyonu:

```pascal
// E-Cam Tablosu Tanımlama
ECamTable[1]:
    MasterAxis := AXIS_2;    // Y Ekseni (Üst)
    SlaveAxis := AXIS_4;     // Alt Ekseni
    TableType := LINEAR;
    
    // Kam profili noktaları
    Points[0]: MasterPos := 0;    SlavePos := 0;
    Points[1]: MasterPos := 100;  SlavePos := 100;
    Points[2]: MasterPos := 200;  SlavePos := 199.5;  // Offset
    Points[3]: MasterPos := 300;  SlavePos := 300;
    Points[4]: MasterPos := 400;  SlavePos := 400;
    
    // E-Cam parametreleri
    SyncVelocity := 100.0;       // %
    SyncAcceleration := 50.0;    // %
    Deceleration := 50.0;        // %
    FlyDwell := FALSE;
    
// E-Cam başlatma
ECamEngage(
    TableID := 1,
    MasterStart := 0,
    SlaveStart := 0,
    Ratio := 1.0
);
```

### 5.2 Lamine Kesim Döngüsü

```pascal
PROGRAM LamineCutting
VAR
    CutLength : REAL := 500.0;  // mm
    CutCount : INT := 0;
    TotalCuts : INT := 10;
END_VAR

// Ana döngü
WHILE CutCount < TotalCuts DO
    // E-Cam senkronizasyonu başlat
    ECamEngage(TableID := 1);
    
    // Kesim uzunluğu kadar hareket
    MC_MoveRelative(
        Axis := AXIS_2,
        Distance := CutLength,
        Velocity := 30000,
        Acceleration := 1000,
        Deceleration := 1000
    );
    
    // Kesim tamamlandı
    IF MC_MoveRelative.Done THEN
        CutCount := CutCount + 1;
        
        // E-Cam bırak
        ECamDisengage(TableID := 1);
        
        // Hızlı geri dönüş
        MC_MoveAbsolute(
            Axis := AXIS_2,
            Position := 0,
            Velocity := 50000,
            Acceleration := 2000,
            Deceleration := 2000
        );
    END_IF;
END_WHILE;

END_PROGRAM
```

## 6. PLC Programlama (Structured Text)

### 6.1 Ana Program Yapısı

```pascal
PROGRAM MAIN
VAR
    // Sistem durumları
    SystemState : INT := 0;      // 0=Idle, 1=Ready, 2=Running, 3=Error
    EmergencyStop : BOOL;
    ServoEnable : BOOL;
    
    // Eksen komutları
    X_Command : REAL;
    Y_Command : REAL;
    Z_Command : REAL;
    
    // Sensör girişleri
    X_LimitPlus : BOOL;
    X_LimitMinus : BOOL;
    X_Home : BOOL;
    GlassDetect : BOOL;
    
    // Çıkışlar
    VacuumPump : BOOL;
    WarningLight : BOOL;
    Buzzer : BOOL;
END_VAR

// Girişleri oku
EmergencyStop := NOT %IX0.12;  // E-STOP1 (NC kontak)
X_LimitPlus := %IX0.0;
X_LimitMinus := %IX0.1;
X_Home := %IX0.2;
GlassDetect := %IX1.0;

// Durum makinesi
CASE SystemState OF
    0: // IDLE
        ServoEnable := FALSE;
        VacuumPump := FALSE;
        WarningLight := FALSE;
        
        // Başlatma koşullarını kontrol et
        IF NOT EmergencyStop AND NOT X_LimitPlus AND NOT X_LimitMinus THEN
            SystemState := 1;  // READY
        END_IF;
        
    1: // READY
        WarningLight := TRUE;  // Yeşil yanıp sönme
        
        // Servo enable
        IF ServoEnable THEN
            MC_Power(
                Axis := AXIS_1,
                Enable := TRUE,
                Regulator := TRUE
            );
            SystemState := 2;  // RUNNING
        END_IF;
        
    2: // RUNNING
        WarningLight := FALSE;
        
        // Acil durdurma kontrolü
        IF EmergencyStop THEN
            MC_Power(
                Axis := AXIS_1,
                Enable := FALSE,
                Regulator := FALSE
            );
            SystemState := 3;  // ERROR
        END_IF;
        
        // Cam algılama
        IF GlassDetect THEN
            VacuumPump := TRUE;
        END_IF;
        
    3: // ERROR
        Buzzer := TRUE;
        WarningLight := TRUE;  // Kırmızı sabit
        
        // Reset bekleniyor
        IF NOT EmergencyStop AND Reset_Button THEN
            Buzzer := FALSE;
            SystemState := 0;  // IDLE
        END_IF;
        
END_CASE;

// Çıkışları yaz
%QX0.0 := ServoEnable;
%QX0.1 := VacuumPump;
%QX0.4 := WarningLight;
%QX0.5 := Buzzer;

END_PROGRAM
```

### 6.2 Referans Dönüş Fonksiyonu

```pascal
FUNCTION_BLOCK FB_HomeSequence
VAR_INPUT
    Start : BOOL;
    Axis : MC_Axis_Ref;
END_VAR
VAR_OUTPUT
    Done : BOOL;
    Error : BOOL;
    ErrorID : INT;
END_VAR
VAR
    Step : INT := 0;
    HomeSwitch : BOOL;
END_VAR

CASE Step OF
    0: // Bekle
        Done := FALSE;
        Error := FALSE;
        IF Start THEN
            Step := 10;
        END_IF;
        
    10: // Eksen geri yönde hareket
        MC_MoveVelocity(
            Axis := Axis,
            Velocity := -1000,
            Acceleration := 500,
            Deceleration := 500
        );
        Step := 20;
        
    20: // Home switch ara
        IF HomeSwitch THEN
            MC_MoveVelocity(
                Axis := Axis,
                Velocity := -100,
                Acceleration := 200,
                Deceleration := 200
            );
            Step := 30;
        END_IF;
        
    30: // Switch'ten çık ve tekrar yaklaş
        IF NOT HomeSwitch THEN
            MC_MoveVelocity(
                Axis := Axis,
                Velocity := 100,
                Acceleration := 200,
                Deceleration := 200
            );
            Step := 40;
        END_IF;
        
    40: // Home switch'e tekrar yaklaş (rising edge)
        IF HomeSwitch THEN
            // Pozisyonu sıfırla
            MC_SetPosition(
                Axis := Axis,
                Position := 0
            );
            Step := 50;
        END_IF;
        
    50: // Dur ve tamamla
        MC_Stop(Axis := Axis);
        Done := TRUE;
        Step := 100;
        
    100: // Son
        ;
        
END_CASE;

END_FUNCTION_BLOCK
```

## 7. HMI Entegrasyonu (Modbus TCP)

### 7.1 NC300 Modbus Register Map

| Adres | Açıklama | Tip | Erişim |
|-------|----------|-----|--------|
| 40001 | System Status | UINT16 | R |
| 40002 | Alarm Code | UINT16 | R |
| 40003 | X Actual Position | REAL | R |
| 40004 | Y Actual Position | REAL | R |
| 40005 | Z Actual Position | REAL | R |
| 40006 | X Command Position | REAL | R |
| 40007 | Y Command Position | REAL | R |
| 40008 | Z Command Position | REAL | R |
| 40009 | Feed Rate Override | UINT16 | R/W |
| 40010 | Start Command | UINT16 | W |
| 40011 | Stop Command | UINT16 | W |
| 40012 | Reset Command | UINT16 | W |
| 40013 | Home All Axes | UINT16 | W |
| 40014 | Program Number | UINT16 | R/W |
| 40015 | Cycle Count | UINT16 | R |

### 7.2 DOP-110CS Ekran Yapısı

#### Ana Ekran
- Sistem durumu göstergesi
- Eksen pozisyonları (X, Y, Z)
- Feed rate override slider
- Start/Stop/Reset butonları
- Aktif program numarası

#### Manuel Ekranı
- Jog butonları (X+, X-, Y+, Y-, Z+, Z-)
- Hız seçimi (%10, %50, %100)
- Servo ON/OFF
- Vakum ON/OFF

#### Otomatik Ekranı
- Program listesi
- Cycle sayısı
- Kesim uzunluğu ayarı
- Parça sayısı ayarı

#### Alarm Ekranı
- Aktif alarm listesi
- Alarm geçmişi
- Alarm açıklaması

## 8. Dosya Yapısı

```
Firmware/NC300/
├── GFB60-30RE_CNC.isp         # ISPSoft projesi
├── Hardware/
│   ├── EtherCAT_Config.xml    # EtherCAT konfigürasyonu
│   └── Axis_Params.xml        # Eksen parametreleri
├── PLC/
│   ├── MAIN.st                # Ana program
│   ├── Homing.st              # Referans fonksiyonları
│   ├── Safety.st              # Güvenlik mantığı
│   └── E-Cam.st               # E-Cam programları
├── ST/
│   ├── Lamine_ClearPath_Main.st # G31 + germe + isitici + E-Cam referansi
│   └── README.md                # FreeCAD parametre eslesmeleri
├── GCode/
│   ├── Standard_Cut.nc        # Standart kesim programı
│   ├── Lamine_Cut.nc          # Lamine kesim programı
│   ├── Lamine_ClearPath.nc    # G31 + X lock + E-Cam + tension macro
│   └── Custom_Patterns/       # Özel desenler
├── HMI/
│   └── GFB60-30RE_HMI.dop     # DiaDesigner projesi
└── Documentation/
    ├── IO_Map.pdf             # I/O haritası
    └── Alarm_List.pdf         # Alarm listesi
```

### 8.1 Lamine Clear Path ST Referansı

Bu revizyonda FreeCAD ve NC300 analizinden türetilen lamine proses mantığı için hazır ST referansı eklendi:

- `/Users/oktaycit/Projeler/CNCRevizyon/Firmware/NC300/ST/Lamine_ClearPath_Main.st`

Kapsadığı başlıklar:
- G31 benzeri kenar bulma ve vantuzlu köprü referanslama
- folyo germe için milimetrik X geri çekme hesabı
- `T1 = -(U1 + V1 - W1)` düzeltme mantığı
- ısıtıcı interlock zinciri ve zon çıkışları
- Leuze home/limit sensörlerinin çevrim geçişlerine katılması
- üst kafa ile alt eksen arasında E-Cam angajmanı ve senkron kesim

### 8.2 Lamine Clear Path G-Code Referansı

Makro referansı:

- `/Users/oktaycit/Projeler/CNCRevizyon/Firmware/NC300/GCode/Lamine_ClearPath.nc`

Temel akış:
- `M10` ile vakum açılır ve cam tutulur
- `G31 X-100` ile cam kenarı bulunur
- `G92 X0` ile cam kenarı sıfırlanır
- `G01 X[#2007]` ile cam kesim konumuna sürülür
- `M11` ile X ekseni kilitlenir
- `#2000 = 1` sonrası sadece `Y` hareketi ile E-Cam kesimi yapılır
- `M12` ve `G04 P[#2003]` ile ısıtma beklemesi yürütülür
- `G01 X[#2007 + #2005]` ve geri settle ile folyo gerilir
- `M13` ile ayırma/kırma başlatılır

### 8.3 I/O ve User Variable Onerisi

Onerilen user variable alani:
- `#2000` E-Cam enable
- `#2001` Lamine mode enable
- `#2002` X lock command
- `#2003` Heater dwell ms
- `#2004` Probe backoff mm
- `#2005` Tension retract mm
- `#2006` Tension settle mm
- `#2007` Cut X target mm
- `#2008` Cut Y target mm
- `#2009` Heater work offset mm
- `#2010` Park retract mm

Onerilen ciktilar:
- `QX0.0` SIR heater valve
- `QX0.1` Vacuum valve
- `QX0.2` X axis lock
- `QX0.3` Break start
- `QX0.4` E-Cam active relay

## 9. Test Prosedürü

### 9.1 PLC Testi
```pascal
// Test programı - Manuel mod
TEST_Manual:
    // Servo enable test
    ServoEnable := TRUE;
    WAIT_TIME(1000);
    
    // X ekseni jog test
    MC_MoveVelocity(
        Axis := AXIS_1,
        Velocity := 1000,
        Enable := TRUE
    );
    WAIT_TIME(2000);
    MC_MoveVelocity(Axis := AXIS_1, Enable := FALSE);
    
    // Limit switch test
    IF X_LimitPlus THEN
        TestResult := 'X+LIMIT OK';
    ELSE
        TestResult := 'X+LIMIT FAIL';
    END_IF;
```

### 9.2 G-Kod Testi
```gcode
%
O9999 (TEST PROGRAMI)
G21 G90 G94
G28 X0 Y0 Z0

(Test kesim döngüsü)
G00 X100 Y100
G01 Z-2 F300
G01 X200 F500
G00 Z10
G28 X0 Y0
M30
%
```

## 10. Hata Kodları

| Kod | Açıklama | Çözüm |
|-----|----------|-------|
| E001 | EtherCAT Communication Error | Kablo bağlantısını kontrol et |
| E002 | Following Error | Gain ayarlarını kontrol et |
| E003 | Over Travel | Limit switch pozisyonunu kontrol et |
| E004 | Servo Alarm | Sürücü alarm kodunu kontrol et |
| E005 | E-Stop Active | E-Stop butonunu sıfırla |
| E006 | Air Pressure Low | Hava basıncını kontrol et |
| E007 | Glass Not Detected | Cam sensörünü kontrol et |
