#!/usr/bin/env python3
"""Parallel-range downloader for throttled hosts."""
import sys, subprocess, os, math

url, out, nconn = sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 12
# get size
r = subprocess.run(['curl', '-sIL', '--max-time', '30', url], capture_output=True, text=True)
size = 0
for line in r.stdout.lower().splitlines():
    if line.startswith('content-length:'):
        size = int(line.split(':')[1].strip())
if size <= 0:
    print('no size, fallback single'); subprocess.run(['curl', '-sL', '-o', out, url]); sys.exit(0)
print('size', size)
chunk = math.ceil(size / nconn)
parts = []
procs = []
for i in range(nconn):
    s, e = i * chunk, min((i + 1) * chunk - 1, size - 1)
    p = f'{out}.p{i}'
    parts.append(p)
    procs.append(subprocess.Popen(['curl', '-sL', '--max-time', '900', '-r', f'{s}-{e}', '-o', p, url]))
for p in procs:
    p.wait()
with open(out, 'wb') as f:
    for pt in parts:
        with open(pt, 'rb') as g:
            f.write(g.read())
        os.remove(pt)
print('done', os.path.getsize(out))
