#!/usr/bin/env python3
"""彩排2a：chrome://extensions 打开开发者模式。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='chrome://extensions')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

# 点 Developer mode 开关
x.click(1893, 114)
time.sleep(2)
shot('/tmp/r2a_devmode.png')

d.close()
print('R2A DONE')
