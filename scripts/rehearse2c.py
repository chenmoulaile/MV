#!/usr/bin/env python3
"""彩排2c：重试安装扩展 —— 输路径后点 Open 按钮，不走 Enter。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

# 1. 扩展页
x.key('ctrl+l'); time.sleep(0.4)
x.type_text('chrome://extensions'); x.key('Return')
time.sleep(3)

# 2. Load unpacked
x.click(83, 169); time.sleep(2.5)

# 3. GTK：Ctrl+L 输入路径 -> 直接点 Open
x.key('ctrl+l'); time.sleep(0.6)
x.type_text('/home/z/opt/ext/cc')
time.sleep(1.2)
x.click(1070, 797)  # Open
time.sleep(3)
shot('/tmp/r2c_1_installed.png')

# 4. 洛谷
x.key('ctrl+l'); time.sleep(0.4)
x.type_text('https://www.luogu.com.cn/problem/P17831')
x.key('Return')
time.sleep(14)
shot('/tmp/r2c_2_luogu.png')

d.close()
print('R2C DONE')
