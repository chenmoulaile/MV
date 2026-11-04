#!/usr/bin/env python3
"""Build VO track + BGM track + final encode (filter graphs via script files)."""
import subprocess, os
os.chdir("/home/z/my-project/workspace/assembly")

def run(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL:", cmd[:200], "\nSTDERR:", r.stderr[-700:])
        raise SystemExit(1)

V = "/home/z/my-project/workspace/vo_out"
A = "/home/z/my-project/workspace/assets"
VO_START = {1:0.7, 2:4.6, 3:12.0, 4:27.8, 5:34.0, 6:39.9, 7:48.4, 8:52.5, 9:60.9, 10:69.4, 11:79.3, 12:88.3}
total = 95.5

# ---- VO track ----
inputs = " ".join(f"-i {V}/l{i:02d}.wav" for i in range(1, 13))
with open("vo_fc.txt", "w") as f:
    for k, i in enumerate(range(1, 13)):
        ms = int(VO_START[i] * 1000)
        f.write(f"[{k}:a]aresample=44100,volume=1.9,adelay={ms}|{ms}[a{k}];\n")
    f.write("".join(f"[a{k}]" for k in range(12)))
    f.write(f"amix=inputs=12:normalize=0,apad=whole_dur={total}[vo]\n")
run(f"ffmpeg -y -v error {inputs} -filter_complex_script vo_fc.txt -map [vo] -ar 44100 -ac 2 vo_track.wav")
print("vo ok")

# ---- BGM ----
run(f'ffmpeg -y -v error -i {A}/bgm.wav -af "atrim=0:{total},volume=0.24,afade=t=in:st=0:d=1.5,afade=t=out:st={total-3}:d=3,aresample=44100" -ar 44100 -ac 2 bgm_track.wav')
print("bgm ok")

# ---- final ----
with open("final_fc.txt", "w") as f:
    f.write("[0:v]ass=subs.ass[v];\n[1:a][2:a]amix=inputs=2:duration=first:normalize=0[a]\n")
run("ffmpeg -y -v error -i video_noaudio.mp4 -i vo_track.wav -i bgm_track.wav "
    "-filter_complex_script final_fc.txt -map [v] -map [a] "
    "-c:v libx264 -preset fast -crf 19 -c:a aac -b:a 192k final_mv.mp4")
print("FINAL DONE")
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", "final_mv.mp4"],
                   capture_output=True, text=True)
print(r.stdout)
