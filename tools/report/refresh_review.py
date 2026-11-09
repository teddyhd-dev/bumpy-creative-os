"""Refresh review: the data behind the weekly launch-review deck (tools/report/REFRESH-REVIEW.md).

Usage (from the repo root, after `bash engine/run_all.sh`):
    python3 tools/report/refresh_review.py --batch Batch2026Week40 [--creator Batch2026Week44] [--end 2026-11-01] [--out followup.json]

Needs daily ad rows (an `ad_` export with one row per ad per day) for the review weeks: upload days and
before/after windows are measured in days. Writes reports/<week>/refresh_review.json and prints a summary.

For every adset the batch landed in:
  upload   = first day the batch's ads spent in that adset (uploads on different days = different waves)
  before   = adset ROAS in the 7 days before the upload; after = upload day → --end
  rank     = the batch's best concept rank by spend in the adset since upload (batch ads grouped per concept,
             apart from older ads of the same concept, so new variants of an old concept count as new)
  read     = Worked / Almost / Flat / Watch / Worse / Miss / Miss (left), same rule as engine/tickets.py (spec §6.2b)
  #1       = top concept before vs since upload; NEW = the batch is #1, NEW-OLD = an older concept just became #1
  reign    = weeks the current #1 has led the adset (weekly #1s, counted back from the latest week)
Action items (owner-first on the slides, one creative row per persona × language): priority = read weight × the adset's weekly spend (Worse first, then misses under the bar,
then Almost / Flat); Miss (left) and Worked are left alone. Account news: every other adset with $1k+ a week
whose #1 changed, or where a concept jumped into the top 3 with 15%+ share (+10 points), week on week.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "engine"))
from adload import load_ads  # noqa: E402
from adparse import parse_ad  # noqa: E402
from build import parse_name  # noqa: E402
from codes import concept_keys, concept_names  # noqa: E402
from settings import READ, bar  # noqa: E402
from tickets import refresh_read  # noqa: E402

WEIGHT = {"Worse": 1.0, "Miss": 0.8, "Almost": 0.6, "Flat": 0.6, "Worked": 0.0, "Watch": 0.0, "Miss (left)": 0.0}
ACTION = {
    "Worse": "Fix first: new concept, 3+ variants; pause the batch ads that took spend",
    "Miss": "Refresh again with a different concept (this one didn't get spend)",
    "Almost": "Refresh again: keep the batch ads on, add a stronger hook",
    "Flat": "Refresh again: the batch didn't move ROAS",
    "Worked": "Leave: watch week 2",
    "Watch": "Leave: the new creative took over and ROAS dipped but stays at the bar; re-read next week (no strike)",
    "Miss (left)": "Leave: old creatives carry it above the bar",
}


def load(batch, creator):
    d = load_ads()
    d = d[d.spend.fillna(0) > 0].copy()
    d["adset_id"] = d.adset_id.astype(str)
    P = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d.ad_name.unique()])
    d = d.merge(P, on="ad_name", how="left")
    d["key"] = concept_keys(d)
    # a reused code with a different concept name stays its own concept here (e.g. h7km3n internationalfriends)
    low, cn = d.concept.fillna("").str.lower(), d.conceptname.fillna("").str.lower()
    names = concept_names()
    reg = d.key.map(lambda k: str(names.get(k, "")).lower())
    clash = (d.key != d.concept) & (reg != "") & (cn != "") & (cn != reg)
    d.loc[clash, "key"] = d.loc[clash, "concept"]
    d["name"] = np.where(clash, d.conceptname, d.key.map(lambda k: names.get(k, k.replace("name:", "")[:16])))
    b = d.ad_name.str.extract(r"(?i)(batch\d{4}week\d+)")[0].str.lower()
    d["is_batch"] = b.eq(batch.lower())
    d["is_creator"] = b.eq(creator.lower()) if creator else False
    d["grp"] = np.where(d.is_batch, d.name + " ★", np.where(d.is_creator, d.name + " ◆", d.name))
    dims = {a: parse_name(n) for a, n in d.sort_values("start").groupby("adset_id").adset_name.last().items()}
    d["os"] = d.adset_id.map(lambda a: dims[a]["os"])
    d["day"] = d.start
    daily = d[d.start == d.end]
    if daily.empty:
        sys.exit("No daily ad rows: export the ad level with a Day breakdown for the review weeks.")
    return d, daily, dims


def roas(x):
    s = x.spend.sum()
    return float(x.rev.sum() / s) if s > 0 else None


def reign_weeks(d, aid, name, last_week):
    w = d[d.adset_id == aid].groupby(["week", "name"]).spend.sum().reset_index()
    top = w.sort_values("spend", ascending=False).drop_duplicates("week").set_index("week").name.sort_index()
    n = 0
    for wk in sorted(top.index[top.index <= last_week], reverse=True):
        if top[wk] != name:
            break
        n += 1
    return n


def landings(d, daily, dims, end, last_week, wk_spend, flag, mark):
    """One row per adset where the ads flagged `flag` (grouped per concept, suffix `mark`) spent."""
    up = daily[daily[flag]].groupby("adset_id").day.min()
    rows = []
    for aid, u in up.items():
        if u > end:
            continue                    # first spent after the review window: next week's review
        p = dims[aid]
        pre = daily[(daily.adset_id == aid) & (daily.day >= u - pd.Timedelta(days=7)) & (daily.day < u)]
        post = daily[(daily.adset_id == aid) & (daily.day >= u) & (daily.day <= end)]
        g = post.groupby("grp").spend.sum().sort_values(ascending=False)
        mine = [k for k in g.index if k.endswith(mark)]
        rank = min(list(g.index).index(k) + 1 for k in mine)
        sh = g / g.sum()
        cum_above = float(sh.cumsum().iloc[rank - 1] - sh.iloc[rank - 1])   # share of the ads ranked above it
        gb = pre.groupby("grp").spend.sum().sort_values(ascending=False)
        n1_before = gb.index[0].rstrip(" ★◆") if len(gb) else None
        n1_after = g.index[0]
        tag = "NEW" if n1_after.endswith(mark) else ("NEW-OLD" if n1_before and n1_after.rstrip(" ★◆") != n1_before else "")
        before, after = roas(pre), roas(post)
        b = bar(last_week, p["os"])
        read = refresh_read(rank, before if before is not None else np.nan, after if after is not None else np.nan, b, cum_above)
        n1 = n1_after.rstrip(" ★◆")
        rows.append(dict(cum_above=round(cum_above, 3),
            adset_id=aid, persona=p["persona"], os=p["os"], lang=p["lang"], subangle=p["subangle"], launch=p["launch"],
            upload=str(u.date()), days_after=int((end - u).days) + 1,
            concepts=sorted({k[:-len(mark)] for k in mine}), batch_share=round(float(g[mine].sum() / g.sum()), 3),
            rank=int(rank), before=before, after=after, read=read,
            no1_before=n1_before, no1_after=n1, no1_tag=tag, no1_share=round(float(g.iloc[0] / g.sum()), 3),
            no1_weeks=0 if tag else reign_weeks(d, aid, n1, last_week),
            weekly_roas={w: roas(x) for w, x in d[d.adset_id == aid].groupby("week")},
            spend_week=round(float(wk_spend.get(aid, 0))), priority=round(WEIGHT[read] * float(wk_spend.get(aid, 0))),
            action=ACTION[read]))
    return pd.DataFrame(rows), up


def slide_order(R, by=()):
    """Top-3 group first, ROAS after best → worst; then the rest worst → best (bad rows meet in the middle)."""
    if R.empty:
        return R
    R = R.copy()
    R["_in"] = R["rank"] <= READ["top_n"]
    R["_k"] = np.where(R._in, -R.after.fillna(-1), R.after.fillna(-1))
    return R.sort_values([*by, "_in", "_k"], ascending=[True] * len(by) + [False, True]).drop(columns=["_in", "_k"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--creator", default="")
    ap.add_argument("--end", default=None)
    ap.add_argument("--out", default="refresh_review.json", help="file name in reports/<week>/ (e.g. a follow-up read)")
    a = ap.parse_args()
    d, daily, dims = load(a.batch, a.creator)
    end = pd.Timestamp(a.end) if a.end else daily.day.max()
    last_week = (end - pd.Timedelta(days=end.weekday())).strftime("%Y-%m-%d")
    prev_week = (end - pd.Timedelta(days=end.weekday() + 7)).strftime("%Y-%m-%d")
    wk_spend = d[d.week == last_week].groupby("adset_id").spend.sum()
    R, up = landings(d, daily, dims, end, last_week, wk_spend, "is_batch", " ★")
    R = slide_order(R, by=("persona",))
    # creator content (section 2): same read, one slide; "works" when most creator adsets read Worked / Almost
    C, creator_summary = pd.DataFrame(), {}
    if a.creator:
        C, _ = landings(d, daily, dims, end, last_week, wk_spend, "is_creator", " ◆")
        C = slide_order(C)
    if len(C):
        top3 = C[C["rank"] <= READ["top_n"]]
        good = top3[top3.read.isin(["Worked", "Almost"])]
        works = bool(len(good) > len(C) / 2)
        creator_summary = dict(adsets=len(C), top3=len(top3), no1=int((C["rank"] == 1).sum()), top3_good=len(good),
                               works=works, title="Creator creative works" if works
                               else "Creator creative still hasn't beaten our past winners")
    # ---- account news: every other adset with $1k+ a week whose top spenders moved ----
    news = []
    w = d[d.week.isin([prev_week, last_week])].groupby(["adset_id", "week", "grp"]).spend.sum().reset_index()
    for aid, g in w.groupby("adset_id"):
        if aid in up.index or wk_spend.get(aid, 0) < 1000:
            continue
        if dims[aid]["objective"] not in ("Purchase", "Sales"):
            continue
        P0 = g[g.week == prev_week].set_index("grp").spend
        P1 = g[g.week == last_week].set_index("grp").spend
        if P0.empty or P1.empty:
            continue
        s0, s1 = (P0 / P0.sum()), (P1 / P1.sum())
        t0, t1 = s0.sort_values(ascending=False), s1.sort_values(ascending=False)
        new_no1 = t1.index[0].rstrip(" ★◆") != t0.index[0].rstrip(" ★◆")
        risers = [k for k in t1.index[:3] if s1[k] >= 0.15 and s1[k] - s0.get(k, 0) >= 0.10 and k != t1.index[0]]
        if not new_no1 and not risers:
            continue
        x = d[d.adset_id == aid]
        mover = t1.index[0] if new_no1 else risers[0]
        news.append(dict(
            adset_id=aid, persona=dims[aid]["persona"], os=dims[aid]["os"], lang=dims[aid]["lang"],
            roas_before=roas(x[x.week == prev_week]), roas_after=roas(x[x.week == last_week]),
            prev_winner=t0.index[0], prev_winner_weeks=reign_weeks(d, aid, t0.index[0].rstrip(" ★◆"), prev_week),
            prev_share=round(float(t0.iloc[0]), 3), event="new #1" if new_no1 else "new in top 3",
            mover=mover, mover_share=round(float(s1[mover]), 3), mover_before=round(float(s0.get(mover, 0)), 3),
            spend_week=round(float(wk_spend.get(aid, 0)))))
    N = pd.DataFrame(news) if news else pd.DataFrame()
    if len(N):   # slide order: ROAS after high → low, then the biggest improvement (on the rounded numbers)
        N["_a"], N["_d"] = N.roas_after.round(2), N.roas_after.round(2) - N.roas_before.round(2)
        N = N.sort_values(["_a", "_d"], ascending=False).drop(columns=["_a", "_d"])
    out = dict(batch=a.batch, creator_batch=a.creator, end=str(end.date()), week=last_week, read_rule=READ,
               adsets=json.loads(R.to_json(orient="records")),
               creator=json.loads(C.to_json(orient="records")) if len(C) else [], creator_summary=creator_summary,
               account_news=json.loads(N.to_json(orient="records")))
    od = os.path.join(ROOT, "reports", last_week)
    os.makedirs(od, exist_ok=True)
    with open(os.path.join(od, a.out), "w") as f:
        json.dump(out, f, indent=1)
    pd.set_option("display.width", 220)
    print(R[["upload", "persona", "os", "lang", "before", "after", "rank", "batch_share", "read", "no1_after", "no1_tag",
             "no1_weeks", "spend_week", "priority"]].round(3).to_string(index=False))
    print("\naction items (priority = read weight × weekly spend):")
    print(R[R.priority > 0].sort_values("priority", ascending=False)[["persona", "os", "lang", "read", "spend_week", "priority", "action"]].to_string(index=False))
    if len(C):
        print("\ncreator content:", creator_summary["title"])
        print(C[["persona", "os", "lang", "before", "after", "rank", "batch_share", "read", "no1_after", "no1_tag"]].round(3).to_string(index=False))
    if len(N):
        print("\naccount news:")
        print(N.drop(columns=["adset_id"]).round(3).to_string(index=False))
    print(f"\nwrote reports/{last_week}/refresh_review.json")


if __name__ == "__main__":
    main()
