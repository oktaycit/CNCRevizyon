# FreeCAD Lamine Sync Simulation

Date: 2026-04-17
Model: `/Users/oktaycit/Projeler/CNCRevizyon/CAD/30RE-S Hibrit Sistem.FCStd`
Method: FreeCAD MCP Python execution on the current FCStd model

## Scope

Simulated and sampled:

- upper/lower head synchronized Y-stroke alignment
- safe/home, synchronized drawing, and heads-up/break states
- key shape intersections and clearances against the simplified machine geometry

## Synchronized motion result

The upper and lower cutting wheels stay on the same X line through the full sampled Y stroke.

Sampled `Variables.B1` values:

- `Y=0 -> top_x=300.0 mm, low_x=300.0 mm, delta=0.0 mm`
- `Y=500 -> top_x=800.0 mm, low_x=800.0 mm, delta=0.0 mm`
- `Y=1400 -> top_x=1700.0 mm, low_x=1700.0 mm, delta=0.0 mm`
- `Y=2300 -> top_x=2600.0 mm, low_x=2600.0 mm, delta=0.0 mm`
- `Y=3000 -> top_x=3300.0 mm, low_x=3300.0 mm, delta=0.0 mm`

This confirms the current FCStd kinematics represent the upper/lower head E-cam style alignment as a perfect shared X track.

## Sampled states

Sampled spreadsheet states:

- `safe_home = (A1=500, B1=500, C1=0, D1=0)`
- `sync_draw = (A1=3500, B1=2300, C1=16, D1=250)`
- `heads_up_break = (A1=3500, B1=2300, C1=0, D1=0)`

## Collision / clearance findings

Measured with `Shape.distToShape()` and `Shape.common().Volume`.

### Persistent intersections in the current simplified model

- `Lower_Cutter_Head vs Table_Grid`
  - `distance = 0.0 mm`
  - `common volume = 400000.0 mm^3`
- `Lower_Cutting_Wheel vs Table_Grid`
  - `distance = 0.0 mm`
  - `common volume = 18849.556 mm^3`
- `Heater_Rod vs Table_Grid`
  - `distance = 0.0 mm`
  - `common volume = 35342.917 mm^3`
- `Pressure_Roller vs Table_Grid`
  - `distance = 0.0 mm`
  - `common volume = 141371.669 mm^3`

These intersections remain unchanged across the sampled states, so the current FCStd is suitable for kinematic alignment checks but not yet valid for mechanical clash approval.

### Non-intersecting sampled pairs

- `Breaking_Profile vs Table_Grid`
  - `distance = 85.0 mm`
  - `common volume = 0.0 mm^3`
- `Lower_Cutter_Head vs Cable_Track_V`
  - `distance = 25.0 mm`
  - `common volume = 0.0 mm^3`

## Heater standoff modeling status

The current heater rod is not parameterized with a vertical standoff axis.

FreeCAD expression snapshot:

- `Heater_Rod.ExpressionEngine = [('.Placement.Base.x', '200 mm + Variables.B1')]`

This means the present model only tracks heater motion along the synchronized travel direction and does not encode the requested `15-20 mm` or nominal `18 mm` gap to glass.

## Sensor modeling status

Objects found with sensor-like naming:

- `Vacuum_Pressure_Sensor`

Not present in the current FCStd sampling:

- `Leuze`
- `inductive`
- `limit switch`

So limit-trigger timing for Leuze IS 218 style sensors is not yet verifiable from the current model alone.

## Conclusion

What is validated:

- upper/lower head synchronized travel is modeled consistently

What is not yet mechanically trustworthy:

- lower head, heater rod, and pressure roller currently intersect the table geometry
- heater-to-glass standoff is not parameterized
- cable chain bend radius is not modeled as an articulated chain
- Leuze limit sensors are not represented in the sampled FCStd model

## Recommended next step

To make this simulation suitable for engineering sign-off, implement:

- a dedicated heater standoff parameter, nominal `18 mm`
- non-intersecting lower-head / table geometry offsets
- explicit Leuze sensor bodies and trigger positions
- articulated drag-chain envelope or minimum bend-radius proxy checks

## 2026-04-17 Geometry update

The FCStd source model and the saved FreeCAD document were updated to reflect the real lamine workflow more closely.

### Mechanical updates applied

- `Glass_Sheet_Reference` was moved onto the actual table top plane
- `Lower_Cutter_Head` was re-bound to an under-table travel corridor using the vertical `Y` axis
- `Lower_Cutting_Wheel` was re-bound to the glass underside with nominal `R1 = 5 mm` clearance
- `Heater_Rod` was moved below the glass and now uses nominal `Q1 = 18 mm` standoff to the glass underside
- `Pressure_Roller` was moved above the glass and now uses nominal `S1 = 2 mm` standoff to the glass top surface

### NC300 control note

For the real machine sequence, the following controls should be treated as mandatory in the NC layer:

- `E-Cam`: upper head master axis and lower cutter follower axis must stay on the same sampled X line through the lamine cut
- `Heating timing`: SIR heater segments should be switched through `R1-EC0902O` digital outputs, preferably as phase-based outputs in the lamine process state machine

### Suggested output grouping for heater control

Assumed grouping for implementation review:

- `R1-EC0902O #4`: heater enable / zone 1
- `R1-EC0902O #5`: heater zone 2 / auxiliary pneumatic outputs
- `R1-EC0902O #6`: heater safety interlocks / alarm relays

This grouping is an engineering assumption for the CAD/simulation layer and should be finalized against the electrical I/O list before commissioning.
