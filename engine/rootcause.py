"""Root-cause analysis of the Feb–Mar 2026 ROAS break.

Reads the adset export, the monthly ad exports and the Apple proceeds file, and
writes the rc_*.csv datasets the dashboard's "Why ROAS fell" tab reads.

Run:  python3 engine/rootcause.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build import load_raw, parse_name, JUDGED_OBJECTIVES  # noqa: E402
from adload import load_ads  # noqa: E402
from adparse import parse_ad  # noqa: E402
from apple import load_apple  # noqa: E402
from settings import SWITCH  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "output", "data")
PRE_END = "2026-02-22"      # last week (Mon) before the break window
BREAK = (SWITCH["iOS"], "2026-03-09")   # the Singular switch weeks (iOS 23 Feb, Android 9 Mar), shaded in charts
POST_START = "2026-03-01"   # used for the proceeds-per-dollar test (weeks from 2 Mar)


def wk(s: pd.Series) -> pd.Series:
    """Daily series -> Mon-Sun weekly sums keyed by Monday."""
    key = (s.index - pd.to_timedelta(s.index.weekday, unit="D")).strftime("%Y-%m-%d")
    return s.groupby(key).sum()


def adstock(x, dec):
    o = np.zeros_like(x, dtype=float)
    for i in range(len(x)):
        o[i] = x[i] + (dec * o[i - 1] if i else 0)
    return o


def main():
    os.makedirs(OUT, exist_ok=True)
    # ---------------- adset weekly (Mon-Sun) --------------------------------------
    df = load_raw()
    P = df["name"].map(parse_name).apply(pd.Series)
    df = pd.concat([df, P], axis=1)
    j = df[df["objective"].isin(JUDGED_OBJECTIVES) & (df["spend"] > 0)].copy()
    ap = load_apple()
    apple_w = wk(ap.sum(axis=1))
    us_w = wk(ap["United States"])
    weeks = sorted(j["week"].unique())
    weeks = [w for w in weeks if w in apple_w.index]

    rows = []
    us_targeted = j["name"].str.contains(r"US-ENG|US-ES", regex=True) | (j["geo"] == "US")
    for w in weeks:
        g = j[j["week"] == w]
        r = {"week": w}
        for o, lab in [("iOS", "ios"), ("Android", "and")]:
            x = g[g["os"] == o]
            s, rv, im = x["spend"].sum(), x["rev"].sum(), x["impressions"].sum()
            r[f"{lab}_spend"] = s
            r[f"{lab}_rev"] = rv
            r[f"{lab}_roas"] = rv / s if s else np.nan
            r[f"{lab}_ppm"] = x["purchases"].sum() * 1e6 / im if im else np.nan
            r[f"{lab}_cpm"] = s * 1000 / im if im else np.nan
            r[f"{lab}_ctr"] = x["clicks"].sum() / im if im else np.nan
            r[f"{lab}_c2i"] = x["installs"].sum() / x["clicks"].sum() if x["clicks"].sum() else np.nan
        r["apple_proceeds"] = apple_w.get(w, np.nan)
        r["us_proceeds"] = us_w.get(w, np.nan)
        r["us_targeted_spend"] = g.loc[us_targeted.loc[g.index], "spend"].sum()
        r["in_break"] = BREAK[0] <= w <= BREAK[1]
        rows.append(r)
    W = pd.DataFrame(rows)
    W["ios_meta_share"] = W["ios_rev"] / W["apple_proceeds"]
    W.to_csv(os.path.join(OUT, "rc_weekly.csv"), index=False, float_format="%.4f")

    # ---------------- proceeds per iOS dollar, before vs after ------------------
    y = W["apple_proceeds"].values.astype(float)
    s = W["ios_spend"].values.astype(float)
    a = W["and_spend"].values.astype(float)
    tt = np.arange(len(y))
    post = (W["week"] >= POST_START).astype(float).values
    variants = []
    for dec in (0.0, 0.3, 0.5, 0.7):
        for trend in (True, False):
            A = adstock(s, dec)
            cols = [np.ones_like(y)] + ([tt] if trend else []) + [A, A * post, post]
            X = np.column_stack(cols)
            b = np.linalg.lstsq(X, y, rcond=None)[0]
            k = 1 + int(trend)
            mult = 1 / (1 - dec)
            variants.append(dict(decay=dec, trend=trend, pre=b[k] * mult, post=(b[k] + b[k + 1]) * mult))
    V = pd.DataFrame(variants)
    V["post_vs_pre"] = V["post"] / V["pre"] - 1
    main_v = V[(V.decay == 0.5) & (V.trend)].iloc[0]
    Xp = np.column_stack([np.ones_like(y), tt, adstock(s, 0.5), adstock(a, 0.5)])
    bp = np.linalg.lstsq(Xp, y, rcond=None)[0]

    pre_w = W[W["week"] <= PRE_END]
    post_w = W[W["week"] >= "2026-03-02"]
    us_pre = W[(W["week"] >= "2026-01-05") & (W["week"] <= "2026-02-22")]
    us_now = W[W["week"] >= "2026-08-03"]
    us_low = W[(W["week"] >= "2026-05-11") & (W["week"] <= "2026-08-24")]

    # ---------------- ad level: cohorts, creative index, arrivals ---------------
    d = load_ads()
    Pa = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d["ad_name"].unique()])
    d = d.merge(Pa, on="ad_name", how="left")
    A2 = pd.DataFrame([dict(adset_name=n, **parse_name(n)) for n in d["adset_name"].unique()])
    A2 = A2.rename(columns={c: "as_" + c for c in A2.columns if c != "adset_name"})
    d = d.merge(A2, on="adset_name", how="left")
    d = d[d["as_objective"].isin(JUDGED_OBJECTIVES) & (d["spend"] > 0)].copy()
    d["month"] = d["start"].dt.strftime("%Y-%m")
    d["concept_key"] = np.where(d["concept"] != "", d["concept"], "name:" + d["ad_clean"])
    first_m = d.groupby("concept_key")["start"].transform("min").dt.strftime("%Y-%m")

    def cohort(m):
        if m <= "2025-12":
            return "Running before Dec"
        if m <= "2026-02":
            return "Launched Jan–Feb"
        if m <= "2026-05":
            return "Launched Mar–May"
        return "Launched Jun–Oct"

    d["cohort"] = first_m.map(cohort)
    C = d.groupby(["cohort", "month"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index()
    C["roas"] = C["rev"] / C["spend"]
    C = C[C["spend"] >= 5000]
    C["key"] = C["cohort"] + "|" + C["month"]
    C.to_csv(os.path.join(OUT, "rc_cohort.csv"), index=False, float_format="%.4f")
    pre_cohort = C[(C.cohort == "Running before Dec")].set_index("month")["roas"]

    # within adset-period index
    d["period"] = d["start"].dt.strftime("%Y-%m-%d")
    g = d.groupby(["adset_id", "period"]).agg(as_s=("spend", "sum"), as_r=("rev", "sum"))
    d = d.join(g, on=["adset_id", "period"])
    d["exp_rev"] = d["spend"] * d["as_r"] / d["as_s"]
    d["cname"] = d["conceptname"].fillna("").str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    ctx = d[d["as_s"] >= 500]

    # arrivals of a concept into an adset (full 7-day buckets)
    f7 = d[(d["end"] - d["start"]).dt.days == 6].copy()
    per = sorted(f7["period"].unique())
    f7["pi"] = f7["period"].map({p: i for i, p in enumerate(per)})
    fa = f7.groupby(["adset_id", "concept_key"])["pi"].min().rename("fpi").reset_index()
    f7 = f7.merge(fa, on=["adset_id", "concept_key"])
    acct_first = f7.groupby("concept_key")["pi"].min()
    arr = f7[(f7.pi >= f7.fpi) & (f7.pi <= f7.fpi + 1)].groupby(["adset_id", "concept_key"]).agg(
        s=("spend", "sum"), as_s=("as_s", "sum"), cname=("cname", "first"), fpi=("fpi", "first")).reset_index()
    arr = arr[arr["as_s"] >= 1000]
    arr["delivered"] = arr["s"] / arr["as_s"] >= 0.20
    arr["new_to_account"] = arr["fpi"] == arr["concept_key"].map(acct_first)

    fam = ctx.groupby("cname").agg(spend=("spend", "sum"), rev=("rev", "sum"), exp=("exp_rev", "sum"),
                                   ads=("ad_id", "nunique")).reset_index()
    fam = fam[(fam["spend"] >= 30000) & (fam["cname"] != "")]
    fam["roas"] = fam["rev"] / fam["spend"]
    fam["index"] = fam["rev"] / fam["exp"]
    fam["gap"] = fam["rev"] - fam["exp"]
    dl = arr.groupby("cname").agg(arrivals=("delivered", "size"), delivered=("delivered", "mean"))
    fam = fam.merge(dl, left_on="cname", right_index=True, how="left")
    fam = fam.sort_values("index", ascending=False)
    fam.to_csv(os.path.join(OUT, "rc_creative.csv"), index=False, float_format="%.4f")

    # refresh event study (adset relative ROAS 2 periods before vs 2 after)
    # compared with the same OS in the same period (the two OS switched to Singular on different weeks)
    accp = f7.groupby(["pi", "as_os"]).agg(s=("spend", "sum"), r=("rev", "sum"))
    accp["ar"] = accp.r / accp.s
    accp = accp["ar"].to_dict()
    AS = f7.groupby(["adset_id", "pi"]).agg(s=("spend", "sum"), r=("rev", "sum"), os=("as_os", "first")).reset_index()
    f7["bkey"] = np.where(f7["batch"] != "", f7["batch"], "nb:" + f7["concept_key"])
    fb = f7.groupby(["adset_id", "bkey"])["pi"].min().rename("bpi").reset_index()
    f7 = f7.merge(fb, on=["adset_id", "bkey"])
    nw = f7[f7.pi == f7.bpi].groupby(["adset_id", "pi"])["spend"].sum().rename("new_s").reset_index()
    AS = AS.merge(nw, on=["adset_id", "pi"], how="left").fillna({"new_s": 0})
    AS["new_share"] = AS["new_s"] / AS["s"]
    Ai = AS.set_index(["adset_id", "pi"])
    ev = []
    for (aid, p), r in Ai.iterrows():
        try:
            b_ = [Ai.loc[(aid, p - k)] for k in (1, 2)]
            f_ = [Ai.loc[(aid, p + k)] for k in (1, 2)]
        except KeyError:
            continue
        if min(x.s for x in b_) < 300 or r.s < 300:
            continue
        o_ = r.os
        try:
            pre = sum(x.r for x in b_) / sum(x.s for x in b_) / np.mean([accp[(p - 1, o_)], accp[(p - 2, o_)]])
            pst = sum(x.r for x in f_) / sum(x.s for x in f_) / np.mean([accp[(p + 1, o_)], accp[(p + 2, o_)]])
        except KeyError:
            continue
        if pre <= 0 or pst <= 0:
            continue
        ev.append(dict(new_share=r.new_share, dl=np.log(pst / pre),
                       ds=np.log(np.mean([x.s for x in f_]) / np.mean([x.s for x in b_]))))
    E = pd.DataFrame(ev)
    E["type"] = pd.cut(E.new_share, [-0.01, 0.0001, 0.2, 1.01],
                       labels=["No new creative", "New creative, under 20% of spend", "New creative won 20%+ of spend"])
    R = E.groupby("type", observed=True).agg(events=("dl", "size"),
                                             rel_roas_change=("dl", lambda s: np.expm1(s.median())),
                                             share_improved=("dl", lambda s: (s > 0).mean()),
                                             spend_change=("ds", lambda s: np.expm1(s.median()))).reset_index()
    R.to_csv(os.path.join(OUT, "rc_refresh.csv"), index=False, float_format="%.4f")

    # ---------------- spend level test (adset weekly) ----------------------------
    acc = j.groupby(["week", "os"]).agg(s=("spend", "sum"), r=("rev", "sum"))
    acc["ar"] = acc.r / acc.s
    j = j.join(acc["ar"], on=["week", "os"])
    j["rel"] = (j["rev"] / j["spend"]) / j["ar"]
    j = j.sort_values(["adset_id", "week"])
    for c in ["spend", "rel", "week"]:
        j["p_" + c] = j.groupby("adset_id")[c].shift()
    x = j[(j.p_spend >= 300) & (j.spend >= 300) & (j.rel > 0) & (j.p_rel > 0)
          & (pd.to_datetime(j.week) - pd.to_datetime(j.p_week) == pd.Timedelta(days=7))].copy()
    x["dls"] = np.log(x.spend / x.p_spend)
    x["lp"] = np.log(x.p_rel)
    x["drel"] = np.log(x.rel / x.p_rel)
    Wt = np.sqrt(x.spend.values)
    X = np.column_stack([np.ones(len(x)), x.dls, x.lp])
    b = np.linalg.lstsq(X * Wt[:, None], x.drel.values * Wt, rcond=None)[0]
    bands = [("Cut more than 40%", -9, -0.51), ("Cut 5–40%", -0.51, -0.05), ("Roughly flat", -0.05, 0.05),
             ("Raised 5–22%", 0.05, 0.2), ("Raised 22–65%", 0.2, 0.5), ("Raised more than 65%", 0.5, 9)]
    S = []
    for lab, lo, hi in bands:
        sx = x[(x.dls > lo) & (x.dls <= hi)]
        S.append(dict(change=lab, adset_weeks=len(sx), raw=np.expm1(sx.drel.median()),
                      adjusted=np.expm1(b[1] * sx.dls.median())))
    S = pd.DataFrame(S)
    S.to_csv(os.path.join(OUT, "rc_spend.csv"), index=False, float_format="%.4f")
    react = x[x.p_rel >= 1.2].dls.median()

    # ---------------- country table ------------------------------------------
    before = ap.loc["2025-12-01":"2026-02-22"].mean()
    now = ap.loc["2026-08-01":"2026-10-18"].mean()
    T = pd.DataFrame({"before": before, "now": now})
    T["change"] = T["now"] / T["before"] - 1
    T["delta"] = T["now"] - T["before"]
    top = T.sort_values("now", ascending=False).head(15)
    rest = T.drop(top.index).sum()
    rest["change"] = rest["now"] / rest["before"] - 1
    top.loc["All other countries"] = rest
    top.loc["Total"] = T[["before", "now", "delta"]].sum()
    top.loc["Total", "change"] = top.loc["Total", "now"] / top.loc["Total", "before"] - 1
    top = top.reset_index().rename(columns={"index": "country"})
    top.to_csv(os.path.join(OUT, "rc_country.csv"), index=False, float_format="%.4f")

    # ---------------- headline facts --------------------------------------------
    def roas(frame, lab):
        return frame[f"{lab}_rev"].sum() / frame[f"{lab}_spend"].sum()

    F = [
        ("meta_ios_roas_pre", roas(pre_w, "ios"), "Meta iOS ROAS, weeks of 1 Dec – 16 Feb"),
        ("meta_ios_roas_post", roas(post_w, "ios"), "Meta iOS ROAS, weeks from 2 Mar"),
        ("meta_and_roas_pre", roas(pre_w, "and"), "Meta Android ROAS, weeks of 1 Dec – 16 Feb"),
        ("meta_and_roas_post", roas(post_w, "and"), "Meta Android ROAS, weeks from 2 Mar"),
        ("proceeds_per_dollar_pre", main_v.pre, "App Store proceeds per iOS ad dollar before (weekly model, 0.5 carry-over, trend)"),
        ("proceeds_per_dollar_post", main_v.post, "App Store proceeds per iOS ad dollar after"),
        ("proceeds_ratio_min", 1 + V.post_vs_pre.min(), "Lowest after/before ratio across 8 model variants"),
        ("proceeds_ratio_max", 1 + V.post_vs_pre.max(), "Highest after/before ratio across 8 model variants"),
        ("meta_ratio", roas(post_w, "ios") / roas(pre_w, "ios"), "Meta iOS ROAS after / before"),
        ("android_placebo", bp[3] * 2, "App Store proceeds per Android ad dollar (should be ~0)"),
        ("apple_day_pre", ap.loc["2025-12-01":"2026-02-22"].sum(axis=1).mean(), "App Store proceeds per day, 1 Dec – 22 Feb"),
        ("apple_day_now", ap.loc["2026-08-01":"2026-10-18"].sum(axis=1).mean(), "App Store proceeds per day, 1 Aug – 18 Oct"),
        ("ios_ppm_pre", j[(j.os == "iOS") & (j.week <= PRE_END)].purchases.sum() * 1e6 / j[(j.os == "iOS") & (j.week <= PRE_END)].impressions.sum(), "iOS purchases per million impressions before"),
        ("ios_ppm_post", j[(j.os == "iOS") & (j.week >= "2026-03-16") & (j.week <= "2026-04-26")].purchases.sum() * 1e6 / j[(j.os == "iOS") & (j.week >= "2026-03-16") & (j.week <= "2026-04-26")].impressions.sum(), "iOS purchases per million impressions, 16 Mar – 26 Apr"),
        ("and_ppm_pre", j[(j.os == "Android") & (j.week <= PRE_END)].purchases.sum() * 1e6 / j[(j.os == "Android") & (j.week <= PRE_END)].impressions.sum(), "Android purchases per million impressions before"),
        ("and_ppm_post", j[(j.os == "Android") & (j.week >= "2026-03-16") & (j.week <= "2026-04-26")].purchases.sum() * 1e6 / j[(j.os == "Android") & (j.week >= "2026-03-16") & (j.week <= "2026-04-26")].impressions.sum(), "Android purchases per million impressions, 16 Mar – 26 Apr"),
        ("cohort_old_feb", pre_cohort.get("2026-02", np.nan), "ROAS of creatives running before Dec, February"),
        ("cohort_old_mar", pre_cohort.get("2026-03", np.nan), "ROAS of creatives running before Dec, March"),
        ("us_week_pre", us_pre.us_proceeds.mean(), "US App Store proceeds per week, 5 Jan – 22 Feb"),
        ("us_week_low", us_low.us_proceeds.mean(), "US App Store proceeds per week, 11 May – 30 Aug"),
        ("us_week_now", us_now.us_proceeds.mean(), "US App Store proceeds per week, from 3 Aug"),
        ("us_spend_pre", us_pre.us_targeted_spend.mean(), "US-only adset spend per week, 5 Jan – 22 Feb"),
        ("us_spend_now", us_now.us_targeted_spend.mean(), "US-only adset spend per week, from 3 Aug"),
        ("us_adset_roas_decjan", None, ""),
        ("spend_elasticity", b[1], "Change in relative ROAS per 1.0 log change in adset spend, after removing last week's luck"),
        ("mean_reversion", -b[2], "Share of last week's above/below-average result that disappears the next week"),
        ("buyer_raise_after_good_week", np.expm1(react), "Median budget change after a week 20%+ above account ROAS"),
        ("arrivals", len(arr), "Concept arrivals into adsets (adset spend ≥ $1k in first 2 weeks)"),
        ("delivered_share_proven", arr[~arr.new_to_account].delivered.mean(), "Share of proven concepts that won 20%+ of adset spend in their first 2 weeks"),
        ("delivered_share_new", arr[arr.new_to_account].delivered.mean(), "Share of brand-new concepts that won 20%+ of adset spend"),
    ]
    usr = j[j["name"] == "Ad Set / US-ENG / iOS / Purchase"]
    dj = usr[usr.week <= "2026-01-25"]
    ma = usr[(usr.week >= "2026-02-23") & (usr.week <= "2026-04-26")]
    F = [f for f in F if f[0] != "us_adset_roas_decjan"]
    F += [("us_adset_roas_decjan", dj.rev.sum() / dj.spend.sum(), "US-only iOS adset ROAS, Dec – Jan"),
          ("us_adset_roas_marapr", ma.rev.sum() / ma.spend.sum(), "US-only iOS adset ROAS, 23 Feb – 26 Apr"),
          ("us_adset_rpp", usr.rev.sum() / usr.purchases.sum(), "US-only iOS adset revenue per purchase"),
          ("ios_rpp_pre", pre_w.ios_rev.sum() / j[(j.os == "iOS") & (j.week <= PRE_END)].purchases.sum(), "iOS revenue per purchase before"),
          ("ios_rpp_now", post_w[post_w.week >= "2026-06-01"].ios_rev.sum() / j[(j.os == "iOS") & (j.week >= "2026-06-01")].purchases.sum(), "iOS revenue per purchase from June")]
    Fd = pd.DataFrame(F, columns=["fact", "value", "label"])
    Fd.to_csv(os.path.join(OUT, "rc_facts.csv"), index=False, float_format="%.4f")
    print(Fd.to_string())
    print(V.round(3).to_string())
    print(S.round(3).to_string())
    print(R.round(3).to_string())


if __name__ == "__main__":
    main()
