# Ana Pano FreeCAD Hazirlik Notu

Bu dokuman, pano imalatina gidecek ana pano mekanik FreeCAD paketinin kapsamini tarif eder.

## Referanslar

- `Electrical/Panel_Manufacturer/01_PANEL_LAYOUT.md`
- `Electrical/Panel_Manufacturer/02_TERMINAL_DIAGRAMS.md`
- `Electrical/Panel_Manufacturer/04_ASSEMBLY_NOTES.md`

## Hedef Geometri

- Dis olculer: `1200 x 2000 x 600 mm`
- Montaj plakasi: `1000 x 1800 mm`
- Tip: ayakli, on acilir, IP65 endustriyel pano

## Hazirlanan FreeCAD Kaynagi

- `Main_Panel_Generator.py`

Bu script su parcalari uretecek sekilde yazilmistir:

- `Main_Panel_Body`
- `Main_Panel_Door`
- `Main_Panel_Mounting_Plate`

## Not

Mevcut oturumda FreeCAD runtime islemci uyumsuzlugu nedeniyle script calistirilip yeni `FCStd/STEP` export alinamamistir. Buna ragmen panocuya gonderilecek teslim paketine:

- kaynak FreeCAD scripti
- panel yerlesim ve montaj dokumanlari
- operator terminal icin mevcut STEP dosyalari

dahil edilmistir.
