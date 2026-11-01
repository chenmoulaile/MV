#!/usr/bin/env python3
"""Full companion pipeline test: Sublime listener + Chrome (extension loaded)
on the Luogu page -> Ctrl+Shift+U -> crystal.cpp should appear."""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
from lib_x import ask, place_window
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'

DEMO = '/home/z/my-project/workspace/demo'
URL = 'https://www.luogu.com.cn/problem/P17831'


def cdp_navigate(url):
    data = json.loads(urllib.request.urlopen(
        'http://127.0.0.1:9222/json', timeout=5).read())
    pages = [t for t in data if t['type'] == 'page']
    from websocket import create_connection
    ws = create_connection(pages[0]['webSocketDebuggerUrl'], timeout=10)
    ws.send(json.dumps({'id': 1, 'method': 'Page.navigate',
                        'params': {'url': url}}))
    time.sleep(2)
    ws.close()


def clean_demo():
    for name in ('crystal.cpp', 'crystal', 'crystal.exe'):
        p = os.path.join(DEMO, name)
        if os.path.exists(p):
            os.remove(p)
    tdir = os.path.join(DEMO, 'tests')
    if os.path.isdir(tdir):
        for f in os.listdir(tdir):
            os.remove(os.path.join(tdir, f))


def focus_chrome():
    ok = place_window('google-chrome')
    if not ok:
        print('WARN: chrome window not found')
    time.sleep(0.6)
    from Xlib import X
    d = lib_x.xdpy()
    d.screen().root.set_input_focus(X.PointerRoot, X.CurrentTime)
    d.sync()
    place_window('google-chrome')
    time.sleep(0.6)
    # hard-verify: click into the page area to force focus
    pyautogui.click(700, 500)
    time.sleep(0.6)
    place_window('google-chrome')
    time.sleep(0.5)


def port_open(port, timeout=1.0):
    import socket as _s
    try:
        c = _s.create_connection(('127.0.0.1', port), timeout=timeout)
        c.close()
        return True
    except Exception:
        return False


def main():
    clean_demo()
    # is Chrome still running with CDP?
    try:
        urllib.request.urlopen('http://127.0.0.1:9222/json', timeout=3)
        print('chrome alive, navigating')
        cdp_navigate(URL)
    except Exception:
        subprocess.Popen(
            ['/tmp/chrome-ext/opt/google/chrome/google-chrome',
             '--user-data-dir=/tmp/chrome-demo', '--no-first-run',
             '--no-default-browser-check', '--disable-crash-reporter',
             '--hide-crash-restore-bubble', '--disable-session-crashed-bubble',
             '--remote-debugging-port=9222', '--window-position=0,0',
             '--window-size=1920,1080', '--start-maximized', URL],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(12)
    place_window('google-chrome')
    time.sleep(1.5)

    # Sublime with listener
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
    print('sublime up; listener 12345 open:', port_open(12345))

    focus_chrome()
    print('sending Ctrl+Shift+U')
    pyautogui.hotkey('ctrl', 'shift', 'u')
    for i in range(40):
        time.sleep(0.5)
        if os.path.exists(os.path.join(DEMO, 'crystal.cpp')):
            print('crystal.cpp created after %.1fs' % (i * 0.5))
            break
    else:
        print('FAILED: no file')
        return 1
    time.sleep(2.5)
    head = open(os.path.join(DEMO, 'crystal.cpp'), encoding='utf-8').read()
    print('--- file head ---')
    print(head[:240])
    print('tests stored:',
          os.path.exists(os.path.join(DEMO, 'tests', 'crystal.cpp__tests')))
    print('views:', lib_x.view_names())
    return 0


if __name__ == '__main__':
    sys.exit(main())
