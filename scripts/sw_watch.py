#!/usr/bin/env python3
"""Attach to CC service worker, enable console capture, wait for click, dump logs."""
import json, threading, time, urllib.request, websocket

def get(path):
    with urllib.request.urlopen("http://localhost:9222" + path, timeout=10) as r:
        return json.loads(r.read().decode())

# wait for SW target
sw = None
for i in range(40):
    try:
        ts = get("/json/list")
        sw = [t for t in ts if t["type"] == "service_worker"]
        if sw:
            break
    except Exception:
        pass
    time.sleep(0.5)
print("SW:", sw[0]["url"] if sw else None, flush=True)
if not sw:
    raise SystemExit(1)

w = websocket.create_connection(sw[0]["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
w.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
w.send(json.dumps({"id": 2, "method": "Log.enable"}))
t0 = time.time()
logs = []
while time.time() - t0 < 25:
    try:
        m = json.loads(w.recv())
    except Exception:
        break
    meth = m.get("method")
    if meth in ("Runtime.consoleAPICalled", "Runtime.exceptionThrown", "Log.entryAdded"):
        p = m.get("params", {})
        if meth == "Log.entryAdded":
            e = p["entry"]
            logs.append(f"[log] {e.get('level')}: {e.get('text')[:200]}")
        elif meth == "Runtime.exceptionThrown":
            d = p.get("exceptionDetails", {})
            logs.append(f"[exc] {json.dumps(d, ensure_ascii=False)[:300]}")
        else:
            args = p.get("args", [])
            txt = " ".join(str(a.get("value", a.get("description", "")))[:120] for a in args)
            logs.append(f"[{p.get('type')}] {txt[:250]}")
w.close()
print("\n".join(logs) if logs else "NO_CAPTURED_LOGS")
