"""Demo helper plugin: file-queue driven clipboard & paste operations.

Queue dir: /home/z/my-project/workspace/demo/cmds/
Each JSON file: {"op": "set_clip", "path": "..."} or
{"op": "paste_at_eof"} or {"op": "insert_at_eof", "path": "..."}
Executed then deleted.
"""
import sublime, sublime_plugin, os, json, threading, time

QDIR = '/home/z/my-project/workspace/demo/cmds'
os.makedirs(QDIR, exist_ok=True)


def _process():
    try:
        for fn in sorted(os.listdir(QDIR)):
            if not fn.endswith('.json'):
                continue
            path = os.path.join(QDIR, fn)
            try:
                with open(path) as f:
                    spec = json.load(f)
            except Exception:
                os.remove(path)
                continue
            op = spec.get('op')
            win = sublime.active_window()
            view = win.active_view() if win else None
            if op == 'set_clip':
                with open(spec['path'], encoding='utf-8') as f:
                    sublime.set_clipboard(f.read())
            elif op == 'paste_at_eof' and view:
                def do_paste(v=view):
                    v.run_command('demo_move_eof')
                    v.run_command('paste')
                    v.run_command('demo_show_eof')
                sublime.set_timeout(do_paste, 50)
            elif op == 'insert_at_eof' and view:
                with open(spec['path'], encoding='utf-8') as f:
                    text = f.read()

                def do_insert(v=view, t=text):
                    v.run_command('demo_insert_text', {'text': t})
                sublime.set_timeout(do_insert, 50)
            os.remove(path)
    except Exception as e:
        print('[demo_helper]', e)


def _loop():
    while True:
        try:
            sublime.set_timeout(_process, 0)
        except Exception:
            pass
        time.sleep(0.25)


threading.Thread(target=_loop, daemon=True).start()


class DemoMoveEofCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        v.sel().clear()
        v.sel().add(sublime.Region(v.size(), v.size()))
        v.show(v.size(), show_surrounds=False)


class DemoShowEofCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        v = self.view
        v.show(v.size())
        v.run_command('scroll_lines', {'amount': 3})


class DemoInsertTextCommand(sublime_plugin.TextCommand):
    def run(self, edit, text):
        v = self.view
        v.sel().clear()
        v.sel().add(sublime.Region(v.size(), v.size()))
        v.insert(edit, v.size(), text)
        v.show(v.size())
