#!/usr/bin/env python3
"""Rehearse the full companion pipeline: Sublime listener + Chrome extension
sends P17831 on Ctrl+Shift+U -> crystal.cpp appears with header + samples."""
import os
import subprocess
import sys
import time

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
from lib_x import ask, place_window
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'

DEMO = '/home/z/my-project/workspace/demo'
CHROME = '/tmp/chrome-ext/opt/google/chrome/google-chrome'
URL = 'https://www.luogu.com.cn/problem/P17831'


def kill_all():
    for pat in ('sublime_text', 'opt/google/chrome', 'chrome-demo'):
        subprocess.run(['pkill', '-9', '-f', pat], capture_output=True)
    time.sleep(1.5)


def main():
    kill_all()
    # clean slate
    for name in ('crystal.cpp', 'crystal', 'crystal.exe'):
        p = os.path.join(DEMO, name)
        if os.path.exists(p):
            os.remove(p)
    tdir = os.path.join(DEMO, 'tests')
    if os.path.isdir(tdir):
        for f in os.listdir(tdir):
            os.remove(os.path.join(tdir, f))

    # Sublime first: its companion listener must be up before the click
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
    print('sublime bridge up')
    time.sleep(2.0)  # companion listener start

    # Chrome with the extension loaded, straight onto the problem page
    subprocess.Popen([CHROME, '--user-data-dir=/tmp/chrome-demo',
                      '--no-first-run', '--no-default-browser-check',
                      '--disable-crash-reporter', '--hide-crash-restore-bubble',
                      '--disable-session-crashed-bubble',
                      '--load-extension=/tmp/ccext',
                      '--window-position=0,0', '--window-size=1920,1080',
                      '--start-maximized', URL],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    place_window('google-chrome')
    time.sleep(1)

    print('pressing Ctrl+Shift+U ...')
    pyautogui.hotkey('ctrl', 'shift', 'u')
    for i in range(30):
        time.sleep(0.5)
        if os.path.exists(os.path.join(DEMO, 'crystal.cpp')):
            print('crystal.cpp created after %.1fs' % (i * 0.5))
            break
    else:
        print('FAILED: no crystal.cpp')
        return 1
    time.sleep(2.5)
    print('content head:')
    print(open(os.path.join(DEMO, 'crystal.cpp')).read()[:260])
    print('tests file exists:',
          os.path.exists(os.path.join(DEMO, 'tests', 'crystal.cpp__tests')))
    print('views:', lib_x.view_names())
    return 0


if __name__ == '__main__':
    sys.exit(main())
