#!/usr/bin/env python3
"""彩排3f：右键 CC 图标 -> 菜单截图。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

# 右键 CC 图标
x.click(1769, 62, btn=3)
time.sleep(1.5)
shot('/tmp/r3f_1_ctxmenu.png')

d.close()
print('R3F DONE')
