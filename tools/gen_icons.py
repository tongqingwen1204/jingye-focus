#!/usr/bin/env python3
"""生成矢量图标（位图类图标由 tools/prepare_art.py 从插画抠出）。

目前只有「屏幕用时」的时钟：实心圆盘 + 白色指针，和插画的扁平风格一致，
圆盘用强调色、指针用卡片底色，深浅色模式都自动成立。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAWABLE = os.path.join(ROOT, "app", "src", "main", "res", "drawable")

CLOCK = """<?xml version="1.0" encoding="utf-8"?>
<!-- 由 tools/gen_icons.py 生成，请勿手改 -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="@color/accent"
        android:pathData="M12,2.6a9.4,9.4 0 1,0 0.01,0z" />
    <path
        android:fillColor="#00000000"
        android:pathData="M12,6.4L12,12.2L15.6,14.3"
        android:strokeColor="@color/widget_bg"
        android:strokeLineCap="round"
        android:strokeLineJoin="round"
        android:strokeWidth="1.9" />
</vector>
"""


def main():
    path = os.path.join(DRAWABLE, "ic_clock.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(CLOCK)
    print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
