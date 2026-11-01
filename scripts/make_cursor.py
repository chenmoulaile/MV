#!/usr/bin/env python3
"""Generate a custom X cursor (yellow translucent halo + big white arrow) and
install it as the user default cursor theme. Pure-Python Xcursor writer."""
import math
import os
import struct

SIZE = 64
HALO_R = 27
TIP = (7, 3)  # hotspot (arrow tip)

px = [[(0, 0, 0, 0)] * SIZE for _ in range(SIZE)]

# --- halo: translucent yellow disc with soft edge -------------------------
cx, cy = TIP[0] + 16, TIP[1] + 15
for y in range(SIZE):
    for x in range(SIZE):
        d = math.hypot(x - cx, y - cy)
        if d <= HALO_R - 2.2:
            a = 118
        elif d <= HALO_R:
            a = int(118 * (HALO_R - d) / 2.2)
        else:
            a = 0
        if a:
            px[y][x] = (255, 224, 50, a)  # r g b a

# --- arrow (scaled DMZ-like shape), white fill + black outline ------------
# outline polygon (unit design ~ 16x24, scaled x1.9)
SC = 1.95
outline = [
    (0, 0), (0, 16.5), (3.8, 13.2), (6.6, 20.5), (9.4, 19.4), (6.6, 12.4),
    (11.5, 12.4),
]
def T(p):
    return (TIP[0] + p[0] * SC, TIP[1] + p[1] * SC)

outline = [T(p) for p in outline]

def inside(x, y, poly):
    n = len(poly)
    j = n - 1
    odd = False
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi):
            odd = not odd
        j = i
    return odd

for y in range(SIZE):
    for x in range(SIZE):
        if inside(x + 0.5, y + 0.5, outline):
            # distance to polygon edge for antialiasing-ish outline
            px[y][x] = (20, 20, 20, 255)

# inner white arrow (shrunk by 1.2px via smaller scale around tip)
SC2 = 1.95
inner = [
    (1.15, 1.7), (1.15, 14.6), (4.35, 11.8), (7.0, 18.6), (9.0, 17.8),
    (6.4, 11.2), (10.3, 11.2),
]
inner = [T(p) for p in inner]
for y in range(SIZE):
    for x in range(SIZE):
        if inside(x + 0.5, y + 0.5, inner):
            px[y][x] = (250, 250, 250, 255)

# pack Xcursor
def pack_image(nominal):
    data = struct.pack('<IIIIIIIII', 36, 0xFFFD0002, nominal, 1,
                       SIZE, SIZE, TIP[0], TIP[1], 50)
    for y in range(SIZE):
        for x in range(SIZE):
            r, g, b, a = px[y][x]
            if a:
                r = r * a // 255
                g = g * a // 255
                b = b * a // 255
            data += struct.pack('<I', (a << 24) | (r << 16) | (g << 8) | b)
    return data

ntoc = 1
toc_end = 16 + 12 * ntoc          # where the first image chunk starts
img = pack_image(SIZE)
# file header: magic('Xcur' as LE uint32), header size (16), version, ntoc
blob = struct.pack('<IIII', 0x72756358, 16, 65536, ntoc)
blob += struct.pack('<III', 0xFFFD0002, SIZE, toc_end)
blob += img

out = os.path.expanduser('~/.icons/default/cursors')
os.makedirs(out, exist_ok=True)
with open(os.path.join(out, 'left_ptr'), 'wb') as f:
    f.write(blob)
idx = os.path.expanduser('~/.icons/default/index.theme')
os.makedirs(os.path.dirname(idx), exist_ok=True)
with open(idx, 'w') as f:
    f.write('[Icon Theme]\nName=Default\nComment=Demo halo cursor\n\n'
            '[X]\nInherits=\n')
# also alias other common names so text/copy cursors keep working
for alias in ('left_arrow', 'top_left_arrow', 'arrow', 'default', 'grabbing',
              'hand2', 'xterm', 'text', 'ibeam', 'cross', 'pointing_hand',
              'pointer', 'right_ptr', 'sb_h_double_arrow', 'sb_v_double_arrow',
              'watch', 'left_side', 'right_side', 'top_side', 'bottom_side',
              'bottom_left_corner', 'bottom_right_corner', 'top_left_corner',
              'top_right_corner'):
    with open(os.path.join(out, alias), 'wb') as f:
        f.write(blob)
print('cursor written:', out)
print('size:', os.path.getsize(os.path.join(out, 'left_ptr')), 'bytes')
