"""Choose puzzles from gen.cpp candidates.

usage: python3 pick.py CANDIDATES.txt OUT.json TIERS
  TIERS  four ranges of shortest-solution length, e.g. 4-7,8-12,13-18,19-99

Takes ten puzzles per tier, spread evenly across the tier's range.
"""
import json, sys, collections

names = ["beginner", "intermediate", "advanced", "expert"]
tiers = []
for name, rng in zip(names, sys.argv[3].split(",")):
    lo, hi = rng.split("-")
    tiers.append((name, int(lo), int(hi)))

pool = {t[0]: {} for t in tiers}
hist = collections.Counter()
for line in open(sys.argv[1]):
    d, g = line.split()
    d = int(d)
    hist[d] += 1
    for name, lo, hi in tiers:
        if lo <= d <= hi:
            pool[name][g] = d

print("candidates per distance:", dict(sorted(hist.items())), file=sys.stderr)
out = []
for name, lo, hi in tiers:
    items = sorted(pool[name].items(), key=lambda kv: kv[1])
    print(name, len(items), "in pool", file=sys.stderr)
    if len(items) > 10:
        idxs = [round(i * (len(items) - 1) / 9) for i in range(10)]
        items = [items[i] for i in idxs]
    out += [{"tier": name, "par": d, "grid": g} for g, d in items]
json.dump(out, open(sys.argv[2], "w"), separators=(",", ":"))
print(len(out), "puzzles written", file=sys.stderr)
