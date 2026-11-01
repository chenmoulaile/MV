#!/usr/bin/env python3
"""正式 B 卷：Sublime 中文场景 —— 粘贴代码 + 运行判题 + 详情。

前置：A 卷已抓题（~/cp 有文件+样例）。输出 B_sublime_zh.mp4 + B_cursor.csv
"""
import os
import subprocess
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import (Desktop, X, Recorder, CursorLogger, mark, demo_file,
                   trim_to_header, SUBL, ENV)

OUT = '/home/z/my-project/download/footage'
os.makedirs(OUT, exist_ok=True)

trim_to_header()
SRC = demo_file()
print('file:', SRC)

os.environ["PYTHONUNBUFFERED"] = "1"
d = Desktop(sublime_dir=SRC, plugin_lang="zh")
time.sleep(9)

x = X()
x.arrow_cursor()
w = x.sublime_window()
if w:
    x.move_resize(w, 0, 0, 1920, 1080)
    x.focus(w)
time.sleep(1.5)

# ---------------- 开拍 ----------------
rec = Recorder(OUT + '/B_sublime_zh.mp4')
cur = CursorLogger(OUT + '/B_cursor.csv')
rec.start()
mark('REC START')
time.sleep(2.0)

# 1. 聚焦编辑器，跳到最底
x.click(620, 400)
time.sleep(0.8)
x.key('ctrl+End')
time.sleep(1.0)
mark('at bottom')

# 2. 粘贴代码
code = open('/home/z/my-project/workspace/demo_code.cpp').read()
x.set_clipboard(code)
time.sleep(1.0)
x.key('ctrl+v')
time.sleep(2.0)
mark('pasted')

# 3. 运行判题
x.key('ctrl+alt+b')
time.sleep(2.5)
mark('compiling')
time.sleep(6.0)
mark('AC cards shown')
time.sleep(3.0)

# 4. 测试 1 详情
x.click(1604, 98)
time.sleep(2.5)
mark('detail open')
time.sleep(3.0)

# 5. 回到源码页
x.click(150, 33)
time.sleep(1.5)
mark('back to source')
time.sleep(1.5)

# ---------------- 收机 ----------------
rec.stop(); cur.stop()
d.close()
from aca_x import sweep
sweep()
print('TAKE B DONE')
