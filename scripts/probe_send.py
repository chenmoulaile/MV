#!/usr/bin/env python3
"""Binary-search the companion send: capture server on 12345 (Sublime killed),
then trigger the extension two ways (shortcut, toolbar puzzle menu)."""
import json
import os
import socket
import subprocess
import sys
import threading
import time

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'
from Xlib import X

HITS = []


def capture_server(port=12345):
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', port))
    s.listen(4)

    def serve():
        while True:
            try:
                c, a = s.accept()
            except Exception:
                return
            try:
                c.settimeout(2)
                buf = b''
                while b'\r\n\r\n' not in buf and len(buf) < 65536:
                    d = c.recv(4096)
                    if not d:
                        break
                    buf += d
                head = buf.split(b'\r\n\r\n')[0].decode('utf-8', 'replace')
                HITS.append(head[:300])
                c.sendall(b'HTTP/1.1 200 OK\r\nContent-Length: 2\r\n'
                          b'Connection: close\r\n\r\nok')
            except Exception:
                pass
            finally:
                try:
                    c.close()
                except Exception:
                    pass
    threading.Thread(target=serve, daemon=True).start()


def chrome_window():
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
    return w


def focus_chrome():
    w = chrome_window()
    if w:
        w.configure(stack_mode=X.Above)
        w.set_input_focus(X.RevertToParent, X.CurrentTime)
        lib_x.xdpy().sync()
        time.sleep(1.0)
    return w


def main():
    subprocess.run(['pkill', '-9', '-f', 'sublime_text'], capture_output=True)
    time.sleep(1.5)
    capture_server()
    print('capture server on 12345')

    # is chrome alive? if not, launch
    w = chrome_window()
    if w is None:
        subprocess.Popen(
            ['/tmp/chrome-ext/opt/google/chrome/google-chrome',
             '--user-data-dir=/tmp/chrome-demo', '--no-first-run',
             '--no-default-browser-check', '--disable-crash-reporter',
             '--hide-crash-restore-bubble', '--disable-session-crashed-bubble',
             '--window-position=0,0', '--window-size=1920,1080',
             '--start-maximized', 'https://www.luogu.com.cn/problem/P17831'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(13)
    focus_chrome()

    print('--- attempt 1: Ctrl+Shift+U')
    pyautogui.hotkey('ctrl', 'shift', 'u')
    t0 = time.time()
    while time.time() - t0 < 10 and not HITS:
        time.sleep(0.4)
    print('hits after shortcut:', len(HITS))
    for h in HITS:
        print(h.split('\r\n')[0])

    if not HITS:
        print('--- attempt 2: puzzle menu click')
        # puzzle icon sits right of the address bar; extensions button area
        pyautogui.click(1590, 25)
        time.sleep(2)
        lib_x.shot('/tmp/_puzzle.png')
        # click the first extension row ("Competitive Companion")
        pyautogui.click(1000, 120)
        time.sleep(6)
        print('hits after puzzle:', len(HITS))
        for h in HITS:
            print(h.split('\r\n')[0])
        lib_x.shot('/tmp/_puzzle2.png')
    print('done, hits:', len(HITS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
