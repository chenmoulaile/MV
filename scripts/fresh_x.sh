#!/bin/bash
# Full X session reset + launch apps fresh
XPY=/home/z/my-project/workspace/xenv/bin/python3
DEMO=/home/z/my-project/workspace/demo
APPS=/home/z/my-project/workspace/apps

# kill everything X-related
pkill -9 -f "Xvfb :99" 2>/dev/null; pkill -9 -f sublime_text 2>/dev/null; pkill -9 -f chrome-linux64 2>/dev/null; pkill -9 -f "ffmpeg.*x11grab" 2>/dev/null
sleep 2
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null

setsid nohup Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp > /tmp/xvfb.log 2>&1 < /dev/null &
sleep 3

cd $APPS/sublime_text
DISPLAY=:99 GTK_CSD=0 setsid nohup ./sublime_text -n "$DEMO/crystal.cpp" > /tmp/sublime.log 2>&1 < /dev/null &
sleep 8

cd $APPS/chrome-linux64
DISPLAY=:99 setsid nohup ./chrome --no-sandbox --disable-gpu --test-type --lang=zh-CN \
  --disable-features=Translate,TranslateUI \
  --user-data-dir=$APPS/chrome-profile \
  --load-extension=$APPS/companion-ext --no-first-run --no-default-browser-check --disable-sync \
  --disable-crash-reporter --disable-session-crashed-bubble --window-size=1920,1080 --window-position=0,0 \
  "https://www.luogu.com.cn/problem/P17831" > /tmp/chrome.log 2>&1 < /dev/null &
sleep 6

DISPLAY=:99 $XPY /home/z/my-project/scripts/xwin.py list
