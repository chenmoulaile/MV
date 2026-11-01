#!/usr/bin/env python3
"""Capture the extension's full POST (headers+body), then replay it verbatim
to the live Sublime listener; check crystal.cpp + plugin debug log."""
import json
import os
import subprocess
import sys
import threading
import time

sys.path.insert(0, '/home/z/my-project/scripts')
import lib_x
import pyautogui
pyautogui.FAILSAFE = False
os.environ['DISPLAY'] = ':99'

DEMO = '/home/z/my-project/workspace/demo'
REQ = '/tmp/cc_request.txt'

CAPTURE = r'''
import socket, sys
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 12345))
s.listen(2)
c, _ = s.accept()
c.settimeout(3)
buf = b""
while len(buf) < 262144:
    try:
        d = c.recv(65536)
    except Exception:
        break
    if not d:
        break
    buf += d
    # stop early if body complete: content-length reached
    try:
        head, body = buf.split(b"\r\n\r\n", 1)
        for line in head.split(b"\r\n"):
            if line.lower().startswith(b"content-length:"):
                n = int(line.split(b":")[1])
                if len(body) >= n:
                    break
    except Exception:
        pass
open("/tmp/cc_request.txt", "wb").write(buf)
try:
    c.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 2\r\nConnection: close\r\n\r\nok")
except Exception:
    pass
c.close()
'''


def main():
    subprocess.run(['pkill', '-9', '-f', 'sublime_text'], capture_output=True)
    time.sleep(1.5)
    if os.path.exists(REQ):
        os.remove(REQ)
    cap = subprocess.Popen([sys.executable, '-c', CAPTURE])
    cap.wait(40)
    print('captured bytes:', os.path.getsize(REQ) if os.path.exists(REQ) else 0)
    raw = open(REQ, 'rb').read()
    head, body = raw.split(b'\r\n\r\n', 1)
    print('--- request head ---')
    print(head.decode('utf-8', 'replace')[:400])
    print('--- body head ---')
    print(body.decode('utf-8', 'replace')[:260])
    # extract Origin/Content-Type headers
    headers = {}
    for line in head.split(b'\r\n')[1:]:
        if b':' in line:
            k, v = line.split(b':', 1)
            headers[k.decode().strip().lower()] = v.decode().strip()

    # start Sublime, wait for listener
    subprocess.Popen(['/home/z/my-project/apps/sublime_text/sublime_text',
                      '--detached', DEMO],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 45:
        try:
            import socket
            s = socket.create_connection(('127.0.0.1', 12345), timeout=1)
            s.close()
            break
        except Exception:
            time.sleep(0.8)
    time.sleep(2.0)
    print('listener up; replaying...')

    import socket as sk
    req = b'POST / HTTP/1.1\r\nHost: localhost:12345\r\n'
    for k in ('content-type', 'origin', 'sec-fetch-site', 'user-agent',
              'accept', 'accept-encoding', 'accept-language', 'connection'):
        if k in headers:
            req += ('%s: %s\r\n' % (k, headers[k])).encode()
    req += b'Content-Length: ' + str(len(body)).encode() + b'\r\n\r\n' + body
    s = sk.create_connection(('127.0.0.1', 12345), timeout=8)
    s.sendall(req)
    time.sleep(2)
    try:
        s.recv(4096)
    except Exception:
        pass
    s.close()

    for i in range(20):
        time.sleep(0.5)
        if os.path.exists(os.path.join(DEMO, 'crystal.cpp')):
            print('FILE CREATED %.1fs after replay' % (i * 0.5))
            break
    else:
        print('no file after replay')
    logf = os.path.expanduser('~/.config/sublime-text/Log/aca-companion.log')
    for cand in (logf,
                 os.path.expanduser(
                     '~/.config/sublime-text/Data/Log/aca-companion.log')):
        if os.path.exists(cand):
            print('--- plugin log (%s) ---' % cand)
            print(open(cand, encoding='utf-8', errors='replace').read()[-600:])
            break
    else:
        print('no plugin log found')
    print('views:', lib_x.view_names())


if __name__ == '__main__':
    main()
