#!/bin/bash
# Rebuild /home/z/apps from cached packages (fast, no network needed except none)
set -e
P=/home/z/my-project/workspace/xenv/pkg
rm -rf ~/apps
mkdir -p ~/apps

# x11 tools
mkdir -p ~/apps/x11
for d in xdotool libxdo3 libxtst6 libxmuu1 "x11-xserver-utils*"; do
  dpkg -x $P/${d}*.deb ~/apps/x11/ 2>/dev/null || dpkg -x $P/$d.deb ~/apps/x11/
done

# chrome for testing
mkdir -p ~/apps
cd ~/apps && unzip -q $P/chrome.zip

# competitive companion ext
mkdir -p ~/apps/cc_ext && cd ~/apps/cc_ext && unzip -oq $P/cc.zip

# sublime
mkdir -p ~/apps/sublime && dpkg -x $P/sublime.deb ~/apps/sublime

echo APPS_REBUILT
ls ~/apps/
