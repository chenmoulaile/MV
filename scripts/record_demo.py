#!/usr/bin/env python3
"""Record the real plugin demo on the Xvfb display, in one continuous take.

Sequence: companion POST -> crystal.cpp created -> type solution at the bottom
-> save -> Ctrl+Alt+B judge -> AC cards -> open the detail view of test 1.
Everything runs against the real Sublime Text + Algorithm Competition Assistant.
"""
import json
import os
import signal
import socket
import subprocess
import time

os.environ['DISPLAY'] = ':99'
import pyautogui
pyautogui.FAILSAFE = False
from PIL import Image

OUT = '/tmp/raw_rec.mp4'
ASK_PORT = 19999
SCALE = 1.240           # Sublime content-space -> XTest click space


def ask(req, timeout=6):
    s = socket.create_connection(('127.0.0.1', ASK_PORT), timeout=timeout)
    s.sendall(json.dumps(req).encode('utf-8'))
    s.shutdown(socket.SHUT_WR)
    buf = b''
    while True:
        b = s.recv(65536)
        if not b:
            break
        buf += b
    s.close()
    return json.loads(buf.decode('utf-8')) if buf else None


def shot(path):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f',
                    'x11grab', '-video_size', '1920x1080', '-i', ':99',
                    '-frames:v', '1', '-update', '1', path, '-y'])


def detail_center(path):
    """Center of the TEST-1 详情 button: purple pixels, split into rows by
    y-gaps, topmost row, densest x-run inside it."""
    im = Image.open(path).convert('RGB')
    px = im.load()
    pts = []
    for y in range(74, 150):
        for x in range(1000, 1919):
            r, g, b = px[x, y]
            if abs(r - 123) < 22 and abs(g - 114) < 22 and abs(b - 136) < 22 \
                    and b > g + 8 and r > g + 2:
                pts.append((x, y))
    if len(pts) < 40:
        return None
    pts.sort(key=lambda p: p[1])
    rows = []
    cur = [pts[0]]
    for p in pts[1:]:
        if p[1] - cur[-1][1] <= 8:
            cur.append(p)
        else:
            rows.append(cur)
            cur = [p]
    rows.append(cur)
    row = max(rows[:2], key=len) if len(rows) >= 2 else rows[0]
    row = rows[0]                      # topmost = test 1
    xs = sorted(p[0] for p in row)
    best = None
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[j + 1] - xs[j] <= 4:
            j += 1
        n = j - i + 1
        if best is None or n > best[0]:
            best = (n, xs[i], xs[j])
        i = j + 1
    cx = (best[1] + best[2]) / 2.0
    band = [p[1] for p in row if abs(p[0] - cx) <= (best[2] - best[1]) / 2 + 4]
    cy = sum(band) / len(band)
    return cx, cy


# ---- start recording ----
rec = subprocess.Popen(
    ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
     '-f', 'x11grab', '-framerate', '30', '-video_size', '1920x1080', '-i', ':99',
     '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
     '-pix_fmt', 'yuv420p', OUT],
    stdin=subprocess.PIPE)
time.sleep(1.6)

pyautogui.moveTo(960, 540)
time.sleep(1.4)

# ---- companion POST (browser-extension channel) ----
subprocess.run(['curl', '-s', '--max-time', '8', '-X', 'POST',
                '-H', 'Content-Type: application/json',
                '--data', '@/home/z/my-project/scripts/crystal_companion.json',
                'http://127.0.0.1:12345/'],
               capture_output=True)
for _ in range(30):
    if os.path.exists('/home/z/my-project/workspace/demo/crystal.cpp'):
        break
    time.sleep(0.2)
time.sleep(2.2)

# ---- type the solution at the bottom ----
pyautogui.moveTo(520, 560)
text = open('/home/z/my-project/scripts/solution_code.txt', encoding='utf-8').read()
ask({'cmd': 'type', 'text': text, 'cps': 118})
time.sleep(len(text) / 118 + 3.2)

# ---- save, then judge ----
pyautogui.hotkey('ctrl', 's')
time.sleep(1.4)
pyautogui.hotkey('ctrl', 'alt', 'b')

cards = None
for _ in range(40):
    time.sleep(0.5)
    shot('/tmp/rec_scan.png')
    cards = detail_center('/tmp/rec_scan.png')
    if cards:
        time.sleep(2.8)
        break
print('cards at', cards)

# ---- open the detail view of test 1 ----
if cards:
    cx, cy = cards
    opened = False
    tx, ty = int(cx * SCALE), int(cy * SCALE)
    pyautogui.moveTo(640, 520)
    time.sleep(0.2)
    pyautogui.moveTo(tx, ty, duration=0.55)
    time.sleep(0.25)
    pyautogui.click(tx, ty)
    for _ in range(8):
        time.sleep(0.5)
        names = ask({'cmd': 'views'}).get('names', [])
        if any('- test ' in n and 'detail' in n for n in names):
            opened = True
            break
    print('detail opened:', opened, ask({'cmd': 'views'}).get('names'))

time.sleep(3.5)

# ---- stop recording ----
rec.send_signal(signal.SIGINT)
try:
    rec.wait(20)
except Exception:
    rec.kill()
print('recorded ->', OUT)
