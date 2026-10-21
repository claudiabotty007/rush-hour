import random, json, time, sys
from collections import deque

random.seed(11)
N = 6
TIERS = [
    ("beginner", 4, 7),
    ("intermediate", 8, 12),
    ("advanced", 13, 18),
    ("expert", 19, 99),
]
PER_TIER = 10
POOL_TARGET = 30
TIME_LIMIT = float(sys.argv[1]) if len(sys.argv) > 1 else 120


def gen_layout(nv):
    occ = [[False] * N for _ in range(N)]
    veh = []
    rx = random.randint(0, 3)
    veh.append((True, 2, 2, rx))
    occ[2][rx] = occ[2][rx + 1] = True
    ntr = random.randint(1, 4)
    trucks = 0
    tries = 0
    while len(veh) < nv and tries < 300:
        tries += 1
        h = random.random() < 0.5
        L = 3 if (trucks < ntr and random.random() < 0.4) else 2
        if h:
            r = random.randrange(N)
            if r == 2:
                continue
            c = random.randrange(N - L + 1)
            cells = [(r, c + k) for k in range(L)]
            fixed, pos = r, c
        else:
            c = random.randrange(N)
            r = random.randrange(N - L + 1)
            cells = [(r + k, c) for k in range(L)]
            fixed, pos = c, r
        if any(occ[a][b] for a, b in cells):
            continue
        for a, b in cells:
            occ[a][b] = True
        veh.append((h, L, fixed, pos))
        if L == 3:
            trucks += 1
    return veh


def build_masks(veh):
    M = []
    for h, L, f, p in veh:
        row = []
        for pos in range(N - L + 1):
            m = 0
            for k in range(L):
                r, c = (f, pos + k) if h else (pos + k, f)
                m |= 1 << (r * N + c)
            row.append(m)
        M.append(row)
    return M


def neighbors(s, M, veh):
    n = len(veh)
    occ = 0
    for i in range(n):
        occ |= M[i][s[i]]
    for i in range(n):
        L = veh[i][1]
        own = M[i][s[i]]
        rest = occ & ~own
        p = s[i]
        for d in (-1, 1):
            q = p + d
            while 0 <= q <= N - L and not (M[i][q] & rest):
                t = list(s)
                t[i] = q
                yield tuple(t)
                q += d


def analyze(veh, limit=40000):
    M = build_masks(veh)
    start = tuple(v[3] for v in veh)
    seen = {start}
    q = deque([start])
    while q:
        s = q.popleft()
        for t in neighbors(s, M, veh):
            if t not in seen:
                seen.add(t)
                if len(seen) > limit:
                    return None
                q.append(t)
    sources = [s for s in seen if s[0] == 4]
    if not sources:
        return None
    dist = {s: 0 for s in sources}
    q = deque(sources)
    while q:
        s = q.popleft()
        for t in neighbors(s, M, veh):
            if t not in dist:
                dist[t] = dist[s] + 1
                q.append(t)
    return dist


def to_grid(veh, state):
    g = ["."] * 36
    car_letters = iter("ABCDEFGHIJK")
    truck_letters = iter("OPQR")
    for i, (h, L, f, _) in enumerate(veh):
        if i == 0:
            ch = "X"
        elif L == 3:
            ch = next(truck_letters)
        else:
            ch = next(car_letters)
        p = state[i]
        for k in range(L):
            r, c = (f, p + k) if h else (p + k, f)
            g[r * N + c] = ch
    return "".join(g)


pools = {t[0]: {} for t in TIERS}
t0 = time.time()
layouts = 0
while time.time() - t0 < TIME_LIMIT:
    if all(len(pools[t[0]]) >= POOL_TARGET for t in TIERS):
        break
    nv = random.randint(8, 13)
    veh = gen_layout(nv)
    if len(veh) < 8:
        continue
    dist = analyze(veh)
    layouts += 1
    if not dist:
        continue
    by_tier = {t[0]: [] for t in TIERS}
    for s, d in dist.items():
        for name, lo, hi in TIERS:
            if lo <= d <= hi:
                by_tier[name].append((d, s))
    for name, cands in by_tier.items():
        if not cands or len(pools[name]) >= POOL_TARGET * 2:
            continue
        cands.sort(key=lambda x: x[0])
        # take the hardest state in this tier for this layout, plus a mid one for variety
        for d, s in (cands[-1], cands[len(cands) // 2]):
            g = to_grid(veh, s)
            if g not in pools[name]:
                pools[name][g] = d
                break

print("layouts tried", layouts, "time", round(time.time() - t0, 1), file=sys.stderr)
puzzles = []
for name, lo, hi in TIERS:
    items = sorted(pools[name].items(), key=lambda kv: kv[1])
    print(name, len(items), [d for _, d in items][:3], "...", [d for _, d in items][-3:], file=sys.stderr)
    if len(items) > PER_TIER:
        idxs = [round(i * (len(items) - 1) / (PER_TIER - 1)) for i in range(PER_TIER)]
        items = [items[i] for i in idxs]
    for g, d in items:
        puzzles.append({"tier": name, "par": d, "grid": g})

json.dump(puzzles, open(sys.argv[2] if len(sys.argv) > 2 else "puzzles.json", "w"))
print(len(puzzles), "puzzles", file=sys.stderr)
