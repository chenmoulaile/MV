#!/usr/bin/env python3
"""Warm up the Chrome profile against the Cloudflare challenge on Luogu.

Opens the problem page, waits, clicks the Turnstile checkbox if present,
repeats until the real page paints. The cf_clearance cookie persists in the
profile, so later takes load the page directly.
"""
import os
import subprocess
import sys
import time

os.environ['DISPLAY'] = ':99'
import pyautogui
pyautogui.FAILSAFE = False
from PIL import Image

CHROME = '/tmp/chrome-ext/opt/google/chrome/google-chrome'
URL = 'https://www.luogu.com.cn/problem/P17831'


def shot(path):
    subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y',
                    '-f', 'x11grab', '-video_size', '1920x1080', '-i', ':99',
                    '-frames:v', '1', '-update', '1', path])


def is_challenge(path):
    im = Image.open(path).convert('RGB')
    px = im.load()
    # challenge page: large white canvas + centered gray text + spinner;
    # real page: Luogu orange/nav accents and lots of content
    white = 0
    for y in range(200, 900, 7):
        for x in range(100, 1800, 7):
            r, g, b = px[x, y]
            if r > 242 and g > 242 and b > 242:
                white += 1
    return white > 13000


def find_checkbox(path):
    """Turnstile box: a bordered rectangle near the center; checkbox sits at
    its left inside edge. Scan rows 500-700 for a light-gray horizontal box."""
    im = Image.open(path).convert('RGB')
    px = im.load()
    rows = []
    for y in range(420, 780):
        run = 0
        for x in range(700, 1500):
            r, g, b = px[x, y]
            if 235 < r < 253 and 235 < g < 253 and 235 < b < 253 and \
                    abs(r - g) < 6 and abs(g - b) < 6:
                run += 1
            else:
                if run > 250:
                    rows.append((y, x - run, x))
                run = 0
    if not rows:
        return None
    y, x0, x1 = rows[len(rows) // 2]
    return (x0 + 28, y)


def main():
    subprocess.run(['pkill', '-f', 'opt/google/chrome'], capture_output=True)
    time.sleep(1.5)
    subprocess.Popen([CHROME, '--user-data-dir=/tmp/chrome-demo',
                      '--no-first-run', '--no-default-browser-check',
                      '--disable-crash-reporter', '--hide-crash-restore-bubble',
                      '--disable-session-crashed-bubble',
                      '--window-position=0,0', '--window-size=1920,1080',
                      '--start-maximized', URL],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(10)
    for attempt in range(8):
        shot('/tmp/cf_check.png')
        if not is_challenge('/tmp/cf_check.png'):
            print('PAGE OK after attempt', attempt)
            return 0
        box = find_checkbox('/tmp/cf_check.png')
        print('attempt', attempt, 'challenge; checkbox at', box)
        if box:
            pyautogui.moveTo(box[0], box[1], duration=0.4)
            time.sleep(0.4)
            pyautogui.click(box[0], box[1])
        time.sleep(9)
    print('STILL CHALLENGED')
    return 1


if __name__ == '__main__':
    sys.exit(main())
