#!/usr/bin/env python3
"""大肥猴 — 把精灵图白底抠成透明"""
import os
from PIL import Image

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'sprites')
DST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'sprites_transparent')

os.makedirs(DST, exist_ok=True)

def make_transparent(src, dst):
    img = Image.open(src).convert('RGBA')
    pixels = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            # 近白色 -> 透明
            if r > 240 and g > 240 and b > 240:
                pixels[x, y] = (r, g, b, 0)
            # 近白色边缘羽化
            elif r > 220 and g > 220 and b > 220:
                alpha = int(255 - (min(r, g, b) - 220) * 8.5)
                alpha = max(0, min(255, alpha))
                pixels[x, y] = (r, g, b, alpha)
    img.save(dst)
    return dst

count = 0
for name in sorted(os.listdir(SRC)):
    if not name.endswith('.png'):
        continue
    src = os.path.join(SRC, name)
    dst = os.path.join(DST, name)
    make_transparent(src, dst)
    count += 1
    print(f'OK {name}')

print(f'\n完成! {count} 个精灵图已透明化 -> {DST}')

