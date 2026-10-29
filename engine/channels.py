"""Channels: Meta and TikTok side by side against the App Store money.

Each network credits itself on its own ruler (Meta through Singular since 23 Feb / 9 Mar 2026,
TikTok through its MMP campaigns since the week of 2 Feb 2026), so credited ROAS is never
compared across channels. The common currency is App Store proceeds by country and week.

TikTok "ghost" value: since the MMP migration TikTok is credited with purchase value on ad groups
that didn't spend that week (most haven't spent since 2024–25: renewals and repeat purchases of
old users). It is real money but not caused by current spend, so TikTok is judged on "live" value
(ad-group weeks with spend >= $20) and the ghost value is reported as a check.

Needs engine/model.py (data/model/*.pkl) and data/raw/tiktok/. Writes to output/data/:
  ch_weekly.csv    week: spend and credited revenue per channel × OS, App Store proceeds
  ch_store.csv     App Store proceeds per iOS $ by channel, several model specs
  ch_country.csv   countries: spend per channel before vs now, credited ROAS index, store money
  ch_adgroups.csv  TikTok ad groups: last week, peak, weekly spend and ROAS vs TikTok's own OS
  ch_facts.csv     numbers quoted in the dashboard text

Run:  python3 engine/channels.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from settings import PRE_END, SINGULAR_START, TIKTOK_MMP_START, era  # noqa: E402
from tiktok import load_tiktok  # noqa: E402

ROOT = os.path.dirname(HERE)
MODEL = os.path.join(ROOT, "data", "model")
OUT = os.path.join(ROOT, "output", "data")
NOW_N = 10
WEEKS_SHOWN = 16
LIVE_MIN = 20          # an ad-group week counts as live from $20 of spend


def adstock(v, dec):
    o = np.zeros(len(v))
    for i in range(len(v)):
        o[i] = v[i] + (dec * o[i - 1] if i else 0)
    return o


def two_way(Q, ycol, xcols):
    """Country + week fixed effects by double demeaning a balanced store × week panel."""
    def dm(col):
        Z = Q.pivot(index="week", columns="store", values=col)
        return (Z - Z.mean(axis=0) - Z.mean(axis=1).values[:, None] + Z.values.mean()).values.ravel()
    X = np.column_stack([dm(c) for c in xcols])
    return np.linalg.lstsq(X, dm(ycol), rcond=None)[0]


def main():
    os.makedirs(OUT, exist_ok=True)
    m = {k: pd.read_pickle(os.path.join(MODEL, f"{k}.pkl")) for k in ("country_week", "adset_dim", "apple_week", "meta")}
    fw = m["meta"].full_weeks.tolist()
    NOW = fw[-NOW_N:]
    ap = m["apple_week"]
    ap = ap[ap.week.isin(fw)]
    dim = m["adset_dim"]
    cw = m["country_week"].join(dim[["os", "judged"]], on="adset_id")
    cw = cw[cw.judged & cw.week.isin(fw) & cw.os.isin(["iOS", "Android"])]
    tt = load_tiktok(ap.store.unique())
    agw = tt.groupby(["adgroup_id", "week"]).spend.transform("sum")
    tt["live"] = agw >= LIVE_MIN
    tt["rev_all"] = tt["rev"]
    tt["ghost"] = np.where(tt.live, 0.0, tt.rev)
    tt["rev"] = np.where(tt.live, tt.rev, 0.0)        # judged value = live value only
    tt.to_pickle(os.path.join(MODEL, "tt_week.pkl"))
    tj = tt[(tt.objective == "Purchase") & tt.os.isin(["iOS", "Android"]) & tt.week.isin(fw)]

    # ================= weekly, account level ==================================
    def wk(df, s, r, o):
        x = df[df.os == o]
        return x.groupby("week")[s].sum(), x.groupby("week")[r].sum()
    W = pd.DataFrame(index=pd.Index(fw, name="week"))
    for lab, df, s, r in (("meta", cw, "spend", "rev"), ("tt", tj, "spend", "rev")):
        for o, k in (("iOS", "ios"), ("Android", "and")):
            a, b = wk(df, s, r, o)
            W[f"{lab}_{k}_spend"], W[f"{lab}_{k}_rev"] = a, b
    for o, k in (("iOS", "ios"), ("Android", "and")):
        W[f"tt_{k}_ghost"] = tj[tj.os == o].groupby("week").ghost.sum()
    W = W.fillna(0)
    W["store_proceeds"] = ap.groupby("week").proceeds.sum()
    for lab in ("meta", "tt"):
        for k in ("ios", "and"):
            W[f"{lab}_{k}_roas"] = W[f"{lab}_{k}_rev"] / W[f"{lab}_{k}_spend"].replace(0, np.nan)
    for k in ("ios", "and"):
        W[f"tt_{k}_roas_reported"] = (W[f"tt_{k}_rev"] + W[f"tt_{k}_ghost"]) / W[f"tt_{k}_spend"].replace(0, np.nan)
    W["paid_spend"] = W[["meta_ios_spend", "meta_and_spend", "tt_ios_spend", "tt_and_spend"]].sum(axis=1)
    W["tt_share"] = (W.tt_ios_spend + W.tt_and_spend) / W.paid_spend
    W["era"] = [era(w) for w in W.index]
    W = W.reset_index()
    W.to_csv(os.path.join(OUT, "ch_weekly.csv"), index=False, float_format="%.4f")

    # ================= App Store proceeds per iOS $ by channel =================
    mi = cw[cw.os == "iOS"].dropna(subset=["store"]).groupby(["store", "week"]).spend.sum().rename("m_ios")
    ma = cw[cw.os == "Android"].dropna(subset=["store"]).groupby(["store", "week"]).spend.sum().rename("m_and")
    ti = tj[tj.os == "iOS"].dropna(subset=["store"]).groupby(["store", "week"]).spend.sum().rename("t_ios")
    ta = tj[tj.os == "Android"].dropna(subset=["store"]).groupby(["store", "week"]).spend.sum().rename("t_and")
    P = ap.set_index(["store", "week"]).join([mi, ma, ti, ta]).fillna(0).reset_index().sort_values(["store", "week"])
    top40 = P.groupby("store")[["m_ios", "t_ios"]].sum().sum(axis=1).sort_values(ascending=False).head(40).index
    P40 = P[P.store.isin(top40)].copy()

    def est(cols, dec=0.5, lo=None, boot=0):
        Q = P40.copy()
        for c in cols:
            Q["A_" + c] = Q.groupby("store")[c].transform(lambda v: pd.Series(adstock(v.values, dec), index=v.index))
        if lo:
            Q = Q[Q.week >= lo]
        b = two_way(Q, "proceeds", ["A_" + c for c in cols]) / (1 - dec)
        se = np.full(len(cols), np.nan)
        if boot:
            rng = np.random.default_rng(7)
            stores = Q.store.unique()
            bs = []
            for _ in range(boot):
                sel = rng.choice(stores, len(stores), replace=True)
                parts = [Q[Q.store == s].assign(store=f"{s}#{i}") for i, s in enumerate(sel)]
                bs.append(two_way(pd.concat(parts), "proceeds", ["A_" + c for c in cols]) / (1 - dec))
            se = np.array(bs).std(axis=0)
        return b, se

    rows = []
    b, se = est(["m_ios", "t_ios"], 0.5, boot=150)
    main_b, main_se = b, se
    rows.append(dict(spec="Main: country + week fixed effects, 50% weekly carry-over, all weeks", meta=b[0], meta_se=se[0], tiktok=b[1], tiktok_se=se[1]))
    for dec in (0.0, 0.3, 0.7):
        b, _ = est(["m_ios", "t_ios"], dec)
        rows.append(dict(spec=f"Same, {int(dec * 100)}% carry-over", meta=b[0], tiktok=b[1]))
    b, _ = est(["m_ios", "t_ios"], 0.5, lo=SINGULAR_START)
    rows.append(dict(spec="Same, Singular weeks only", meta=b[0], tiktok=b[1]))
    b, _ = est(["m_ios", "t_ios", "m_and", "t_and"], 0.5)
    rows.append(dict(spec="Same, with Android spend added (should be about 0)", meta=b[0], tiktok=b[1], meta_and=b[2], tiktok_and=b[3]))
    # cross-country: change in weekly proceeds vs change in weekly spend, before vs now
    pre = P[P.week <= PRE_END].groupby("store")[["proceeds", "m_ios", "t_ios"]].mean()
    now = P[P.week.isin(NOW)].groupby("store")[["proceeds", "m_ios", "t_ios"]].mean()
    vol = (pre.m_ios + now.m_ios + pre.t_ios + now.t_ios)
    D = (now - pre)[vol > 200].dropna()
    w = np.sqrt(vol.reindex(D.index)).values
    bx = np.linalg.lstsq(np.column_stack([np.ones(len(D)), D.m_ios, D.t_ios]) * w[:, None], D.proceeds.values * w, rcond=None)[0]
    rows.append(dict(spec=f"Cross-country: change in weekly spend vs proceeds, before vs last {NOW_N} weeks ({len(D)} countries)", meta=bx[1], tiktok=bx[2]))
    ST = pd.DataFrame(rows)
    ST["key"] = [f"s{i}" for i in range(len(ST))]
    ST.to_csv(os.path.join(OUT, "ch_store.csv"), index=False, float_format="%.4f")

    # ================= countries =================================================
    def per(df, weeks, s, r, o):
        x = df[df.week.isin(weeks) & (df.os == o)]
        return x.groupby("country")[s].sum() / len(weeks), x.groupby("country")[r].sum() / len(weeks)
    pre_w = [w for w in fw if w <= PRE_END]
    C = pd.DataFrame()
    for k, wks in (("pre", pre_w), ("now", NOW)):
        for lab, df in (("meta", cw), ("tt", tj)):
            for o, ok in (("iOS", "ios"), ("Android", "and")):
                s_, r_ = per(df, wks, "spend", "rev", o)
                C[f"{lab}_{ok}_spend_{k}"], C[f"{lab}_{ok}_rev_{k}"] = s_, r_
    C = C.fillna(0)
    for k in ("pre", "now"):
        for lab in ("meta", "tt"):
            for ok in ("ios", "and"):
                tot_s = C[f"{lab}_{ok}_spend_{k}"].sum()
                tot_r = C[f"{lab}_{ok}_rev_{k}"].sum()
                C[f"{lab}_{ok}_idx_{k}"] = (C[f"{lab}_{ok}_rev_{k}"] / C[f"{lab}_{ok}_spend_{k}"].replace(0, np.nan)) / (tot_r / tot_s)
        C[f"paid_{k}"] = C[[f"{lab}_{ok}_spend_{k}" for lab in ("meta", "tt") for ok in ("ios", "and")]].sum(axis=1)
        C[f"tt_share_{k}"] = (C[f"tt_ios_spend_{k}"] + C[f"tt_and_spend_{k}"]) / C[f"paid_{k}"].replace(0, np.nan)
    store_of = pd.concat([cw[["country", "store"]], tj[["country", "store"]]]).dropna().drop_duplicates("country").set_index("country").store
    C["store"] = C.index.map(store_of)
    apk = {k: ap[ap.week.isin(wks)].groupby("store").proceeds.sum() / len(wks) for k, wks in (("pre", pre_w), ("now", NOW))}
    C["proceeds_pre"], C["proceeds_now"] = C.store.map(apk["pre"]), C.store.map(apk["now"])
    C["d_proceeds"] = C.proceeds_now - C.proceeds_pre
    C["d_meta_ios"] = C.meta_ios_spend_now - C.meta_ios_spend_pre
    C["d_tt_ios"] = C.tt_ios_spend_now - C.tt_ios_spend_pre
    C.index.name = "country"
    C = C.sort_values("paid_now", ascending=False)
    keep = ["store", "paid_pre", "paid_now", "tt_share_pre", "tt_share_now", "meta_ios_spend_pre", "meta_ios_spend_now",
            "tt_ios_spend_pre", "tt_ios_spend_now", "tt_and_spend_now", "meta_ios_idx_now", "tt_ios_idx_now",
            "proceeds_pre", "proceeds_now", "d_meta_ios", "d_tt_ios", "d_proceeds"]
    C[keep].head(30).reset_index().to_csv(os.path.join(OUT, "ch_country.csv"), index=False, float_format="%.4f")

    # ================= TikTok ad groups ==========================================
    tw = tt[tt.week.isin(fw) & tt.live]
    A = tw.groupby(["adgroup_id", "week"]).agg(spend=("spend", "sum"), rev=("rev", "sum")).reset_index()
    meta_ag = tw.sort_values("week").groupby("adgroup_id")[["name", "os", "geo", "lang", "persona", "subangle", "objective", "version", "migration", "campaign"]].last()
    A = A.join(meta_ag[["os"]], on="adgroup_id")
    acc = tw[tw.os.isin(["iOS", "Android"])].groupby(["week", "os"]).agg(S=("spend", "sum"), R=("rev", "sum"))
    acc["ar"] = acc.R / acc.S
    A = A.join(acc["ar"], on=["week", "os"])
    A["roas"] = A.rev / A.spend.replace(0, np.nan)
    A["rel"] = A.roas / A.ar
    shown = fw[-WEEKS_SHOWN:]
    L, Lp = fw[-1], fw[-2]
    G = meta_ag.copy()
    piv_s = A.pivot_table(index="adgroup_id", columns="week", values="spend", aggfunc="sum").reindex(columns=fw).fillna(0)
    piv_r = A.pivot_table(index="adgroup_id", columns="week", values="rel", aggfunc="mean").reindex(columns=fw)
    piv_ro = A.pivot_table(index="adgroup_id", columns="week", values="roas", aggfunc="mean").reindex(columns=fw)
    G["spend_last"] = piv_s[L]
    G["roas_last"] = piv_ro[L]
    G["rel_last"] = piv_r[L]
    G["spend_prev"] = piv_s[Lp]
    A4 = A[A.week.isin(fw[-4:])].assign(exp=lambda x: x.spend * x.ar).groupby("adgroup_id")[["rev", "exp"]].sum()
    G["rel_4w"] = (A4.rev / A4.exp.replace(0, np.nan)).reindex(G.index)
    G["peak"] = piv_s.max(axis=1)
    G["peak_week"] = piv_s.idxmax(axis=1)
    G["first_week"] = piv_s.apply(lambda r: r[r > 0].index.min(), axis=1)
    G["last_week"] = piv_s.apply(lambda r: r[r > 0].index.max(), axis=1)
    G["total"] = piv_s.sum(axis=1)
    G["active"] = G.spend_last > 0
    us = tw[tw.country == "US"].groupby("adgroup_id").spend.sum()
    G["us_share"] = us.reindex(G.index).fillna(0) / G.total.replace(0, np.nan)
    topc = tw[tw.week.isin(fw[-4:])].groupby(["adgroup_id", "country"]).spend.sum().reset_index().sort_values("spend", ascending=False).drop_duplicates("adgroup_id").set_index("adgroup_id")
    G["top_country"] = topc.country.reindex(G.index)
    for w in shown:
        G[f"s_{w}"] = piv_s[w].round(2)
        G[f"x_{w}"] = piv_r[w].round(3)
    G = G[(G.total >= 500)].copy()
    G["status"] = np.select([~G.active, G.rel_4w >= 1.0, G.rel_4w >= 0.85], ["⚫ Off", "✅ At/above avg", "🟠 85–100%"], "🆘 Under 85%")
    G = G.sort_values(["active", "spend_last", "peak"], ascending=[False, False, False]).reset_index()
    G["key"] = "t:" + G.adgroup_id.astype(str)
    G.to_csv(os.path.join(OUT, "ch_adgroups.csv"), index=False, float_format="%.4f")

    # ================= facts ======================================================
    def roas(lab, k, e, ghost=False):
        x = W[W.era == e]
        g = x[f"tt_{k}_ghost"].sum() if ghost else 0
        return (x[f"{lab}_{k}_rev"].sum() + g) / x[f"{lab}_{k}_spend"].sum()
    gx = tt[tt.week.isin(fw) & (tt.week >= SINGULAR_START) & ~tt.live & (tt.rev_all > 0)]
    lifetime = tt.groupby("adgroup_id").spend.sum()
    gags = gx.groupby("adgroup_id").rev_all.sum()
    never = gags[lifetime.reindex(gags.index).fillna(0) < 1]
    gap = W[(W.week >= TIKTOK_MMP_START) & (W.tt_and_spend > 1000) & (W.tt_and_roas < 0.2)].week
    usw = P[P.store == "United States"].set_index("week")
    jun, sep = [w for w in fw if "2026-06-01" <= w <= "2026-06-29"], [w for w in fw if "2026-09-07" <= w <= "2026-09-28"]
    # credit shift test: did Meta lose more credit where TikTok is big?
    sh = []
    for o in ("iOS",):
        a = cw[cw.os == o].assign(e=cw.week.map(era)).groupby(["country", "e"]).agg(s=("spend", "sum"), r=("rev", "sum")).unstack("e")
        b = tj[tj.os == o].assign(e=tj.week.map(era)).groupby(["country", "e"]).spend.sum().unstack("e").reindex(a.index).fillna(0)
        D2 = pd.DataFrame({"ratio": (a.r.singular / a.s.singular) / (a.r.pre / a.s.pre), "ms": a.s.pre + a.s.singular,
                           "tts": (b.get("pre", 0) + b.get("singular", 0)) / (b.get("pre", 0) + b.get("singular", 0) + a.s.pre + a.s.singular)})
        D2 = D2[(a.s.pre > 15000) & (a.s.singular > 15000)].dropna()
        hi, lo_ = D2[D2.tts >= 0.15], D2[D2.tts < 0.05]
        gm = lambda x: np.exp(np.average(np.log(x.ratio), weights=np.sqrt(x.ms))) if len(x) else np.nan
        sh = [("credit_ratio_tt_high", gm(hi), f"Meta iOS ROAS Singular ÷ before, countries where TikTok is 15%+ of iOS spend ({len(hi)})"),
              ("credit_ratio_tt_low", gm(lo_), f"Same, countries where TikTok is under 5% ({len(lo_)})")]
    F = [
        ("tt_spend_wk_pre", W[W.era == "pre"][["tt_ios_spend", "tt_and_spend"]].sum(axis=1).mean(), "TikTok spend per week, before (Dec – mid Feb)"),
        ("tt_spend_wk_now", W[W.week.isin(NOW)][["tt_ios_spend", "tt_and_spend"]].sum(axis=1).mean(), f"TikTok spend per week, last {NOW_N} weeks"),
        ("tt_spend_wk_low", W[(W.week >= "2026-05-04") & (W.week <= "2026-08-10")][["tt_ios_spend", "tt_and_spend"]].sum(axis=1).mean(), "TikTok spend per week, May – mid Aug"),
        ("tt_share_pre", W[W.era == "pre"].pipe(lambda x: (x.tt_ios_spend + x.tt_and_spend).sum() / x.paid_spend.sum()), "TikTok share of paid spend, before"),
        ("tt_share_now", W[W.week.isin(NOW)].pipe(lambda x: (x.tt_ios_spend + x.tt_and_spend).sum() / x.paid_spend.sum()), f"TikTok share of paid spend, last {NOW_N} weeks"),
        ("tt_ios_share_of_tt", tj[tj.os == "iOS"].spend.sum() / tj.spend.sum(), "iOS share of TikTok spend"),
        ("tt_general_share", tj[tj.persona == "General"].spend.sum() / tj.spend.sum(), "Share of TikTok spend in General (broad) ad groups"),
        ("tt_ios_roas_pre", roas("tt", "ios", "pre", True), "TikTok-reported iOS ROAS, before"),
        ("tt_ios_roas_sing_reported", roas("tt", "ios", "singular", True), "TikTok-reported iOS ROAS, Singular era (all value)"),
        ("tt_ios_roas_sing", roas("tt", "ios", "singular"), "TikTok iOS ROAS on live ad groups only, Singular era"),
        ("tt_and_roas_pre", roas("tt", "and", "pre", True), "TikTok-reported Android ROAS, before"),
        ("tt_and_roas_sing_reported", roas("tt", "and", "singular", True), "TikTok-reported Android ROAS, Singular era (all value)"),
        ("tt_and_roas_sing", roas("tt", "and", "singular"), "TikTok Android ROAS on live ad groups only, Singular era"),
        ("tt_ghost_share_ios", W[W.era == "singular"].pipe(lambda x: x.tt_ios_ghost.sum() / (x.tt_ios_ghost.sum() + x.tt_ios_rev.sum())), "Share of TikTok iOS value on ad groups not spending that week, Singular era"),
        ("tt_ghost_share_and", W[W.era == "singular"].pipe(lambda x: x.tt_and_ghost.sum() / (x.tt_and_ghost.sum() + x.tt_and_rev.sum())), "Share of TikTok Android value on ad groups not spending that week, Singular era"),
        ("tt_ghost_share_pre", W[W.era == "pre"].pipe(lambda x: (x.tt_ios_ghost.sum() + x.tt_and_ghost.sum()) / (x.tt_ios_ghost.sum() + x.tt_and_ghost.sum() + x.tt_ios_rev.sum() + x.tt_and_rev.sum())), "Same, both OS, before the migration"),
        ("tt_ghost_wk_now", W[W.week.isin(NOW)][["tt_ios_ghost", "tt_and_ghost"]].sum(axis=1).mean(), f"TikTok value per week on ad groups not spending, last {NOW_N} weeks"),
        ("tt_ghost_adgroups", len(gags), "Ad groups credited with value in weeks they didn't spend, Singular era"),
        ("tt_ghost_never_spent", len(never), "Of those, ad groups with no spend at all since Dec 2025"),
        ("tt_ghost_never_value", never.sum(), "Value credited to them, Singular era"),
        ("meta_ios_roas_sing", roas("meta", "ios", "singular"), "Meta-credited iOS ROAS, Singular era"),
        ("meta_and_roas_sing", roas("meta", "and", "singular"), "Meta-credited Android ROAS, Singular era"),
        ("store_per_meta_ios", main_b[0], "App Store proceeds per Meta iOS $ (main model)"),
        ("store_per_meta_ios_se", main_se[0], "Its bootstrap standard error (by country)"),
        ("store_per_tt_ios", main_b[1], "App Store proceeds per TikTok iOS $ (main model)"),
        ("store_per_tt_ios_se", main_se[1], "Its bootstrap standard error (by country)"),
        ("store_per_tt_ios_hi", ST.tiktok.max(), "Highest TikTok estimate across model specs"),
        ("store_per_tt_ios_lo", ST.tiktok.min(), "Lowest TikTok estimate across model specs"),
        ("tt_android_gap_weeks", len(gap), "Weeks after the TikTok MMP migration with Android spend but almost no purchases reported"),
        ("tt_android_gap_from", np.nan, gap.min() if len(gap) else ""),
        ("tt_android_gap_to", np.nan, gap.max() if len(gap) else ""),
        ("tt_mmp_start", np.nan, TIKTOK_MMP_START),
        ("us_store_jun", usw.loc[jun].proceeds.mean(), "US App Store proceeds per week, June"),
        ("us_store_sep", usw.loc[sep].proceeds.mean(), "US App Store proceeds per week, September"),
        ("us_meta_ios_jun", usw.loc[jun].m_ios.mean(), "Meta US iOS spend per week, June"),
        ("us_meta_ios_sep", usw.loc[sep].m_ios.mean(), "Meta US iOS spend per week, September"),
        ("us_tt_ios_jun", usw.loc[jun].t_ios.mean(), "TikTok US iOS spend per week, June"),
        ("us_tt_ios_sep", usw.loc[sep].t_ios.mean(), "TikTok US iOS spend per week, September"),
        ("tt_adgroups_live", int(G.active.sum()), "TikTok ad groups with spend last week"),
    ] + sh
    FD = pd.DataFrame(F, columns=["fact", "value", "label"])
    FD.to_csv(os.path.join(OUT, "ch_facts.csv"), index=False, float_format="%.4f")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 90)
    print(ST.round(3).to_string())
    print(FD.round(3).to_string())
    print(C[keep].head(12).round(2).to_string())
    print(G[["name", "os", "status", "spend_last", "roas_last", "rel_4w", "peak", "top_country"]].head(15).round(2).to_string())


if __name__ == "__main__":
    main()
