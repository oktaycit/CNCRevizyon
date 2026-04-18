%
O3000 (30RE-S LAMINE CLEAR PATH)
(Delta NC300 reference macro aligned with FreeCAD clear-path model)

(#2000 E-CAM ENABLE)
(#2001 LAMINE MODE ENABLE)
(#2002 X LOCK ENABLE)
(#2003 HEATER DWELL MS)
(#2004 PROBE SEARCH MM)
(#2005 TENSION OFFSET MM)
(#2007 CUT X TARGET MM)
(#2008 CUT Y TARGET MM)
(#2010 PARK RETRACT MM)

#2000 = 0
#2001 = 0
#2002 = 0
#2003 = 4000
#2004 = 100
#2005 = 2
#2007 = 500
#2008 = 2300
#2010 = 50

; --- ADIM A: CAMI YAKALA VE ORIJINLE ---
M10                 ; vacuum on -> QX0.1
G31 X-100 F500      ; glass edge probe search
G92 X0              ; accept the detected edge as X0

; --- ADIM B: KESIM HATTINA KONUMLANDIR ---
G01 X[#2007] F1500  ; move glass onto the cut line
M11                 ; X axis software brake / lock -> QX0.2
#2001 = 1           ; lamine mode active
#2002 = 1

; --- ADIM C: SENKRONIZE Y KESIMI ---
#2000 = 1           ; upper head = master, lower unit = EtherCAT follower
G01 Y[#2008] F5000  ; X remains fixed on the cut line
#2000 = 0

; --- ADIM D: ISITMA VE FOLYO GERME ---
M12                 ; heater relay -> QX0.0
G04 P[#2003]        ; 4 s heater dwell
#2002 = 0           ; release X lock before tension stroke
G01 X[#2007 + #2005] F200

; --- AYIRMA / KIRMA ---
M13                 ; break-start output -> QX0.3

M30
%
