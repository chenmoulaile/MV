#!/usr/bin/env python3
"""正式 A 卷：Chrome 抓题场景（Sublime 后台监听）。

流程：洛谷页面已加载 -> 缓慢滚动浏览 -> 回顶 -> 移到 CC 图标 -> 点击发送。
输出：download/footage/A_chrome.mp4 + A_cursor.csv
"""
import os
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import (Desktop, X, Recorder, CursorLogger, mark, reset_state, sweep, survivors_report)

OUT = '/home/z/my-project/download/footage'
os.makedirs(OUT, exist_ok=True)
LUOGU = 'https://www.luogu.com.cn/problem/P17831'

reset_state()
d = Desktop(sublime_dir='/home/z/cp', chrome_url=LUOGU)
time.sleep(10)
x = X()
x.arrow_cursor()

# Sublime 全屏放后台（保证监听就绪、点击后能收到）
w = x.sublime_window()
if w:
    x.move_resize(w, 0, 0, 1920, 1080)
time.sleep(1)

# Chrome 明确全屏并聚焦
cw = x.chrome_window()
if cw:
    x.move_resize(cw, 0, 0, 1920, 1080)
    x.raise_win(cw)
    x.focus(cw)
time.sleep(12)   # 等洛谷完全渲染（CC 防护 + 前端渲染）

# 关掉可能出现的翻译气泡
x.key('Escape')
time.sleep(0.8)
x.move(960, 560)
time.sleep(0.5)

# ---------------- 开拍 ----------------
rec = Recorder(OUT + '/A_chrome.mp4')
cur = CursorLogger(OUT + '/A_cursor.csv')
rec.start()
mark('REC START')

# 1. 缓慢滚动浏览题面
for i in range(3):
    x.scroll(960, 560, clicks=1)
    time.sleep(0.8)
mark('scrolled')
time.sleep(1.2)

# 2. 回到顶部
x.key('ctrl+Home')
time.sleep(1.2)
mark('back to top')

# 3. 光标滑向 CC 扩展图标（后期聚焦点）
for px, py in ((1300, 200), (1500, 130), (1650, 90), (1769, 62)):
    x.move(px, py)
    time.sleep(0.3)
time.sleep(0.8)
mark('hover CC icon')

# 4. 点击发送，绿光反馈停留
x.click(1769, 62)
time.sleep(4.5)
mark('clicked CC')

# ---------------- 收机 ----------------
rec.stop(); cur.stop()
d.close()
sweep()
survivors_report()
print('TAKE A DONE', flush=True)
import subprocess as _sp
open('/tmp/ps_full.txt','w').write(_sp.run(['ps','-eo','pid,ppid,pgid,sess,stat,cmd'],capture_output=True,text=True).stdout)

# 强制退出，跳过解释器收尾
import os as _os
_os._exit(0)
