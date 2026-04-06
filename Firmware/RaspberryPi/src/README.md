# Raspberry Pi Kontrol Katmanı

Bu klasör, makinenin kontrol tarafı için çalışan Python modüllerini içerir.

## NC300 Simülatörü

`nc300_simulator.py` orta seviye bir Delta NC300 taklididir.

Kapsam:
- register tabanlı komut alma
- X/Y/Z/V eksen pozisyon takibi
- lamine çevrim state machine
- dijital giriş/çıkış mantığı
- FreeCAD veya HMI entegrasyonu için callback noktası

Hızlı kullanım:

```bash
python3 Firmware/RaspberryPi/src/nc300_simulator.py --demo --seconds 10 --json
```

Register örnekleri:

- `0x1000-0x1003`: hedef pozisyonlar (`µm`)
- `0x1010-0x1013`: eksen hızları (`µm/s`)
- `0x2000`: hareket başlat
- `0x2001`: lamine çevrim başlat
- `0x3000-0x3003`: gerçek pozisyonlar
- `0x3010`: status word
- `0x3011`: aktif state
- `0x3012`: alarm kodu
