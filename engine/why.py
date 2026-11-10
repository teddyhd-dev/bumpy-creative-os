"""Why did an adset's ROAS move? (core/mistakes.md rule 10, spec §6.2c)

Splits the move between two windows into three causes, from the ad export alone:
  media buying  daily spend changed by 20%+ or ads that carried 15%+ of the spend stopped
  creative      per concept: mix = (share after - share before) x (ROAS before - adset ROAS before)
                                    spend moved to a weaker / stronger creative
                              perf = share after x (ROAS after - ROAS before)
                                    the creative itself got worse / better
                the funnel says why a creative earns less: hook rate (stops the thumb), installs per
                1k impressions, purchases per 100 installs (do its installers pay?)
  audience      country mix, when a country export covers the windows (country_why)

Every function takes the daily ad rows of one adset (engine/adload.load_ads, `name` = concept name) and
returns plain dicts, so the launch review, the tickets and the board can all show the same why.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

BUDGET_MOVE = 0.20     # daily spend up or down 20%+ = a media-buying move
STOPPED_SHARE = 0.15   # ads that stopped and had carried 15%+ of the spend
MIN_SHARE = 0.03       # concepts under 3% in both windows are left out of the text
MIN_IMP = 3000         # under 3k impressions a rate is noise
MIN_CLICKS = 30
NEW_SHARE = 0.01       # under 1% of a window's spend = not really there (its ROAS is noise)


def _roas(x):
    s = x.spend.sum()
    return float(x.rev.sum() / s) if s > 0 else np.nan


def funnel(x):
    """Where an ad wins or loses, step by step: hook (stops the thumb; video only), CTR (link clicks per impression:
    does the message make them want it), C>I (installs per link click: does the store page keep the promise),
    IPM (installs per 1k impressions: demand, the three together), purchases per 100 installs (do they pay)."""
    imp, clk, inst, pur = x.impressions.sum(), x.clicks.sum() if "clicks" in x else 0, x.installs.sum(), x.purchases.sum()
    hook = x.hook_x_imp.sum() / imp if imp > 0 and "hook_x_imp" in x else np.nan
    return dict(spend=float(x.spend.sum()), roas=_roas(x), impressions=int(imp),
                hook=float(hook) if pd.notna(hook) and hook > 0 else None,
                ctr=float(clk / imp) if imp >= MIN_IMP else None,
                c2i=float(inst / clk) if clk >= MIN_CLICKS and imp >= MIN_IMP else None,
                ipm=float(inst / imp * 1000) if imp >= MIN_IMP else None,
                pur_per_100=float(pur / inst * 100) if inst >= 20 else None)


STEPS = [("hook", "hook"), ("ctr", "CTR"), ("c2i", "C>I"), ("ipm", "IPM"), ("pur_per_100", "payers")]
WHERE = {"hook": "the first second: it doesn't stop the thumb, so nobody clicks",
         "ctr": "the message: they watch but don't click",
         "c2i": "the store page: they click but don't install (does the App Store / Play page keep the ad's promise?)",
         "ipm": "demand: a little lower at both the click and the install",
         "pur_per_100": "who it brings: they install but don't pay"}


IMG_RE = r"(?i)-IMG-|\.png|\.jpg|\.jpeg"


def is_image(x):
    return x.ad_name.str.contains(IMG_RE, regex=True) if "ad_name" in x else pd.Series(False, index=x.index)


def _check(new, old, gap, os_name, old_all=None):
    a, b = funnel(new), funnel(old)
    if old_all is not None:                  # who it brings doesn't depend on the format: payers vs every other ad
        b = dict(b, pur_per_100=funnel(old_all)["pur_per_100"])
    lab = dict(STEPS)
    if a["impressions"] < MIN_IMP:
        return dict(new=a, old=b, breaks=None, worse=[], better=[],
                    text=f'Not tested: Meta gave it {a["impressions"]:,} impressions.')
    worse, better = [], []
    for k, _ in STEPS:
        if a.get(k) is None or b.get(k) is None or not b[k]:
            continue
        r = a[k] / b[k] - 1
        (worse if r <= -gap else better if r >= gap else []).append(k)
    # IPM = CTR x C>I: only when installs per impression fall does the click or the install step break;
    # a lower CTR made up by a higher C>I is a different audience, not a break
    if "ipm" in worse:
        brk = next((k for k in ("ctr", "c2i") if k in worse), "ipm")
        if brk == "ctr" and "hook" in worse:
            brk = "hook"
    else:
        brk = "pur_per_100" if "pur_per_100" in worse else None
    txt = f"Breaks at {lab[brk]}: {WHERE[brk]}." if brk else "No step 20%+ worse than the ads it competes with."
    if brk == "c2i" and os_name == "iOS":
        txt += " (iOS installs per ad are Meta's estimate: a hint.)"
    if better:
        txt += " Better at " + ", ".join(lab[k] for k in better) + "."
    return dict(new=a, old=b, breaks=brk, worse=worse, better=better, text=txt)


def funnel_check(new, old, gap=0.20, os_name=""):
    """The new creative's funnel against the ads it competes with, in the same adset and days, like with like:
    its videos against the other videos (the main read), its images against the other images (kept apart: on iOS,
    image clicks are inflated, see image_check). Payers (purchases per 100 installs) against every other ad. The
    break: if installs per 1k impressions (IPM = CTR x C>I) are 20%+ lower, the first of hook/CTR/C>I that is;
    otherwise payers, if 20%+ lower. Too few impressions = Meta never tested it."""
    ni, oi = is_image(new), is_image(old)
    vid = _check(new[~ni], old[~oi], gap, os_name, old) if (~ni).any() else None
    img = _check(new[ni], old[oi], gap, os_name, old) if ni.any() else None
    main = vid or img                     # a new video that wasn't tested stays "not tested": images don't stand in
    out = dict(main, format="video" if main is vid else "image")
    if img and main is vid and not img["text"].startswith("Not tested"):
        out["image"] = img
    if out["format"] == "image" and os_name == "iOS":
        out["text"] += " iOS image clicks are inflated (see image_check): read ROAS and payers, not C>I."
    return out


def image_check(d, since):
    """Account-wide, per OS: images vs videos, ads first live since `since` vs older ads, over the same days.
    Flags new images that click 1.5x+ the older images but install less than half as often per click:
    on iOS that has meant inflated clicks (ROAS stays normal); check placements and the link."""
    x = d[(d.day >= since)].copy()
    x["img"] = is_image(x)
    first = d[d.spend > 0].groupby("ad_id").day.min()
    x["recent"] = x.ad_id.map(first) >= since             # new ads: first spent inside the window
    x["os"] = x["os"] if "os" in x else ""
    g = x.groupby(["os", "img", "recent"]).agg(imp=("impressions", "sum"), clk=("clicks", "sum"), inst=("installs", "sum"),
                                               pur=("purchases", "sum"), spend=("spend", "sum"), rev=("rev", "sum")).reset_index()
    g["ctr"], g["c2i"], g["ipm"] = g.clk / g.imp, g.inst / g.clk, g.inst / g.imp * 1000
    g["pur_per_100"], g["roas"] = g.pur / g.inst * 100, g.rev / g.spend
    base = g[g.img & ~g.recent].set_index("os")
    g["flag"] = [bool(r.img and r.recent and r.os in base.index and r.ctr >= 1.5 * base.loc[r.os, "ctr"]
                      and r.c2i <= 0.5 * base.loc[r.os, "c2i"]) for r in g.itertuples()]
    x["batch"] = x.ad_name.str.extract(r"(?i)batch\d{4}week(\d+)")[0].astype(float)
    bb = x[x.recent].groupby(["os", "img", "batch"]).agg(imp=("impressions", "sum"), clk=("clicks", "sum"), inst=("installs", "sum"),
                                                        pur=("purchases", "sum"), spend=("spend", "sum"), rev=("rev", "sum")).reset_index()
    bb = bb[bb.imp >= 100000]
    bb["ctr"], bb["c2i"], bb["ipm"] = bb.clk / bb.imp, bb.inst / bb.clk, bb.inst / bb.imp * 1000
    bb["pur_per_100"], bb["roas"] = bb.pur / bb.inst * 100, bb.rev / bb.spend
    return dict(since=str(pd.Timestamp(since).date()), rows=json_rows(g), by_batch=json_rows(bb))


def json_rows(g):
    return [{k: (None if pd.isna(v) else (bool(v) if isinstance(v, (bool, np.bool_)) else float(v) if isinstance(v, (int, float, np.number)) else v))
             for k, v in r.items()} for r in g.to_dict("records")]


def concepts(pre, post):
    """Per concept: share, ROAS and funnel in both windows, plus its mix and perf part of the move."""
    r0 = _roas(pre)
    s0, s1 = pre.spend.sum(), post.spend.sum()
    out = []
    for name in sorted(set(pre.name) | set(post.name)):
        a, b = pre[pre.name == name], post[post.name == name]
        sh0 = a.spend.sum() / s0 if s0 else 0.0
        sh1 = b.spend.sum() / s1 if s1 else 0.0
        ro0, ro1 = _roas(a), _roas(b)
        if sh0 < NEW_SHARE:
            ro0 = np.nan                 # (almost) new in the adset: its whole part is mix, not perf
        if sh1 < NEW_SHARE:
            ro1 = np.nan
        base = ro0 if pd.notna(ro0) else (ro1 if pd.notna(ro1) else r0)
        mix = (sh1 - sh0) * ((base if pd.notna(base) else r0) - r0) if pd.notna(r0) else 0.0
        perf = sh1 * (ro1 - ro0) if pd.notna(ro0) and pd.notna(ro1) else 0.0
        out.append(dict(name=name, share_before=round(sh0, 3), share_after=round(sh1, 3),
                        roas_before=None if pd.isna(ro0) else round(ro0, 3),
                        roas_after=None if pd.isna(ro1) else round(ro1, 3),
                        mix=round(float(mix), 4), perf=round(float(perf), 4),
                        funnel=funnel(b if len(b) else a)))
    return sorted(out, key=lambda c: -(c["share_after"] + c["share_before"]))


def media(pre, post):
    """Budget and ads switched off. An ad that spent $20+/day and then got 0 impressions from one day to the next
    was switched off (Meta lowers delivery gradually); one that faded first is listed as faded, not as a media move."""
    d0, d1 = max(pre.day.nunique(), 1), max(post.day.nunique(), 1)
    sp0, sp1 = pre.spend.sum() / d0, post.spend.sum() / d1
    both = pd.concat([pre, post])
    a0 = pre.groupby("ad_id").spend.sum()
    off, faded = [], []
    for ad, s in a0[a0 > 0].items():
        x = both[both.ad_id == ad].groupby("day")[["spend", "impressions"]].sum().sort_index()
        live = x[x.impressions > 0]
        if live.empty or live.index.max() >= both.day.max():
            continue                                  # still delivering on the last day
        last3 = live.spend.tail(3).mean()
        (off if last3 >= 20 else faded).append((ad, s, live.index.max()))
    tot = a0.sum() or 1.0
    nm = pre.drop_duplicates("ad_id").set_index("ad_id").name
    off = sorted(off, key=lambda t: -t[1])
    return dict(spend_day_before=round(float(sp0)), spend_day_after=round(float(sp1)),
                budget_move=round(float(sp1 / sp0 - 1), 3) if sp0 else None,
                stopped_share=round(float(sum(t[1] for t in off) / tot), 3),
                stopped=[f"{nm.get(t[0], '?')} (last day {t[2]:%-d %b})" for t in off[:3]],
                faded_share=round(float(sum(t[1] for t in faded) / tot), 3))


def explain(pre, post):
    """The why for one adset between two windows: causes, the concepts that moved it, and one line of text."""
    r0, r1 = _roas(pre), _roas(post)
    C = concepts(pre, post)
    M = media(pre, post)
    causes = []
    if M["budget_move"] is not None and abs(M["budget_move"]) >= BUDGET_MOVE:
        causes.append("media buying")
    if M["stopped_share"] >= STOPPED_SHARE and "media buying" not in causes:
        causes.append("media buying")
    movers = [c for c in C if max(c["share_before"], c["share_after"]) >= MIN_SHARE]
    movers = sorted(movers, key=lambda c: c["mix"] + c["perf"])
    if movers:
        causes.append("creative")
    return dict(roas_before=None if pd.isna(r0) else round(r0, 3), roas_after=None if pd.isna(r1) else round(r1, 3),
                causes=causes, media=M, concepts=C, text=text(r0, r1, movers, M))


def _f(x):
    return "–" if x is None or pd.isna(x) else f"{x:.2f}"


def _say(c):
    if abs(c["perf"]) >= abs(c["mix"]):
        return f'{c["name"]} {"fell" if c["perf"] < 0 else "rose"} {_f(c["roas_before"])} → {_f(c["roas_after"])} ({c["share_after"]:.0%} of spend)'
    r = c["roas_after"] if c["roas_after"] is not None else c["roas_before"]
    moved = "took" if c["share_after"] > c["share_before"] else "lost"
    return f'{c["name"]} {moved} spend ({c["share_before"]:.0%} → {c["share_after"]:.0%}) at {_f(r)}'


def text(r0, r1, movers, M):
    if pd.isna(r0) or pd.isna(r1):
        return "Too little spend in one of the windows to say."
    down = r1 < r0
    parts = []
    hurt = [c for c in movers if (c["mix"] + c["perf"]) < -0.005]
    helped = [c for c in movers if (c["mix"] + c["perf"]) > 0.005][::-1]
    lead, other = (hurt, helped) if down else (helped, hurt)
    parts = [_say(c) for c in lead[:2]]
    if other:
        parts.append("against it: " + _say(other[0]))
    mb = []
    if M["budget_move"] is not None and abs(M["budget_move"]) >= BUDGET_MOVE:
        mb.append(f'spend ${M["spend_day_before"]} → ${M["spend_day_after"]}/day')
    if M["stopped_share"] >= STOPPED_SHARE:
        mb.append(f'switched off: ads with {M["stopped_share"]:.0%} of the spend ({", ".join(M["stopped"])})')
    tail = ("Media buying: " + "; ".join(mb) + ".") if mb else \
        f'Not media buying: ${M["spend_day_before"]} → ${M["spend_day_after"]}/day, nothing big switched off.'
    return f'{_f(r0)} → {_f(r1)}: ' + "; ".join(parts) + ". " + tail


def country_why(cw, adset_id, wk0, wk1):
    """Audience: country mix vs ROAS inside the same countries, from the weekly country export.
    cw columns: adset_id, week, country, spend, rev. Returns mix and within parts of the move."""
    x = cw[cw.adset_id.astype(str) == str(adset_id)]
    a, b = x[x.week == wk0].groupby("country")[["spend", "rev"]].sum(), x[x.week == wk1].groupby("country")[["spend", "rev"]].sum()
    if a.spend.sum() == 0 or b.spend.sum() == 0:
        return None
    J = a.join(b, lsuffix="0", rsuffix="1", how="outer").fillna(0)
    sh0, sh1 = J.spend0 / J.spend0.sum(), J.spend1 / J.spend1.sum()
    r0c = (J.rev0 / J.spend0).where(J.spend0 > 0)
    r1c = (J.rev1 / J.spend1).where(J.spend1 > 0)
    R0 = J.rev0.sum() / J.spend0.sum()
    mix = float(((sh1 - sh0) * (r0c.fillna(R0) - R0)).sum())
    within = float((sh1 * (r1c - r0c)).fillna(0).sum())
    return dict(mix=round(mix, 4), within=round(within, 4),
                text=("the country mix" if abs(mix) > abs(within) else "inside the same countries"))


def load_country(weeks):
    """Weekly country rows (adset_id, week, country, spend, rev) from the exports with an Ad set ID column."""
    import os
    from files import raw_files
    fr = []
    for f in raw_files("country", "country"):
        x = pd.read_csv(f, encoding="utf-8-sig", dtype={"Ad set ID": str}, low_memory=False)
        if "Ad set ID" not in x or "Reporting starts" not in x:
            continue
        x = x[x["Reporting starts"].astype(str).str[:10].isin(weeks)]
        if x.empty:
            continue
        sp = pd.to_numeric(x["Amount spent (USD)"], errors="coerce").fillna(0)
        fr.append(pd.DataFrame(dict(adset_id=x["Ad set ID"].astype(str), week=x["Reporting starts"].astype(str).str[:10],
                                    country=x["Country"], spend=sp,
                                    rev=pd.to_numeric(x["Purchase ROAS (return on ad spend)"], errors="coerce").fillna(0) * sp,
                                    _f=os.path.basename(f))))
    if not fr:
        return pd.DataFrame(columns=["adset_id", "week", "country", "spend", "rev"])
    c = pd.concat(fr)
    c = c[c._f == c.groupby("week")._f.transform("max")]       # one file per week: the latest export wins
    return c.drop(columns="_f")
