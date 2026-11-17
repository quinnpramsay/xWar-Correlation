"""Build one row per player-season (2015-2026) with fWAR, bWAR, aWAR, xWAR(xFIP) and xWAR(xERA).

xWAR is fWAR with three swaps (see PLAN.md):
  batting  : FanGraphs batting runs + (xwOBA - wOBA, season-centered) / wOBA scale * PA. FanGraphs' park
             adjustment is kept (tested without it: no gain, and worse at the 10-year horizon)
  fielding : FanGraphs fielding (FRV) replaced by w*FRV + (1-w)*DRS, w by position from Tango (2026-09-28):
             C .93, LF/CF/RF .92, 1B .67, SS .60, 2B .40, 3B .40. Both metrics centered within position-season.
  pitching : (FIP - xFIP) * IP/9  [xWAR(xFIP)]   or   (FIP - xERA_centered) * IP/9  [xWAR(xERA)]
Earlier variants (park-kept batting delta, 50/50 fielding, our own fitted weights) are kept for comparison.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, FG, OUT = ROOT / "data/raw", ROOT / "data/fangraphs", ROOT / "data/processed"
OUT.mkdir(parents=True, exist_ok=True)
YEARS = range(2015, 2027)


def fg(name):
    return pd.read_csv(FG / name, encoding="utf-8-sig")


def ip_dec(s):
    """FanGraphs innings 6.2 = 6 2/3."""
    s = s.fillna(0)
    return np.floor(s) + (s - np.floor(s)) * 10 / 3


# ---------- season constants ----------
bref_p = pd.read_csv(RAW / "war_daily_pitch.txt", na_values="NULL")
bref_b = pd.read_csv(RAW / "war_daily_bat.txt", na_values="NULL")
bat = fg("fg_bat_value.csv")
const = []
for y in YEARS:
    q = bref_p[bref_p.year_ID == y]
    rpw = 9 * q.RA.sum() / (q.IPouts.sum() / 3) * 1.5 + 3
    bb = bat[(bat.Season == y) & (bat.PA >= (120 if y == 2020 else 300))]
    scale = 1 / np.polyfit(bb.wOBA, (bb.Off - bb.BsR) / bb.PA, 1)[0]
    const.append({"Season": y, "rpw": rpw, "woba_scale": scale})
const = pd.DataFrame(const)

# ---------- batting delta ----------
sav_b = pd.concat([pd.read_csv(RAW / f"savant_x_batter_{y}.csv", encoding="utf-8-sig") for y in YEARS])
sav_b = sav_b.rename(columns={"player_id": "MLBAMID", "year": "Season"})[["MLBAMID", "Season", "pa", "woba", "est_woba"]]
sav_b["dx"] = sav_b.est_woba - sav_b.woba
lg = sav_b.groupby("Season").apply(lambda g: np.average(g.dx, weights=g.pa)).rename("dx_lg")
sav_b = sav_b.join(lg, on="Season")
sav_b["dx_c"] = sav_b.dx - sav_b.dx_lg
b = bat[["Season", "PlayerId", "MLBAMID", "Name", "PA", "WAR"]].rename(columns={"WAR": "fWAR_bat"})
b = b.merge(sav_b[["MLBAMID", "Season", "dx_c"]], on=["MLBAMID", "Season"], how="left").merge(const, on="Season")
b["dBat_runs"] = b.dx_c.fillna(0) / b.woba_scale * b.PA  # v1: keeps FanGraphs park adjustment
sav_x = sav_b[["MLBAMID", "Season", "est_woba", "pa"]]
b = b.merge(sav_x, on=["MLBAMID", "Season"], how="left").merge(bat[["MLBAMID", "Season", "Off", "BsR"]], on=["MLBAMID", "Season"])
pit_ip = fg("fg_pit_dash.csv").assign(ipd=lambda x: ip_dec(x.IP))[["MLBAMID", "Season", "ipd"]]
b = b.merge(pit_ip, on=["MLBAMID", "Season"], how="left")
b["pitcher"] = (b.ipd.fillna(0) >= 10) & (b.PA < 100)
np_ = b[~b.pitcher & b.est_woba.notna()]
lgx = np_.groupby("Season").apply(lambda g: np.average(g.est_woba, weights=g.PA)).rename("lg_xwoba")
b = b.join(lgx, on="Season")
b["xBat_runs"] = (b.est_woba - b.lg_xwoba) / b.woba_scale * b.PA
b["fgBat_runs"] = b.Off - b.BsR
b["dBatNP_runs"] = np.where(b.est_woba.notna(), b.xBat_runs - b.fgBat_runs, 0.0)

# ---------- fielding delta ----------
fld = fg("fg_fld.csv")
fld = fld[fld.Pos != "P"].copy()
both = fld.FRV.notna() & fld.DRS.notna()
fld["dFld_runs"] = np.where(both, (fld.DRS - fld.FRV) / 2, 0.0)  # v1: 50/50, uncentered
fld["inn"] = ip_dec(fld.Inn)
for m in ["FRV", "DRS"]:
    rate = fld[both].groupby(["Season", "Pos"]).apply(lambda g: g[m].sum() / g.inn.sum()).rename(m + "_lgrate")
    fld = fld.join(rate, on=["Season", "Pos"])
    fld[m + "_c"] = fld[m] - fld[m + "_lgrate"] * fld.inn
TANGO_W = {"C": .93, "LF": .92, "CF": .92, "RF": .92, "1B": .67, "SS": .60, "2B": .40, "3B": .40}
OURS_W = {"C": .61, "LF": .86, "CF": .86, "RF": .86, "1B": .43, "SS": .51, "2B": .59, "3B": .39}  # src/defense_weights.py, 2016-2026
for tag, W in [("tango", TANGO_W), ("ours", OURS_W), ("c5050", {k: .5 for k in TANGO_W})]:
    fld["dFld_" + tag] = np.where(both, (1 - fld.Pos.map(W)) * (fld.DRS_c - fld.FRV_c), 0.0)
fld_tot = fld.groupby(["MLBAMID", "Season"], as_index=False).agg(
    dFld_runs=("dFld_runs", "sum"), dFld_tango=("dFld_tango", "sum"), dFld_ours=("dFld_ours", "sum"),
    dFld_c5050=("dFld_c5050", "sum"), FRV=("FRV", "sum"), DRS=("DRS", "sum"))
b = b.merge(fld_tot, on=["MLBAMID", "Season"], how="left")
FLD = ["dFld_runs", "dFld_tango", "dFld_ours", "dFld_c5050"]
b[FLD] = b[FLD].fillna(0)
b.loc[b.Season < 2016, FLD] = 0.0  # no FRV in 2015
b["dBat_war"] = b.dBat_runs / b.rpw
b["dBatNP_war"] = b.dBatNP_runs / b.rpw
for c in FLD:
    b[c.replace("_runs", "") + "_war"] = b[c] / b.rpw
b["dFld_war"] = b.dFld_runs / b.rpw

# ---------- pitching deltas ----------
pd_ = fg("fg_pit_dash.csv")
pv = fg("fg_pit_value.csv")[["PlayerId", "Season", "RAR", "WAR"]].rename(columns={"WAR": "WAR_v"})
p = pd_[["Season", "PlayerId", "MLBAMID", "Name", "IP", "FIP", "xFIP", "xERA", "WAR"]].rename(columns={"WAR": "fWAR_pit"})
p = p.merge(pv, on=["PlayerId", "Season"], how="left").merge(const, on="Season")
p["ipd"] = ip_dec(p.IP)
ratio = p.RAR / p.WAR_v
p["rpw_i"] = np.where((p.WAR_v.abs() >= 0.5) & ratio.between(7, 13), ratio, p.rpw)
ok = p.ipd >= 10  # tiny samples get no adjustment
for col in ["FIP", "xFIP", "xERA"]:
    lgm = p[ok].groupby("Season").apply(lambda g: np.average(g[col].fillna(g.FIP), weights=g.ipd)).rename(col + "_lg")
    p = p.join(lgm, on="Season")
p["xFIP_c"] = p.xFIP - p.xFIP_lg + p.FIP_lg
p["xERA_c"] = p.xERA.fillna(p.FIP) - p.xERA_lg + p.FIP_lg
p["dPit1_war"] = np.where(ok, (p.FIP - p.xFIP_c) * p.ipd / 9 / p.rpw_i, 0.0)
p["dPit2_war"] = np.where(ok, (p.FIP - p.xERA_c) * p.ipd / 9 / p.rpw_i, 0.0)

# ---------- bWAR ----------
bb = bref_b.groupby(["mlb_ID", "year_ID"], as_index=False).agg(bWAR_bat=("WAR", "sum"), age_b=("age", "first"))
bp = bref_p.groupby(["mlb_ID", "year_ID"], as_index=False).agg(bWAR_pit=("WAR", "sum"), age_p=("age", "first"))
bref = bb.merge(bp, on=["mlb_ID", "year_ID"], how="outer").rename(columns={"mlb_ID": "MLBAMID", "year_ID": "Season"})
bref = bref[bref.Season.isin(YEARS)]
bref["age"] = bref.age_b.fillna(bref.age_p)

# ---------- combine ----------
keys = ["MLBAMID", "Season"]
cols_b = ["MLBAMID", "Season", "Name", "PA", "fWAR_bat", "dBat_war", "dBatNP_war", "dFld_war", "dFld_tango_war", "dFld_ours_war", "dFld_c5050_war", "FRV", "DRS"]
cols_p = ["MLBAMID", "Season", "Name", "ipd", "fWAR_pit", "dPit1_war", "dPit2_war", "FIP", "xFIP", "xERA"]
ps = b[cols_b].merge(p[cols_p], on=keys, how="outer", suffixes=("", "_p"))
ps["Name"] = ps.Name.fillna(ps.Name_p)
ps = ps.drop(columns="Name_p").merge(bref[keys + ["bWAR_bat", "bWAR_pit", "age"]], on=keys, how="left")
num = ["PA", "ipd", "fWAR_bat", "fWAR_pit", "dBat_war", "dBatNP_war", "dFld_war", "dFld_tango_war", "dFld_ours_war", "dFld_c5050_war", "dPit1_war", "dPit2_war", "bWAR_bat", "bWAR_pit"]
ps[num] = ps[num].fillna(0)
ps = ps.rename(columns={"ipd": "IP"})
ps["fWAR"] = ps.fWAR_bat + ps.fWAR_pit
ps["bWAR"] = ps.bWAR_bat + ps.bWAR_pit
ps["aWAR"] = (ps.fWAR + ps.bWAR) / 2
base = ps.fWAR + ps.dBat_war + ps.dFld_tango_war  # park factor kept (user decision 2026-11-17)
ps["xWAR_xFIP"] = base + ps.dPit1_war
ps["xWAR_xERA"] = base + ps.dPit2_war
# comparison variants (hitters; pitching piece = xFIP)
ps["v1_parkkept_5050"] = ps.fWAR + ps.dBat_war + ps.dFld_war + ps.dPit1_war       # previous build
ps["v_nopark_5050"] = ps.fWAR + ps.dBatNP_war + ps.dFld_c5050_war + ps.dPit1_war
ps["v_nopark_ours"] = ps.fWAR + ps.dBatNP_war + ps.dFld_ours_war + ps.dPit1_war
ps["v_nopark_tango"] = ps.fWAR + ps.dBatNP_war + ps.dFld_tango_war + ps.dPit1_war
ps.to_csv(OUT / "player_seasons.csv", index=False)
const.to_csv(OUT / "season_constants.csv", index=False)

# ---------- checks ----------
print(const.round(3).to_string(index=False))
print(f"\n{len(ps):,} player-seasons, {ps.MLBAMID.nunique():,} players, bWAR missing: {ps.age.isna().mean():.1%}")
lgsum = ps.groupby("Season")[["fWAR", "bWAR", "xWAR_xFIP", "xWAR_xERA"]].sum().round(0)
print("\nLeague WAR totals (xWAR should stay close to fWAR):\n", lgsum.to_string())
h = ps[(ps.PA >= 200) & (ps.Season >= 2016)]
pt = ps[(ps.IP >= 40) & (ps.Season >= 2016)]
print("\nHitters PA>=200: corr", h[["fWAR", "bWAR", "aWAR", "xWAR_xFIP"]].corr().round(2).to_string())
print("\nPitchers IP>=40: corr", pt[["fWAR", "bWAR", "aWAR", "xWAR_xFIP", "xWAR_xERA"]].corr().round(2).to_string())
print("\nSD of deltas (wins), hitters: bat(no park) %.2f bat(park kept) %.2f fld(Tango) %.2f fld(50/50) %.2f | pitchers: xFIP %.2f xERA %.2f" % (
    h.dBatNP_war.std(), h.dBat_war.std(), h.dFld_tango_war.std(), h.dFld_war.std(), pt.dPit1_war.std(), pt.dPit2_war.std()))
