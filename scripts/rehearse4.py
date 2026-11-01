#!/usr/bin/env python3
"""彩排4：设置端口 12345 -> 端到端（点扩展 -> Sublime 建文件）。"""
import glob
import os
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot, wait_port

for f in glob.glob('/home/z/cp/*'):
    os.remove(f)

d = Desktop(sublime_dir='/home/z/cp',
            chrome_url='https://www.luogu.com.cn/problem/P17831')
time.sleep(9)
x = X()
x.arrow_cursor()

sw = x.find(name_contains='Sublime Text', min_w=300, min_h=200)
if sw:
    x.move_resize(sw[0], 0, 0, 1920, 1080)
print('wait port:', wait_port(12345, timeout=25))

# 打开扩展 Options（右键 -> Options）
cw = x.find(wm_class_contains='google-chrome', min_w=800, min_h=500)
if cw:
    x.raise_win(cw[0]); x.focus(cw[0])
time.sleep(2)
x.click(1769, 62, btn=3); time.sleep(1.2)
x.click(1719, 275)  # Options
time.sleep(2.5)
x.click(965, 416)   # Custom ports 输入框
time.sleep(0.5)
x.type_text('12345')
time.sleep(1.5)
shot('/tmp/r4_1_port.png')

# 关掉弹窗
x.click(930, 231)   # 弹窗右上角 ×
time.sleep(1)

# 回到洛谷页（Options 是嵌在 details 页的，关掉后回列表页；直接开新标签去洛谷）
x.key('ctrl+t'); time.sleep(1)
x.type_text('https://www.luogu.com.cn/problem/P17831')
x.key('Return')
time.sleep(13)

# 点击 CC 图标发送
x.click(1769, 62)
time.sleep(4)

files = sorted(glob.glob('/home/z/cp/*'))
print('created:', files)

# 切到 Sublime 看运行面板
sw = x.find(name_contains='Sublime Text', min_w=800, min_h=500)
if sw:
    x.raise_win(sw[0]); x.focus(sw[0])
time.sleep(1.5)
shot('/tmp/r4_2_sublime.png')

log = '/home/z/.config/sublime-text/Data/Log/aca-companion.log'
if os.path.exists(log):
    print('--- companion log tail ---')
    print('\n'.join(open(log).read().splitlines()[-15:]))
else:
    print('no companion debug log')

d.close()
print('R4 DONE')
