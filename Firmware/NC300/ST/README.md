# NC300 ST Kaynaklari

Bu klasor, `30RE-S Hibrit Sistem` icin hazirlanan Structured Text referanslarini icerir.

Dosyalar:
- `Lamine_ClearPath_Main.st`
  - G31 ile cam kenari bulma
  - cami kesim X koordinatina surme ve X kilitleme
  - sadece Y ekseninde E-Cam senkron kesim
  - kesim biter bitmez 4 saniyelik M12 isitma
  - X ekseni ile +2.0 mm folyo germe stroku
  - M13 ile ayirma/kirma tetigi

FreeCAD parametre eslesmesi:
- `Variables.X1` -> `#2001` lamine mode enable
- `Variables.Y1` -> `#2007` cut X target / X lock position
- `Variables.Z1` -> `#2010` park retract
- `Variables.Q1` -> `#2009` heater working offset
- `Variables.T1` -> runtime bridge correction
- `Variables.U1` -> `#2004` probe backoff
- `Variables.V1` -> `#2005` tension stroke
- `Variables.AD1` -> `is_clamped` / vakum kavrama teyidi

I/O onerisi:
- `%QX0.0` -> SIR heater relay (`M12`)
- `%QX0.1` -> vacuum valve (`M10`)
- `%QX0.2` -> X axis lock (`M11`)
- `%QX0.3` -> break start (`M13`)
- `%QX0.4` -> E-Cam active relay
- `%IX0.0` -> G31 probe input
- `%IX0.1` -> Safe_To_Move_X (alt kafa park sensoru)

Not:
- `#2000-#2010` alanlari `%MW2000-%MW2010` uzerinden orneklenmistir.
- Gercek ISPSoft projede motion FB isimleri, register tipi ve scaling son kez kontrol edilmelidir.
