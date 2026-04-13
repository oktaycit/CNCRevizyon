# -*- coding: utf-8 -*-
"""
FreeCAD Makro - STEP/DXF/STL Export
CNC Revizyon Projesi için

Kullanım:
    exec(open("/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD/07_Exports/Macro_Export.py").read())
    export_all_parts()
"""

import FreeCAD as App
import Part
import Mesh
import os


# Export dizinleri
PROJECT_ROOT = "/Users/oktaycit/Projeler/CNCRevizyon"
FREECAD_DIR = os.path.join(PROJECT_ROOT, "CAD", "FreeCAD")
EXPORTS_DIR = os.path.join(FREECAD_DIR, "07_Exports")

STEP_DIR = os.path.join(EXPORTS_DIR, "STEP")
DXF_DIR = os.path.join(EXPORTS_DIR, "DXF")
STL_DIR = os.path.join(EXPORTS_DIR, "STL")
PNG_DIR = os.path.join(EXPORTS_DIR, "PNG")


def ensure_directories():
    """Export dizinlerini oluştur"""
    for d in [STEP_DIR, DXF_DIR, STL_DIR, PNG_DIR]:
        os.makedirs(d, exist_ok=True)
        print(f"✅ Dizin hazır: {d}")


def export_to_step(obj, filename, directory=STEP_DIR):
    """
    Objeyi STEP formatında export et

    Args:
        obj: FreeCAD objesi
        filename: Dosya adı
        directory: Hedef dizin
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    if not filepath.endswith(".stp") and not filepath.endswith(".step"):
        filepath += ".stp"

    Part.export(obj, filepath)
    print(f"✅ STEP export: {filepath}")
    return filepath


def export_to_dxf(obj, filename, directory=DXF_DIR):
    """
    Objeyi DXF formatında export et

    Args:
        obj: FreeCAD objesi
        filename: Dosya adı
        directory: Hedef dizin
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    if not filepath.endswith(".dxf"):
        filepath += ".dxf"

    # Mesh üzerinden DXF export
    mesh = Mesh.PartMesh(obj.Shape)
    Mesh.export(mesh, filepath)
    print(f"✅ DXF export: {filepath}")
    return filepath


def export_to_stl(obj, filename, directory=STL_DIR, tolerance=0.1):
    """
    Objeyi STL formatında export et

    Args:
        obj: FreeCAD objesi
        filename: Dosya adı
        directory: Hedef dizin
        tolerance: Mesh toleransı (mm)
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    if not filepath.endswith(".stl"):
        filepath += ".stl"

    # Mesh oluştur ve export et
    mesh = Mesh.PartMesh(obj.Shape, tolerance)
    Mesh.export(mesh, filepath)
    print(f"✅ STL export: {filepath}")
    return filepath


def export_to_png(
    doc,
    filename,
    directory=PNG_DIR,
    width=1920,
    height=1080,
    view="isometric"
):
    """
    Document'i PNG olarak export et

    Args:
        doc: FreeCAD document
        filename: Dosya adı
        directory: Hedef dizin
        width: Genişlik (px)
        height: Yükseklik (px)
        view: Görünüm açısı
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

    filepath = os.path.join(directory, filename)
    if not filepath.endswith(".png"):
        filepath += ".png"

    try:
        import FreeCADGui as Gui

        Gui.ActiveDocument = doc
        Gui.SendMsgToActiveView("ViewFit")

        # Görünüm açısını ayarla
        if view == "isometric":
            Gui.activeDocument().activeView().viewIsometric()
        elif view == "front":
            Gui.activeDocument().activeView().viewFront()
        elif view == "top":
            Gui.activeDocument().activeView().viewTop()
        elif view == "right":
            Gui.activeDocument().activeView().viewRight()

        Gui.activeDocument().activeView().saveImage(filepath, width, height, "Current")
        print(f"✅ PNG export: {filepath}")
        return filepath

    except ImportError:
        print("⚠️ FreeCADGui bulunamadı, PNG export atlandı")
        return None


def export_all_objects(doc, base_name="assembly"):
    """
    Document'teki tüm objeleri export et

    Args:
        doc: FreeCAD document
        base_name: Dosya adı temeli
    """
    ensure_directories()

    exported = {
        "step": [],
        "dxf": [],
        "stl": []
    }

    for i, obj in enumerate(doc.Objects):
        obj_name = f"{base_name}_{obj.Name}"

        # STEP export
        try:
            step_file = export_to_step(obj, f"{obj_name}.stp")
            exported["step"].append(step_file)
        except Exception as e:
            print(f"⚠️ STEP export hatası ({obj.Name}): {e}")

        # STL export
        try:
            stl_file = export_to_stl(obj, f"{obj_name}.stl")
            exported["stl"].append(stl_file)
        except Exception as e:
            print(f"⚠️ STL export hatası ({obj.Name}): {e}")

    print(f"\n📊 Export Özeti:")
    print(f"   STEP: {len(exported['step'])} dosya")
    print(f"   STL: {len(exported['stl'])} dosya")

    return exported


def export_assembly(
    assembly_file,
    output_name=None,
    formats=["step", "stl", "png"]
):
    """
    Assembly dosyasını tüm formatlarda export et

    Args:
        assembly_file: Assembly .FCStd dosyası
        output_name: Çıktı adı (varsayılan: assembly adı)
        formats: Export formatları
    """
    ensure_directories()

    # Assembly dosyasını aç
    doc = App.open(assembly_file)
    print(f"✅ Assembly açıldı: {doc.Label}")

    if not output_name:
        output_name = os.path.basename(assembly_file).replace(".FCStd", "")

    results = {}

    # STEP export
    if "step" in formats:
        step_files = []
        for obj in doc.Objects:
            try:
                step_file = export_to_step(obj, f"{output_name}_{obj.Name}.stp")
                step_files.append(step_file)
            except Exception as e:
                print(f"⚠️ {obj.Name}: {e}")
        results["step"] = step_files

    # STL export
    if "stl" in formats:
        stl_files = []
        for obj in doc.Objects:
            try:
                stl_file = export_to_stl(obj, f"{output_name}_{obj.Name}.stl")
                stl_files.append(stl_file)
            except Exception as e:
                print(f"⚠️ {obj.Name}: {e}")
        results["stl"] = stl_files

    # PNG export
    if "png" in formats:
        png_files = []
        for view in ["isometric", "front", "top", "right"]:
            try:
                png_file = export_to_png(
                    doc,
                    f"{output_name}_{view}.png",
                    view=view
                )
                if png_file:
                    png_files.append(png_file)
            except Exception as e:
                print(f"⚠️ PNG export hatası ({view}): {e}")
        results["png"] = png_files

    print(f"\n📊 Export Tamamlandı:")
    for fmt, files in results.items():
        print(f"   {fmt.upper()}: {len(files)} dosya")

    return results


# Hızlı test
if __name__ == "__main__":
    print("🔧 Export makrosu hazır")
    print(f"📁 STEP: {STEP_DIR}")
    print(f"📁 DXF: {DXF_DIR}")
    print(f"📁 STL: {STL_DIR}")
    print(f"📁 PNG: {PNG_DIR}")

    ensure_directories()
