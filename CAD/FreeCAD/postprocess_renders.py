#!/usr/bin/env python3

from __future__ import annotations

import os
from collections import deque

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps, ImageStat


ROOT = "/Users/oktaycit/Projeler/CNCRevizyon/CAD/FreeCAD"
OUT_DIR = os.path.join(ROOT, "renders")


def non_white_mask(img: Image.Image, threshold: int = 244) -> Image.Image:
    rgb = img.convert("RGB")
    mask = Image.new("L", rgb.size, 0)
    src = rgb.load()
    dst = mask.load()
    w, h = rgb.size
    for y in range(h):
        for x in range(w):
            r, g, b = src[x, y]
            if min(r, g, b) < threshold:
                dst[x, y] = 255
    return mask


def largest_component(mask: Image.Image) -> Image.Image:
    w, h = mask.size
    src = mask.load()
    seen = [[False] * w for _ in range(h)]
    best = []

    for y in range(h):
        for x in range(w):
            if seen[y][x] or src[x, y] == 0:
                continue
            q = deque([(x, y)])
            seen[y][x] = True
            pixels = []
            while q:
                cx, cy = q.popleft()
                pixels.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and src[nx, ny] != 0:
                        seen[ny][nx] = True
                        q.append((nx, ny))
            if len(pixels) > len(best):
                best = pixels

    out = Image.new("L", (w, h), 0)
    px = out.load()
    for x, y in best:
        px[x, y] = 255
    return out


def tint_image(img: Image.Image, mask: Image.Image, color: tuple[int, int, int], preserve_color: bool = False) -> Image.Image:
    base = img.convert("RGBA")
    if preserve_color:
        base = ImageEnhance.Color(base).enhance(1.15)
        base = ImageEnhance.Contrast(base).enhance(1.08)
        return base

    tinted = ImageOps.colorize(mask, black=(0, 0, 0), white=color).convert("RGBA")
    shaded = ImageChops.multiply(base.convert("RGB"), tinted.convert("RGB")).convert("RGBA")
    shaded = ImageEnhance.Contrast(shaded).enhance(1.12)
    alpha = Image.new("L", base.size, 0)
    alpha.paste(mask)
    shaded.putalpha(alpha)
    return shaded


def studio_background(size: tuple[int, int]) -> Image.Image:
    w, h = size
    bg = Image.new("RGBA", size, (237, 241, 244, 255))
    px = bg.load()
    for y in range(h):
        t = y / max(1, h - 1)
        r = int(242 - 18 * t)
        g = int(244 - 14 * t)
        b = int(246 - 10 * t)
        for x in range(w):
            px[x, y] = (r, g, b, 255)
    return bg


def add_shadow(canvas: Image.Image, obj_mask: Image.Image, bbox, opacity: int = 82) -> Image.Image:
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = bbox
    width = int((x1 - x0) * 0.88)
    height = max(24, int((y1 - y0) * 0.11))
    ellipse = Image.new("L", (width, height), 0)
    epx = ellipse.load()
    cx = width / 2
    cy = height / 2
    for y in range(height):
        for x in range(width):
            dx = (x - cx) / max(1, width / 2)
            dy = (y - cy) / max(1, height / 2)
            d = dx * dx + dy * dy
            if d <= 1:
                epx[x, y] = int(opacity * (1 - d))
    ellipse = ellipse.filter(ImageFilter.GaussianBlur(radius=max(16, width // 18)))
    ox = (x0 + x1 - width) // 2
    oy = min(canvas.size[1] - height - 10, y1 - height // 3)
    shadow.paste((40, 46, 52, 255), (ox, oy), ellipse)
    return Image.alpha_composite(canvas, shadow)


def fit_and_compose(src_path: str, out_path: str, tint: tuple[int, int, int] | None = None, preserve_color: bool = False):
    src = Image.open(src_path).convert("RGBA")
    mask = largest_component(non_white_mask(src))
    bbox = mask.getbbox()
    if not bbox:
        raise RuntimeError(f"No visible geometry found in {src_path}")

    obj = src.crop(bbox)
    obj_mask = mask.crop(bbox)
    obj = tint_image(obj, obj_mask, tint or (220, 224, 229), preserve_color=preserve_color)

    canvas = studio_background((1600, 1000))
    target_w = int(canvas.size[0] * 0.72)
    target_h = int(canvas.size[1] * 0.70)
    obj.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    obj_mask = obj_mask.resize(obj.size, Image.Resampling.LANCZOS)

    ox = (canvas.size[0] - obj.size[0]) // 2
    oy = int(canvas.size[1] * 0.16 + max(0, (target_h - obj.size[1]) * 0.18))
    placed_box = (ox, oy, ox + obj.size[0], oy + obj.size[1])
    canvas = add_shadow(canvas, obj_mask, placed_box)
    canvas.paste(obj, (ox, oy), obj)

    canvas = ImageEnhance.Sharpness(canvas).enhance(1.12)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)


def main():
    fit_and_compose(
        os.path.join(ROOT, "camera_tests", "rot1.png"),
        os.path.join(OUT_DIR, "machine_presentation.png"),
        preserve_color=True,
    )
    fit_and_compose(
        os.path.join(ROOT, "main_panel_render.png"),
        os.path.join(OUT_DIR, "main_panel_presentation.png"),
        tint=(217, 221, 226),
    )
    fit_and_compose(
        os.path.join(ROOT, "operator_panel_render.png"),
        os.path.join(OUT_DIR, "operator_panel_presentation.png"),
        tint=(94, 102, 112),
    )
    print(f"Presentation renders saved in {OUT_DIR}")


if __name__ == "__main__":
    main()
