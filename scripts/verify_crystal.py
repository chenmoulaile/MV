#!/usr/bin/env python3
"""CSP-S 2026 T1 crystal: verify user's solution vs independent brute force,
then emit the Competitive Companion JSON with the official Luogu P17831 samples."""
import itertools, json, os, random, subprocess, sys

WORK = "/home/z/my-project/workspace/demo"
CODE = "/tmp/codetest/crystal.cpp"
BIN = "/tmp/codetest/crystal"
os.makedirs(WORK, exist_ok=True)
os.makedirs("/tmp/codetest", exist_ok=True)

# 1. compile the user's code exactly as the plugin will (g++ -std=c++17 -O2)
subprocess.run(["g++", "-std=c++17", "-O2", "-o", BIN, CODE], check=True)

def user_sol(n, m, a):
    inp = f"{n} {m}\n" + " ".join(map(str, a)) + "\n"
    out = subprocess.run([BIN], input=inp, capture_output=True, text=True, timeout=10)
    return int(out.stdout.strip())

def brute(n, m, a):
    """Independent check: enumerate every subset, cost = raise all to subset max."""
    best = 0
    for r in range(1, n + 1):
        for comb in itertools.combinations(range(n), r):
            mx = max(a[i] for i in comb)
            cost = sum(mx - a[i] for i in comb)
            if cost <= m and r > best:
                best = r
    return best

# 2. official samples (Luogu P17831)
official = [
    {"input": "5 5\n1 2 4 8 9\n", "output": "3\n"},
    {"input": "5 8\n-3 -1 2 2 7\n", "output": "4\n"},
]
for t in official:
    n, m = map(int, t["input"].split("\n")[0].split())
    a = list(map(int, t["input"].split("\n")[1].split()))
    got = user_sol(n, m, a)
    want = int(t["output"])
    print(f"official sample: got={got} want={want} {'OK' if got == want else 'FAIL'}")
    assert got == want

# 3. randomized cross-check against subset-enumeration brute force
random.seed(20261031)
bad = 0
for case in range(3000):
    n = random.randint(1, 10)
    a = [random.randint(-20, 20) for _ in range(n)]
    m = random.randint(0, 60)
    u, b = user_sol(n, m, a), brute(n, m, a)
    if u != b:
        bad += 1
        print(f"MISMATCH n={n} m={m} a={a}: user={u} brute={b}")
        if bad > 5:
            sys.exit(1)
print(f"random cross-check: 3000 cases, mismatches={bad}")
assert bad == 0

# 4. extra edge cases
edges = [
    (1, 0, [5], 1),
    (5, 0, [3, 3, 3, 3, 3], 5),
    (5, 10**18, [-10**12, 10**12, 0, 7, -7], 5),
]
for n, m, a, want in edges:
    got = user_sol(n, m, a)
    print(f"edge n={n} m={m}: got={got} want={want} {'OK' if got == want else 'FAIL'}")
    assert got == want

# 5. big case inside official constraints (5e5, |a|<=1e12, m<=1e18) for the
#    benchmark/demo "stress" feel; sanity-check it runs fast.
n = 500000
a = [random.randint(-10**12, 10**12) for _ in range(n)]
m = random.randint(0, 10**18)
import time
t0 = time.time()
out = subprocess.run([BIN], input=f"{n} {m}\n" + " ".join(map(str, a)) + "\n",
                     capture_output=True, text=True)
dt = time.time() - t0
print(f"big case n=5e5: ans={out.stdout.strip()} wall={dt:.2f}s (limit 1s)")

# 6. Competitive Companion JSON with the REAL P17831 data
payload = {
    "name": "crystal",
    "group": "CSP-S 2026",
    "url": "https://www.luogu.com.cn/problem/P17831",
    "interactive": False,
    "memoryLimit": 512,
    "timeLimit": 1000,
    "tests": [
        {"input": "5 5\n1 2 4 8 9", "output": "3"},
        {"input": "5 8\n-3 -1 2 2 7", "output": "4"},
    ],
}
with open("/home/z/my-project/scripts/crystal_companion.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, ensure_ascii=False, indent=2)
print("companion JSON written")
print("ALL CHECKS PASSED")
