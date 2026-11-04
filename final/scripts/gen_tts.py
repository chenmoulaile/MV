#!/usr/bin/env python3
"""Batch TTS via GPT-SoVITS api_v2 (local HTTP). Lines -> wav files."""
import json, subprocess, sys, time, os, urllib.request

BASE = '/home/z/my-project/workspace/tts'
GS = f'{BASE}/GPT-SoVITS'
OUT = f'{BASE}/vo'
os.makedirs(OUT, exist_ok=True)

REF = sys.argv[1] if len(sys.argv) > 1 else f'{BASE}/ref/hina_ref.wav'
PROMPT = sys.argv[2] if len(sys.argv) > 2 else ''

LINES = [
	('vo01', '平时写算法题，是不是老得在浏览器和编辑器中间来回切？题面看一半，样例还得自己手动贴，真的挺烦的。'),
	('vo02', '今天给大家看一个 Sublime 的插件，专门治这个。'),
	('vo03', '我随便找了一道题，浏览器里正常打开，网址复制一下。'),
	('vo04', '回到编辑器，把这个网址丢给它，题面、样例，它自己全抓进来了。'),
	('vo05', '代码就贴在下面，该咋写咋写，跟平时一模一样。'),
	('vo06', '写完按一下运行，几个测试点、用时多少、吃多少内存，直接排在右边。'),
	('vo07', '全绿，这题就算过了，连答案都不用自己对。'),
	('vo08', '界面中英文都有，按个人口味随便切。'),
	('vo09', '另外，对拍、练习统计、比赛计时器这些小工具，它也全给你备好了。'),
	('vo10', '这个插件已经上架官方的 Package Control 了，装起来就是搜个名字的事。'),
	('vo11', '这期先混个脸熟，具体怎么玩，下期接着聊。'),
]


def start_api():
	proc = subprocess.Popen(
		['/home/z/.venv/bin/python3', 'api_v2.py', '-a', '127.0.0.1', '-p', '9880', '-c',
		 'GPT_SoVITS/configs/tts_infer.yaml'],
		cwd=GS, stdout=open(f'{BASE}/api_v2.log', 'w'), stderr=subprocess.STDOUT)
	for i in range(120):
		time.sleep(2)
		try:
			urllib.request.urlopen('http://127.0.0.1:9880/tts', timeout=2)
		except Exception as e:
			msg = str(e)
			if '400' in msg or '422' in msg:
				return proc
			continue
	return proc


def gen(name, text):
	req = {
		'text': text, 'text_lang': 'zh',
		'ref_audio_path': REF, 'prompt_text': PROMPT, 'prompt_lang': 'zh',
		'text_split_method': 'cut0', 'speed_factor': 1.0,
		'seed': -1, 'media_type': 'wav', 'streaming_mode': False,
	}
	r = urllib.request.Request('http://127.0.0.1:9880/tts',
							   data=json.dumps(req).encode(),
							   headers={'Content-Type': 'application/json'})
	with urllib.request.urlopen(r, timeout=300) as resp:
		data = resp.read()
	if data[:4] != b'RIFF':
		print(name, 'FAIL', data[:200])
		return False
	with open(f'{OUT}/{name}.wav', 'wb') as f:
		f.write(data)
	print(name, 'OK', len(data))
	return True


if __name__ == '__main__':
	proc = start_api()
	ok = 0
	for name, text in LINES:
		if not os.path.exists(f'{OUT}/{name}.wav') or os.environ.get('REGEN'):
			if gen(name, text):
				ok += 1
		else:
			ok += 1
			print(name, 'cached')
	print(f'done {ok}/{len(LINES)}')
	if '--keep' not in sys.argv:
		proc.terminate()
