#!/usr/bin/env python3
"""聚焦诊断：点击 vs windowfocus，谁真正拿到输入焦点。"""
import glob
import os
import subprocess
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot, SUBL, ENV, XDOTOOL

SRC = glob.glob('/home/z/cp/*.cpp')[0]
d = Desktop(sublime_dir=None)
subprocess.Popen([SUBL, '-n', SRC], env=ENV,
                 stdout=open('/tmp/sublime_stdout.log', 'w'),
                 stderr=subprocess.STDOUT, preexec_fn=os.setsid)
time.sleep(9)

x = X()
x.arrow_cursor()
w = x.sublime_window()
print('sublime window id:', hex(w.id) if w else None)
if w:
    x.move_resize(w, 0, 0, 1920, 1080)
time.sleep(1.2)


def focus_id():
    r = subprocess.run([XDOTOOL, 'getwindowfocus', '-p'], env=ENV,
                       capture_output=True, text=True)
    return r.stdout.strip()


print('focus at start:', focus_id())
# 方法1：XSetInputFocus
if w:
    x.focus(w)
time.sleep(0.6)
print('focus after x.focus:', focus_id())
# 方法2：xdotool windowfocus
if w:
    subprocess.run([XDOTOOL, 'windowfocus', str(w.id)], env=ENV,
                   capture_output=True)
time.sleep(0.6)
print('focus after xdotool windowfocus:', focus_id())
# 方法3：点击标签页
x.click(150, 33)
time.sleep(0.8)
print('focus after tab click:', focus_id())

# 验证：Ctrl+End 后看状态栏（截图人工确认）
x.key('ctrl+End')
time.sleep(0.8)
shot('/tmp/focus_test.png')

d.close()
print('FOCUS TEST DONE')
