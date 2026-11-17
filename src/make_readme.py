"""Write README.md from the local results (results/results_*.json). The README shows only aggregate summary statistics."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
o = json.load(open(R / "results_main.json"))
SENS = {t: json.load(open(R / f"results_{t}.json")) for t in ["strict", "no2020", "played", "fixed1619"]}
COLS = ["xWAR_xFIP", "xWAR_xERA", "fWAR", "bWAR", "aWAR"]
NAME = {"xWAR_xFIP": "xWAR(xFIP)", "xWAR_xERA": "xWAR(xERA)", "fWAR": "fWAR", "bWAR": "bWAR", "aWAR": "aWAR"}


def cols_for(group):
    return ["xWAR_xFIP", "fWAR", "bWAR", "aWAR"] if group == "hitters" else COLS


def label(c, group):
    return "xWAR" if (group == "hitters" and c == "xWAR_xFIP") else NAME[c]
ROWS = [("next", "Next season"), ("mean5", "Average of next 5 seasons"), ("max5", "Best season in next 5"),
        ("max10", "Best season in next 10 †")]


def find(res, group, kind, tgt):
    G = res[group]
    pool = {"next": G["next"], "mean5": G["mean5"], "max5": G["max"], "max10": G["max"]}[kind]
    return next(e for e in pool if e and e["target"] == f"{kind}_{tgt}")


def md_table(tgt, group):
    cols = cols_for(group)
    L = ["| Horizon | n | " + " | ".join(label(c, group) for c in cols) + " | Leader's edge [95% interval] |",
         "|---|---:|" + "---:|" * len(cols) + "---|"]
    for kind, kl in ROWS:
        e = find(o, group, kind, tgt)
        clear = e["gap_ci"][0] > 0
        cells = [f"**{e['r'][c]:.3f}**" if c == e["best"] else f"{e['r'][c]:.3f}" for c in cols]
        lo, hi = e["gap_ci"]
        L.append(f"| {kl} | {e['n']:,} | " + " | ".join(cells) + f" | {e['gap']:+.3f} [{lo:+.3f}, {hi:+.3f}] {'clear' if clear else 'tie'} |")
    return "\n".join(L)


def md_horizon():
    H = {g: {e["N"]: e for e in o[g]["horizon"]} for g in ["hitters", "pitchers"]}
    rel = lambda e: "—" if e["reliability"] != e["reliability"] else f"{e['reliability']:.2f}"
    L = ["| N seasons | Base seasons | Hitter n | Hitter reliability | Pitcher n | Pitcher reliability |", "|---:|---|---:|---:|---:|---:|"]
    for N in range(1, 11):
        a, b = H["hitters"][N], H["pitchers"][N]
        bold = "**" if N == 5 else ""
        L.append(f"| {bold}{N}{bold} | {a['bases']} | {a['n']:,} | {rel(a)} | {b['n']:,} | {rel(b)} |")
    return "\n".join(L)


TANGO = {"C": .93, "OF": .92, "1B": .67, "SS": .60, "2B": .40, "3B": .40}
wmd = "\n".join(["| Position | FRV weight | DRS weight |", "|---|---:|---:|"] +
                [f"| {p} | {TANGO[p]:.2f} | {1 - TANGO[p]:.2f} |" for p in ["C", "OF", "1B", "SS", "2B", "3B"]])

intro = {"aWAR": "aWAR is the fairest target, because it isn't built from any single site's WAR.",
         "bWAR": "This target favors bWAR, since it shares bWAR's own method.",
         "fWAR": "This target favors fWAR and both xWARs, which are built on fWAR."}
tables, k = [], 1
for t in ["aWAR", "bWAR", "fWAR"]:
    for g, gl in [("hitters", "Hitters"), ("pitchers", "Pitchers")]:
        tables.append(f"### Table {k}. {gl}: correlation with future {t}\n\n{intro[t]}\n\n{md_table(t, g)}")
        k += 1

pn, pm = find(o, "pitchers", "next", "aWAR"), find(o, "pitchers", "mean5", "aWAR")
hn, hm, h10 = find(o, "hitters", "next", "aWAR"), find(o, "hitters", "mean5", "aWAR"), find(o, "hitters", "max10", "aWAR")
nh, nhp, np_, npp = o["hitters"]["n_rows"], o["hitters"]["n_players"], o["pitchers"]["n_rows"], o["pitchers"]["n_players"]

# robustness checks used in the text (asserted so the README can't drift from the results)
for res in [o] + list(SENS.values()):
    for kind in ["next", "mean5"]:
        e = find(res, "pitchers", kind, "aWAR")
        assert e["best"] == "xWAR_xFIP" and e["gap_ci"][0] > 0, "pitcher claim no longer holds"
        assert e["r"]["xWAR_xERA"] < e["r"]["fWAR"], "xERA claim no longer holds"
        assert find(res, "hitters", kind, "aWAR")["gap_ci"][0] <= 0, "hitter tie claim no longer holds"
    assert find(res, "pitchers", "max10", "aWAR")["best"] == "xWAR_xFIP", "pitcher 10-year claim no longer holds"

readme = f"""# xWAR Correlation: does xWAR predict the future better than WAR?

**The idea for xWAR comes from [Thomas Nestico (TJStats on X)](https://x.com/TJStats).** His goal is to capture player value from the factors a player can most directly impact, while my goal is to predict a player's future WAR, so I made some fine-tuning changes to help toward that goal. Fielding weights come from [Tom Tango's research](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs). Full credits and a disclaimer are at the bottom.

When looking at expected stats, I usually like to see whether a player outperformed or underperformed them, and whether that gap correlates with future outcomes. So I decided to put that together and look into it.

xWAR rebuilds fWAR from the parts of a season a player controls most: expected batting (xwOBA), expected pitching (xFIP or xERA) and a position-weighted blend of two fielding metrics. This project tests whether xWAR predicts a player's future WAR better than FanGraphs WAR (fWAR), Baseball-Reference WAR (bWAR) or their average (aWAR).

## The short answer

| | Result |
|---|---|
| **Pitchers** | **xWAR(xFIP) is the best predictor** at every horizon and on every target. Next-season aWAR: r = {pn['r']['xWAR_xFIP']:.3f}, vs {pn['r']['fWAR']:.3f} for fWAR. The xERA version predicts worse than plain fWAR ({pn['r']['xWAR_xERA']:.3f}). |
| **Hitters** | **A tie.** xWAR and aWAR finish within noise of each other (next-season r = {hn['r']['xWAR_xFIP']:.3f} vs {hn['r']['aWAR']:.3f}). Both edge out fWAR and bWAR by about 0.01 to 0.02. |
| **Horizon** | **5 seasons.** The future average levels off by 5 seasons (reliability 0.89 hitters, 0.85 pitchers). Longer windows cost a base season per year and mostly measure aging. |

## The stats compared

| Stat | Definition |
|---|---|
| fWAR | FanGraphs Wins Above Replacement. |
| bWAR | Baseball-Reference Wins Above Replacement. |
| aWAR | The average of the two: (fWAR + bWAR) / 2. |
| xWAR(xFIP) | fWAR with batting runs adjusted from wOBA to Statcast xwOBA (park factor kept), fielding as a position-weighted blend of Statcast Fielding Run Value (FRV) and Defensive Runs Saved (DRS), and pitching runs from xFIP instead of FIP. |
| xWAR(xERA) | The same, with pitching runs from Statcast xERA instead of xFIP. For hitters the two xWARs are identical, so hitter tables show one xWAR column. |

- **Why xFIP beats xERA for prediction:** published research finds xERA predicts next-season ERA worse than xFIP and SIERA ([Dan Richards, Pitcher List](https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/)). Contact quality allowed is less stable year to year for pitchers than strikeouts, walks and ground balls.

## Results

Each value is the Pearson r between a stat in one season and the player's later WAR. The highest value in each row is bold. "Clear" means the leader's 95% interval over second place is above zero; "tie" means it isn't. For hitters the two xWARs are identical, so they share one column.

{chr(10).join(chr(10) + x + chr(10) for x in tables)}
† Only the 2016 season has 10 complete future seasons (2017 to 2026), so this row uses about 350 hitters and 385 pitchers. Treat it as a rough check.

## Why a 5-season horizon

Before seeing which stat won, I set a rule (see [PLAN.md](PLAN.md)): pick the shortest horizon where the future average stops getting more reliable (gain under 0.03 per added year) and the ranking of the stats stops changing. For pitchers the rule picked 5 seasons in 4 of 5 checks, and 6 in the other. For hitters it landed between 5 and 7, because the top hitter stats are tied and keep swapping places. Five seasons keeps the most data at nearly full reliability. Past that, aging (about 0.5 WAR lost per year after 30) and survivor bias drive the numbers more than the season being measured.

{md_horizon()}

Reliability is split-half (odd vs even future seasons), corrected to the full window. Each added season removes one base season from the sample.

## How xWAR was built

- **Batting:** FanGraphs batting runs plus (xwOBA − wOBA) / wOBA scale × PA, using Baseball Savant's xwOBA and wOBA, centered so each season's league total is unchanged. FanGraphs' park adjustment is kept. (Removing it gave no gain over 1 to 5 seasons and was worse for the 10-year best season.)
- **Fielding:** FanGraphs fielding is based on FRV, so it is replaced with w × FRV + (1 − w) × DRS, with both centered within position and season. The weight w depends on position (below).
- **Pitching:** fWAR plus (FIP − xFIP) × IP / 9, or (FIP − xERA) × IP / 9, converted to wins with each pitcher's own FanGraphs runs-per-win ratio. Both are centered so each season's league average is unchanged.
- **League check:** league-wide xWAR stays within about 1% of fWAR in every season.

### Fielding weights by position

I used the position weights from Tom Tango's ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) (September 2026), because his research is the best available on how the two metrics compare by position. Catchers and outfielders lean on FRV, while 2B and 3B lean on DRS.

{wmd}

## Sample and method

- **Base seasons:** 2016 to 2025, the years Statcast FRV is available; future seasons run through 2026. Hitters with 200+ PA ({nh:,} player-seasons, {nhp:,} players); pitchers with 40+ IP ({np_:,} player-seasons, {npp:,} players).
- **Missing seasons:** a season with no MLB appearance counts as 0 WAR.
- **2020:** WAR in 2020 is scaled by 162/60.
- **Uncertainty:** 95% intervals come from 2,000 bootstrap resamples of players, since a player can appear in several base seasons.
- **Robustness:** the pitcher and hitter results also hold with 100+ PA / 100+ IP only, without the 2020 scaling, among players who played the next season, and on 2016–2019 base seasons only.
- **Limits:** WAR includes playing time, so these correlations partly measure who keeps getting at-bats or innings. aWAR averages two measurements of the same season, which by itself reduces noise.

## Data

All data was downloaded locally and is **not included in this repository**. Some of it is behind paywalls (FanGraphs membership exports), and every provider has its own rules on reuse and redistribution. The sources are FanGraphs (fWAR, FIP, xFIP, xERA, DRS, FRV), Baseball Savant (xwOBA, wOBA, xERA) and Baseball-Reference (bWAR), all for 2015 to 2026. To rerun the analysis, get the data from those sites under their terms and place it in a local `data/` folder.

## Code

| Path | Contents |
|---|---|
| `PLAN.md` | Test plan written before any results, plus later amendments |
| `src/build.py` | Builds the player-season table with fWAR, bWAR, aWAR, xWAR(xFIP) and xWAR(xERA) |
| `src/analyze.py` | Main tests (see PLAN.md). Sensitivity flags: `--pa 400 --ip 100`, `--no2020scale`, `--played-only`, `--bases 2016-2019` |
| `src/report.py`, `src/make_readme.py` | Write the full tables and this README |

Requirements: Python 3.9+, pandas, numpy (`pip install -r requirements.txt`).

## Credits

- **xWAR idea:** [Thomas Nestico (TJStats on X)](https://x.com/TJStats). His own version and leaderboard: [tjstats.ca/xwar](https://tjstats.ca/xwar/).
- **Fielding-weight research:** Tom Tango, ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) and ["FRV v DRS"](https://tangotiger.com/index.php/site/article/frv-v-drs), Tangotiger Blog. Tom Tango also created FIP and, with Mitchel Lichtman and Andrew Dolphin, wOBA (*The Book*).
- **fWAR, FIP, xFIP and DRS exports:** [FanGraphs](https://www.fangraphs.com). xFIP was developed by Dave Studeman of The Hardball Times.
- **bWAR:** [Baseball-Reference.com](https://www.baseball-reference.com) (Sports Reference LLC). Its WAR framework was originally provided by Sean Smith.
- **xwOBA, wOBA, xERA and Fielding Run Value:** MLB Statcast via [Baseball Savant](https://baseballsavant.mlb.com) (MLB Advanced Media).
- **Defensive Runs Saved (DRS):** [Sports Info Solutions](https://www.sportsinfosolutions.com), as published on FanGraphs.
- **ERA-estimator research:** Dan Richards, ["The Relative Value of FIP, xFIP, SIERA and xERA, Pt. II"](https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/), Pitcher List (2020).
- **Aging research:** Piper Slowinski, ["Aging Curve"](https://library.fangraphs.com/principles/aging-curve), FanGraphs Library.

## Disclaimer

**For educational and non-commercial purposes only.** This is an independent analysis. It is not affiliated with, sponsored by or endorsed by FanGraphs, Sports Reference LLC (Baseball-Reference.com), Major League Baseball, MLB Advanced Media, Baseball Savant, Sports Info Solutions, Pitcher List, Tom Tango or Thomas Nestico (TJStats).

fWAR is a statistic of FanGraphs. bWAR (Baseball-Reference WAR) is a statistic of Sports Reference LLC. The xWAR concept is the work of Thomas Nestico. Statcast metrics (xwOBA, xERA, Fielding Run Value) belong to MLB Advanced Media. Defensive Runs Saved belongs to Sports Info Solutions. All names and trademarks belong to their respective owners and are used here only to identify the source of the data.

This repository publishes only code and the aggregate summary statistics shown above (correlations and sample sizes) from my own analysis. It does not reproduce or redistribute any provider's data tables, player-level statistics or leaderboards. To view the underlying statistics, please visit the original sources linked above.

Data accessed November 2026. Source figures may be revised by their providers. Results are provided as is, without warranty of accuracy, and are not betting, fantasy or financial advice.
"""
(ROOT / "README.md").write_text(readme)
print("wrote", ROOT / "README.md")
