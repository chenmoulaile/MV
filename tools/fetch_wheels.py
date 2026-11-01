#!/usr/bin/env python3
"""Parallel wheel fetcher: for each pkg, parse tuna simple index, pdl the wheel, then pip install --no-deps all."""
import re, subprocess, sys, urllib.request, html as H
from urllib.parse import urljoin

BASE = "https://pypi.tuna.tsinghua.edu.cn/simple/"
PKGS = {
    "transformers": None, "safetensors": None, "accelerate": None,
    "vocos": None, "torchdiffeq": None, "x-transformers": None,
    "jieba": None, "cn2an": None, "pypinyin": None, "f5-tts": None,
    "ema-pytorch": None, "scipy": None,
}

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "pip/24"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")

def pick(pkg, html):
    links = re.findall(r'href="([^"]+)"', html)
    cp312, py3 = [], []
    for l in links:
        f = urljoin(BASE + pkg + "/", l.split("#sha256=")[0])
        fn = H.unescape(f.rsplit("/", 1)[-1])
        if "cp312" in fn and ("manylinux" in fn or "linux_x86_64" in fn) and "x86_64" in fn:
            cp312.append((fn, f))
        elif fn.endswith("py3-none-any.whl"):
            py3.append((fn, f))
    for cand in (cp312, py3):
        if cand:
            cand.sort(key=lambda x: x[0], reverse=True)
            return cand[0]
    return None

def main():
    fetched = []
    for pkg in PKGS:
        try:
            html = get(BASE + pkg + "/")
            m = pick(pkg, html)
            if not m:
                print(f"[skip] {pkg}: no wheel found"); continue
            fn, url = m
            dest = "/tmp/wheels/" + fn
            import os
            os.makedirs("/tmp/wheels", exist_ok=True)
            r = subprocess.run(["/home/z/my-project/scripts/pdl.sh", url, dest, "12"],
                               capture_output=True, text=True, timeout=560)
            ok = "PDL_OK" in r.stdout
            print(f"[{'OK ' if ok else 'FAIL'}] {fn} ({'fetched' if ok else r.stdout[-200:]})")
            if ok: fetched.append(dest)
        except Exception as e:
            print(f"[ERR ] {pkg}: {e}")
    if fetched:
        r = subprocess.run(["pip", "install", "-q", "--no-deps"] + fetched, capture_output=True, text=True)
        print("pip rc=", r.returncode, r.stderr[-500:] if r.returncode else "")
    for pkg in PKGS:
        mod = pkg.replace("-", "_")
        try:
            __import__(mod)
            print(f"import OK: {pkg}")
        except Exception as e:
            print(f"import MISSING: {pkg} ({type(e).__name__})")

if __name__ == "__main__":
    main()
