#!/usr/bin/env python3
"""Ensure extension installed -> graceful quit -> relaunch -> verify -> send."""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
from lib_x import ask, shot
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'
from Xlib import X
from websocket import create_connection

DEMO = '/home/z/my-project/workspace/demo'
URL = 'https://www.luogu.com.cn/problem/P17831'
EXT = '/tmp/ccext'
CHROME = '/tmp/chrome-ext/opt/google/chrome/google-chrome'


def cdp_eval(expr, want='chrome://extensions', timeout=15, wait=True,
             port=9222):
    for _ in range(20):
        try:
            data = json.loads(urllib.request.urlopen(
                'http://127.0.0.1:%d/json' % port, timeout=4).read())
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError('no CDP')
    page = [t for t in data if t['type'] == 'page' and want in t.get('url', '')]
    if not page:
        pages = [t for t in data if t['type'] == 'page']
        ws = create_connection(pages[0]['webSocketDebuggerUrl'], timeout=10)
        ws.send(json.dumps({'id': 1, 'method': 'Page.navigate',
                            'params': {'url': want}}))
        time.sleep(3)
        try:
            ws.close()
        except Exception:
            pass
        data = json.loads(urllib.request.urlopen(
            'http://127.0.0.1:%d/json' % port, timeout=4).read())
        page = [t for t in data if t['type'] == 'page'
                and want in t.get('url', '')]
    ws = create_connection(page[0]['webSocketDebuggerUrl'], timeout=timeout)
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate',
                        'params': {'expression': expr, 'awaitPromise': True,
                                   'returnByValue': True}}))
    if not wait:
        time.sleep(0.8)
        ws.close()
        return None
    while True:
        msg = json.loads(ws.recv())
        if msg.get('id') == 1:
            ws.close()
            res = msg['result']
            if 'exceptionDetails' in res:
                raise RuntimeError(str(res['exceptionDetails'])[:300])
            return res.get('result', {}).get('value')


def ext_present():
    try:
        info = cdp_eval(
            "(new Promise(r => chrome.developerPrivate.getExtensionsInfo("
            "es => r(es.map(e => [e.name, e.state])))))")
        return info and 'Companion' in str(info)
    except Exception as e:
        print('ext check err:', e)
        return False


def launch(url='chrome://extensions'):
    subprocess.Popen(
        [CHROME, '--user-data-dir=/tmp/chrome-demo', '--no-first-run',
         '--no-default-browser-check', '--disable-crash-reporter',
         '--hide-crash-restore-bubble', '--disable-session-crashed-bubble',
         '--remote-debugging-port=9222', '--window-position=0,0',
         '--window-size=1920,1080', '--start-maximized', url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(11)


def graceful_quit():
    try:
        data = json.loads(urllib.request.urlopen(
            'http://127.0.0.1:9222/json/version', timeout=4).read())
        ws = create_connection(data['webSocketDebuggerUrl'], timeout=8)
        ws.send(json.dumps({'id': 1, 'method': 'Browser.close'}))
        time.sleep(2)
        ws.close()
    except Exception as e:
        print('graceful quit err:', e)
    time.sleep(2)


def install():
    cdp_eval("(async () => { const cfg = await new Promise(r => "
             "chrome.developerPrivate.getProfileConfiguration(r));"
             " if (!cfg.inDeveloperMode) await new Promise(r => "
             "chrome.developerPrivate.updateProfileConfiguration("
             "{inDeveloperMode: true}, r)); return 'dev-ok'; })()")
    cdp_eval("window.__lu = new Promise(r => "
             "chrome.developerPrivate.loadUnpacked(r)); 'fired'", wait=False)
    time.sleep(3)
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.7)
    pyautogui.typewrite(EXT, interval=0.03)
    time.sleep(0.4)
    pyautogui.click(1072, 798)   # Open button
    time.sleep(4)


def main():
    subprocess.run(['pkill', '-9', '-f', 'opt/google/chrome'],
                   capture_output=True)
    time.sleep(2)
    launch('chrome://extensions')
    if not ext_present():
        print('installing extension...')
        install()
        print('after install:', cdp_eval(
            "(new Promise(r => chrome.developerPrivate.getExtensionsInfo("
            "es => r(es.map(e => [e.name, e.state])))))"))
    else:
        print('extension already present')
    graceful_quit()
    time.sleep(2)
    launch(URL)                  # relaunch on the problem page
    print('ext after clean restart:', ext_present())
    if not ext_present():
        print('EXT LOST AFTER RESTART')
        return 1

    # sublime listener
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

    w = None
    for win in lib_x._walk(lib_x.xdpy().screen().root):
        try:
            cls = win.get_wm_class()
            g = win.get_geometry()
        except Exception:
            continue
        if cls and 'google-chrome' in ((cls[0] or '') + (cls[1] or '')).lower() \
                and g.width > 1000:
            if win.get_attributes().map_state == 2:
                w = win
    if w is None:
        print('no chrome window')
        return 1
    w.configure(stack_mode=X.Above)
    w.set_input_focus(X.RevertToParent, X.CurrentTime)
    lib_x.xdpy().sync()
    time.sleep(1.2)
    print('sending Ctrl+Shift+U')
    pyautogui.hotkey('ctrl', 'shift', 'u')
    for i in range(40):
        time.sleep(0.5)
        if os.path.exists(os.path.join(DEMO, 'crystal.cpp')):
            print('crystal.cpp created after %.1fs' % (i * 0.5))
            break
    else:
        print('no file')
        return 1
    time.sleep(2.5)
    print(open(os.path.join(DEMO, 'crystal.cpp'), encoding='utf-8').read()[:230])
    print('tests stored:',
          os.path.exists(os.path.join(DEMO, 'tests', 'crystal.cpp__tests')))
    print('views:', lib_x.view_names())
    return 0


if __name__ == '__main__':
    sys.exit(main())
