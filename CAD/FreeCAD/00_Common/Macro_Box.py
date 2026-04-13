# -*- coding: utf-8 -*-
"""
FreeCAD Makro - Parametrik Kutu Oluşturma
CNC Revizyon Projesi için

Kullanım:
    exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/00_Common/Macro_Box.py").read())
    create_parametric_box(100, 50, 30)
"""

import FreeCAD as App
import Part


def create_parametric_box(length=100, width=50, height=30, name="ParametricBox"):
    """
    Parametrik kutu oluştur

    Args:
        length: Uzunluk (mm)
        width: Genişlik (mm)
        height: Yükseklik (mm)
        name: Obje adı
    """
    # Yeni document oluştur
    doc = App.newDocument("Box_Part")

    # Kutu oluştur
    box = Part.makeBox(length, width, height)

    # Shape objesi ekle
    shape_obj = doc.addObject("Part::Feature", name)
    shape_obj.Shape = box

    # Görünüm rengini ayarla
    shape_obj.ViewObject.ShapeColor = (0.5, 0.7, 1.0)

    # Document'i yeniden hesapla
    doc.recompute()

    print(f"✅ Kutu oluşturuldu: {name}")
    print(f"   Boyutlar: {length} x {width} x {height} mm")
    print(f"   Volume: {box.Volume:.2f} mm³")

    return doc, shape_obj


def create_box_with_holes(length=100, width=50, height=30, hole_radius=5, hole_positions=None):
    """
    Delikli kutu oluştur

    Args:
        length: Uzunluk (mm)
        width: Genişlik (mm)
        height: Yükseklik (mm)
        hole_radius: Delik yarıçapı (mm)
        hole_positions: Delik pozisyonları [(x,y,z), ...]
    """
    doc = App.newDocument("Box_With_Holes")

    # Ana kutu
    box = Part.makeBox(length, width, height)

    # Delikleri oluştur
    if hole_positions is None:
        # Varsayılan olarak köşelere delikler
        hole_positions = [
            (10, 10, height),
            (length - 10, 10, height),
            (10, width - 10, height),
            (length - 10, width - 10, height),
        ]

    for x, y, z in hole_positions:
        cylinder = Part.makeCylinder(hole_radius, height + 10)
        cylinder.translate(App.Vector(x, y, -5))
        box = box.cut(cylinder)

    # Shape objesi ekle
    shape_obj = doc.addObject("Part::Feature", "Box_With_Holes")
    shape_obj.Shape = box

    doc.recompute()

    print(f"✅ Delikli kutu oluşturuldu")
    print(f"   Delik sayısı: {len(hole_positions)}")

    return doc, shape_obj


# Hızlı test
if __name__ == "__main__":
    create_parametric_box(100, 50, 30)
