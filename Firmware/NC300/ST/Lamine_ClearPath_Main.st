(*
    Delta NC300 - 30RE-S Lamine Clear Path Reference
    REVIZYON: VB ünitesi mekanik bağlı - E-Cam gereksiz

    Sistem Yapisi:
    - Kartezyen köprü (beyaz): X,Y,Z eksenleri, vakum+lama silme servisi
    - VB ünitesi (lila): Dar ünite, sadece Y yönünde çalışır, X yönünde hareket edemez
    - VB ünitesinde alt kafa servo, üst kafaya mekanik bağlı
    - Lamine kesimde kartezyen köprünün Y ekseni kullanılmaz
    - VB Y ekseni doğrudan Y hareketi ile kesim yapar (E-Cam gereksiz)

    Sira:
    1. M10 ile cami kavra
    2. G31 ile kenari bul, G92 X0 kabul et
    3. X=500 mm kesim hattina sur
    4. M11 ile X eksenini kilitle
    5. VB-Y ile simetrik scoring yap
    6. Kırma barı + pressure roller ile iki camı çatlat
    7. SIR isitici ile PVB folyoyu yumusat
    8. X ekseni +2.0 mm gap açma stroku uygulasin
    9. Folyo kesme bicagi ile ayirmayi tamamla

    Kritik interlock:
    - %IX0.0 -> G31 cam kenari sensoru
    - %IX0.1 -> Safe_To_Move_X (alt kafa parkta)
    - VacuumPressureSensor -> FreeCAD Variables.AD1 / is_clamped ile hizalanan clamp teyidi
*)

TYPE E_LamineStep :
(
    STEP_IDLE := 0,
    STEP_VACUUM_PICK := 10,
    STEP_G31_SEARCH := 20,
    STEP_G31_SET_ZERO := 30,
    STEP_MOVE_TO_CUT_X := 40,
    STEP_X_LOCK := 50,
    STEP_SYNC_CUT := 60,
    STEP_BREAK_CRACK := 70,
    STEP_HEATER_DWELL := 80,
    STEP_TENSION_STROKE := 90,
    STEP_SEPARATE_BLADE := 100,
    STEP_COMPLETE := 110,
    STEP_FAULT := 900
);
END_TYPE


PROGRAM PRG_LamineClearPath
VAR
    Step : E_LamineStep := STEP_IDLE;
    StepInit : BOOL := FALSE;
    AlarmActive : BOOL := FALSE;

    AxisX : MC_Axis_Ref;
    AxisY : MC_Axis_Ref;

    MoveAbsX : MC_MoveAbsolute;
    MoveAbsY : MC_MoveAbsolute;
    MoveRelX : MC_MoveRelative;
    HaltX : MC_Halt;

    HeatTimer : TON;
    LockTimer : TON;
    BreakTimer : TON;
    BladeTimer : TON;

    XActualPos : REAL := 0.0;
    StartCmd : BOOL := FALSE;
    CycleDone : BOOL := FALSE;

    EdgeProbeLatched : BOOL := FALSE;
    XZeroSetDone : BOOL := FALSE;
    SyncCutDone : BOOL := FALSE;
    BreakDone : BOOL := FALSE;
    TensionDone : BOOL := FALSE;
    SeparateDone : BOOL := FALSE;
END_VAR

VAR RETAIN
    User2000_ECamEnable AT %MW2000 : INT := 0;       (* REZERV - VB mekanik bağlı, E-Cam gereksiz *)
    User2001_LamineModeEnable AT %MW2001 : INT := 0; (* VB ünitesi aktif *)
    User2002_XLockEnable AT %MW2002 : INT := 0;      (* X ekseni kilitli *)
    User2003_HeaterDwellMs AT %MW2003 : INT := 4000;
    User2004_ProbeSearchMm AT %MW2004 : INT := 100;
    User2005_TensionStrokeMm AT %MW2005 : INT := 2;
    User2007_CutXTargetMm AT %MW2007 : INT := 500;
    User2008_CutYTargetMm AT %MW2008 : INT := 2300;
    User2010_ParkRetractMm AT %MW2010 : INT := 50;
END_VAR

VAR
    G31ProbeInput AT %IX0.0 : BOOL;
    Safe_To_Move_X AT %IX0.1 : BOOL;
    VacuumPressureSensor AT %IX0.2 : BOOL;
    XLockOK AT %IX0.3 : BOOL;
    LeuzeXPosLimit AT %IX0.4 : BOOL;
    LeuzeXNegLimit AT %IX0.5 : BOOL;
    LeuzeYPosLimit AT %IX0.6 : BOOL;
    LeuzeYNegLimit AT %IX0.7 : BOOL;
    HeaterReady AT %IX1.0 : BOOL;
    BreakOK AT %IX1.1 : BOOL;
    SafetyOK AT %IX1.2 : BOOL;

    M12_Heater_ON AT %QX0.0 : BOOL;
    M10_Vacuum_ON AT %QX0.1 : BOOL;
    M11_XAxisLock AT %QX0.2 : BOOL;
    M13_BreakStart AT %QX0.3 : BOOL;
    DO_ECamActive AT %QX0.4 : BOOL;
    DO_LamineMode AT %QX0.5 : BOOL;
    DO_ProbeEnable AT %QX0.6 : BOOL;
    DO_TensionEnable AT %QX0.7 : BOOL;
    M14_SeparationBlade_ON AT %QX1.0 : BOOL;
    M16_PressureRoller_ON AT %QX1.1 : BOOL;
END_VAR


M12_Heater_ON := FALSE;
M10_Vacuum_ON := FALSE;
M11_XAxisLock := FALSE;
M13_BreakStart := FALSE;
DO_ECamActive := FALSE;
DO_LamineMode := FALSE;
DO_ProbeEnable := FALSE;
DO_TensionEnable := FALSE;
M14_SeparationBlade_ON := FALSE;
M16_PressureRoller_ON := FALSE;
CycleDone := FALSE;

HeatTimer(IN := FALSE, PT := INT_TO_TIME(User2003_HeaterDwellMs));
LockTimer(IN := FALSE, PT := T#100MS);
BreakTimer(IN := FALSE, PT := T#1S);
BladeTimer(IN := FALSE, PT := T#1S);

IF (NOT SafetyOK) OR LeuzeXPosLimit OR LeuzeXNegLimit OR LeuzeYPosLimit OR LeuzeYNegLimit THEN
    AlarmActive := TRUE;
    Step := STEP_FAULT;
END_IF;

CASE Step OF
    STEP_IDLE:
        StepInit := FALSE;
        AlarmActive := FALSE;
        EdgeProbeLatched := FALSE;
        XZeroSetDone := FALSE;
        SyncCutDone := FALSE;
        BreakDone := FALSE;
        TensionDone := FALSE;
        SeparateDone := FALSE;

        User2000_ECamEnable := 0;
        User2001_LamineModeEnable := 0;
        User2002_XLockEnable := 0;

        IF StartCmd THEN
            Step := STEP_VACUUM_PICK;
        END_IF;

    STEP_VACUUM_PICK:
        M10_Vacuum_ON := TRUE;              (* M10 *)
        User2001_LamineModeEnable := 0;     (* Alt kafa parkta kalmali *)

        IF VacuumPressureSensor AND Safe_To_Move_X THEN
            Step := STEP_G31_SEARCH;
            StepInit := FALSE;
        END_IF;

    STEP_G31_SEARCH:
        M10_Vacuum_ON := TRUE;
        DO_ProbeEnable := TRUE;

        IF NOT Safe_To_Move_X THEN
            Step := STEP_FAULT;
            AlarmActive := TRUE;
        ELSIF NOT StepInit THEN
            StepInit := TRUE;
            MoveRelX(
                Axis := AxisX,
                Execute := TRUE,
                Distance := -INT_TO_REAL(User2004_ProbeSearchMm),
                Velocity := 500.0,
                Acceleration := 1200.0,
                Deceleration := 1200.0
            );
        END_IF;

        IF G31ProbeInput THEN
            EdgeProbeLatched := TRUE;
            HaltX(Axis := AxisX, Execute := TRUE, Deceleration := 1200.0);
            Step := STEP_G31_SET_ZERO;
            StepInit := FALSE;
        END_IF;

    STEP_G31_SET_ZERO:
        M10_Vacuum_ON := TRUE;
        DO_ProbeEnable := TRUE;

        IF EdgeProbeLatched THEN
            (* G92 X0 equivalent *)
            XActualPos := 0.0;
            XZeroSetDone := TRUE;
            Step := STEP_MOVE_TO_CUT_X;
            StepInit := FALSE;
        END_IF;

    STEP_MOVE_TO_CUT_X:
        M10_Vacuum_ON := TRUE;

        IF NOT Safe_To_Move_X THEN
            Step := STEP_FAULT;
            AlarmActive := TRUE;
        ELSIF NOT StepInit THEN
            StepInit := TRUE;
            MoveAbsX(
                Axis := AxisX,
                Execute := TRUE,
                Position := INT_TO_REAL(User2007_CutXTargetMm),
                Velocity := 1500.0,
                Acceleration := 2000.0,
                Deceleration := 2000.0
            );
        END_IF;

        IF MoveAbsX.Done THEN
            Step := STEP_X_LOCK;
            StepInit := FALSE;
        END_IF;

    STEP_X_LOCK:
        M10_Vacuum_ON := TRUE;
        M11_XAxisLock := TRUE;              (* M11 *)
        DO_LamineMode := TRUE;
        User2001_LamineModeEnable := 1;
        User2002_XLockEnable := 1;

        LockTimer(IN := TRUE, PT := T#100MS);
        IF XLockOK OR LockTimer.Q THEN
            Step := STEP_SYNC_CUT;
            StepInit := FALSE;
        END_IF;

    STEP_SYNC_CUT:
        (* 
           VB ÜNITESI MEKANIK BAĞLI - E-CAM GEREKSIZ
           Alt kafa servo, üst kafaya mekanik bağlı
           Y ekseni hareketi ile doğrudan kesim yapar
        *)
        M10_Vacuum_ON := TRUE;
        M11_XAxisLock := TRUE;
        DO_LamineMode := TRUE;
        User2001_LamineModeEnable := 1;
        User2002_XLockEnable := 1;

        (* E-Cam gereksiz, doğrudan Y hareketi yeterli *)
        User2000_ECamEnable := 0;  (* REZERV *)
        DO_ECamActive := FALSE;

        IF NOT StepInit THEN
            StepInit := TRUE;
            (* VB ünitesi Y eksenini doğrudan sür - mekanik bağlı *)
            MoveAbsY(
                Axis := AxisY,
                Execute := TRUE,
                Position := INT_TO_REAL(User2008_CutYTargetMm),
                Velocity := 5000.0,
                Acceleration := 6000.0,
                Deceleration := 6000.0
            );
        END_IF;

        IF MoveAbsY.Done THEN
            SyncCutDone := TRUE;
            Step := STEP_BREAK_CRACK;
            StepInit := FALSE;
        END_IF;

    STEP_BREAK_CRACK:
        M10_Vacuum_ON := TRUE;
        DO_LamineMode := TRUE;
        M11_XAxisLock := TRUE;
        M16_PressureRoller_ON := TRUE;      (* M16 *)
        M13_BreakStart := TRUE;             (* M13 *)

        BreakTimer(IN := TRUE, PT := T#1S);
        IF BreakOK OR BreakTimer.Q THEN
            BreakDone := TRUE;
            Step := STEP_HEATER_DWELL;
            StepInit := FALSE;
        END_IF;

    STEP_HEATER_DWELL:
        M10_Vacuum_ON := TRUE;
        DO_LamineMode := TRUE;
        M11_XAxisLock := TRUE;
        M12_Heater_ON := TRUE;              (* Heater_ON / QX0.0 *)

        HeatTimer(IN := TRUE, PT := INT_TO_TIME(User2003_HeaterDwellMs));
        IF HeatTimer.Q THEN
            Step := STEP_TENSION_STROKE;
            StepInit := FALSE;
        END_IF;

    STEP_TENSION_STROKE:
        M10_Vacuum_ON := TRUE;
        DO_LamineMode := TRUE;
        DO_TensionEnable := TRUE;
        User2002_XLockEnable := 0;          (* Gap acmadan once X kilidi serbest *)

        IF NOT StepInit THEN
            StepInit := TRUE;
            MoveAbsX(
                Axis := AxisX,
                Execute := TRUE,
                Position := INT_TO_REAL(User2007_CutXTargetMm + User2005_TensionStrokeMm),
                Velocity := 200.0,
                Acceleration := 500.0,
                Deceleration := 500.0
            );
        END_IF;

        IF MoveAbsX.Done THEN
            TensionDone := TRUE;
            Step := STEP_SEPARATE_BLADE;
            StepInit := FALSE;
        END_IF;

    STEP_SEPARATE_BLADE:
        M10_Vacuum_ON := TRUE;
        DO_LamineMode := TRUE;
        M14_SeparationBlade_ON := TRUE;     (* M14 *)

        BladeTimer(IN := TRUE, PT := T#1S);
        IF BladeTimer.Q THEN
            SeparateDone := TRUE;
            Step := STEP_COMPLETE;
            StepInit := FALSE;
        END_IF;

    STEP_COMPLETE:
        CycleDone := TRUE;
        User2000_ECamEnable := 0;
        User2001_LamineModeEnable := 0;
        User2002_XLockEnable := 0;

    STEP_FAULT:
        AlarmActive := TRUE;
        User2000_ECamEnable := 0;
        User2001_LamineModeEnable := 0;
        User2002_XLockEnable := 0;

ELSE
    Step := STEP_FAULT;
END_CASE;
