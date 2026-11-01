#!/usr/bin/env python3
"""片头/片尾卡片 + 中英对比分屏帧（PIL 绘制，1920x1080）。"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
DIR = '/home/z/my-project/download/footage'
FONTS = '/usr/share/fonts/truetype'
F_CN_BOLD = FONTS + '/chinese/NotoSansSC-Bold.ttf'
F_CN_REG = FONTS + '/chinese/NotoSansSC-Regular.ttf'
F_MONO = FONTS + '/dejavu/DejaVuSansMono.ttf'
F_MONO_B = FONTS + '/dejavu/DejaVuSansMono-Bold.ttf'


def gradient(c1, c2):
    base = Image.new('RGB', (W, H))
    px = base.load()
    for y in range(H):
        k = y / H
        r = int(c1[0] + (c2[0] - c1[0]) * k)
        g = int(c1[1] + (c2[1] - c1[1]) * k)
        b = int(c1[2] + (c2[2] - c1[2]) * k)
        for x in range(0, W, 4):
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = (r, g, b)
    return base


def vignette(img):
    mask = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.ellipse((-W * 0.25, -H * 0.35, W * 1.25, H * 1.35), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(220))
    black = Image.new('RGB', (W, H), (0, 0, 0))
    return Image.composite(img, black, mask.point(lambda v: 60 + v * 195 // 255))


def dot_grid(img, step=46, alpha=26):
    d = ImageDraw.Draw(img, 'RGBA')
    for y in range(step, H, step):
        for x in range(step, W, step):
            d.point((x, y), fill=(120, 160, 220, alpha))
    return img


def title_card():
    img = gradient((9, 13, 26), (16, 27, 48))
    img = dot_grid(img)
    img = vignette(img)
    d = ImageDraw.Draw(img, 'RGBA')

    # 顶部绿 + 徽标（致敬 Competitive Companion 的绿加号）
    bx, by = W // 2 - 34, 208
    d.rounded_rectangle((bx, by, bx + 68, by + 68), 18,
                        fill=(46, 160, 67, 255))
    d.rectangle((bx + 28, by + 14, bx + 40, by + 54), fill=(255, 255, 255, 235))
    d.rectangle((bx + 14, by + 28, bx + 54, by + 40), fill=(255, 255, 255, 235))

    f_sub = ImageFont.truetype(F_MONO, 34)
    f_main = ImageFont.truetype(F_CN_BOLD, 92)
    f_tag = ImageFont.truetype(F_CN_REG, 40)
    f_foot = ImageFont.truetype(F_MONO, 30)

    def center(y, text, font, fill):
        tw = d.textlength(text, font=font)
        d.text(((W - tw) / 2, y), text, font=font, fill=fill)

    center(330, 'SUBLIME TEXT 4  ·  COMPETITIVE PROGRAMMING',
           f_sub, (110, 168, 220))
    center(410, 'Algorithm Competition Assistant',
           ImageFont.truetype(F_MONO_B, 74), (238, 244, 250))
    center(530, '算法竞赛测试助手 · 判题 · 抓题 · 双语界面',
           f_tag, (172, 190, 210))
    center(760, 'v3.0.7   ·   MIT License', f_foot, (120, 138, 158))
    center(810, 'github.com/chenmoulaile/algorithm-competition-assistant',
           f_foot, (90, 120, 150))
    img.save(DIR + '/card_title.png')
    print('card_title done')


def end_card():
    img = gradient((9, 13, 26), (13, 21, 38))
    img = dot_grid(img)
    img = vignette(img)
    d = ImageDraw.Draw(img, 'RGBA')

    f_main = ImageFont.truetype(F_CN_BOLD, 84)
    f_sub = ImageFont.truetype(F_CN_REG, 40)
    f_foot = ImageFont.truetype(F_MONO, 32)

    def center(y, text, font, fill):
        tw = d.textlength(text, font=font)
        d.text(((W - tw) / 2, y), text, font=font, fill=fill)

    center(400, '把时间留给算法本身。', f_main, (238, 244, 250))
    center(560, '抓题 · 判题 · 双语界面 · 一键开源', f_sub, (150, 172, 196))
    center(770, 'github.com/chenmoulaile/algorithm-competition-assistant',
           f_foot, (110, 168, 220))
    center(825, 'MIT Licensed  ·  Algorithm Competition Assistant v3.0.7',
           f_foot, (110, 128, 148))
    img.save(DIR + '/card_end.png')
    print('card_end done')


def compare_frame():
    """中英对比分屏：各取原帧右半（判题面板），1:1 拼接。"""
    a = Image.open(DIR + '/_zh_detail.png')
    b = Image.open(DIR + '/_en_detail.png')
    img = Image.new('RGB', (W, H), (10, 14, 26))
    img.paste(a.crop((960, 0, 1920, 1080)), (0, 0))
    img.paste(b.crop((960, 0, 1920, 1080)), (960, 0))
    d = ImageDraw.Draw(img, 'RGBA')
    d.rectangle((958, 0, 962, H), fill=(70, 90, 110, 255))
    f = ImageFont.truetype(F_CN_BOLD, 44)
    d.rounded_rectangle((40, 40, 260, 112), 16, fill=(20, 30, 48, 220))
    d.text((64, 52), '中文界面', font=f, fill=(240, 246, 252))
    d.rounded_rectangle((W - 260, 40, W - 40, 112), 16, fill=(20, 30, 48, 220))
    tw = d.textlength('English UI', font=f)
    d.text((W - 260 + (220 - tw) / 2, 52), 'English UI', font=f,
           fill=(240, 246, 252))
    img.save(DIR + '/card_compare.png')
    print('card_compare done')


def grab(src, out, ss):
    subprocess.run(['ffmpeg', '-y', '-v', 'quiet', '-ss', ss, '-i', src,
                    '-frames:v', '1', out], check=True)


title_card()
end_card()
grab(DIR + '/B_sublime_zh.mp4', DIR + '/_zh_detail.png', '23.5')
grab(DIR + '/B2_sublime_en.mp4', DIR + '/_en_detail.png', '21')
compare_frame()
print('ALL_DONE')
