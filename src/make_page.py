"""Generate the public write-up page (results/xwar_page.html) from results/results_main.json.
Only aggregate summary statistics are published. No player-level data is included."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
o = json.load(open(ROOT / "results/results_main.json"))
dw = __import__("pandas").read_csv(ROOT / "results/defense_weights.csv")
COLS = ["xWAR_xFIP", "xWAR_xERA", "fWAR", "bWAR", "aWAR"]
LABEL = {"xWAR_xFIP": "xWAR<span class='sub'>(xFIP)</span>", "xWAR_xERA": "xWAR<span class='sub'>(xERA)</span>",
         "fWAR": "fWAR", "bWAR": "bWAR", "aWAR": "aWAR"}
ROWS = [("next", "Next season"), ("mean5", "Average of next 5 seasons"), ("max5", "Best season in next 5"),
        ("max10", "Best season in next 10<sup>†</sup>")]


def find(group, kind, tgt):
    G = o[group]
    pool = {"next": G["next"], "mean5": G["mean5"], "max5": G["max"], "max10": G["max"]}[kind]
    name = {"next": f"next_{tgt}", "mean5": f"mean5_{tgt}", "max5": f"max5_{tgt}", "max10": f"max10_{tgt}"}[kind]
    return next(e for e in pool if e and e["target"] == name)


def cols_for(group):
    return ["xWAR_xFIP", "fWAR", "bWAR", "aWAR"] if group == "hitters" else COLS


def head(c, group):
    return "xWAR" if (group == "hitters" and c == "xWAR_xFIP") else LABEL[c]


def table(tgt, group):
    cols = cols_for(group)
    h = ["<div class='tw'><table><thead><tr><th class='l'>Horizon</th><th>n</th>"]
    h += [f"<th>{head(c, group)}</th>" for c in cols] + ["<th class='edge'>Leader's edge<br><span class='sub'>95% interval</span></th></tr></thead><tbody>"]
    for kind, kl in ROWS:
        e = find(group, kind, tgt)
        clear = e["gap_ci"][0] > 0
        cells = []
        for c in cols:
            cls = "best clear" if (c == e["best"] and clear) else ("best" if c == e["best"] else "")
            cells.append(f"<td class='{cls}'>{e['r'][c]:.3f}</td>")
        lo, hi = e["gap_ci"]
        verdict = "<span class='pill win'>clear</span>" if clear else "<span class='pill tie'>tie</span>"
        h.append(f"<tr><th class='l'>{kl}</th><td class='n'>{e['n']:,}</td>{''.join(cells)}"
                 f"<td class='edge'>{e['gap']:+.3f} <span class='ci'>[{lo:+.3f}, {hi:+.3f}]</span> {verdict}</td></tr>")
    h.append("</tbody></table></div>")
    return "".join(h)


MDLABEL = {"xWAR_xFIP": "xWAR(xFIP)", "xWAR_xERA": "xWAR(xERA)", "fWAR": "fWAR", "bWAR": "bWAR", "aWAR": "aWAR"}


def md_table(tgt, group):
    cols = cols_for(group)
    hd = ["xWAR" if (group == "hitters" and c == "xWAR_xFIP") else MDLABEL[c] for c in cols]
    L = ["| Horizon | n | " + " | ".join(hd) + " | Leader's edge [95% interval] |", "|---|---:|" + "---:|" * len(cols) + "---|"]
    for kind, kl in ROWS:
        e = find(group, kind, tgt)
        clear = e["gap_ci"][0] > 0
        cells = [f"**{e['r'][c]:.3f}**" if c == e["best"] else f"{e['r'][c]:.3f}" for c in cols]
        lo, hi = e["gap_ci"]
        L.append(f"| {kl.replace('<sup>†</sup>', '†')} | {e['n']:,} | " + " | ".join(cells) + f" | {e['gap']:+.3f} [{lo:+.3f}, {hi:+.3f}] {'clear' if clear else 'tie'} |")
    return "\n".join(L)


def horizon_rows():
    out = []
    H = {g: {e["N"]: e for e in o[g]["horizon"]} for g in ["hitters", "pitchers"]}
    for N in range(1, 11):
        a, b = H["hitters"].get(N), H["pitchers"].get(N)
        rel = lambda e: "—" if e["reliability"] != e["reliability"] else f"{e['reliability']:.2f}"
        hl = " class='pick'" if N == 5 else ""
        out.append(f"<tr{hl}><th>{N}</th><td>{a['bases']}</td><td>{a['n']:,}</td><td>{rel(a)}</td><td>{b['n']:,}</td><td>{rel(b)}</td></tr>")
    return "".join(out)


TANGO = {"C": .93, "OF": .92, "1B": .67, "SS": .60, "2B": .40, "3B": .40}
ours = dw[dw.window == "2021-2026"].set_index("group")
wrows = "".join(f"<tr><th>{p}</th><td>{TANGO[p]:.2f}</td><td>{1 - TANGO[p]:.2f}</td><td>{ours.loc[p, 'FRV weight']:.2f}</td><td>{int(ours.loc[p, 'pairs'])}</td></tr>"
                for p in ["C", "OF", "1B", "SS", "2B", "3B"])
nh, nhp = o["hitters"]["n_rows"], o["hitters"]["n_players"]
np_, npp = o["pitchers"]["n_rows"], o["pitchers"]["n_players"]
pn = find("pitchers", "next", "aWAR")
pm = find("pitchers", "mean5", "aWAR")
hn = find("hitters", "next", "aWAR")

html = f"""<title>Testing xWAR</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: a single reading column styled like a stat sheet; wide tables scroll inside their own frame. */
:root {{
  --bg: #f6f7f9; --paper: #ffffff; --ink: #14213d; --muted: #5b6577; --rule: #d9dee7;
  --accent: #1d5c96; --accent-soft: #e3edf7; --win: #1f7a4d; --win-soft: #e2f3ea; --tie: #6b7280; --tie-soft: #eceef1;
  --display: "Barlow Condensed", "Arial Narrow", sans-serif;
  --body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0f1522; --paper: #161e2e; --ink: #e6ebf3; --muted: #9aa5b8; --rule: #2a3447;
  --accent: #7fb3e6; --accent-soft: #1c2c44; --win: #6fd3a0; --win-soft: #143326; --tie: #a3abb8; --tie-soft: #232b3a; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #0f1522; --paper: #161e2e; --ink: #e6ebf3; --muted: #9aa5b8; --rule: #2a3447;
  --accent: #7fb3e6; --accent-soft: #1c2c44; --win: #6fd3a0; --win-soft: #143326; --tie: #a3abb8; --tie-soft: #232b3a; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--ink); font: 16px/1.6 var(--body); }}
.wrap {{ max-width: 980px; margin: 0 auto; padding-block: 40px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: grid; gap: 40px; }}
.wrap > * {{ min-width: 0; }}
h1, h2, h3 {{ font-family: var(--display); letter-spacing: .01em; line-height: 1.1; text-wrap: balance; margin: 0; }}
h1 {{ font-size: clamp(2.4rem, 6vw, 3.6rem); }}
h2 {{ font-size: 1.9rem; }}
h3 {{ font-size: 1.3rem; }}
p {{ margin: 0; max-width: 68ch; }}
section {{ display: grid; gap: 14px; }}
.eyebrow {{ font: 600 .78rem/1 var(--body); text-transform: uppercase; letter-spacing: .12em; color: var(--accent); }}
.lede {{ font-size: 1.15rem; color: var(--muted); }}
.credit {{ font-size: .95rem; }}
.credit a, a {{ color: var(--accent); }}
.findings {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }}
.finding {{ background: var(--paper); border: 1px solid var(--rule); border-radius: 6px; padding: 18px; display: grid; gap: 8px; align-content: start; }}
.finding .big {{ font: 700 2.2rem/1 var(--display); }}
.finding.win {{ border-top: 4px solid var(--win); }}
.finding.tie {{ border-top: 4px solid var(--tie); }}
.finding.n {{ border-top: 4px solid var(--accent); }}
.tw {{ overflow-x: auto; background: var(--paper); border: 1px solid var(--rule); border-radius: 6px; }}
table {{ border-collapse: collapse; width: 100%; font-variant-numeric: tabular-nums; font-size: .92rem; }}
th, td {{ padding: 9px 12px; text-align: right; border-bottom: 1px solid var(--rule); white-space: nowrap; }}
thead th {{ font: 600 .8rem/1.25 var(--body); color: var(--muted); text-transform: uppercase; letter-spacing: .05em; vertical-align: bottom; }}
td {{ font-family: var(--mono); }}
.l {{ text-align: left; }}
tbody th {{ font-weight: 500; }}
tr.grp th {{ background: var(--accent-soft); font: 700 1.05rem/1 var(--display); letter-spacing: .04em; text-transform: uppercase; color: var(--ink); }}
td.best {{ font-weight: 600; }}
td.best.clear {{ background: var(--win-soft); color: var(--win); }}
td.same {{ color: var(--muted); font-family: var(--body); font-style: italic; }}
td.n {{ color: var(--muted); }}
.sub {{ font-size: .78em; text-transform: none; letter-spacing: 0; font-weight: 400; }}
.ci {{ color: var(--muted); }}
.pill {{ display: inline-block; font: 600 .68rem/1 var(--body); text-transform: uppercase; letter-spacing: .08em; padding: 4px 7px; border-radius: 999px; margin-left: 6px; }}
.pill.win {{ background: var(--win-soft); color: var(--win); }}
.pill.tie {{ background: var(--tie-soft); color: var(--tie); }}
.note {{ font-size: .88rem; color: var(--muted); }}
tr.pick {{ background: var(--accent-soft); }}
.defs {{ display: grid; grid-template-columns: max-content 1fr; gap: 8px 18px; }}
.defs dt {{ font-weight: 600; }}
.defs dd {{ margin: 0; }}
ul {{ margin: 0; padding-left: 1.2em; display: grid; gap: 6px; max-width: 72ch; }}
.legal {{ background: var(--paper); border: 1px solid var(--rule); border-radius: 6px; padding: 20px; display: grid; gap: 10px; font-size: .9rem; }}
@media (max-width: 560px) {{ .defs {{ grid-template-columns: 1fr; gap: 2px 0; }} .defs dd {{ margin-bottom: 8px; }} }}
</style>

<div class="wrap">
<header style="display:grid;gap:14px">
  <div class="eyebrow">Educational analysis · Not affiliated with any data provider</div>
  <h1>Does xWAR predict the future better than WAR?</h1>
  <p class="lede">xWAR rebuilds fWAR from the parts of a season a player controls most: expected batting (xwOBA), expected pitching (xFIP or xERA) and a blend of two fielding metrics. We tested whether it predicts a player's future WAR better than FanGraphs WAR, Baseball-Reference WAR, or the average of the two.</p>
  <p class="credit"><strong>The xWAR idea comes from <a href="https://x.com/TJStats">Thomas Nestico (TJStats on X)</a>.</strong> This page is an independent rebuild from the published description and may differ from the original formula. Fielding weights come from <a href="https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs">Tom Tango's research</a>. Full credits are at the bottom.</p>
</header>

<section>
  <h2>The short answer</h2>
  <div class="findings">
    <div class="finding win"><div class="eyebrow">Pitchers</div><div class="big">xWAR(xFIP)</div><p>Best predictor at every horizon and on every target. Next-season aWAR: r = {pn['r']['xWAR_xFIP']:.3f} vs {pn['r']['fWAR']:.3f} for fWAR. The xERA version predicts worse than plain fWAR.</p></div>
    <div class="finding tie"><div class="eyebrow">Hitters</div><div class="big">A tie</div><p>xWAR and aWAR finish within noise of each other (next-season r = {hn['r']['xWAR_xFIP']:.3f} vs {hn['r']['aWAR']:.3f}). Both edge out fWAR and bWAR by about 0.01 to 0.02.</p></div>
    <div class="finding n"><div class="eyebrow">Horizon</div><div class="big">5 seasons</div><p>The future average levels off by 5 seasons (reliability 0.89 hitters, 0.85 pitchers). Longer windows cost a base season per year and mostly measure aging.</p></div>
  </div>
</section>

<section>
  <h2>The stats compared</h2>
  <dl class="defs">
    <dt>fWAR</dt><dd>FanGraphs Wins Above Replacement.</dd>
    <dt>bWAR</dt><dd>Baseball-Reference Wins Above Replacement.</dd>
    <dt>aWAR</dt><dd>The average of the two: (fWAR + bWAR) / 2.</dd>
    <dt>xWAR(xFIP)</dt><dd>fWAR with batting runs adjusted from wOBA to Statcast xwOBA (park factor kept), fielding as a position-weighted blend of Statcast Fielding Run Value (FRV) and Defensive Runs Saved (DRS), and pitching runs from xFIP instead of FIP.</dd>
    <dt>xWAR(xERA)</dt><dd>The same, with pitching runs from Statcast xERA instead of xFIP. For hitters the two xWARs are identical.</dd>
  </dl>
</section>

<section>
  <h2>How to read the tables</h2>
  <p>Each value is the Pearson r between a stat in one season and the player's later WAR. The highest value in each row is bold, and it is shaded green when its lead over second place is clear (95% interval above zero). For hitters the two xWARs are identical, so they share one column.</p>
  <p class="note">† Only the 2016 season has 10 complete future seasons (2017 to 2026), so this row uses about 350 hitters and 385 pitchers. Treat it as a rough check.</p>
</section>
<section>
  <h2>Table 1 · Hitters: correlation with future aWAR</h2>
  <p>aWAR is the fairest target, because it isn't built from any single site's WAR. The next-season lead is borderline: its interval starts at 0.000.</p>
  {table('aWAR', 'hitters')}
</section>

<section>
  <h2>Table 2 · Pitchers: correlation with future aWAR</h2>
  <p>aWAR is the fairest target, because it isn't built from any single site's WAR.</p>
  {table('aWAR', 'pitchers')}
</section>

<section>
  <h2>Table 3 · Hitters: correlation with future bWAR</h2>
  <p>This target favors bWAR, since it shares bWAR's own method.</p>
  {table('bWAR', 'hitters')}
</section>

<section>
  <h2>Table 4 · Pitchers: correlation with future bWAR</h2>
  <p>This target favors bWAR, since it shares bWAR's own method. xWAR(xFIP) still wins on bWAR's home turf.</p>
  {table('bWAR', 'pitchers')}
</section>

<section>
  <h2>Table 5 · Hitters: correlation with future fWAR</h2>
  <p>This target favors fWAR and both xWARs, which are built on fWAR. xWAR's clear next-season lead here comes mostly from that shared base.</p>
  {table('fWAR', 'hitters')}
</section>

<section>
  <h2>Table 6 · Pitchers: correlation with future fWAR</h2>
  <p>This target favors fWAR and both xWARs, which are built on fWAR.</p>
  {table('fWAR', 'pitchers')}
</section>

<section>
  <h2>Why a 5-season horizon</h2>
  <p>Before seeing which stat won, we set a rule: pick the shortest horizon where the future average stops getting more reliable (gain under 0.03 per added year) and the ranking of the stats stops changing. For pitchers the rule picked 5 seasons in 4 of 5 checks, and 6 in the other. For hitters it landed between 5 and 7, because the top hitter stats are tied and keep swapping places. Five seasons keeps the most data at nearly full reliability. Past that, aging (about 0.5 WAR lost per year after 30) and survivor bias drive the numbers more than the season being measured.</p>
  <div class="tw"><table><thead><tr><th>N seasons</th><th>Base seasons</th><th>Hitter n</th><th>Hitter reliability</th><th>Pitcher n</th><th>Pitcher reliability</th></tr></thead><tbody>{horizon_rows()}</tbody></table></div>
  <p class="note">Reliability is split-half (odd vs even future seasons), corrected to the full window. Each added season removes one base season from the sample.</p>
</section>

<section>
  <h2>How xWAR was built</h2>
  <ul>
    <li><strong>Batting:</strong> FanGraphs batting runs plus (xwOBA − wOBA) / wOBA scale × PA, using Baseball Savant's xwOBA and wOBA, centered so each season's league total is unchanged. FanGraphs' park adjustment is kept.</li>
    <li><strong>Fielding:</strong> FanGraphs fielding is based on FRV, so it is replaced with w × FRV + (1 − w) × DRS, with both centered within position and season. The weight w depends on position (below).</li>
    <li><strong>Pitching:</strong> fWAR plus (FIP − xFIP) × IP / 9, or (FIP − xERA) × IP / 9, converted to wins with each pitcher's own FanGraphs runs-per-win ratio. Both are centered so each season's league average is unchanged.</li>
    <li><strong>League check:</strong> league-wide xWAR stays within 1% of fWAR in every season.</li>
  </ul>
  <h3>Fielding weights by position</h3>
  <p>From Tom Tango's <a href="https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs">"Comparing Statcast Fielding Run Value (FRV) to DRS"</a> (September 2026). We reproduced his test on the same seasons and got the same sample sizes and year-to-year correlations within 0.02. Our own fitted weights agree on direction: catchers and outfielders lean FRV, 2B and 3B lean DRS. Swapping these weights for a flat 50/50 changed no result by more than 0.003.</p>
  <div class="tw"><table><thead><tr><th>Position</th><th>FRV weight (Tango)</th><th>DRS weight</th><th>Our check, 2021–26</th><th>Year-to-year pairs</th></tr></thead><tbody>{wrows}</tbody></table></div>
</section>

<section>
  <h2>Sample and method</h2>
  <ul>
    <li><strong>Base seasons:</strong> 2016 to 2025, the years Statcast FRV is available; future seasons run through 2026. Hitters with 200+ PA ({nh:,} player-seasons, {nhp:,} players); pitchers with 40+ IP ({np_:,} player-seasons, {npp:,} players).</li>
    <li><strong>Missing seasons:</strong> a season with no MLB appearance counts as 0 WAR.</li>
    <li><strong>2020:</strong> WAR in 2020 is scaled by 162/60.</li>
    <li><strong>Uncertainty:</strong> 95% intervals come from 2,000 bootstrap resamples of players, since a player can appear in several base seasons.</li>
    <li><strong>Robustness:</strong> the pitcher result holds with 100+ IP only, without the 2020 scaling, among players who played the next season, and on 2016–2019 base seasons only. The hitter tie holds in all of these too, with aWAR ahead in some and xWAR in others.</li>
    <li><strong>Limits:</strong> WAR includes playing time, so these correlations partly measure who keeps getting at-bats or innings. aWAR averages two measurements of the same season, which by itself reduces noise.</li>
  </ul>
</section>

<section>
  <h2>Credits</h2>
  <ul>
    <li><strong>xWAR concept:</strong> <a href="https://x.com/TJStats">Thomas Nestico (TJStats on X)</a>.</li>
    <li><strong>Fielding-weight research:</strong> Tom Tango, <a href="https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs">"Comparing Statcast Fielding Run Value (FRV) to DRS"</a> and <a href="https://tangotiger.com/index.php/site/article/frv-v-drs">"FRV v DRS"</a>, Tangotiger Blog. Tom Tango also created FIP and, with Mitchel Lichtman and Andrew Dolphin, wOBA (<em>The Book</em>).</li>
    <li><strong>fWAR, wOBA scale inputs, FIP, xFIP and DRS exports:</strong> <a href="https://www.fangraphs.com">FanGraphs</a>. xFIP was developed by Dave Studeman of The Hardball Times.</li>
    <li><strong>bWAR:</strong> <a href="https://www.baseball-reference.com">Baseball-Reference.com</a> (Sports Reference LLC). Its WAR framework was originally provided by Sean Smith.</li>
    <li><strong>xwOBA, wOBA, xERA and Fielding Run Value:</strong> MLB Statcast via <a href="https://baseballsavant.mlb.com">Baseball Savant</a> (MLB Advanced Media).</li>
    <li><strong>Defensive Runs Saved (DRS):</strong> <a href="https://www.sportsinfosolutions.com">Sports Info Solutions</a>, as published on FanGraphs.</li>
    <li><strong>ERA-estimator research:</strong> Dan Richards, <a href="https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/">"The Relative Value of FIP, xFIP, SIERA and xERA, Pt. II"</a>, Pitcher List (2020).</li>
    <li><strong>Aging research:</strong> Piper Slowinski, <a href="https://library.fangraphs.com/principles/aging-curve">"Aging Curve"</a>, FanGraphs Library.</li>
  </ul>
</section>

<section>
  <h2>Disclaimer</h2>
  <div class="legal">
    <p><strong>For educational and non-commercial purposes only.</strong> This is an independent analysis. It is not affiliated with, sponsored by or endorsed by FanGraphs, Sports Reference LLC (Baseball-Reference.com), Major League Baseball, MLB Advanced Media, Baseball Savant, Sports Info Solutions, Pitcher List, Tom Tango or Thomas Nestico (TJStats).</p>
    <p>fWAR is a statistic of FanGraphs. bWAR (Baseball-Reference WAR) is a statistic of Sports Reference LLC. Statcast metrics (xwOBA, xERA, Fielding Run Value) belong to MLB Advanced Media. Defensive Runs Saved belongs to Sports Info Solutions. All names and trademarks belong to their respective owners and are used here only to identify the source of the data.</p>
    <p>This page publishes only aggregate summary statistics (correlations and sample sizes) from our own analysis. It does not reproduce or redistribute any provider's data tables, player-level statistics or leaderboards. To view the underlying statistics, please visit the original sources linked above.</p>
    <p>Data accessed November 2026. Source figures may be revised by their providers. Results are provided as is, without warranty of accuracy, and are not betting, fantasy or financial advice.</p>
  </div>
</section>
</div>
"""
(ROOT / "results/xwar_page.html").write_text(html)
print("wrote", ROOT / "results/xwar_page.html", len(html), "chars")

# ---------------- README.md (same write-up, Markdown) ----------------
def md_horizon():
    H = {g: {e["N"]: e for e in o[g]["horizon"]} for g in ["hitters", "pitchers"]}
    rel = lambda e: "—" if e["reliability"] != e["reliability"] else f"{e['reliability']:.2f}"
    L = ["| N seasons | Base seasons | Hitter n | Hitter reliability | Pitcher n | Pitcher reliability |", "|---:|---|---:|---:|---:|---:|"]
    for N in range(1, 11):
        a, b = H["hitters"][N], H["pitchers"][N]
        bold = "**" if N == 5 else ""
        L.append(f"| {bold}{N}{bold} | {a['bases']} | {a['n']:,} | {rel(a)} | {b['n']:,} | {rel(b)} |")
    return "\n".join(L)


wmd = "\n".join(["| Position | FRV weight (Tango) | DRS weight | Our check, 2021–26 | Year-to-year pairs |", "|---|---:|---:|---:|---:|"] +
                [f"| {p} | {TANGO[p]:.2f} | {1 - TANGO[p]:.2f} | {ours.loc[p, 'FRV weight']:.2f} | {int(ours.loc[p, 'pairs'])} |" for p in ["C", "OF", "1B", "SS", "2B", "3B"]])
intro_md = {"aWAR": "aWAR is the fairest target, because it isn't built from any single site's WAR.",
            "bWAR": "This target favors bWAR, since it shares bWAR's own method.",
            "fWAR": "This target favors fWAR and both xWARs, which are built on fWAR."}
tables_md, k = [], 1
for t in ["aWAR", "bWAR", "fWAR"]:
    for g, gl in [("hitters", "Hitters"), ("pitchers", "Pitchers")]:
        tables_md.append(f"### Table {k}. {gl}: correlation with future {t}\n\n{intro_md[t]}\n\n{md_table(t, g)}")
        k += 1

readme = f"""# xWAR Correlation: does xWAR predict the future better than WAR?

**The xWAR idea comes from [Thomas Nestico (TJStats on X)](https://x.com/TJStats).** This repository is an independent rebuild from the published description and may differ from the original formula. Fielding weights come from [Tom Tango's research](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs). Full credits and a disclaimer are at the bottom.

xWAR rebuilds fWAR from the parts of a season a player controls most: expected batting (xwOBA), expected pitching (xFIP or xERA), and a blend of two fielding metrics. This project tests whether xWAR predicts a player's future WAR better than FanGraphs WAR (fWAR), Baseball-Reference WAR (bWAR), or their average (aWAR).

## The short answer

| | Result |
|---|---|
| **Pitchers** | **xWAR(xFIP) is the best predictor** at every horizon and on every target. Next-season aWAR: r = {pn['r']['xWAR_xFIP']:.3f} vs {pn['r']['fWAR']:.3f} for fWAR. The xERA version predicts worse than plain fWAR. |
| **Hitters** | **A tie.** xWAR and aWAR finish within noise of each other (next-season r = {hn['r']['xWAR_xFIP']:.3f} vs {hn['r']['aWAR']:.3f}). Both edge out fWAR and bWAR by about 0.01 to 0.02. |
| **Horizon** | **5 seasons.** The future average levels off by 5 seasons (reliability 0.89 hitters, 0.85 pitchers). Longer windows cost a base season per year and mostly measure aging. |

## The stats compared

| Stat | Definition |
|---|---|
| fWAR | FanGraphs Wins Above Replacement. |
| bWAR | Baseball-Reference Wins Above Replacement. |
| aWAR | The average of the two: (fWAR + bWAR) / 2. |
| xWAR(xFIP) | fWAR with batting runs adjusted from wOBA to Statcast xwOBA (park factor kept), fielding as a position-weighted blend of Statcast Fielding Run Value (FRV) and Defensive Runs Saved (DRS), and pitching runs from xFIP instead of FIP. |
| xWAR(xERA) | The same, with pitching runs from Statcast xERA instead of xFIP. For hitters the two xWARs are identical. |

## Results

Each value is the Pearson r between a stat in one season and the player's later WAR. The highest value in each row is bold. "Clear" means the leader's 95% interval over second place is above zero; "tie" means it isn't. For hitters the two xWARs are identical, so they share one column.

{chr(10).join(chr(10) + x + chr(10) for x in tables_md)}
† Only the 2016 season has 10 complete future seasons (2017 to 2026), so this row uses about 350 hitters and 385 pitchers. Treat it as a rough check.

## Why a 5-season horizon

Before seeing which stat won, we set a rule (see [PLAN.md](PLAN.md)): pick the shortest horizon where the future average stops getting more reliable (gain under 0.03 per added year) and the ranking of the stats stops changing. For pitchers the rule picked 5 seasons in 4 of 5 checks, and 6 in the other. For hitters it landed between 5 and 7, because the top hitter stats are tied and keep swapping places. Five seasons keeps the most data at nearly full reliability. Past that, aging (about 0.5 WAR lost per year after 30) and survivor bias drive the numbers more than the season being measured.

{md_horizon()}

Reliability is split-half (odd vs even future seasons), corrected to the full window. Each added season removes one base season from the sample.

## How xWAR was built

- **Batting:** FanGraphs batting runs plus (xwOBA − wOBA) / wOBA scale × PA, using Baseball Savant's xwOBA and wOBA, centered so each season's league total is unchanged. FanGraphs' park adjustment is kept. (We tested removing it: no gain over 1 to 5 years, and worse for the 10-year best season.)
- **Fielding:** FanGraphs fielding is based on FRV, so it is replaced with w × FRV + (1 − w) × DRS, with both centered within position and season. The weight w depends on position (below).
- **Pitching:** fWAR plus (FIP − xFIP) × IP / 9, or (FIP − xERA) × IP / 9, converted to wins with each pitcher's own FanGraphs runs-per-win ratio. Both are centered so each season's league average is unchanged.
- **League check:** league-wide xWAR stays within 1% of fWAR in every season.

### Fielding weights by position

From Tom Tango's ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) (September 2026). We reproduced his test on the same seasons ([src/defense_weights.py](src/defense_weights.py)) and got the same sample sizes and year-to-year correlations within 0.02. Our own fitted weights agree on direction: catchers and outfielders lean FRV, 2B and 3B lean DRS. Swapping these weights for a flat 50/50 changed no result by more than 0.003.

{wmd}

## Sample and method

- **Base seasons:** 2016 to 2025, the years Statcast FRV is available; future seasons run through 2026. Hitters with 200+ PA ({nh:,} player-seasons, {nhp:,} players); pitchers with 40+ IP ({np_:,} player-seasons, {npp:,} players).
- **Missing seasons:** a season with no MLB appearance counts as 0 WAR.
- **2020:** WAR in 2020 is scaled by 162/60.
- **Uncertainty:** 95% intervals come from 2,000 bootstrap resamples of players, since a player can appear in several base seasons.
- **Robustness:** the pitcher result holds with 100+ IP only, without the 2020 scaling, among players who played the next season, and on 2016–2019 base seasons only. The hitter tie holds in all of these too, with aWAR ahead in some and xWAR in others.
- **Limits:** WAR includes playing time, so these correlations partly measure who keeps getting at-bats or innings. aWAR averages two measurements of the same season, which by itself reduces noise.

## Data

All data was downloaded locally and is **not included in this repository**. Some of it is behind paywalls (FanGraphs membership exports), and every provider has its own rules on reuse and redistribution. The sources are FanGraphs (fWAR, FIP, xFIP, xERA, DRS, FRV), Baseball Savant (xwOBA, wOBA, xERA) and Baseball-Reference (bWAR), all for 2015 to 2026. To rerun the analysis, get the data from those sites under their terms and place it in a local `data/` folder.

## Code

| Path | Contents |
|---|---|
| `PLAN.md` | Test plan written before any results, plus later amendments |
| `src/build.py` | Builds the player-season table with fWAR, bWAR, aWAR, xWAR(xFIP) and xWAR(xERA) |
| `src/defense_weights.py` | Replicates Tango's FRV vs DRS test |
| `src/analyze.py` | Main tests (see PLAN.md). Sensitivity flags: `--pa 400 --ip 100`, `--no2020scale`, `--played-only`, `--bases 2016-2019` |
| `src/report.py`, `src/make_page.py` | Write the full tables and this README |

Requirements: Python 3.9+, pandas, numpy (`pip install -r requirements.txt`).

## Credits

- **xWAR concept:** [Thomas Nestico (TJStats on X)](https://x.com/TJStats).
- **Fielding-weight research:** Tom Tango, ["Comparing Statcast Fielding Run Value (FRV) to DRS"](https://tangotiger.com/index.php/site/comments/comparing-statcast-fielding-run-value-frv-to-drs) and ["FRV v DRS"](https://tangotiger.com/index.php/site/article/frv-v-drs), Tangotiger Blog. Tom Tango also created FIP and, with Mitchel Lichtman and Andrew Dolphin, wOBA (*The Book*).
- **fWAR, FIP, xFIP and DRS exports:** [FanGraphs](https://www.fangraphs.com). xFIP was developed by Dave Studeman of The Hardball Times.
- **bWAR:** [Baseball-Reference.com](https://www.baseball-reference.com) (Sports Reference LLC). Its WAR framework was originally provided by Sean Smith.
- **xwOBA, wOBA, xERA and Fielding Run Value:** MLB Statcast via [Baseball Savant](https://baseballsavant.mlb.com) (MLB Advanced Media).
- **Defensive Runs Saved (DRS):** [Sports Info Solutions](https://www.sportsinfosolutions.com), as published on FanGraphs.
- **ERA-estimator research:** Dan Richards, ["The Relative Value of FIP, xFIP, SIERA and xERA, Pt. II"](https://pitcherlist.com/the-relative-value-of-fip-xfip-siera-and-xera-pt-ii/), Pitcher List (2020).
- **Aging research:** Piper Slowinski, ["Aging Curve"](https://library.fangraphs.com/principles/aging-curve), FanGraphs Library.

## Disclaimer

**For educational and non-commercial purposes only.** This is an independent analysis. It is not affiliated with, sponsored by or endorsed by FanGraphs, Sports Reference LLC (Baseball-Reference.com), Major League Baseball, MLB Advanced Media, Baseball Savant, Sports Info Solutions, Pitcher List, Tom Tango or Thomas Nestico (TJStats).

fWAR is a statistic of FanGraphs. bWAR (Baseball-Reference WAR) is a statistic of Sports Reference LLC. Statcast metrics (xwOBA, xERA, Fielding Run Value) belong to MLB Advanced Media. Defensive Runs Saved belongs to Sports Info Solutions. All names and trademarks belong to their respective owners and are used here only to identify the source of the data.

This repository publishes only code and the aggregate summary statistics shown above (correlations and sample sizes) from our own analysis. It does not reproduce or redistribute any provider's data tables, player-level statistics or leaderboards. To view the underlying statistics, please visit the original sources linked above.

Data accessed November 2026. Source figures may be revised by their providers. Results are provided as is, without warranty of accuracy, and are not betting, fantasy or financial advice.
"""
(ROOT / "README.md").write_text(readme)
print("wrote", ROOT / "README.md")
