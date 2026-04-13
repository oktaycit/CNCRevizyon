# -*- coding: utf-8 -*-
"""
FreeCAD Makro - Parametrik Silindir Oluşturma
CNC Revizyon Projesi için

Kullanım:
    exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/00_Common/Macro_Cylinder.py").read())
    create_parametric_cylinder(25, 100)
"""

import FreeCAD as App
import Part
import math


def create_parametric_cylinder(radius=25, height=100, name="ParametricCylinder"):
    """
    Parametrik silindir oluştur

    Args:
        radius: Yarıçap (mm)
        height: Yükseklik (mm)
        name: Obje adı
    """
    doc = App.newDocument("Cylinder_Part")

    # Silindir oluştur
    cylinder = Part.makeCylinder(radius, height)

    # Shape objesi ekle
    shape_obj = doc.addObject("Part::Feature", name)
    shape_obj.Shape = cylinder

    shape_obj.ViewObject.ShapeColor = (1.0, 0.7, 0.5)

    doc.recompute()

    print(f"✅ Silindir oluşturuldu: {name}")
    print(f"   Radius: {radius} mm, Height: {height} mm")
    print(f"   Volume: {cylinder.Volume:.2f} mm³")

    return doc, shape_obj


def create_gear_cylinder(
    outer_radius=30,
    inner_radius=20,
    height=10,
    teeth_count=12,
    name="Gear_Cylinder"
):
    """
    Dişli silindir oluştur

    Args:
        outer_radius: Dış yarıçap (mm)
        inner_radius: İç yarıçap (mm)
        height: Yükseklik (mm)
        teeth_count: Diş sayısı
        name: Obje adı
    """
    doc = App.newDocument("Gear_Cylinder")

    # Ana silindir
    base_cylinder = Part.makeCylinder(outer_radius, height)

    # Dişleri oluştur
    for i in range(teeth_count):
        angle = (2 * math.pi * i) / teeth_count
        tooth_x = (outer_radius - 5) * math.cos(angle)
        tooth_y = (outer_radius - 5) * math.sin(angle)

        # Diş (küçük kutu)
        tooth = Part.makeBox(10, 8, height)
        tooth.translate(App.Vector(tooth_x - 5, tooth_y - 4, 0))
        base_cylinder = base_cylinder.fuse(tooth)

    # İç delik
    if inner_radius > 0:
        hole = Part.makeCylinder(inner_radius, height + 1)
        hole.translate(App.Vector(0, 0, -0.5))
        base_cylinder = base_cylinder.cut(hole)

    shape_obj = doc.addObject("Part::Feature", name)
    shape_obj.Shape = base_cylinder
    shape_obj.ViewObject.ShapeColor = (0.8, 0.8, 0.2)

    doc.recompute()

    print(f"✅ Dişli silindir oluşturuldu")
    print(f"   Diş sayısı: {teeth_count}")
    print(f"   Dış yarıçap: {outer_radius} mm")

    return doc, shape_obj


def create_flanged_cylinder(
    radius=20,
    shaft_height=50,
    flange_height=5,
    flange_radius=35,
    name="Flanged_Cylinder"
):
    """
    Flanşlı silindir oluştur

    Args:
        radius: Mil yarıçapı (mm)
        shaft_height: Mil yüksekliği (mm)
        flange_height: Flanş yüksekliği (mm)
        flange_radius: Flanş yarıçapı (mm)
        name: Obje adı
    """
    doc = App.newDocument("Flanged_Cylinder")

    # Mil
    shaft = Part.makeCylinder(radius, shaft_height)

    # Flanş
    flange = Part.makeCylinder(flange_radius, flange_height)
    flange.translate(App.Vector(0, 0, -flange_height))

    # Birleştir
    combined = shaft.fuse(flange)

    # Merkez delik
    hole = Part.makeCylinder(radius - 2, shaft_height + flange_height + 1)
    hole.translate(App.Vector(0, 0, -flange_height - 0.5))
    combined = combined.cut(hole)

    shape_obj = doc.addObject("Part::Feature", name)
    shape_obj.Shape = combined
    shape_obj.ViewObject.ShapeColor = (0.6, 0.6, 0.6)

    doc.recompute()

    print(f"✅ Flanşlı silindir oluşturuldu")
    print(f"   Flanş çapı: Ø{flange_radius * 2} mm")

    return doc, shape_obj


# Hızlı test
if __name__ == "__main__":
    create_parametric_cylinder(25, 100)
