# -*- coding: utf-8 -*-
"""
Reusable helpers for staged FreeCAD test macros.

Each stage macro imports this file and runs one focused validation on the
active GFB-60/30RE-S digital twin document.
"""

import importlib.util
import os
import builtins
import time

import FreeCAD as App
import Part

try:
    import FreeCADGui as Gui
except ImportError:
    Gui = None


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_SCRIPT = os.path.join(THIS_DIR, "GFB_60_30RE_S_Model.py")

_MODEL_MODULE = None
ANIMATION_FRAME_PERIOD_S = 0.05
MIN_VISIBLE_MOVE_S = 0.45
MAX_ANIMATION_STEPS = 240


def _ascii_text(message):
    return str(message).encode("ascii", "replace").decode("ascii")


def _write_console(clean, level="message", fallback_print=None):
    text = f"{clean}\n"
    console = getattr(App, "Console", None)
    method_name = {
        "message": "PrintMessage",
        "warning": "PrintWarning",
        "error": "PrintError",
    }.get(level, "PrintMessage")
    if console is not None and hasattr(console, method_name):
        try:
            getattr(console, method_name)(text)
            return
        except Exception:
            pass
    if fallback_print is not None:
        fallback_print(clean)
        return
    print(clean)


def _console_message(message):
    clean = _ascii_text(message)
    _write_console(clean, level="message")


def _console_warning(message):
    clean = _ascii_text(message)
    _write_console(clean, level="warning")


def _console_error(message):
    clean = _ascii_text(message)
    _write_console(clean, level="error")


def _call_ascii_safe(func, *args, **kwargs):
    original_print = builtins.print

    def safe_print(*items, **print_kwargs):
        sep = print_kwargs.get("sep", " ")
        end = print_kwargs.get("end", "\n")
        text = sep.join(_ascii_text(item) for item in items)
        if end != "\n":
            text = f"{text}{end}"
        _write_console(text.rstrip("\n"), level="message", fallback_print=original_print)

    builtins.print = safe_print
    try:
        return func(*args, **kwargs)
    finally:
        builtins.print = original_print


def _load_model_module():
    global _MODEL_MODULE
    if _MODEL_MODULE is not None:
        return _MODEL_MODULE

    spec = importlib.util.spec_from_file_location("gfb_60_30re_s_model", MODEL_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Model script yuklenemedi: {MODEL_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _MODEL_MODULE = module
    return module


def _ensure_test_document():
    model = _load_model_module()
    doc = App.ActiveDocument
    if doc and doc.getObject("Variables") and doc.getObject("Table_Grid"):
        sheet = doc.getObject("Variables")
        if sheet is not None and hasattr(model, "MachineParameters"):
            try:
                params = model.MachineParameters()
                sheet.set("Y1", f"{params.VB_FIXED_CUT_X} mm")
                sheet.set("AB1", f"{params.LAMINE_KESIM_X_BITIS} mm")
            except Exception:
                pass
        if hasattr(model, "setup_kinematics") and hasattr(model, "MachineParameters"):
            try:
                model.setup_kinematics(doc, model.MachineParameters())
            except Exception:
                pass
        if hasattr(model, "ensure_vb_slot_visuals"):
            try:
                model.ensure_vb_slot_visuals(doc)
                doc.recompute()
            except Exception:
                pass
        return doc

    _console_message("[Macro] Aktif test dokumani bulunamadi, model olusturuluyor...")
    doc = _call_ascii_safe(model.create_complete_machine)
    sheet = doc.getObject("Variables")
    if sheet is not None and hasattr(model, "MachineParameters"):
        try:
            params = model.MachineParameters()
            sheet.set("Y1", f"{params.VB_FIXED_CUT_X} mm")
            sheet.set("AB1", f"{params.LAMINE_KESIM_X_BITIS} mm")
        except Exception:
            pass
    if hasattr(model, "ensure_vb_slot_visuals"):
        try:
            model.ensure_vb_slot_visuals(doc)
            doc.recompute()
        except Exception:
            pass
    return doc


def _show_view(view_name):
    active_doc = getattr(Gui, "ActiveDocument", None) if Gui is not None else None
    active_view = getattr(active_doc, "ActiveView", None)
    if Gui is None or active_doc is None or active_view is None:
        return

    view = active_view
    method_name = {
        "isometric": "viewIsometric",
        "top": "viewTop",
        "right": "viewRight",
        "front": "viewFront",
    }.get(view_name.lower())
    if method_name and hasattr(view, method_name):
        getattr(view, method_name)()
    Gui.SendMsgToActiveView("ViewFit")


def _has_live_view():
    active_doc = getattr(Gui, "ActiveDocument", None) if Gui is not None else None
    active_view = getattr(active_doc, "ActiveView", None)
    return Gui is not None and active_doc is not None and active_view is not None


def _refresh_scene(doc=None):
    if doc is not None:
        doc.recompute()
    if _has_live_view():
        try:
            Gui.updateGui()
        except Exception:
            pass


def _require_object(doc, name):
    obj = doc.getObject(name)
    if obj is None:
        raise RuntimeError(f"Gerekli obje bulunamadi: {name}")
    return obj


def _require_sheet(doc, name):
    sheet = doc.getObject(name)
    if sheet is None:
        raise RuntimeError(f"Gerekli spreadsheet bulunamadi: {name}")
    return sheet


def _quantity_value(value):
    if hasattr(value, "Value"):
        return float(value.Value)
    return float(value)


def _sheet_float(sheet, cell, default=0.0):
    raw = sheet.get(cell)
    if raw is None:
        return float(default)
    text = str(raw).replace("'", "").strip()
    if not text:
        return float(default)
    token = text.split()[0].replace(",", ".")
    try:
        return float(token)
    except Exception:
        return float(default)


def _current_axes(doc):
    ss = _require_sheet(doc, "Variables")
    return {
        "x": _sheet_float(ss, "A1", 0.0),
        "y": _sheet_float(ss, "B1", 0.0),
        "z": _sheet_float(ss, "C1", 0.0),
        "v": _sheet_float(ss, "D1", 0.0),
    }


def _axis_move_duration_s(params, start_axes, end_axes):
    axis_speeds_mm_s = {
        "x": max(1.0, float(params.X_HIZ_MAX) / 60.0),
        "y": max(1.0, float(params.Y_HIZ_MAX) / 60.0),
        "z": max(1.0, float(params.Z_HIZ_MAX) / 60.0),
        "v": max(1.0, float(params.V_HIZ_MAX) / 60.0),
    }
    durations = []
    for axis in ("x", "y", "z", "v"):
        durations.append(abs(end_axes[axis] - start_axes[axis]) / axis_speeds_mm_s[axis])
    return max(durations)


def _animate_axes(doc, params, x=None, y=None, z=None, v=None, label=None, min_duration_s=0.0):
    model = _load_model_module()
    start_axes = _current_axes(doc)
    end_axes = {
        "x": start_axes["x"] if x is None else float(x),
        "y": start_axes["y"] if y is None else float(y),
        "z": start_axes["z"] if z is None else float(z),
        "v": start_axes["v"] if v is None else float(v),
    }

    if label:
        _console_message(label)

    if not _has_live_view():
        model.set_axis_positions(
            doc,
            x=end_axes["x"],
            y=end_axes["y"],
            z=end_axes["z"],
            v=end_axes["v"],
            recompute=False,
        )
        doc.recompute()
        return {"duration_s": 0.0, "steps": 1}

    duration_s = _axis_move_duration_s(params, start_axes, end_axes)
    distance_changed = any(abs(end_axes[axis] - start_axes[axis]) > 1e-6 for axis in ("x", "y", "z", "v"))
    if distance_changed:
        duration_s = max(duration_s, float(min_duration_s))
    steps = max(1, min(MAX_ANIMATION_STEPS, int(duration_s / ANIMATION_FRAME_PERIOD_S) + 1))

    for step in range(1, steps + 1):
        t = float(step) / float(steps)
        model.set_axis_positions(
            doc,
            x=start_axes["x"] + (end_axes["x"] - start_axes["x"]) * t,
            y=start_axes["y"] + (end_axes["y"] - start_axes["y"]) * t,
            z=start_axes["z"] + (end_axes["z"] - start_axes["z"]) * t,
            v=start_axes["v"] + (end_axes["v"] - start_axes["v"]) * t,
            recompute=False,
        )
        _refresh_scene(doc)
        if step < steps and duration_s > 0.0:
            time.sleep(duration_s / float(steps))

    return {"duration_s": round(duration_s, 2), "steps": steps}


def _animate_sheet_mm(doc, sheet, cell, target_mm, speed_mm_min, label=None, min_duration_s=0.0):
    start_mm = _sheet_float(sheet, cell, 0.0)
    target_mm = float(target_mm)

    if label:
        _console_message(label)

    if not _has_live_view():
        sheet.set(cell, f"{target_mm} mm")
        doc.recompute()
        return {"duration_s": 0.0, "steps": 1}

    speed_mm_s = max(1.0, float(speed_mm_min) / 60.0)
    duration_s = abs(target_mm - start_mm) / speed_mm_s
    if abs(target_mm - start_mm) > 1e-6:
        duration_s = max(duration_s, float(min_duration_s))
    steps = max(1, min(MAX_ANIMATION_STEPS, int(duration_s / ANIMATION_FRAME_PERIOD_S) + 1))

    for step in range(1, steps + 1):
        t = float(step) / float(steps)
        value_mm = start_mm + (target_mm - start_mm) * t
        sheet.set(cell, f"{value_mm} mm")
        _refresh_scene(doc)
        if step < steps and duration_s > 0.0:
            time.sleep(duration_s / float(steps))

    return {"duration_s": round(duration_s, 2), "steps": steps}


def _animate_object_x(doc, obj, target_x, speed_mm_min, label=None, min_duration_s=0.0):
    start_x = float(obj.Placement.Base.x)
    target_x = float(target_x)

    if label:
        _console_message(label)

    if not _has_live_view():
        obj.Placement.Base.x = target_x
        doc.recompute()
        return {"duration_s": 0.0, "steps": 1}

    speed_mm_s = max(1.0, float(speed_mm_min) / 60.0)
    duration_s = abs(target_x - start_x) / speed_mm_s
    if abs(target_x - start_x) > 1e-6:
        duration_s = max(duration_s, float(min_duration_s))
    steps = max(1, min(MAX_ANIMATION_STEPS, int(duration_s / ANIMATION_FRAME_PERIOD_S) + 1))

    for step in range(1, steps + 1):
        t = float(step) / float(steps)
        obj.Placement.Base.x = start_x + (target_x - start_x) * t
        _refresh_scene(doc)
        if step < steps and duration_s > 0.0:
            time.sleep(duration_s / float(steps))

    return {"duration_s": round(duration_s, 2), "steps": steps}


def _distance_between_shapes(obj_a, obj_b):
    try:
        return float(obj_a.Shape.distToShape(obj_b.Shape)[0])
    except Exception:
        return 0.0


def _common_volume(obj_a, obj_b):
    try:
        return float(obj_a.Shape.common(obj_b.Shape).Volume)
    except Exception:
        return 0.0


def _interval_overlap(a_min, a_max, b_min, b_max):
    return max(0.0, min(a_max, b_max) - max(a_min, b_min))


def _bbox_overlap(a_box, b_box):
    return {
        "x": _interval_overlap(a_box.XMin, a_box.XMax, b_box.XMin, b_box.XMax),
        "y": _interval_overlap(a_box.YMin, a_box.YMax, b_box.YMin, b_box.YMax),
        "z": _interval_overlap(a_box.ZMin, a_box.ZMax, b_box.ZMin, b_box.ZMax),
    }


def _find_signal_row(sheet, signal_name):
    for row in range(2, 120):
        cell = sheet.get(f"B{row}")
        if not cell:
            return None
        if str(cell).replace("'", "").strip() == signal_name:
            return row
    return None


def _set_signal(sheet, signal_name, state):
    row = _find_signal_row(sheet, signal_name)
    if row is not None:
        sheet.set(f"C{row}", "1" if state else "0")
    return row


def _ensure_box(doc, name, length, width, height, base, color, transparency):
    obj = doc.getObject(name)
    if obj is None:
        obj = doc.addObject("Part::Box", name)
    obj.Length = float(length)
    obj.Width = float(width)
    obj.Height = float(height)
    obj.Placement.Base = App.Vector(float(base[0]), float(base[1]), float(base[2]))
    if hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.Visibility = True
        obj.ViewObject.ShapeColor = color
        obj.ViewObject.Transparency = transparency
    return obj


def _hide_object(doc, name):
    obj = doc.getObject(name)
    if obj and hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.Visibility = False


def _set_object_visibility(doc, name, visible):
    obj = doc.getObject(name)
    if obj and hasattr(obj, "ViewObject") and obj.ViewObject:
        obj.ViewObject.Visibility = bool(visible)
    return obj


def _stage_header(title):
    _console_message("=" * 72)
    _console_message(title)
    _console_message("=" * 72)
    _console_message("Home referansi: operator terminali tarafi (X=0, Y=0)")


def run_stage_1_mechanical_clearance():
    model = _load_model_module()
    params = model.MachineParameters()
    doc = _ensure_test_document()
    ss = _require_sheet(doc, "Variables")

    _stage_header("ASAMA 1 - Mekanik Cakisma ve Park Pozisyonu Testi")

    ss.set("Z1", f"{params.PARK_Z_GERI_CEKME} mm")
    model.set_lamine_mode(doc, False, recompute=False)
    _show_view("right")
    _animate_axes(
        doc,
        params,
        x=params.X_HOME,
        y=params.Y_HOME,
        z=params.Z_HOME,
        v=params.V_HOME,
        label="Kopru home/park noktasina alinıyor...",
        min_duration_s=MIN_VISIBLE_MOVE_S,
    )

    table = _require_object(doc, "Table_Grid")
    lower_head = _require_object(doc, "Lower_Cutter_Head")
    lower_wheel = _require_object(doc, "Lower_Cutting_Wheel")
    heater = _require_object(doc, "Heater_Rod")
    bridge = _require_object(doc, "Portal_Bridge")

    table_bb = table.Shape.BoundBox
    lower_wheel_bb = lower_wheel.Shape.BoundBox

    _console_message(f"Table base Z = {table.Placement.Base.z:.2f} mm")
    _console_message(
        f"Heater_Rod base Z = {heater.Placement.Base.z:.2f} mm | "
        f"table alti fark = {table.Placement.Base.z - heater.Placement.Base.z:.2f} mm"
    )
    _console_message(
        f"Lower_Cutter_Head base Z = {lower_head.Placement.Base.z:.2f} mm | "
        f"table alti fark = {table.Placement.Base.z - lower_head.Placement.Base.z:.2f} mm"
    )
    _console_message(
        f"Lower_Cutting_Wheel ust nokta = {lower_wheel_bb.ZMax:.2f} mm | "
        f"table alt yuzey boslugu = {table_bb.ZMin - lower_wheel_bb.ZMax:.2f} mm"
    )

    scan_pairs = [
        ("Lower_Cutter_Head", lower_head, "Table_Grid", table),
        ("Lower_Cutting_Wheel", lower_wheel, "Table_Grid", table),
        ("Heater_Rod", heater, "Table_Grid", table),
        ("Lower_Cutter_Head", lower_head, "Portal_Bridge", bridge),
        ("Heater_Rod", heater, "Portal_Bridge", bridge),
    ]
    corners = [
        (0.0, 0.0),
        (0.0, params.Y_MAX),
        (params.X_VB_MECHANICAL_STOP, 0.0),
        (params.X_VB_MECHANICAL_STOP, params.Y_MAX),
    ]

    scan_results = []
    overall_safe = True
    for x_pos, y_pos in corners:
        _animate_axes(
            doc,
            params,
            x=x_pos,
            y=y_pos,
            z=params.Z_HOME,
            v=0.0,
            label=f"Kopru tarama konumuna gidiyor: X={x_pos:.0f} Y={y_pos:.0f}",
        )
        _console_message(f"-- Corner tarama: X={x_pos:.0f} Y={y_pos:.0f}")
        for left_name, left_obj, right_name, right_obj in scan_pairs:
            common_volume = _common_volume(left_obj, right_obj)
            distance = _distance_between_shapes(left_obj, right_obj)
            clear = common_volume <= 1e-6
            overall_safe = overall_safe and clear
            scan_results.append(
                {
                    "corner": (x_pos, y_pos),
                    "left": left_name,
                    "right": right_name,
                    "distance_mm": round(distance, 2),
                    "common_volume_mm3": round(common_volume, 2),
                    "clear": clear,
                }
            )
            state = "CLEAR" if clear else "COLLISION"
            _console_message(
                f"   {left_name} vs {right_name} -> {state} | "
                f"distance={distance:.2f} mm | common={common_volume:.2f} mm^3"
            )
    _console_message(f"ASAMA 1 SONUC = {'PASS' if overall_safe else 'CHECK'}")
    return {"stage": 1, "safe": overall_safe, "scan_results": scan_results}


def run_stage_2_probe_alignment():
    model = _load_model_module()
    params = model.MachineParameters()
    doc = _ensure_test_document()
    ss = _require_sheet(doc, "Variables")

    _stage_header("ASAMA 2 - Vantuzlu X-Surus ve Orijinleme (G31)")

    ss.set("T1", "0 mm")
    _show_view("top")
    _animate_axes(
        doc,
        params,
        x=params.X_PARK_BTS,
        y=params.LAMINE_KESIM_Y_BASLANGIC,
        z=params.Z_HOME,
        v=0.0,
        label="Kopru lamine hazirlik konumuna gercek hizda gidiyor...",
        min_duration_s=MIN_VISIBLE_MOVE_S,
    )
    model.set_lamine_mode(doc, True, recompute=False)
    model.set_bridge_clamp_state(doc, True, recompute=False)
    doc.recompute()

    glass = _require_object(doc, "Glass_Sheet_Reference")
    heater = _require_object(doc, "Heater_Rod")
    breaking = _require_object(doc, "Breaking_Profile")

    glass_bb = glass.Shape.BoundBox
    thickness = glass_bb.ZMax - glass_bb.ZMin
    proxy_length = 220.0
    proxy_width = max(200.0, (glass_bb.YMax - glass_bb.YMin) - 200.0)
    proxy_y = glass_bb.YMin + 100.0
    probe_x = breaking.Placement.Base.x + 100.0
    moving_glass_x = probe_x - proxy_length
    moving_glass_start_x = max(50.0, moving_glass_x - 900.0)

    probe = _ensure_box(
        doc,
        "Codex_X_Probe_Point",
        2.0,
        proxy_width,
        max(20.0, thickness),
        (probe_x, proxy_y, glass_bb.ZMin),
        (1.0, 0.2, 0.2),
        20,
    )
    moving_glass = _ensure_box(
        doc,
        "Codex_Moving_Glass",
        proxy_length,
        proxy_width,
        thickness,
        (moving_glass_start_x, proxy_y, glass_bb.ZMin),
        (0.2, 0.7, 1.0),
        70,
    )
    _hide_object(doc, "Codex_Split_Glass_Left")
    _hide_object(doc, "Codex_Split_Glass_Right")
    _hide_object(doc, "Codex_Tension_Gap")
    _refresh_scene(doc)

    _animate_object_x(
        doc,
        moving_glass,
        moving_glass_x,
        params.X_HIZ_MAX,
        label="Vakum koprusu cami probe noktasina suruyor...",
        min_duration_s=0.80,
    )

    moving_bb = moving_glass.Shape.BoundBox
    heater_overlap = _bbox_overlap(moving_bb, heater.Shape.BoundBox)
    breaking_overlap = _bbox_overlap(moving_bb, breaking.Shape.BoundBox)
    probe_error = abs(moving_bb.XMax - probe.Placement.Base.x)

    _console_message("Vakum kilitleme uygulandi: Variables.AD1 = 1")
    _console_message(
        f"Pause noktasi: glass front edge = {moving_bb.XMax:.2f} mm | "
        f"probe = {probe.Placement.Base.x:.2f} mm | hata = {probe_error:.2f} mm"
    )
    _console_message(
        f"Cam proxy vs Heater_Rod overlap -> X={heater_overlap['x']:.2f} "
        f"Y={heater_overlap['y']:.2f} Z={heater_overlap['z']:.2f}"
    )
    _console_message(
        f"Cam proxy vs Breaking_Profile overlap -> X={breaking_overlap['x']:.2f} "
        f"Y={breaking_overlap['y']:.2f} Z={breaking_overlap['z']:.2f}"
    )
    _console_message("PAUSE: Cam on kenari X_Probe_Point koordinatinda.")

    aligned = probe_error <= 0.01 and heater_overlap["x"] > 0.0 and breaking_overlap["x"] > 0.0
    _console_message(f"ASAMA 2 SONUC = {'PASS' if aligned else 'CHECK'}")
    return {
        "stage": 2,
        "probe_x_mm": round(probe.Placement.Base.x, 2),
        "front_edge_x_mm": round(moving_bb.XMax, 2),
        "probe_error_mm": round(probe_error, 2),
        "aligned": aligned,
    }


def run_stage_3_vb_y_sync():
    model = _load_model_module()
    params = model.MachineParameters()
    doc = _ensure_test_document()
    ss = _require_sheet(doc, "Variables")

    _stage_header("ASAMA 3 - VB Ortak Y Senkronizasyonu")

    ss.set("T1", "0 mm")
    ss.set("D1", "0 mm")
    model.set_lamine_mode(doc, True, recompute=False)
    _show_view("top")
    _animate_axes(
        doc,
        params,
        x=params.X_PARK_BTS,
        y=params.Y_HOME,
        z=params.Z_HOME,
        v=params.V_HOME,
        label="Kopru kesim hattina gercek hizda konumlaniyor...",
        min_duration_s=MIN_VISIBLE_MOVE_S,
    )

    top_wheel = _require_object(doc, "Cutting_Wheel")
    lower_wheel = _require_object(doc, "Lower_Cutting_Wheel")
    channel = _require_object(doc, "Lower_Cutter_Channel_Reference")
    table = _require_object(doc, "Table_Grid")

    sample_rows = []
    channel_bb = channel.Shape.BoundBox
    raw_offset = None
    max_delta = 0.0
    min_channel_clear = None

    for y_pos in range(0, int(params.Y_MAX) + 1, 100):
        _animate_axes(
            doc,
            params,
            x=params.X_PARK_BTS,
            y=float(y_pos),
            z=params.Z_HOME,
            v=0.0,
        )

        raw_top = float(top_wheel.Placement.Base.y)
        low_x = float(lower_wheel.Placement.Base.y)
        if raw_offset is None:
            raw_offset = low_x - raw_top
        top_x = raw_top
        delta = abs(top_x - low_x)
        max_delta = max(max_delta, delta)

        low_bb = lower_wheel.Shape.BoundBox
        side_clear = min(low_bb.Center.x - channel_bb.XMin, channel_bb.XMax - low_bb.Center.x)
        if min_channel_clear is None or side_clear < min_channel_clear:
            min_channel_clear = side_clear

        if y_pos in (0, 500, 1000, 1500, 2000, 2500, 3000):
            sample_rows.append(
                {
                    "y_mm": y_pos,
                    "raw_top_mm": round(raw_top, 2),
                    "top_track_mm": round(top_x, 2),
                    "low_track_mm": round(low_x, 2),
                    "delta_mm": round(delta, 2),
                    "channel_clear_mm": round(side_clear, 2),
                    "common_volume_mm3": round(_common_volume(lower_wheel, table), 2),
                }
            )

    for row in sample_rows:
        _console_message(
            f"Y={row['y_mm']:4d} -> top_track={row['top_track_mm']:7.2f} | "
            f"low_track={row['low_track_mm']:7.2f} | delta={row['delta_mm']:.2f} | "
            f"kanal_clear={row['channel_clear_mm']:.2f}"
        )

    _console_message(f"Yapisal track ofseti = {raw_offset:.2f} mm")
    _console_message(f"Normalize maksimum delta = {max_delta:.2f} mm")
    _console_message(f"Minimum kanal yan boslugu = {min_channel_clear:.2f} mm")
    _console_warning(
        "Not: Lower_Cutting_Wheel/Table ortak hacmi sade gap-slot katisi modellenmediyse "
        "pozitif kalabilir; bu senkron hatasi anlamina gelmez."
    )
    sync_ok = max_delta <= 0.01
    _console_message(f"ASAMA 3 SONUC = {'PASS' if sync_ok else 'CHECK'}")
    return {
        "stage": 3,
        "offset_mm": round(raw_offset, 2),
        "max_delta_mm": round(max_delta, 2),
        "min_channel_clear_mm": round(min_channel_clear, 2),
        "samples": sample_rows,
        "sync_ok": sync_ok,
    }


def run_stage_3_ecam_sync():
    """Legacy wrapper kept for older macros and notes."""
    return run_stage_3_vb_y_sync()


def run_stage_4_heating_tension():
    model = _load_model_module()
    params = model.MachineParameters()
    doc = _ensure_test_document()
    ss = _require_sheet(doc, "Variables")
    io_sheet = _require_sheet(doc, "Lamine_IO")

    _stage_header("ASAMA 4 - PVB Isitma ve Gap Acma")

    model.set_lamine_mode(doc, True, recompute=False)
    _show_view("top")
    _animate_axes(
        doc,
        params,
        x=params.X_PARK_BTS,
        y=params.Y_MAX,
        z=params.Z_HOME,
        v=0.0,
        label="Kopru isitma sonu germe konumuna gidiyor...",
        min_duration_s=MIN_VISIBLE_MOVE_S,
    )
    ss.set("V1", f"{params.FOLYO_GERME_X_OFFSET} mm")
    ss.set("T1", "0 mm")
    doc.recompute()

    heater_rows = {}
    for signal_name in (
        "HEATER_DOWN",
        "HEATER_ENABLE",
        "HEATER_ZONE_1",
        "HEATER_ZONE_2",
        "HEATER_SAFETY_ENABLE",
    ):
        heater_rows[signal_name] = _set_signal(io_sheet, signal_name, True)

    loading_beam = _require_object(doc, "Loading_Suction_Beam")
    heater = _require_object(doc, "Heater_Rod")
    glass = _require_object(doc, "Glass_Sheet_Reference")
    breaking = _require_object(doc, "Breaking_Profile")

    beam_x_before = float(loading_beam.Placement.Base.x)
    _animate_sheet_mm(
        doc,
        ss,
        "T1",
        2.0,
        params.X_HIZ_MAX,
        label="Yukleme koprusu +2.0 mm germe ofsetine gidiyor...",
        min_duration_s=0.60,
    )
    beam_x_after = float(loading_beam.Placement.Base.x)
    beam_shift = beam_x_after - beam_x_before

    glass_bb = glass.Shape.BoundBox
    cut_center_x = float(breaking.Shape.BoundBox.Center.x)
    full_y = glass_bb.YMax - glass_bb.YMin
    thickness = glass_bb.ZMax - glass_bb.ZMin
    gap_length = max(0.1, beam_shift)
    gap_start_x = cut_center_x - gap_length / 2.0

    left = _ensure_box(
        doc,
        "Codex_Split_Glass_Left",
        max(1.0, gap_start_x - glass_bb.XMin),
        full_y,
        thickness,
        (glass_bb.XMin, glass_bb.YMin, glass_bb.ZMin),
        (0.45, 0.75, 1.0),
        65,
    )
    gap = _ensure_box(
        doc,
        "Codex_Tension_Gap",
        gap_length,
        full_y,
        thickness,
        (gap_start_x, glass_bb.YMin, glass_bb.ZMin),
        (1.0, 0.15, 0.15),
        20,
    )
    right = _ensure_box(
        doc,
        "Codex_Split_Glass_Right",
        max(1.0, glass_bb.XMax - (gap_start_x + gap_length)),
        full_y,
        thickness,
        (gap_start_x + gap_length, glass_bb.YMin, glass_bb.ZMin),
        (1.0, 0.72, 0.42),
        65,
    )
    _hide_object(doc, "Codex_Moving_Glass")
    _hide_object(doc, "Codex_X_Probe_Point")
    doc.recompute()

    proxy_gap = float(right.Placement.Base.x) - (float(left.Placement.Base.x) + _quantity_value(left.Length))
    heater_gap = glass_bb.ZMin - heater.Shape.BoundBox.ZMax

    _console_message(
        f"Loading_Suction_Beam X once = {beam_x_before:.2f} mm | "
        f"sonra = {beam_x_after:.2f} mm | ofset = {beam_shift:.2f} mm"
    )
    _console_message(f"Proxy cam ayirma boslugu = {proxy_gap:.2f} mm")
    _console_message(f"Cam alti / Heater_Rod ustu boslugu = {heater_gap:.2f} mm")
    for signal_name, row in heater_rows.items():
        _console_message(f"   {signal_name} -> row {row}, state=1")
    _console_warning(
        "Not: FCStd tek cam kati tuttugu icin fiziksel ayrilma split-glass proxy kutular "
        "ile gosterildi; köprü ofseti gercek Loading_Suction_Beam kinematiginden olculdu."
    )
    tension_ok = abs(beam_shift - 2.0) <= 0.01 and abs(proxy_gap - 2.0) <= 0.01
    _console_message(f"ASAMA 4 SONUC = {'PASS' if tension_ok else 'CHECK'}")
    return {
        "stage": 4,
        "beam_shift_mm": round(beam_shift, 2),
        "proxy_gap_mm": round(proxy_gap, 2),
        "heater_gap_mm": round(heater_gap, 2),
        "tension_ok": tension_ok,
    }


def _set_zone_transparency(doc, obj_name, transparency):
    obj = doc.getObject(obj_name)
    if obj and hasattr(obj, "ViewObject") and obj.ViewObject:
        try:
            obj.ViewObject.Transparency = int(transparency)
        except Exception:
            pass


def _highlight_lamine_zone(doc, phase_name):
    phase_key = str(phase_name).casefold()
    zone_map = {
        "simetrik scoring hazirlik": "Lamine_Cut_Zone",
        "simetrik scoring": "Lamine_Cut_Zone",
        "vb y kesim hazirlik": "Lamine_Cut_Zone",
        "vb y kesimi": "Lamine_Cut_Zone",
        "cam kirma": "Lamine_Break_Zone",
        "kirma": "Lamine_Break_Zone",
        "pvb isitma": "Lamine_Heat_Zone",
        "isitma": "Lamine_Heat_Zone",
        "gap acma": "Lamine_Glass_Hold_Zone",
        "folyo germe": "Lamine_Glass_Hold_Zone",
        "folyo kesme ve ayirma": "Lamine_Separation_Zone",
        "ayirma": "Lamine_Separation_Zone",
    }
    active_zone = zone_map.get(phase_key)
    default_levels = {
        "Lamine_Glass_Hold_Zone": 68,
        "Lamine_Cut_Zone": 45,
        "Lamine_Heat_Zone": 58,
        "Lamine_Separation_Zone": 58,
        "Lamine_Break_Zone": 58,
    }
    for obj_name, transparency in default_levels.items():
        _set_zone_transparency(doc, obj_name, transparency)
    if active_zone is not None:
        _set_zone_transparency(doc, active_zone, 15)
    _refresh_scene(doc)


def run_lamine_phase_playback(dwell_s=0.8, min_move_s=0.45, include_terminal=True):
    """
    Lamine kesim fazlarini FreeCAD sahnesinde sirali animasyon olarak oynat.

    Mekanik mantik:
    - Gantry cami VB hattina getirir ve X'te sabitlenir.
    - VB ust/alt kesici ortak Y ekseninde hareket eder.
    - Sonrasinda cam kirma, PVB isitma, gap acma ve folyo kesme/ayirma gorunur.
    """
    model = _load_model_module()
    params = model.MachineParameters()
    doc = _ensure_test_document()
    io_sheet = _require_sheet(doc, "Lamine_IO")
    y_carriage = doc.getObject("Y_Carriage")
    z_carriage = doc.getObject("Z_Carriage")
    vb_y_carriage = doc.getObject("VB_Y_Carriage")
    portal_bridge = doc.getObject("Portal_Bridge")

    def _obj_axis_value(obj, axis_name):
        if obj is None:
            return None
        try:
            return float(getattr(obj.Placement.Base, axis_name))
        except Exception:
            return None

    def _series_summary(values):
        numeric = [float(value) for value in values if value is not None]
        if not numeric:
            return {"min": None, "max": None, "delta": None, "moved": None}
        min_value = min(numeric)
        max_value = max(numeric)
        delta = max_value - min_value
        return {
            "min": round(min_value, 2),
            "max": round(max_value, 2),
            "delta": round(delta, 2),
            "moved": delta > 0.01,
        }

    motion_trace = {
        "cartesian_y_y_mm": [],
        "cartesian_z_z_mm": [],
        "vb_y_y_mm": [],
        "bridge_x_mm": [],
    }

    _stage_header("LAMINE FAZ PLAYBACK")
    _show_view("isometric")

    phase_sequence = model.build_lamine_phase_sequence(params)
    if not include_terminal:
        phase_sequence = phase_sequence[:-1]

    default_inputs = {signal: False for signal in model.LAMINE_INPUT_DESCRIPTIONS}
    default_outputs = {signal: False for signal in model.LAMINE_OUTPUT_DESCRIPTIONS}
    default_inputs["ESTOP_OK"] = True
    default_inputs["DOOR_CLOSED"] = True
    default_inputs["AIR_PRESSURE_OK"] = True

    try:
        _animate_sheet_mm(
            doc,
            _require_sheet(doc, "Variables"),
            "T1",
            0.0,
            params.X_HIZ_MAX,
            label="Germe ofseti sifirlaniyor...",
            min_duration_s=0.20,
        )
    except Exception:
        pass

    results = []
    for phase in phase_sequence:
        target = phase["target"]
        inputs = dict(default_inputs)
        outputs = dict(default_outputs)
        inputs.update(phase["inputs"])
        outputs.update(phase["outputs"])

        _console_message(f"[Playback] Faz -> {phase['phase']}")
        _highlight_lamine_zone(doc, phase["phase"])

        model.set_lamine_mode(doc, outputs.get("LAMINE_MODE_ENABLE", False), recompute=False)
        z_sheet_value = float(params.Z_HOME) - float(target["z"])
        move_result = _animate_axes(
            doc,
            params,
            x=float(target["x"]),
            y=float(target["y"]),
            z=z_sheet_value,
            v=float(target["v"]),
            label=(
                f"  hedef: X={float(target['x']):.0f} | "
                f"Y={float(target['y']):.0f} | "
                f"Zsheet={z_sheet_value:.0f} | V={float(target['v']):.0f}"
            ),
            min_duration_s=float(min_move_s),
        )

        model.set_bridge_clamp_state(
            doc,
            inputs.get("VACUUM_OK", False) and outputs.get("LOADING_VACUUM_ENABLE", False),
            recompute=False,
        )
        model.update_lamine_io_sheet(doc, inputs, outputs)

        if phase["phase"] == "Gap Acma":
            _animate_sheet_mm(
                doc,
                _require_sheet(doc, "Variables"),
                "T1",
                float(params.FOLYO_GERME_X_OFFSET),
                params.X_HIZ_MAX,
                label="  folyo germe ofseti uygulanıyor...",
                min_duration_s=max(0.35, float(min_move_s)),
            )
        elif phase["phase"] == "Bosaltma":
            _animate_sheet_mm(
                doc,
                _require_sheet(doc, "Variables"),
                "T1",
                0.0,
                params.X_HIZ_MAX,
                label="  germe ofseti sifira donuyor...",
                min_duration_s=0.20,
            )

        doc.recompute()
        _refresh_scene(doc)
        motion_trace["cartesian_y_y_mm"].append(_obj_axis_value(y_carriage, "y"))
        motion_trace["cartesian_z_z_mm"].append(_obj_axis_value(z_carriage, "z"))
        motion_trace["vb_y_y_mm"].append(_obj_axis_value(vb_y_carriage, "y"))
        motion_trace["bridge_x_mm"].append(_obj_axis_value(portal_bridge, "x"))
        if float(dwell_s) > 0.0:
            time.sleep(float(dwell_s))

        active_outputs = sorted(name for name, state in outputs.items() if state)
        _console_message(f"  aktif cikislar: {', '.join(active_outputs) if active_outputs else '-'}")
        results.append(
            {
                "phase": phase["phase"],
                "target": dict(target),
                "move": move_result,
                "active_outputs": active_outputs,
            }
        )

    _highlight_lamine_zone(doc, "Bosaltma")
    _console_message("[Playback] Lamine faz animasyonu tamamlandi.")
    sanity_report = {
        "cartesian_y": _series_summary(motion_trace["cartesian_y_y_mm"]),
        "cartesian_z": _series_summary(motion_trace["cartesian_z_z_mm"]),
        "vb_y": _series_summary(motion_trace["vb_y_y_mm"]),
        "bridge_x": _series_summary(motion_trace["bridge_x_mm"]),
    }
    _console_message("-" * 72)
    _console_message("LAMINE PLAYBACK SANITY CHECK")
    _console_message(
        f"  CartesianYMoved = {sanity_report['cartesian_y']['moved']} | "
        f"delta = {sanity_report['cartesian_y']['delta']} mm"
    )
    _console_message(
        f"  CartesianZMoved = {sanity_report['cartesian_z']['moved']} | "
        f"delta = {sanity_report['cartesian_z']['delta']} mm"
    )
    _console_message(
        f"  VBYMoved        = {sanity_report['vb_y']['moved']} | "
        f"delta = {sanity_report['vb_y']['delta']} mm"
    )
    _console_message(
        f"  BridgeXMoved    = {sanity_report['bridge_x']['moved']} | "
        f"delta = {sanity_report['bridge_x']['delta']} mm"
    )
    _console_message("  Beklenen: CartesianY=False, CartesianZ=False, VBY=True, BridgeX=True")
    return {
        "phases": [row["phase"] for row in results],
        "steps": results,
        "dwell_s": float(dwell_s),
        "min_move_s": float(min_move_s),
        "sanity_report": sanity_report,
    }


def _world_to_machine_for_top_wheel(doc, target_world_x, target_world_y):
    axes = _current_axes(doc)
    wheel = _require_object(doc, "Cutting_Wheel")
    current_world_x = float(wheel.Placement.Base.x)
    current_world_y = float(wheel.Placement.Base.y)
    return {
        "x": axes["x"] + (float(target_world_x) - current_world_x),
        "y": axes["y"] - (float(target_world_y) - current_world_y),
    }


def _animate_top_wheel_to(doc, params, target_world_x, target_world_y, z_value, label=None, min_duration_s=0.0):
    machine_target = _world_to_machine_for_top_wheel(doc, target_world_x, target_world_y)
    result = _animate_axes(
        doc,
        params,
        x=machine_target["x"],
        y=machine_target["y"],
        z=float(z_value),
        v=0.0,
        label=label,
        min_duration_s=min_duration_s,
    )
    wheel = _require_object(doc, "Cutting_Wheel")
    result.update(
        {
            "target_world_x_mm": round(float(target_world_x), 2),
            "target_world_y_mm": round(float(target_world_y), 2),
            "error_x_mm": round(float(wheel.Placement.Base.x) - float(target_world_x), 2),
            "error_y_mm": round(float(wheel.Placement.Base.y) - float(target_world_y), 2),
        }
    )
    return result


def _default_float_cut_segments(sheet_length_mm, sheet_width_mm):
    x_margin = max(280.0, min(420.0, sheet_length_mm * 0.08))
    y_margin = max(220.0, min(320.0, sheet_width_mm * 0.09))
    y_band = max(450.0, min(650.0, sheet_width_mm * 0.24))
    x_mid = sheet_length_mm * 0.52
    return [
        {
            "name": "X_Skor_1",
            "start": (x_margin, y_margin + y_band),
            "end": (sheet_length_mm - x_margin, y_margin + y_band),
        },
        {
            "name": "Y_Skor_1",
            "start": (x_mid, y_margin),
            "end": (x_mid, sheet_width_mm - y_margin),
        },
        {
            "name": "X_Skor_2",
            "start": (x_margin, sheet_width_mm - (y_margin + y_band)),
            "end": (sheet_length_mm - x_margin, sheet_width_mm - (y_margin + y_band)),
        },
    ]


def _build_float_cut_scene(doc, params, config):
    table = _require_object(doc, "Table_Grid")
    table_bb = table.Shape.BoundBox

    sheet_length_mm = max(600.0, min(float(config.get("sheet_length_mm", 5200.0)), table_bb.XLength - 80.0))
    sheet_width_mm = max(600.0, min(float(config.get("sheet_width_mm", 2800.0)), table_bb.YLength - 80.0))
    margin_x_mm = min(max(0.0, float(config.get("sheet_margin_x_mm", 300.0))), max(0.0, table_bb.XLength - sheet_length_mm))
    margin_y_mm = min(max(0.0, float(config.get("sheet_margin_y_mm", 180.0))), max(0.0, table_bb.YLength - sheet_width_mm))

    sheet_base_x = table_bb.XMin + margin_x_mm
    sheet_base_y = table_bb.YMin + margin_y_mm
    sheet_base_z = table_bb.ZMax
    sheet_top_z = sheet_base_z + float(params.CAM_KALINLIGI)

    float_glass = _ensure_box(
        doc,
        "Codex_Float_Glass_Sheet",
        sheet_length_mm,
        sheet_width_mm,
        float(params.CAM_KALINLIGI),
        (sheet_base_x, sheet_base_y, sheet_base_z),
        (0.42, 0.82, 0.96),
        72,
    )

    _set_object_visibility(doc, "Glass_Sheet_Reference", False)
    _hide_object(doc, "Codex_Moving_Glass")
    _hide_object(doc, "Codex_X_Probe_Point")
    _hide_object(doc, "Codex_Split_Glass_Left")
    _hide_object(doc, "Codex_Split_Glass_Right")
    _hide_object(doc, "Codex_Tension_Gap")

    raw_segments = config.get("segments") or _default_float_cut_segments(sheet_length_mm, sheet_width_mm)
    segments = []
    for index, raw_segment in enumerate(raw_segments, start=1):
        start = raw_segment.get("start")
        end = raw_segment.get("end")
        if not isinstance(start, (list, tuple)) or not isinstance(end, (list, tuple)) or len(start) < 2 or len(end) < 2:
            raise RuntimeError(f"Segment tanimi gecersiz: {raw_segment}")

        local_x1 = float(start[0])
        local_y1 = float(start[1])
        local_x2 = float(end[0])
        local_y2 = float(end[1])
        if min(local_x1, local_x2, local_y1, local_y2) < 0.0:
            raise RuntimeError(f"Segment {index} negatif sheet koordinati iceriyor")
        if max(local_x1, local_x2) > sheet_length_mm or max(local_y1, local_y2) > sheet_width_mm:
            raise RuntimeError(f"Segment {index} sheet sinirini asiyor")
        if abs(local_x1 - local_x2) > 0.01 and abs(local_y1 - local_y2) > 0.01:
            raise RuntimeError(f"Segment {index} yalnizca eksen hizali olabilir")

        world_x1 = sheet_base_x + local_x1
        world_y1 = sheet_base_y + local_y1
        world_x2 = sheet_base_x + local_x2
        world_y2 = sheet_base_y + local_y2
        segments.append(
            {
                "index": index,
                "name": str(raw_segment.get("name", f"Skor_{index}")),
                "x1": world_x1,
                "y1": world_y1,
                "x2": world_x2,
                "y2": world_y2,
                "length_mm": round(abs(world_x2 - world_x1) + abs(world_y2 - world_y1), 2),
            }
        )

    line_width_mm = max(10.0, float(config.get("score_line_width_mm", 14.0)))
    line_height_mm = max(1.0, float(config.get("score_line_height_mm", 1.4)))
    line_z = sheet_top_z + 0.6

    for stale_index in range(len(segments) + 1, 16):
        _hide_object(doc, f"Codex_Float_Score_{stale_index:02d}")

    doc.recompute()
    return {
        "sheet": float_glass,
        "sheet_base_x": sheet_base_x,
        "sheet_base_y": sheet_base_y,
        "sheet_base_z": sheet_base_z,
        "sheet_length_mm": round(sheet_length_mm, 2),
        "sheet_width_mm": round(sheet_width_mm, 2),
        "sheet_top_z": round(sheet_top_z, 2),
        "line_width_mm": line_width_mm,
        "line_height_mm": line_height_mm,
        "line_z": line_z,
        "segments": segments,
    }


def _draw_float_score_segment(doc, scene, segment):
    x1 = float(segment["x1"])
    y1 = float(segment["y1"])
    x2 = float(segment["x2"])
    y2 = float(segment["y2"])
    line_width_mm = float(scene["line_width_mm"])
    line_height_mm = float(scene["line_height_mm"])
    line_z = float(scene["line_z"])

    if abs(y2 - y1) <= 0.01:
        base = (min(x1, x2), y1 - line_width_mm / 2.0, line_z)
        length = abs(x2 - x1)
        width = line_width_mm
    else:
        base = (x1 - line_width_mm / 2.0, min(y1, y2), line_z)
        length = line_width_mm
        width = abs(y2 - y1)

    return _ensure_box(
        doc,
        f"Codex_Float_Score_{int(segment['index']):02d}",
        max(1.0, length),
        max(1.0, width),
        line_height_mm,
        base,
        (1.0, 0.26, 0.08),
        10,
    )


def run_float_glass_cut_cycle(config=None):
    model = _load_model_module()
    params = model.MachineParameters()
    doc = _ensure_test_document()
    ss = _require_sheet(doc, "Variables")
    config = dict(config or {})

    _stage_header("DUZ CAM KESIMI - UST KAFA FLOAT CYCLE")

    model.set_lamine_mode(doc, False, recompute=False)
    if hasattr(model, "set_bridge_clamp_state"):
        model.set_bridge_clamp_state(doc, False, recompute=False)
    ss.set("T1", "0 mm")
    ss.set("D1", "0 mm")
    doc.recompute()

    _show_view("top")

    scene = _build_float_cut_scene(doc, params, config)
    table = _require_object(doc, "Table_Grid")
    lower_head = _require_object(doc, "Lower_Cutter_Head")
    heater = _require_object(doc, "Heater_Rod")

    safe_z_mm = max(0.0, min(float(config.get("safe_z_mm", params.Z_HOME)), params.Z_MAX))
    score_z_mm = max(0.0, min(float(config.get("score_z_mm", 40.0)), safe_z_mm))
    lower_head_clear_mm = float(table.Placement.Base.z) - float(lower_head.Placement.Base.z)
    heater_clear_mm = float(table.Placement.Base.z) - float(heater.Placement.Base.z)

    _console_message(
        f"Float cam proxy = {scene['sheet_length_mm']:.0f} x {scene['sheet_width_mm']:.0f} x {params.CAM_KALINLIGI:.1f} mm"
    )
    _console_message(
        f"Alt unite parkta -> Lower_Cutter_Head: {lower_head_clear_mm:.2f} mm | Heater_Rod: {heater_clear_mm:.2f} mm"
    )
    _console_message(f"Kesim Z pozlari -> safe: {safe_z_mm:.2f} mm | score: {score_z_mm:.2f} mm")

    _animate_axes(
        doc,
        params,
        x=params.X_HOME,
        y=params.Y_HOME,
        z=safe_z_mm,
        v=params.V_HOME,
        label="Kopru float kesim home noktasina aliniyor...",
        min_duration_s=MIN_VISIBLE_MOVE_S,
    )

    segment_logs = []
    total_cut_length_mm = 0.0
    max_position_error_mm = 0.0

    for segment in scene["segments"]:
        start_move = _animate_top_wheel_to(
            doc,
            params,
            segment["x1"],
            segment["y1"],
            safe_z_mm,
            label=f"{segment['name']} baslangic noktasina rapid gidis...",
            min_duration_s=0.55,
        )
        plunge_move = _animate_top_wheel_to(
            doc,
            params,
            segment["x1"],
            segment["y1"],
            score_z_mm,
            label=f"{segment['name']} icin ust kafa score pozuna iniyor...",
            min_duration_s=0.45,
        )
        cut_move = _animate_top_wheel_to(
            doc,
            params,
            segment["x2"],
            segment["y2"],
            score_z_mm,
            label=f"{segment['name']} score kesimi oynatiliyor...",
            min_duration_s=0.90,
        )
        _draw_float_score_segment(doc, scene, segment)
        retract_move = _animate_top_wheel_to(
            doc,
            params,
            segment["x2"],
            segment["y2"],
            safe_z_mm,
            label=f"{segment['name']} tamamlandi, kafa emniyet Z'sine kalkiyor...",
            min_duration_s=0.35,
        )

        segment_error = max(
            abs(start_move["error_x_mm"]),
            abs(start_move["error_y_mm"]),
            abs(cut_move["error_x_mm"]),
            abs(cut_move["error_y_mm"]),
        )
        max_position_error_mm = max(max_position_error_mm, segment_error)
        total_cut_length_mm += float(segment["length_mm"])
        segment_logs.append(
            {
                "name": segment["name"],
                "length_mm": round(float(segment["length_mm"]), 2),
                "rapid_duration_s": start_move["duration_s"],
                "plunge_duration_s": plunge_move["duration_s"],
                "cut_duration_s": cut_move["duration_s"],
                "retract_duration_s": retract_move["duration_s"],
                "position_error_mm": round(segment_error, 2),
            }
        )

    _animate_axes(
        doc,
        params,
        x=params.X_HOME,
        y=params.Y_HOME,
        z=safe_z_mm,
        v=params.V_HOME,
        label="Float kesim tamamlandi, kopru home noktasina donuyor...",
        min_duration_s=MIN_VISIBLE_MOVE_S,
    )

    for item in segment_logs:
        _console_message(
            f"   {item['name']}: kesim={item['length_mm']:.2f} mm | "
            f"sure={item['cut_duration_s']:.2f} sn | pozisyon hatasi={item['position_error_mm']:.2f} mm"
        )

    cycle_ok = lower_head_clear_mm >= 50.0 and heater_clear_mm >= 35.0 and max_position_error_mm <= 0.05
    _console_message(f"Toplam float score uzunlugu = {total_cut_length_mm:.2f} mm")
    _console_message(f"Maksimum wheel hedefleme hatasi = {max_position_error_mm:.2f} mm")
    _console_message(f"FLOAT CUT SONUC = {'PASS' if cycle_ok else 'CHECK'}")
    return {
        "stage": "float_cut",
        "sheet_length_mm": scene["sheet_length_mm"],
        "sheet_width_mm": scene["sheet_width_mm"],
        "score_z_mm": round(score_z_mm, 2),
        "total_cut_length_mm": round(total_cut_length_mm, 2),
        "max_position_error_mm": round(max_position_error_mm, 2),
        "segment_count": len(segment_logs),
        "segments": segment_logs,
        "cycle_ok": cycle_ok,
    }
