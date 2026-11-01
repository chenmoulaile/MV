#!/usr/bin/env python3
"""Inspect the extension's id + registered commands + options, and optionally
trigger the send through the extension's own action (fallback path)."""
import json
import sys
import time
import urllib.request
from websocket import create_connection


def eval_on(expr, want='chrome://extensions', timeout=15, port=9222):
    data = json.loads(urllib.request.urlopen(
        'http://127.0.0.1:%d/json' % port, timeout=5).read())
    page = [t for t in data if t['type'] == 'page' and want in t.get('url', '')]
    if not page:
        pages = [t for t in data if t['type'] == 'page']
        ws = create_connection(pages[0]['webSocketDebuggerUrl'], timeout=10)
        ws.send(json.dumps({'id': 1, 'method': 'Page.navigate',
                            'params': {'url': want}}))
        time.sleep(3)
        try:
            ws.close()
        except Exception:
            pass
        data = json.loads(urllib.request.urlopen(
            'http://127.0.0.1:%d/json' % port, timeout=5).read())
        page = [t for t in data if t['type'] == 'page'
                and want in t.get('url', '')]
    ws = create_connection(page[0]['webSocketDebuggerUrl'], timeout=timeout)
    ws.send(json.dumps({'id': 1, 'method': 'Runtime.evaluate',
                        'params': {'expression': expr, 'awaitPromise': True,
                                   'returnByValue': True}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get('id') == 1:
            ws.close()
            res = msg['result']
            if 'exceptionDetails' in res:
                raise RuntimeError(str(res['exceptionDetails'])[:400])
            return res.get('result', {}).get('value')


if __name__ == '__main__':
    info = eval_on(
        "(new Promise(r => chrome.developerPrivate.getExtensionsInfo("
        "es => r(es.map(e => ({id: e.id, name: e.name, state: e.state,"
        " commands: e.commands, optionsPageUrl: e.optionsPageUrl,"
        " views: e.views && e.views.map(v => v.url)}))))))")
    print(json.dumps(info, indent=1, ensure_ascii=False)[:1800])
