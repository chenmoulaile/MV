#!/usr/bin/env python3
"""彩排3e：详情页滚动 -> 扩展程序选项。"""
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
x.type_text('chrome://extensions/?id=ijdklpjmcnabepikdghpmhblnfbnocon')
x.key('Return')
time.sleep(3)

# 滚动找“扩展程序选项”
x.scroll(790, 600, clicks=4)
time.sleep(1)
shot('/tmp/r3e_1_scrolled.png')

d.close()
print('R3E DONE')
