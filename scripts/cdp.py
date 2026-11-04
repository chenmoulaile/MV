#!/usr/bin/env python3
"""Tiny CDP helper: python3 cdp.py <cmd> [args]
cmds: targets | new <url> | nav <tabid-prefix> <url> | eval <tabid-prefix> <js> | close <tabid-prefix>
"""
import json, sys, urllib.request, websocket

HOST = "http://localhost:9222"

def get(path):
    with urllib.request.urlopen(HOST + path, timeout=10) as r:
        return json.loads(r.read().decode())

def find_tab(prefix):
    for t in get("/json/list"):
        if t["type"] == "page" and (prefix in t["url"] or prefix == "any"):
            return t
    return None

def ws(t):
    w = websocket.create_connection(t["webSocketDebuggerUrl"], timeout=20, suppress_origin=True)
    return w

def send(w, method, params=None):
    w.send(json.dumps({"id": 1, "method": method, "params": params or {}}))
    while True:
        m = json.loads(w.recv())
        if m.get("id") == 1:
            return m

def main():
    cmd = sys.argv[1]
    if cmd == "targets":
        for t in get("/json/list"):
            print(t["type"], "|", t.get("title", "")[:40], "|", t["url"][:80], "|", t["id"][:8])
    elif cmd == "new":
        url = sys.argv[2]
        req = urllib.request.Request(HOST + "/json/new?" + url, method="PUT")
        with urllib.request.urlopen(req, timeout=10) as r:
            t = json.loads(r.read().decode())
        print(t["id"][:8])
    elif cmd == "nav":
        t = find_tab(sys.argv[2]); w = ws(t)
        send(w, "Page.navigate", {"url": sys.argv[3]})
        w.close(); print("nav ok")
    elif cmd == "eval":
        t = find_tab(sys.argv[2]); w = ws(t)
        r = send(w, "Runtime.evaluate", {"expression": sys.argv[3], "returnByValue": True, "awaitPromise": False})
        print(json.dumps(r.get("result", {}).get("result", {}), ensure_ascii=False)[:500])
        w.close()
    elif cmd == "close":
        t = find_tab(sys.argv[2])
        urllib.request.urlopen(HOST + f"/json/close/{t['id']}", timeout=5).read()
        print("closed")

if __name__ == "__main__":
    main()
