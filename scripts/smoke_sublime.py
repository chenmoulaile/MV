#!/usr/bin/env python3
"""Sublime 冒烟：启动 -> 等待 -> 截图 -> 列窗口。"""
import subprocess
import time
import os

os.environ['DISPLAY'] = ':99'

xvfb = subprocess.Popen(
    ['unshare', '--user', '--map-root-user', 'Xvfb', ':99',
     '-screen', '0', '1920x1080x24'],
    stdout=open('/tmp/xvfb.log', 'w'), stderr=subprocess.STDOUT)
time.sleep(2)

subl = subprocess.Popen(
    ['/home/z/opt/sublime/opt/sublime_text/sublime_text', '-n', '/home/z/cp'],
    stdout=open('/tmp/sublime_stdout.log', 'w'), stderr=subprocess.STDOUT)
time.sleep(7)

r = subprocess.run(
    "ffmpeg -y -f x11grab -video_size 1920x1080 -i :99.0 -frames:v 1 /tmp/smoke_sublime.png",
    shell=True, capture_output=True, text=True)
print('ffmpeg:', r.returncode)

from Xlib import display
d = display.Display(':99')
root = d.screen().root


def walk(win, depth=0):
    try:
        name = win.get_wm_name()
    except Exception:
        name = None
    if name:
        g = win.get_geometry()
        print('WIN %r %dx%d+%d+%d' % (name, g.width, g.height, g.x, g.y))
    for c in win.query_tree().children:
        walk(c, depth + 1)


walk(root)

print('--- sublime stdout ---')
print(open('/tmp/sublime_stdout.log').read()[-500:])
subl.terminate()
xvfb.terminate()
print('DONE')
