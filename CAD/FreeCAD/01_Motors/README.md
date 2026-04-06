# ECMA Servo Motor CAD Modelleri

Delta ECMA Servo Motorları için FreeCAD parametrik modelleme dosyaları.

## Dosyalar

| Dosya | Açıklama |
|-------|----------|
| `ECMA_Motor_Generator.py` | Tüm motorları tek FreeCAD dosyasında oluşturan script |
| `ECMA_Motor_STEP_Export.py` | Her motoru ayrı STEP dosyası olarak export eden script |

## Motor Modelleri

### ECMA-L11845 (4.5kW X Ekseni)
- **Flanş:** 180 mm
- **Mil Çapı:** 48 mm
- **Mil Uzunluğu:** 110 mm
- **Gövde Uzunluğu:** 215 mm (frensiz)
- **Toplam Uzunluk:** 340 mm (konektörlü)

### ECMA-E11320 (2.0kW Y/Alt Ekseni)
- **Flanş:** 130 mm
- **Mil Çapı:** 24 mm
- **Mil Uzunluğu:** 50 mm
- **Gövde Uzunluğu:** 170 mm

### ECMA-C11010 (1.0kW Frenli Z Ekseni)
- **Flanş:** 100 mm
- **Mil Çapı:** 24 mm
- **Mil Uzunluğu:** 50 mm
- **Fren Çapı:** Ø90 mm
- **Gövde Uzunluğu:** 165 mm (frenli)

### ECMA-E11315 (1.5kW IP67)
- **Flanş:** 130 mm
- **Mil Çapı:** 24 mm
- **Mil Uzunluğu:** 50 mm
- **Gövde Uzunluğu:** 155 mm

## Kullanım

### Yöntem 1: FreeCAD Macro Menüsü

1. **FreeCAD'i açın**
2. **Macro → Macros...** menüsüne tıklayın
3. **Create** butonuna basın
4. Dosya adı: `ECMA_Motors` yazın
5. Editör açılınca, `ECMA_Motor_STEP_Export.py` dosyasının içeriğini kopyalayıp yapıştırın
6. **Run** butonuna basın

### Yöntem 2: Python Console

FreeCAD Python Console'da şu komutu çalıştırın:

```python
exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/01_Motors/ECMA_Motor_STEP_Export.py").read())
```

### Yöntem 3: Command Line

```bash
freecadcmd --console "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/01_Motors/ECMA_Motor_STEP_Export.py"
```

## Çıktı Dosyaları

Script çalıştırıldığında aşağıdaki dosyalar oluşturulur:

### FreeCAD Dosyaları (.fcstd)
- `ECMA_L11845.fcstd` - 4.5kW X ekseni motor
- `ECMA_E11320.fcstd` - 2.0kW Y ekseni motor
- `ECMA_C11010.fcstd` - 1.0kW frenli Z ekseni motor
- `ECMA_E11315.fcstd` - 1.5kW IP67 motor

### STEP Dosyaları
```
CAD/FreeCAD/07_Exports/STEP/Motors/
├── ECMA-L11845.stp
├── ECMA-E11320.stp
├── ECMA-C11010.stp
└── ECMA-E11315.stp
```

## Parametrik Değişiklikler

Script'teki fonksiyonları kullanarak özel motor modelleri oluşturabilirsiniz:

```python
import FreeCAD as App
import Part

# Script'i import et
exec(open("ECMA_Motor_Generator.py").read())

# Yeni doküman oluştur
doc = App.newDocument("Custom_Motor")

# Özel motor oluştur
create_ecma_l11845(doc, name="My_Custom_Motor")

doc.recompute()
```

## Notlar

- Ölçüler Delta datasheet'lerinden alınmıştır
- Montaj delikleri standart M8/M6 cıvatalar için tasarlanmıştır
- Kama yuvası (keyway) standart ölçülerdedir
- STEP dosyaları AP214 formatında export edilir

## Kaynaklar

- [Delta ECMA Motor Datasheetleri](https://www.delta-automation.com/tr/products/detail/ECMA/)
- [FreeCAD Dokümantasyon](https://wiki.freecad.org/)