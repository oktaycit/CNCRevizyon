# GFB-60/30RE-S Fritzing Project

## Overview

This Fritzing project represents the electrical revision schematic for the Lisec GFB-60/30RE glass cutting machine CNC revision project.

## Components Included

- **Delta NC300 Motion Controller**: Main CNC controller with EtherCAT communication
- **Delta ASDA-A3-E Servo Drivers**: 3 units for X, Y, and Z axes with EtherCAT interface
- **R1-EC I/O Modules**: 2 units providing 16 digital inputs each for sensor connections
- **Leuze IS 218 Inductive Sensors**: 12 sensors for limit/home detection with M12 connectors
- **Power Supply**: +24V DC distribution system

## Electrical Connections

### Power Distribution

- +24V DC connected to all servo drivers, I/O modules, and sensors
- Common ground (GND) connected to all components

### EtherCAT Network

- Daisy-chain topology: NC300 → Servo X → I/O Module 1 → Servo Y → I/O Module 2 → Servo Z → NC300
- High-speed real-time communication for motion control and I/O data

### Sensor Connections

- All Leuze IS 218 sensors connected to R1-EC I/O modules:
  - **Module 1**: X+LIMIT, X-LIMIT, X-HOME, Y+LIMIT, Y-LIMIT, Y-HOME, Z+LIMIT, Z-HOME
  - **Module 2**: ALT+LIM, ALT-LIM, ALT-HOM, E-STOP

### Control Signals

- NC300 outputs control signals to servo drivers for axis movement
- Servo drivers provide feedback signals to NC300 for position verification

## File Structure

```
Fritzing_Project/
├── GFB-60-30RE-S.fzz          # Main Fritzing project file
├── parts/                      # Custom component definitions
│   ├── Delta_NC300.fzp         # NC300 controller definition
│   ├── Delta_ASDA_A3E.fzp      # Servo driver definition  
│   ├── R1_EC_IO_Module.fzp     # I/O module definition
│   └── Leuze_IS218.fzp         # Sensor definition
└── README.md                   # This documentation file
```

## Usage Notes

Since Fritzing is not installed on the current system, this project provides the XML structure and component definitions that can be imported into Fritzing when available. The main `.fzz` file contains the complete connection mapping based on the original KiCad schematic.

## Reference Documentation

- Original KiCad schematic: `Electrical/Schematics/KiCad_Project/GFB_60_30RE_Schematic.kicad_sch`
- Sensor mounting details: `Electrical/Schematics/Sensor_Mounting_Details.md`

## Technical Specifications

- **Power**: 24V DC, 20mA max per sensor
- **Communication**: EtherCAT protocol
- **Sensors**: Leuze IS 218 MM/AM series, M12 4-pin connector
- **I/O Modules**: R1-EC 16-channel digital I/O
- **Controller**: Delta NC300 with BGA-256 package
- **Servo Drivers**: Delta ASDA-A3-E with DIP-10 package

## Safety Considerations

- All limit switches configured as Normally Closed (NC) for safety
- Emergency stop circuits use redundant NC configuration
- Home sensors configured as Normally Open (NO) for reference detection
