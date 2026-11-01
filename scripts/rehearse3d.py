#!/usr/bin/env python3
"""彩排3d：Details -> 扩展程序选项 -> 截图选项页。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

x.key('ctrl+l'); time.sleep(0.4)
x.type_text('chrome://extensions'); x.key('Return')
time.sleep(3)

x.click(453, 474)  # Details
time.sleep(2.5)
shot('/tmp/r3d_1_details.png')

# 详情页里“扩展程序选项”链接位置未知，先截图确认
d.close()
print('R3D DONE')
