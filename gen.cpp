// Rush Hour puzzle candidate generator.
//
// usage: gen N SECONDS NV_LO NV_HI STATE_LIMIT SEED > candidates.txt
//
// Starts from random layouts, then hill-climbs: relocating, adding and removing
// vehicles to push up the longest shortest-solution in the layout's state
// space. Every analysed layout has all its reachable states labelled with the
// distance (in moves) to the nearest solved state, and one candidate per
// distinct distance is printed:  "<moves> <grid>"
// A grid is N*N characters, row-major; '.' is empty, 'X' is the red car, and
// every other vehicle has its own letter. pick.py chooses puzzles from these.
#include <bits/stdc++.h>
using namespace std;
typedef unsigned long long u64;

static int N, RED_ROW, GOAL, NV_LO, NV_HI;
static size_t LIMIT;
struct V { bool h; int L, f, p; };
typedef vector<V> Layout;
static mt19937_64 rng;
static int rnd(int a, int b) { return (int)(rng() % (u64)(b - a + 1)) + a; }

static bool fits(const vector<vector<char>>& occ, const V& v) {
    for (int k = 0; k < v.L; k++) {
        int r = v.h ? v.f : v.p + k, c = v.h ? v.p + k : v.f;
        if (occ[r][c]) return false;
    }
    return true;
}
static void mark(vector<vector<char>>& occ, const V& v, char val) {
    for (int k = 0; k < v.L; k++) occ[v.h ? v.f : v.p + k][v.h ? v.p + k : v.f] = val;
}
static bool random_vehicle(const vector<vector<char>>& occ, V& out, int trucks, int ntr) {
    for (int t = 0; t < 60; t++) {
        bool h = rnd(0, 1);
        int L = (trucks < ntr && rnd(0, 99) < 40) ? 3 : 2;
        V v;
        v.h = h; v.L = L;
        v.f = rnd(0, N - 1);
        v.p = rnd(0, N - L);
        if (h && v.f == RED_ROW) continue;
        if (fits(occ, v)) { out = v; return true; }
    }
    return false;
}
static vector<vector<char>> occupancy(const Layout& l, int skip = -1) {
    vector<vector<char>> occ(N, vector<char>(N, 0));
    for (int i = 0; i < (int)l.size(); i++) if (i != skip) mark(occ, l[i], 1);
    return occ;
}
static int count_trucks(const Layout& l) { int t = 0; for (auto& v : l) t += v.L == 3; return t; }

static Layout gen_layout(int nv) {
    Layout l;
    l.push_back({true, 2, RED_ROW, rnd(0, N - 3)});
    int ntr = rnd(max(1, N / 3), N / 2 + 2);
    auto occ = occupancy(l);
    for (int tries = 0; (int)l.size() < nv && tries < 2000; tries++) {
        V v;
        if (!random_vehicle(occ, v, count_trucks(l), ntr)) continue;
        mark(occ, v, 1);
        l.push_back(v);
    }
    return l;
}

static bool mutate(const Layout& in, Layout& out) {
    out = in;
    int n = (int)in.size();
    int op = rnd(0, 99);
    int ntr = N / 2 + 2;
    if (op < 60 && n > 1) {
        int i = rnd(1, n - 1);
        auto occ = occupancy(in, i);
        V v;
        int tr = count_trucks(in) - (in[i].L == 3);
        if (!random_vehicle(occ, v, tr, ntr)) return false;
        out[i] = v;
        return true;
    }
    if (op < 80) {
        if (n >= 21) return false;
        auto occ = occupancy(in);
        V v;
        if (!random_vehicle(occ, v, count_trucks(in), ntr)) return false;
        out.push_back(v);
        return true;
    }
    if (n <= NV_LO - 3) return false;
    out.erase(out.begin() + rnd(1, n - 1));
    return true;
}

static string to_grid(const Layout& veh, u64 key) {
    string g(N * N, '.');
    const string letters = "ABCDEFGHIJKLMNOPQRSTUVWYZ";
    for (size_t i = 0; i < veh.size(); i++) {
        char ch = i == 0 ? 'X' : letters[i - 1];
        int p = (key >> (3 * i)) & 7;
        for (int k = 0; k < veh[i].L; k++) {
            int r = veh[i].h ? veh[i].f : p + k, c = veh[i].h ? p + k : veh[i].f;
            g[r * N + c] = ch;
        }
    }
    return g;
}

// returns the longest shortest-solution over all states, or -1 if the layout
// is unsolvable or its state space exceeds LIMIT. Prints candidates if emit.
static int analyse(const Layout& veh, bool emit) {
    int n = (int)veh.size();
    if (n > 21 || n - 1 > 25) return -1;
    vector<vector<u64>> M(n);
    for (int i = 0; i < n; i++)
        for (int p = 0; p + veh[i].L <= N; p++) {
            u64 m = 0;
            for (int k = 0; k < veh[i].L; k++) {
                int r = veh[i].h ? veh[i].f : p + k, c = veh[i].h ? p + k : veh[i].f;
                m |= 1ULL << (r * N + c);
            }
            M[i].push_back(m);
        }
    auto each_neighbor = [&](u64 key, auto&& f) {
        int pos[21];
        u64 occ = 0;
        for (int i = 0; i < n; i++) { pos[i] = (key >> (3 * i)) & 7; occ |= M[i][pos[i]]; }
        for (int i = 0; i < n; i++) {
            u64 rest = occ & ~M[i][pos[i]];
            for (int d = -1; d <= 1; d += 2) {
                int q = pos[i] + d;
                while (q >= 0 && q <= N - veh[i].L && !(M[i][q] & rest)) {
                    f((key & ~(7ULL << (3 * i))) | ((u64)q << (3 * i)));
                    q += d;
                }
            }
        }
    };
    u64 start = 0;
    for (int i = 0; i < n; i++) start |= (u64)veh[i].p << (3 * i);
    unordered_map<u64, int> idx;
    vector<u64> st;
    idx.reserve(1 << 15);
    idx[start] = 0;
    st.push_back(start);
    bool tooBig = false;
    for (size_t h = 0; h < st.size() && !tooBig; h++) {
        each_neighbor(st[h], [&](u64 nk) {
            if (!idx.count(nk)) {
                idx[nk] = (int)st.size();
                st.push_back(nk);
                if (st.size() > LIMIT) tooBig = true;
            }
        });
    }
    if (tooBig) return -1;
    vector<int> dist(st.size(), -1), q;
    for (size_t i = 0; i < st.size(); i++)
        if ((int)(st[i] & 7) == GOAL) { dist[i] = 0; q.push_back((int)i); }
    if (q.empty()) return -1;
    for (size_t h = 0; h < q.size(); h++) {
        int s = q[h];
        each_neighbor(st[s], [&](u64 nk) {
            int j = idx[nk];
            if (dist[j] < 0) { dist[j] = dist[s] + 1; q.push_back(j); }
        });
    }
    int mx = 0;
    map<int, vector<int>> byd;
    for (size_t i = 0; i < st.size(); i++) {
        mx = max(mx, dist[i]);
        if (emit && dist[i] >= 4) byd[dist[i]].push_back((int)i);
    }
    for (auto& kv : byd) {
        int pick = kv.second[rng() % kv.second.size()];
        printf("%d %s\n", kv.first, to_grid(veh, st[pick]).c_str());
    }
    return mx;
}

int main(int argc, char** argv) {
    if (argc < 7) { fprintf(stderr, "usage: gen N SECONDS NV_LO NV_HI STATE_LIMIT SEED\n"); return 1; }
    N = atoi(argv[1]);
    double budget = atof(argv[2]);
    NV_LO = atoi(argv[3]); NV_HI = atoi(argv[4]);
    LIMIT = (size_t)atoll(argv[5]);
    rng.seed(atoll(argv[6]));
    RED_ROW = N / 2 - 1;
    GOAL = N - 2;
    auto t0 = chrono::steady_clock::now();
    auto elapsed = [&]() { return chrono::duration<double>(chrono::steady_clock::now() - t0).count(); };
    long analysed = 0, restarts = 0;
    int bestEver = 0;

    while (elapsed() < budget) {
        // fresh start: a random layout whose state space is small enough
        Layout cur;
        int curScore = -1;
        while (elapsed() < budget && curScore < 0) {
            cur = gen_layout(rnd(NV_LO, NV_HI));
            if ((int)cur.size() < NV_LO) continue;
            curScore = analyse(cur, true);
            analysed++;
        }
        restarts++;
        int stagnant = 0;
        while (elapsed() < budget && stagnant < 120) {
            Layout cand;
            if (!mutate(cur, cand)) { stagnant++; continue; }
            int s = analyse(cand, true);
            analysed++;
            if (s >= curScore && s >= 0) {
                stagnant = s > curScore ? 0 : stagnant + 1;
                cur = cand;
                curScore = s;
                bestEver = max(bestEver, s);
            } else stagnant++;
        }
    }
    fprintf(stderr, "N=%d analysed=%ld restarts=%ld best=%d secs=%.1f\n", N, analysed, restarts, bestEver, elapsed());
    return 0;
}
