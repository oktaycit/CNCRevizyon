# FreeCAD Main Panel Generator
# CNC Revizyon Projesi - GFB-60/30RE
# Ana pano mekanik govde ve montaj plakasi taslagi

import FreeCAD as App
import Part
import os

try:
    BASE_DIR = os.path.dirname(__file__)
except NameError:
    BASE_DIR = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/05_Electronics"

EXPORT_DIR = os.path.join(BASE_DIR, "..", "07_Exports", "STEP", "Electronics")
os.makedirs(EXPORT_DIR, exist_ok=True)


def make_box(width, height, depth, position=(0, 0, 0)):
    return Part.makeBox(width, height, depth, App.Vector(position))


def make_hollow_box(outer_w, outer_h, outer_d, wall_thickness, position=(0, 0, 0)):
    outer = make_box(outer_w, outer_h, outer_d, position)
    inner = make_box(
        outer_w - 2 * wall_thickness,
        outer_h - 2 * wall_thickness,
        outer_d - wall_thickness,
        (
            position[0] + wall_thickness,
            position[1] + wall_thickness,
            position[2] + wall_thickness,
        ),
    )
    return outer.cut(inner)


def make_cylinder(radius, height, position=(0, 0, 0), direction=(0, 0, 1)):
    return Part.makeCylinder(radius, height, App.Vector(position), App.Vector(direction))


def create_main_panel_body(doc, name="Main_Panel_Body"):
    """
    Ana pano govdesi
    Referans: Electrical/Panel_Manufacturer/01_PANEL_LAYOUT.md

    Dis olculer:
    - Genislik: 1200 mm
    - Yukseklik: 2000 mm
    - Derinlik: 600 mm
    """
    width = 1200
    height = 2000
    depth = 600
    wall = 2

    body = make_hollow_box(width, height, depth, wall, (-width / 2, 0, -depth / 2))

    # Alt gland plakasi acikligi
    gland_cutout = make_box(500, 120, wall + 2, (-250, 10, -depth / 2 - 1))
    body = body.cut(gland_cutout)

    # Kapak menteşe referans padleri
    hinge_pad_1 = make_box(25, 180, 30, (-width / 2, height - 250, depth / 2 - 30))
    hinge_pad_2 = make_box(25, 180, 30, (-width / 2, 250, depth / 2 - 30))
    body = body.fuse(hinge_pad_1).fuse(hinge_pad_2)

    # Montaj ayaklari
    foot_1 = make_box(80, 120, 10, (-width / 2 + 80, -120, -depth / 2 + 40))
    foot_2 = make_box(80, 120, 10, (width / 2 - 160, -120, -depth / 2 + 40))
    body = body.fuse(foot_1).fuse(foot_2)

    feature = doc.addObject("Part::Feature", name)
    feature.Shape = body
    return feature


def create_main_panel_door(doc, name="Main_Panel_Door"):
    width = 1140
    height = 1940
    thickness = 2
    door = make_box(width, height, thickness, (-width / 2, 30, 300))

    handle_cutout = make_box(40, 160, thickness + 2, (width / 2 - 120, 900, 299))
    door = door.cut(handle_cutout)

    feature = doc.addObject("Part::Feature", name)
    feature.Shape = door
    return feature


def create_mounting_plate(doc, name="Main_Panel_Mounting_Plate"):
    plate = make_box(1000, 1800, 3, (-500, 100, -1.5))

    # 4 kosede montaj delikleri
    hole_positions = [
        (-450, 150, -3),
        (450, 150, -3),
        (-450, 1750, -3),
        (450, 1750, -3),
    ]
    for pos in hole_positions:
        plate = plate.cut(make_cylinder(4.5, 10, pos, (0, 0, 1)))

    feature = doc.addObject("Part::Feature", name)
    feature.Shape = plate
    return feature


def export_to_step(obj, filename):
    filepath = os.path.join(EXPORT_DIR, filename)
    Part.export([obj], filepath)
    print(f"Export edildi: {filepath}")
    return filepath


def build_main_panel_documents():
    body_doc = App.newDocument("Main_Panel_Body")
    body = create_main_panel_body(body_doc)
    body_doc.recompute()
    export_to_step(body, "Main_Panel_Body.stp")
    body_doc.saveAs(os.path.join(EXPORT_DIR, "Main_Panel_Body.FCStd"))

    door_doc = App.newDocument("Main_Panel_Door")
    door = create_main_panel_door(door_doc)
    door_doc.recompute()
    export_to_step(door, "Main_Panel_Door.stp")
    door_doc.saveAs(os.path.join(EXPORT_DIR, "Main_Panel_Door.FCStd"))

    plate_doc = App.newDocument("Main_Panel_Mounting_Plate")
    plate = create_mounting_plate(plate_doc)
    plate_doc.recompute()
    export_to_step(plate, "Main_Panel_Mounting_Plate.stp")
    plate_doc.saveAs(os.path.join(EXPORT_DIR, "Main_Panel_Mounting_Plate.FCStd"))

    print("Ana pano FreeCAD dosyalari hazirlandi.")


if __name__ == "__main__":
    build_main_panel_documents()
