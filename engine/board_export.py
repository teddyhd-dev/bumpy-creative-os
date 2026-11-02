"""Export the engine's view for the shared Creative Board (spec §20).

Writes three JSON documents to output/board/, each sent to the board's database as one document
in the `engine` collection (Claude does this after each weekly run, with ArtifactData):
  * queue.json  → engine/queue   tickets ranked, with dossier, at-bats, J1 candidates, sparkline
  * people.json → engine/people  roster and history scorecards (designers from the Notion tracker)
  * codes.json  → engine/codes   every concept code in use (lowercase), so new codes never collide
People's own work (briefs, handoffs, retros, signals) lives in other collections and is never
overwritten by this export.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
from datetime import date

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from settings import BARS  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output", "data")
BOARD = os.path.join(ROOT, "output", "board")
MAX_TICKETS = 100

def _roster():
    """The team lives in core/team.csv (one place for every tool)."""
    T = pd.read_csv(os.path.join(ROOT, "core", "team.csv"), dtype=str).fillna("")
    out = []
    for r in T.itertuples():
        d = dict(code=r.code, name=r.name.split(" ")[0] if r.code != "KIM" else r.name, role=r.role, active=r.active.lower() == "true")
        if r.role == "designer" and r.notion_match:
            d["match"] = r.notion_match
        out.append(d)
    return out


ROSTER = _roster()
TASKS = ["Image Generation / Creation", "Image to Video / Video Generation", "Voice Generation / Sourcing",
         "Lipsync (Image+Voice to Video) Generation", "Simple Video Generation Non-AI", "Non-AI Video Generation",
         "Core Output Edit", "Complex Core Output Edit", "Replication/Variation", "Complex Replication/Variation"]


def num(x, nd=4):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(v) else round(v, nd)


def s(x):
    return "" if x is None or (isinstance(x, float) and not np.isfinite(x)) or str(x) == "nan" else str(x)


def queue_doc():
    Q = pd.read_csv(os.path.join(OUT, "tk_queue.csv"), dtype={"adset_id": str})
    D = pd.read_csv(os.path.join(OUT, "tk_atbats.csv"), dtype={"adset_id": str})
    C = pd.read_csv(os.path.join(OUT, "tk_candidates.csv"), dtype={"adset_id": str})
    Z = pd.read_csv(os.path.join(OUT, "tk_resurrect.csv"), dtype={"adset_id": str})
    F = pd.read_csv(os.path.join(OUT, "tk_facts.csv")).set_index("fact")
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"].set_index("adset_id")
    wk = sorted(c[2:] for c in G.columns if c.startswith("s_"))[-8:]
    tickets = []
    for r in Q.head(MAX_TICKETS).itertuples():
        g = G.loc[r.adset_id] if r.adset_id in G.index else None
        hist = dict(w=wk, s=[num(g[f"s_{w}"], 0) if g is not None else None for w in wk],
                    r=[num(g[f"r_{w}"], 3) if g is not None else None for w in wk])
        ab = D[D.adset_id == r.adset_id].tail(5)
        j1 = C[C.adset_id == r.adset_id].sort_values("n")
        tickets.append(dict(
            id=r.ticket, rank=int(r.rank), type=r.type, state=r.state, score=num(r.score, 0),
            adset=r.adset, adset_id=r.adset_id, name=s(r.name), persona=s(r.persona), lang=s(r.lang), os=s(r.os),
            status=s(r.status), why=s(r.why), spend=num(r.spend_last, 0), roas=num(r.roas_last, 3), roas_prev=num(r.roas_prev, 3),
            top_code=s(r.top_code), top_name=s(r.top_name), top_share=num(r.top_share, 3), reign=int(r.reign_week or 0),
            strikes=int(r.strikes), tried8=int(r.tried_8w), last_hit=s(r.last_hit),
            weeks_under=int(r.weeks_under), fading=bool(r.fading),
            reign_since=s(r.reign_since), last_refresh=s(r.last_refresh), data_start=s(r.data_start),
            in_test=s(r.in_test), test_verdict=s(r.test_verdict), test_s1=num(r.test_week1_share, 3),
            low_ceiling=bool(r.low_ceiling), notes=s(r.notes),
            brief_with=[x.strip() for x in s(r.brief_with).split(",") if x.strip()],
            past=json.loads(r.past_json or "[]"),
            j1=[dict(code=s(x.code), name=s(x.name), fit=s(x.fit), won_in=s(x.won_in), spend_as_1=num(x.spend_as_1, 0),
                     last_as_1=s(x.last_as_1)) for x in j1.itertuples()],
            atbats=[dict(w0=s(x.w0), codes=s(x.codes), concepts=int(x.concepts), variants=int(x.variants_max),
                         s1=num(x.best_s1, 3), verdict=s(x.verdict), context=s(x.context)) for x in ab.itertuples()],
            hist=hist))
    fv = F["value"]
    facts = {k: num(fv[k]) for k in fv.index if k != "last_ad_week"}
    G2 = pd.read_csv(os.path.join(OUT, "grid.csv"), usecols=["level", "last_week"], low_memory=False)
    return dict(
        generated=date.today().isoformat(), adset_week=str(G2[G2.level == "adset"].last_week.max()),
        ad_week=str(F.loc["last_ad_week", "label"]),
        bar=dict(green=BARS["singular"]["green"], amber=BARS["singular"]["amber"], deep=BARS["singular"]["deep"]),
        capacity=num(fv["capacity_per_week"], 1), facts=facts, tickets=tickets,
        resurrect=[dict(adset=s(z.adset), adset_id=s(z.adset_id), name=s(z.name), last_week=s(z.last_week),
                        peak=num(z.peak_wk, 0), rel=num(z.rel_last4, 3), fate=s(z.persona_fate)) for z in Z.itertuples()],
        personas=sorted(G.persona.dropna().astype(str).unique().tolist()),
    )


_CTX = {}


def ctx():
    """Concept-week table, concept → batches, and per-concept outcomes (computed once)."""
    if _CTX:
        return _CTX
    import tickets as tk
    from adload import load_ads
    from adparse import parse_ad
    c, A, meta, names = tk.concept_weeks()
    d = load_ads()
    P = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d.ad_name.unique()])
    codes = set(P.concept.str.lower()) - {""}
    P = P[(P.concept != "") & (P.batch != "")]
    cb = P.groupby(P.concept.str.lower()).batch.agg(lambda x: set(x))
    _CTX.update(c=c, A=A, meta=meta, names=names, cb=cb, codes=codes)
    return _CTX


def people_doc():
    """Roster + designer history from the Notion tracker (code + batch joined to ad data)."""
    X = ctx()
    c, cb = X["c"], X["cb"]
    last = sorted(c.week.unique())[-1]
    arr = c[(c.wk == 0) & (c.as_s >= 1000) & (c.spend >= 20)].copy()
    tops = c[c["rank"] == 1][["adset_id", "concept_key", "wk"]]
    t1 = tops.groupby(["adset_id", "concept_key"]).wk.min()
    arr["wk_top"] = [t1.get((a, k), np.nan) for a, k in zip(arr.adset_id, arr.concept_key)]
    arr["k"] = arr.concept_key.str.lower()
    per = arr.groupby("k").agg(w1max=("share", "max"), first=("week", "min"),
                               became1=("wk_top", lambda x: bool((x <= 4).any())))
    per["complete"] = (pd.to_datetime(last) - pd.to_datetime(per["first"])).dt.days >= 28
    _CTX["per"] = per
    files = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "notion", "notion_tracker_*.csv")))
    T = pd.read_csv(files[-1]) if files else pd.DataFrame(columns=["Concept (BRIEF)", "Designer"])
    m = T["Concept (BRIEF)"].astype(str).str.extract(r"Batch(\d{4})\s*Week\s*(\d{1,2})\s*[-_ ]+([A-Za-z0-9]{5,7})")
    T["batch"] = m[0].fillna("") + "W" + m[1].fillna("").str.zfill(2)
    T["code_l"] = m[2].str.lower()
    T["fin"] = pd.to_datetime(T["Finish Date"], errors="coerce")
    T["start"] = pd.to_datetime(T["Start Date"], errors="coerce", format="mixed")
    T["cycle"] = (T.fin - T.start).dt.days
    T["finished"] = T["Design Status"].astype(str).str.lower().eq("finished")
    today = pd.Timestamp(date.today())
    weeks = [(today - pd.Timedelta(weeks=k)).to_period("W-SUN").start_time for k in range(11, -1, -1)]
    hist = {}
    for p in ROSTER:
        if "match" not in p:
            continue
        mine = T[T.Designer.astype(str).str.lower().str.contains(p["match"], regex=True, na=False)]
        done = mine[mine.finished]
        k = done.dropna(subset=["code_l"])
        k = k[[(cl in per.index) and (b in cb.get(cl, set())) for cl, b in zip(k.code_l, k.batch)]]
        o = per.loc[k.code_l.unique()] if len(k) else per.iloc[0:0]
        o = o[o.complete]
        fin_w = done.fin.dropna().dt.to_period("W-SUN").dt.start_time
        hist[p["code"]] = dict(
            briefs=int(len(mine)), finished=int(len(done)),
            cycle_days=num(done.cycle[(done.cycle >= 0) & (done.cycle <= 60)].median(), 1),
            last8=int((done.fin >= today - pd.Timedelta(weeks=8)).sum()),
            weekly=[int((fin_w == w).sum()) for w in weeks],
            with_results=int(len(o)), won20=num((o.w1max >= 0.2).mean(), 3) if len(o) else None,
            became1=num(o.became1.mean(), 3) if len(o) else None,
            first=s(done.fin.min().date() if done.fin.notna().any() else ""),
            last=s(done.fin.max().date() if done.fin.notna().any() else ""))
    F = pd.read_csv(os.path.join(OUT, "tk_facts.csv")).set_index("fact")["value"]
    allc = per[per.complete & ~per.index.str.startswith("name:")]
    return dict(
        generated=date.today().isoformat(),
        roster=[{k: v for k, v in p.items() if k != "match"} for p in ROSTER],
        history=hist, weeks=[w.strftime("%Y-%m-%d") for w in weeks], tasks=TASKS,
        baseline=dict(won20=num((allc.w1max >= 0.2).mean(), 3), became1=num(allc.became1.mean(), 3), concepts=int(len(allc)),
                      hit_rate=num(F.get("hit_rate")), hit_rate_3var=num(F.get("hit_rate_3var")),
                      hit_rate_12var=num(F.get("hit_rate_12var"))),
        source="Notion Ad Creative Tracker (export 27 Oct 2026) joined to Meta ad data by concept code + batch",
        metric="Won 20%+ of an adset's spend in its first week there (adsets spending $1k+ that week); became an adset's #1 within 4 weeks",
    )


def codes_doc():
    codes = set(ctx()["codes"])
    files = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "notion", "notion_tracker_*.csv")))
    if files:
        T = pd.read_csv(files[-1])
        codes |= set(T["Concept (BRIEF)"].astype(str).str.extract(r"[-_ ]([A-Za-z0-9]{6})[-_ ]")[0].dropna().str.lower())
    return dict(generated=date.today().isoformat(), codes=sorted(c for c in codes if re.fullmatch(r"[a-z0-9]{5,7}", c)))


def log_doc():
    """Every refresh at-bat since December with its verdict, and a week-by-week history."""
    D = pd.read_csv(os.path.join(OUT, "tk_atbats.csv"), dtype={"adset_id": str})
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"].set_index("adset_id")
    lab = lambda a: (f"{G.persona.get(a, '')} · {G.os.get(a, '')} · {G.lang.get(a, '')}" if a in G.index else a)
    atbats = [dict(adset_id=r.adset_id, adset=lab(r.adset_id), persona=s(G.persona.get(r.adset_id, "")), w0=s(r.w0), codes=s(r.codes),
                   concepts=int(r.concepts), variants=int(r.variants_max), s1=num(r.best_s1, 3), verdict=s(r.verdict),
                   context=s(r.context), lift=num(r.adset_lift, 3)) for r in D.itertuples()]
    O = pd.read_csv(os.path.join(OUT, "ov_weekly.csv"))
    from settings import bar
    wk = sorted(c[2:] for c in G.columns if c.startswith("s_"))
    J = G[G.judged.astype(str).isin(["True", "true"])]
    weeks = []
    for w in wk:
        sp = pd.to_numeric(J[f"s_{w}"], errors="coerce").fillna(0)
        rr = pd.to_numeric(J[f"r_{w}"], errors="coerce")
        green = pd.Series([bar(w, o)["green"] for o in J.os], index=J.index)
        live = sp > 0
        under = live & (rr < green)
        ab = D[D.w0 == w]
        o = O[O.week == w]
        weeks.append(dict(
            week=w, live_adsets=int(live.sum()), spend=num(sp.sum(), 0), under_share=num(sp[under].sum() / sp.sum(), 3) if sp.sum() else None,
            paid_spend=num(o.paid_spend.iloc[0], 0) if len(o) else None, store=num(o.store_proceeds.iloc[0], 0) if len(o) else None,
            roas_ios=num(o.roas_ios.iloc[0], 3) if len(o) else None, roas_android=num(o.roas_android.iloc[0], 3) if len(o) else None,
            era=s(o.era.iloc[0]) if len(o) else "", bar=num(green.median(), 2),
            atbats=int(len(ab)), hits=int(ab.verdict.str.contains("Hit|Home run").sum()), home_runs=int((ab.verdict == "Home run").sum()),
            strikes=int(ab.verdict.str.startswith("Strike").sum()), fouls=int(ab.verdict.str.startswith("Foul").sum()),
            late=int((ab.verdict == "Late hit").sum())))
    return dict(generated=date.today().isoformat(), atbats=atbats, weeks=weeks)


def archive_doc():
    """The Notion Ad Creative Tracker, kept as read-only history, with outcomes where the code + batch join."""
    X = ctx()
    per, cb = X.get("per"), X["cb"]
    files = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "notion", "notion_tracker_*.csv")))
    if not files:
        return dict(generated=date.today().isoformat(), briefs=[])
    T = pd.read_csv(files[-1])
    m = T["Concept (BRIEF)"].astype(str).str.extract(r"Batch(\d{4})\s*Week\s*(\d{1,2})\s*[-_ ]+([A-Za-z0-9]{5,7})")
    T["batch"] = m[0].fillna("") + "W" + m[1].fillna("").str.zfill(2)
    T["code_l"] = m[2].str.lower()
    code_of = {r["match"]: r["code"] for r in ROSTER if "match" in r}
    def des(v):
        v = str(v).lower()
        return " ".join(c for pat, c in code_of.items() if re.search(pat, v))
    out = []
    for r in T.itertuples():
        title = s(getattr(r, "_1", ""))
        if not title or title == "Untitled":
            continue
        k = r.code_l if isinstance(r.code_l, str) else ""
        o = per.loc[k] if per is not None and k in per.index and r.batch in cb.get(k, set()) else None
        out.append(dict(t=title[:80], code=s(m.loc[r.Index, 2]), batch=s(r.batch), des=des(r.Designer), st=s(getattr(r, "_4", "")),
                        start=s(getattr(r, "_20", ""))[:20], fin=s(getattr(r, "_21", ""))[:12], camp=s(r.Campaign)[:60],
                        lang=s(r.Language)[:60], w1=num(o.w1max, 3) if o is not None else None,
                        top=bool(o.became1) if o is not None else None, done=bool(o.complete) if o is not None else None))
    return dict(generated=date.today().isoformat(), source="Notion Ad Creative Tracker export, 27 Oct 2026", briefs=out)


def personas_doc():
    """The living persona file's data: Notion cards (mapped to v8), winners by persona, live state."""
    import personas as pz
    X = ctx()
    c, meta, names = X["c"], X["meta"], X["names"]
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"]
    tops = c[(c["rank"] == 1) & (c.as_s >= 500)].copy()
    tops["persona"] = tops.adset_id.map(meta.as_persona)
    recent = sorted(c.week.unique())[-26]
    t = tops[tops.week >= recent].groupby(["persona", "concept_key"]).agg(
        weeks=("week", "size"), spend=("spend", "sum"), last=("week", "max"), adsets=("adset_id", "nunique")).reset_index()
    P = {}
    for p, g in t.groupby("persona"):
        g = g.sort_values("spend", ascending=False).head(6)
        P[p] = dict(winners=[dict(code=k.replace("name:", "")[:24], name=s(names.get(k, ""))[:24], weeks=int(w), spend=num(sp, 0),
                                  last=s(l), adsets=int(a)) for k, w, sp, l, a in zip(g.concept_key, g.weeks, g.spend, g.last, g.adsets)])
    for p, g in G.groupby("persona"):
        act = g[g.active.astype(str).isin(["True", "true"])]
        sp = pd.to_numeric(act.spend_last, errors="coerce").fillna(0)
        ro = pd.to_numeric(act.roas_last, errors="coerce").fillna(0)
        P.setdefault(p, {}).update(live_adsets=int(len(act)), adsets_ever=int(len(g)), spend=num(sp.sum(), 0),
                                   roas=num((sp * ro).sum() / sp.sum(), 3) if sp.sum() else None,
                                   last_week=s(g.last_week.max()))
    return dict(generated=date.today().isoformat(), cards=pz.load_cards(), personas=P)


def snapshot_doc(queue):
    """A compact copy of this week's queue, kept forever in the board's `history` collection."""
    return dict(week=queue["adset_week"], generated=queue["generated"], capacity=queue["capacity"], bar=queue["bar"]["green"],
                facts={k: queue["facts"].get(k) for k in ("tickets_open", "tickets_need_refresh", "tickets_fading", "tickets_review", "hit_rate", "capacity_per_week")},
                tickets=[dict(id=t["id"], adset=t["adset"], persona=t["persona"], type=t["type"], rank=t["rank"], spend=t["spend"], roas=t["roas"],
                              reign=t["reign"], strikes=t["strikes"], weeks_under=t["weeks_under"], fading=t["fading"], top=t["top_code"])
                         for t in queue["tickets"]])


def main():
    os.makedirs(BOARD, exist_ok=True)
    q = None
    for name, fn in (("queue", queue_doc), ("people", people_doc), ("codes", codes_doc), ("log", log_doc),
                     ("archive", archive_doc), ("personas", personas_doc)):
        doc = fn()
        q = doc if name == "queue" else q
        path = os.path.join(BOARD, f"{name}.json")
        with open(path, "w") as f:
            json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
        print(f"{name}.json {os.path.getsize(path) / 1024:.0f} KB")
    snap = snapshot_doc(q)
    path = os.path.join(BOARD, f"history_{snap['week']}.json")
    with open(path, "w") as f:
        json.dump(snap, f, ensure_ascii=False, separators=(",", ":"))
    print(f"history_{snap['week']}.json {os.path.getsize(path) / 1024:.0f} KB  → board collection history/{snap['week']}")


if __name__ == "__main__":
    main()
