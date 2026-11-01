#!/usr/bin/env python3
"""彩排3：端到端 —— Sublime 监听 + Chrome 点扩展 -> 自动建文件。"""
import glob
import os
import sys
import time
sys.path.insert(0, '/home/z/my-project/scripts')
from aca_x import Desktop, X, shot, wait_port

# 清空演示目录
for f in glob.glob('/home/z/cp/*'):
    os.remove(f)

d = Desktop(sublime_dir='/home/z/cp',
            chrome_url='https://www.luogu.com.cn/problem/P17831')
time.sleep(8)
x = X()
x.arrow_cursor()

# Sublime 窗口全屏化（先移出主屏区，最后再raise）
wins = x.find(name_contains='Sublime Text', min_w=300, min_h=200)
if wins:
    x.move_resize(wins[0], 0, 0, 1920, 1080)
    print('sublime resized')

# 等插件监听端口
ok = wait_port(12345, timeout=25)
print('port 12345:', ok)

# 确认 Chrome 在前台
cw = x.find(wm_class_contains='google-chrome', min_w=800, min_h=500)
if cw:
    x.raise_win(cw[0])
    x.focus(cw[0])
time.sleep(3)

# 点击 Competitive Companion 图标
x.click(1769, 62)
time.sleep(4)

# 检查建文件结果
files = sorted(glob.glob('/home/z/cp/*'))
print('created:', files)
tests_files = sorted(glob.glob('/home/z/cp/**/*__tests*', recursive=True))
print('tests:', tests_files)

# 切到 Sublime 看效果
sw = x.find(name_contains='Sublime Text', min_w=800, min_h=500)
if sw:
    x.raise_win(sw[0])
    x.focus(sw[0])
time.sleep(1.5)
shot('/tmp/r3_sublime.png')

# 插件调试日志
log = '/home/z/.config/sublime-text/Data/Log/aca-companion.log'
if os.path.exists(log):
    print('--- companion log tail ---')
    print('\n'.join(open(log).read().splitlines()[-12:]))
else:
    print('no companion debug log')

d.close()
print('R3 DONE')
