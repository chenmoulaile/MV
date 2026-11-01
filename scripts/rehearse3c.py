#!/usr/bin/env python3
"""彩排3c：扩展 Details 页 -> 找到选项入口。"""
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

# 点扩展卡片的 Details（卡片 ~ (498,320) real）
x.click(498, 320)
time.sleep(2.5)
shot('/tmp/r3c_1_details.png')

d.close()
print('R3C DONE')
