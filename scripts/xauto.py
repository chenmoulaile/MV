#!/usr/bin/env python3
"""X11 automation helper: keys / typing / mouse moves (XTEST via python-xlib)."""
import sys, time
from Xlib import display, X
from Xlib.ext import xtest

d = display.Display()

KEYMAP = {
    'ctrl': 37, 'shift': 50, 'alt': 64, 'tab': 23, 'enter': 36, 'return': 36,
    'escape': 9, 'space': 65, 'backspace': 22, 'delete': 119, 'home': 110,
    'end': 115, 'left': 113, 'up': 111, 'right': 114, 'down': 116,
    'f5': 71, 'super': 133, 'pagedown': 117, 'pageup': 112,
}

def key(KeyCode):
    xtest.fake_input(d, X.KeyPress, KeyCode)
    d.sync()
    time.sleep(0.03)
    xtest.fake_input(d, X.KeyRelease, KeyCode)
    d.sync()
    time.sleep(0.03)

def combo(spec):
    """combo like 'ctrl+shift+p' or 'Return'"""
    parts = [p.strip().lower() for p in spec.split('+')]
    codes = []
    for p in parts:
        if p in KEYMAP:
            codes.append(KEYMAP[p])
        elif len(p) == 1:
            codes.append(d.keysym_to_keycode(ord(p)))
        else:
            ks = p.upper() if len(p) > 1 else p
            kc = d.keysym_to_keycode(ord(ks[0]) if len(ks) == 1 else getattr(__import__('Xlib.keysymdef.xkb_keysyms', fromlist=['XK_%s' % ks]), 'XK_%s' % ks))
            codes.append(kc)
    for c in codes[:-1]:
        xtest.fake_input(d, X.KeyPress, c)
        d.sync()
    time.sleep(0.04)
    xtest.fake_input(d, X.KeyPress, codes[-1])
    d.sync()
    time.sleep(0.05)
    xtest.fake_input(d, X.KeyRelease, codes[-1])
    d.sync()
    for c in reversed(codes[:-1]):
        xtest.fake_input(d, X.KeyRelease, c)
        d.sync()
    time.sleep(0.05)

CHAR_SHIFT = '~!@#$%^&*()_+{}|:"<>?ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def type_text(text, delay=0.035):
    for ch in text:
        kc = d.keysym_to_keycode(ord(ch.lower()) if ch.isalpha() else ord(ch))
        if kc == 0:
            continue
        need_shift = ch in CHAR_SHIFT
        if need_shift:
            xtest.fake_input(d, X.KeyPress, 50)
            d.sync()
        xtest.fake_input(d, X.KeyPress, kc)
        d.sync()
        time.sleep(0.012)
        xtest.fake_input(d, X.KeyRelease, kc)
        d.sync()
        if need_shift:
            xtest.fake_input(d, X.KeyRelease, 50)
            d.sync()
        time.sleep(delay)

def move(x, y, steps=18):
    cur = d.screen().root.query_pointer()
    x0, y0 = cur.root_x, cur.root_y
    for i in range(1, steps + 1):
        t = i / steps
        e = t * t * (3 - 2 * t)
        nx = int(x0 + (x - x0) * e)
        ny = int(y0 + (y - y0) * e)
        xtest.fake_input(d, X.MotionNotify, x=nx, y=ny)
        d.sync()
        time.sleep(0.012)

def scroll(button, times=3):
    for _ in range(times):
        xtest.fake_input(d, X.ButtonPress, button)
        d.sync()
        xtest.fake_input(d, X.ButtonRelease, button)
        d.sync()
        time.sleep(0.08)

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'combo':
        combo(sys.argv[2])
    elif cmd == 'type':
        type_text(sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.035)
    elif cmd == 'move':
        move(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == 'scroll':
        scroll(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 3)
