"""Replicate Tango's FRV vs DRS test (tangotiger.com, 2026-09-28) on our FanGraphs export.

Player-position seasons with 333+ innings (~1,000 outs) in back-to-back seasons.
Both metrics re-centered to the position-season average and scaled per 1,000 innings.
Reports self and cross year-to-year r, and the blend weight that best predicts next season's
50/50 average of the two (Tango's "target-based" weight), with a player bootstrap interval.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
f = pd.read_csv(ROOT / "data/fangraphs/fg_fld.csv", encoding="utf-8-sig")
f = f[(f.Pos != "P") & (f.Season >= 2016) & f.FRV.notna() & f.DRS.notna()].copy()
f["inn"] = np.floor(f.Inn) + (f.Inn - np.floor(f.Inn)) * 10 / 3
f = f.groupby(["MLBAMID", "Season", "Pos"], as_index=False)[["inn", "FRV", "DRS"]].sum()
for m in ["FRV", "DRS"]:
    lg = f.groupby(["Season", "Pos"]).apply(lambda g: g[m].sum() / g.inn.sum()).rename(m + "_lgrate")
    f = f.join(lg, on=["Season", "Pos"])
    f[m + "_r"] = (f[m] - f[m + "_lgrate"] * f.inn) / f.inn * 1000
f = f[f.inn >= 333]
nxt = f.assign(Season=f.Season - 1)[["MLBAMID", "Season", "Pos", "FRV_r", "DRS_r"]]
pairs = f.merge(nxt, on=["MLBAMID", "Season", "Pos"], suffixes=("", "_n"))
GROUPS = {"C": ["C"], "OF": ["LF", "CF", "RF"], "1B": ["1B"], "2B": ["2B"], "SS": ["SS"], "3B": ["3B"], "IF": ["1B", "2B", "SS", "3B"]}
TANGO = {"C": 0.93, "OF": 0.92, "1B": 0.67, "2B": 0.40, "SS": 0.60, "3B": 0.40, "IF": 0.50}
rng = np.random.default_rng(7)


def weight(d):
    X = np.column_stack([np.ones(len(d)), d.FRV_r, d.DRS_r])
    y = (d.FRV_r_n + d.DRS_r_n) / 2
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return b[1] / (b[1] + b[2])


def run(years, label):
    rows = []
    for g, ps in GROUPS.items():
        d = pairs[pairs.Pos.isin(ps) & pairs.Season.between(*years)]
        c = lambda a, b: np.corrcoef(d[a], d[b])[0, 1]
        w = weight(d)
        ids = d.MLBAMID.unique()
        bs = []
        for _ in range(1000):
            pick = rng.choice(ids, len(ids))
            dd = pd.concat([d[d.MLBAMID == i] for i in pick[:0]]) if False else d.set_index("MLBAMID").loc[pick].reset_index()
            bs.append(weight(dd))
        rows.append({"group": g, "pairs": len(d), "FRV→FRV": c("FRV_r", "FRV_r_n"), "DRS→DRS": c("DRS_r", "DRS_r_n"),
                     "FRV→DRS": c("FRV_r", "DRS_r_n"), "DRS→FRV": c("DRS_r", "FRV_r_n"),
                     "FRV weight": w, "lo": np.percentile(bs, 2.5), "hi": np.percentile(bs, 97.5), "Tango": TANGO[g]})
    t = pd.DataFrame(rows).round(2)
    print(f"\n{label}\n{t.to_string(index=False)}")
    return t


a = run((2016, 2025), "Ours, 2016-2026 (pairs start 2016-2025)")
b = run((2021, 2025), "Ours, 2021-2026 (Tango's window)")
(ROOT / "results").mkdir(exist_ok=True)
pd.concat([a.assign(window="2016-2026"), b.assign(window="2021-2026")]).to_csv(ROOT / "results/defense_weights.csv", index=False)
