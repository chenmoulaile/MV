#!/usr/bin/env python3
"""Parallel-range downloader with per-part resume."""
import sys, subprocess, os, math

url, out, nconn = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12
r = subprocess.run(['curl', '-sIL', '--max-time', '30', url], capture_output=True, text=True)
size = 0
for line in r.stdout.lower().splitlines():
    if line.startswith('content-length:'):
        size = int(line.split(':')[1].strip())
if size <= 0:
    print('no size, fallback single')
    subprocess.run(['curl', '-sL', '-o', out, url])
    sys.exit(0)
print('size', size)
chunk = math.ceil(size / nconn)
procs = []
expect = []
for i in range(nconn):
    s, e = i * chunk, min((i + 1) * chunk - 1, size - 1)
    p = f'{out}.p{i}'
    expect.append((p, s, e, e - s + 1))

def have(p):
    return os.path.getsize(p) if os.path.exists(p) else 0

def worker(p, s, e):
    for _ in range(30):
        h = have(p)
        need = e - s + 1
        if h >= need:
            return
        rs = s + h
        subprocess.run(['curl', '-sL', '--max-time', '240', '-r', f'{rs}-{e}', '-o', p, url], capture_output=True)
    return

for p, s, e, need in expect:
    if have(p) < need:
        procs.append(subprocess.Popen(worker, args=(p, s, e)))
for p in procs:
    p.wait()
ok = all(have(p) >= need for p, s, e, need in expect)
if not ok:
    print('INCOMPLETE')
    sys.exit(1)
with open(out, 'wb') as f:
    for p, s, e, need in expect:
        with open(p, 'rb') as g:
            f.write(g.read())
        os.remove(p)
print('done', os.path.getsize(out))
