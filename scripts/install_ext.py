#!/usr/bin/env python3
"""Install the unpacked extension via chrome://extensions with several GTK
dialog strategies; poll getExtensionsInfo after each until it appears."""
import json
import os
import subprocess
import sys
import time
import urllib.request

sys.path.insert(0, '/home/z/my-project/scripts')
from lib_x import shot, place_window
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'

CHROME = '/tmp/chrome-ext/opt/google/chrome/google-chrome'
EXT = '/tmp/ccext'


def cdp_eval(expr, timeout=15, want='chrome://extensions', wait=True):
    data = json.loads(urllib.request.urlopen(
        'http://127.0.0.1:9222/json', timeout=5).read())
    page = [t for t in data if t['type'] == 'page' and want in t.get('url', '')]
    if not page:
        pages = [t for t in data if t['type'] == 'page']
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
            'http://127.0.0.1:9222/json', timeout=5).read())
        page = [t for t in data if t['type'] == 'page'
                and want in t.get('url', '')]
    from websocket import create_connection
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
            return msg['result'].get('result', {}).get('value')


def exts():
    try:
        return cdp_eval("(new Promise(r => "
                        "chrome.developerPrivate.getExtensionsInfo("
                        "es => r(es.map(e => [e.name, e.state])))))")
    except Exception as e:
        return 'ERR %s' % e


def open_dialog():
    cdp_eval("window.__lu = new Promise(r => "
             "chrome.developerPrivate.loadUnpacked(r)); 'fired'",
             wait=False)
    time.sleep(3)


def type_path():
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.7)
    pyautogui.typewrite(EXT, interval=0.03)
    time.sleep(0.4)


def main():
    subprocess.run(['pkill', '-9', '-f', 'opt/google/chrome'],
                   capture_output=True)
    time.sleep(1.5)
    subprocess.Popen([CHROME, '--user-data-dir=/tmp/chrome-demo',
                      '--no-first-run', '--no-default-browser-check',
                      '--disable-crash-reporter', '--hide-crash-restore-bubble',
                      '--disable-session-crashed-bubble',
                      '--remote-debugging-port=9222',
                      '--window-position=0,0', '--window-size=1920,1080',
                      '--start-maximized', 'chrome://extensions'],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(8)
    cdp_eval("(async () => { const cfg = await new Promise(r => "
             "chrome.developerPrivate.getProfileConfiguration(r));"
             " if (!cfg.inDeveloperMode) await new Promise(r => "
             "chrome.developerPrivate.updateProfileConfiguration("
             "{inDeveloperMode: true}, r)); return 'dev-ok'; })()")

    strategies = [
        ('double-enter', [
            ('type', None), ('key', 'enter'), ('wait', 1.2),
            ('key', 'enter'), ('wait', 2.5)]),
        ('enter-then-open', [
            ('type', None), ('key', 'enter'), ('wait', 1.2),
            ('click', (1072, 798)), ('wait', 2.5)]),
        ('shift-enter', [
            ('type', None), ('key', 'shift+enter'), ('wait', 2.5)]),
        ('type-open', [
            ('type', None), ('wait', 0.3), ('click', (1072, 798)),
            ('wait', 2.5)]),
    ]
    for name, steps in strategies:
        print('--- strategy:', name)
        open_dialog()
        for kind, arg in steps:
            if kind == 'type':
                type_path()
            elif kind == 'key':
                pyautogui.press(arg)
            elif kind == 'click':
                pyautogui.click(*arg)
            elif kind == 'wait':
                time.sleep(arg)
        got = exts()
        print('exts:', got)
        shot('/tmp/_strat_%s.png' % name.replace('-', '_'))
        if got and got != 'ERR' and 'Companion' in str(got):
            print('INSTALLED via', name)
            return 0
        # dismiss a still-open dialog for the next strategy
        pyautogui.press('escape')
        time.sleep(1)
    print('ALL STRATEGIES FAILED')
    return 1


if __name__ == '__main__':
    sys.exit(main())
