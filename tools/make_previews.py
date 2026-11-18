#!/usr/bin/env python3
"""生成小部件预览图（小米规范：1080p 下圆角 55px、安全区 42px）。

预览按 2x 密度出图，1dp = 2px：
  1x1  110dp -> 220 x 220
  2x2  220dp -> 440 x 440
  4x2  474dp -> 948 x 440

这里是把「布局 XML 里写了什么」按像素重画一遍，尺寸公式与布局一一对应，
所以预览里的留白、字号、图形比例就是实机上的比例。
资源里交付直角图，由桌面统一裁圆角；docs/ 下的圆角版本仅供预览页使用。
"""
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "app", "src", "main", "res")
NODPI = os.path.join(RES, "drawable-nodpi")
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
D = 2  # 每 dp 的像素数

LIGHT = dict(
    card=(255, 255, 255, 255),
    hero_top=(243, 249, 255, 255),
    hero_bottom=(195, 220, 246, 255),
    glow=(255, 255, 255, 153),
    tile=(241, 248, 255, 255),
    title=(26, 28, 34, 255),
    sub=(26, 28, 34, 102),
    chip=(26, 28, 34, 13),
    accent=(60, 130, 214, 255),
)
DARK = dict(
    card=(26, 33, 48, 255),
    hero_top=(38, 51, 63, 255),
    hero_bottom=(21, 30, 40, 255),
    glow=(255, 255, 255, 31),
    tile=(26, 36, 49, 255),
    title=(241, 244, 247, 255),
    sub=(241, 244, 247, 102),
    chip=(255, 255, 255, 20),
    accent=(143, 194, 245, 255),
)


def dp(v):
    return int(round(v * D))


def flat(card, overlay):
    """半透明色先按 alpha 混到卡片底色上：预览图最后存的是不透明 RGB，
    直接画 (0,0,0,13) 会被当成纯黑。"""
    a = overlay[3] / 255.0
    return tuple(int(round(overlay[i] * a + card[i] * (1 - a))) for i in range(3))


def save(img, out):
    """预览图存 WebP：渐变底用 PNG 要 44KB（不量化）或压出一段段色带（量化），
    WebP q92 只要 7KB 且看不出损失。"""
    img.convert("RGB").save(out, "WEBP", quality=92, method=6)


def hero_card(w, h, palette, pad):
    """渐变底 + 头部后方的柔光，与 bg_widget_hero.xml 的两层一一对应。"""
    top = np.array(palette["hero_top"][:3], np.float32)
    bot = np.array(palette["hero_bottom"][:3], np.float32)
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    rgb = top * (1 - t) + bot * t
    rgb = np.repeat(rgb, w, axis=1)

    cx, cy = w * 0.5, h * 0.26
    radius = 74 * D
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    a = np.clip(1 - r / radius, 0, 1) * (palette["glow"][3] / 255.0)
    rgb = rgb * (1 - a[..., None]) + 255 * a[..., None]

    img = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    return img, ImageDraw.Draw(img)


def clock(d, cx, cy, r, palette):
    """与 ic_clock.xml 一致：实心圆盘 + 指针（指针用卡片底色）。"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=palette["accent"])
    w = max(2, int(r * 0.22))
    d.line([cx, cy, cx, cy - r * 0.62], fill=palette["tile"], width=w)
    d.line([cx, cy, cx + r * 0.50, cy + r * 0.34], fill=palette["tile"], width=w)


def fit(img, box_w, box_h):
    """等价于 ImageView 的 fitCenter：等比缩到框内，居中摆放。"""
    ratio = min(box_w / img.width, box_h / img.height)
    return img.resize((max(1, int(img.width * ratio)), max(1, int(img.height * ratio))),
                      Image.LANCZOS)


def line_h(sp):
    """includeFontPadding=false 时的一行高度，CJK 约 1.08 倍字号。"""
    return dp(sp * 1.08)


def preview_1x1(palette, figure, kind, out):
    size = dp(110)
    pad = dp(12)
    margin = dp(0 if kind == "focus" else 2)
    img = Image.new("RGBA", (size, size), palette["tile"])

    box = size - pad * 2 - margin * 2
    if kind == "focus":
        art = fit(figure, box, box)
        img.alpha_composite(art, ((size - art.width) // 2, (size - art.height) // 2))
    else:
        r = box // 2
        d = ImageDraw.Draw(img)
        clock(d, size // 2, size // 2, r - dp(1), palette)
    save(img, out)


def preview_2x2(palette, figure, out):
    """2×2 只放人像、不放字：安全区内等比撑满，卡片多大就画多大。"""
    w = h = dp(220)
    pad = dp(16)
    img, d = hero_card(w, h, palette, pad)

    art = fit(figure, w - pad * 2, h - pad * 2)
    img.alpha_composite(art, ((w - art.width) // 2, (h - art.height) // 2))
    save(img, out)


def preview_4x2(palette, figure, out):
    w, h = dp(474), dp(220)
    pad = dp(16)
    inner_h = h - pad * 2
    img = Image.new("RGBA", (w, h), palette["card"])
    d = ImageDraw.Draw(img)

    # 左：专注热区（weight 1）——人像占 34% 宽、高度撑满，文案竖排在右侧
    left_w = w - pad * 2 - dp(8) - dp(104)
    d.rounded_rectangle([pad, pad, pad + left_w, pad + inner_h],
                        radius=dp(12), fill=flat(palette["card"], palette["chip"]))
    inner_pad = dp(12)
    art_w = int((left_w - inner_pad * 2 - dp(12)) * 0.40 / 1.40)
    art = fit(figure, art_w, inner_h - inner_pad * 2)
    img.alpha_composite(art, (pad + inner_pad, pad + (inner_h - art.height) // 2))

    tx = pad + inner_pad + art_w + dp(12)
    f_title = ImageFont.truetype(FONT_BOLD, dp(22))
    f_sub = ImageFont.truetype(FONT_REG, dp(11))
    stack = line_h(22) + dp(4) + line_h(11)
    ty = pad + int((inner_h - stack) // 2)
    d.text((tx, ty), "专注", font=f_title, fill=palette["title"])
    d.text((tx, ty + line_h(22) + dp(4)), "点一下 · 进入专注模式", font=f_sub,
           fill=palette["sub"])

    # 右：屏幕用时热区（固定 104dp），内容居中
    rx = w - pad - dp(104)
    d.rounded_rectangle([rx, pad, rx + dp(104), pad + inner_h],
                        radius=dp(12), fill=flat(palette["card"], palette["chip"]))
    r = dp(17)
    f_small = ImageFont.truetype(FONT_BOLD, dp(13))
    f_tiny = ImageFont.truetype(FONT_REG, dp(11))
    stack2 = r * 2 + dp(8) + line_h(13) + dp(3) + line_h(11)
    top2 = pad + int((inner_h - stack2) // 2)
    cx = rx + dp(52)
    clock(d, cx, top2 + r, r, palette)
    d.text((cx, top2 + r * 2 + dp(8)), "屏幕时间", font=f_small,
           fill=palette["title"], anchor="mt")
    d.text((cx, top2 + r * 2 + dp(8) + line_h(13) + dp(3)), "今日用时",
           font=f_tiny, fill=palette["sub"], anchor="mt")
    save(img, out)


def main():
    plain = os.path.join(RES, "drawable-nodpi")
    night = os.path.join(RES, "drawable-night-nodpi")
    os.makedirs(plain, exist_ok=True)
    os.makedirs(night, exist_ok=True)

    figure = Image.open(os.path.join(plain, "mark_figure.png")).convert("RGBA")

    for palette, out_dir in ((LIGHT, plain), (DARK, night)):
        preview_1x1(palette, figure, "focus", os.path.join(out_dir, "widget_preview_1x1_focus.webp"))
        preview_1x1(palette, figure, "usage", os.path.join(out_dir, "widget_preview_1x1_usage.webp"))
        preview_2x2(palette, figure, os.path.join(out_dir, "widget_preview_2x2.webp"))
        preview_4x2(palette, figure, os.path.join(out_dir, "widget_preview_4x2.webp"))

    print("previews written")


if __name__ == "__main__":
    main()
