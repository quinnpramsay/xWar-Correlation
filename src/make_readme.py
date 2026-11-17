"""Write README.md from the local results (results/results_main.json, results/changes.json,
results/defense_weights.csv). The README shows only aggregate summary statistics."""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "results"
o = json.load(open(R / "results_main.json"))
ch = json.load(open(R / "changes.json"))
dw = pd.read_csv(R / "defense_weights.csv")
SENS = {t: json.load(open(R / f"results_{t}.json")) for t in ["strict", "no2020", "played", "fixed1619"]}
COLS = ["xWAR_orig", "xWAR_upd", "fWAR", "bWAR", "aWAR"]
NAME = {"xWAR_orig": "xWAR original", "xWAR_upd": "xWAR updated", "fWAR": "fWAR", "bWAR": "bWAR", "aWAR": "aWAR"}
ROWS = [("next", "Next season"), ("mean5", "Average of next 5 seasons"), ("max5", "Best season in next 5"),
        ("max10", "Best season in next 10 †")]


def find(res, group, kind, tgt):
    G = res[group]
    pool = {"next": G["next"], "mean5": G["mean5"], "max5": G["max"], "max10": G["max"]}[kind]
    return next(e for e in pool if e and e["target"] == f"{kind}_{tgt}")


def md_table(tgt, group):
    L = ["| Horizon | n | " + " | ".join(NAME[c] for c in COLS) + " | Leader's edge [95% interval] |",
         "|---|---:|" + "---:|" * len(COLS) + "---|"]
    for kind, kl in ROWS:
        e = find(o, group, kind, tgt)
        clear = e["gap_ci"][0] > 0
        cells = [f"**{e['r'][c]:.3f}**" if c == e["best"] else f"{e['r'][c]:.3f}" for c in COLS]
        lo, hi = e["gap_ci"]
        L.append(f"| {kl} | {e['n']:,} | " + " | ".join(cells) + f" | {e['gap']:+.3f} [{lo:+.3f}, {hi:+.3f}] {'clear' if clear else 'tie'} |")
    return "\n".join(L)


def md_changes():
    L = ["| Group | Change | Next season | Average of next 5 | Best season in next 10 |", "|---|---|---|---|---|"]
    for group, gl in [("pitchers", "Pitchers"), ("hitters", "Hitters")]:
        by = {}
        for r in ch[group]:
            by.setdefault(r["change"], {})[r["target"]] = r
        for cname, t in by.items():
            cells = []
            for tl in ["Next season", "Average of next 5", "Best season in next 10"]:
                r = t[tl]
                sig = " **(clear)**" if (r["hi"] < 0 or r["lo"] > 0) else ""
                cells.append(f"{r['r_original']:.3f} → {r['r_changed']:.3f} ({r['diff']:+.3f} [{r['lo']:+.3f}, {r['hi']:+.3f}]){sig}")
            L.append(f"| {gl} | {cname} | " + " | ".join(cells) + " |")
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
ours = dw[dw.window == "2021-2026"].set_index("group")
wmd = "\n".join(["| Position | FRV weight (Tango) | DRS weight | Our check, 2021–26 | Year-to-year pairs |", "|---|---:|---:|---:|---:|"] +
                [f"| {p} | {TANGO[p]:.2f} | {1 - TANGO[p]:.2f} | {ours.loc[p, 'FRV weight']:.2f} | {int(ours.loc[p, 'pairs'])} |"
                 for p in ["C", "OF", "1B", "SS", "2B", "3B"]])

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
px = {r["target"]: r for r in ch["pitchers"] if r["change"] == "xFIP → xERA"}
hp = {r["target"]: r for r in ch["hitters"] if r["change"] == "Park factor removed"}
nh, nhp, np_, npp = o["hitters"]["n_rows"], o["hitters"]["n_players"], o["pitchers"]["n_rows"], o["pitchers"]["n_players"]

# robustness checks used in the text (asserted so the README can't drift from the results)
for res in [o] + list(SENS.values()):
    for kind in ["next", "mean5", "max10"]:
        e = find(res, "pitchers", kind, "aWAR")
        assert e["best"] == "xWAR_orig" and e["gap_ci"][0] > 0, "pitcher claim no longer holds"
    for kind in ["next", "mean5"]:
        assert find(res, "hitters", kind, "aWAR")["gap_ci"][0] <= 0, "hitter tie claim no longer holds"
    e = find(res, "hitters", "max10", "aWAR")
    assert e["ranking"][-1] == "xWAR_upd", "hitter 10-year claim no longer holds"

readme = f"""# xWAR Correlation: does xWAR predict the future better than WAR?

**xWAR was created by [Thomas Nestico (TJStats on X)](https://x.com/TJStats).** His official version and full leaderboard are at [tjstats.ca/xwar](https://tjstats.ca/xwar/). This repository is an independent rebuild of both of his published versions from his descriptions. It may differ from his exact implementation, so use his leaderboard for official xWAR values. Fielding weights come from [Tom Tango's research](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs). Full credits and a disclaimer are at the bottom.

xWAR is built from fWAR and uses expected stats to capture player value from the factors a player can more directly impact. This project asks a different question than xWAR was designed for: **how well does each version predict a player's future WAR**, compared with FanGraphs WAR (fWAR), Baseball-Reference WAR (bWAR) and their average (aWAR)? A stat can describe a season well and still forecast worse, so these results are about prediction only.

## The two versions of xWAR

| | xWAR original (Nov 16, 2026) | xWAR updated (Nov 17, 2026) |
|---|---|---|
| Base | fWAR | fWAR |
| Batting | xwOBA, with wOBA park factors | xwOBA, park factors removed ("xwOBA is mostly unaffected by location") |
| Pitching | xFIP | xERA ("to remain consistent with the xwOBA framework") |
| Defense | Average of FRV and DRS | FRV and DRS weighted by position, following Tom Tango's research |

## The short answer

| | Result |
|---|---|
| **Pitchers** | **The original xWAR (xFIP) is the best predictor** at every horizon and in every check. Next-season aWAR: r = {pn['r']['xWAR_orig']:.3f}, vs {pn['r']['fWAR']:.3f} for fWAR. The updated xWAR predicts worse than plain fWAR ({pn['r']['xWAR_upd']:.3f}), and the xFIP → xERA swap accounts for all of the drop. |
| **Hitters** | **A tie.** Over 1 to 5 seasons, both xWARs and aWAR finish within noise of each other (next season: original {hn['r']['xWAR_orig']:.3f}, updated {hn['r']['xWAR_upd']:.3f}, aWAR {hn['r']['aWAR']:.3f}). All three edge out fWAR and bWAR by about 0.01 to 0.02. For the best season over the next 10 years, the updated version ranks last ({h10['r']['xWAR_upd']:.3f}), mostly because of the park-factor removal. |
| **Horizon** | **5 seasons.** The future average levels off by 5 seasons (reliability 0.89 hitters, 0.85 pitchers). Longer windows cost a base season per year and mostly measure aging. |

## What each Nov 17 change did

Starting from the original xWAR, each change was applied on its own, then all three together (the updated xWAR). Values are r with future aWAR, original → changed, with the change and its 95% paired bootstrap interval. **(clear)** means the interval excludes zero.

{md_changes()}

- **xFIP → xERA** is the only change with a clear effect, and it lowers predictive accuracy at every horizon. This matches published research: xERA predicts next-season ERA worse than xFIP and SIERA ([Dan Richards, Pitcher List](https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/)). Contact quality allowed is less stable year to year for pitchers than strikeouts, walks and ground balls.
- **Tango's position weights** have no measurable effect on prediction (within ±0.003). They are better grounded, but fielding moves a player's WAR by only about 0.2 wins a season, too little to change a forecast.
- **Removing park factors** has no effect over 1 to 5 seasons and lowers the 10-year result ({hp['Best season in next 10']['diff']:+.3f}, interval [{hp['Best season in next 10']['lo']:+.3f}, {hp['Best season in next 10']['hi']:+.3f}], only the 2016 class). Derived xwOBA park factors, which TJStats plans to add, would be worth testing here.

## Results

Each value is the Pearson r between a stat in one season and the player's later WAR. The highest value in each row is bold. "Clear" means the leader's 95% interval over second place is above zero; "tie" means it isn't.

{chr(10).join(chr(10) + x + chr(10) for x in tables)}
† Only the 2016 season has 10 complete future seasons (2017 to 2026), so this row uses about 350 hitters and 385 pitchers. Treat it as a rough check.

## Why a 5-season horizon

Before seeing which stat won, we set a rule (see [PLAN.md](PLAN.md)): pick the shortest horizon where the future average stops getting more reliable (gain under 0.03 per added year) and the ranking of the stats stops changing. For pitchers the rule picked 5 seasons in 4 of 5 checks, and 6 in the other. For hitters it landed between 5 and 7, because the top hitter stats are tied and keep swapping places. Five seasons keeps the most data at nearly full reliability. Past that, aging (about 0.5 WAR lost per year after 30) and survivor bias drive the numbers more than the season being measured.

{md_horizon()}

Reliability is split-half (odd vs even future seasons), corrected to the full window. Each added season removes one base season from the sample.

## How the rebuild works

- **Batting:** FanGraphs batting runs plus (xwOBA − wOBA) / wOBA scale × PA, using Baseball Savant's xwOBA and wOBA, centered so each season's league total is unchanged. That keeps FanGraphs' park adjustment (original version). The updated version instead measures xwOBA against the MLB non-pitcher average with no park adjustment.
- **Fielding:** FanGraphs fielding is based on FRV. The original version replaces it with the average of FRV and DRS. The updated version uses w × FRV + (1 − w) × DRS, with both centered within position and season and w set by position (below).
- **Pitching:** fWAR plus (FIP − xFIP) × IP / 9 (original) or (FIP − xERA) × IP / 9 (updated), converted to wins with each pitcher's own FanGraphs runs-per-win ratio and centered so each season's league average is unchanged.
- **League check:** league-wide xWAR stays within about 1% of fWAR in every season.

### Fielding weights by position (updated version)

From Tom Tango's ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) (September 2026). We reproduced his test on the same seasons ([src/defense_weights.py](src/defense_weights.py)) and got the same sample sizes and year-to-year correlations within 0.02. Our own fitted weights agree on direction: catchers and outfielders lean FRV, 2B and 3B lean DRS.

{wmd}

## Sample and method

- **Base seasons:** 2016 to 2025, the years Statcast FRV is available; future seasons run through 2026. Hitters with 200+ PA ({nh:,} player-seasons, {nhp:,} players); pitchers with 40+ IP ({np_:,} player-seasons, {npp:,} players).
- **Missing seasons:** a season with no MLB appearance counts as 0 WAR.
- **2020:** WAR in 2020 is scaled by 162/60.
- **Uncertainty:** 95% intervals come from 2,000 bootstrap resamples of players, since a player can appear in several base seasons.
- **Robustness:** every claim above also holds with 100+ PA / 100+ IP only, without the 2020 scaling, among players who played the next season, and on 2016–2019 base seasons only.
- **Limits:** WAR includes playing time, so these correlations partly measure who keeps getting at-bats or innings. aWAR averages two measurements of the same season, which by itself reduces noise.

## Data

All data was downloaded locally and is **not included in this repository**. Some of it is behind paywalls (FanGraphs membership exports), and every provider has its own rules on reuse and redistribution. The sources are FanGraphs (fWAR, FIP, xFIP, xERA, DRS, FRV), Baseball Savant (xwOBA, wOBA, xERA) and Baseball-Reference (bWAR), all for 2015 to 2026. To rerun the analysis, get the data from those sites under their terms and place it in a local `data/` folder.

## Code

| Path | Contents |
|---|---|
| `PLAN.md` | Test plan written before any results, plus later amendments |
| `src/build.py` | Builds the player-season table with fWAR, bWAR, aWAR and both xWAR versions |
| `src/defense_weights.py` | Replicates Tango's FRV vs DRS test |
| `src/analyze.py` | Main tests (see PLAN.md). Sensitivity flags: `--pa 400 --ip 100`, `--no2020scale`, `--played-only`, `--bases 2016-2019` |
| `src/changes.py` | Tests each Nov 17 change on its own |
| `src/report.py`, `src/make_readme.py` | Write the full tables and this README |

Requirements: Python 3.9+, pandas, numpy (`pip install -r requirements.txt`).

## Credits

- **xWAR:** [Thomas Nestico (TJStats on X)](https://x.com/TJStats). Official leaderboard: [tjstats.ca/xwar](https://tjstats.ca/xwar/).
- **Fielding-weight research:** Tom Tango, ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) and ["FRV v DRS"](https://tangotiger.com/index.php/site/article/frv-v-drs), Tangotiger Blog. Tom Tango also created FIP and, with Mitchel Lichtman and Andrew Dolphin, wOBA (*The Book*).
- **fWAR, FIP, xFIP and DRS exports:** [FanGraphs](https://www.fangraphs.com). xFIP was developed by Dave Studeman of The Hardball Times.
- **bWAR:** [Baseball-Reference.com](https://www.baseball-reference.com) (Sports Reference LLC). Its WAR framework was originally provided by Sean Smith.
- **xwOBA, wOBA, xERA and Fielding Run Value:** MLB Statcast via [Baseball Savant](https://baseballsavant.mlb.com) (MLB Advanced Media).
- **Defensive Runs Saved (DRS):** [Sports Info Solutions](https://www.sportsinfosolutions.com), as published on FanGraphs.
- **ERA-estimator research:** Dan Richards, ["The Relative Value of FIP, xFIP, SIERA and xERA, Pt. II"](https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/), Pitcher List (2020).
- **Aging research:** Piper Slowinski, ["Aging Curve"](https://library.fangraphs.com/principles/aging-curve), FanGraphs Library.

## Disclaimer

**For educational and non-commercial purposes only.** This is an independent analysis. It is not affiliated with, sponsored by or endorsed by FanGraphs, Sports Reference LLC (Baseball-Reference.com), Major League Baseball, MLB Advanced Media, Baseball Savant, Sports Info Solutions, Pitcher List, Tom Tango or Thomas Nestico (TJStats).

fWAR is a statistic of FanGraphs. bWAR (Baseball-Reference WAR) is a statistic of Sports Reference LLC. xWAR is the work of Thomas Nestico. Statcast metrics (xwOBA, xERA, Fielding Run Value) belong to MLB Advanced Media. Defensive Runs Saved belongs to Sports Info Solutions. All names and trademarks belong to their respective owners and are used here only to identify the source of the data.

This repository publishes only code and the aggregate summary statistics shown above (correlations and sample sizes) from our own analysis. It does not reproduce or redistribute any provider's data tables, player-level statistics or leaderboards. To view the underlying statistics, please visit the original sources linked above.

Data accessed November 2026. Source figures may be revised by their providers. Results are provided as is, without warranty of accuracy, and are not betting, fantasy or financial advice.
"""
(ROOT / "README.md").write_text(readme)
print("wrote", ROOT / "README.md")
