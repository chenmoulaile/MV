#!/bin/bash
# 生成配音：11 段中文旁白（xiaochen 音色）
set -e
DIR=/home/z/my-project/download/audio
mkdir -p "$DIR"

tts() {
  local file="$1"; local text="$2"; local speed="${3:-1.0}"
  z-ai tts -i "$text" -o "$DIR/$file.wav" --voice xiaochen --speed "$speed" --format wav
  echo "OK $file $(ffprobe -v quiet -show_entries format=duration -of csv=p=0 "$DIR/$file.wav" 2>/dev/null)"
}

tts vo01 "算法竞赛，你需要一个更顺手的搭档。" 1.0
tts vo02 "CSP-S 2026 第一题，能量水晶。洛谷 P17831，真实赛题，真实页面。" 1.0
tts vo03 "装好 Competitive Companion，轻轻一点。" 1.0
tts vo04 "源文件自动建好，样例、时限、内存限制，全部就位。" 1.0
tts vo05 "算法贴到文件末尾，四十行，一气呵成。" 1.0
tts vo06 "Ctrl Alt B，编译运行，两组样例同时判定。" 1.0
tts vo07 "AC。七毫秒，十五毫秒，时间与内存，一目了然。" 1.0
tts vo08 "点开详情：输入、期望、实际、逐行比对，全部对齐。" 1.0
tts vo09 "一条命令，切换英文界面。" 1.0
tts vo10 "同一份代码，两种语言，一样的利落。" 1.0
tts vo11 "Algorithm Competition Assistant，MIT 开源，一键安装。把时间留给算法本身。" 1.0
echo ALL_DONE
