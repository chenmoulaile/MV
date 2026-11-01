#!/usr/bin/env python3
"""Sublime Text + 插件用户目录配置（免 root）。

- 插件源码复制到 Packages/Algorithm Competition Assistant
- User/Preferences.sublime-settings: DejaVu Sans Mono + Mariana 配色
- User/Algorithm Competition Assistant.sublime-settings: language=zh 等
- User/setclip.py: 提供 aca_set_clip 命令，从 /tmp/aca_clip.txt 设置剪贴板
"""
import json
import os
import shutil

HOME = '/home/z'
CFG = os.path.join(HOME, '.config', 'sublime-text')
PKGS = os.path.join(CFG, 'Packages')
USER = os.path.join(PKGS, 'User')
PLUGIN_SRC = '/home/z/my-project/workspace/algorithm-competition-assistant'
PLUGIN_DST = os.path.join(PKGS, 'Algorithm Competition Assistant')
CP_DIR = os.path.join(HOME, 'cp')

for d in (CFG, PKGS, USER, CP_DIR):
    os.makedirs(d, exist_ok=True)

# 1. 插件本体
if os.path.isdir(PLUGIN_DST):
    shutil.rmtree(PLUGIN_DST)
shutil.copytree(PLUGIN_SRC, PLUGIN_DST,
                ignore=shutil.ignore_patterns('.git', 'tests'))

# 2. 全局编辑器偏好
prefs = {
    "color_scheme": "Mariana.sublime-color-scheme",
    "font_face": "DejaVu Sans Mono",
    "font_size": 13,
    "tab_size": 4,
    "translate_tabs_to_spaces": False,
    "detect_indentation": False,
    "index_files": False,
    "update_check": False,
    "show_definitions": False,
    "word_wrap": False,
    "remember_open_files": False,
    "hot_exit": False,
    "ignored_packages": ["Vintage"],
}
with open(os.path.join(USER, 'Preferences.sublime-settings'), 'w') as f:
    json.dump(prefs, f, indent=4)

# 3. 插件设置（中文界面 + 自动建文件目录）
acaset = {
    "language": "zh",
    "auto_create_dir": CP_DIR,
    "companion_auto_listen": True,
}
with open(os.path.join(USER, 'Algorithm Competition Assistant.sublime-settings'), 'w') as f:
    json.dump(acaset, f, indent=4)

# 4. 剪贴板注入小插件
setclip = '''import sublime
import sublime_plugin


class AcaSetClipCommand(sublime_plugin.ApplicationCommand):
    def run(self):
        try:
            with open('/tmp/aca_clip.txt', 'r', encoding='utf-8') as f:
                sublime.set_clipboard(f.read())
            print('[aca_set_clip] clipboard set, %d chars' % len(f.read() if False else ''))
        except Exception as e:
            print('[aca_set_clip] error: %s' % e)
'''
with open(os.path.join(USER, 'setclip.py'), 'w') as f:
    f.write(setclip)

print('Configured:', CFG)
print('Plugin at:', PLUGIN_DST)
print('Demo dir:', CP_DIR)
