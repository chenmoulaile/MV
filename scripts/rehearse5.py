#!/usr/bin/env python3
"""彩排5：Sublime 打开已抓取的文件 -> 底部粘贴代码 -> Ctrl+Alt+B 运行。"""
import glob
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

SRC = glob.glob('/home/z/cp/*.cpp')[0]

d = Desktop(sublime_dir=None)
time.sleep(1.5)
import subprocess
from aca_x import SUBL, ENV
subprocess.Popen([SUBL, '-n', SRC], env=ENV,
                 stdout=open('/tmp/sublime_stdout.log', 'w'),
                 stderr=subprocess.STDOUT)
time.sleep(8)

x = X()
x.arrow_cursor()
sw = x.find(name_contains='Sublime Text', min_w=300, min_h=200)
print('windows:', len(sw))
if sw:
    x.move_resize(sw[0], 0, 0, 1920, 1080)
time.sleep(1)

# 点击编辑器中央聚焦，Ctrl+End 到末尾
x.click(700, 400)
time.sleep(0.8)
x.key('ctrl+End')
time.sleep(0.5)

# 粘贴代码（aca_set_clip -> Ctrl+V）
code = open('/home/z/my-project/workspace/demo_code.cpp').read()
x.set_clipboard(code)
time.sleep(1)
x.key('ctrl+v')
time.sleep(1.5)
shot('/tmp/r5_1_pasted.png')

# 运行判题
x.key('ctrl+alt+b')
time.sleep(10)
shot('/tmp/r5_2_run.png')
time.sleep(3)
shot('/tmp/r5_3_run2.png')

d.close()
print('R5 DONE')
