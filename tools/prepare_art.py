#!/usr/bin/env python3
"""把用户新提供的抠图（干净版）处理成图标资源。

与上一版不同：这次的原图已经是矢量化过的扁平插画，没有 JPEG 块效应、没有投影，
所以不再需要去噪/反锐化，处理链改成「精修边缘」四步：

  1) 近白判背景（脸和手的米色 d≈38，阈值 6 足够安全），取最大连通域，
     顺手把左上角的工具栏残片、右下角的水印（都是孤立小块）丢掉；
  2) 颜色去污：抠图软件留了一圈半透明白边，直接保留会在彩色背景上泛出白边。
     先把「实心内部」的颜色按最近邻向外扩散，边缘像素改用这份扩散色；
  3) 软 alpha：用与白色的距离算出覆盖率，边缘 2px 内平滑过渡，不出现锯齿；
  4) 收边 1px（去掉残留的白色描边）+ 单像素羽化。

产出：
  assets/figure-cutout.png                       透明抠图（母版）
  assets/icon-circle-preview.png                 圆形遮罩下的观感（文档用）
  res/drawable-nodpi/mark_figure.png             组件/图标用主图（512）
  res/drawable-nodpi/ic_launcher_foreground.png  自适应图标前景（432）
  res/drawable-nodpi/ic_mono.png                 单色剪影（432，主题图标）
  res/drawable-{mdpi..xxxhdpi}/ic_tile_focus.png 磁贴剪影（深墨）
  res/drawable-night-*/ic_tile_focus.png         磁贴剪影（纯白）
"""
import os

import cv2
import numpy as np
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
SOURCE = os.path.join(ASSETS, "source", "user_cutout.png")
RES = os.path.join(ROOT, "app", "src", "main", "res")
NODPI = os.path.join(RES, "drawable-nodpi")


def load_source():
    bgr = cv2.imread(SOURCE, cv2.IMREAD_COLOR)
    if bgr is None:
        raise SystemExit(f"找不到源图：{SOURCE}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def extract(rgb):
    """返回 (rgba, bbox)。bbox 为人物外接框。"""
    h, w = rgb.shape[:2]
    a = rgb.astype(np.int16)
    dist = 255 - a.min(axis=2)          # 与纯白的距离（取最暗通道，脸/手也能被保住）

    # 1) 主体掩膜：留最大连通域，孤立残片（工具栏、水印）自动出局
    seed = (dist > 6).astype(np.uint8)
    seed = cv2.morphologyEx(seed, cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    num, labels, stats, _ = cv2.connectedComponentsWithStats(seed, 8)
    if num < 2:
        raise SystemExit("没找到主体")
    main = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    mask = (labels == main).astype(np.uint8)

    # 补内部空洞（脖子与衣领之间的浅色块、手与腿之间的缝隙）
    ff = mask.copy()
    ff_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(ff, ff_mask, (0, 0), 1)
    holes = ((ff == 0) & (mask == 0)).astype(np.uint8)
    holes = cv2.morphologyEx(holes, cv2.MORPH_OPEN,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    mask = np.clip(mask + holes, 0, 1).astype(np.uint8)

    # 2) 颜色去污：实心内部向外扩散，边缘不再沿用「与白底混合」的颜色
    core = (dist > 26).astype(np.uint8) * mask
    core = cv2.erode(core, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    _, near = cv2.distanceTransformWithLabels(
        1 - core, cv2.DIST_L2, 5, labelType=cv2.DIST_LABEL_PIXEL)
    # near: 每个像素最近的 core 像素编号（含 0 号虚背景），先建立编号→坐标的映射
    ys, xs = np.nonzero(core)
    lut_y = np.zeros(near.max() + 1, np.int32)
    lut_x = np.zeros(near.max() + 1, np.int32)
    lut_y[near[ys, xs]] = ys
    lut_x[near[ys, xs]] = xs
    clean = np.dstack([rgb[..., i][lut_y[near], lut_x[near]] for i in range(3)])

    # 3) 软 alpha：距离越大覆盖率越高，边缘 2px 内做线性过渡
    cov = np.clip(dist / 22.0, 0.0, 1.0)
    cov = np.where(mask > 0, cov, 0)
    cov = cv2.GaussianBlur(cov, (0, 0), 0.9)

    # 4) 收边：去掉半透明白描边（原抠图自带约 2px 白边）
    cov = np.clip((cov - 0.16) / 0.84, 0, 1)

    rgba = np.dstack([clean, (cov * 255).astype(np.uint8)])
    ys, xs = np.nonzero(cov > 0.06)
    return rgba.astype(np.uint8), (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)


def trim_square(rgba, box, margin_ratio=0.03):
    x0, y0, x1, y1 = box
    mx = int((x1 - x0) * margin_ratio)
    my = int((y1 - y0) * margin_ratio)
    h, w = rgba.shape[:2]
    x0, y0 = max(0, x0 - mx), max(0, y0 - my)
    x1, y1 = min(w, x1 + mx), min(h, y1 + my)
    sub = rgba[y0:y1, x0:x1]

    side = max(sub.shape[0], sub.shape[1])
    canvas = np.zeros((side, side, 4), dtype=np.uint8)
    oy = (side - sub.shape[0]) // 2
    ox = (side - sub.shape[1]) // 2
    canvas[oy:oy + sub.shape[0], ox:ox + sub.shape[1]] = sub
    return canvas


def save_png(arr_or_img, path, size, colors=256):
    """扁平插画也需要一条平滑的肤色/衣褶渐变，所以量化只用中位切分 + 保留原始 alpha。

    上一版用 FASTOCTREE 直接压 RGBA，调色板被大片透明区吃光，胸口出现横向色带；
    中位切分作用在 RGB 上、alpha 单独保留，512 下肉眼无色阶，体积也只多 40KB。
    """
    im = arr_or_img if isinstance(arr_or_img, Image.Image) else Image.fromarray(arr_or_img, "RGBA")
    im = im.resize((size, size), Image.LANCZOS)
    alpha = im.getchannel("A")
    rgb = im.convert("RGB").quantize(colors=colors, method=Image.MEDIANCUT,
                                     dither=Image.NONE).convert("RGB")
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    out.save(path, optimize=True)


def silhouette(rgba, color=(255, 255, 255), threshold=110):
    """单色剪影：alpha 二值化后填单色。

    小尺寸下软 alpha 会让整张图发灰、糊成一团，所以剪影走硬边。
    """
    a = rgba[..., 3]
    solid = np.where(a > threshold, 255, 0).astype(np.uint8)
    out = np.zeros((*a.shape, 4), dtype=np.uint8)
    out[..., :3] = color
    out[..., 3] = solid
    return out


def launcher_foreground(rgba, size=432, ratio=0.62):
    """108dp 画布，内容压在 66dp 安全区内（约 60%），四周留给遮罩。"""
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    target_h = int(size * ratio)

    fig = Image.fromarray(rgba, "RGBA")
    ratio = target_h / fig.height
    fig = fig.resize((max(1, int(fig.width * ratio)), target_h), Image.LANCZOS)

    cy = int(size * 0.5)
    canvas.alpha_composite(fig, ((size - fig.width) // 2, cy - target_h // 2))
    return canvas


def main():
    os.makedirs(ASSETS, exist_ok=True)
    os.makedirs(NODPI, exist_ok=True)

    rgba, box = extract(load_source())
    figure = trim_square(rgba, box)
    Image.fromarray(figure, "RGBA").save(os.path.join(ASSETS, "figure-cutout.png"))
    print("wrote assets/figure-cutout.png", figure.shape[1], "见方")

    save_png(figure, os.path.join(NODPI, "mark_figure.png"), 512)
    save_png(silhouette(figure), os.path.join(NODPI, "ic_mono.png"), 512, colors=8)

    # 磁贴图标按密度出图，系统按 24dp 取对应像素，避免缩放发虚；
    # 浅色界面用深墨剪影，深色界面用白剪影
    tile_colors = (("drawable", (70, 78, 90)), ("drawable-night", (255, 255, 255)))
    for folder, color in tile_colors:
        for bucket, px in (("mdpi", 24), ("hdpi", 36), ("xhdpi", 48),
                           ("xxhdpi", 72), ("xxxhdpi", 96)):
            d = os.path.join(RES, f"{folder}-{bucket}")
            os.makedirs(d, exist_ok=True)
            save_png(silhouette(figure, color), os.path.join(d, "ic_tile_focus.png"), px, colors=8)

    # 桌面图标的圆形观感：前景按自适应图标的安全区缩到 60% 再压圆
    fg = launcher_foreground(figure, 512)
    bg = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    ImageDraw.Draw(bg).rectangle([0, 0, 512, 512], fill=(226, 240, 253, 255))
    bg.alpha_composite(fg)
    mask = Image.new("L", (512, 512), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 511, 511], fill=255)
    out = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    out.paste(bg, (0, 0), mask)
    out.save(os.path.join(ASSETS, "icon-circle-preview.png"))
    print("wrote assets/icon-circle-preview.png")


if __name__ == "__main__":
    main()
