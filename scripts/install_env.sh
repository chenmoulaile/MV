#!/bin/bash
# Install recording environment in background
set -x
exec > /home/z/my-project/scripts/install_env.log 2>&1

export DEBIAN_FRONTEND=noninteractive

# Check sudo
if [ "$(whoami)" != "root" ]; then
  SUDO="sudo"
else
  SUDO=""
fi

$SUDO apt-get update -qq

# Core recording + dev tools
$SUDO apt-get install -y -qq xvfb ffmpeg x11-utils xdotool wmctrl x11-apps imagemagick \
  build-essential gdb fonts-dejavu fonts-noto-cjk xclip at-spi2-core libgtk-3-0 libnss3 \
  libasound2 libgbm1 libxss1 fonts-liberation libu2f-adapter libvulkan1 xdg-utils 2>&1 | tail -5

# Google Chrome
if ! command -v google-chrome >/dev/null 2>&1; then
  cd /tmp
  wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -O chrome.deb
  $SUDO apt-get install -y -qq /tmp/chrome.deb 2>&1 | tail -3
fi

# Sublime Text 4
if ! command -v sublime_text >/dev/null 2>&1; then
  cd /tmp
  wget -q https://download.sublimetext.com/sublime-text_build-4192_amd64.deb -O sublime.deb
  $SUDO apt-get install -y -qq /tmp/sublime.deb 2>&1 | tail -3
fi

echo "=== DONE ==="
which google-chrome sublime_text Xvfb ffmpeg xdotool g++ 2>&1
fc-list | grep -i "dejavu sans mono" | head -2
