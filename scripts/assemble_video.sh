#!/bin/bash
# Assemble the final promo video: intro card -> recorded demo (captioned) -> end card.
set -e
NOTO=/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf
OUT=/home/z/my-project/download/algorithm-competition-assistant-demo.mp4

ffmpeg -hide_banner -loglevel warning -y \
  -loop 1 -t 4 -framerate 30 -i /tmp/card_intro.png \
  -i /tmp/raw_rec.mp4 \
  -loop 1 -t 6 -framerate 30 -i /tmp/card_end.png \
  -f lavfi -t 38.4 -i anullsrc=r=44100:cl=stereo \
  -filter_complex "\
[0:v]format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st=3.6:d=0.4[v0];\
[1:v]tpad=stop_mode=clone:stop_duration=2.6,format=yuv420p,\
drawtext=fontfile=$NOTO:text='① Companion 协议一键导入 · 洛谷 P17831 官方样例':fontsize=34:fontcolor=white:box=1:boxcolor=0x000000A6:boxborderw=16:x=(w-text_w)/2:y=h-104:enable='between(t,2.6,5.4)',\
drawtext=fontfile=$NOTO:text='② 在文件底部完成正解 · DejaVu Sans Mono':fontsize=34:fontcolor=white:box=1:boxcolor=0x000000A6:boxborderw=16:x=(w-text_w)/2:y=h-104:enable='between(t,5.4,15.2)',\
drawtext=fontfile=$NOTO:text='③ Ctrl+Alt+B 本地编译判题 · g++ -std=c++17 -O2':fontsize=34:fontcolor=white:box=1:boxcolor=0x000000A6:boxborderw=16:x=(w-text_w)/2:y=h-104:enable='between(t,15.2,21.4)',\
drawtext=fontfile=$NOTO:text='④ 2/2 AC · 打开「详情」逐行对比':fontsize=34:fontcolor=white:box=1:boxcolor=0x000000A6:boxborderw=16:x=(w-text_w)/2:y=h-104:enable='between(t,21.4,28.2)'[v1];\
[2:v]format=yuv420p,fade=t=in:st=0:d=0.4,fade=t=out:st=5.0:d=1.0[v2];\
[v0][v1][v2]concat=n=3:v=1:a=0,format=yuv420p[vout]" \
  -map "[vout]" -map 3:a \
  -c:v libx264 -preset veryfast -threads 2 -crf 18 -r 30 \
  -c:a aac -b:a 96k -shortest -movflags +faststart \
  "$OUT"
echo "=== done ==="
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT"
