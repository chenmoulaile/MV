#!/bin/bash
# Record the Package Control install segment (take_install)
set -x
export DISPLAY=:99
export LD_LIBRARY_PATH=~/apps/x11/usr/lib/x86_64-linux-gnu
X=~/apps/x11/usr/bin/xdotool
OUT=/home/z/my-project/workspace/takes2
mkdir -p $OUT

# --- pre-stage: uninstall plugin, fresh Sublime ---
rm -f ~/.config/sublime-text/"Installed Packages/Algorithm Competition Assistant.sublime-package"
pkill -f sublime_text; sleep 1.5
(~/apps/sublime/opt/sublime_text/sublime_text /home/z/demo > /tmp/sublime.log 2>&1 &)
sleep 9
python3 /home/z/my-project/scripts/fix_cursor.py > /dev/null
WID=$($X search --onlyvisible --class sublime_text | tail -1)
$X windowmove $WID 0 0; $X windowsize $WID 1920 1080; $X windowraise $WID
sleep 1
# close any stale tabs: ctrl+k w? just leave; new session (hot_exit false) should be clean-ish
$X key ctrl+k; $X key ctrl+w; sleep 0.6   # close current tab if any

# --- RECORD ---
(ffmpeg -y -v error -f x11grab -framerate 30 -video_size 1920x1080 -i :99 -draw_mouse 1 \
  -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p $OUT/seg_install.mp4 &) 
REC=$!
sleep 1.2

# focus editor area
$X mousemove 700 500; sleep 0.4; $X click 1; sleep 0.6
# small idle drift (mouse visible, alive)
$X mousemove 720 505; sleep 0.7

# palette
$X key ctrl+shift+p; sleep 1.4
$X type --delay 55 "install package"; sleep 1.2
$X key Return; sleep 4.5          # PC loads channel
$X type --delay 45 "algorithm competition"; sleep 1.8
$X key Return; sleep 10           # download + install
sleep 2
$X mousemove 740 510; sleep 0.8
$X key Escape; sleep 0.5

sleep 1.5
# stop recording
pkill -f "x11grab" ; sleep 1
echo TAKE_INSTALL_DONE
ls -la $OUT/
