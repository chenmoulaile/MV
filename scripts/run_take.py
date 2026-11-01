#!/usr/bin/env python3
"""Scene runner for the promo video takes. One invocation = one scene = one
continuous real-screen recording (cursor composited in post).

Scenes:
  chrome   - Luogu problem page, scroll, click the Competitive Companion icon
  zh_main  - Sublime: raise window, paste solution, judge, detail, statement
  lang     - live UI language switch zh -> en with the run panel visible
  en_main  - full flow with the plugin UI in English
"""
import json
import os
import socket
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lib_x
from lib_x import (Recorder, PointerSampler, ask, click, keys, move, place_window,
                   set_clipboard, shot, subl_cmd, type_text, view_names,
                   wait_view)
import pyautogui
pyautogui.FAILSAFE = False

DEMO = '/home/z/my-project/workspace/demo'
CODE = open('/home/z/my-project/scripts/solution_code.txt', encoding='utf-8').read()
URL = 'https://www.luogu.com.cn/problem/P17831'
CHROME = '/tmp/chrome-ext/opt/google/chrome/google-chrome'
SUBLIME = '/home/z/my-project/apps/sublime_text/sublime_text'
OUT_DIR = '/home/z/my-project/workspace/takes'
PROBLEM_FILE = os.path.join(DEMO, 'P17831 [CSP-S 2026] 能量水晶 crystal（民间数据）.cpp')
SETTINGS = os.path.expanduser(
    '~/.config/sublime-text/Packages/User/'
    'Algorithm Competition Assistant.sublime-settings')

os.makedirs(OUT_DIR, exist_ok=True)
os.environ['DISPLAY'] = ':99'
from Xlib import X


def kill_all():
    for pat in ('sublime_text', 'opt/google/chrome'):
        subprocess.run(['pkill', '-9', '-f', pat], capture_output=True)
    time.sleep(2)


def port_open(port, timeout=1.0):
    try:
        s = socket.create_connection(('127.0.0.1', port), timeout=timeout)
        s.close()
        return True
    except Exception:
        return False


def launch_sublime(path=DEMO, wait_listener=True):
    for f in os.listdir(os.path.expanduser('~/.config/sublime-text/Local')):
        if f.endswith('.session'):
            os.remove(os.path.expanduser(
                '~/.config/sublime-text/Local/' + f))
    subprocess.Popen([SUBLIME, '--detached', path],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    while time.time() - t0 < 45:
        try:
            if ask({'cmd': 'ping'}, timeout=2).get('ok'):
                break
        except Exception:
            pass
        time.sleep(0.8)
    if wait_listener:
        t0 = time.time()
        while time.time() - t0 < 20:
            if port_open(12345):
                break
            time.sleep(0.5)
    time.sleep(1.5)


def launch_chrome(url=URL, wait_paint=True):
    subprocess.Popen(
        [CHROME, '--user-data-dir=/tmp/chrome-demo', '--no-first-run',
         '--no-default-browser-check', '--disable-crash-reporter',
         '--hide-crash-restore-bubble', '--disable-session-crashed-bubble',
         '--window-position=0,0', '--window-size=1920,1080',
         '--start-maximized', url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(11)
    place_window('google-chrome')
    time.sleep(0.6)
    if wait_paint:
        t0 = time.time()
        while time.time() - t0 < 30:
            shot('/tmp/_paint.png')
            if not mostly_white('/tmp/_paint.png'):
                break
            time.sleep(0.6)
        time.sleep(1.2)


def mostly_white(path):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    px = im.load()
    white = total = 0
    for y in range(140, 1000, 9):
        for x in range(120, 1880, 9):
            r, g, b = px[x, y]
            total += 1
            if r > 242 and g > 242 and b > 242:
                white += 1
    return white > total * 0.55


def chrome_win():
    best = None
    for w in lib_x._walk(lib_x.xdpy().screen().root):
        try:
            cls = w.get_wm_class()
            g = w.get_geometry()
        except Exception:
            continue
        if cls and 'google-chrome' in ((cls[0] or '') + (cls[1] or '')).lower() \
                and g.width > 1000 and g.height > 800:
            if w.get_attributes().map_state == 2:
                best = w
    return best


def raise_chrome():
    w = chrome_win()
    if w:
        w.configure(stack_mode=X.Above)
        w.set_input_focus(X.RevertToParent, X.CurrentTime)
        lib_x.xdpy().sync()
        time.sleep(0.8)
    return w


def ac_green_seen(path):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    px = im.load()
    hits = 0
    for y in range(70, 300):
        for x in range(1150, 1919):
            r, g, b = px[x, y]
            if g > 110 and g > r + 30 and g > b + 20 and r < 120:
                hits += 1
    return hits > 60


def wait_ac(timeout=35):
    t0 = time.time()
    while time.time() - t0 < timeout:
        p = '/tmp/_scan.png'
        shot(p)
        if ac_green_seen(p):
            return True
        time.sleep(0.5)
    return False


def find_detail_button(path):
    from PIL import Image
    im = Image.open(path).convert('RGB')
    px = im.load()
    pts = []
    for y in range(70, 240):
        for x in range(1000, 1919):
            r, g, b = px[x, y]
            if abs(r - 123) < 24 and abs(g - 114) < 24 and abs(b - 136) < 24 \
                    and b > g + 8 and r > g + 2:
                pts.append((x, y))
    if len(pts) < 30:
        return None
    ys = sorted(p[1] for p in pts)
    ymid = ys[len(ys) // 2]
    row = sorted(p for p in pts if abs(p[1] - ymid) <= 12)
    runs = []
    start = prev = row[0][0]
    for x, _ in row[1:]:
        if x - prev <= 5:
            prev = x
        else:
            runs.append((start, prev))
            start = prev = x
    runs.append((start, prev))
    best = max(runs, key=lambda r: r[1] - r[0])
    return (best[0] + best[1]) // 2, ymid


def reset_demo():
    for name in os.listdir(DEMO):
        p = os.path.join(DEMO, name)
        if os.path.isfile(p):
            os.remove(p)
        elif name == 'tests':
            for f in os.listdir(p):
                os.remove(os.path.join(p, f))


def set_language(lang):
    d = json.load(open(SETTINGS, encoding='utf-8'))
    d['language'] = lang
    json.dump(d, open(SETTINGS, 'w', encoding='utf-8'), indent=1,
              ensure_ascii=False)


def save_log(sampler, name):
    json.dump([[t, x, y, m] for t, x, y, m in sampler.stop()],
              open(os.path.join(OUT_DIR, 'ptr_%s.json' % name), 'w'))


# ================================================================= scenes ==
def scene_chrome():
    """Luogu page -> scroll -> click the Competitive Companion icon."""
    kill_all()
    reset_demo()
    launch_sublime(DEMO)          # listener must be up; stays behind Chrome
    launch_chrome(URL)

    sampler = PointerSampler(); sampler.start()
    rec = Recorder(os.path.join(OUT_DIR, 'take_chrome.mp4'))
    rec.start()
    try:
        move(960, 620, 0.8)
        time.sleep(0.8)
        # scroll through the statement and samples
        for _ in range(6):
            pyautogui.scroll(-4)
            time.sleep(0.6)
        time.sleep(1.0)
        for _ in range(2):
            pyautogui.scroll(-4)
            time.sleep(0.7)
        time.sleep(0.8)
        for _ in range(7):
            pyautogui.scroll(5)
            time.sleep(0.45)
        time.sleep(1.0)
        # focus the page (neutral spot inside the statement text)
        click(500, 700)
        time.sleep(0.6)
        # send to the editor: click the pinned Competitive Companion icon
        move(1770, 62, 0.7)
        time.sleep(0.5)
        pyautogui.click(1770, 62)
        time.sleep(3.0)
    finally:
        rec.stop()
        save_log(sampler, 'chrome')
    print('file created:', os.path.exists(PROBLEM_FILE))


def prelude_send():
    """Off-camera: reset demo, let the extension re-create the problem file."""
    kill_all()
    reset_demo()
    launch_sublime(DEMO)
    launch_chrome(URL)
    raise_chrome()
    click(500, 700)
    time.sleep(0.5)
    pyautogui.click(1770, 62)
    t0 = time.time()
    while time.time() - t0 < 20 and not os.path.exists(PROBLEM_FILE):
        time.sleep(0.5)
    print('prelude file created:', os.path.exists(PROBLEM_FILE))
    time.sleep(1.5)


def scene_zh_main():
    """Sublime: raise over Chrome, paste, judge, detail."""
    prelude_send()
    place_window('sublime_text')
    time.sleep(0.8)
    click(700, 500)
    time.sleep(0.6)
    pyautogui.press('f11')
    time.sleep(1.4)

    sampler = PointerSampler(); sampler.start()
    rec = Recorder(os.path.join(OUT_DIR, 'take_zh_main.mp4'))
    rec.start()
    try:
        time.sleep(1.6)                       # establishing: header comment
        keys('ctrl', 'end'); time.sleep(0.6)
        set_clipboard(CODE); time.sleep(0.4)
        keys('ctrl', 'v'); time.sleep(1.8)    # solution lands at the bottom
        keys('ctrl', 's'); time.sleep(1.4)
        keys('ctrl', 'alt', 'b')              # judge
        ok = wait_ac()
        print('AC seen:', ok)
        time.sleep(3.0)

        # open test 1 detail view
        shot('/tmp/_det.png')
        btn = find_detail_button('/tmp/_det.png')
        print('detail btn:', btn)
        if btn:
            click(btn[0], btn[1])
            time.sleep(2.4)
            for _ in range(4):
                pyautogui.scroll(-3)
                time.sleep(0.5)
            time.sleep(1.2)
            keys('ctrl', 'w'); time.sleep(1.4)   # close detail
        time.sleep(1.6)
    finally:
        rec.stop()
        save_log(sampler, 'zh_main')


def scene_lang():
    """Live switch zh -> en with the run panel visible."""
    prelude_send()
    place_window('sublime_text')
    time.sleep(0.8)
    click(700, 500)
    time.sleep(0.6)
    pyautogui.press('f11')
    time.sleep(1.4)

    sampler = PointerSampler(); sampler.start()
    rec = Recorder(os.path.join(OUT_DIR, 'take_lang.mp4'))
    rec.start()
    try:
        keys('ctrl', 'alt', 'b')
        ok = wait_ac()
        print('AC zh:', ok)
        time.sleep(2.6)

        keys('ctrl', 'shift', 'p'); time.sleep(1.3)
        pyautogui.typewrite('switch to english', interval=0.045)
        time.sleep(1.0)
        pyautogui.press('enter')
        time.sleep(2.4)

        keys('ctrl', 'alt', 'b')
        ok = wait_ac()
        print('AC en:', ok)
        time.sleep(3.6)
    finally:
        rec.stop()
        save_log(sampler, 'lang')
    subl_cmd('cph_language_set_language', {'language': 'zh'})


def scene_en_main():
    """Full flow with the plugin UI in English."""
    kill_all()
    reset_demo()
    set_language('en')
    launch_sublime(DEMO)            # listener up, stays behind Chrome
    launch_chrome(URL)
    # send off-camera so the take shows only Sublime
    raise_chrome()
    click(500, 700)
    time.sleep(0.5)
    pyautogui.click(1770, 62)
    t0 = time.time()
    while time.time() - t0 < 20 and not os.path.exists(PROBLEM_FILE):
        time.sleep(0.5)
    print('file created:', os.path.exists(PROBLEM_FILE))

    place_window('sublime_text')
    time.sleep(0.8)
    click(700, 500)
    time.sleep(0.6)
    pyautogui.press('f11')
    time.sleep(1.4)

    sampler = PointerSampler(); sampler.start()
    rec = Recorder(os.path.join(OUT_DIR, 'take_en_main.mp4'))
    rec.start()
    try:
        time.sleep(1.6)
        keys('ctrl', 'end'); time.sleep(0.6)
        set_clipboard(CODE); time.sleep(0.4)
        keys('ctrl', 'v'); time.sleep(1.8)
        keys('ctrl', 's'); time.sleep(1.4)
        keys('ctrl', 'alt', 'b')
        ok = wait_ac()
        print('AC en:', ok)
        time.sleep(3.2)
    finally:
        rec.stop()
        save_log(sampler, 'en_main')
    set_language('zh')


if __name__ == '__main__':
    scene = sys.argv[1]
    {'chrome': scene_chrome, 'zh_main': scene_zh_main,
     'lang': scene_lang, 'en_main': scene_en_main}[scene]()
    print('scene done:', scene)
