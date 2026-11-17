"""How sticky is each WAR? Year-to-year correlation of each stat with itself.

Players who qualify in back-to-back seasons (hitters 200+ PA, pitchers 40+ IP), base seasons 2016-2025.
2020 scaled by 162/60. 95% intervals from 2,000 player bootstrap resamples. Writes results/stickiness.json.
Added after the main tests (not part of the original pre-registered plan).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
S = ["xWAR_xFIP", "xWAR_xERA", "fWAR", "bWAR", "aWAR"]
ps = pd.read_csv(ROOT / "data/processed/player_seasons.csv")
ps.loc[ps.Season == 2020, S] *= 162 / 60
rng = np.random.default_rng(20261117)
B = 2000
out = {}
for group, cond, cols in [("hitters", lambda d: d.PA >= 200, ["xWAR_xFIP", "fWAR", "bWAR", "aWAR"]),
                          ("pitchers", lambda d: d.IP >= 40, S)]:
    d = ps[cond(ps) & ps.Season.between(2016, 2026)]
    nxt = d.assign(Season=d.Season - 1)[["MLBAMID", "Season"] + cols]
    m = d[d.Season <= 2025].merge(nxt, on=["MLBAMID", "Season"], suffixes=("", "_n")).reset_index(drop=True)
    ids, inv = np.unique(m.MLBAMID, return_inverse=True)
    W = np.zeros((B, len(ids)))
    np.add.at(W, (np.repeat(np.arange(B), len(ids)), rng.integers(0, len(ids), size=(B, len(ids))).ravel()), 1)
    W = W[:, inv]

    def wr(x, y):
        sw = W.sum(1)
        mx, my = W @ x / sw, W @ y / sw
        return (W @ (x * y) / sw - mx * my) / np.sqrt((W @ x**2 / sw - mx**2) * (W @ y**2 / sw - my**2))

    r = {c: float(np.corrcoef(m[c], m[c + "_n"])[0, 1]) for c in cols}
    rb = {c: wr(m[c].values, m[c + "_n"].values) for c in cols}
    order = sorted(cols, key=lambda c: -r[c])
    best, second = order[0], order[1]
    gap = rb[best] - rb[second]
    out[group] = {"n": len(m), "r": {c: round(r[c], 3) for c in cols},
                  "ci": {c: [round(float(np.percentile(rb[c], 2.5)), 3), round(float(np.percentile(rb[c], 97.5)), 3)] for c in cols},
                  "best": best, "second": second, "gap": round(r[best] - r[second], 3),
                  "gap_ci": [round(float(np.percentile(gap, 2.5)), 3), round(float(np.percentile(gap, 97.5)), 3)],
                  "vs": {c: [round(r[best] - r[c], 3), round(float(np.percentile(rb[best] - rb[c], 2.5)), 3),
                             round(float(np.percentile(rb[best] - rb[c], 97.5)), 3)] for c in cols if c != best}}
    print(group, out[group]["n"], {c: out[group]["r"][c] for c in order}, "gap", out[group]["gap"], out[group]["gap_ci"])
(ROOT / "results/stickiness.json").write_text(json.dumps(out, indent=1))
