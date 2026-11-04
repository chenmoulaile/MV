#!/usr/bin/env python3
"""SW watcher with keep-alive pings so MV3 service worker doesn't idle-kill during capture."""
import json, threading, time, urllib.request, websocket

def get(path):
    with urllib.request.urlopen("http://localhost:9222" + path, timeout=10) as r:
        return json.loads(r.read().decode())

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
mid = [100]
logs = []
stop = threading.Event()

def keepalive():
    while not stop.is_set():
        try:
            mid[0] += 1
            w.send(json.dumps({"id": mid[0], "method": "Runtime.evaluate",
                               "params": {"expression": "1"}}))
        except Exception:
            return
        time.sleep(2)

threading.Thread(target=keepalive, daemon=True).start()

t0 = time.time()
DUR = 50
while time.time() - t0 < DUR:
    try:
        m = json.loads(w.recv())
    except websocket.WebSocketTimeoutException:
        continue
    except Exception:
        break
    meth = m.get("method")
    if meth == "Runtime.consoleAPICalled":
        p = m.get("params", {})
        txt = " ".join(str(a.get("value", a.get("description", "")))[:250] for a in p.get("args", []))
        logs.append(f"[{p.get('type')}] {txt[:300]}")
    elif meth == "Runtime.exceptionThrown":
        logs.append("[EXC] " + json.dumps(m["params"].get("exceptionDetails", {}), ensure_ascii=False)[:300])

stop.set()
try: w.close()
except Exception: pass
open("/tmp/swlog_final.txt", "w").write("\n".join(logs))
print(len(logs), "captured")
