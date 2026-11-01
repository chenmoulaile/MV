#!/usr/bin/env python3
"""彩排6：B 卷干跑 —— Sublime 全屏打开文件 -> 粘贴 -> 运行 -> 详情。"""
import glob
import subprocess
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot, SUBL, ENV

SRC = glob.glob('/home/z/cp/*.cpp')[0]

d = Desktop(sublime_dir=None)
subprocess.Popen([SUBL, '-n', SRC], env=ENV,
                 stdout=open('/tmp/sublime_stdout.log', 'w'),
                 stderr=subprocess.STDOUT)
time.sleep(8)

x = X()
x.arrow_cursor()
w = x.sublime_window()
print('sublime win:', w)
if w:
    x.move_resize(w, 0, 0, 1920, 1080)
time.sleep(0.5)
shot('/tmp/r6_0_open.png')

# 聚焦并粘贴
x.click(600, 400)
time.sleep(0.6)
x.key('ctrl+End'); time.sleep(0.4)
code = open('/home/z/my-project/workspace/demo_code.cpp').read()
x.set_clipboard(code); time.sleep(0.8)
x.key('ctrl+v'); time.sleep(1.5)
shot('/tmp/r6_1_pasted.png')

# 运行
t0 = time.time()
x.key('ctrl+alt+b')
time.sleep(2.5)
shot('/tmp/r6_2_compiling.png')
time.sleep(6)
shot('/tmp/r6_3_ac.png')

# 点测试1的“详情”
x.click(708, 66)
time.sleep(2)
shot('/tmp/r6_4_detail.png')

d.close()
print('R6 DONE %.1fs' % (time.time() - t0))
