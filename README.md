# xWAR Correlation: is xWAR stickier than WAR, and does it predict the future better?

**The idea for xWAR comes from [Thomas Nestico (TJStats on X)](https://x.com/TJStats).** His goal is to capture player value from the factors a player can most directly impact, while my goal is to predict how sticky xWAR is and a player's future WAR, so I made some fine-tuning changes to help toward that goal. Fielding weights come from [Tom Tango's research](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs). Full credits and a disclaimer are at the bottom.

When looking at expected stats, I usually like to see whether a player outperformed or underperformed them, and whether that gap correlates with future outcomes. So I decided to put that together and look into it.

xWAR rebuilds fWAR from the parts of a season a player controls most: expected batting (xwOBA), expected pitching (xFIP or xERA) and a position-weighted blend of two fielding metrics. I wanted to test two things: whether xWAR is **stickier** than FanGraphs WAR (fWAR), Baseball-Reference WAR (bWAR) and their average (aWAR), meaning it predicts itself from one season to the next better, and whether it **predicts other WAR** (a player's future fWAR, bWAR and aWAR) better than those stats do.

## Top finding: xWAR is stickier than fWAR and bWAR

Each value is the correlation between a stat in one season and the same stat the next season, for players who qualified both years (200+ PA or 40+ IP, base seasons 2016 to 2025). Higher means stickier.

| Group | n | xWAR(xFIP) | xWAR(xERA) | fWAR | bWAR | aWAR | xWAR's edge over next best [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Hitters | 2,364 | **0.552** | same as xFIP | 0.507 | 0.494 | 0.507 | +0.045 [+0.027, +0.064] over fWAR |
| Pitchers | 2,314 | **0.674** | 0.556 | 0.550 | 0.352 | 0.472 | +0.118 [+0.091, +0.149] over xWAR(xERA) |

xWAR is the stickiest version of WAR for both hitters and pitchers, and the edge is clear in both groups. For pitchers, xWAR(xFIP) is 0.124 stickier than fWAR and 0.323 stickier than bWAR. For hitters, xWAR is 0.045 stickier than fWAR and 0.058 stickier than bWAR. Sticky doesn't automatically mean better, since a stat can also be sticky by ignoring real differences between players (xFIP, for example, gives every pitcher a league-average home run rate on fly balls). That's why the second test, predicting actual future WAR, matters too.

## The short answer

| | Result |
|---|---|
| **Stickiness** | **xWAR is the stickiest** for both hitters (r = 0.552 vs 0.507 for fWAR) and pitchers (r = 0.674 vs 0.550). |
| **Predicting WAR: pitchers** | **xWAR(xFIP) is the best predictor** at every horizon and on every target. Next-season aWAR: r = 0.562, vs 0.531 for fWAR. The xERA version predicts worse than plain fWAR (0.518). |
| **Predicting WAR: hitters** | **A tie.** xWAR and aWAR finish within noise of each other (next-season r = 0.574 vs 0.565). Both edge out fWAR and bWAR by about 0.01 to 0.02. |
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


### Table 1. Hitters: correlation with future aWAR

aWAR is the fairest target, because it isn't built from any single site's WAR.

| Horizon | n | xWAR | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---|
| Next season | 3,336 | **0.574** | 0.557 | 0.554 | 0.565 | +0.009 [+0.000, +0.019] tie |
| Average of next 5 seasons | 1,903 | **0.595** | 0.583 | 0.586 | 0.594 | +0.001 [-0.009, +0.011] tie |
| Best season in next 5 | 1,903 | **0.609** | 0.593 | 0.600 | 0.607 | +0.002 [-0.007, +0.012] tie |
| Best season in next 10 † | 353 | 0.587 | 0.577 | **0.600** | 0.599 | +0.000 [-0.014, +0.014] tie |


### Table 2. Pitchers: correlation with future aWAR

aWAR is the fairest target, because it isn't built from any single site's WAR.

| Horizon | n | xWAR(xFIP) | xWAR(xERA) | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,721 | **0.562** | 0.518 | 0.531 | 0.436 | 0.501 | +0.031 [+0.019, +0.043] clear |
| Average of next 5 seasons | 2,098 | **0.578** | 0.519 | 0.533 | 0.449 | 0.508 | +0.046 [+0.029, +0.063] clear |
| Best season in next 5 | 2,098 | **0.610** | 0.555 | 0.564 | 0.473 | 0.537 | +0.046 [+0.031, +0.063] clear |
| Best season in next 10 † | 385 | **0.591** | 0.532 | 0.555 | 0.415 | 0.503 | +0.036 [+0.006, +0.066] clear |


### Table 3. Hitters: correlation with future bWAR

This target favors bWAR, since it shares bWAR's own method.

| Horizon | n | xWAR | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---|
| Next season | 3,336 | **0.557** | 0.536 | 0.551 | 0.553 | +0.004 [-0.006, +0.014] tie |
| Average of next 5 seasons | 1,903 | 0.585 | 0.569 | 0.585 | **0.587** | +0.003 [-0.009, +0.013] tie |
| Best season in next 5 | 1,903 | 0.598 | 0.580 | 0.599 | **0.600** | +0.001 [-0.006, +0.009] tie |
| Best season in next 10 † | 353 | 0.575 | 0.562 | **0.598** | 0.591 | +0.007 [-0.007, +0.022] tie |


### Table 4. Pitchers: correlation with future bWAR

This target favors bWAR, since it shares bWAR's own method.

| Horizon | n | xWAR(xFIP) | xWAR(xERA) | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,721 | **0.487** | 0.460 | 0.463 | 0.386 | 0.440 | +0.024 [+0.011, +0.038] clear |
| Average of next 5 seasons | 2,098 | **0.539** | 0.492 | 0.501 | 0.428 | 0.481 | +0.038 [+0.020, +0.056] clear |
| Best season in next 5 | 2,098 | **0.561** | 0.514 | 0.521 | 0.447 | 0.501 | +0.040 [+0.023, +0.058] clear |
| Best season in next 10 † | 385 | **0.560** | 0.501 | 0.532 | 0.395 | 0.480 | +0.028 [-0.002, +0.058] tie |


### Table 5. Hitters: correlation with future fWAR

This target favors fWAR and both xWARs, which are built on fWAR.

| Horizon | n | xWAR | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---|
| Next season | 3,336 | **0.576** | 0.563 | 0.543 | 0.562 | +0.013 [+0.004, +0.023] clear |
| Average of next 5 seasons | 1,903 | **0.599** | 0.590 | 0.580 | 0.595 | +0.004 [-0.006, +0.016] tie |
| Best season in next 5 | 1,903 | **0.612** | 0.599 | 0.591 | 0.605 | +0.007 [-0.002, +0.017] tie |
| Best season in next 10 † | 353 | 0.592 | 0.585 | 0.589 | **0.597** | +0.005 [-0.008, +0.019] tie |


### Table 6. Pitchers: correlation with future fWAR

This target favors fWAR and both xWARs, which are built on fWAR.

| Horizon | n | xWAR(xFIP) | xWAR(xERA) | fWAR | bWAR | aWAR | Leader's edge [95% interval] |
|---|---:|---:|---:|---:|---:|---:|---|
| Next season | 3,721 | **0.605** | 0.546 | 0.567 | 0.460 | 0.532 | +0.037 [+0.026, +0.049] clear |
| Average of next 5 seasons | 2,098 | **0.602** | 0.533 | 0.550 | 0.458 | 0.522 | +0.052 [+0.035, +0.070] clear |
| Best season in next 5 | 2,098 | **0.637** | 0.574 | 0.586 | 0.484 | 0.554 | +0.051 [+0.036, +0.069] clear |
| Best season in next 10 † | 385 | **0.607** | 0.555 | 0.567 | 0.427 | 0.515 | +0.039 [+0.011, +0.072] clear |

† Only the 2016 season has 10 complete future seasons (2017 to 2026), so this row uses about 350 hitters and 385 pitchers. Treat it as a rough check.

## Why a 5-season horizon

Before seeing which stat won, I set a rule (see [PLAN.md](PLAN.md)): pick the shortest horizon where the future average stops getting more reliable (gain under 0.03 per added year) and the ranking of the stats stops changing. For pitchers the rule picked 5 seasons in 4 of 5 checks, and 6 in the other. For hitters it landed between 5 and 7, because the top hitter stats are tied and keep swapping places. Five seasons keeps the most data at nearly full reliability. Past that, aging (about 0.5 WAR lost per year after 30) and survivor bias drive the numbers more than the season being measured.

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

## How xWAR was built

- **Batting:** FanGraphs batting runs plus (xwOBA − wOBA) / wOBA scale × PA, using Baseball Savant's xwOBA and wOBA, centered so each season's league total is unchanged. FanGraphs' park adjustment is kept. (Removing it gave no gain over 1 to 5 seasons and was worse for the 10-year best season.)
- **Fielding:** FanGraphs fielding is based on FRV, so it is replaced with w × FRV + (1 − w) × DRS, with both centered within position and season. The weight w depends on position (below).
- **Pitching:** fWAR plus (FIP − xFIP) × IP / 9, or (FIP − xERA) × IP / 9, converted to wins with each pitcher's own FanGraphs runs-per-win ratio. Both are centered so each season's league average is unchanged.
- **League check:** league-wide xWAR stays within about 1% of fWAR in every season.

### Fielding weights by position

I used the position weights from Tom Tango's ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) (September 2026), because his research is the best available on how the two metrics compare by position. Catchers and outfielders lean on FRV, while 2B and 3B lean on DRS.

| Position | FRV weight | DRS weight |
|---|---:|---:|
| C | 0.93 | 0.07 |
| OF | 0.92 | 0.08 |
| 1B | 0.67 | 0.33 |
| SS | 0.60 | 0.40 |
| 2B | 0.40 | 0.60 |
| 3B | 0.40 | 0.60 |

## Sample and method

- **Base seasons:** 2016 to 2025, the years Statcast FRV is available; future seasons run through 2026. Hitters with 200+ PA (3,336 player-seasons, 963 players); pitchers with 40+ IP (3,721 player-seasons, 1,224 players).
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
| `src/stickiness.py` | Year-to-year stickiness of each stat (added after the main tests) |
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
