#!/bin/bash
# Background downloader v2 (curl-based)
exec > /home/z/my-project/scripts/apps_dl2.log 2>&1
cd /home/z/my-project/workspace/apps

dl() {
  for i in $(seq 1 40); do
    curl -sL -C - --max-time 300 --retry 2 "$1" -o "$2" && return 0
    sleep 2
  done
  return 1
}

rm -f sublime.tar.xz.part chrome.deb.part
dl "https://download.sublimetext.com/sublime_text_build_4192_x64.tar.xz" sublime.tar.xz && tar -xf sublime.tar.xz && echo "SUBLIME EXTRACTED $(date +%H:%M:%S)"
dl "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" chrome.deb && mkdir -p chrome-portable && dpkg -x chrome.deb chrome-portable && echo "CHROME EXTRACTED $(date +%H:%M:%S)"
echo "=== APPS DONE"
