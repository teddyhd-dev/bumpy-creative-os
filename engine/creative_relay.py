"""Creative layer: who is each adset's top spender, week by week, and what that does.

Reads the monthly ad exports (prorated into Mon-Sun weeks), and writes the
cr_*.csv datasets for the dashboard's Creatives tab and the grid's concept relay.

Run:  python3 engine/creative_relay.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build import parse_name, JUDGED_OBJECTIVES  # noqa: E402
from adload import load_ads  # noqa: E402
from adparse import parse_ad  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "output", "data")
ADD = ["spend", "rev", "impressions", "installs", "clicks", "purchases", "hook_x_imp"]
MIN_ADSET_WEEK = 500


def _weekly_rows():
    """Ad rows parsed and prorated into Mon-Sun weeks (judged objectives only)."""
    d = load_ads()
    Pa = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d["ad_name"].unique()])
    d = d.merge(Pa, on="ad_name", how="left")
    A = pd.DataFrame([dict(adset_name=n, **parse_name(n)) for n in d["adset_name"].unique()])
    A = A.rename(columns={c: "as_" + c for c in A.columns if c != "adset_name"})
    d = d.merge(A, on="adset_name", how="left")
    d["concept_key"] = np.where(d["concept"] != "", d["concept"], "name:" + d["ad_clean"])
    # confirmed code fixes (typos, letter case) from core/code_aliases.csv: one concept, one key
    al = os.path.join(os.path.dirname(HERE), "core", "code_aliases.csv")
    if os.path.exists(al):
        A_ = pd.read_csv(al)
        A_ = A_[A_.status.astype(str).str.lower() == "confirmed"]
        if len(A_):
            d["concept_key"] = d["concept_key"].replace(dict(zip(A_.alias, A_.code)))
    d = d[d["as_objective"].isin(JUDGED_OBJECTIVES)]
    # prorate each export bucket evenly over its days, then sum into Mon-Sun weeks
    d = d.copy()
    d["days"] = (d["end"] - d["start"]).dt.days + 1
    rep = d.loc[d.index.repeat(d["days"])].copy()
    rep["off"] = rep.groupby(level=0).cumcount()
    rep["day"] = rep["start"] + pd.to_timedelta(rep["off"], unit="D")
    for c in ADD:
        rep[c] = rep[c].fillna(0) / rep["days"]
    rep["week"] = (rep["day"] - pd.to_timedelta(rep["day"].dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")
    last_day = d["end"].max()
    full_weeks = rep.groupby("week")["day"].max()
    keep = full_weeks[full_weeks - pd.to_datetime(full_weeks.index) >= pd.Timedelta(days=6)].index
    rep = rep[rep["week"].isin(keep)]
    return d, rep, last_day


def load_variants():
    """adset × week × concept × full ad name (cleaned of '- Copy' and file extensions) → spend."""
    d, rep, _ = _weekly_rows()
    return rep.groupby(["adset_id", "week", "concept_key", "ad_clean"]).agg(spend=("spend", "sum")).reset_index()


def load():
    d, rep, last_day = _weekly_rows()
    c = rep.groupby(["adset_id", "week", "concept_key"]).agg(
        spend=("spend", "sum"), rev=("rev", "sum"), imp=("impressions", "sum"), ins=("installs", "sum"),
        clk=("clicks", "sum"), pur=("purchases", "sum"), hx=("hook_x_imp", "sum")).reset_index()
    attrs = d.groupby("concept_key").agg(cname=("conceptname", lambda s: s.mode().iat[0] if len(s.mode()) else ""),
                                         first_acct=("start", "min")).reset_index()
    hooks = d.groupby(["concept_key", "hook"])["spend"].sum().reset_index().sort_values("spend", ascending=False) \
        .drop_duplicates("concept_key").set_index("concept_key")["hook"]
    attrs["top_hook"] = attrs["concept_key"].map(hooks).fillna("")
    meta = d.drop_duplicates("adset_id").set_index("adset_id")[["as_persona", "as_lang", "as_os"]]
    return c, attrs, meta, last_day


def main():
    os.makedirs(OUT, exist_ok=True)
    c, attrs, meta, last_day = load()
    c = c.merge(attrs[["concept_key", "cname"]], on="concept_key", how="left")
    # "the account" = the same OS in the same week: iOS and Android switched to Singular on
    # different weeks, and each OS has its own level, so adsets are compared within their OS
    c["os"] = c.adset_id.map(meta.as_os).fillna("Other")
    acc = c.groupby(["week", "os"]).agg(s=("spend", "sum"), r=("rev", "sum"))
    acc["ar"] = acc.r / acc.s
    A = c.groupby(["adset_id", "week"]).agg(as_s=("spend", "sum"), as_r=("rev", "sum"),
                                             Ai=("ins", "sum"), Aimp=("imp", "sum"), Ac=("clk", "sum"),
                                             Ap=("pur", "sum"), Ahx=("hx", "sum")).reset_index()
    A["as_roas"] = A.as_r / A.as_s
    A["os"] = A.adset_id.map(meta.as_os).fillna("Other")
    A = A.join(acc["ar"].rename("acc_roas"), on=["week", "os"])
    A["rel"] = A.as_roas / A.acc_roas
    c = c.merge(A.drop(columns=["os"]), on=["adset_id", "week"])
    c["share"] = c.spend / c.as_s
    c["roas"] = c.rev / c.spend.replace(0, np.nan)
    c["rank"] = c.groupby(["adset_id", "week"]).spend.rank(ascending=False, method="first")
    fin = c[c.spend > 0].groupby(["adset_id", "concept_key"]).week.min().rename("first_in_adset")
    c = c.join(fin, on=["adset_id", "concept_key"])
    c["weeks_in_adset"] = (pd.to_datetime(c.week) - pd.to_datetime(c.first_in_adset)).dt.days // 7

    top = c[c["rank"] == 1][["adset_id", "week", "concept_key", "share", "roas", "spend"]].rename(
        columns={"concept_key": "top", "share": "top_share", "roas": "top_roas", "spend": "top_spend"})
    A = A.merge(top, on=["adset_id", "week"], how="left").sort_values(["adset_id", "week"]).reset_index(drop=True)
    g = A.groupby("adset_id")
    A["prev_top"] = g.top.shift()
    A["prev_week"] = g.week.shift()
    A["consec"] = (pd.to_datetime(A.week) - pd.to_datetime(A.prev_week)) == pd.Timedelta(days=7)
    run = (~(A.consec & (A.top == A.prev_top))).cumsum()
    A["run_id"] = run
    A["tenure"] = A.groupby(run).cumcount() + 1
    A["run_len"] = A.groupby("run_id").tenure.transform("max")
    B = A[A.as_s >= MIN_ADSET_WEEK].copy()

    # ---- facts ---------------------------------------------------------------
    runs = B.groupby("run_id").agg(weeks=("tenure", "max"), s=("as_s", "sum"))
    runs = runs[runs.s >= 2000]
    facts = [
        ("top_share_median", B.top_share.median(), "Median share of an adset's weekly spend taken by its #1 concept"),
        ("reign_median", runs.weeks.median(), "Median weeks a concept stays an adset's #1"),
        ("reign_mean", runs.weeks.mean(), "Mean weeks a concept stays an adset's #1"),
        ("reign_6plus", (runs.weeks >= 6).mean(), "Share of reigns lasting 6+ weeks"),
        ("reigns", len(runs), "Reigns counted (adset spend ≥ $2k over the reign)"),
    ]

    # ---- reign trajectory (runs of 4+ weeks) -----------------------------------
    L = B[B.run_len >= 4].copy()
    f = L[L.tenure == 1].set_index("run_id")
    L["rel_vs_start"] = L.rel / L.run_id.map(f.rel)
    L["top_vs_start"] = (L.top_roas / L.acc_roas) / L.run_id.map(f.top_roas / f.acc_roas)
    L["share_vs_start"] = L.top_share / L.run_id.map(f.top_share)
    L["spend_vs_start"] = L.as_s / L.run_id.map(f.as_s)
    reign = L[L.tenure <= 10].groupby("tenure").agg(
        runs=("run_id", "nunique"), adset_roas=("rel_vs_start", "median"), top_roas=("top_vs_start", "median"),
        top_share=("share_vs_start", "median"), adset_spend=("spend_vs_start", "median")).reset_index()
    reign.to_csv(os.path.join(OUT, "cr_reign.csv"), index=False, float_format="%.4f")

    # ---- concentration -----------------------------------------------------------
    X = B[(B.top_share < 0.95) & (B.as_s - B.top_spend >= 150)].copy()
    X["band"] = pd.cut(X.top_share, [0, .35, .5, .7, .95], labels=["Under 35%", "35–50%", "50–70%", "70–95%"])
    conc = X.groupby("band", observed=True).apply(lambda x: pd.Series({
        "adset_weeks": len(x),
        "adset_roas_vs_acct": x.as_r.sum() / (x.as_s * x.acc_roas).sum(),
        "top_vs_rest": ((x.top_roas * x.top_spend).sum() / x.top_spend.sum()) /
                       ((x.as_r - x.top_roas * x.top_spend).sum() / (x.as_s - x.top_spend).sum())})).reset_index()
    conc.to_csv(os.path.join(OUT, "cr_concentration.csv"), index=False, float_format="%.4f")
    facts.append(("top_vs_rest", ((X.top_roas * X.top_spend).sum() / X.top_spend.sum()) /
                  ((X.as_r - X.top_roas * X.top_spend).sum() / (X.as_s - X.top_spend).sum()),
                  "ROAS of the #1 concept vs the rest of its adset, same week (spend-weighted)"))

    # ---- takeovers --------------------------------------------------------------
    T = A.copy()
    gg = T.groupby("adset_id")
    for k in (1, 2):
        for col in ("rel", "as_s", "week"):
            T[f"{col}_m{k}"] = gg[col].shift(k)
            T[f"{col}_p{k}"] = gg[col].shift(-k)
    T = T.dropna(subset=["rel_m1", "rel_m2", "rel_p1", "rel_p2"])
    T = T[(pd.to_datetime(T.week_p2) - pd.to_datetime(T.week_m2)).dt.days == 28]
    T = T[(T.as_s_m1 >= MIN_ADSET_WEEK) & (T.as_s_m2 >= MIN_ADSET_WEEK) & (T.as_s >= MIN_ADSET_WEEK)]
    T = T[(T[["rel_m1", "rel_m2", "rel_p1", "rel_p2"]] > 0).all(axis=1)]
    tage = c[c["rank"] == 1].set_index(["adset_id", "week"])["weeks_in_adset"]
    T["top_age"] = [tage.get((a, w), np.nan) for a, w in zip(T.adset_id, T.week)]
    T["takeover"] = T.top != T.prev_top
    T["kind"] = np.where(~T.takeover, "Same #1 as last week",
                         np.where(T.top_age <= 2, "New #1: fresh concept (in adset ≤ 2 weeks)",
                                  "New #1: older concept already in the adset"))
    T["dl"] = np.log(np.sqrt(T.rel_p1 * T.rel_p2) / np.sqrt(T.rel_m1 * T.rel_m2))
    T["ds"] = np.log((T.as_s_p1 + T.as_s_p2) / (T.as_s_m1 + T.as_s_m2))
    tk = T.groupby("kind").agg(cases=("dl", "size"), roas_change=("dl", lambda s: np.expm1(s.median())),
                               improved=("dl", lambda s: (s > 0).mean()),
                               spend_change=("ds", lambda s: np.expm1(s.median()))).reset_index()
    tk.to_csv(os.path.join(OUT, "cr_takeover.csv"), index=False, float_format="%.4f")

    # ---- leaders -----------------------------------------------------------------
    ldr = B.groupby("top").apply(lambda x: pd.Series({
        "adsets_led": x.adset_id.nunique(), "weeks_as_1": len(x), "spend_as_1": x.top_spend.sum(),
        "roas_vs_acct": (x.top_roas * x.top_spend).sum() / (x.top_spend * x.acc_roas).sum(),
        "vs_rest": ((x.top_roas * x.top_spend).sum() / x.top_spend.sum()) /
                   max(1e-9, (x.as_r - x.top_roas * x.top_spend).sum() / max(1e-9, (x.as_s - x.top_spend).sum())),
        "first_as_1": x.week.min(), "last_as_1": x.week.max()})).reset_index().rename(columns={"top": "code"})
    ldr = ldr.merge(attrs.rename(columns={"concept_key": "code"}), on="code", how="left")
    ldr["first_acct"] = ldr["first_acct"].dt.strftime("%Y-%m-%d")
    ldr = ldr.sort_values("spend_as_1", ascending=False).head(25)
    ldr["code"] = ldr["code"].str.replace("^name:", "", regex=True)
    ldr.to_csv(os.path.join(OUT, "cr_leaders.csv"), index=False, float_format="%.4f")

    # ---- account relay: share of all spend by code per week ----------------------
    topcodes = c.groupby("concept_key").spend.sum().sort_values(ascending=False).head(8).index
    ar = c.assign(code=np.where(c.concept_key.isin(topcodes), c.concept_key, "Other")).groupby(["week", "code"]).spend.sum().reset_index()
    ar["share"] = ar.spend / ar.week.map(ar.groupby("week").spend.sum())
    lab = attrs.set_index("concept_key")["cname"]
    ar["label"] = ar.code.map(lambda k: k if k == "Other" else f"{k} · {lab.get(k, '')}")
    ar["key"] = ar.week + "|" + ar.code
    ar.to_csv(os.path.join(OUT, "cr_acct_relay.csv"), index=False, float_format="%.4f")

    # ---- early signals -------------------------------------------------------
    cc = c[c.week < (pd.Timestamp(last_day) - pd.Timedelta(days=34)).strftime("%Y-%m-%d")]
    arr = cc[(cc.weeks_in_adset == 0) & (cc.as_s >= 1000) & (cc.spend >= 20)].copy()
    tops = c[c["rank"] == 1][["adset_id", "concept_key", "week"]]
    tt = tops.merge(arr[["adset_id", "concept_key", "week"]], on=["adset_id", "concept_key"], suffixes=("", "_a"))
    tt = tt[(pd.to_datetime(tt.week) >= pd.to_datetime(tt.week_a)) & (pd.to_datetime(tt.week) <= pd.to_datetime(tt.week_a) + pd.Timedelta(days=28))]
    won = set(zip(tt.adset_id, tt.concept_key))
    arr["won"] = [(a, k) in won for a, k in zip(arr.adset_id, arr.concept_key)]
    arr["share1"] = arr.share
    arr["ipm_rel"] = (arr.ins / arr.imp) / (arr.Ai / arr.Aimp)
    arr["c2i_rel"] = (arr.ins / arr.clk.replace(0, np.nan)) / (arr.Ai / arr.Ac)
    arr["roas_rel"] = arr.roas / arr.as_roas
    arr["ctr_rel"] = (arr.clk / arr.imp) / (arr.Ac / arr.Aimp)
    arr["hook_rel"] = (arr.hx / arr.imp) / (arr.Ahx / arr.Aimp)
    arr["i2p_rel"] = (arr.pur / arr.ins.replace(0, np.nan)) / (arr.Ap / arr.Ai)

    def auc(x, y):
        m = x.notna() & np.isfinite(x)
        x, y = x[m], y[m]
        r = x.rank()
        n1 = y.sum()
        n0 = len(y) - n1
        return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else np.nan

    sig = []
    for k, labl in [("share1", "Share of adset spend in week 1"), ("ipm_rel", "Installs per 1,000 impressions"),
                    ("c2i_rel", "Click → install"), ("roas_rel", "ROAS"), ("hook_rel", "Hook rate"),
                    ("ctr_rel", "Click-through rate"), ("i2p_rel", "Install → purchase")]:
        sig.append(dict(signal=labl, winners=arr[arr.won][k].median(), others=arr[~arr.won][k].median(),
                        power=auc(arr[k], arr.won)))
    pd.DataFrame(sig).to_csv(os.path.join(OUT, "cr_signals.csv"), index=False, float_format="%.4f")
    th = []
    for lo, hi, labl in [(0, 0.05, "Under 5%"), (0.05, 0.10, "5–10%"), (0.10, 0.20, "10–20%"), (0.20, 1.01, "20% or more")]:
        s = arr[(arr.share1 >= lo) & (arr.share1 < hi)]
        th.append(dict(week1_share=labl, arrivals=len(s), became_top=s.won.mean()))
    pd.DataFrame(th).to_csv(os.path.join(OUT, "cr_week1.csv"), index=False, float_format="%.4f")
    facts += [("arrivals", len(arr), "New concepts entering an adset (adset ≥ $1k that week, concept ≥ $20)"),
              ("became_top", arr.won.mean(), "Share that became the adset's #1 within 4 weeks")]

    # ---- the break: same #1 vs changed ---------------------------------------
    def per(lo, hi):
        x = c[(c.week >= lo) & (c.week <= hi)].groupby(["adset_id", "concept_key"]).agg(s=("spend", "sum"), r=("rev", "sum")).reset_index()
        tot = x.groupby("adset_id").agg(S=("s", "sum"), R=("r", "sum"))
        t1 = x.sort_values("s", ascending=False).drop_duplicates("adset_id").set_index("adset_id")
        tot["top"] = t1.concept_key
        tot["top_s"] = t1.s
        tot["top_r"] = t1.r
        return tot
    b, a = per("2026-02-02", "2026-02-15"), per("2026-03-16", "2026-03-29")
    m = b.join(a, lsuffix="_b", rsuffix="_a", how="inner")
    m = m[(m.S_b >= 1500) & (m.S_a >= 1500)]
    m["group"] = np.where(m.top_b == m.top_a, "Same #1 creative before and after", "#1 creative changed")
    brk = m.groupby("group").agg(adsets=("S_b", "size"), S_b=("S_b", "sum"), R_b=("R_b", "sum"), S_a=("S_a", "sum"), R_a=("R_a", "sum")).reset_index()
    brk["roas_before"] = brk.R_b / brk.S_b
    brk["roas_after"] = brk.R_a / brk.S_a
    brk["change"] = brk.roas_after / brk.roas_before - 1
    brk[["group", "adsets", "roas_before", "roas_after", "change"]].to_csv(os.path.join(OUT, "cr_break.csv"), index=False, float_format="%.4f")
    same = m[m.group.str.startswith("Same")]
    facts += [("same_top_before", same.top_r_b.sum() / same.top_s_b.sum(), "ROAS of the unchanged #1 creative, 2–15 Feb"),
              ("same_top_after", same.top_r_a.sum() / same.top_s_a.sum(), "ROAS of the same #1 creative in the same adsets, 16–29 Mar")]
    pd.DataFrame(facts, columns=["fact", "value", "label"]).to_csv(os.path.join(OUT, "cr_facts.csv"), index=False, float_format="%.4f")

    # ---- per-entity concept relay for the grid dossier --------------------------
    c2 = c.merge(meta, left_on="adset_id", right_index=True, how="left")
    c2["key_a"] = "a:" + c2.adset_id.astype(str)
    c2["key_p"] = "p:" + c2.as_persona.astype(str)
    c2["key_pl"] = "pl:" + c2.as_persona.astype(str) + "|" + c2.as_lang.astype(str)
    parts = []
    for kcol in ("key_a", "key_p", "key_pl"):
        e = c2.groupby([kcol, "week", "concept_key"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index().rename(columns={kcol: "ekey"})
        top5 = e.groupby(["ekey", "concept_key"]).spend.sum().reset_index().sort_values("spend", ascending=False).groupby("ekey").head(5)
        keep = set(zip(top5.ekey, top5.concept_key))
        e["code"] = [k if (ek, k) in keep else "Other" for ek, k in zip(e.ekey, e.concept_key)]
        e = e.groupby(["ekey", "week", "code"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index()
        parts.append(e)
    rel = pd.concat(parts, ignore_index=True)
    rel["share"] = rel.spend / rel.groupby(["ekey", "week"]).spend.transform("sum")
    rel["roas"] = rel.rev / rel.spend.replace(0, np.nan)
    rel["cname"] = rel.code.map(lab).fillna("")
    rel["code"] = rel["code"].str.replace("^name:", "", regex=True).str.slice(0, 40)
    rel = rel[rel.spend >= 1]
    rel["key"] = rel.ekey + "|" + rel.week + "|" + rel.code
    rel = rel.drop_duplicates("key")
    rel[["key", "ekey", "week", "code", "cname", "spend", "share", "roas"]].to_csv(
        os.path.join(OUT, "cr_relay.csv"), index=False, float_format="%.4f")

    print(pd.DataFrame(facts, columns=["fact", "value", "label"]).to_string())
    print(reign.round(3).to_string())
    print(conc.round(3).to_string())
    print(tk.round(3).to_string())
    print(pd.read_csv(os.path.join(OUT, "cr_signals.csv")).round(3).to_string())
    print(pd.read_csv(os.path.join(OUT, "cr_week1.csv")).round(3).to_string())
    print(pd.read_csv(os.path.join(OUT, "cr_break.csv")).round(3).to_string())
    print(ldr[["code", "cname", "top_hook", "adsets_led", "weeks_as_1", "spend_as_1", "roas_vs_acct", "vs_rest"]].head(12).round(3).to_string())
    for f in ("cr_relay.csv", "cr_acct_relay.csv"):
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")


if __name__ == "__main__":
    main()
