# -*- coding: utf-8 -*-
"""
FreeCAD Makro - Assembly4 Montaj İşlemleri
CNC Revizyon Projesi için

Assembly4 Workbench gerektirir:
    https://github.com/Zolko-123/FreeCAD_Assembly4

Kullanım:
    exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/06_Assembly/Macro_Assembly4.py").read())
    create_assembly4_structure()
"""

import FreeCAD as App
import Part
import os


def create_lcs(parent_doc, parent_obj, name="LCS_0", position=(0, 0, 0), rotation=(0, 0, 0)):
    """
    Local Coordinate System (LCS) oluştur

    Args:
        parent_doc: Document
        parent_obj: Ebeveyn obje
        name: LCS adı
        position: Pozisyon (x, y, z)
        rotation: Rotasyon (rx, ry, rz) derece
    """
    lcs = parent_doc.addObject("PartDesign::CoordinateSystem", name)
    lcs.Label = name

    # Pozisyon ve rotasyon ayarla
    lcs.Placement = App.Placement(
        App.Vector(position[0], position[1], position[2]),
        App.Rotation(
            App.Vector(1, 0, 0), rotation[0],
            App.Vector(0, 1, 0), rotation[1],
            App.Vector(0, 0, 1), rotation[2]
        )
    )

    return lcs


def create_assembly4_structure(assembly_name="CNC_Assembly"):
    """
    Assembly4 montaj yapısı oluştur
    """
    # Yeni assembly document
    doc = App.newDocument(assembly_name)

    # Ana LCS oluştur
    main_lcs = doc.addObject("PartDesign::CoordinateSystem", "LCS_0")
    main_lcs.Label = "Ana Referans"

    # X ekseni montajı
    x_axis_lcs = doc.addObject("PartDesign::CoordinateSystem", "LCS_X_Axis")
    x_axis_lcs.Label = "X Ekseni"
    x_axis_lcs.Placement = App.Placement(
        App.Vector(0, 0, 0),
        App.Rotation(0, 0, 0)
    )

    # Y ekseni montajı
    y_axis_lcs = doc.addObject("PartDesign::CoordinateSystem", "LCS_Y_Axis")
    y_axis_lcs.Label = "Y Ekseni"
    y_axis_lcs.Placement = App.Placement(
        App.Vector(3000, 0, 0),
        App.Rotation(0, 0, 0)
    )

    # Z ekseni montajı
    z_axis_lcs = doc.addObject("PartDesign::CoordinateSystem", "LCS_Z_Axis")
    z_axis_lcs.Label = "Z Ekseni"
    z_axis_lcs.Placement = App.Placement(
        App.Vector(0, 1500, 500),
        App.Rotation(0, 0, 0)
    )

    # Kesim kafası LCS
    cutting_head_lcs = doc.addObject("PartDesign::CoordinateSystem", "LCS_Cutting_Head")
    cutting_head_lcs.Label = "Kesim Kafası"
    cutting_head_lcs.Placement = App.Placement(
        App.Vector(1500, 750, 200),
        App.Rotation(0, 0, 0)
    )

    doc.recompute()

    print(f"✅ Assembly4 yapısı oluşturuldu: {assembly_name}")
    print(f"   LCS sayısı: {len([o for o in doc.Objects if 'CoordinateSystem' in o.TypeId])}")

    return doc


def add_part_to_assembly(
    assembly_doc,
    part_file,
    part_name,
    lcs_name="LCS_0",
    position=(0, 0, 0)
):
    """
    Assembly'ye parça ekle

    Args:
        assembly_doc: Assembly document
        part_file: Parça dosya yolu (.FCStd)
        part_name: Parça adı
        lcs_name: Bağlanacak LCS adı
        position: Pozisyon ofseti
    """
    # Parçayı yükle
    part_doc = App.open(part_file)
    part_obj = part_doc.Objects[0]

    # Link oluştur
    link = assembly_doc.addObject("App::Link", part_name)
    link.Label = part_name
    link.setLink(part_obj)

    # LCS'e bağla
    if lcs_name in assembly_doc.Objects:
        lcs = assembly_doc.getObject(lcs_name)
        link.Placement = lcs.Placement

    assembly_doc.recompute()

    print(f"✅ Parça eklendi: {part_name}")

    return link


def create_motor_assembly(motor_type="ECMA-L11845", position=(0, 0, 0)):
    """
    Motor montajı oluştur

    Args:
        motor_type: Motor tipi
        position: Montaj pozisyonu
    """
    doc = App.newDocument(f"Motor_{motor_type}")

    # Motor gövdesi (basit silindir)
    motor_radius = 55  # ECMA-L11845 için yaklaşık
    motor_height = 150

    motor_body = Part.makeCylinder(motor_radius, motor_height)
    motor_obj = doc.addObject("Part::Feature", f"Motor_{motor_type}")
    motor_obj.Shape = motor_body
    motor_obj.ViewObject.ShapeColor = (0.2, 0.2, 0.8)

    # Mil
    shaft_radius = 19  # Motor mili
    shaft_height = 50

    shaft = Part.makeCylinder(shaft_radius, shaft_height)
    shaft.translate(App.Vector(0, 0, motor_height))
    shaft_obj = doc.addObject("Part::Feature", "Motor_Shaft")
    shaft_obj.Shape = shaft
    shaft_obj.ViewObject.ShapeColor = (0.8, 0.8, 0.8)

    # Montaj delikleri
    bolt_circle_radius = 70
    bolt_count = 4
    bolt_radius = 5

    for i in range(bolt_count):
        angle = (2 * 3.14159 * i) / bolt_count
        x = bolt_circle_radius * App.cos(angle)
        y = bolt_circle_radius * App.sin(angle)

        hole = Part.makeCylinder(bolt_radius, motor_height + 10)
        hole.translate(App.Vector(x, y, -5))
        motor_body = motor_body.cut(hole)

    doc.recompute()

    print(f"✅ Motor montajı oluşturuldu: {motor_type}")
    print(f"   Pozisyon: {position}")

    return doc


def create_linear_guide_assembly(length=3000, width=50, height=30):
    """
    Lineer kılavuz montajı oluştur

    Args:
        length: Uzunluk (mm)
        width: Genişlik (mm)
        height: Yükseklik (mm)
    """
    doc = App.newDocument("Linear_Guide")

    # Ray
    rail = Part.makeBox(length, width, height)
    rail_obj = doc.addObject("Part::Feature", "Guide_Rail")
    rail_obj.Shape = rail
    rail_obj.ViewObject.ShapeColor = (0.7, 0.7, 0.7)

    # Araba (carriage)
    carriage_length = 100
    carriage = Part.makeBox(carriage_length, width + 10, height + 20)
    carriage.translate(App.Vector(length / 2 - carriage_length / 2, -5, 0))
    carriage_obj = doc.addObject("Part::Feature", "Guide_Carriage")
    carriage_obj.Shape = carriage
    carriage_obj.ViewObject.ShapeColor = (0.5, 0.5, 0.5)

    doc.recompute()

    print(f"✅ Lineer kılavuz oluşturuldu: {length}mm")

    return doc


# Hızlı test
if __name__ == "__main__":
    # Assembly4 yapısı oluştur
    doc = create_assembly4_structure("Test_Assembly")

    # Motor montajı oluştur
    motor_doc = create_motor_assembly("ECMA-L11845")
