#!/usr/bin/env python3
"""单次调用内：启动 Xvfb -> 等待 -> 启动 Chrome -> 加载页面 -> 截图。"""
import subprocess
import time
import os

os.environ['DISPLAY'] = ':99'

def run(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)

# 1. Xvfb（userns 内成为 root，才能建 socket）
xvfb = subprocess.Popen(
    ['unshare', '--user', '--map-root-user', 'Xvfb', ':99',
     '-screen', '0', '1920x1080x24'],
    stdout=open('/tmp/xvfb.log', 'w'), stderr=subprocess.STDOUT)
time.sleep(2)

# 2. Chrome
chrome = subprocess.Popen(
    ['/home/z/opt/chrome/opt/google/chrome/chrome',
     '--user-data-dir=/home/z/chrome-profile',
     '--no-first-run', '--no-default-browser-check',
     '--disable-session-crashed-bubble',
     '--window-position=0,0', '--window-size=1920,1080',
     'https://example.com'],
    stdout=open('/tmp/chrome.log', 'w'), stderr=subprocess.STDOUT)
time.sleep(8)

# 3. 截图
r = run("ffmpeg -y -f x11grab -video_size 1920x1080 -i :99.0 -frames:v 1 /tmp/smoke_chrome.png")
print('ffmpeg:', r.returncode, r.stderr[-200:] if r.returncode else 'ok')

# 4. 列出窗口（python-xlib）
from Xlib import display
d = display.Display(':99')
root = d.screen().root
from Xlib import X


def walk(win, depth=0):
    name = None
    try:
        name = win.get_wm_name()
    except Exception:
        pass
    if name:
        g = win.get_geometry()
        print('WIN %r %dx%d+%d+%d depth=%d' % (name, g.width, g.height, g.x, g.y, depth))
    tree = win.query_tree()
    for c in tree.children:
        walk(c, depth + 1)


walk(root)

chrome.terminate()
xvfb.terminate()
print('DONE')
