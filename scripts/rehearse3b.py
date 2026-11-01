#!/usr/bin/env python3
"""彩排3b：打开 CC 扩展选项页，把端口改为 12345。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

EXT_ID = 'ijdklpjmcnabepikdghpmhblnfbnocon'

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

x.key('ctrl+l'); time.sleep(0.4)
x.type_text('chrome-extension://%s/options.html' % EXT_ID)
x.key('Return')
time.sleep(4)
shot('/tmp/r3b_1_options.png')

d.close()
print('R3B DONE')
