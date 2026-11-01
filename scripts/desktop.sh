#!/bin/bash
# 桌面环境启动：Xvfb + Sublime + Chrome（免 root）
export DISPLAY=:99
export LD_LIBRARY_PATH=/home/z/opt/xdotool/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH
XDOTOOL=/home/z/opt/xdotool/usr/bin/xdotool
SUBL=/home/z/opt/sublime/opt/sublime_text/sublime_text
CHROME=/home/z/opt/chrome/opt/google/chrome/chrome

case "$1" in
  xvfb)
    Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
    sleep 1.5
    xdpyinfo -display :99 >/dev/null 2>&1 && echo "Xvfb UP" || echo "Xvfb FAIL"
    ;;
  sublime)
    # $2 = 项目目录（可选）
    nohup "$SUBL" -n ${2:+--add} "$2" > /tmp/sublime_stdout.log 2>&1 &
    echo "sublime launching"
    ;;
  chrome)
    # $2 = 启动 URL（可选）；--load-extension 在 137+ 可能被忽略，备用方案走 UI 装扩展
    nohup "$CHROME" --user-data-dir=/home/z/chrome-profile \
      --no-first-run --no-default-browser-check --disable-session-crashed-bubble \
      --window-position=0,0 --window-size=1920,1080 \
      --load-extension=/home/z/opt/ext/cc \
      ${2:+"$2"} > /tmp/chrome_stdout.log 2>&1 &
    echo "chrome launching"
    ;;
esac
