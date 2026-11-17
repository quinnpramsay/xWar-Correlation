# xWAR test plan (written 2026-11-17, before any results)

## Stats compared (predictors, one player-season each)
| Stat | Definition |
|---|---|
| fWAR | FanGraphs WAR (batting + pitching) |
| bWAR | Baseball-Reference WAR (batting + pitching) |
| aWAR | (fWAR + bWAR) / 2 |
| xWAR-1 | fWAR with batting runs from xwOBA instead of wOBA, fielding = mean(FRV, DRS), pitcher runs from xFIP instead of FIP |
| xWAR-2 | Same as xWAR-1, but pitchers use xERA (Statcast xwOBA-against on the ERA scale) instead of xFIP |

xWAR-1 and xWAR-2 are identical for hitters. They differ only for pitchers.

### xWAR construction (deltas on top of fWAR)
- Batting: ΔBat = (xwOBA − wOBA, from Savant, centered on the season's PA-weighted mean) / wOBA scale × PA.
- Fielding: ΔFld = mean(FRV, DRS) − FRV = (DRS − FRV) / 2, summed over positions played. FanGraphs fielding is FRV-based since 2016 (r = 0.95; mean gap within ±2 runs at every position), so replacing FRV with the average moves fWAR's fielding halfway to DRS.
- Pitching: ΔPit = (FIP − xFIP) × IP / 9 for xWAR-1, or (FIP − xERA) × IP / 9 for xWAR-2. Both are centered so each season's IP-weighted league mean of FIP is unchanged.
- Runs to wins: hitters use the season's runs per win (FanGraphs formula: 9 × lgR/IP × 1.5 + 3). Pitchers use their own FanGraphs RAR/WAR ratio when |WAR| ≥ 0.5 and the ratio is between 7 and 13, otherwise the season value.
- wOBA scale for each season is estimated from the FanGraphs export (slope of batting runs per PA on wOBA). It matches the published values within about 0.02.

## Samples
- Base seasons 2016 to 2025. FRV starts in 2016, and 2026 has no future.
- Hitters: PA ≥ 200 in the base season. Pitchers: IP ≥ 40. Two-way players count in both groups.
- 2020 WAR values (predictors and targets) are scaled by 162/60.
- A future season with no MLB appearance counts as 0 WAR.

## Targets
1. Next-season fWAR, bWAR and aWAR.
2. Best single season (max WAR) over the next 10 years. Only the 2016 base season has 10 future seasons (2017 to 2026), so this is reported but small. The max over shorter windows is also shown.
3. Mean WAR over the next N years, for N = 1 to 10.

## Metrics
- Primary: Pearson r between predictor and target, with 95% intervals from 2,000 bootstrap resamples of players (clustered, because a player appears in several base seasons).
- Paired bootstrap difference between each stat and the best stat on the same resamples. A stat "wins" only if the interval of its lead over the second-best stat excludes 0.
- Secondary: Spearman ρ; r after controlling for age and age²; leave-one-season-out prediction error (RMSE) of target ~ stat + age + age².

## Choosing N (for target 3)
Decided before seeing the predictor comparison:
- For each N: sample size, split-half reliability of the target (odd vs even future years), the r of every stat and the CI of the gap between the top two stats.
- Pick the smallest N at which (a) target reliability levels off (gain < 0.03 from N−1 to N) and (b) the ranking of the five stats is the same as at N+1 and N+2. If no N passes both by N = 7, pick the N with the narrowest CI on the top-two gap.

## Known biases to report
- An fWAR target favors fWAR and both xWARs (shared FanGraphs base). A bWAR target favors bWAR. aWAR is the most neutral target, but the aWAR predictor shares half its components with each target.
- aWAR averages two measurements of the same season, which cuts noise. Part of any aWAR win is averaging, not a better method.

## Sensitivities
PA ≥ 400 or IP ≥ 100; 2020 not scaled; only players who played in the target season; base seasons 2016 to 2019 only (fixed sample across N).

## Amendment (2026-11-17, after the first results, at the user's direction)
- Renamed xWAR-1 → xWAR(xFIP), xWAR-2 → xWAR(xERA).
- Fielding: replaced the 50/50 FRV/DRS average with Tango's position weights (FRV share: C .93, OF .92, 1B .67, SS .60, 2B .40, 3B .40), with both metrics centered within position-season.
- Batting: batting runs come from xwOBA vs the MLB non-pitcher average with no park factor, replacing FanGraphs' park-adjusted batting runs.
- Tests, targets, metrics and the N rule are unchanged. The earlier variants are kept in data/processed/player_seasons.csv for comparison.
- Update: the park factor was restored at the user's direction (FanGraphs park-adjusted batting runs plus the xwOBA − wOBA delta). Removing it gave no gain over 1 to 5 years and was worse for the 10-year best season. The no-park and 50/50-fielding variants are still built in src/build.py for comparison.
- Update: the main comparison is this repo's xWAR(xFIP) and xWAR(xERA) (park factor kept, Tango position weights), tuned toward predicting future WAR.
- Added after the main tests (not pre-registered): year-to-year stickiness of each stat, src/stickiness.py.
