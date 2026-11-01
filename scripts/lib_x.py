#!/usr/bin/env python3
"""Shared automation toolkit for the promo-video takes (Xvfb :99).

- window management via python-xlib (no WM running)
- bridge client for the Sublime demo_helper (port 19999)
- cursor sampler: logs the REAL pointer path at ~120 Hz for the
  post-production halo/arrow overlay
- ffmpeg x11grab recorder with -draw_mouse 0 (cursor composited in post)
"""
import json
import os
import socket
import subprocess
import threading
import time

os.environ.setdefault('DISPLAY', ':99')

from Xlib import display as xdisplay, X
import pyautogui

pyautogui.FAILSAFE = False

BRIDGE_PORT = 19999
SCREEN = (1920, 1080)


# ---------------------------------------------------------------- windows --
def _walk(win, depth=0):
    try:
        children = win.query_tree().children
    except Exception:
        return
    for c in children:
        yield c
        if depth < 6:
            for sub in _walk(c, depth + 1):
                yield sub


_dpy = None


def xdpy():
    global _dpy
    if _dpy is None:
        _dpy = xdisplay.Display(os.environ.get('DISPLAY', ':99'))
    return _dpy


def find_window(substr):
    for w in _walk(xdpy().screen().root):
        try:
            cls = w.get_wm_class()
        except Exception:
            continue
        if cls and cls[1] and substr.lower() in cls[1].lower():
            return w
    return None


def place_window(substr, x=0, y=0, w=1920, h=1080, above=True):
    win = find_window(substr)
    if win is None:
        return False
    try:
        win.configure(x=x, y=y, width=w, height=h,
                      stack_mode=X.Above if above else X.Below)
    except Exception:
        try:
            win.configure(stack_mode=X.Above if above else X.Below)
        except Exception:
            pass
    try:
        win.set_input_focus(X.RevertToParent, X.CurrentTime)
    except Exception:
        pass
    try:
        xdpy().sync()
    except Exception:
        pass
    return True


def window_geom(substr):
    win = find_window(substr)
    if win is None:
        return None
    g = win.get_geometry()
    return (g.x, g.y, g.width, g.height)


# ----------------------------------------------------------------- bridge --
def ask(req, timeout=8):
    s = socket.create_connection(('127.0.0.1', BRIDGE_PORT), timeout=timeout)
    s.sendall(json.dumps(req).encode('utf-8'))
    s.shutdown(socket.SHUT_WR)
    buf = b''
    while True:
        chunk = s.recv(65536)
        if not chunk:
            break
        buf += chunk
    s.close()
    return json.loads(buf.decode('utf-8')) if buf else None


def view_names():
    try:
        return ask({'cmd': 'views'}).get('names', [])
    except Exception:
        return []


def wait_view(substr, timeout=20):
    t0 = time.time()
    while time.time() - t0 < timeout:
        for n in view_names():
            if substr in n:
                return True
        time.sleep(0.25)
    return False


def set_clipboard(text):
    return ask({'cmd': 'clip', 'text': text})


def type_text(text, cps=140):
    return ask({'cmd': 'type', 'text': text, 'cps': cps})


def subl_cmd(name, args=None):
    return ask({'cmd': 'win', 'name': name, 'args': args or {}})


# ---------------------------------------------------------------- pointer --
class PointerSampler(threading.Thread):
    """Log (t, x, y, buttons) at ~120 Hz for overlay rendering."""

    def __init__(self):
        super().__init__(daemon=True)
        self.log = []
        self.running = False

    def start(self):
        self.running = True
        super().start()

    def run(self):
        d = xdisplay.Display(':99')
        root = d.screen().root
        while self.running:
            try:
                p = root.query_pointer()
                self.log.append((time.time(), p.root_x, p.root_y,
                                 int(p.mask) & 0x300))
            except Exception:
                pass
            time.sleep(0.008)

    def stop(self):
        self.running = False
        self.join(timeout=2)
        return list(self.log)


# --------------------------------------------------------------- recorder --
class Recorder:
    """x11grab without the X cursor; the halo/arrow goes in in post."""

    def __init__(self, out, fps=30):
        self.out = out
        self.fps = fps
        self.proc = None

    def start(self):
        self.proc = subprocess.Popen(
            ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
             '-f', 'x11grab', '-draw_mouse', '0', '-framerate', str(self.fps),
             '-video_size', '%dx%d' % SCREEN, '-i', ':99',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
             '-pix_fmt', 'yuv420p', self.out],
            stdin=subprocess.PIPE)
        time.sleep(1.2)  # let the encoder settle

    def stop(self):
        if not self.proc:
            return
        self.proc.send_signal(15)
        try:
            self.proc.wait(20)
        except Exception:
            self.proc.kill()
        print('recorded ->', self.out)


# ------------------------------------------------------------------ input --
def move(x, y, dur=0.45):
    pyautogui.moveTo(x, y, duration=dur)


def click(x=None, y=None):
    if x is not None:
        pyautogui.moveTo(x, y, duration=0.3)
    time.sleep(0.15)
    pyautogui.click()


def keys(*combo, delay=0.09):
    pyautogui.hotkey(*combo)
    time.sleep(delay)


def shot(path):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-f', 'x11grab', '-video_size', '%dx%d' % SCREEN,
                    '-i', ':99', '-frames:v', '1', '-update', '1', path])


def px_gray(im, x, y):
    return sum(im.getpixel((x, y))[:3]) // 3
