# xWAR Correlation: does xWAR predict the future better than WAR?

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
| **Pitchers** | **The original xWAR (xFIP) is the best predictor** at every horizon and in every check. Next-season aWAR: r = 0.562, vs 0.531 for fWAR. The updated xWAR predicts worse than plain fWAR (0.518), and the xFIP → xERA swap accounts for all of the drop. |
| **Hitters** | **A tie.** Over 1 to 5 seasons, both xWARs and aWAR finish within noise of each other (next season: original 0.573, updated 0.572, aWAR 0.565). All three edge out fWAR and bWAR by about 0.01 to 0.02. For the best season over the next 10 years, the updated version ranks last (0.552), mostly because of the park-factor removal. |
| **Horizon** | **5 seasons.** The future average levels off by 5 seasons (reliability 0.89 hitters, 0.85 pitchers). Longer windows cost a base season per year and mostly measure aging. |

## What each Nov 17 change did

Starting from the original xWAR, each change was applied on its own, then all three together (the updated xWAR). Values are r with future aWAR, original → changed, with the change and its 95% paired bootstrap interval. **(clear)** means the interval excludes zero.

| Group | Change | Next season | Average of next 5 | Best season in next 10 |
|---|---|---|---|---|
| Pitchers | xFIP → xERA | 0.562 → 0.518 (-0.044 [-0.059, -0.030]) **(clear)** | 0.578 → 0.519 (-0.059 [-0.084, -0.037]) **(clear)** | 0.591 → 0.532 (-0.059 [-0.112, -0.009]) **(clear)** |
| Pitchers | All three (updated xWAR) | 0.562 → 0.518 (-0.044 [-0.060, -0.030]) **(clear)** | 0.578 → 0.519 (-0.060 [-0.085, -0.037]) **(clear)** | 0.591 → 0.530 (-0.061 [-0.117, -0.007]) **(clear)** |
| Hitters | FRV/DRS 50/50 → Tango weights | 0.573 → 0.574 (+0.001 [-0.002, +0.004]) | 0.597 → 0.595 (-0.002 [-0.007, +0.003]) | 0.591 → 0.587 (-0.003 [-0.012, +0.006]) |
| Hitters | Park factor removed | 0.573 → 0.571 (-0.002 [-0.011, +0.008]) | 0.597 → 0.598 (+0.001 [-0.017, +0.019]) | 0.591 → 0.556 (-0.035 [-0.074, +0.004]) |
| Hitters | All three (updated xWAR) | 0.573 → 0.572 (-0.001 [-0.011, +0.010]) | 0.597 → 0.597 (+0.000 [-0.018, +0.019]) | 0.591 → 0.552 (-0.039 [-0.082, +0.001]) |

- **xFIP → xERA** is the only change with a clear effect, and it lowers predictive accuracy at every horizon. This matches published research: xERA predicts next-season ERA worse than xFIP and SIERA ([Dan Richards, Pitcher List](https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/)). Contact quality allowed is less stable year to year for pitchers than strikeouts, walks and ground balls.
- **Tango's position weights** have no measurable effect on prediction (within ±0.003). They are better grounded, but fielding moves a player's WAR by only about 0.2 wins a season, too little to change a forecast.
- **Removing park factors** has no effect over 1 to 5 seasons and lowers the 10-year result (-0.035, interval [-0.074, +0.004], only the 2016 class). Derived xwOBA park factors, which TJStats plans to add, would be worth testing here.

## Results

Each value is the Pearson r between a stat in one season and the player's later WAR. The highest value in each row is bold. "Clear" means the leader's 95% interval over second place is above zero; "tie" means it isn't.


### Table 1. Hitters: correlation with future aWAR

aWAR is the fairest target, because it isn't built from any single site's WAR.

| Horizon | n | xWAR original | xWAR updated | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,336 | **0.573** | 0.572 | 0.557 | 0.554 | 0.565 | +0.001 [-0.010, +0.011] tie |
| Average of next 5 seasons | 1,903 | 0.597 | **0.597** | 0.583 | 0.586 | 0.594 | +0.000 [-0.019, +0.018] tie |
| Best season in next 5 | 1,903 | **0.612** | 0.610 | 0.593 | 0.600 | 0.607 | +0.002 [-0.016, +0.020] tie |
| Best season in next 10 † | 353 | 0.591 | 0.552 | 0.577 | **0.600** | 0.599 | +0.000 [-0.014, +0.014] tie |


### Table 2. Pitchers: correlation with future aWAR

aWAR is the fairest target, because it isn't built from any single site's WAR.

| Horizon | n | xWAR original | xWAR updated | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,721 | **0.562** | 0.518 | 0.531 | 0.436 | 0.501 | +0.031 [+0.019, +0.043] clear |
| Average of next 5 seasons | 2,098 | **0.578** | 0.519 | 0.533 | 0.449 | 0.508 | +0.046 [+0.029, +0.063] clear |
| Best season in next 5 | 2,098 | **0.610** | 0.555 | 0.564 | 0.473 | 0.537 | +0.046 [+0.031, +0.063] clear |
| Best season in next 10 † | 385 | **0.591** | 0.530 | 0.555 | 0.415 | 0.503 | +0.036 [+0.006, +0.066] clear |


### Table 3. Hitters: correlation with future bWAR

This target favors bWAR, since it shares bWAR's own method.

| Horizon | n | xWAR original | xWAR updated | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,336 | **0.557** | 0.555 | 0.536 | 0.551 | 0.553 | +0.002 [-0.008, +0.013] tie |
| Average of next 5 seasons | 1,903 | 0.587 | 0.586 | 0.569 | 0.585 | **0.587** | +0.000 [-0.010, +0.009] tie |
| Best season in next 5 | 1,903 | **0.602** | 0.598 | 0.580 | 0.599 | 0.600 | +0.002 [-0.007, +0.010] tie |
| Best season in next 10 † | 353 | 0.579 | 0.540 | 0.562 | **0.598** | 0.591 | +0.007 [-0.007, +0.022] tie |


### Table 4. Pitchers: correlation with future bWAR

This target favors bWAR, since it shares bWAR's own method.

| Horizon | n | xWAR original | xWAR updated | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,721 | **0.487** | 0.460 | 0.463 | 0.386 | 0.440 | +0.024 [+0.011, +0.038] clear |
| Average of next 5 seasons | 2,098 | **0.539** | 0.491 | 0.501 | 0.428 | 0.481 | +0.038 [+0.020, +0.056] clear |
| Best season in next 5 | 2,098 | **0.561** | 0.514 | 0.521 | 0.447 | 0.501 | +0.040 [+0.023, +0.058] clear |
| Best season in next 10 † | 385 | **0.560** | 0.499 | 0.532 | 0.395 | 0.480 | +0.028 [-0.002, +0.058] tie |


### Table 5. Hitters: correlation with future fWAR

This target favors fWAR and both xWARs, which are built on fWAR.

| Horizon | n | xWAR original | xWAR updated | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,336 | 0.574 | **0.575** | 0.563 | 0.543 | 0.562 | +0.001 [-0.010, +0.011] tie |
| Average of next 5 seasons | 1,903 | 0.600 | **0.601** | 0.590 | 0.580 | 0.595 | +0.002 [-0.019, +0.020] tie |
| Best season in next 5 | 1,903 | **0.614** | 0.614 | 0.599 | 0.591 | 0.605 | +0.000 [-0.017, +0.017] tie |
| Best season in next 10 † | 353 | 0.594 | 0.556 | 0.585 | 0.589 | **0.597** | +0.004 [-0.007, +0.013] tie |


### Table 6. Pitchers: correlation with future fWAR

This target favors fWAR and both xWARs, which are built on fWAR.

| Horizon | n | xWAR original | xWAR updated | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,721 | **0.605** | 0.546 | 0.567 | 0.460 | 0.532 | +0.037 [+0.026, +0.049] clear |
| Average of next 5 seasons | 2,098 | **0.602** | 0.532 | 0.550 | 0.458 | 0.522 | +0.052 [+0.035, +0.070] clear |
| Best season in next 5 | 2,098 | **0.637** | 0.574 | 0.586 | 0.484 | 0.554 | +0.051 [+0.036, +0.069] clear |
| Best season in next 10 † | 385 | **0.607** | 0.553 | 0.567 | 0.427 | 0.515 | +0.039 [+0.011, +0.072] clear |

† Only the 2016 season has 10 complete future seasons (2017 to 2026), so this row uses about 350 hitters and 385 pitchers. Treat it as a rough check.

## Why a 5-season horizon

Before seeing which stat won, we set a rule (see [PLAN.md](PLAN.md)): pick the shortest horizon where the future average stops getting more reliable (gain under 0.03 per added year) and the ranking of the stats stops changing. For pitchers the rule picked 5 seasons in 4 of 5 checks, and 6 in the other. For hitters it landed between 5 and 7, because the top hitter stats are tied and keep swapping places. Five seasons keeps the most data at nearly full reliability. Past that, aging (about 0.5 WAR lost per year after 30) and survivor bias drive the numbers more than the season being measured.

| N seasons | Base seasons | Hitter n | Hitter reliability | Pitcher n | Pitcher reliability |
|---:|---|---:|---:|---:|---:|
| 1 | 2016-2025 | 3,336 | — | 3,721 | — |
| 2 | 2016-2024 | 2,988 | 0.76 | 3,319 | 0.70 |
| 3 | 2016-2023 | 2,623 | 0.83 | 2,917 | 0.78 |
| 4 | 2016-2022 | 2,261 | 0.87 | 2,507 | 0.82 |
| **5** | 2016-2021 | 1,903 | 0.89 | 2,098 | 0.85 |
| 6 | 2016-2020 | 1,541 | 0.91 | 1,700 | 0.86 |
| 7 | 2016-2019 | 1,417 | 0.92 | 1,589 | 0.87 |
| 8 | 2016-2018 | 1,057 | 0.93 | 1,191 | 0.88 |
| 9 | 2016-2017 | 702 | 0.94 | 795 | 0.89 |
| 10 | 2016-2016 | 353 | 0.94 | 385 | 0.90 |

Reliability is split-half (odd vs even future seasons), corrected to the full window. Each added season removes one base season from the sample.

## How the rebuild works

- **Batting:** FanGraphs batting runs plus (xwOBA − wOBA) / wOBA scale × PA, using Baseball Savant's xwOBA and wOBA, centered so each season's league total is unchanged. That keeps FanGraphs' park adjustment (original version). The updated version instead measures xwOBA against the MLB non-pitcher average with no park adjustment.
- **Fielding:** FanGraphs fielding is based on FRV. The original version replaces it with the average of FRV and DRS. The updated version uses w × FRV + (1 − w) × DRS, with both centered within position and season and w set by position (below).
- **Pitching:** fWAR plus (FIP − xFIP) × IP / 9 (original) or (FIP − xERA) × IP / 9 (updated), converted to wins with each pitcher's own FanGraphs runs-per-win ratio and centered so each season's league average is unchanged.
- **League check:** league-wide xWAR stays within about 1% of fWAR in every season.

### Fielding weights by position (updated version)

From Tom Tango's ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) (September 2026). We reproduced his test on the same seasons ([src/defense_weights.py](src/defense_weights.py)) and got the same sample sizes and year-to-year correlations within 0.02. Our own fitted weights agree on direction: catchers and outfielders lean FRV, 2B and 3B lean DRS.

| Position | FRV weight (Tango) | DRS weight | Our check, 2021–26 | Year-to-year pairs |
|---|---:|---:|---:|---:|
| C | 0.93 | 0.07 | 0.77 | 204 |
| OF | 0.92 | 0.08 | 0.77 | 311 |
| 1B | 0.67 | 0.33 | 0.67 | 127 |
| SS | 0.60 | 0.40 | 0.58 | 126 |
| 2B | 0.40 | 0.60 | 0.36 | 108 |
| 3B | 0.40 | 0.60 | 0.29 | 119 |

## Sample and method

- **Base seasons:** 2016 to 2025, the years Statcast FRV is available; future seasons run through 2026. Hitters with 200+ PA (3,336 player-seasons, 963 players); pitchers with 40+ IP (3,721 player-seasons, 1,224 players).
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
