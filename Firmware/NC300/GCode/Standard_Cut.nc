%
O1000 (CAM KESME PROGRAMI)
(Material: 6000x3000x10mm)
(Tool: Diamond Wheel D25mm)

(Tum eksenleri referansa gonder)
G28 X0 Y0 Z0

(Hizli hareket baslangic pozisyonuna)
G21 G90 G94
G00 X100 Y200

(Z ekseni asagi - kesim pozisyonu)
G01 Z-5 F500

(Kesim baslat)
M03

(Ilk kesim - X ekseni)
G01 X5900 F2000

(Z ekseni yukari)
G00 Z50
M05

(Hizli geri donus)
G00 Y400

(Tekrar asagi)
G01 Z-5 F500
M03

(Ikinci kesim - geri yon)
G01 X100 F2000

G00 Z50
M05

(Program sonu)
G28 X0 Y0
M30
%
