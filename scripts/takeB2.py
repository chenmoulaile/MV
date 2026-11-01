#!/usr/bin/env python3
"""正式 B2 卷：切换英文界面 + 重跑判题（中英对比素材）。

前置：B 卷已粘贴代码。输出 B2_sublime_en.mp4 + B2_cursor.csv
"""
import os
import subprocess
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import (Desktop, X, Recorder, CursorLogger, mark, demo_file,
                   SUBL, ENV)

OUT = '/home/z/my-project/download/footage'
os.makedirs(OUT, exist_ok=True)

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
rec = Recorder(OUT + '/B2_sublime_en.mp4')
cur = CursorLogger(OUT + '/B2_cursor.csv')
rec.start()
mark('REC START')
time.sleep(2.0)

# 1. 命令面板 -> Switch to English
x.key('ctrl+shift+p')
time.sleep(1.0)
x.type_text('Switch to English')
time.sleep(1.2)
mark('palette typed')
x.key('Return')        # 面板第一条结果已高亮，Enter 执行
time.sleep(2.5)
mark('switched to en')

# 2. 重跑（编译已缓存，秒出）
x.key('ctrl+alt+b')
time.sleep(5.0)
mark('rerun done')
time.sleep(3.0)

# 3. 详情（英文界面）
x.click(1604, 98)
time.sleep(2.5)
mark('detail open en')
time.sleep(3.0)

# 4. 回源码
x.click(150, 33)
time.sleep(1.5)
mark('back to source')
time.sleep(1.2)

# ---------------- 收机 ----------------
rec.stop(); cur.stop()
d.close()
from aca_x import sweep
sweep()
print('TAKE B2 DONE')
