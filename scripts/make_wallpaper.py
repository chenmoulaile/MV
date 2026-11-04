#!/usr/bin/env python3
"""Generate a clean dark-blue gradient wallpaper (BA-ish palette)."""
from PIL import Image, ImageDraw, ImageFilter
import math, random

W, H = 1920, 1080
img = Image.new('RGB', (W, H))
d = ImageDraw.Draw(img)

# vertical gradient: deep navy -> soft blue-grey
top = (16, 24, 44)
bottom = (36, 62, 106)
for y in range(H):
    t = y / H
    r = int(top[0] + (bottom[0]-top[0])*t)
    g = int(top[1] + (bottom[1]-top[1])*t)
    b = int(top[2] + (bottom[2]-top[2])*t)
    d.line([(0, y), (W, y)], fill=(r, g, b))

# subtle diagonal light beams
beam = Image.new('RGBA', (W, H), (0, 0, 0, 0))
bd = ImageDraw.Draw(beam)
random.seed(7)
for i in range(5):
    x0 = random.randint(200, 1700)
    w = random.randint(120, 320)
    alpha = random.randint(8, 16)
    bd.polygon([(x0, 0), (x0+w, 0), (x0-w+300, H), (x0-w+300-w, H)], fill=(120, 170, 235, alpha))
beam = beam.filter(ImageFilter.GaussianBlur(60))
img = Image.alpha_composite(img.convert('RGBA'), beam)

# faint vignette
vig = Image.new('L', (W, H), 0)
vd = ImageDraw.Draw(vig)
vd.ellipse([-400, -300, W+400, H+300], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(180))
dark = Image.new('RGBA', (W, H), (5, 8, 18, 110))
dark.putalpha(Image.eval(vig, lambda p: 110 - int(p * 110 / 255)))
img = Image.alpha_composite(img, dark)

img.convert('RGB').save('/home/z/my-project/workspace/demo/wallpaper.png', 'PNG')
print('wallpaper saved')
