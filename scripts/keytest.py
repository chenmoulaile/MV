#!/usr/bin/env python3
"""受控键盘实验：每步验证 X 焦点 + 键盘是否真正生效。"""
import glob
import os
import subprocess
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot, SUBL, ENV, XDOTOOL

f = glob.glob('/home/z/cp/*.cpp')[0]
lines = open(f).readlines()
open(f, 'w').writelines(lines[:4])

d = Desktop(sublime_dir=f)
time.sleep(9)
x = X()
x.arrow_cursor()

wins = x.find(wm_class_contains='sublime_text', min_w=400, min_h=300)
print('candidates:', [hex(w.id) for w in wins], flush=True)
w = wins[0]
x.move_resize(w, 0, 0, 1920, 1080)
time.sleep(0.8)


def fid():
    fo = x.d.get_input_focus().focus
    return hex(fo.id) if hasattr(fo, 'id') else str(fo)


print('F0 start:', fid(), flush=True)
x.focus(w)
print('F1 after x.focus:', fid(), flush=True)

# 实验A：直接发 Ctrl+End + 打字
x.key('ctrl+End')
time.sleep(0.4)
x.type_text('ZZ1')
time.sleep(0.6)
shot('/tmp/kt_A.png')
print('F2 after keys:', fid(), flush=True)

# 实验B：点击标签栏再打字
x.click(400, 33)
time.sleep(0.6)
print('F3 after tabbar click:', fid(), flush=True)
x.type_text('ZZ2')
time.sleep(0.6)
shot('/tmp/kt_B.png')

# 实验C：点击编辑器中央再打字
x.click(960, 500)
time.sleep(0.6)
print('F4 after editor click:', fid(), flush=True)
x.type_text('ZZ3')
time.sleep(0.6)
shot('/tmp/kt_C.png')

d.close()
print('KEYTEST DONE', flush=True)
