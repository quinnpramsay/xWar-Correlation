"""Write results/REPORT_tables.md from results_main.json and the sensitivity runs."""
import json
from pathlib import Path
R = Path(__file__).resolve().parents[1] / "results"
o = json.load(open(R / "results_main.json"))
name = {"xWAR_orig": "xWAR original", "xWAR_upd": "xWAR updated", "fWAR": "fWAR", "bWAR": "bWAR", "aWAR": "aWAR"}
L = []
def table(title, rows, group):
    stats = ["xWAR_orig", "xWAR_upd", "fWAR", "bWAR", "aWAR"]
    hdr = [name[s] for s in stats]
    L.append(f"\n**{title}**\n\n| Target | n | " + " | ".join(hdr) + " | Leader's edge over 2nd [95% CI] |\n|" + "---|" * (len(stats) + 3))
    for e in rows:
        if not e: continue
        cells = [(f"**{e['r'][s]:.3f}**" if s == e["best"] else f"{e['r'][s]:.3f}") for s in stats]
        L.append(f"| {e['target']} | {e['n']} | " + " | ".join(cells) + f" | {e['gap']:+.3f} [{e['gap_ci'][0]:+.3f}, {e['gap_ci'][1]:+.3f}] |")
for g in ["hitters", "pitchers"]:
    G = o[g]
    L.append(f"\n## {g.title()} ({G['n_rows']:,} base seasons, {G['n_players']:,} players)")
    table("Next season (Pearson r)", G["next"], g)
    table("Best single season over next K years", G["max"], g)
    table("Mean aWAR over next N years (horizon scan)", G["horizon"], g)
    L.append("\n| N | Base seasons | Target reliability |\n|---|---|---|")
    for e in G["horizon"]:
        L.append(f"| {e['N']} | {e['bases']} | {e['reliability'] if e['reliability']==e['reliability'] else '—'} |")
    table(f"Mean over next {G['N_chosen']} years (rule: {G['N_rule']})", G["meanN"], g)
L.append("\n## Sensitivities: N chosen by the pre-registered rule\n\n| Run | Hitters N | Pitchers N |\n|---|---|---|")
for t in ["main", "strict", "no2020", "played", "fixed1619"]:
    x = json.load(open(R / f"results_{t}.json"))
    L.append(f"| {t} | {x['hitters']['N_chosen']} | {x['pitchers']['N_chosen']} |")
(R / "REPORT_tables.md").write_text("\n".join(L) + "\n")
print("wrote", R / "REPORT_tables.md")
