# How to Use the GFB-60/30RE-S Fritzing Project

## Prerequisites

1. **Install Fritzing** on your system:
   - Download from [fritzing.org](https://fritzing.org/download/)
   - Install the latest version compatible with your operating system

2. **Import Custom Parts** (if needed):
   - The custom parts are already defined in the `.fzp` files
   - Fritzing should automatically recognize them when opening the main project file

## Opening the Project

1. Navigate to the Fritzing project directory:

   ```bash
   cd /Users/oktaycit/Projeler/CNCRevizyon/Electrical/Schematics/Fritzing_Project
   ```

2. Open the main project file in Fritzing:
   - Launch Fritzing application
   - File → Open → Select `GFB-60-30RE-S.fzz`

## Project Structure Overview

### Main Components

- **Delta NC300 Controller**: Central motion controller with EtherCAT communication
- **3x Delta ASDA-A3-E Servo Drivers**: One each for X, Y, and Z axes
- **2x R1-EC I/O Modules**: Handle all sensor inputs (16 channels each)
- **12x Leuze IS 218 Sensors**: Limit and home position detection
- **Power Distribution**: +24V and GND connections throughout

### Connection Topology

- **EtherCAT Daisy Chain**: NC300 → Servo_X → I/O_Module_1 → Servo_Y → I/O_Module_2 → Servo_Z → NC300
- **Power Bus**: +24V and GND distributed to all components
- **Sensor Matrix**: All sensors connected to I/O modules based on axis and function

## Views Available in Fritzing

1. **Breadboard View**: Shows physical layout and component placement
2. **Schematic View**: Shows electrical connections and signal flow
3. **PCB View**: Shows potential printed circuit board layout (if applicable)

## Modifying the Design

- **Add/Remove Components**: Use Fritzing's part library or custom parts
- **Modify Connections**: Click and drag to create or remove wires
- **Edit Component Properties**: Right-click on components to access properties

## Exporting Options

From Fritzing, you can export:

- **PDF Schematics**: File → Export → As PDF
- **PNG Images**: File → Export → As Image
- **Gerber Files**: For PCB manufacturing (File → Export → For PCB)

## Reference Documentation

- **Original KiCad Schematic**: Located at `../KiCad_Project/GFB_60_30RE_Schematic.kicad_sch`
- **Sensor Specifications**: Detailed in `Sensor_Mounting_Details.md`
- **Project Requirements**: Documented in `Documentation/Reports/GFB-60-30RE-S_Lamine_Revizyon.md`

## Troubleshooting

### Missing Parts

If custom parts don't appear correctly:

1. Ensure all `.fzp` files are in the `parts/` directory
2. Check that the main `.fzz` file references the correct part IDs
3. You may need to manually import parts via Fritzing's Parts Editor

### Connection Issues

- Verify that all pin names match between components
- Check that power and ground connections are properly established
- Ensure EtherCAT daisy chain is correctly configured

### Performance Notes

- This project contains multiple custom components which may slow down Fritzing
- Consider working with simplified views if performance is an issue

## Safety Reminders

- **Limit Switches**: Configured as Normally Closed (NC) for safety
- **Emergency Stop**: Uses redundant NC configuration
- **Home Sensors**: Configured as Normally Open (NO) for reference detection
- Always verify safety circuits before implementing in hardware

## Next Steps

1. **Review the schematic** in Fritzing to ensure it matches your requirements
2. **Validate connections** against the original KiCad design
3. **Test with actual hardware** using proper safety protocols
4. **Document any modifications** made to the Fritzing project

## Support and Questions

For questions about this Fritzing project:

- Refer to the main README.md file for technical specifications
- Consult the original KiCad schematic for detailed pin assignments
- Review the sensor mounting documentation for physical installation details
