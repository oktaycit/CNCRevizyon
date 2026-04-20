%
O3000 (30RE-S LAMINE CLEAR PATH)
(Delta NC300 reference macro aligned with FreeCAD clear-path model)

REVIZYON NOTU:
- VB ünitesi mekanik bağlı - E-Cam gereksiz
- Kartezyen köprü (beyaz): X,Y,Z eksenleri, vakum+lama silme servisi
- VB ünitesi (lila): Dar ünite, sadece Y yönünde çalışır
- VB ünitesinde alt kafa servo, üst kafaya mekanik bağlı
- Lamine kesimde kartezyen köprünün Y ekseni kullanılmaz

PARAMETRELER:
#2000 REZERV - E-Cam gereksiz (VB mekanik bağlı)
#2001 LAMINE MODE ENABLE
#2002 X LOCK ENABLE
#2003 HEATER DWELL MS
#2004 PROBE SEARCH MM
#2005 TENSION OFFSET MM
#2007 CUT X TARGET MM
#2008 CUT Y TARGET MM
#2010 PARK RETRACT MM

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

; --- ADIM C: SIMETRIK SCORING (VB-Y) ---
#2000 = 1           ; VB_Y_LINK_ENABLE
G00 Y0 F5000        ; VB Y başlangıç tarafı
M03 S1000           ; üst + alt scoring aktif
G01 Y[#2008] F5000  ; VB ünitesi Y eksenini doğrudan sür (X sabit)
M05                 ; scoring pasif

; --- ADIM D: CAM KIRMA ---
M16                 ; pressure roller ON
M13                 ; breaking bar ON
G04 P1.0            ; çatlatma bekleme
M20                 ; breaking bar OFF
M17                 ; pressure roller OFF

; --- ADIM E: PVB ISITMA ---
M12                 ; heater relay -> QX0.0
G04 P[#2003]        ; 4 s heater dwell
M22                 ; heater OFF

; --- ADIM F: GAP ACMA ---
#2002 = 0           ; release X lock before tension stroke
M18                 ; tension retract ON
G01 X[#2007 + #2005] F200
M19                 ; tension retract OFF

; --- ADIM G: FOLYO KESME VE AYIRMA ---
M14                 ; separating blade ON
G04 P1.0            ; blade dwell
M15                 ; separating blade OFF
#2000 = 0           ; VB_Y_LINK_ENABLE off
#2001 = 0           ; lamine mode off

M30
%
