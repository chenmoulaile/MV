#!/usr/bin/env python3
"""Deterministic companion send: fresh single Chrome (Luogu) + fresh single
Sublime, verified focus, then Ctrl+Shift+U."""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
from lib_x import ask, shot
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'

from Xlib import X

DEMO = '/home/z/my-project/workspace/demo'
URL = 'https://www.luogu.com.cn/problem/P17831'


def kill_all():
    for pat in ('sublime_text', 'opt/google/chrome'):
        subprocess.run(['pkill', '-9', '-f', pat], capture_output=True)
    time.sleep(2)


def focused_class():
    d = lib_x.xdpy()
    f = d.get_input_focus()
    try:
        return (f.focus.id, f.focus.get_wm_class())
    except Exception:
        return (None, None)


def chrome_win():
    best = None
    for w in lib_x._walk(lib_x.xdpy().screen().root):
        try:
            cls = w.get_wm_class()
            g = w.get_geometry()
        except Exception:
            continue
        if cls and 'google-chrome' in (cls[0] or '').lower() + (cls[1] or '').lower() \
                and g.width > 1000 and g.height > 800:
            attrs = w.get_attributes()
            if attrs.map_state == 2:
                best = w
    return best


def main():
    kill_all()
    for name in ('crystal.cpp', 'crystal', 'crystal.exe'):
        p = os.path.join(DEMO, name)
        if os.path.exists(p):
            os.remove(p)
    tdir = os.path.join(DEMO, 'tests')
    if os.path.isdir(tdir):
        for f in os.listdir(tdir):
            os.remove(os.path.join(tdir, f))

    # Sublime first
    subprocess.Popen(['/home/z/my-project/apps/sublime_text/sublime_text',
                      '--detached', DEMO],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 40:
        try:
            if ask({'cmd': 'ping'}, timeout=2).get('ok'):
                break
        except Exception:
            pass
        time.sleep(0.8)
    time.sleep(2.5)
    print('sublime up')

    # Chrome directly on the problem page
    subprocess.Popen(
        ['/tmp/chrome-ext/opt/google/chrome/google-chrome',
         '--user-data-dir=/tmp/chrome-demo', '--no-first-run',
         '--no-default-browser-check', '--disable-crash-reporter',
         '--hide-crash-restore-bubble', '--disable-session-crashed-bubble',
         '--window-position=0,0', '--window-size=1920,1080',
         '--start-maximized', URL],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(13)
    w = chrome_win()
    if w is None:
        print('no chrome window!')
        return 1
    w.configure(stack_mode=X.Above)
    w.set_input_focus(X.RevertToParent, X.CurrentTime)
    lib_x.xdpy().sync()
    time.sleep(1.5)
    print('focused:', focused_class())
    # content painted?
    shot('/tmp/_pre_send.png')
    import run_take
    print('mostly_white:', run_take._mostly_white('/tmp/_pre_send.png'))

    print('sending Ctrl+Shift+U')
    pyautogui.hotkey('ctrl', 'shift', 'u')
    for i in range(40):
        time.sleep(0.5)
        if os.path.exists(os.path.join(DEMO, 'crystal.cpp')):
            print('crystal.cpp created after %.1fs' % (i * 0.5))
            break
    else:
        print('FAILED: no file')
        shot('/tmp/_post_fail.png')
        return 1
    time.sleep(2.5)
    print(open(os.path.join(DEMO, 'crystal.cpp'), encoding='utf-8')
          .read()[:220])
    print('tests stored:',
          os.path.exists(os.path.join(DEMO, 'tests', 'crystal.cpp__tests')))
    print('views:', lib_x.view_names())
    return 0


if __name__ == '__main__':
    sys.exit(main())
