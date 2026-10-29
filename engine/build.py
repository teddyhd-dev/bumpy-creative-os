"""Bumpy ads engine — adset-level build (spec v0.6.x).

Reads every adset export in data/raw/, applies the spec rules, and writes the
datasets the dashboard reads into output/data/.

Run:  python3 engine/build.py
"""
from __future__ import annotations

import glob
import os
import re

import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from settings import BARS, SINGULAR_START, bar, era, ruler  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "output", "data")

# ---- thresholds (spec §15) -------------------------------------------------
# The ROAS bar depends on the ruler (Meta's own attribution before the Singular switch,
# Singular after): see engine/settings.py. GREEN / AMBER here are the CURRENT bar.
GREEN = BARS["singular"]["green"]
AMBER = BARS["singular"]["amber"]
ALERT_FLOOR_SHARE = 0.01          # adset spend >= 1% of account spend that week
SHRINK_FROM_PEAK = 0.30           # >= 30% below 6-month peak
PEAK_WINDOW_WEEKS = 26            # "6 months"
MARKET_DROP = 0.15                # ROAS down >= 15% ...
MARKET_SHARE = 0.50               # ... in > 50% of alert-floor spend
LEADING_DROP = 0.20               # IPM or hook rate down >= 20% vs prior 4-week avg
SCALING_UP = 0.15                 # spend up >= 15% vs 2 weeks ago (budget proxy)
SPEND_STEP = 0.20                 # spend change marker (budget proxy)

JUDGED_OBJECTIVES = {"Purchase", "Sales"}

CANONICAL = {
    "GringoMaleLover", "AsianFemaleLover", "LatinaFemaleLover", "SlavicFemaleLover",
    "KoreanMaleCultureLover", "IndianFemaleDreamingForAsianMale", "MuslimMatchWorldwide",
    "ChristianMatchWorldwide", "PassportBro", "GirlWantsToRelocate", "MatureDating",
    "InterracialDatingSeekers", "SingleMom", "InternationalFriendFinder", "NewLanguageLearner",
    "EgoBoostForIndianBoy", "RichHusbandFinder", "LGBTQ", "LocalDatingFatigue",
    "CelebrityCrushLookalikeLover", "General",
}
ISO_LANG = {"EN", "ES", "PT", "TH", "ID", "TR", "RU", "JA", "KO", "ZH", "FR", "DE", "IT",
            "NL", "PL", "UK", "VI", "AR", "NO", "TX", "All"}

# Legacy adset names → persona (by judgment; spec §18). First match wins.
LEGACY_PERSONA = [
    (r"passport girl", "GirlWantsToRelocate"),
    (r"passport bro", "PassportBro"),
    (r"asian dating|/ asian\b|asian lp|\basian$", "AsianFemaleLover"),
    (r"muslim", "MuslimMatchWorldwide"),
    (r"christian", "ChristianMatchWorldwide"),
    (r"30-60|middle aged", "MatureDating"),
    (r"\bblk\b", "InterracialDatingSeekers"),
    (r"indian boy", "EgoBoostForIndianBoy"),
    (r"latina", "LatinaFemaleLover"),
    (r"lgbtq", "LGBTQ"),
    (r"single mom", "SingleMom"),
    (r"gringo lover", "GringoMaleLover"),
    (r"international friend|friends v1", "IntlFriendFinder"),
    (r"woman marriage|wedding", "RichHusbandFinder"),
    (r"slavic", "SlavicFemaleLover"),
    (r"churn raya", "CelebrityCrushLookalikeLover"),
    (r"beach girl", "BeachGirl"),
    (r"middle eastern", "MiddleEastern"),
    (r"plus size", "PlusSizeWomen"),
    (r"short kings", "ShortKings"),
    (r"divorcee", "Divorcee"),
]
LEGACY_LANG = {"ENG": "EN", "ES": "ES", "PT": "PT", "TH": "TH", "ID": "ID", "JP": "JA",
               "KR": "KO", "RU": "RU", "PL": "PL", "UA": "UK", "TR": "TR", "DE": "DE",
               "FR": "FR", "CH": "ZH", "NL": "NL", "NO": "NO", "VN": "VI", "IT": "IT", "IN": "EN"}


def parse_name(name: str) -> dict:
    parts = [p.strip() for p in name.split("/")]
    if parts[0] == "AS" and len(parts) == 12:
        persona = re.sub(r"\s+", "", parts[2])
        return dict(version="v8", persona=persona, subangle=parts[3], os=parts[4], geo=parts[5],
                    lang=parts[6], gender=parts[7], objective=parts[8], bid=parts[9],
                    modifier=parts[10], launch=parts[11])
    low = name.lower()
    persona = "General"
    for pat, p in LEGACY_PERSONA:
        if re.search(pat, low):
            persona = p
            break
    os_ = next((o for o in ("iOS", "Android", "Web") if re.search(rf"\b{o}\b", name, re.I)), "?")
    m = re.search(r"\b([A-Za-z]+)-(ENG|ES|PT|TH|ID|JP|KR|RU|PL|UA|TR|DE|FR|CH|NL|NO|VN|IT|IN)\b", name)
    lang = LEGACY_LANG.get(m.group(2), m.group(2)) if m else "?"
    geo = m.group(1).upper() if m else "?"
    if re.search(r"post engagement", low):
        objective = "Engagement"
    elif re.search(r"sign ?up|registration", low):
        objective = "SignUp"
    elif re.search(r"\binstall\b", low):
        objective = "Install"
    elif re.search(r"\bsales\b", low):
        objective = "Sales"
    else:
        objective = "Purchase"
    return dict(version="legacy", persona=persona, subangle="", os=os_, geo=geo, lang=lang,
                gender="", objective=objective, bid="", modifier="", launch="")


def safe_div(a, b):
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.where(b > 0, a / b, np.nan)
    return r


def load_raw() -> pd.DataFrame:
    frames = []
    for path in sorted(glob.glob(os.path.join(RAW, "adset", "adset_*.csv"))):
        f = pd.read_csv(path, encoding="utf-8-sig")
        f["_file"] = os.path.basename(path)
        frames.append(f)
    df = pd.concat(frames, ignore_index=True)
    df = df.rename(columns={
        "Ad set name": "name", "Ad set ID": "adset_id", "Amount spent (USD)": "spend",
        "Purchase ROAS (return on ad spend)": "roas_meta",
        "In-app purchases conversion value": "value_inapp", "App installs": "installs",
        "Link clicks": "clicks", "Purchases": "purchases", "Impressions": "impressions",
        "Frequency": "frequency", "Hook Rate": "hook_rate", "Reporting starts": "week",
    })
    # newer uploads overwrite older ones for the same adset-week
    df = df.sort_values("_file").drop_duplicates(["adset_id", "week"], keep="last")
    for c in ["spend", "roas_meta", "value_inapp", "installs", "clicks", "purchases",
              "impressions", "frequency", "hook_rate"]:
        if c not in df:
            df[c] = np.nan
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["adset_id"] = df["adset_id"].astype(str)
    # Revenue: Purchase ROAS × spend covers app AND web purchases; the in-app value
    # column misses web purchases, so it is only a cross-check.
    df["rev"] = (df["roas_meta"] * df["spend"]).fillna(0.0)
    df[["installs", "clicks", "purchases", "impressions"]] = (
        df[["installs", "clicks", "purchases", "impressions"]].fillna(0))
    return df


def zone(r, week=None, os_=None):
    if pd.isna(r):
        return "none"
    b = bar(week, os_) if week is not None else BARS["singular"]
    if r >= b["green"]:
        return "green"
    if r >= b["amber"]:
        return "amber"
    return "critical"


def build():
    os.makedirs(OUT, exist_ok=True)
    df = load_raw()
    parsed = df["name"].map(parse_name).apply(pd.Series)
    df = pd.concat([df, parsed], axis=1)
    weeks = sorted(df["week"].unique())
    L = weeks[-1]
    widx = {w: i for i, w in enumerate(weeks)}

    # ---- weekly rows per adset --------------------------------------------
    df["roas"] = safe_div(df["rev"], df["spend"])
    df["ipm"] = safe_div(df["installs"] * 1000, df["impressions"])
    df["cpm"] = safe_div(df["spend"] * 1000, df["impressions"])
    df["c2i"] = safe_div(df["installs"], df["clicks"])
    df["i2p"] = safe_div(df["purchases"], df["installs"])
    df["bar_green"] = [bar(w, o)["green"] for w, o in zip(df["week"], df["os"])]
    df["bar_amber"] = [bar(w, o)["amber"] for w, o in zip(df["week"], df["os"])]
    df["zone"] = [zone(r, w, o) for r, w, o in zip(df["roas"], df["week"], df["os"])]
    df["judged"] = df["objective"].isin(JUDGED_OBJECTIVES)
    df.loc[~df["judged"], "zone"] = "other"

    # ---- account weekly ------------------------------------------------------
    acc = df.groupby("week").agg(spend=("spend", "sum"), rev=("rev", "sum"),
                                 impressions=("impressions", "sum"), installs=("installs", "sum"),
                                 clicks=("clicks", "sum"), purchases=("purchases", "sum"),
                                 adsets=("adset_id", "nunique")).reindex(weeks)
    for z in ["green", "amber", "critical", "other"]:
        acc[f"spend_{z}"] = df[df["zone"] == z].groupby("week")["spend"].sum().reindex(weeks).fillna(0)
    acc["roas"] = safe_div(acc["rev"], acc["spend"])
    acc["ipm"] = safe_div(acc["installs"] * 1000, acc["impressions"])
    acc["cpm"] = safe_div(acc["spend"] * 1000, acc["impressions"])
    acc["ctr"] = safe_div(acc["clicks"], acc["impressions"])
    acc["c2i"] = safe_div(acc["installs"], acc["clicks"])
    acc["i2p"] = safe_div(acc["purchases"], acc["installs"])
    acc["rpp"] = safe_div(acc["rev"], acc["purchases"])
    acc["cpi"] = safe_div(acc["spend"], acc["installs"])
    acc["green_share"] = safe_div(acc["spend_green"], acc["spend"])
    acc["floor"] = acc["spend"] * ALERT_FLOOR_SHARE
    df["floor"] = df["week"].map(acc["floor"])
    df["above_floor"] = df["spend"] >= df["floor"]
    acc["critical_adsets"] = (df[(df["zone"] == "critical") & df["above_floor"]]
                              .groupby("week")["adset_id"].nunique().reindex(weeks).fillna(0).astype(int))
    acc["leaking"] = (df[df["judged"]].assign(l=lambda d: d["spend"] * (d["bar_green"] - d["roas"]).clip(lower=0))
                      .groupby("week")["l"].sum().reindex(weeks).fillna(0))

    # market day: > 50% of alert-floor spend in adsets whose ROAS fell >= 15% w/w
    piv_roas = df.pivot_table(index="adset_id", columns="week", values="roas")
    piv_sp = df.pivot_table(index="adset_id", columns="week", values="spend", aggfunc="sum")
    piv_fl = df.pivot_table(index="adset_id", columns="week", values="above_floor", aggfunc="max")
    md_share = []
    for i, w in enumerate(weeks):
        if i == 0:
            md_share.append(np.nan)
            continue
        p = weeks[i - 1]
        base = piv_fl[w].fillna(False).astype(bool) & (piv_roas[p] > 0) & piv_roas[w].notna()
        tot = piv_sp.loc[base, w].sum()
        fall = piv_sp.loc[base & (piv_roas[w] <= piv_roas[p] * (1 - MARKET_DROP)), w].sum()
        md_share.append(fall / tot if tot else np.nan)
    acc["falling_share"] = md_share
    acc["market_day"] = acc["falling_share"] > MARKET_SHARE
    acc["ipm_change"] = acc["ipm"].pct_change()
    acc["roas_change"] = acc["roas"].pct_change()
    acc["spend_change"] = acc["spend"].pct_change()
    acc["roas_delta"] = acc["roas"].diff()
    acc["green_share_delta"] = acc["green_share"].diff()
    acc["critical_delta"] = acc["critical_adsets"].diff()
    acc["leaking_change"] = acc["leaking"].pct_change()
    jd = df[df["judged"]]
    for o, lab in (("iOS", "ios"), ("Android", "android")):
        x = jd[jd["os"] == o].groupby("week")[["spend", "rev"]].sum().reindex(weeks)
        acc[f"roas_{lab}"] = safe_div(x["rev"], x["spend"])
    acc["era"] = [era(w) for w in acc.index]
    acc["ruler_ios"] = [ruler(w, "iOS") for w in acc.index]
    acc["ruler_android"] = [ruler(w, "Android") for w in acc.index]
    acc["bar_green"] = [bar(w)["green"] for w in acc.index]
    acc["bar_amber"] = [bar(w)["amber"] for w in acc.index]
    acc["is_latest"] = False
    acc.loc[acc.index[-1], "is_latest"] = True
    acc = acc.reset_index().rename(columns={"index": "week"})
    acc["week_label"] = acc["week"].map(lambda w: pd.Timestamp(w).strftime("%d %b"))

    # ---- adset summary -----------------------------------------------------------
    meta_cols = ["name", "version", "persona", "subangle", "os", "geo", "lang", "gender",
                 "objective", "bid", "modifier", "launch"]
    meta = df.sort_values("week").groupby("adset_id")[meta_cols].last()
    rows = []
    recent = weeks[-PEAK_WINDOW_WEEKS:]
    for aid, g in df.groupby("adset_id"):
        g = g.set_index("week").reindex(weeks)
        sp = g["spend"].fillna(0)
        ro = g["roas"]
        cur, prev, prev2 = sp[L], sp[weeks[-2]], sp[weeks[-3]]
        r_cur, r_prev = ro[L], ro[weeks[-2]]
        m = meta.loc[aid]
        judged = m["objective"] in JUDGED_OBJECTIVES
        bL = bar(L, m["os"])                      # the bar that applies to the latest week
        G_, A_ = bL["green"], bL["amber"]
        active = cur > 0
        floor_L = acc.set_index("week").loc[L, "floor"]
        above = cur >= floor_L
        sp_recent = sp[recent]
        peak = sp_recent.max()
        peak_week = sp_recent.idxmax() if peak > 0 else None
        peak_roas = ro[peak_week] if peak_week else np.nan
        alltime_peak_week = sp.idxmax()
        active_weeks = int((sp > 0).sum())
        first_week = sp[sp > 0].index.min()
        last_week = sp[sp > 0].index.max()

        # leading signal: IPM or hook rate down >= 20% vs average of previous 4 spending weeks
        lead = []
        for col, label in [("ipm", "IPM"), ("hook_rate", "hook rate")]:
            hist = g[col][weeks[-5:-1]][sp[weeks[-5:-1]] > 0].dropna()
            if active and len(hist) >= 2 and pd.notna(g[col][L]) and hist.mean() > 0:
                ch = g[col][L] / hist.mean() - 1
                if ch <= -LEADING_DROP:
                    lead.append(f"{label} {ch:+.0%} vs 4-wk avg")

        # low ceiling: best rolling 4-week ROAS (last 26 weeks) at alert-floor spend never reached
        # the bar of its own ruler, AND never matched the account over the same weeks
        fl = acc.set_index("week")["floor"]
        acc_sp = acc.set_index("week")["spend"]
        acc_rv = acc.set_index("week")["rev"]
        best4, best4_rel = np.nan, np.nan
        for i in range(len(recent) - 3):
            win = recent[i:i + 4]
            s, r = sp[win].sum(), g["rev"][win].fillna(0).sum()
            if s >= fl[win].sum() and s > 0:
                rel = (r / s) / (acc_rv[win].sum() / acc_sp[win].sum())
                vb = (r / s) / bar(win[-1], m["os"])["green"]   # in units of that window's green bar
                best4 = max(best4, vb) if pd.notna(best4) else vb
                best4_rel = max(best4_rel, rel) if pd.notna(best4_rel) else rel
        # judged only where there was a real chance at scale (a 4-week window at alert-floor spend)
        low_ceiling = (judged and pd.notna(best4) and best4 < 1.0
                       and pd.notna(best4_rel) and best4_rel < 1.0)

        cuts = (sp[weeks[-1]] <= sp[weeks[-2]] * (1 - 0.10)) and (sp[weeks[-2]] <= sp[weeks[-3]] * (1 - 0.10))
        shrinking = active and peak > 0 and (cur <= peak * (1 - SHRINK_FROM_PEAK) or cuts)

        if not judged:
            status, sev, why = ("⚫ Off" if not active else "▫️ Not judged"), (9 if not active else 8), \
                f"{m['objective']} objective, not judged on ROAS"
        elif not active:
            status, sev = "⚫ Off", 9
            if pd.isna(last_week):
                why = "Never spent"
            else:
                why = f"Last spend {pd.Timestamp(last_week).strftime('%d %b')}; peak ${sp.max():,.0f}/wk ({pd.Timestamp(alltime_peak_week).strftime('%d %b')})"
        elif r_cur < A_ or pd.isna(r_cur):
            status, sev = "🆘 Critical", 1
            fmt = ".3f" if pd.notna(r_cur) and round(r_cur, 2) == round(A_, 2) else ".2f"
            why = f"ROAS {r_cur:{fmt}}" + (f" (prev {r_prev:.2f})" if pd.notna(r_prev) else "") + f", under {A_:.2f}"
        elif r_cur < G_ and pd.notna(r_prev) and r_cur < r_prev:
            status, sev = "🔻 Falling", 2
            why = f"Under {G_:.2f} and falling: ROAS {r_cur:.2f} from {r_prev:.2f}"
        elif r_cur < G_:
            status, sev = "🟠 Amber", 4
            why = f"ROAS {r_cur:.2f}, under {G_:.2f}, not falling"
        elif lead:
            status, sev = "🔻 Falling", 3
            why = "Green, but " + "; ".join(lead)
        elif prev2 > 0 and cur >= prev2 * (1 + SCALING_UP):
            status, sev = "🚀 Scaling", 6
            why = f"ROAS {r_cur:.2f}, spend {cur / prev2 - 1:+.0%} vs 2 weeks ago"
        else:
            status, sev = "✅ Healthy", 7
            why = f"ROAS {r_cur:.2f}"
        if status == "🆘 Critical" and not above:
            sev = 5  # below alert floor: colour shows, no alert

        flags = []
        if shrinking:
            flags.append("📉")
        if low_ceiling and active:
            flags.append("🧱")
        rows.append(dict(
            adset_id=aid, name=m["name"], version=m["version"], persona=m["persona"], judged=judged,
            subangle=m["subangle"], os=m["os"], lang=m["lang"], gender=m["gender"],
            objective=m["objective"], modifier=m["modifier"], launch=m["launch"],
            status=status, severity=sev, why=why, alert=bool(active and above and sev <= 3),
            spend_last=round(cur, 2), roas_last=r_cur, spend_prev=round(prev, 2), roas_prev=r_prev,
            leaking=round(cur * max(0.0, G_ - r_cur), 2) if active and judged and pd.notna(r_cur) else 0.0,
            peak_6m=round(peak, 2), peak_week=peak_week or "", peak_roas=peak_roas,
            peak_all=round(sp.max(), 2), peak_all_week=alltime_peak_week if sp.max() > 0 else "",
            scale_lost=round(max(0.0, peak - cur), 2),
            best4_vs_bar=best4, best4_vs_account=best4_rel, flags=" ".join(flags), shrinking=shrinking,
            low_ceiling=bool(low_ceiling), active=bool(active), active_weeks=active_weeks,
            first_week=first_week, last_week=last_week,
            ipm_last=g["ipm"][L], c2i_last=g["c2i"][L], i2p_last=g["i2p"][L],
            cpm_last=g["cpm"][L], hook_last=g["hook_rate"][L], freq_last=g["frequency"][L],
        ))
    ad = pd.DataFrame(rows)

    # ---- grid: one row per entity, one spend + roas column per week ----------
    sp_p = df.pivot_table(index="adset_id", columns="week", values="spend", aggfunc="sum")
    rv_p = df.pivot_table(index="adset_id", columns="week", values="rev", aggfunc="sum")

    def wide(spend_frame, rev_frame):
        out = {}
        for w in weeks:
            s = spend_frame.get(w)
            r = rev_frame.get(w)
            out[f"s_{w}"] = s.round(2) if s is not None else np.nan
            out[f"r_{w}"] = (r / s.where(s > 0)).round(3) if s is not None else np.nan
        return pd.DataFrame(out)

    g_ad = wide(sp_p, rv_p).reindex(ad["adset_id"]).reset_index(drop=True)
    grid_ad = pd.concat([ad.reset_index(drop=True), g_ad], axis=1)
    grid_ad.insert(0, "level", "adset")
    grid_ad.insert(0, "key", "a:" + grid_ad["adset_id"])
    grid_ad["label"] = grid_ad["name"]

    # persona and persona × language aggregates
    def agg_level(keys, level, prefix, judged=True):
        jd = df[df["judged"] == judged]
        s = jd.pivot_table(index=keys, columns="week", values="spend", aggfunc="sum")
        r = jd.pivot_table(index=keys, columns="week", values="rev", aggfunc="sum")
        s, r = s.reindex(columns=weeks), r.reindex(columns=weeks)
        w = wide(s, r)
        w.index = s.index
        summ = ad[ad["objective"].isin(JUDGED_OBJECTIVES) == judged].groupby(keys).agg(
            spend_last=("spend_last", "sum"), leaking=("leaking", "sum"),
            scale_lost=("scale_lost", "sum"), severity=("severity", "min"),
            adsets_active=("active", "sum"), adsets_total=("adset_id", "count"),
            alerts=("alert", "sum"))
        w = w.join(summ)
        w["roas_last"] = (w[f"r_{L}"])
        w["roas_prev"] = (w[f"r_{weeks[-2]}"])
        w["peak_6m"] = s[recent].max(axis=1).round(2)
        w["peak_all"] = s.max(axis=1).round(2)
        w["peak_all_week"] = s.idxmax(axis=1)
        w["last_week"] = s.apply(lambda r: r[r > 0].index.max(), axis=1)
        w["scale_lost"] = (w["peak_6m"] - w["spend_last"]).clip(lower=0).round(2)
        w = w.reset_index()
        if isinstance(keys, list):
            w["persona"] = w[keys[0]]
            w["lang"] = w[keys[1]]
            w["label"] = w[keys[0]] + " · " + w[keys[1]]
            w["key"] = prefix + w[keys[0]] + "|" + w[keys[1]]
        else:
            w["persona"] = w[keys]
            w["label"] = w[keys]
            w["key"] = prefix + w[keys]
        w["level"] = level
        w["judged"] = judged
        # status for aggregates, same rules on aggregated ROAS
        def st(row):
            if row["spend_last"] <= 0:
                return "⚫ Off"
            rr, rp = row["roas_last"], row["roas_prev"]
            bL = bar(L)
            if pd.isna(rr) or rr < bL["amber"]:
                return "🆘 Critical"
            if rr < bL["green"] and pd.notna(rp) and rr < rp:
                return "🔻 Falling"
            if rr < bL["green"]:
                return "🟠 Amber"
            return "✅ Healthy"
        w["status"] = w.apply(st, axis=1)
        w["active"] = w["spend_last"] > 0
        if not judged:
            w["status"] = np.where(w["active"], "▫️ Not judged", "⚫ Off")
            w["severity"] = 8
        w.loc[~w["active"], "severity"] = 9
        w["why"] = w.apply(lambda r: "Not a purchase objective, not judged on ROAS" if not judged and r["active"] else (
            f"{int(r['alerts'])} alerting · {int(r['adsets_active'])} of {int(r['adsets_total'])} adsets live"
            if r["active"] else
            f"Gone dark: last spend {pd.Timestamp(r['last_week']).strftime('%d %b')} · peak ${r['peak_all']:,.0f}/wk"
            f" ({pd.Timestamp(r['peak_all_week']).strftime('%d %b')})"), axis=1)
        return w

    def with_unjudged(keys, level, prefix):
        a = agg_level(keys, level, prefix, True)
        b = agg_level(keys, level, prefix, False)
        return pd.concat([a, b[~b["key"].isin(a["key"])]], ignore_index=True)

    grid_p = with_unjudged("persona", "persona", "p:")
    grid_pl = with_unjudged(["persona", "lang"], "perslang", "pl:")
    grid = pd.concat([grid_p, grid_pl, grid_ad], ignore_index=True, sort=False)
    week_cols = [c for c in grid.columns if c.startswith(("s_", "r_"))]
    front = ["key", "level", "label", "persona", "lang", "os", "status", "severity", "why", "flags",
             "alert", "active", "judged", "spend_last", "roas_last", "roas_prev", "leaking", "scale_lost",
             "peak_6m", "peak_week", "peak_all", "peak_all_week", "adset_id", "name", "version", "objective", "subangle", "gender",
             "modifier", "launch", "adsets_active", "adsets_total", "alerts", "low_ceiling",
             "shrinking", "best4_vs_bar", "best4_vs_account", "active_weeks", "first_week", "last_week"]
    def short(r):
        if r["level"] == "persona":
            return r["persona"]
        if r["level"] == "perslang":
            return f"{r['persona']} · {r['lang']}"
        if r.get("version") == "v8":
            bits = [r["persona"], r["subangle"], r["os"], r["lang"]]
            if r["gender"] and r["gender"] != "BothGender":
                bits.append(r["gender"])
            if r["modifier"] and r["modifier"] != "Normal":
                bits.append(r["modifier"])
            bits.append(str(r["launch"]))
            return " · ".join(str(b) for b in bits if b)
        return r["name"]

    grid["short"] = grid.apply(short, axis=1)
    front.insert(3, "short")
    grid = grid[[c for c in front if c in grid.columns] + week_cols]

    # ---- weekly long table (dossier charts), every level --------------------
    df["hook_x_imp"] = df["hook_rate"] * df["impressions"]
    df["key_adset"] = "a:" + df["adset_id"]
    df["key_persona"] = "p:" + df["persona"]
    df["key_perslang"] = "pl:" + df["persona"] + "|" + df["lang"]
    parts_w = []
    base_cols = ["spend", "rev", "impressions", "installs", "clicks", "purchases", "hook_x_imp"]
    for kcol, judged_only in [("key_adset", False), ("key_persona", True), ("key_perslang", True)]:
        src = df[df["judged"]] if judged_only else df
        agg = src.groupby([kcol, "week"])[base_cols].sum(min_count=1).reset_index().rename(columns={kcol: "ekey"})
        if kcol == "key_adset":
            agg = agg.merge(src[["key_adset", "week", "frequency"]].rename(columns={"key_adset": "ekey"}),
                            on=["ekey", "week"], how="left")
        else:
            agg["frequency"] = np.nan
        parts_w.append(agg)
    weekly = pd.concat(parts_w, ignore_index=True)
    weekly["roas"] = safe_div(weekly["rev"], weekly["spend"])
    weekly["ipm"] = safe_div(weekly["installs"] * 1000, weekly["impressions"])
    weekly["cpm"] = safe_div(weekly["spend"] * 1000, weekly["impressions"])
    weekly["c2i"] = safe_div(weekly["installs"], weekly["clicks"])
    weekly["i2p"] = safe_div(weekly["purchases"], weekly["installs"])
    weekly["hook_rate"] = safe_div(weekly["hook_x_imp"], weekly["impressions"])
    weekly = weekly.drop(columns=["hook_x_imp"])
    weekly.insert(0, "key", weekly["ekey"] + "|" + weekly["week"])
    weekly = weekly.sort_values(["ekey", "week"])

    # ---- data checks ---------------------------------------------------------
    issues = []
    miss = df[(df["spend"] > 0) & df["value_inapp"].isna() & df["roas_meta"].notna()]
    issues.append(dict(check="Revenue column", finding="In-app value misses web purchases; revenue uses Purchase ROAS × spend instead",
                       count=int(len(miss)), spend=round(miss["spend"].sum(), 2),
                       detail=f"{miss['adset_id'].nunique()} adsets (mostly Web) had Purchase ROAS but no in-app value"))
    nr = df[(df["spend"] > 0) & df["roas_meta"].isna() & df["judged"]]
    issues.append(dict(check="No purchase value", finding="Purchase-objective rows with spend but no Purchase ROAS (counted as ROAS 0)",
                       count=int(len(nr)), spend=round(nr["spend"].sum(), 2), detail=", ".join(sorted(nr["persona"].unique())[:8])))
    leg = ad[ad["version"] == "legacy"]
    issues.append(dict(check="Legacy adset names", finding="Pre-v8 names; persona read by judgment",
                       count=int(len(leg)), spend=round(df[df["version"] == "legacy"]["spend"].sum(), 2),
                       detail=f"{int(leg['active'].sum())} still spending last week"))
    off_canon = df[(df["version"] == "v8") & ~df["persona"].isin(CANONICAL)]
    for p, s in off_canon.groupby("persona")["spend"].sum().sort_values(ascending=False).items():
        issues.append(dict(check="Persona not in taxonomy", finding=p, count=int(off_canon[off_canon.persona == p]["adset_id"].nunique()),
                           spend=round(s, 2), detail="add to the Persona Taxonomy or rename"))
    off_lang = df[(df["version"] == "v8") & ~df["lang"].isin(ISO_LANG)]
    for l_, s in off_lang.groupby("lang")["spend"].sum().sort_values(ascending=False).items():
        issues.append(dict(check="Language code not ISO 639-1", finding=l_, count=int(off_lang[off_lang.lang == l_]["adset_id"].nunique()),
                           spend=round(s, 2), detail={"JP": "JA", "KR": "KO", "CH": "ZH", "UA": "UK", "PH": "TL or TX"}.get(l_, "check")))
    dupn = df.groupby("name")["adset_id"].nunique()
    issues.append(dict(check="Same name, different adsets", finding="Names reused by more than one adset ID (kept apart by ID)",
                       count=int((dupn > 1).sum()), spend=round(df[df["name"].isin(dupn[dupn > 1].index)]["spend"].sum(), 2), detail=""))
    issues.append(dict(check="Budget column", finding="Adset export has no budget; ad and country files carry today's budget only, so past budget moves are inferred from spend",
                       count=0, spend=0.0, detail="add Ad set budget to the weekly adset export"))
    issues = pd.DataFrame(issues)
    issues.insert(0, "id", [f"i{i:02d}" for i in range(len(issues))])

    # ---- what moved account ROAS ----------------------------------------------
    # ROAS = IPM × I>P × $/purchase ÷ CPM  (IPM = CTR × C>I × 1000)
    a_idx = acc.set_index("week")
    # base = the first 8 weeks on Singular, so both windows are on the same ruler
    sing = [w_ for w_ in weeks if w_ >= SINGULAR_START]
    base_w, cur_w = sing[:8], weeks[-4:]

    def window(ws):
        t = a_idx.loc[ws, ["spend", "rev", "impressions", "installs", "clicks", "purchases"]].sum()
        return dict(roas=t.rev / t.spend, ipm=t.installs * 1000 / t.impressions,
                    i2p=t.purchases / t.installs, rpp=t.rev / t.purchases,
                    cpm=t.spend * 1000 / t.impressions, ctr=t.clicks / t.impressions,
                    c2i=t.installs / t.clicks)

    b, c = window(base_w), window(cur_w)
    total_log = np.log(c["roas"] / b["roas"])
    d_rows = []
    spec_rows = [("ipm", "Installs per 1,000 impressions (IPM)", 1, "driver"),
                 ("i2p", "Install → purchase (I>P)", 1, "driver"),
                 ("rpp", "Revenue per purchase", 1, "driver"),
                 ("cpm", "Cost per 1,000 impressions (CPM)", -1, "driver"),
                 ("ctr", "Click-through rate (part of IPM)", 1, "part of IPM"),
                 ("c2i", "Click → install (part of IPM)", 1, "part of IPM")]
    for k, label, sign, kind in spec_rows:
        lr = np.log(c[k] / b[k]) * sign
        d_rows.append(dict(driver=k, label=label, kind=kind, base=b[k], current=c[k],
                           change=c[k] / b[k] - 1,
                           roas_points=(lr / total_log) * (c["roas"] - b["roas"]) if kind == "driver" else np.nan))
    d_rows.append(dict(driver="roas", label="ROAS (7-day click)", kind="result", base=b["roas"],
                       current=c["roas"], change=c["roas"] / b["roas"] - 1, roas_points=c["roas"] - b["roas"]))
    drivers = pd.DataFrame(d_rows)
    drivers["base_period"] = f"{base_w[0]} to {base_w[-1]}"
    drivers["current_period"] = f"{cur_w[0]} to {cur_w[-1]}"

    # ---- write ----------------------------------------------------------------
    def w(frame, name):
        frame.to_csv(os.path.join(OUT, name), index=False, float_format="%.4f")

    w(grid, "grid.csv")
    w(weekly, "weekly.csv")
    w(acc, "account.csv")
    w(issues, "checks.csv")
    w(drivers, "drivers.csv")
    print("weeks", weeks[0], "→", L, len(weeks))
    print("grid rows", len(grid), "cols", grid.shape[1])
    for f in ["grid.csv", "weekly.csv", "account.csv", "checks.csv", "drivers.csv"]:
        print(f, os.path.getsize(os.path.join(OUT, f)) // 1024, "KB")
    return df, acc, ad, grid, issues


if __name__ == "__main__":
    build()
