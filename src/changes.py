"""What did each of TJStats' Nov 17 changes do? Start from his original xWAR and apply one change at a time.

  xFIP -> xERA          (pitchers)
  50/50 -> Tango weights (hitters)
  park factor removed    (hitters)
plus all three together (= his updated xWAR). Target: future aWAR. Paired player bootstrap, 2,000 resamples.
Reads data/processed/analysis_{group}_main.csv written by analyze.py; writes results/changes.json.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VAR = ["chg_xera", "chg_tango", "chg_nopark"]
CHANGES = {"pitchers": [("xFIP → xERA", "chg_xera"), ("All three (updated xWAR)", "xWAR_upd")],
           "hitters": [("FRV/DRS 50/50 → Tango weights", "chg_tango"), ("Park factor removed", "chg_nopark"),
                       ("All three (updated xWAR)", "xWAR_upd")]}
TARGETS = [("next_aWAR", "Next season"), ("mean5_aWAR", "Average of next 5"), ("max10_aWAR", "Best season in next 10")]
rng = np.random.default_rng(20261117)
out = {}
for group, changes in CHANGES.items():
    d = pd.read_csv(ROOT / f"data/processed/analysis_{group}_main.csv")
    d.loc[d.Season == 2020, VAR] *= 162 / 60  # analyze.py scales 2020 only for the five main stats
    rows = []
    for tcol, tl in TARGETS:
        m = d[d[tcol].notna()].reset_index(drop=True)
        ids, inv = np.unique(m.MLBAMID, return_inverse=True)
        W = np.zeros((2000, len(ids)))
        draws = rng.integers(0, len(ids), size=(2000, len(ids)))
        np.add.at(W, (np.repeat(np.arange(2000), len(ids)), draws.ravel()), 1)
        W = W[:, inv]

        def wr(x):
            y = m[tcol].values
            sw = W.sum(1)
            mx, my = W @ x / sw, W @ y / sw
            cov = W @ (x * y) / sw - mx * my
            return cov / np.sqrt((W @ x**2 / sw - mx**2) * (W @ y**2 / sw - my**2))

        base = m.xWAR_orig.values
        r0 = np.corrcoef(base, m[tcol])[0, 1]
        b0 = wr(base)
        for cl, col in changes:
            r1 = np.corrcoef(m[col], m[tcol])[0, 1]
            diff = wr(m[col].values) - b0
            rows.append({"change": cl, "target": tl, "n": len(m), "r_original": round(r0, 3), "r_changed": round(r1, 3),
                         "diff": round(r1 - r0, 3), "lo": round(float(np.percentile(diff, 2.5)), 3),
                         "hi": round(float(np.percentile(diff, 97.5)), 3)})
    out[group] = rows
    print(f"\n{group}"); print(pd.DataFrame(rows).to_string(index=False))
(ROOT / "results/changes.json").write_text(json.dumps(out, indent=1))
