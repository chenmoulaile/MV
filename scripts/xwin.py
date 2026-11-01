#!/usr/bin/env python3
"""Window utilities: list windows, resize/move, focus."""
import sys
from Xlib import display, X
from Xlib.ext import xtest

d = display.Display()
root = d.screen().root


def walk(win, acc, depth=0):
    try:
        attrs = win.get_attributes()
    except Exception:
        return
    if attrs.map_state == 2:
        acc.append(win)
    for c in win.query_tree().children:
        walk(c, acc, depth + 1)


def windows():
    acc = []
    walk(root, acc)
    return acc


def wm_name(win):
    try:
        from Xlib import Xutil
        prop = win.get_full_property(d.intern_atom('_NET_WM_NAME'), 0) or \
               win.get_full_property(d.intern_atom('WM_NAME'), Xutil.AnyPropertyType)
        if prop:
            return str(prop.value)
    except Exception:
        pass
    return ''


def find(sub):
    for w in windows():
        if sub.lower() in wm_name(w).lower():
            return w
    return None


def geom_move_resize(sub, x, y, w, h):
    win = find(sub)
    if not win:
        print('not found:', sub)
        return
    win.configure(x=x, y=y, width=w, height=h, stack_mode=X.Above)
    d.sync()
    print('resized', wm_name(win))


def focus(sub):
    win = find(sub)
    if win:
        win.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
        win.configure(stack_mode=X.Above)
        d.sync()
        print('focused', wm_name(win))


def click(x, y):
    rootx = root.query_pointer().root_x
    rooty = root.query_pointer().root_y
    for i in range(12):
        t = (i + 1) / 12
        e = t * t * (3 - 2 * t)
        xtest.fake_input(d, X.MotionNotify, x=int(rootx + (x - rootx) * e), y=int(rooty + (y - rooty) * e))
        d.sync()
    xtest.fake_input(d, X.ButtonPress, 1)
    d.sync()
    xtest.fake_input(d, X.ButtonRelease, 1)
    d.sync()


def listwins():
    for w in windows():
        g = w.get_geometry()
        print(f'"{wm_name(w)}" {w.id:#x} {g.width}x{g.height}')


def by_id(hexid):
    wid = int(hexid, 16)
    acc = []
    walk(root, acc)
    for w in acc:
        if w.id == wid:
            return w
    return None


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list':
        listwins()
    elif cmd == 'fit':
        geom_move_resize(sys.argv[2], 0, 0, 1920, 1080)
        focus(sys.argv[2])
    elif cmd == 'focusid':
        w = by_id(sys.argv[2])
        if w:
            w.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
            w.configure(stack_mode=X.Above)
            d.sync()
            print('raised', hex(w.id))
    elif cmd == 'focus':
        focus(sys.argv[2])
    elif cmd == 'click':
        click(int(sys.argv[2]), int(sys.argv[3]))
