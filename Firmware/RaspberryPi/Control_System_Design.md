# STM32 / Raspberry Pi Kontrol Sistemi Tasarımı
## Lisec GFB 60-30 Cam Kesme Makinesi

## 1. Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Ana Kontrol Sistemi                          │
│                                                                     │
│  ┌─────────────────┐              ┌─────────────────────────────┐  │
│  │   Raspberry Pi  │◄──Ethernet──►│    Delta NC300              │  │
│  │   (Ana PC)      │              │    (Motion Controller)      │  │
│  │                 │              │                             │  │
│  │  - Python UI    │              │  - X Ekseni Sürücü          │  │
│  │  - AI Engine    │              │  - Y Ekseni Sürücü          │  │
│  │  - Vision       │              │  - Z Ekseni Sürücü          │  │
│  └─────────────────┘              └─────────────────────────────┘  │
│           │                                                         │
│           │ GPIO/I2C/SPI                                            │
│           ▼                                                         │
│  ┌─────────────────┐                                               │
│  │   STM32 Board   │                                               │
│  │   (I/O Controller)                                              │
│  │                 │                                               │
│  │  - Limit Sw.    │                                               │
│  │  - E-Stop       │                                               │
│  │  - Sensors      │                                               │
│  │  - Relays       │                                               │
│  └─────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## 2. Raspberry Pi Seçimi

### 2.1 Önerilen Model
**Raspberry Pi 4 Model B (4GB)** veya **Raspberry Pi 5 (4GB)**

| Özellik | RPi 4 | RPi 5 |
|---------|-------|-------|
| CPU | Quad-core Cortex-A72 | Quad-core Cortex-A76 |
| RAM | 2/4/8 GB | 4/8 GB |
| Ethernet | Gigabit | Gigabit (PoE+ destekli) |
| USB | 2x USB3, 2x USB2 | 2x USB3, 2x USB2 |
| GPIO | 40-pin | 40-pin |

### 2.2 Alternatif: Endüstriyel PLC
**Kunbus RevPi Connect 4** veya **RevPi Core 3**

## 3. STM32 Tabanlı I/O Kontrolcü

### 3.1 Önerilen MCU
**STM32F407VGT6** veya **STM32F767VIT6**

| Özellik | STM32F407 | STM32F767 |
|---------|-----------|-----------|
| CPU | Cortex-M4 @ 168 MHz | Cortex-M7 @ 216 MHz |
| Flash | 1 MB | 2 MB |
| SRAM | 192 KB | 512 KB |
| ADC | 3x 12-bit | 3x 16-bit |
| DAC | 2x 12-bit | 2x 12-bit |
| Ethernet | Var | Var |
| CAN | 2x | 2x |

### 3.2 I/O Haritalaması

#### Digital Inputs (DI)
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| PA0 | X+LIMIT | X ekseni + limit switch |
| PA1 | X-LIMIT | X ekseni - limit switch |
| PA2 | X-HOME | X ekseni referans |
| PA3 | Y+LIMIT | Y ekseni + limit switch |
| PA4 | Y-LIMIT | Y ekseni - limit switch |
| PA5 | Y-HOME | Y ekseni referans |
| PA6 | Z+LIMIT | Z ekseni + limit switch |
| PA7 | Z-LIMIT | Z ekseni - limit switch |
| PA8 | Z-HOME | Z ekseni referans |
| PA9 | E-STOP1 | Acil durdurma 1 |
| PA10 | E-STOP2 | Acil durdurma 2 |
| PA11 | DOOR_OPEN | Güvenlik kapısı |
| PA12 | VACUUM_OK | Vakum sensörü |
| PA13 | OIL_LEVEL | Yağ seviyesi |
| PA14 | AIR_PRESSURE | Hava basıncı |
| PA15 | GLASS_DETECT | Cam algılama |

#### Digital Outputs (DO)
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| PB0 | SERVO_ENABLE_X | X servo enable |
| PB1 | SERVO_ENABLE_Y | Y servo enable |
| PB2 | SERVO_ENABLE_Z | Z servo enable |
| PB3 | VACUUM_PUMP | Vakum pompası |
| PB4 | OIL_PUMP | Yağ pompası |
| PB5 | COOLING_FAN | Soğutma fanı |
| PB6 | WARNING_LIGHT | Uyarı lambası |
| PB7 | BUZZER | Zil |
| PB8 | LIGHT_CURTAIN | Işık perdesi enable |
| PB9 | MARKER | İşaretleme solenoid |

#### Analog Inputs (AI)
| Pin | Sinyal | Açıklama |
|-----|--------|----------|
| PC0 | PRESSURE_X | X ekseni basınç sensörü |
| PC1 | PRESSURE_Y | Y ekseni basınç sensörü |
| PC2 | CURRENT_X | X motor akımı |
| PC3 | CURRENT_Y | Y motor akımı |
| PC4 | TEMPERATURE | Sıcaklık sensörü |
| PC5 | VIBRATION | Titreşim sensörü |

## 4. Haberleşme Protokolleri

### 4.1 Raspberry Pi ↔ STM32
**UART/USB Serial** veya **SPI**

```python
# Python - Raspberry Pi tarafı
import serial
import time

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

def send_command(cmd):
    ser.write(f"{cmd}\n".encode())
    
def read_response():
    return ser.readline().decode().strip()

# Örnek kullanım
send_command("GET_STATUS")
status = read_response()
```

**STM32 Firmware (UART Interrupt)**
```c
// STM32CubeIDE HAL UART Callback
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2) {
        // Komutu işle
        ProcessCommand(uart_rx_buffer);
        // Yeni okuma başlat
        HAL_UART_Receive_IT(huart, uart_rx_buffer, RX_BUFFER_SIZE);
    }
}
```

### 4.2 Raspberry Pi ↔ Delta NC300
**Modbus TCP** veya **EtherCAT**

```python
# Python - Modbus TCP örneği
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('192.168.1.100')

def move_absolute(x, y, z):
    # Hedef pozisyonları yaz
    client.write_register(0x1000, int(x * 1000))  # X * 1000 (um)
    client.write_register(0x1001, int(y * 1000))  # Y * 1000
    client.write_register(0x1002, int(z * 1000))  # Z * 1000
    # Hareketi başlat
    client.write_register(0x2000, 0x0001)  # START bit

def read_position():
    # Pozisyonları oku
    x = client.read_holding_registers(0x3000, 1).registers[0] / 1000
    y = client.read_holding_registers(0x3001, 1).registers[0] / 1000
    z = client.read_holding_registers(0x3002, 1).registers[0] / 1000
    return x, y, z
```

### 4.3 Raspberry Pi ↔ Delta Servo Sürücü
**EtherCAT** (CANopen over EtherCAT)

```python
# Python - SOEM (Simple Open EtherCAT Master)
import soem

def init_ethercat():
    ec = soem.SimpleOpenEtherCAT()
    ec.open('eth0')
    ec.config_init()
    ec.config_map()
    ec.state_write(soem.SAFEOP_OP, False)
    return ec

def send_position_command(ec, axis, position):
    # PDO mapping through EtherCAT
    process_data = ec.get_process_data()
    process_data[axis]['position'] = position
    ec.send_process_data()
```

## 5. Raspberry Pi GPIO Bağlantıları

### 5.1 GPIO Pin Assignment
| GPIO | Fonksiyon | Açıklama |
|------|-----------|----------|
| GPIO2 | I2C_SDA | I2C data (RTC, EEPROM) |
| GPIO3 | I2C_SCL | I2C clock |
| GPIO4 | SPI_CE0 | SPI chip select 0 |
| GPIO5 | SPI_CE1 | SPI chip select 1 |
| GPIO6 | SPI_CE2 | SPI chip select 2 |
| GPIO7 | SPI_MOSI | SPI data out |
| GPIO8 | SPI_MISO | SPI data in |
| GPIO9 | SPI_SCLK | SPI clock |
| GPIO10 | UART_TX | STM32 TX |
| GPIO11 | UART_RX | STM32 RX |
| GPIO12 | PWM0 | Servo PWM enable |
| GPIO13 | STATUS_LED | Durum LED |
| GPIO14 | UART_TXD | Konsol TX |
| GPIO15 | UART_RXD | Konsol RX |
| GPIO16 | RELAY1 | Röle kontrol 1 |
| GPIO17 | RELAY2 | Röle kontrol 2 |
| GPIO18 | PWM1 | Işık kontrolü |
| GPIO27 | INPUT1 | Dijital giriş 1 |
| GPIO22 | INPUT2 | Dijital giriş 2 |
| GPIO23 | INPUT3 | Dijital giriş 3 |
| GPIO24 | INPUT4 | Dijital giriş 4 |

### 5.2 Röle Kartı Bağlantısı
```
Raspberry Pi          8-Channel Relay Module
───────────           ──────────────────────
GPIO16 (RELAY1)  ───► IN1  → Vakum Pompası
GPIO17 (RELAY2)  ───► IN2  → Yağ Pompası
GPIO5V           ───► VCC
GPIO_GND         ───► GND
```

## 6. Yazılım Mimarisi

### 6.1 Python Ana Program Yapısı
```python
# main.py
import asyncio
from controllers import MotionController, IOController
from ai import CuttingOptimizer
from hmi import WebInterface

class GlassCuttingMachine:
    def __init__(self):
        self.motion = MotionController()
        self.io = IOController()
        self.optimizer = CuttingOptimizer()
        self.hmi = WebInterface()
        
    async def run(self):
        # Tüm görevleri paralel çalıştır
        await asyncio.gather(
            self.motion_loop(),
            self.io_loop(),
            self.hmi.serve()
        )
    
    async def motion_loop(self):
        while True:
            await self.motion.update()
            await asyncio.sleep(0.001)  # 1 kHz
    
    async def io_loop(self):
        while True:
            await self.io.read_inputs()
            await self.io.write_outputs()
            await asyncio.sleep(0.01)  # 100 Hz

if __name__ == '__main__':
    machine = GlassCuttingMachine()
    asyncio.run(machine.run())
```

### 6.2 STM32 Firmware Yapısı
```c
// main.c
#include "main.h"
#include "usart.h"
#include "gpio.h"
#include "adc.h"

// Global değişkenler
volatile uint8_t uart_rx_buffer[RX_BUFFER_SIZE];
volatile uint8_t uart_tx_buffer[TX_BUFFER_SIZE];
IO_State io_state;

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_USART2_UART_Init();
    MX_ADC1_Init();
    
    // UART interrupt okumayı başlat
    HAL_UART_Receive_IT(&huart2, uart_rx_buffer, RX_BUFFER_SIZE);
    
    while (1) {
        // Ana döngü
        Read_Inputs();
        Process_Commands();
        Write_Outputs();
        HAL_Delay(10);  // 100 Hz
    }
}

// UART Interrupt Handler
void USART2_IRQHandler(void)
{
    HAL_UART_IRQHandler(&huart2);
}
```

## 7. Güvenlik Fonksiyonları

### 7.1 Watchdog Timer
```python
# Python watchdog
from watchdog import Watchdog

wd = Watchdog(timeout=5.0)

def safety_loop():
    while True:
        if not wd.pet():
            # Watchdog timeout - güvenli durdurma
            emergency_stop()
        time.sleep(0.5)
```

```c
// STM32 IWDG
void IWDG_Init(void)
{
    // 40kHz LSI, 256 prescaler = ~6.4s timeout
    IWDG->KR = 0x5555;  // Enable register access
    IWDG->PR = 0x06;    // Prescaler 256
    IWDG->RLR = 0xFFF;  // Reload value
    IWDG->KR = 0xAAAA;  // Reload
    IWDG->KR = 0xCCCC;  // Start IWDG
}

void IWDG_Feed(void)
{
    IWDG->KR = 0xAAAA;  // Reload
}
```

### 7.2 Acil Durdurma Fonksiyonu
```python
async def emergency_stop():
    """Acil durdurma prosedürü"""
    # 1. Servoları disable et
    await io.write_output('SERVO_ENABLE_X', False)
    await io.write_output('SERVO_ENABLE_Y', False)
    await io.write_output('SERVO_ENABLE_Z', False)
    
    # 2. Vakumu kapat
    await io.write_output('VACUUM_PUMP', False)
    
    # 3. Uyarı lambasını yak
    await io.write_output('WARNING_LIGHT', True)
    await io.write_output('BUZZER', True)
    
    # 4. NC'ye acil durdurma gönder
    await motion.emergency_stop()
    
    # 5. Log kaydı
    logger.critical("EMERGENCY STOP ACTIVATED")
```

## 8. Dosya Yapısı

```
Firmware/
├── RaspberryPi/
│   ├── src/
│   │   ├── main.py              # Ana program
│   │   ├── motion_controller.py # Hareket kontrolü
│   │   ├── io_controller.py     # I/O kontrolü
│   │   ├── optimizer.py         # Kesim optimizasyonu
│   │   └── hmi_server.py        # Web arayüzü
│   ├── requirements.txt         # Python dependencies
│   └── config/
│       ├── machine_config.yaml  # Makine parametreleri
│       └── servo_config.yaml    # Servo ayarları
└── STM32/
    ├── Core/
    │   ├── Inc/
    │   │   ├── main.h
    │   │   ├── io_map.h
    │   │   └── protocol.h
    │   └── Src/
    │       ├── main.c
    │       ├── io_control.c
    │       └── uart_protocol.c
    ├── Drivers/
    │   ├── HAL/
    │   └── CMSIS/
    └── .ioc                     # STM32CubeMX projesi
```

## 9. Test ve Debug

### 9.0 NC300 Orta Seviye Simülatör

Bu repo içinde register tabanlı bir NC300 simülatörü de eklenmiştir:

- `Firmware/RaspberryPi/src/nc300_simulator.py`

Kapsam:
- hedef pozisyon register'ları
- X/Y/Z/V eksen motion loop
- lamine çevrim state machine
- dijital giriş / çıkış mantığı
- alarm ve status word üretimi

Örnek kullanım:

```bash
python3 Firmware/RaspberryPi/src/nc300_simulator.py --demo --seconds 10 --json
```

### 9.1 Unit Testler
```python
# tests/test_motion.py
import pytest
from motion_controller import MotionController

def test_home_sequence():
    motion = MotionController()
    result = motion.execute_home_sequence()
    assert result == True
    assert motion.get_position() == (0, 0, 0)

def test_linear_move():
    motion = MotionController()
    motion.move_linear(100, 200, 50)
    assert motion.get_position() == (100, 200, 50)
```

### 9.2 Integration Test
```bash
# Test çalıştırma
cd Firmware/RaspberryPi
pytest tests/ -v

# Coverage raporu
pytest tests/ --cov=src --cov-report=html
```

## 10. Kurulum ve Başlangıç

### 10.1 Raspberry Pi Kurulumu
```bash
# 1. Raspberry Pi OS kurulumu
# 2. Güncellemeler
sudo apt update && sudo apt upgrade -y

# 3. Python bağımlılıkları
pip3 install -r requirements.txt

# 4. Servis olarak ekleme
sudo cp cnc-machine.service /etc/systemd/system/
sudo systemctl enable cnc-machine
sudo systemctl start cnc-machine
```

### 10.2 STM32 Programlama
```bash
# 1. STM32CubeIDE ile derle
# 2. ST-Link ile yükle
st-flash write Release/firmware.bin 0x8000000
```

## 11. Malzeme Listesi

| No | Ürün | Model | Miktar |
|----|------|-------|--------|
| 1 | Raspberry Pi 4 | 4GB Model B | 1 |
| 2 | Raspberry Pi Power Supply | 5V 3A USB-C | 1 |
| 3 | STM32F407VGT6 Board | Nucleo-144 | 1 |
| 4 | 8-Channel Relay Module | 5V Opto-Isolated | 1 |
| 5 | RTC Module | DS3231 I2C | 1 |
| 6 | Ethernet Switch | 5-Port Gigabit | 1 |
| 7 | USB-RS485 Adapter | FTDI | 1 |
| 8 | 24V Power Supply | 5A DIN-Rail | 1 |
| 9 | Enclosure | IP65 Control Box | 1 |
| 10 | Cooling Fan | 24V 80mm | 2 |
