#!/usr/bin/env python3
"""aca_x.py — 无 WM 桌面控制器。

单次调用内生命周期管理：Xvfb(userns) / Sublime / Chrome。
能力：窗口查找与移动/置顶/聚焦、xdotool 键鼠注入、剪贴板注入、
ffmpeg 截图与录制、光标轨迹 CSV（后期"聚焦鼠标"用）。
"""
import json
import os
import subprocess
import time

HOME = '/home/z'
DISPLAY = ':99'
SUBL = HOME + '/opt/sublime/opt/sublime_text/sublime_text'
CHROME = HOME + '/opt/chrome/opt/google/chrome/chrome'
XDOTOOL = HOME + '/opt/xdotool/usr/bin/xdotool'
ENV = dict(os.environ, DISPLAY=DISPLAY,
           LD_LIBRARY_PATH=HOME + '/opt/xdotool/usr/lib/x86_64-linux-gnu')


# ---------------------------------------------------------------- boot ---

class Desktop:
    def __init__(self, sublime_dir=HOME + '/cp', chrome_url=None,
                 plugin_lang=None):
        self.xvfb = None
        self.subl = None
        self.chrome = None
        self.ffmpeg = None
        self.cursor_log = None
        if plugin_lang:
            self.set_plugin_lang(plugin_lang)
        self._boot_xvfb()
        if chrome_url is not None:
            self._boot_chrome(chrome_url)
        if sublime_dir is not None:
            self._pending_project = sublime_dir
            self._boot_sublime(sublime_dir)

    # -- Xvfb ------------------------------------------------------------
    def _boot_xvfb(self):
        os.makedirs('/tmp/.X11-unix', exist_ok=True)
        # 清理残留服务器与锁文件
        subprocess.run('pkill -9 -f "Xvfb %s"; rm -f /tmp/.X99-lock '
                       '/tmp/.X99-unix 2>/dev/null' % DISPLAY, shell=True,
                       capture_output=True)
        time.sleep(0.6)
        self.xvfb = subprocess.Popen(
            ['unshare', '--user', '--map-root-user', 'Xvfb', DISPLAY,
             '-screen', '0', '1920x1080x24'],
            stdout=open('/tmp/xvfb.log', 'w'), stderr=subprocess.STDOUT,
            preexec_fn=os.setsid)
        for _ in range(50):
            try:
                from Xlib import display
                d = display.Display(DISPLAY)
                d.close()
                return
            except Exception:
                time.sleep(0.2)
        raise RuntimeError('Xvfb failed to start')

    # -- Chrome ------------------------------------------------------------
    def _boot_chrome(self, url):
        os.environ['DISPLAY'] = DISPLAY
        self.prepare_chrome_profile()
        subprocess.run('rm -rf /tmp/com.google.Chrome.* /dev/shm/*:subl_*',
                       shell=True, capture_output=True)
        self.chrome = subprocess.Popen(
            [CHROME, '--user-data-dir=' + HOME + '/chrome-profile',
             '--no-first-run', '--no-default-browser-check',
             '--disable-session-crashed-bubble', '--disable-sync',
             '--window-position=0,0', '--window-size=1920,1080',
             '--load-extension=' + HOME + '/opt/ext/cc',
             '--disable-features=Translate',
             '--lang=zh-CN'] + ([url] if url else []),
            stdout=open('/tmp/chrome.log', 'w'), stderr=subprocess.STDOUT,
            preexec_fn=os.setsid)

    @staticmethod
    def prepare_chrome_profile():
        """预置偏好：关闭登录推广、恢复提示。"""
        prof = HOME + '/chrome-profile/Default'
        os.makedirs(prof, exist_ok=True)
        pf = prof + '/Preferences'
        try:
            data = json.load(open(pf)) if os.path.exists(pf) else {}
        except Exception:
            data = {}
        data.setdefault('signin', {})['allowed'] = False
        data['credentials_enable_service'] = False
        prof = data.setdefault('profile', {})
        prof['exit_type'] = 'Normal'
        prof['exited_cleanly'] = True
        json.dump(data, open(pf, 'w'))

    # -- Sublime -----------------------------------------------------------
    def _boot_sublime(self, project_dir):
        os.environ['DISPLAY'] = DISPLAY
        self._kill_sublime()
        self.subl = subprocess.Popen(
            [SUBL, '-n', project_dir], env=ENV,
            stdout=open('/tmp/sublime_stdout.log', 'w'),
            stderr=subprocess.STDOUT, preexec_fn=os.setsid)
        self._wait_single_window()

    @staticmethod
    def _kill_sublime():
        """杀光 sublime/plugin_host，清 CLI socket 与损坏风险 session。"""
        subprocess.run(
            'pkill -9 -f "opt/[s]ublime_text"; '
            'pkill -9 -f "plugin_[h]ost"; '
            'rm -f "/tmp/Sublime Text."*.socket; '
            'find /home/z/.config/sublime-text -type s -delete 2>/dev/null; '
            'rm -f /dev/shm/*:subl_* 2>/dev/null; '
            'rm -rf /tmp/com.google.Chrome.* 2>/dev/null; '
            'rm -f "/home/z/.config/sublime-text/Local/'
            'Auto Save Session.sublime_session" '
            '/home/z/.config/sublime-text/Local/Session.sublime_session',
            shell=True, capture_output=True)
        time.sleep(1.0)

    def _wait_single_window(self, timeout=25):
        """等待至少一个可见主窗出现（socket 已清，实例必新）。"""
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                x = X()
                wins = x.find(wm_class_contains='sublime_text',
                              min_w=400, min_h=300)
                if wins:
                    return
            except Exception:
                pass
            time.sleep(0.5)

    _pending_project = None

    def set_plugin_lang(self, lang):
        """zh / en：直接改用户设置文件（Sublime 启动时生效）。

        Sublime 保存的 JSON 允许尾逗号，Python 不允许 —— 解析前清一下。
        """
        import re
        p = (HOME + '/.config/sublime-text/Packages/User/'
             'Algorithm Competition Assistant.sublime-settings')
        raw = open(p).read()
        raw = re.sub(r',\s*([}\]])', r'\1', raw)
        d = json.loads(raw)
        d['language'] = lang
        json.dump(d, open(p, 'w'), indent=4)

    def close(self):
        import signal
        for p in (self.ffmpeg, self.cursor_log, self.chrome, self.subl,
                  self.xvfb):
            if p:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGKILL)
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
        # [x] 正则自排除：避免 pkill 把自己的 shell 杀掉
        subprocess.run(
            'pkill -9 -f "opt/[g]oogle/chrome"; '
            'pkill -9 -f "opt/[s]ublime_text"; '
            'pkill -9 -f "map-[r]oot-user Xvfb"; '
            'pkill -9 -f "[x]11grab"; '
            'pkill -9 -f "get[m]ouselocation"; '
            'rm -f /tmp/.X99-lock',
            shell=True, capture_output=True)


def sweep():
    """兜底清扫全部拍摄相关进程（正则自排除）。"""
    import signal as _sg
    subprocess.run(
        'pkill -9 -f "opt/[g]oogle/chrome"; '
        'pkill -9 -f "opt/[s]ublime_text"; '
        'pkill -9 -f "map-[r]oot-user Xvfb"; '
        'pkill -9 -f "[x]11grab"; '
        'pkill -9 -f "get[m]ouselocation"; '
        'rm -f /tmp/.X99-lock',
        shell=True, capture_output=True)


def survivors_report():
    """打印残留进程清单（诊断调用挂起用）。"""
    try:
        out = subprocess.run(
            ['ps', '-eo', 'pid', 'ppid', 'cmd'], capture_output=True,
            text=True).stdout
        keep = []
        for ln in out.splitlines():
            if any(k in ln for k in (
                    'opt/google/chrome', 'opt/sublime_text',
                    'plugin_host', 'Xvfb', 'x11grab', 'xdotool',
                    'getmouselocation')):
                keep.append(ln.strip())
        print('--- survivors ---')
        for ln in keep:
            print(ln)
        print('--- end survivors ---')
    except Exception as e:
        print('survivors_report error:', e)


# ------------------------------------------------------------- windows ---

def _xd(*args):
    return subprocess.run([XDOTOOL] + list(args), env=ENV,
                          capture_output=True, text=True)


class X:
    """连接共享 display 的窗口与输入操作。"""

    def __init__(self):
        from Xlib import display, X
        self._X = X
        self.d = display.Display(DISPLAY)
        self.root = self.d.screen().root

    # -- 窗口 ------------------------------------------------------------
    def all_windows(self):
        out = []

        def walk(w):
            try:
                out.append(w)
            except Exception:
                pass
            try:
                for c in w.query_tree().children:
                    walk(c)
            except Exception:
                pass

        walk(self.root)
        return out

    def find(self, name_contains=None, wm_class_contains=None,
             min_w=400, min_h=300):
        res = []
        for w in self.all_windows():
            try:
                g = w.get_geometry()
                if g.width < min_w or g.height < min_h:
                    continue
                if name_contains:
                    n = (w.get_wm_name() or '')
                    if isinstance(n, bytes):
                        n = n.decode('utf-8', 'replace')
                    if name_contains.lower() not in n.lower():
                        continue
                if wm_class_contains:
                    cls = w.get_wm_class() or ('', '')
                    if wm_class_contains.lower() not in (cls[0] + ' ' +
                                                         cls[1]).lower():
                        continue
                res.append(w)
            except Exception:
                continue
        return res

    def move_resize(self, w, x, y, width, height):
        w.configure(x=x, y=y, width=width, height=height)
        self.d.sync()

    def sublime_window(self):
        cands = [w for w in self.find(wm_class_contains='sublime_text',
                                       min_w=400, min_h=300)]
        if not cands:
            return None
        # 返回面积最大的（真实 UI 主窗）
        def area(w):
            g = w.get_geometry()
            return g.width * g.height
        return max(cands, key=area)

    def chrome_window(self):
        cands = [w for w in self.find(wm_class_contains='google-chrome',
                                      min_w=400, min_h=300)]
        return cands[0] if cands else None

    def raise_win(self, w):
        w.configure(stack_mode=self._X.Above)
        self.d.sync()

    def focus(self, w):
        try:
            w.set_input_focus(self._X.RevertToPointerRoot,
                              self._X.CurrentTime)
            self.d.sync()
        except Exception:
            pass

    def arrow_cursor(self):
        """把根窗口光标换成标准箭头（应用未自定义处生效）。"""
        try:
            font = self.d.open_font('cursor')
            cid = font.create_glyph_cursor(
                font, 68, 69,  # XC_left_ptr 源/掩码字形
                (0, 0, 0), (255, 255, 255))
            self.root.change_attributes(cursor=cid)
            self.d.sync()
        except Exception as e:
            print('arrow_cursor skipped:', e)

    # -- 输入 ------------------------------------------------------------
    def key(self, keys):
        _xd('key', '--clearmodifiers', keys)

    def type_text(self, text, delay=12):
        _xd('type', '--clearmodifiers', '--delay', str(delay), text)

    def move(self, x, y):
        _xd('mousemove', str(x), str(y))

    def click(self, x=None, y=None, btn=1):
        if x is not None:
            self.move(x, y)
        time.sleep(0.15)
        _xd('click', str(btn))

    def scroll(self, x, y, clicks=3, up=False):
        self.move(x, y)
        btn = 4 if up else 5
        for _ in range(clicks):
            _xd('click', str(btn))
            time.sleep(0.12)

    def cursor_pos(self):
        r = _xd('getmouselocation', '--shell')
        vals = {}
        for kv in r.stdout.split():
            if '=' in kv:
                k, v = kv.split('=', 1)
                vals[k] = int(v)
        return vals.get('X', 0), vals.get('Y', 0)

    # -- 剪贴板 ------------------------------------------------------------
    def set_clipboard(self, text):
        with open('/tmp/aca_clip.txt', 'w') as f:
            f.write(text)
        subprocess.run([SUBL, '--command', 'aca_set_clip'], env=ENV,
                       capture_output=True, timeout=10)


# ------------------------------------------------------------ 等待工具 ---

def wait_port(port, timeout=30):
    import socket
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            s = socket.create_connection(('127.0.0.1', port), timeout=1)
            s.close()
            return True
        except OSError:
            time.sleep(0.4)
    return False


def shot(path, ms=0):
    if ms:
        time.sleep(ms)
    subprocess.run(['ffmpeg', '-y', '-f', 'x11grab',
                    '-video_size', '1920x1080', '-i', DISPLAY + '.0',
                    '-frames:v', '1', path], env=ENV, capture_output=True)


# ------------------------------------------------------------- 录制 -----

class Recorder:
    def __init__(self, path, fps=30):
        self.path = path
        self.fps = fps
        self.p = None

    def start(self):
        self.p = subprocess.Popen(
            ['ffmpeg', '-y', '-f', 'x11grab', '-video_size', '1920x1080',
             '-framerate', str(self.fps), '-i', DISPLAY + '.0',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19',
             '-pix_fmt', 'yuv420p', self.path],
            env=ENV, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def stop(self):
        if self.p:
            subprocess.run(['pkill', '-INT', '-f', 'x11grab'],
                           capture_output=True)
            try:
                self.p.wait(timeout=10)
            except Exception:
                self.p.kill()
            self.p = None


class CursorLogger:
    """每 100ms 记录光标位置 -> CSV(t, x, y)，后期聚焦用（python 线程版）。"""

    def __init__(self, path):
        import threading
        self.path = path
        self.stop_flag = False
        self._t = threading.Thread(target=self._run, args=(path,), daemon=True)
        self._t.start()

    def _run(self, path):
        try:
            from Xlib import display
            d = display.Display(DISPLAY)
            with open(path, 'w') as f:
                while not self.stop_flag:
                    p = d.screen().root.query_pointer()
                    f.write('%.3f,%d,%d\n' % (time.time(), p.root_x, p.root_y))
                    f.flush()
                    time.sleep(0.1)
        except Exception as e:
            print('cursor logger died:', e, flush=True)

    def stop(self):
        self.stop_flag = True
        time.sleep(0.2)


# --------------------------------------------------------------- 脚本 ----

def mark(msg):
    """动作时间戳标记（与光标 CSV 同钟）。"""
    print('[t=%.3f] %s' % (time.time(), msg), flush=True)


def reset_state():
    """清空演示目录（回到“还没抓题”的状态）。"""
    import glob
    import shutil
    for f in glob.glob(HOME + '/cp/*'):
        try:
            shutil.rmtree(f) if os.path.isdir(f) else os.remove(f)
        except Exception:
            pass


def demo_file():
    import glob
    fs = glob.glob(HOME + '/cp/*.cpp')
    return fs[0] if fs else None


def trim_to_header():
    """把演示文件裁回 companion 刚建好的 4 行头（未粘贴状态）。"""
    f = demo_file()
    if f:
        lines = open(f, encoding='utf-8').readlines()
        open(f, 'w', encoding='utf-8').writelines(lines[:4])
