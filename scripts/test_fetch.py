#!/usr/bin/env python3
"""端到端验证插件抓题代码能否解析洛谷 P17831 (crystal)。

直接导入被测插件的真实代码（core/cph_fetch.py + core/cph_html.py），
只伪造 sublime 模块。验证：标题、样例数量、样例内容、状态栏摘要。
"""
import sys
import types
import importlib

PLUGIN_PARENT = '/home/z/my-project/workspace'
PLUGIN_DIR_NAME = 'algorithm-competition-assistant'

# ---- 伪造 sublime 模块（cph_settings 顶层 import sublime） ----
fake_sublime = types.ModuleType('sublime')
fake_sublime.load_settings = lambda name: types.SimpleNamespace(
    get=lambda *a, **k: None, set=lambda *a, **k: None)
fake_sublime.save_settings = lambda name: None
sys.modules['sublime'] = fake_sublime

sys.path.insert(0, PLUGIN_PARENT)

fetch_mod = importlib.import_module(
    PLUGIN_DIR_NAME + '.core.cph_fetch')

URL = 'https://www.luogu.com.cn/problem/P17831'

html, err = fetch_mod.fetch(URL)
if err:
    print('FETCH_ERROR:', err)
    sys.exit(1)

print('HTML bytes:', len(html))
title = fetch_mod.title_of(html)
print('TITLE:', repr(title))

pairs = fetch_mod.samples(html)
print('SAMPLES:', len(pairs))
for i, (inp, outp) in enumerate(pairs, 1):
    print('--- sample %d input ---' % i)
    print(inp)
    print('--- sample %d output ---' % i)
    print(outp)

status_label = title or fetch_mod.summarize(html)
print('STATUS LABEL:', repr(status_label))
print('STATUS BAR WOULD SHOW: [Algorithm Competition Assistant] %s | %s'
      % (status_label, fetch_mod.describe_samples(pairs)))

md = fetch_mod.statement(html, URL)
print('--- statement markdown head (first 600 chars) ---')
print(md[:600])
