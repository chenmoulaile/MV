#!/bin/bash
# Ensure Xvfb :99 is running; restart Sublime/Chrome if needed (caller passes them)
if ! xdpyinfo -display :99 > /dev/null 2>&1; then
  rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null
  setsid nohup Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp > /tmp/xvfb.log 2>&1 < /dev/null &
  sleep 2
fi
xdpyinfo -display :99 > /dev/null 2>&1 && echo "X OK" || echo "X FAIL"
