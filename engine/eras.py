"""Measurement eras: what the Singular switch changed, which decisions were made on
the new ruler, and whether our findings hold in the Singular era alone.

Needs engine/model.py (data/model/*.pkl). Writes to output/data/:
  era_weekly.csv   week × OS × metric, indexed to the pre-switch average (what moved, what didn't)
  era_os.csv       the same per OS: before vs Singular era, and the ratio
  era_moves.csv    budget moves per era: did they follow the adset's relative result?
  era_cuts.csv     adsets switched off since the switch while at or above their OS average
  era_launch.csv   concepts launched per month, judged on the stable (relative) ruler
  era_compare.csv  each key finding on full history vs Singular era only
  era_facts.csv    switch dates, bars, ratios, spend path

Run:  python3 engine/eras.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from settings import SWITCH, PRE_END, SINGULAR_START, BARS, BAR_STATUS, era  # noqa: E402

ROOT = os.path.dirname(HERE)
MODEL = os.path.join(ROOT, "data", "model")
OUT = os.path.join(ROOT, "output", "data")
OSES = ("iOS", "Android")
MOVE = 0.20          # |log spend change| that counts as a budget move (≈ ±20%)
STRONG, WEAK = 1.05, 0.95


def wsum(v, w):
    v, w = np.asarray(v, float), np.asarray(w, float)
    m = np.isfinite(v) & np.isfinite(w)
    return (v[m] * w[m]).sum() / w[m].sum() if w[m].sum() else np.nan


def dt(s):
    return pd.to_datetime(s)


def load():
    m = {k: pd.read_pickle(os.path.join(MODEL, f"{k}.pkl")) for k in
         ("adset_week", "adset_dim", "ad_week", "apple_week", "country_week", "meta")}
    fw = m["meta"].full_weeks.tolist()
    dim = m["adset_dim"]
    a = m["adset_week"]
    a = a[a.week.isin(fw)].join(dim[["name", "os", "persona", "lang", "judged", "geo"]], on="adset_id")
    a = a[a.judged & a.os.isin(OSES) & (a.spend > 0)].copy()
    acc = a.groupby(["week", "os"]).agg(S=("spend", "sum"), R=("rev", "sum"))
    acc["os_roas"] = acc.R / acc.S
    a = a.join(acc["os_roas"], on=["week", "os"])
    a["roas"] = a.rev / a.spend
    a["rel"] = a.roas / a.os_roas
    a["era"] = a.week.map(era)
    ad = m["ad_week"]
    ad = ad[ad.week.isin(fw)].join(dim[["os", "judged"]], on="adset_id")
    ad = ad[ad.judged & ad.os.isin(OSES)]
    c = ad.groupby(["adset_id", "week", "concept_key"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index()
    c = c.join(dim["os"], on="adset_id").join(acc["os_roas"], on=["week", "os"])
    c = c[c.spend > 0]
    return m, fw, dim, a, acc, c


# ---------------------------------------------------------------------------------------------
def measurement(a, m, fw):
    """Weekly OS metrics indexed to the pre-switch average: which ones stepped at the switch."""
    W = a.groupby(["week", "os"]).agg(spend=("spend", "sum"), rev=("rev", "sum"), imp=("impressions", "sum"),
                                      ins=("installs", "sum"), clk=("clicks", "sum"), pur=("purchases", "sum"))
    hook = a.assign(hx=a.hook_rate.fillna(0) * a.impressions).groupby(["week", "os"]).hx.sum()
    W["Meta ROAS"] = W.rev / W.spend
    W["Purchases per 1M impressions"] = W.pur * 1e6 / W.imp
    W["Installs per 1k impressions"] = W.ins * 1000 / W.imp
    W["Click → install"] = W.ins / W.clk
    W["CPM"] = W.spend * 1000 / W.imp
    W["Click-through rate"] = W.clk / W.imp
    W["Hook rate"] = hook / W.imp
    mets = [("Meta ROAS", "Credited through the MMP"), ("Purchases per 1M impressions", "Credited through the MMP"),
            ("Installs per 1k impressions", "Credited through the MMP"), ("Click → install", "Credited through the MMP"),
            ("CPM", "Meta's own count"), ("Click-through rate", "Meta's own count"), ("Hook rate", "Meta's own count")]
    W = W.reset_index()
    W["era"] = W.week.map(era)
    rows, tab = [], []
    for o in OSES:
        x = W[W.os == o]
        pre, sing = x[x.era == "pre"], x[x.era == "singular"]
        base = {}
        for k, kind in mets:
            # ratio of sums for the era values, so one odd week doesn't dominate
            def agg(f):
                if k == "Meta ROAS":
                    return f.rev.sum() / f.spend.sum()
                if k == "Purchases per 1M impressions":
                    return f.pur.sum() * 1e6 / f.imp.sum()
                if k == "Installs per 1k impressions":
                    return f.ins.sum() * 1000 / f.imp.sum()
                if k == "Click → install":
                    return f.ins.sum() / f.clk.sum()
                if k == "CPM":
                    return f.spend.sum() * 1000 / f.imp.sum()
                if k == "Click-through rate":
                    return f.clk.sum() / f.imp.sum()
                return wsum(f[k], f.imp)
            b, s = agg(pre), agg(sing)
            base[k] = b
            # step at the switch: 4 weeks before vs 4 weeks after this OS's switch week
            sw = SWITCH[o]
            bef = x[(x.week < sw)].tail(4)
            aft = x[(x.week >= sw)].head(4)
            step = agg(aft) / agg(bef) - 1 if len(bef) and len(aft) else np.nan
            tab.append(dict(os=o, metric=k, kind=kind, pre=b, singular=s, ratio=s / b if b else np.nan, step=step,
                            key=f"{o}|{k}"))
        for _, r in x.iterrows():
            for k, kind in mets:
                rows.append(dict(week=r.week, os=o, metric=k, kind=kind, value=r[k],
                                 index=r[k] / base[k] if base[k] else np.nan))
    E = pd.DataFrame(rows)
    E["key"] = E.week + "|" + E.os + "|" + E.metric
    E.to_csv(os.path.join(OUT, "era_weekly.csv"), index=False, float_format="%.4f")
    T = pd.DataFrame(tab)
    T.to_csv(os.path.join(OUT, "era_os.csv"), index=False, float_format="%.4f")
    return T


# ---------------------------------------------------------------------------------------------
def moves_table(a):
    """Week-over-week budget moves of ±20%+, judged against the adset's result vs its OS account
    in the two weeks before (what the buyer could see)."""
    x = a.sort_values(["adset_id", "week"]).copy()
    g = x.groupby("adset_id")
    for k in (1, 2):
        x[f"s_m{k}"] = g.spend.shift(k)
        x[f"r_m{k}"] = g.rev.shift(k)
        x[f"rel_m{k}"] = g.rel.shift(k)
        x[f"w_m{k}"] = g.week.shift(k)
        x[f"os_m{k}"] = g.os_roas.shift(k)
    ok = ((dt(x.week) - dt(x.w_m1)).dt.days == 7) & ((dt(x.w_m1) - dt(x.w_m2)).dt.days == 7)
    x = x[ok & (x.s_m1 >= 300) & (x.s_m2 >= 300)].copy()
    x["dls"] = np.log(x.spend / x.s_m1)
    x["prior_rel"] = (x.rel_m1 * x.s_m1 + x.rel_m2 * x.s_m2) / (x.s_m1 + x.s_m2)
    x["prior_roas"] = (x.r_m1 + x.r_m2) / (x.s_m1 + x.s_m2)
    x["prior_ruler"] = np.where(x.w_m2 >= x.os.map(SWITCH), "singular", np.where(x.w_m1 < x.os.map(SWITCH), "meta", "mixed"))
    x["old_bar_red"] = x.prior_roas < BARS["meta"]["amber"]
    mv = x[x.dls.abs() >= MOVE].copy()
    up = mv.dls > 0
    mv["verdict"] = np.select([(mv.prior_rel >= STRONG) & up, (mv.prior_rel >= STRONG) & ~up,
                               (mv.prior_rel <= WEAK) & ~up, (mv.prior_rel <= WEAK) & up],
                              ["right", "wrong", "right", "wrong"], "neutral")
    mv["moved"] = (mv.spend - mv.s_m1).abs()
    rows = []
    for e in ("pre", "transition", "singular"):
        z = mv[mv.era == e]
        if not len(z):
            continue
        n_w = z.week.nunique()
        sc = z[(z.prior_rel >= STRONG) & ~(z.dls > 0)]
        rows.append(dict(
            era=e, weeks=n_w, moves=len(z), moves_per_week=len(z) / n_w,
            right=(z.verdict == "right").sum(), wrong=(z.verdict == "wrong").sum(), neutral=(z.verdict == "neutral").sum(),
            right_share=(z.verdict == "right").sum() / max(1, (z.verdict != "neutral").sum()),
            right_dollars=z[z.verdict == "right"].moved.sum(), wrong_dollars=z[z.verdict == "wrong"].moved.sum(),
            strong_cut=len(sc), strong_cut_red_old_bar=int(sc.old_bar_red.sum()),
            strong_cut_red_new_bar=int((sc.prior_roas < BARS["singular"]["amber"]).sum()),
            weak_raised=int(((z.prior_rel <= WEAK) & (z.dls > 0)).sum())))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "era_moves.csv"), index=False, float_format="%.4f")
    return R, mv


# ---------------------------------------------------------------------------------------------
def cuts_table(a, fw):
    """Adsets switched off since the iOS switch, judged on their last 4 spending weeks vs their OS account."""
    L = a.groupby("adset_id").agg(last=("week", "max"), name=("name", "first"), persona=("persona", "first"),
                                  os=("os", "first"), peak=("spend", "max"))
    off = L[(L["last"] >= SWITCH["iOS"]) & (L["last"] <= fw[-3]) & (L.peak >= 1500)]
    rows = []
    for aid, r in off.iterrows():
        g = a[(a.adset_id == aid) & (a.week <= r["last"])].sort_values("week").tail(4)
        if g.spend.sum() < 1000:
            continue
        lw = dt(r["last"])
        p = a[(a.persona == r.persona) & (a.os == r.os)]
        pw = dt(p.week)
        before = p[(pw > lw - pd.Timedelta(days=28)) & (pw <= lw)].spend.sum() / 4
        after = p[(pw > lw) & (pw <= lw + pd.Timedelta(days=28))].spend.sum() / 4
        now = p[p.week.isin(fw[-4:])].spend.sum() / 4
        roas4 = g.rev.sum() / g.spend.sum()
        rows.append(dict(adset_id=aid, name=r["name"], persona=r.persona, os=r.os, last_week=r["last"],
                         era_off=era(r["last"]), peak_wk=r.peak, spend_last4=g.spend.sum() / len(g),
                         roas_last4=roas4, rel_last4=wsum(g.rel, g.spend),
                         old_bar=("red" if roas4 < BARS["meta"]["amber"] else "amber" if roas4 < BARS["meta"]["green"] else "green"),
                         new_bar=("red" if roas4 < BARS["singular"]["amber"] else "amber" if roas4 < BARS["singular"]["green"] else "green"),
                         persona_before=before, persona_after=after, persona_now=now))
    O = pd.DataFrame(rows).sort_values("peak_wk", ascending=False)
    O["verdict"] = np.select([O.rel_last4 >= 1.0, O.rel_last4 >= WEAK], ["At or above its OS average", "About average"],
                             "Below its OS average")
    O["persona_fate"] = np.select([O.persona_now <= 1, O.persona_now < 0.5 * O.persona_before],
                                  ["Persona dark on this OS", "Persona shrank"], "Persona carried on")
    O.to_csv(os.path.join(OUT, "era_cuts.csv"), index=False, float_format="%.4f")
    return O


# ---------------------------------------------------------------------------------------------
def launches(c, fw):
    """Concepts launched per month, and how they did on the stable ruler (vs their OS account)."""
    first = c.groupby("concept_key").week.min()
    life = c.groupby("concept_key").spend.sum()
    keys = first[(first > fw[0]) & (life.reindex(first.index) >= 200)].index
    x = c[c.concept_key.isin(keys)].copy()
    x["age"] = (dt(x.week) - dt(x.concept_key.map(first))).dt.days // 7
    x = x[x.age <= 7]
    x["exp"] = x.spend * x.os_roas
    # became #1 somewhere within its first 5 weeks (adset ≥ $500 that week)
    A = c.groupby(["adset_id", "week"]).spend.sum().rename("as_s")
    cc = c.join(A, on=["adset_id", "week"])
    tops = cc[cc.as_s >= 500].sort_values("spend", ascending=False).drop_duplicates(["adset_id", "week"])
    tops = tops[tops.concept_key.isin(keys)]
    tops["age"] = (dt(tops.week) - dt(tops.concept_key.map(first))).dt.days // 7
    won = set(tops[tops.age <= 4].concept_key)
    g = x.groupby("concept_key").agg(spend8=("spend", "sum"), rev8=("rev", "sum"), exp8=("exp", "sum"))
    g["month"] = dt(g.index.map(first)).strftime("%Y-%m")
    g["won"] = g.index.isin(won)
    g["era"] = g.index.map(first).map(era)
    M = g.groupby("month").agg(concepts=("spend8", "size"), spend_first_8w=("spend8", "sum"),
                               rev=("rev8", "sum"), exp=("exp8", "sum"), became_top=("won", "mean")).reset_index()
    M["rel_index"] = M.rev / M.exp
    M["spend_per_concept"] = M.spend_first_8w / M.concepts
    # a month is complete once its last launch has had 8 weeks to run
    M["complete"] = (dt(M.month + "-01") + pd.offsets.MonthEnd(0) + pd.Timedelta(days=56)) <= dt(fw[-1]) + pd.Timedelta(days=6)
    M = M.drop(columns=["rev", "exp"])
    M.to_csv(os.path.join(OUT, "era_launch.csv"), index=False, float_format="%.4f")
    return M


# ---------------------------------------------------------------------------------------------
def findings(a, c, m, fw, lo):
    """Key findings computed only from weeks >= lo (None = full history). Same method both ways."""
    out = {}
    A = a if lo is None else a[a.week >= lo]
    # concept table with first-in-adset and first-in-account from FULL history (so the window
    # start doesn't create fake "new" arrivals)
    fia = c.groupby(["adset_id", "concept_key"]).week.min().rename("fia")
    fic = c.groupby("concept_key").week.min().rename("fic")
    C = c.join(fia, on=["adset_id", "concept_key"]).join(fic, on="concept_key")
    C = C if lo is None else C[C.week >= lo]
    S = C.groupby(["adset_id", "week"]).agg(as_s=("spend", "sum"), as_r=("rev", "sum"), os_roas=("os_roas", "first")).reset_index()
    S["rel"] = (S.as_r / S.as_s) / S.os_roas
    C = C.merge(S[["adset_id", "week", "as_s", "as_r", "rel"]], on=["adset_id", "week"])
    C["share"] = C.spend / C.as_s
    top = C.sort_values("spend", ascending=False).drop_duplicates(["adset_id", "week"])[["adset_id", "week", "concept_key", "spend", "rev", "share"]]
    top = top.rename(columns={"concept_key": "top", "spend": "top_s", "rev": "top_r", "share": "top_share"})
    B = S.merge(top, on=["adset_id", "week"]).sort_values(["adset_id", "week"]).reset_index(drop=True)
    g = B.groupby("adset_id")
    B["prev_top"], B["pweek"] = g.top.shift(), g.week.shift()
    cont = (B.top == B.prev_top) & ((dt(B.week) - dt(B.pweek)).dt.days == 7)
    B["run"] = (~cont).cumsum()
    B["tenure"] = B.groupby("run").cumcount() + 1
    B["run_len"] = B.groupby("run").tenure.transform("max")
    Bm = B[B.as_s >= 500]

    # 1 reign length
    runs = Bm.groupby("run").agg(weeks=("tenure", "max"), s=("as_s", "sum"))
    runs = runs[runs.s >= 2000]
    out["reign_median"] = runs.weeks.median()
    # 2 reign slide: adset rel in week 3 and 5 of a 4+ week reign vs week 1
    Lr = Bm[Bm.run_len >= 4].copy()
    f1 = Lr[Lr.tenure == 1].set_index("run").rel
    Lr["vs1"] = Lr.rel / Lr.run.map(f1)
    out["reign_wk3"] = Lr[Lr.tenure == 3].vs1.median() - 1
    out["reign_wk5"] = Lr[Lr.tenure == 5].vs1.median() - 1
    # 3 #1 vs rest of its adset (same week; no ruler involved)
    X = Bm[(Bm.top_share < 0.95) & (Bm.as_s - Bm.top_s >= 150)]
    out["top_vs_rest"] = (X.top_r.sum() / X.top_s.sum()) / ((X.as_r - X.top_r).sum() / (X.as_s - X.top_s).sum())
    # 4 concentration: adset vs OS account when #1 holds 70–95% vs under 35%
    hi, low = X[X.top_share >= 0.70], X[X.top_share < 0.35]
    out["conc_hi_rel"] = wsum(hi.rel, hi.as_s)
    out["conc_low_rel"] = wsum(low.rel, low.as_s)
    # 5 takeovers by a fresh concept: rel 2 weeks after vs 2 weeks before
    T = B.copy()
    gg = T.groupby("adset_id")
    for k in (1, 2):
        for col in ("rel", "as_s", "week"):
            T[f"{col}_m{k}"] = gg[col].shift(k)
            T[f"{col}_p{k}"] = gg[col].shift(-k)
    T = T.dropna(subset=["rel_m1", "rel_m2", "rel_p1", "rel_p2"])
    T = T[(dt(T.week_p2) - dt(T.week_m2)).dt.days == 28]
    T = T[(T[["as_s_m1", "as_s_m2", "as_s"]] >= 500).all(axis=1) & (T[["rel_m1", "rel_m2", "rel_p1", "rel_p2"]] > 0).all(axis=1)]
    T = T.join(fia.rename("top_fia"), on=["adset_id", "top"])
    T["dl"] = np.log(np.sqrt(T.rel_p1 * T.rel_p2) / np.sqrt(T.rel_m1 * T.rel_m2))
    fresh = T[(T.top != T.prev_top) & ((dt(T.week) - dt(T.top_fia)).dt.days <= 14)]
    same = T[T.top == T.prev_top]
    out["takeover_fresh"] = np.expm1(fresh.dl.median())
    out["takeover_same"] = np.expm1(same.dl.median())
    # 6 refresh: new concepts (≤ 2 weeks in the adset) took 20%+ of spend that week vs none
    C["is_new"] = (dt(C.week) - dt(C.fia)).dt.days <= 7
    ns = C[C.is_new].groupby(["adset_id", "week"]).spend.sum()
    T2 = T.join(ns.rename("new_s"), on=["adset_id", "week"]).fillna({"new_s": 0})
    T2["new_share"] = T2.new_s / T2.as_s
    out["refresh_won"] = np.expm1(T2[T2.new_share >= 0.20].dl.median())
    out["refresh_none"] = np.expm1(T2[T2.new_share <= 0.001].dl.median())
    # 7 week-1 delivery decides: arrivals in adsets ≥ $1k, followed up for 4 weeks
    cutoff = (dt(fw[-1]) - pd.Timedelta(days=28)).strftime("%Y-%m-%d")
    arr = C[(C.week == C.fia) & (C.as_s >= 1000) & (C.spend >= 20) & (C.week <= cutoff)].copy()
    tt = B[["adset_id", "week", "top"]].rename(columns={"top": "concept_key", "week": "tw"})
    tt = tt.merge(arr[["adset_id", "concept_key", "week"]], on=["adset_id", "concept_key"])
    tt = tt[(dt(tt.tw) >= dt(tt.week)) & (dt(tt.tw) <= dt(tt.week) + pd.Timedelta(days=28))]
    won = set(zip(tt.adset_id, tt.concept_key))
    arr["won"] = [(x, y) in won for x, y in zip(arr.adset_id, arr.concept_key)]
    out["wk1_hi_top"] = arr[arr.share >= 0.20].won.mean()
    out["wk1_lo_top"] = arr[arr.share < 0.05].won.mean()
    r = arr.share.rank()
    n1, n0 = arr.won.sum(), (~arr.won).sum()
    out["wk1_auc"] = (r[arr.won].sum() - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else np.nan
    arr["new_acct"] = arr.week == arr.fic
    out["new_delivered"] = (arr[arr.new_acct].share >= 0.20).mean()
    out["proven_delivered"] = (arr[~arr.new_acct].share >= 0.20).mean()
    # 8 spend elasticity and luck (adset weekly, vs OS account)
    j = A.sort_values(["adset_id", "week"]).copy()
    for col in ("spend", "rel", "week"):
        j["p_" + col] = j.groupby("adset_id")[col].shift()
    x = j[(j.p_spend >= 300) & (j.spend >= 300) & (j.rel > 0) & (j.p_rel > 0) & ((dt(j.week) - dt(j.p_week)).dt.days == 7)]
    Wt = np.sqrt(x.spend.values)
    Xm = np.column_stack([np.ones(len(x)), np.log(x.spend / x.p_spend), np.log(x.p_rel)])
    b = np.linalg.lstsq(Xm * Wt[:, None], np.log(x.rel / x.p_rel).values * Wt, rcond=None)[0]
    out["elasticity"] = b[1]
    out["mean_reversion"] = -b[2]
    # 9 App Store proceeds per iOS $ (top 40 storefronts, country + week fixed effects)
    cw, ap, dim = m["country_week"], m["apple_week"], m["adset_dim"]
    cw = cw[cw.week.isin(fw)].join(dim[["os", "judged"]], on="adset_id")
    sw = cw[(cw.os == "iOS") & cw.judged].dropna(subset=["store"]).groupby(["store", "week"]).spend.sum()
    top40 = sw.groupby("store").sum().sort_values(ascending=False).head(40).index
    P = ap[ap.store.isin(top40) & ap.week.isin(fw)].set_index(["store", "week"]).join(sw.rename("s")).fillna({"s": 0}).reset_index().sort_values(["store", "week"])

    def ads(v, dec=0.5):
        o = np.zeros(len(v))
        for i in range(len(v)):
            o[i] = v[i] + (dec * o[i - 1] if i else 0)
        return o
    P["A"] = P.groupby("store").s.transform(lambda v: pd.Series(ads(v.values), index=v.index))
    if lo is not None:
        P = P[P.week >= lo]
    Y, Xa = P.pivot(index="week", columns="store", values="proceeds"), P.pivot(index="week", columns="store", values="A")

    def dm(Z):
        return Z - Z.mean(axis=0) - Z.mean(axis=1).values[:, None] + Z.values.mean()
    yy, xx = dm(Y).values.ravel(), dm(Xa).values.ravel()
    mk = np.isfinite(yy) & np.isfinite(xx)
    out["store_per_ios_dollar"] = (xx[mk] * yy[mk]).sum() / (xx[mk] ** 2).sum() * 2
    # 10 budget moves that followed the relative result
    return out


def compare(a, c, m, fw):
    full = findings(a, c, m, fw, None)
    sing = findings(a, c, m, fw, SINGULAR_START)
    spec = [
        ("Creatives", "reign_median", "Weeks a concept stays an adset's #1 (median)", "n1"),
        ("Creatives", "reign_wk3", "Adset ROAS in week 3 of a reign vs week 1 (vs its OS account)", "pct"),
        ("Creatives", "reign_wk5", "Adset ROAS in week 5 of a reign vs week 1", "pct"),
        ("Creatives", "top_vs_rest", "ROAS of the #1 concept vs the rest of its adset, same week", "x"),
        ("Creatives", "conc_hi_rel", "Adset vs OS account when the #1 takes 70–95% of spend", "x"),
        ("Creatives", "conc_low_rel", "Adset vs OS account when the #1 takes under 35%", "x"),
        ("Creatives", "takeover_fresh", "Adset ROAS change when a fresh concept takes #1 (2 wks after vs before)", "pct"),
        ("Creatives", "takeover_same", "Same, when the #1 doesn't change", "pct"),
        ("Creatives", "refresh_won", "Adset ROAS change when new creative wins 20%+ of spend", "pct"),
        ("Creatives", "refresh_none", "Same, with no new creative", "pct"),
        ("Creatives", "wk1_hi_top", "New concepts with 20%+ of adset spend in week 1 that became #1", "pct"),
        ("Creatives", "wk1_lo_top", "New concepts with under 5% in week 1 that became #1", "pct"),
        ("Creatives", "wk1_auc", "How well week-1 spend share predicts a new #1 (0.5 = coin flip)", "n2"),
        ("Creatives", "new_delivered", "Brand-new concepts that won 20%+ of adset spend in week 1", "pct"),
        ("Creatives", "proven_delivered", "Proven concepts entering a new adset that won 20%+", "pct"),
        ("Budget", "elasticity", "Change in relative ROAS per doubling of adset spend (log units), luck removed", "n2"),
        ("Budget", "mean_reversion", "Share of a week's edge over the account that is gone the next week", "pct"),
        ("Store money", "store_per_ios_dollar", "App Store proceeds per iOS ad $ (country + week fixed effects)", "usd"),
    ]
    rows = []
    for area, k, label, fmt in spec:
        f, s = full.get(k, np.nan), sing.get(k, np.nan)
        if pd.isna(f) or pd.isna(s):
            v = "Not enough data"
        elif fmt == "pct" and abs(f) < 0.03 and abs(s) < 0.03:
            v = "Holds (both about zero)"
        elif (f > 0) != (s > 0) and fmt in ("pct", "n2") and k not in ("wk1_auc",):
            v = "Doesn't hold"
        else:
            ratio = s / f if f else np.nan
            if fmt in ("x", "n2") and k not in ("elasticity",):
                ok = abs(s - f) <= 0.1 * max(abs(f), 0.5)
            else:
                ok = 0.75 <= ratio <= 1.33 if pd.notna(ratio) else False
            v = "Holds" if ok else ("Same direction, smaller" if abs(s) < abs(f) else "Same direction, bigger")
        rows.append(dict(area=area, finding=k, label=label, fmt=fmt, full=f, singular=s, verdict=v))
    # the absolute ruler itself, as a warning row
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "era_compare.csv"), index=False, float_format="%.4f")
    return R


# ---------------------------------------------------------------------------------------------
def main():
    os.makedirs(OUT, exist_ok=True)
    m, fw, dim, a, acc, c = load()
    T = measurement(a, m, fw)
    R, mv = moves_table(a)
    O = cuts_table(a, fw)
    M = launches(c, fw)
    K = compare(a, c, m, fw)

    # account path, store money and green share per era
    ap = m["apple_week"]
    ap = ap[ap.week.isin(fw)].groupby("week").proceeds.sum()
    sp = a.groupby("week").spend.sum()
    win = [("pre", fw[0], PRE_END), ("transition", SWITCH["iOS"], "2026-03-15"),
           ("singular_early", SINGULAR_START, "2026-06-29"), ("singular_late", "2026-07-06", fw[-1])]
    F = []
    for k, lo, hi in win:
        F += [(f"spend_wk_{k}", sp[(sp.index >= lo) & (sp.index <= hi)].mean(), f"Purchase-adset spend per week, {lo} to {hi}"),
              (f"store_wk_{k}", ap[(ap.index >= lo) & (ap.index <= hi)].mean(), f"App Store proceeds per week, {lo} to {hi}")]
    # green share on each bar
    a["old_green"] = a.roas >= BARS["meta"]["green"]
    a["new_green"] = a.roas >= BARS["singular"]["green"]
    for e in ("pre", "singular"):
        z = a[a.era == e]
        F += [(f"green_old_bar_{e}", z[z.old_green].spend.sum() / z.spend.sum(), f"Spend share at ROAS ≥ 0.50, {e} era"),
              (f"green_new_bar_{e}", z[z.new_green].spend.sum() / z.spend.sum(), f"Spend share at ROAS ≥ {BARS['singular']['green']:.2f}, {e} era")]
    for o in OSES:
        pre = a[(a.os == o) & (a.era == "pre")]
        sg = a[(a.os == o) & (a.era == "singular")]
        rp, rs = pre.rev.sum() / pre.spend.sum(), sg.rev.sum() / sg.spend.sum()
        F += [(f"meta_roas_pre_{o}", rp, f"Meta {o} ROAS, Meta's own attribution (weeks to {PRE_END})"),
              (f"meta_roas_sing_{o}", rs, f"Meta {o} ROAS, Singular era (weeks from {SINGULAR_START})"),
              (f"ruler_ratio_{o}", rs / rp, f"Singular-era Meta ROAS / pre-switch Meta ROAS, {o}")]
    ratio = np.mean([dict((f[0], f[1]) for f in F)[f"ruler_ratio_{o}"] for o in OSES])
    F += [("switch_ios", np.nan, SWITCH["iOS"]), ("switch_android", np.nan, SWITCH["Android"]),
          ("pre_end", np.nan, PRE_END), ("singular_start", np.nan, SINGULAR_START),
          ("bar_green_meta", BARS["meta"]["green"], "Green from, Meta's own attribution"),
          ("bar_amber_meta", BARS["meta"]["amber"], "Amber from, Meta's own attribution"),
          ("bar_deep_meta", BARS["meta"]["deep"], "Deep red below, Meta's own attribution"),
          ("bar_green_singular", BARS["singular"]["green"], "Green from, Singular"),
          ("bar_amber_singular", BARS["singular"]["amber"], "Amber from, Singular"),
          ("bar_deep_singular", BARS["singular"]["deep"], "Deep red below, Singular"),
          ("bar_status", np.nan, BAR_STATUS),
          ("ruler_ratio", ratio, "Average Singular / pre-switch ratio, both OS"),
          ("old_units_of_039", 0.39 / ratio, "A Singular-era ROAS of 0.39 in pre-switch units"),
          ("cuts_strong", int((O.rel_last4 >= 1.0).sum()), "Adsets switched off since the switch while at or above their OS average"),
          ("cuts_strong_peak", O[O.rel_last4 >= 1.0].peak_wk.sum(), "Their combined peak spend per week"),
          ("cuts_total", len(O), "Adsets (peak ≥ $1.5k/wk) switched off since the switch"),
          ]
    for e in ("pre", "singular"):
        r = R[R.era == e]
        if len(r):
            r = r.iloc[0]
            F += [(f"moves_right_{e}", r.right_share, f"Budget moves that followed the relative result, {e} era"),
                  (f"moves_per_week_{e}", r.moves_per_week, f"Budget moves of ±20%+ per week, {e} era"),
                  (f"strong_cut_per_week_{e}", r.strong_cut / r.weeks, f"Cuts of adsets beating their OS average, per week, {e} era")]
    # US inside the same worldwide adsets (iOS): Meta ROAS of US traffic vs the rest
    cw = m["country_week"]
    cw = cw[cw.week.isin(fw)].join(dim[["os", "judged", "name"]], on="adset_id")
    ww = cw[cw.judged & (cw.os == "iOS") & ~cw.name.str.contains("US-ENG|US-ES", regex=True, na=False)]
    for e in ("pre", "singular"):
        z = ww[ww.week.map(era) == e]
        us, rest = z[z.country == "US"], z[z.country != "US"]
        F.append((f"us_vs_rest_ww_{e}", (us.rev.sum() / us.spend.sum()) / (rest.rev.sum() / rest.spend.sum()),
                  f"Inside worldwide iOS adsets: US Meta ROAS / rest of world, {e} era"))
    FD = pd.DataFrame(F, columns=["fact", "value", "label"])
    FD.to_csv(os.path.join(OUT, "era_facts.csv"), index=False, float_format="%.4f")

    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 80)
    print(T.round(3).to_string())
    print(R.round(3).to_string())
    print(O[["name", "os", "last_week", "peak_wk", "roas_last4", "rel_last4", "old_bar", "new_bar", "persona_before", "persona_now", "verdict", "persona_fate"]].round(2).head(20).to_string())
    print(M.round(3).to_string())
    print(K[["label", "full", "singular", "verdict"]].round(3).to_string())
    print(FD.round(3).to_string())


if __name__ == "__main__":
    main()
