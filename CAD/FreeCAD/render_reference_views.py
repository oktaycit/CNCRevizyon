#!/usr/bin/env python3
"""
Generate presentation-style renders from the existing STEP exports.

This is not a physically-based renderer; it uses tessellated STEP geometry and
material-inspired colors to create more realistic presentation views than raw
technical screenshots. The goal is repeatable, fast visual communication.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

import Part


ROOT = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD"
STEP_ROOT = os.path.join(ROOT, "07_Exports", "STEP")
OUT_ROOT = os.path.join(ROOT, "renders")


@dataclass(frozen=True)
class Material:
    name: str
    color: str
    edge: str
    alpha: float = 1.0


MATERIALS = {
    "light_painted_steel": Material("Light Painted Steel", "#D9DDE2", "#7D8790"),
    "dark_painted_steel": Material("Dark Painted Steel", "#5E6670", "#40474F"),
    "anthracite": Material("Anthracite Matte", "#2B2F34", "#171A1D"),
    "satin_metal": Material("Satin Metal", "#9FA6AD", "#727981"),
    "galvanized": Material("Galvanized Metal", "#B8BEC4", "#858D96"),
    "black_plastic": Material("Black Plastic", "#1A1C1F", "#090B0C"),
    "display_glass": Material("Display Glass", "#11161C", "#3C5669", 0.96),
}


def _rgba(hex_color: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4)) + (alpha,)


def _load_shape(path: str):
    shape = Part.Shape()
    shape.read(path)
    return shape


def _poly_collection(polys, material: Material, linewidth: float = 0.10):
    return Poly3DCollection(
        polys,
        facecolor=_rgba(material.color, material.alpha),
        edgecolor=_rgba(material.edge, min(1.0, material.alpha)),
        linewidths=linewidth,
        alpha=material.alpha,
    )


def _solid_polys(solid, tolerance: float):
    verts, faces = solid.tessellate(tolerance)
    return [[verts[i] for i in face] for face in faces if len(face) >= 3], verts


def _set_axes_equal(ax, mins, maxs):
    span = max(maxs[i] - mins[i] for i in range(3))
    centers = [(maxs[i] + mins[i]) / 2 for i in range(3)]
    ax.set_xlim(centers[0] - span / 2, centers[0] + span / 2)
    ax.set_ylim(centers[1] - span / 2, centers[1] + span / 2)
    ax.set_zlim(centers[2] - span / 2, centers[2] + span / 2)


def _style_scene(ax, elev: float, azim: float):
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    ax.set_facecolor("#EEF1F4")


def _save_fig(fig, out_path: str):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.tight_layout(pad=0)
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0.04, facecolor=fig.get_facecolor())
    plt.close(fig)


def _overall_bounds(shape):
    box = shape.BoundBox
    mins = (box.XMin, box.YMin, box.ZMin)
    maxs = (box.XMax, box.YMax, box.ZMax)
    return mins, maxs, box


def classify_machine_solid(solid, overall):
    box = solid.BoundBox
    total = overall
    cx = (box.XMin + box.XMax) / 2
    cy = (box.YMin + box.YMax) / 2
    cz = (box.ZMin + box.ZMax) / 2

    if box.ZLength < total.ZLength * 0.05 and box.XLength > total.XLength * 0.35 and box.YLength > total.YLength * 0.35:
        return MATERIALS["anthracite"]

    if cz < total.ZMin + total.ZLength * 0.14 and box.ZLength > total.ZLength * 0.06:
        return MATERIALS["dark_painted_steel"]

    if box.ZLength > total.ZLength * 0.18 and box.XLength < total.XLength * 0.06 and box.YLength < total.YLength * 0.18:
        return MATERIALS["black_plastic"]

    if box.XLength > total.XLength * 0.12 and box.YLength < total.YLength * 0.04:
        return MATERIALS["satin_metal"]

    if box.XLength < total.XLength * 0.03 and box.YLength < total.YLength * 0.03 and box.ZLength < total.ZLength * 0.08:
        return MATERIALS["black_plastic"]

    if box.ZLength < total.ZLength * 0.1 and (cx < total.XMin + total.XLength * 0.15 or cx > total.XMax - total.XLength * 0.15):
        return MATERIALS["dark_painted_steel"]

    return MATERIALS["light_painted_steel"]


def classify_operator_panel_solid(solid, overall):
    box = solid.BoundBox
    cy = (box.YMin + box.YMax) / 2
    cz = (box.ZMin + box.ZMax) / 2
    high_zone = overall.ZMin + overall.ZLength * 0.62
    front_zone = overall.YMin + overall.YLength * 0.18

    if cz < overall.ZMin + overall.ZLength * 0.20:
        return MATERIALS["anthracite"]

    if box.ZLength > overall.ZLength * 0.38 and box.XLength < overall.XLength * 0.22:
        return MATERIALS["anthracite"]

    if cz > high_zone and cy < front_zone and box.ZLength < overall.ZLength * 0.18:
        return MATERIALS["display_glass"]

    if box.XLength < overall.XLength * 0.08 and box.YLength < overall.YLength * 0.08 and box.ZLength < overall.ZLength * 0.08:
        return MATERIALS["black_plastic"]

    if cz > high_zone:
        return MATERIALS["dark_painted_steel"]

    return MATERIALS["dark_painted_steel"]


def classify_main_panel_solid(solid, overall):
    box = solid.BoundBox
    if box.ZMin < overall.ZMin + overall.ZLength * 0.12 and box.ZLength < overall.ZLength * 0.14:
        return MATERIALS["dark_painted_steel"]
    if box.XLength > overall.XLength * 0.70 and box.YLength > overall.YLength * 0.50 and box.ZLength < overall.ZLength * 0.08:
        return MATERIALS["galvanized"]
    if box.XLength < overall.XLength * 0.10 and box.YLength < overall.YLength * 0.10:
        return MATERIALS["black_plastic"]
    return MATERIALS["light_painted_steel"]


def render_shape(shape, out_path: str, classifier, elev: float, azim: float, tolerance: float):
    mins, maxs, overall = _overall_bounds(shape)
    fig = plt.figure(figsize=(13, 9), dpi=180)
    fig.patch.set_facecolor("#EEF1F4")
    ax = fig.add_subplot(111, projection="3d")

    for solid in shape.Solids:
        polys, verts = _solid_polys(solid, tolerance)
        if not polys:
            continue
        material = classifier(solid, overall)
        coll = _poly_collection(polys, material)
        ax.add_collection3d(coll)

    _set_axes_equal(ax, mins, maxs)
    ax.set_box_aspect((1.8, 1.0, 0.45 if overall.ZLength < overall.XLength * 0.35 else 0.9))
    _style_scene(ax, elev=elev, azim=azim)
    _save_fig(fig, out_path)


def render_machine_views():
    shape = _load_shape(os.path.join(STEP_ROOT, "Assembly", "Full_Machine_Assembly.stp"))
    render_shape(
        shape,
        os.path.join(OUT_ROOT, "machine_hero.png"),
        classify_machine_solid,
        elev=23,
        azim=-54,
        tolerance=18.0,
    )
    render_shape(
        shape,
        os.path.join(OUT_ROOT, "machine_operator_side.png"),
        classify_machine_solid,
        elev=18,
        azim=118,
        tolerance=18.0,
    )


def render_main_panel():
    shape = _load_shape(os.path.join(STEP_ROOT, "Electronics", "Control_Panel_Box.stp"))
    render_shape(
        shape,
        os.path.join(OUT_ROOT, "main_panel_hero.png"),
        classify_main_panel_solid,
        elev=17,
        azim=-43,
        tolerance=6.0,
    )


def render_operator_panel():
    shape = _load_shape(os.path.join(STEP_ROOT, "Electronics", "Operator_Terminal_Complete.stp"))
    render_shape(
        shape,
        os.path.join(OUT_ROOT, "operator_panel_hero.png"),
        classify_operator_panel_solid,
        elev=18,
        azim=-58,
        tolerance=6.0,
    )


def main():
    render_machine_views()
    render_main_panel()
    render_operator_panel()
    print(f"Renders written to {OUT_ROOT}")


if __name__ == "__main__":
    main()
