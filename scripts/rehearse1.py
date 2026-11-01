#!/usr/bin/env python3
"""彩排1：Chrome 打开扩展页与洛谷页面，截图供坐标标定。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()

# 打开 chrome://extensions
x.key('ctrl+l')
time.sleep(0.4)
x.type_text('chrome://extensions')
x.key('Return')
time.sleep(3)
shot('/tmp/r1_extensions.png')

# 打开洛谷题目页
x.key('ctrl+l')
time.sleep(0.4)
x.type_text('https://www.luogu.com.cn/problem/P17831')
x.key('Return')
time.sleep(12)
shot('/tmp/r1_luogu.png')
time.sleep(3)
shot('/tmp/r1_luogu2.png')

# 检查 --load-extension 是否生效（窗口标题/扩展页内容看截图）
print('checking extension via load-extension flag result in screenshots')

d.close()
print('R1 DONE')
