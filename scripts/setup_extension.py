#!/usr/bin/env python3
"""One-shot: launch Chrome (CDP) -> enable dev mode -> load unpacked
extension via native picker -> restart on Luogu page -> Ctrl+Shift+U ->
verify crystal.cpp appears. Everything in one process lifetime."""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
from lib_x import ask, place_window, shot
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'

DEMO = '/home/z/my-project/workspace/demo'
CHROME = '/tmp/chrome-ext/opt/google/chrome/google-chrome'
URL = 'https://www.luogu.com.cn/problem/P17831'
EXT = '/tmp/ccext'


def cdp_eval(expr, port=9222, timeout=15, want='chrome://extensions',
             wait=True):
    """Evaluate JS in a tab via CDP; navigate to `want` if not there."""
    data = json.loads(urllib.request.urlopen(
        'http://127.0.0.1:%d/json' % port, timeout=5).read())
    page = [t for t in data if t['type'] == 'page'
            and want in t.get('url', '')]
    if not page:
        pages = [t for t in data if t['type'] == 'page']
        if not pages:
            raise RuntimeError('no page targets: %s' % data)
        from websocket import create_connection
        ws = create_connection(pages[0]['webSocketDebuggerUrl'], timeout=10)
        ws.send(json.dumps({'id': 1, 'method': 'Page.navigate',
                            'params': {'url': want}}))
        time.sleep(3)
        try:
            ws.close()
        except Exception:
            pass
        data = json.loads(urllib.request.urlopen(
            'http://127.0.0.1:%d/json' % port, timeout=5).read())
        page = [t for t in data if t['type'] == 'page'
                and want in t.get('url', '')]
        if not page:
            raise RuntimeError('navigation failed: %s'
                               % [t.get('url') for t in data])
    ws_url = page[0]['webSocketDebuggerUrl']
    from websocket import create_connection  # websocket-client
    ws = create_connection(ws_url, timeout=timeout)
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate',
                        'params': {'expression': expr, 'awaitPromise': True,
                                   'returnByValue': True}}))
    if not wait:
        time.sleep(1.0)
        ws.close()
        return None
    while True:
        msg = json.loads(ws.recv())
        if msg.get('id') == 1:
            ws.close()
            res = msg['result']
            if 'exceptionDetails' in res:
                raise RuntimeError(res['exceptionDetails'].get('exception',
                                  {}).get('description', 'eval error'))
            return res.get('result', {}).get('value')


def clean_demo():
    for name in ('crystal.cpp', 'crystal', 'crystal.exe'):
        p = os.path.join(DEMO, name)
        if os.path.exists(p):
            os.remove(p)
    tdir = os.path.join(DEMO, 'tests')
    if os.path.isdir(tdir):
        for f in os.listdir(tdir):
            os.remove(os.path.join(tdir, f))


def launch_chrome(url, extra=None):
    cmd = [CHROME, '--user-data-dir=/tmp/chrome-demo',
           '--no-first-run', '--no-default-browser-check',
           '--disable-crash-reporter', '--hide-crash-restore-bubble',
           '--disable-session-crashed-bubble',
           '--window-position=0,0', '--window-size=1920,1080',
           '--start-maximized', url]
    if extra:
        cmd = cmd[:1] + extra + cmd[1:]
    subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def main():
    subprocess.run(['pkill', '-9', '-f', 'opt/google/chrome'],
                   capture_output=True)
    subprocess.run(['pkill', '-9', '-f', 'sublime_text'], capture_output=True)
    time.sleep(1.5)

    # 1) Chrome on the extensions page with CDP
    launch_chrome('chrome://extensions', ['--remote-debugging-port=9222'])
    time.sleep(8)

    # 2) dev mode on (Chrome 156 API names)
    val = cdp_eval(
        "(async () => { const cfg = await new Promise(r => "
        "chrome.developerPrivate.getProfileConfiguration(r));"
        " if (!cfg.inDeveloperMode) await new Promise(r => "
        "chrome.developerPrivate.updateProfileConfiguration("
        "{inDeveloperMode: true}, r)); return 'dev-ok'; })()")
    print('devmode:', val)

    # 3) load unpacked -> native GTK picker (fire and forget: the callback
    # only resolves after the file is chosen)
    cdp_eval("(new Promise(r => chrome.developerPrivate.loadUnpacked(r)))"
             ".then(id => 'loaded-' + id)", timeout=8, wait=False)
    time.sleep(3.0)
    shot('/tmp/_gtk1.png')
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.8)
    pyautogui.typewrite(EXT, interval=0.03)
    time.sleep(0.5)
    shot('/tmp/_gtk2.png')
    pyautogui.press('enter')          # navigate into the folder
    time.sleep(1.2)
    pyautogui.click(1072, 798)        # "Open" selects the current folder
    time.sleep(4)
    shot('/tmp/_gtk3.png')
    ids = cdp_eval(
        "(new Promise(r => chrome.developerPrivate.getExtensionsInfo("
        "es => r(es.map(e => [e.id, e.name, e.state])))))")
    print('extensions:', ids)
    ext_id = None
    for item in (ids or []):
        if 'Companion' in str(item[1]):
            ext_id = item[0]
    if not ext_id:
        print('EXTENSION NOT LOADED')
        return 1
    print('ext id:', ext_id)
    # save id for future reference
    json.dump({'id': ext_id}, open('/tmp/ccext_id.json', 'w'))

    # 4) Sublime must be listening before the send
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
    time.sleep(2.0)
    print('sublime up')

    # 5) navigate Chrome to the problem page (reuse running instance)
    launch_chrome(URL)
    time.sleep(12)
    place_window('google-chrome')
    time.sleep(1)

    # 6) send via keyboard shortcut
    pyautogui.hotkey('ctrl', 'shift', 'u')
    created = False
    for i in range(30):
        time.sleep(0.5)
        if os.path.exists(os.path.join(DEMO, 'crystal.cpp')):
            created = True
            print('crystal.cpp created after %.1fs' % (i * 0.5))
            break
    if not created:
        print('shortcut failed; trying toolbar icon path later')
        return 2
    time.sleep(2.5)
    print(open(os.path.join(DEMO, 'crystal.cpp')).read()[:220])
    print('tests stored:',
          os.path.exists(os.path.join(DEMO, 'tests', 'crystal.cpp__tests')))
    print('views:', lib_x.view_names())
    return 0


if __name__ == '__main__':
    sys.exit(main())
