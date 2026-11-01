#!/bin/bash
# Background downloader for apps: sublime portable + chrome deb
exec > /home/z/my-project/scripts/apps_dl.log 2>&1
cd /home/z/my-project/workspace/apps

dl() { for i in $(seq 1 60); do wget -c -q --timeout=25 "$1" -O "$2.part" && { mv "$2.part" "$2"; return 0; }; sleep 2; done; return 1; }

dl "https://download.sublimetext.com/sublime_text_build_4192_x64.tar.xz" sublime.tar.xz && tar -xf sublime.tar.xz && echo "SUBLIME EXTRACTED"

dl "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" chrome.deb && mkdir -p chrome-portable && dpkg -x chrome.deb chrome-portable && echo "CHROME EXTRACTED"

echo "=== APPS DONE $(date)"
ls -la
