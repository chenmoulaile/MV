#!/usr/bin/env python3
"""彩排2b：UI 安装扩展 -> 打开洛谷 -> 截图验证。"""
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot

d = Desktop(sublime_dir=None, chrome_url='about:blank')
time.sleep(6)
x = X()
x.arrow_cursor()
time.sleep(2)

# 1. 打开扩展页
x.key('ctrl+l'); time.sleep(0.4)
x.type_text('chrome://extensions'); x.key('Return')
time.sleep(3)

# 2. 开发者模式开关
x.click(1893, 114); time.sleep(2)
shot('/tmp/r2b_1_devmode.png')

# 3. Load unpacked（左上第一颗按钮，预期 ~ (95,168)）
x.click(95, 168); time.sleep(2.5)
shot('/tmp/r2b_2_dialog.png')

# 4. GTK 对话框：Ctrl+L 输路径
x.key('ctrl+l'); time.sleep(0.5)
x.type_text('/home/z/opt/ext/cc')
time.sleep(0.5)
x.key('Return')
time.sleep(3)
shot('/tmp/r2b_3_installed.png')

# 5. 去洛谷
x.key('ctrl+l'); time.sleep(0.4)
x.type_text('https://www.luogu.com.cn/problem/P17831')
x.key('Return')
time.sleep(14)
shot('/tmp/r2b_4_luogu.png')

d.close()
print('R2B DONE')
