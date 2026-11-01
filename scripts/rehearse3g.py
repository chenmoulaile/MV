#!/usr/bin/env python3
"""彩排3g：右键 -> Options -> 修改端口为 12345。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

x.click(1769, 62, btn=3)
time.sleep(1.2)
x.click(1719, 275)  # Options
time.sleep(3)
shot('/tmp/r3g_1_optionspage.png')

d.close()
print('R3G DONE')
