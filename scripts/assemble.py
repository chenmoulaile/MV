#!/usr/bin/env python3
"""最终成片装配：12 段拼接 + 推镜聚焦 + BGM/VO/SFX 混音。

时间轴（秒）：
S0 片头卡片      0.0- 5.5   zoompan 缓推          vo01
S1 洛谷浏览      5.5-14.3   A 0-8.8               vo02
S2 点击扩展     14.3-18.1   A 8.8-12.6 推镜图标    vo03 + click
S3 文件就绪     18.1-22.6   B 0-4.5               vo04
S4 粘贴编译     22.6-29.6   B 4.5-11.5 缓推        vo05
S5 运行AC       29.6-34.1   B 11.5-16             vo06 + chime
S6 AC特写       34.1-40.0   B 16-21.9 推镜卡片     vo07
S7 详情         40.0-46.1   B 21.9-28.03          vo08
S8 切换英文     46.1-57.1   B2 0-11               vo09 + click
S9 英文卡片     57.1-61.6   B2 11-15.5
S10 中英对比    61.6-67.6   card_compare 缓推      vo10 + riser
S11 片尾        67.6-76.6   card_end 缓推          vo11
"""
import os
import subprocess

F = '/home/z/my-project/download/footage'
A = '/home/z/my-project/download/audio'
TMP = '/home/z/my-project/download/footage/_seg'
os.makedirs(TMP, exist_ok=True)
FINAL = '/home/z/my-project/download/algorithm-competition-assistant-promo.mp4'

FPS = 30
V = ['-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '15',
     '-pix_fmt', 'yuv420p', '-r', str(FPS)]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1200:])
        raise SystemExit('FFMPEG FAILED: ' + ' '.join(cmd[:6]))


def crop_zoom(src, ss, to, out, cx, cy, zoom_from, zoom_to, dur):
    """2x 超采样 + 动态 crop 推镜 + 缩放回 1080p。

    cx, cy: 1080p 坐标系中的推镜中心；zoom: 相对全画面倍率。
    起点中心=画面中心，终点中心=(cx,cy)，zoom 线性变化。
    """
    z0, z1 = zoom_from, zoom_to

    wz = ('3840/({z0}+({z1}-{z0})*min(t/{d},1))'
          .format(z0=z0, z1=z1, d=dur))
    hz = ('2160/({z0}+({z1}-{z0})*min(t/{d},1))'
          .format(z0=z0, z1=z1, d=dur))
    vf = ("scale=3840:2160:flags=bilinear,"
          "crop=w='{w}':h='{h}':"
          "x='({cx2}-out_w/2)*min(t/{d},1)':"
          "y='({cy2}-out_h/2)*min(t/{d},1)',"
          "scale=1920:1080:flags=bilinear"
          ).format(w=wz, h=hz, cx2=cx * 2, cy2=cy * 2, d=dur)
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ss), '-i', src,
         '-t', str(to), '-vf', vf] + V + [out])


def plain(src, ss, to, out, dur):
    run(['ffmpeg', '-y', '-v', 'error', '-ss', str(ss), '-i', src,
         '-t', str(dur)] + V + [out])


def still(img, out, dur, z=1.06):
    """静帧缓推：2x 超采样 + zoompan 中心放大（用 in_time 变量）。"""
    vf = ("scale=3840:2160:flags=bilinear,"
          "zoompan=z='1+({z}-1)*min(in_time/{d},1)':"
          "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
          "d=1:s=1920x1080:fps={fps}").format(z=z, d=dur, fps=FPS)
    run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-i', img,
         '-t', str(dur), '-vf', vf] + V + [out])


print('S0 title');    still(F + '/card_title.png',   TMP + '/s00.mp4', 5.5, 1.06)
print('S1 browse');   plain(F + '/A_chrome.mp4', 0, 8.8, TMP + '/s01.mp4', 8.8)
print('S2 click');    crop_zoom(F + '/A_chrome.mp4', 8.8, 3.8, TMP + '/s02.mp4',
                                cx=1730, cy=90, zoom_from=1.0, zoom_to=2.3, dur=3.0)
print('S3 ready');    plain(F + '/B_sublime_zh.mp4', 0, 4.5, TMP + '/s03.mp4', 4.5)
print('S4 paste+run'); crop_zoom(F + '/B_sublime_zh.mp4', 4.5, 9.0, TMP + '/s04.mp4',
                                cx=960, cy=540, zoom_from=1.0, zoom_to=1.25, dur=6.5)
print('S5 AC zoom');  crop_zoom(F + '/B_sublime_zh.mp4', 13.5, 5.3, TMP + '/s05.mp4',
                                cx=1150, cy=120, zoom_from=1.0, zoom_to=1.9, dur=3.8)
print('S6 detail');   plain(F + '/B_sublime_zh.mp4', 18.8, 9.23, TMP + '/s06.mp4', 9.23)
print('S7 switch');   plain(F + '/B2_sublime_en.mp4', 0, 11, TMP + '/s07.mp4', 11)
print('S8 en cards'); plain(F + '/B2_sublime_en.mp4', 11, 4.5, TMP + '/s08.mp4', 4.5)
print('S9 compare');  still(F + '/card_compare.png', TMP + '/s09.mp4', 6.0, 1.08)
print('S10 end');     still(F + '/card_end.png',     TMP + '/s10.mp4', 9.0, 1.05)

# ---- 拼接 ----
with open(TMP + '/list.txt', 'w') as f:
    for i in range(11):
        f.write("file 's%02d.mp4'\n" % i)
run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0',
     '-i', TMP + '/list.txt', '-c', 'copy', TMP + '/video.mp4'])
print('concat done')

# ---- 混音 ----
VO = {
    'vo01': 0.7, 'vo02': 5.7, 'vo03': 14.6, 'vo04': 18.4, 'vo05': 23.5,
    'vo06': 28.2, 'vo07': 32.0, 'vo08': 38.5, 'vo09': 49.0, 'vo10': 62.2,
    'vo11': 68.4,
}
SFX = [
    (A + '/whoosh.wav', 14.3, 0.5), (A + '/click.wav', 15.0, 0.8),
    (A + '/whoosh.wav', 18.1, 0.5), (A + '/chime.wav', 31.7, 0.55),
    (A + '/whoosh.wav', 46.1, 0.5), (A + '/click.wav', 49.6, 0.7),
    (A + '/riser.wav', 60.4, 0.5), (A + '/whoosh.wav', 61.6, 0.5),
    (A + '/whoosh.wav', 67.6, 0.55),
]

inputs = ['-i', TMP + '/video.mp4', '-i', A + '/bgm.wav']
for name in VO:
    inputs += ['-i', A + '/%s.wav' % name]
for path, _, _ in SFX:
    inputs += ['-i', path]

n_video = 2
n_vo = len(VO)
n_sfx = len(SFX)
fc = []
# BGM：音量压低 + 结尾淡出
fc.append('[1:a]volume=0.16,afade=t=out:st=71.6:d=5[bgm]')
# VO：延迟 + 限制响度
for i, (name, at) in enumerate(VO.items()):
    ms = int(at * 1000)
    fc.append('[%d:a]adelay=%d|%d,volume=1.35[v%d]'
              % (n_video + i, ms, ms, i))
# SFX
for i, (path, at, vol) in enumerate(SFX):
    ms = int(at * 1000)
    fc.append('[%d:a]adelay=%d|%d,volume=%.2f[x%d]'
              % (n_video + n_vo + i, ms, ms, vol, i))

mix_ins = '[bgm]'
for i in range(n_vo):
    mix_ins += '[v%d]' % i
for i in range(n_sfx):
    mix_ins += '[x%d]' % i
fc.append('%samix=inputs=%d:normalize=0,alimiter=limit=0.95[aout]'
          % (mix_ins, 1 + n_vo + n_sfx))

run(['ffmpeg', '-y', '-v', 'error'] + inputs +
    ['-filter_complex', ';'.join(fc),
     '-map', '0:v', '-map', '[aout]', '-shortest',
     '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k',
     '-movflags', '+faststart', FINAL])

print('FINAL:', FINAL, os.path.getsize(FINAL) // 1024, 'KB')
r = subprocess.run(['ffprobe', '-v', 'quiet', '-show_entries',
                    'format=duration', '-of', 'csv=p=0', FINAL],
                   capture_output=True, text=True)
print('duration:', r.stdout.strip())
