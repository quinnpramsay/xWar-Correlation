"""Which WAR predicts future WAR best? Follows PLAN.md (pre-registered 2026-11-17).

Usage: python3 src/analyze.py [--pa 200] [--ip 40] [--no2020scale] [--played-only] [--bases 2016-2025] [--tag main]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STATS = ["xWAR_xFIP", "xWAR_xERA", "fWAR", "bWAR", "aWAR"]
TGT = ["aWAR", "fWAR", "bWAR"]
LAST = 2026
B = 2000

ap = argparse.ArgumentParser()
ap.add_argument("--pa", type=int, default=200)
ap.add_argument("--ip", type=float, default=40)
ap.add_argument("--no2020scale", action="store_true")
ap.add_argument("--played-only", action="store_true")
ap.add_argument("--bases", default="2016-2025")
ap.add_argument("--tag", default="main")
a = ap.parse_args()
b0, b1 = map(int, a.bases.split("-"))
rng = np.random.default_rng(20261117)

ps = pd.read_csv(ROOT / "data/processed/player_seasons.csv")
if not a.no2020scale:
    ps.loc[ps.Season == 2020, STATS] *= 162 / 60
war = {k: ps.set_index(["MLBAMID", "Season"])[k].to_dict() for k in TGT}
played = set(zip(ps.MLBAMID, ps.Season))


def fut(pid, s, k, yrs):
    return np.array([war[k].get((pid, s + j), 0.0) for j in yrs])


def stats_for(group):
    """xWAR(xFIP) and xWAR(xERA) differ only in the pitching piece, so hitters get one xWAR."""
    return ["xWAR_xFIP", "fWAR", "bWAR", "aWAR"] if group == "hitters" else STATS


def make(group):
    d = ps[(ps.Season.between(b0, b1))]
    d = d[d.PA >= a.pa] if group == "hitters" else d[d.IP >= a.ip]
    d = d.dropna(subset=["age"]).reset_index(drop=True)
    for k in TGT:
        d[f"next_{k}"] = [war[k].get((p, s + 1), 0.0) for p, s in zip(d.MLBAMID, d.Season)]
        for N in range(1, 11):
            d[f"mean{N}_{k}"] = [fut(p, s, k, range(1, N + 1)).mean() if s + N <= LAST else np.nan
                                 for p, s in zip(d.MLBAMID, d.Season)]
        for K in (3, 5, 10):
            d[f"max{K}_{k}"] = [fut(p, s, k, range(1, K + 1)).max() if s + K <= LAST else np.nan
                                for p, s in zip(d.MLBAMID, d.Season)]
    for N in range(2, 11):  # split-half reliability pieces (aWAR)
        d[f"odd{N}"] = [fut(p, s, "aWAR", range(1, N + 1, 2)).mean() if s + N <= LAST else np.nan for p, s in zip(d.MLBAMID, d.Season)]
        d[f"even{N}"] = [fut(p, s, "aWAR", range(2, N + 1, 2)).mean() if s + N <= LAST else np.nan for p, s in zip(d.MLBAMID, d.Season)]
    d["played_next"] = [(p, s + 1) in played for p, s in zip(d.MLBAMID, d.Season)]
    return d


def wcorr(X, y, w):
    """Weighted Pearson r of each column of X with y. w: (reps, n) or (n,)."""
    w = np.atleast_2d(w)
    sw = w.sum(1, keepdims=True)
    mx = (w @ X) / sw
    my = (w @ y)[:, None] / sw
    cov = (w @ (X * y[:, None])) / sw - mx * my
    vx = (w @ X**2) / sw - mx**2
    vy = (w @ y**2)[:, None] / sw - my**2
    return cov / np.sqrt(vx * vy)


def boot_weights(pid):
    u, inv = np.unique(pid, return_inverse=True)
    draws = rng.integers(0, len(u), size=(B, len(u)))
    cnt = np.zeros((B, len(u)))
    np.add.at(cnt, (np.repeat(np.arange(B), len(u)), draws.ravel()), 1)
    return cnt[:, inv]


def evaluate(d, tcol, W=None):
    STATS = CUR
    m = d[tcol].notna().values
    if a.played_only and tcol.startswith("next_"):
        m &= d.played_next.values
    x, y, pid = d.loc[m, STATS].values, d.loc[m, tcol].values, d.loc[m, "MLBAMID"].values
    if len(y) < 30:
        return None
    r = wcorr(x, y, np.ones(len(y)))[0]
    rb = wcorr(x, y, boot_weights(pid))
    order = np.argsort(-r)
    best, second = order[0], order[1]
    gap = rb[:, best] - rb[:, second]
    rho = pd.DataFrame(x).rank().corrwith(pd.Series(y).rank()).values
    # age-controlled partial r
    age = d.loc[m, "age"].values
    A = np.column_stack([np.ones_like(age), age, age**2])
    res = lambda v: v - A @ np.linalg.lstsq(A, v, rcond=None)[0]
    pr = np.array([np.corrcoef(res(x[:, j]), res(y))[0, 1] for j in range(len(STATS))])
    # leave-one-season-out RMSE, target ~ stat + age + age^2
    seas = d.loc[m, "Season"].values
    rmse = []
    for j in range(len(STATS)):
        Z = np.column_stack([A, x[:, j]])
        err = np.empty_like(y)
        for s in np.unique(seas):
            tr, te = seas != s, seas == s
            beta = np.linalg.lstsq(Z[tr], y[tr], rcond=None)[0]
            err[te] = y[te] - Z[te] @ beta
        rmse.append(np.sqrt(np.mean(err**2)))
    return {
        "target": tcol, "n": int(len(y)), "players": int(len(np.unique(pid))),
        "r": dict(zip(STATS, r.round(3))),
        "ci": {s: [round(float(np.percentile(rb[:, j], 2.5)), 3), round(float(np.percentile(rb[:, j], 97.5)), 3)] for j, s in enumerate(STATS)},
        "rho": dict(zip(STATS, rho.round(3))), "partial_r_age": dict(zip(STATS, pr.round(3))),
        "rmse_loso": dict(zip(STATS, np.round(rmse, 3))),
        "best": STATS[best], "second": STATS[second],
        "gap": round(float(r[best] - r[second]), 3),
        "gap_ci": [round(float(np.percentile(gap, 2.5)), 3), round(float(np.percentile(gap, 97.5)), 3)],
        "gap_vs_best": {s: [round(float(np.percentile(rb[:, best] - rb[:, j], 2.5)), 3), round(float(np.percentile(rb[:, best] - rb[:, j], 97.5)), 3)] for j, s in enumerate(STATS)},
        "ranking": [STATS[i] for i in order],
    }


def reliability(d, N):
    if N < 2:
        return np.nan
    m = d[f"odd{N}"].notna()
    r = np.corrcoef(d.loc[m, f"odd{N}"], d.loc[m, f"even{N}"])[0, 1]
    return 2 * r / (1 + r)


out = {"args": vars(a)}
for group in ["hitters", "pitchers"]:
    CUR = stats_for(group)
    d = make(group)
    g = {"n_rows": len(d), "n_players": int(d.MLBAMID.nunique())}
    g["next"] = [evaluate(d, f"next_{k}") for k in TGT]
    g["max"] = [evaluate(d, f"max{K}_{k}") for K in (3, 5, 10) for k in TGT]
    horizon = []
    for N in range(1, 11):
        e = evaluate(d, f"mean{N}_aWAR")
        if e is None:
            continue
        e["N"], e["reliability"] = N, round(float(reliability(d, N)), 3)
        e["bases"] = f"{b0}-{min(b1, LAST - N)}"
        horizon.append(e)
    g["horizon"] = horizon
    # pre-registered N rule
    chosen = None
    for i, e in enumerate(horizon):
        if i == 0 or i + 2 >= len(horizon):
            continue
        gain = e["reliability"] - (horizon[i - 1]["reliability"] if i > 1 else 0)
        stable = e["ranking"] == horizon[i + 1]["ranking"] == horizon[i + 2]["ranking"]
        if i > 1 and gain < 0.03 and stable and e["N"] <= 7:
            chosen = e["N"]
            break
    if chosen is None:
        cands = [e for e in horizon if e["N"] <= 7]
        chosen = min(cands, key=lambda e: e["gap_ci"][1] - e["gap_ci"][0])["N"]
        g["N_rule"] = "fallback: narrowest top-two gap CI"
    else:
        g["N_rule"] = "reliability plateau + stable ranking"
    g["N_chosen"] = chosen
    g["meanN"] = [evaluate(d, f"mean{chosen}_{k}") for k in TGT]
    g["mean5"] = [evaluate(d, f"mean5_{k}") for k in TGT]  # N = 5 recommended across runs
    out[group] = g
    d.to_csv(ROOT / f"data/processed/analysis_{group}_{a.tag}.csv", index=False)

(ROOT / "results").mkdir(exist_ok=True)
with open(ROOT / f"results/results_{a.tag}.json", "w") as fh:
    json.dump(out, fh, indent=1, default=float)


def show(e):
    if e is None:
        return
    cells = "  ".join(f"{s} {e['r'][s]:.3f}" for s in e["ranking"])
    print(f"  {e['target']:<14} n={e['n']:<5} {cells}  | lead {e['gap']:+.3f} [{e['gap_ci'][0]:+.3f},{e['gap_ci'][1]:+.3f}]")


for group in ["hitters", "pitchers"]:
    g = out[group]
    print(f"\n===== {group.upper()} ({g['n_rows']} base seasons, {g['n_players']} players) =====")
    print("Next season:"); [show(e) for e in g["next"]]
    print("Best season over next K years:"); [show(e) for e in g["max"]]
    print("Horizon scan (mean aWAR over next N years):")
    for e in g["horizon"]:
        print(f"  N={e['N']:<2} bases {e['bases']} rel={e['reliability']:.2f}", end="")
        show(e)
    print(f"Chosen N = {g['N_chosen']} ({g['N_rule']})"); [show(e) for e in g["meanN"]]
