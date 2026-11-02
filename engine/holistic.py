"""Holistic layer: connects creative -> adset -> country -> App Store money.

Needs engine/model.py to have run (data/model/*.pkl), plus build.py, rootcause.py
and creative_relay.py outputs in output/data/.

Writes:
  ov_weekly.csv, ov_actions.csv, ov_facts.csv          Overview tab
  mk_country.csv, mk_share.csv, mk_us.csv, mk_dose.csv  Markets tab
  ct_relay.csv                                          country mix per grid row
  grid.csv (adds: top creative, reign week, US share, top country)

Run:  python3 engine/holistic.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
MODEL = os.path.join(ROOT, "data", "model")
OUT = os.path.join(ROOT, "output", "data")
from settings import PRE_END, SWITCH, BARS, era, bar  # noqa: E402
from codes import concept_names  # noqa: E402

PRE = ("2025-12-01", PRE_END)            # before the Singular switch (12 weeks, Meta's own attribution)
NOW_N = 10                               # last 10 full weeks = "now" (Singular)


def load():
    m = {k: pd.read_pickle(os.path.join(MODEL, f"{k}.pkl")) for k in
         ("adset_week", "adset_dim", "country_week", "ad_week", "apple_week", "meta")}
    return m


def adstock(x, dec=0.5):
    o = np.zeros(len(x))
    for i in range(len(x)):
        o[i] = x[i] + (dec * o[i - 1] if i else 0)
    return o


def main():
    m = load()
    fw = m["meta"].full_weeks.tolist()
    NOW = (fw[-NOW_N], fw[-1])
    dim = m["adset_dim"]
    judged = set(dim.index[dim.judged])
    cw = m["country_week"]
    cw = cw[cw.week.isin(fw) & cw.adset_id.isin(judged)].join(dim[["os", "persona", "lang", "version", "geo"]], on="adset_id")
    aw = m["ad_week"]
    aw = aw[aw.week.isin(fw) & aw.adset_id.isin(judged)]
    ap = m["apple_week"]
    ap = ap[ap.week.isin(fw)]
    asw = m["adset_week"]
    asw = asw[asw.adset_id.isin(judged)]

    def per(df, rng):
        return df[(df.week >= rng[0]) & (df.week <= rng[1])]

    n_pre, n_now = len([w for w in fw if PRE[0] <= w <= PRE[1]]), NOW_N

    # ================= Markets ===================================================
    ios = cw[cw.os == "iOS"]
    store_w = ap.groupby(["store", "week"]).proceeds.sum()
    rows = []
    for k, rng, n in (("pre", PRE, n_pre), ("now", NOW, n_now)):
        x = per(cw, rng)
        g = x.groupby(["country", "os"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).unstack("os").fillna(0)
        g.columns = [f"{a}_{b}_{k}" for a, b in g.columns]
        g = g / n
        rows.append(g)
    C = pd.concat(rows, axis=1).fillna(0)
    # Meta ROAS before and now are on different rulers, so each country is also shown as an
    # index against its own OS account in the same window (1.00 = average); that IS comparable
    acc_os = {}
    for k, rng in (("pre", PRE), ("now", NOW)):
        x = per(cw, rng)
        for o_ in ("iOS", "Android"):
            y = x[x.os == o_]
            acc_os[(k, o_)] = y.rev.sum() / y.spend.sum()
    for k in ("pre", "now"):
        C[f"spend_{k}"] = C.get(f"spend_iOS_{k}", 0) + C.get(f"spend_Android_{k}", 0)
        C[f"roas_ios_{k}"] = C[f"rev_iOS_{k}"] / C[f"spend_iOS_{k}"].replace(0, np.nan)
        C[f"roas_and_{k}"] = C[f"rev_Android_{k}"] / C[f"spend_Android_{k}"].replace(0, np.nan)
        C[f"share_{k}"] = C[f"spend_{k}"] / C[f"spend_{k}"].sum()
        C[f"idx_ios_{k}"] = C[f"roas_ios_{k}"] / acc_os[(k, "iOS")]
        C[f"idx_and_{k}"] = C[f"roas_and_{k}"] / acc_os[(k, "Android")]
    iso_store = cw.dropna(subset=["store"]).drop_duplicates("country").set_index("country")["store"]
    C["store"] = C.index.map(iso_store)
    apk = {k: per(ap, rng).groupby("store").proceeds.sum() / n for k, rng, n in (("pre", PRE, n_pre), ("now", NOW, n_now))}
    C["proceeds_pre"] = C.store.map(apk["pre"])
    C["proceeds_now"] = C.store.map(apk["now"])
    C["d_ios_spend"] = C["spend_iOS_now"] - C["spend_iOS_pre"]
    C["d_proceeds"] = C["proceeds_now"] - C["proceeds_pre"]
    # personas spending there now
    pn = per(cw, NOW).groupby(["country", "persona"]).spend.sum().reset_index().sort_values("spend", ascending=False)
    C["top_personas"] = pn.groupby("country").apply(lambda d: ", ".join(d.persona.head(3)), include_groups=False)
    C = C.sort_values("spend_now", ascending=False)
    C.index.name = "country"
    mk = C.head(30).reset_index()
    rest = C.iloc[30:]
    mk_cols = ["country", "store", "spend_pre", "spend_now", "share_pre", "share_now", "spend_iOS_pre", "spend_iOS_now",
               "roas_ios_pre", "roas_ios_now", "roas_and_pre", "roas_and_now", "idx_ios_pre", "idx_ios_now",
               "idx_and_pre", "idx_and_now", "proceeds_pre", "proceeds_now",
               "d_ios_spend", "d_proceeds", "top_personas"]
    mk = mk[mk_cols]
    mk.to_csv(os.path.join(OUT, "mk_country.csv"), index=False, float_format="%.4f")

    # dose-response across countries: change in weekly iOS spend vs change in weekly proceeds
    D = C.dropna(subset=["store"]).copy()
    D = D[(D.spend_iOS_pre + D.spend_iOS_now) > 200]
    D = D.groupby("store").agg(d_ios_spend=("d_ios_spend", "sum"), d_proceeds=("d_proceeds", "first"),
                               ios_pre=("spend_iOS_pre", "sum"), ios_now=("spend_iOS_now", "sum"),
                               proceeds_pre=("proceeds_pre", "first"), proceeds_now=("proceeds_now", "first"))
    W = np.sqrt(D.ios_pre + D.ios_now).values
    X = np.column_stack([np.ones(len(D)), D.d_ios_spend.values])
    b = np.linalg.lstsq(X * W[:, None], D.d_proceeds.values * W, rcond=None)[0]
    Dx = D.drop("United States", errors="ignore")
    Wx = np.sqrt(Dx.ios_pre + Dx.ios_now).values
    bx = np.linalg.lstsq(np.column_stack([np.ones(len(Dx)), Dx.d_ios_spend.values]) * Wx[:, None], Dx.d_proceeds.values * Wx, rcond=None)[0]
    D = D.reset_index().rename(columns={"store": "country"}).sort_values("ios_now", ascending=False)
    D.to_csv(os.path.join(OUT, "mk_dose.csv"), index=False, float_format="%.4f")

    # pooled two-way fixed-effects check (top 40 storefronts)
    sw = ios.dropna(subset=["store"]).groupby(["store", "week"]).spend.sum()
    top40 = sw.groupby("store").sum().sort_values(ascending=False).head(40).index
    Pn = ap[ap.store.isin(top40)].set_index(["store", "week"]).join(sw.rename("s")).fillna({"s": 0}).reset_index().sort_values(["store", "week"])
    Pn["A"] = Pn.groupby("store").s.transform(lambda x: pd.Series(adstock(x.values), index=x.index))
    Yp = Pn.pivot(index="week", columns="store", values="proceeds")
    Xp = Pn.pivot(index="week", columns="store", values="A")

    def dm(Z):
        return Z - Z.mean(axis=0) - Z.mean(axis=1).values[:, None] + Z.values.mean()
    y, xx = dm(Yp).values.ravel(), dm(Xp).values.ravel()
    k_fe = (xx * y).sum() / (xx * xx).sum() * 2

    # share of spend by country per week (top 8 now + other)
    tw = cw.groupby(["week", "country"]).spend.sum().reset_index()
    top8 = C.head(8).index.tolist()
    tw["country2"] = np.where(tw.country.isin(top8), tw.country, "Other")
    sh = tw.groupby(["week", "country2"]).spend.sum().reset_index().rename(columns={"country2": "country"})
    sh["share"] = sh.spend / sh.groupby("week").spend.transform("sum")
    sh["key"] = sh.week + "|" + sh.country
    sh.to_csv(os.path.join(OUT, "mk_share.csv"), index=False, float_format="%.4f")

    # US view
    en_ios = cw[(cw.lang == "EN") & (cw.os == "iOS")]
    us = pd.DataFrame({
        "us_ios_spend": cw[(cw.country == "US") & (cw.os == "iOS")].groupby("week").spend.sum(),
        "us_only_adset_spend": cw[(cw.country == "US") & cw.geo.isin(["US"])].groupby("week").spend.sum(),
        "us_share_en_ios": en_ios[en_ios.country == "US"].groupby("week").spend.sum() / en_ios.groupby("week").spend.sum(),
        "us_proceeds": ap[ap.store == "United States"].set_index("week").proceeds,
        "us_meta_ios_rev": cw[(cw.country == "US") & (cw.os == "iOS")].groupby("week").rev.sum(),
    }).reindex(fw).fillna({"us_ios_spend": 0, "us_only_adset_spend": 0, "us_meta_ios_rev": 0})
    us.index.name = "week"
    us = us.reset_index()
    us.to_csv(os.path.join(OUT, "mk_us.csv"), index=False, float_format="%.4f")

    # ================= Overview =================================================
    acc = asw[asw.week.isin(fw)].groupby("week").agg(spend=("spend", "sum"), rev=("rev", "sum"))
    os_sp = cw.groupby(["week", "os"]).agg(s=("spend", "sum"), r=("rev", "sum")).unstack("os").fillna(0)
    ov = pd.DataFrame({
        "spend": acc.spend, "meta_rev": acc.rev, "meta_roas": acc.rev / acc.spend,
        "ios_spend": os_sp[("s", "iOS")], "android_spend": os_sp[("s", "Android")],
        "meta_ios_rev": os_sp[("r", "iOS")],
        "store_proceeds": ap.groupby("week").proceeds.sum(),
        "us_share": cw[cw.country == "US"].groupby("week").spend.sum() / cw.groupby("week").spend.sum(),
    }).reindex(fw)
    grid_prev = pd.read_csv(os.path.join(OUT, "account.csv")).set_index("week")
    ov["green_share"] = grid_prev["green_share"].reindex(fw)
    ov["critical_adsets"] = grid_prev["critical_adsets"].reindex(fw)
    ov["store_per_ios_dollar"] = ov.store_proceeds / ov.ios_spend
    ov["roas_ios"] = os_sp[("r", "iOS")] / os_sp[("s", "iOS")]
    ov["roas_android"] = os_sp[("r", "Android")] / os_sp[("s", "Android")]
    chw = pd.read_csv(os.path.join(OUT, "ch_weekly.csv")).set_index("week")
    ov["tt_spend"] = (chw.tt_ios_spend + chw.tt_and_spend).reindex(ov.index)
    ov["tt_rev"] = (chw.tt_ios_rev + chw.tt_and_rev).reindex(ov.index)
    ov["paid_spend"] = ov.spend + ov.tt_spend.fillna(0)
    ov["era"] = [era(w) for w in ov.index]
    ov["bar_green"] = [bar(w)["green"] for w in ov.index]
    ov.index.name = "week"
    ov = ov.reset_index()
    ov["is_latest"] = ov.week == fw[-1]
    ov.to_csv(os.path.join(OUT, "ov_weekly.csv"), index=False, float_format="%.4f")

    # ================= country mix per grid row (dossier) =========================
    parts = []
    cw2 = cw.copy()
    cw2["key_a"] = "a:" + cw2.adset_id.astype(str)
    cw2["key_p"] = "p:" + cw2.persona.astype(str)
    cw2["key_pl"] = "pl:" + cw2.persona.astype(str) + "|" + cw2.lang.astype(str)
    for kcol in ("key_a", "key_p", "key_pl"):
        e = cw2.groupby([kcol, "week", "country"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index().rename(columns={kcol: "ekey"})
        top5 = e.groupby(["ekey", "country"]).spend.sum().reset_index().sort_values("spend", ascending=False).groupby("ekey").head(5)
        keep = set(zip(top5.ekey, top5.country))
        e["code"] = [cc if (ek, cc) in keep else "Other" for ek, cc in zip(e.ekey, e.country)]
        parts.append(e.groupby(["ekey", "week", "code"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index())
    ct = pd.concat(parts, ignore_index=True)
    ct["share"] = ct.spend / ct.groupby(["ekey", "week"]).spend.transform("sum")
    ct["roas"] = ct.rev / ct.spend.replace(0, np.nan)
    ct = ct[ct.spend >= 1]
    ct["key"] = ct.ekey + "|" + ct.week + "|" + ct.code
    ct[["key", "ekey", "week", "code", "spend", "share", "roas"]].to_csv(os.path.join(OUT, "ct_relay.csv"), index=False, float_format="%.4f")

    # ================= enrich the grid ==========================================
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str})
    lw = fw[-1]
    c = aw.groupby(["adset_id", "week", "concept_key"]).spend.sum().reset_index()
    c["share"] = c.spend / c.groupby(["adset_id", "week"]).spend.transform("sum")
    c = c.sort_values(["adset_id", "week", "spend"], ascending=[True, True, False])
    top = c.drop_duplicates(["adset_id", "week"]).sort_values(["adset_id", "week"])
    top["prev"] = top.groupby("adset_id").concept_key.shift()
    top["pweek"] = top.groupby("adset_id").week.shift()
    top["cont"] = (top.concept_key == top.prev) & ((pd.to_datetime(top.week) - pd.to_datetime(top.pweek)).dt.days == 7)
    run = (~top.cont).cumsum()
    top["reign_week"] = top.groupby(run).cumcount() + 1
    tl = top[top.week == lw].set_index("adset_id")
    cname = m["ad_week"].join(pd.read_pickle(os.path.join(MODEL, "ad_dim.pkl"))[["conceptname"]], on="ad_id") \
        .groupby("concept_key").conceptname.agg(lambda s: s.mode().iat[0] if len(s.mode()) else "")
    cname = cname.to_dict()
    cname.update(concept_names())
    cl = cw[cw.week == lw].groupby(["adset_id", "country"]).spend.sum().reset_index()
    cl["sh"] = cl.spend / cl.groupby("adset_id").spend.transform("sum")
    us_sh = cl[cl.country == "US"].set_index("adset_id").sh
    topc = cl.sort_values("spend", ascending=False).drop_duplicates("adset_id").set_index("adset_id")
    ids = G.adset_id.where(G.level == "adset")
    G["top_creative"] = ids.map(tl.concept_key).str.replace("^name:", "", regex=True)
    G["top_creative_name"] = G["top_creative"].map(lambda k: cname.get(k, "") if isinstance(k, str) else "")
    G["top_creative_share"] = ids.map(tl.share)
    G["reign_week"] = ids.map(tl.reign_week)
    G["us_share"] = ids.map(us_sh).where(ids.map(topc.sh).notna())
    G.loc[ids.notna() & ids.map(topc.sh).notna() & G.us_share.isna(), "us_share"] = 0.0
    G["top_country"] = ids.map(topc.country)
    G["top_country_share"] = ids.map(topc.sh)
    G["mix_week"] = lw
    # aggregate rows: US share + top country
    for lvl, kcol in (("persona", "persona"), ("perslang", None)):
        x = cw[cw.week == lw].copy()
        x["k"] = ("p:" + x.persona) if lvl == "persona" else ("pl:" + x.persona + "|" + x.lang)
        t = x.groupby(["k", "country"]).spend.sum().reset_index()
        t["sh"] = t.spend / t.groupby("k").spend.transform("sum")
        u = t[t.country == "US"].set_index("k").sh
        tc = t.sort_values("spend", ascending=False).drop_duplicates("k").set_index("k")
        mask = G.level == lvl
        G.loc[mask, "us_share"] = G.loc[mask, "key"].map(u)
        G.loc[mask & G.key.map(tc.sh).notna() & G.us_share.isna(), "us_share"] = 0.0
        G.loc[mask, "top_country"] = G.loc[mask, "key"].map(tc.country)
        G.loc[mask, "top_country_share"] = G.loc[mask, "key"].map(tc.sh)
    # decay clock flag: winner in week 3+ of its reign on a live adset
    G["decay_due"] = (G.level == "adset") & G.active.astype(str).isin(["True", "true"]) & (G.reign_week >= 3)
    G.to_csv(os.path.join(OUT, "grid.csv"), index=False, float_format="%.4f")

    # ================= Actions ==================================================
    us_pre = us[(us.week >= PRE[0]) & (us.week <= PRE[1])]
    us_now = us[us.week >= NOW[0]]
    us_loss_wk = us_pre.us_proceeds.mean() - us_now.us_proceeds.mean()
    us_spend_cut = us_pre.us_ios_spend.mean() - us_now.us_ios_spend.mean()
    A = G[(G.level == "adset")].copy()
    A["alert_b"] = A.alert.astype(str).isin(["True", "true"])
    crit = A[A.alert_b].copy()
    crit_leak = pd.to_numeric(crit.leaking, errors="coerce").sum()
    due = A[A.decay_due & ~A.alert_b & (pd.to_numeric(A.spend_last, errors="coerce") >= 1000)]
    due_spend = pd.to_numeric(due.spend_last, errors="coerce").sum()
    dark = G[(G.level == "persona") & ~G.active.astype(str).isin(["True", "true"]) & G.judged.astype(str).isin(["True", "true"])]
    # era facts (engine/eras.py runs before this step)
    ef = pd.read_csv(os.path.join(OUT, "era_facts.csv")).set_index("fact")
    ev = ef["value"]
    cuts = pd.read_csv(os.path.join(OUT, "era_cuts.csv"))
    strong_cuts = cuts[cuts.rel_last4 >= 1.0]
    gb = BARS["singular"]
    cf = pd.read_csv(os.path.join(OUT, "ch_facts.csv")).set_index("fact")
    cv, cl = cf["value"], cf["label"]
    acts = [
        dict(rank=1, lever="Budget × country", owner="Media buyer",
             action="Keep rebuilding the US and make it a clean test: a US-only iOS adset at about the old budget for 3–4 weeks, then compare US App Store proceeds with today's baseline",
             evidence=(f"Before vs now, US iOS spend fell by ${us_spend_cut:,.0f}/week and US App Store proceeds by ${us_loss_wk:,.0f}/week. "
                       f"It's coming back: Meta US iOS spend went from ${cv['us_meta_ios_jun']:,.0f} (June) to ${cv['us_meta_ios_sep']:,.0f}/week (September) through worldwide English adsets, "
                       f"and US proceeds from ${cv['us_store_jun']:,.0f} to ${cv['us_store_sep']:,.0f}/week. Singular credits US traffic "
                       f"{ev['us_vs_rest_ww_singular']:.2f}× the rest of the world (was {ev['us_vs_rest_ww_pre']:.2f}×), so Meta under-reads it"),
             at_stake=us_loss_wk, where="Markets"),
        dict(rank=2, lever="Channel", owner="Media buyer + management",
             action=(f"Hold TikTok at today's budget and run a geo test before scaling it: pause TikTok iOS in 3–4 countries where it is a big share "
                     f"(e.g. Philippines, Indonesia) for 4 weeks and compare App Store proceeds with similar countries"),
             evidence=(f"TikTok reports iOS ROAS {cv['tt_ios_roas_sing_reported']:.2f} and Android {cv['tt_and_roas_sing_reported']:.2f}; "
                       f"{cv['tt_ghost_share_and']:.0%} of its Android value and {cv['tt_ghost_share_ios']:.0%} of iOS value sits on ad groups that weren't spending "
                       f"(most likely renewals of users acquired earlier). On live ad groups: {cv['tt_ios_roas_sing']:.2f} / {cv['tt_and_roas_sing']:.2f}. App Store money follows Meta iOS spend "
                       f"(${cv['store_per_meta_ios']:.2f} per $) but barely TikTok's (${cv['store_per_tt_ios']:.2f} ± {cv['store_per_tt_ios_se']:.2f})"),
             at_stake=cv["tt_spend_wk_now"], where="Channels"),
        dict(rank=3, lever="Measurement", owner="Creative lead + management",
             action=(f"Bar set by the creative lead (27 Oct): acceptable from {gb['green']:.2f}, refresh warning under {gb['green']:.2f}, critical under {gb['amber']:.2f}. "
                     f"Never compare Meta ROAS across March: {gb['green']:.2f} today equals {gb['green'] / ev['ruler_ratio']:.2f} on Meta's old reporting"),
             evidence=(f"Singular credits Meta {ev['ruler_ratio_iOS']:.2f}× (iOS) and {ev['ruler_ratio_Android']:.2f}× (Android) of what Meta's own attribution did, so 0.40 today is stricter than the old 0.50 in real money; "
                       f"App Store proceeds per iOS $ held at ${k_fe:.2f}. On the old bar only {ev['green_old_bar_singular']:.0%} of Singular-era spend is green "
                       f"(was {ev['green_old_bar_pre']:.0%}); on {gb['green']:.2f} it is {ev['green_new_bar_singular']:.0%}"),
             at_stake=np.nan, where="Diagnosis"),
        dict(rank=4, lever="Creative", owner="Strategists + designers",
             action=f"Refresh the {len(crit)} flagged adsets (critical or amber and falling on the {gb['green']:.2f} / {gb['amber']:.2f} bar), biggest leak first",
             evidence=f"Flagged at meaningful spend last week; ${crit_leak:,.0f} leaking against the {gb['green']:.2f} bar",
             at_stake=crit_leak, where="Grid"),
        dict(rank=5, lever="Creative", owner="Strategists",
             action=f"Brief the next creative for {len(due)} healthy adsets whose #1 is in week 3+ of its reign (the ticket queue opens them from week 2)",
             evidence=f"ROAS starts sliding in week 3 of a reign (holds in the Singular era alone); a refresh takes about a week to make and a week to read; ${due_spend:,.0f} of last week's spend sits on those adsets",
             at_stake=np.nan, where="Grid"),
        dict(rank=6, lever="Persona", owner="Creative lead + media buyer",
             action=(f"Review the {len(strong_cuts)} adsets switched off since the switch while at or above their OS average, "
                     f"and decide on the {len(dark)} dark personas: relaunch or write the obituary"),
             evidence=("Cut while beating their OS: " + ", ".join(
                 (strong_cuts.persona.astype(str) + " " + strong_cuts.os.astype(str)).drop_duplicates().head(5).tolist())
                 + f" (peak ${strong_cuts.peak_wk.sum():,.0f}/wk combined). Biggest dark personas: "
                 + ", ".join(dark.sort_values("peak_all", ascending=False).short.head(3).tolist())),
             at_stake=np.nan, where="Diagnosis"),
        dict(rank=7, lever="Data", owner="Media buyer",
             action=("Add Google Play earnings by country, and a Singular export by campaign × country × week (cost, installs, revenue D7 / D30, both OS). "
                      "Ask Singular why renewals are posted to TikTok ad groups that stopped spending in 2024–25"),
             evidence=("Android is about 40% of spend and its real money can't be checked yet; Singular's own revenue lets us check what it sends Meta and TikTok. "
                       f"{cv['tt_ghost_never_spent']:.0f} TikTok ad groups with no spend since December were credited ${cv['tt_ghost_never_value']:,.0f} since March. "
                       "Add campaign name and ID to the Meta exports so the two can be joined"),
             at_stake=np.nan, where="Data checks"),
    ]
    pd.DataFrame(acts).to_csv(os.path.join(OUT, "ov_actions.csv"), index=False, float_format="%.2f")

    facts = [
        ("dose_slope", b[1], "Change in weekly App Store proceeds per $1 change in weekly iOS spend, across countries (before vs now)"),
        ("dose_slope_ex_us", bx[1], "Same, excluding the US"),
        ("dose_baseline", b[0], "Proceeds growth per country per week with no change in spend"),
        ("k_fe", k_fe, "App Store proceeds per iOS $ (top 40 storefronts, country + week fixed effects, 50% weekly carry-over)"),
        ("us_share_pre", ov[(ov.week >= PRE[0]) & (ov.week <= PRE[1])].pipe(lambda d: (d.us_share * d.spend).sum() / d.spend.sum()), "US share of purchase-adset spend, before"),
        ("us_share_now", ov[ov.week >= NOW[0]].pipe(lambda d: (d.us_share * d.spend).sum() / d.spend.sum()), "US share of purchase-adset spend, last 10 weeks"),
        ("us_en_ios_pre", en_ios[(en_ios.week >= PRE[0]) & (en_ios.week <= PRE[1]) & (en_ios.country == "US")].spend.sum() / en_ios[(en_ios.week >= PRE[0]) & (en_ios.week <= PRE[1])].spend.sum(), "US share of English iOS spend, before"),
        ("us_en_ios_now", en_ios[(en_ios.week >= NOW[0]) & (en_ios.country == "US")].spend.sum() / en_ios[en_ios.week >= NOW[0]].spend.sum(), "US share of English iOS spend, last 10 weeks"),
        ("us_ios_spend_pre", us_pre.us_ios_spend.mean(), "US iOS spend per week, before"),
        ("us_ios_spend_now", us_now.us_ios_spend.mean(), "US iOS spend per week, last 10 weeks"),
        ("us_proceeds_pre", us_pre.us_proceeds.mean(), "US App Store proceeds per week, before"),
        ("us_proceeds_now", us_now.us_proceeds.mean(), "US App Store proceeds per week, last 10 weeks"),
        ("spend_wk_pre", per(ov, PRE).spend.mean(), "Purchase-adset spend per week, before"),
        ("spend_wk_now", per(ov, NOW).spend.mean(), "Purchase-adset spend per week, last 10 weeks"),
        ("store_wk_pre", per(ov, PRE).store_proceeds.mean(), "App Store proceeds per week, before"),
        ("store_wk_now", per(ov, NOW).store_proceeds.mean(), "App Store proceeds per week, last 10 weeks"),
        ("meta_roas_pre", per(ov, PRE).meta_rev.sum() / per(ov, PRE).spend.sum(), "Meta ROAS (7-day click), before: Meta's own attribution"),
        ("meta_roas_now", per(ov, NOW).meta_rev.sum() / per(ov, NOW).spend.sum(), "Meta ROAS (7-day click), last 10 weeks: Singular"),
        ("countries_spent", cw[cw.week >= NOW[0]].country.nunique(), "Countries with spend, last 10 weeks"),
        ("tt_spend_wk_pre", cv["tt_spend_wk_pre"], "TikTok spend per week, before"),
        ("tt_spend_wk_now", cv["tt_spend_wk_now"], "TikTok spend per week, last 10 weeks"),
        ("pre_label", np.nan, f"{PRE[0]} to {PRE[1]} (weeks starting)"),
        ("now_label", np.nan, f"{NOW[0]} to {NOW[1]} (weeks starting)"),
    ]
    # the break, by country × OS: 2–22 Feb vs 9–29 Mar
    br = []
    for (cc, o), g in cw.groupby(["country", "os"]):
        bb = g[(g.week >= "2026-02-02") & (g.week <= "2026-02-16")]
        aa = g[(g.week >= "2026-03-09") & (g.week <= "2026-03-23")]
        if bb.spend.sum() >= 3000 and aa.spend.sum() >= 3000:
            br.append(aa.rev.sum() / aa.spend.sum() / (bb.rev.sum() / bb.spend.sum()) - 1)
    br = np.array(br)
    facts += [("break_cells", len(br), "Country × OS combinations with $3k+ spend in both windows"),
              ("break_cells_fell", (br < 0).mean(), "Share of those where Meta ROAS fell, 2–22 Feb vs 9–29 Mar"),
              ("break_median", np.median(br), "Median change in Meta ROAS across those combinations")]
    # extra data checks
    chk = pd.read_csv(os.path.join(OUT, "checks.csv"))
    chk = chk[~chk.check.isin(["No App Store storefront", "Concept code collision", "Measurement switch",
                               "TikTok value without spend", "TikTok Android purchases missing", "TikTok countries"])]
    unm = cw[cw.store.isna()]
    extra = [dict(check="No App Store storefront", finding="Spend in countries with no App Store storefront (iOS money can't come back there)",
                  count=int(unm.country.nunique()), spend=round(unm.spend.sum(), 2), detail=", ".join(unm.groupby("country").spend.sum().sort_values(ascending=False).head(6).index))]
    keys = pd.Series(m["ad_week"].concept_key.unique())
    keys = keys[~keys.str.startswith("name:")]
    low = keys.str.lower()
    coll = keys[low.duplicated(keep=False)].sort_values()
    if len(coll):
        extra.append(dict(check="Concept code collision", finding="Codes that differ only by letter case",
                          count=int(len(coll)), spend=round(m["ad_week"][m["ad_week"].concept_key.isin(coll)].spend.sum(), 2),
                          detail=", ".join(coll.tolist()[:12])))
    eo = pd.read_csv(os.path.join(OUT, "era_os.csv")).set_index("key")
    extra.append(dict(check="Measurement switch",
                      finding=(f"Meta numbers come through Singular from {SWITCH['iOS']} (iOS) and {SWITCH['Android']} (Android). "
                               "Absolute ROAS, purchases, installs, IPM and click → install are not comparable across the switch"),
                      count=0, spend=0.0,
                      detail=(f"Meta ROAS ×{eo.loc['iOS|Meta ROAS', 'ratio']:.2f} iOS, ×{eo.loc['Android|Meta ROAS', 'ratio']:.2f} Android; "
                              f"iOS click-through {eo.loc['iOS|Click-through rate', 'step']:+.0%} and click → install "
                              f"{eo.loc['iOS|Click → install', 'step']:+.0%} in the switch weeks (iOS click path changed too)")))
    extra.append(dict(check="TikTok value without spend",
                      finding="TikTok is credited with purchase value on ad groups that didn't spend that week (most likely renewals of users acquired earlier); excluded when judging TikTok",
                      count=int(cv["tt_ghost_adgroups"]), spend=0.0,
                      detail=(f"{cv['tt_ghost_share_and']:.0%} of Android and {cv['tt_ghost_share_ios']:.0%} of iOS value since 16 Mar; "
                              f"{cv['tt_ghost_never_spent']:.0f} ad groups with no spend since Dec got ${cv['tt_ghost_never_value']:,.0f}")))
    if cv["tt_android_gap_weeks"] > 0:
        extra.append(dict(check="TikTok Android purchases missing",
                          finding="Weeks right after the TikTok MMP migration with Android spend but almost no purchases reported",
                          count=int(cv["tt_android_gap_weeks"]), spend=0.0,
                          detail=f"weeks of {cl['tt_android_gap_from']} to {cl['tt_android_gap_to']}; TikTok Android ROAS for those weeks is not usable"))
    tt_raw = pd.read_pickle(os.path.join(MODEL, "tt_week.pkl"))
    nost = tt_raw[tt_raw.store.isna() & (tt_raw.spend > 0)]
    extra.append(dict(check="TikTok countries", finding="TikTok spend in countries with no App Store storefront or no country",
                      count=int(nost.country_name.nunique()), spend=round(nost.spend.sum(), 2),
                      detail=", ".join(nost.groupby("country_name").spend.sum().sort_values(ascending=False).head(5).index)))
    chk = pd.concat([chk, pd.DataFrame(extra)], ignore_index=True)
    chk["id"] = [f"i{i:02d}" for i in range(len(chk))]
    chk.to_csv(os.path.join(OUT, "checks.csv"), index=False, float_format="%.4f")
    F = pd.DataFrame(facts, columns=["fact", "value", "label"])
    F.to_csv(os.path.join(OUT, "ov_facts.csv"), index=False, float_format="%.4f")
    print(F.to_string())
    print(pd.DataFrame(acts)[["rank", "action", "evidence", "at_stake"]].to_string())
    print(mk[["country", "spend_now", "share_pre", "share_now", "roas_ios_pre", "roas_ios_now", "proceeds_pre", "proceeds_now", "d_ios_spend", "d_proceeds"]].head(15).round(2).to_string())
    for f in ("ct_relay.csv", "mk_share.csv", "grid.csv"):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")


if __name__ == "__main__":
    main()
