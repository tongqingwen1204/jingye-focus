#!/usr/bin/env python3
"""把资源里的预览图导成文档用素材（带圆角，供 preview.html 直接引用）。"""
import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "app", "src", "main", "res")
OUT = os.path.join(ROOT, "docs", "assets")


def rounded(src, dst, radius_ratio=0.125):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    r = int(min(w, h) * radius_ratio)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    out.save(dst, optimize=True)
    print("wrote", os.path.relpath(dst, ROOT), out.size)


def main():
    os.makedirs(OUT, exist_ok=True)
    pairs = [
        ("drawable-nodpi/widget_preview_1x1_focus.webp", "widget-1x1-focus-light.png"),
        ("drawable-night-nodpi/widget_preview_1x1_focus.webp", "widget-1x1-focus-dark.png"),
        ("drawable-nodpi/widget_preview_1x1_usage.webp", "widget-1x1-usage-light.png"),
        ("drawable-night-nodpi/widget_preview_1x1_usage.webp", "widget-1x1-usage-dark.png"),
        ("drawable-nodpi/widget_preview_2x2.webp", "widget-2x2-light.png"),
        ("drawable-night-nodpi/widget_preview_2x2.webp", "widget-2x2-dark.png"),
        ("drawable-nodpi/widget_preview_4x2.webp", "widget-4x2-light.png"),
        ("drawable-night-nodpi/widget_preview_4x2.webp", "widget-4x2-dark.png"),
    ]
    for src, name in pairs:
        rounded(os.path.join(RES, src), os.path.join(OUT, name))

    # 磁贴剪影（xxxhdpi 96px 原图，预览页按 44px 显示）
    for src, name in (("drawable-xxxhdpi/ic_tile_focus.png", "tile-light.png"),
                      ("drawable-night-xxxhdpi/ic_tile_focus.png", "tile-dark.png")):
        Image.open(os.path.join(RES, src)).convert("RGBA").save(
            os.path.join(OUT, name), optimize=True)
        print("wrote docs/assets/" + name)

    # 桌面图标（圆形遮罩的实际观感）
    icon = Image.open(os.path.join(ROOT, "assets", "icon-circle-preview.png")).convert("RGBA")
    icon.resize((256, 256), Image.LANCZOS).save(os.path.join(OUT, "app-icon.png"), optimize=True)
    print("wrote docs/assets/app-icon.png")


if __name__ == "__main__":
    main()
