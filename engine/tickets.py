"""Ticket queue: one ticket per adset that needs creative, ranked by severity × size (spec §20).

A ticket answers the two questions Notion couldn't: what to refresh next, and using what.
  * what: every live, judged Meta adset gets a type from its status, its #1's reign and its strikes:
    Decaying (hurting now: under the bar, falling, or hook/IPM down 20%+), Due (healthy, but its #1 has
    led 2+ weeks; brief the successor now), 3 strikes (three misses in a row while under the bar), or Watch;
    its #1 concept's reign, the challengers already in test, and its strike count;
  * using what: the adset's own past #1s (J2 shape-shift material) and concepts that are winning
    elsewhere in the same persona or language but never ran here (J1 cross-pollination).
Dark adsets that were switched off while beating their OS average become Resurrection candidates.

At-bat = new concepts entering an adset in the same week, once the adset is 3+ weeks old (spec §6.1).
Rule (creative lead, 27 Oct): one concept per refresh, landing in each adset with 3+ variants (hooks, text,
re-cuts); add a proven J1 concept when there is one. `variants` = distinct ads with spend in the adset in the
concept's first 2 weeks there (zero-spend variants aren't in the export).
Verdicts (spec §6.2, back-tested 27 Oct 2026):
  * week 1, provisional: 20%+ of adset spend = provisional hit (79% go on to become #1);
    under 20% = provisional strike, kept alive (about 1 in 8 of those under 5% still becomes #1);
  * week 4, final: hit if one of the at-bat's concepts became the adset's #1 within 4 weeks;
  * late hit: #1 in weeks 5–12 turns a strike into a late hit (logged, not erased).
Outputs: output/data/tk_queue.csv, tk_atbats.csv, tk_candidates.csv, tk_resurrect.csv, tk_facts.csv.
Weights are proposals (settings.TICKET_WEIGHTS): the creative lead tunes them.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creative_relay as cr  # noqa: E402
from adload import load_ads  # noqa: E402
from adparse import parse_ad  # noqa: E402
from settings import TICKET_WEIGHTS as W, ATBAT, bar  # noqa: E402
from codes import concept_keys  # noqa: E402
import incidents  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "output", "data")
ROOT = os.path.dirname(HERE)


def concept_weeks():
    """adset × week × concept with share, rank, weeks since the concept entered the adset."""
    c, attrs, meta, last_day = cr.load()
    c["os"] = c.adset_id.map(meta.as_os).fillna("Other")
    acc = c.groupby(["week", "os"]).agg(s=("spend", "sum"), r=("rev", "sum"))
    acc["ar"] = acc.r / acc.s
    A = c.groupby(["adset_id", "week"]).agg(as_s=("spend", "sum"), as_r=("rev", "sum")).reset_index()
    A["os"] = A.adset_id.map(meta.as_os).fillna("Other")
    A = A.join(acc["ar"].rename("acc"), on=["week", "os"])
    A["rel"] = (A.as_r / A.as_s) / A.acc
    c = c.merge(A[["adset_id", "week", "as_s", "rel"]], on=["adset_id", "week"])
    c["share"] = c.spend / c.as_s
    c["rank"] = c.groupby(["adset_id", "week"]).spend.rank(ascending=False, method="first")
    fin = c[c.spend > 0].groupby(["adset_id", "concept_key"]).week.min().rename("first_in")
    c = c.join(fin, on=["adset_id", "concept_key"])
    c["wk"] = (pd.to_datetime(c.week) - pd.to_datetime(c.first_in)).dt.days // 7
    names = attrs.set_index("concept_key")["cname"].fillna("")
    return c, A, meta, names


def variant_weeks():
    """adset × concept × week → distinct ads (variants) with spend."""
    d = load_ads()
    d = d[d.spend > 0]
    P = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d.ad_name.unique()])[["ad_name", "concept", "conceptname", "ad_clean"]]
    d = d.merge(P, on="ad_name", how="left")
    d["concept_key"] = concept_keys(d)
    mid = d.start + (d.end - d.start) / 2
    d["week"] = (mid - pd.to_timedelta(mid.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")
    return d.groupby(["adset_id", "concept_key", "week"]).ad_clean.apply(set)


def at_bats(c, A):
    """One row per at-bat (concepts entering an adset in the same week, adset 3+ weeks old)."""
    weeks = sorted(c.week.unique())
    last = weeks[-1]
    A_os = A.drop_duplicates("adset_id").set_index("adset_id").os.to_dict()
    born = A[A.as_s > 0].groupby("adset_id").week.min()
    arr = c[(c.wk == 0) & (c.as_s >= ATBAT["adset_min"]) & (c.spend >= ATBAT["concept_min"])][
        ["adset_id", "concept_key", "week", "share"]].rename(columns={"week": "w0", "share": "s1"})
    arr["adset_age"] = (pd.to_datetime(arr.w0) - pd.to_datetime(arr.adset_id.map(born))).dt.days // 7
    arr = arr[arr.adset_age >= ATBAT["adset_age"]]
    tops = c[c["rank"] == 1][["adset_id", "concept_key", "week", "wk"]]
    m = arr.merge(tops, on=["adset_id", "concept_key"], how="left")
    m = m[m.week.isna() | (m.week >= m.w0)]
    arr = arr.join(m.groupby(["adset_id", "concept_key"]).wk.min().rename("wk_top"), on=["adset_id", "concept_key"])
    arr["age"] = (pd.to_datetime(last) - pd.to_datetime(arr.w0)).dt.days // 7
    V = variant_weeks()
    nxt = lambda w: (pd.to_datetime(w) + pd.Timedelta(weeks=1)).strftime("%Y-%m-%d")
    arr["variants"] = [len(V.get((a, k, w), set()) | V.get((a, k, nxt(w)), set())) for a, k, w in zip(arr.adset_id, arr.concept_key, arr.w0)]
    D = arr.groupby(["adset_id", "w0"]).agg(
        variants=("variants", "sum"), variants_max=("variants", "max"),
        concepts=("concept_key", "size"), codes=("concept_key", lambda s: " ".join(k.replace("name:", "")[:24] for k in s)),
        best_s1=("s1", "max"), wk_top=("wk_top", "min"), age=("age", "first")).reset_index()
    D = D.sort_values(["adset_id", "w0"]).reset_index(drop=True)
    final = D.age >= ATBAT["final_week"]
    D["verdict"] = np.select(
        [final & (D.wk_top <= ATBAT["final_week"]),
         final & (D.wk_top > ATBAT["final_week"]) & (D.wk_top <= ATBAT["late_week"]),
         final,
         D.wk_top.notna() | (D.best_s1 >= ATBAT["w1_hit_share"])],
        ["Hit", "Late hit", "Strike", "Hit (provisional)"], "Strike (provisional)")
    D["counts_as_hit"] = D.verdict.isin(["Hit", "Late hit", "Hit (provisional)"])
    # landed in an app/tracking incident week (core/incidents.csv): a miss there says nothing about the creative
    D["incident"] = [";".join(incidents.affecting(w, A_os.get(a, "all"))) for a, w in zip(D.adset_id, D.w0)] if len(D) else []
    void = (D.incident != "") & ~D.counts_as_hit
    D.loc[void, "verdict"] = np.where(D.loc[void, "verdict"].str.contains("provisional"), "Void (incident, provisional)", "Void (incident)")
    # adset relative ROAS weeks 3–4 after vs the 2 weeks before (home run = hit that lifted the adset)
    rel = A.set_index(["adset_id", "week"]).rel

    def gm(aid, w, ks):
        v = [rel.get((aid, (pd.to_datetime(w) + pd.Timedelta(weeks=k)).strftime("%Y-%m-%d")), np.nan) for k in ks]
        v = [x for x in v if pd.notna(x) and x > 0]
        return float(np.exp(np.mean(np.log(v)))) if v else np.nan
    D["rel_before"] = [gm(a, w, [-2, -1]) for a, w in zip(D.adset_id, D.w0)]
    D["rel_after"] = [gm(a, w, [3, 4]) if g >= 5 else np.nan for a, w, g in zip(D.adset_id, D.w0, D.age)]
    D["adset_lift"] = D.rel_after / D.rel_before - 1
    D.loc[(D.verdict == "Hit") & (D.adset_lift >= 0), "verdict"] = "Home run"
    # spread: a concept's landings in established adsets within 2 weeks of its first one
    f = arr.groupby("concept_key").w0.min()
    L = arr[(pd.to_datetime(arr.w0) - pd.to_datetime(arr.concept_key.map(f))).dt.days <= 14]
    sp = L.groupby("concept_key").adset_id.nunique()
    L = L.assign(spread=L.concept_key.map(sp), won=L.wk_top <= ATBAT["final_week"])
    Lf = L[L.age >= ATBAT["final_week"]]
    g = Lf.groupby("concept_key").agg(spread=("spread", "first"), any_won=("won", "max"))
    at_bats.spread = dict(
        adsets_per_concept_median=float(sp.median()), share_2plus=float((sp >= 2).mean()),
        landing_win_rate=float(Lf.won.mean()), won_anywhere_1=float(g[g.spread == 1].any_won.mean()),
        won_anywhere_5plus=float(g[g.spread >= 5].any_won.mean()))
    return D, last


def count_strikes(D, G):
    """Strikes count only in a turnaround: at-bats taken while the adset was under the green bar of
    its own ruler (the week before). A challenger that fails to unseat a healthy #1 is a foul ball:
    it stays in the people and concept records but doesn't push the adset toward Review.
    The run resets on a hit, or when the adset is back on green for 2 weeks in a row."""
    rcols = sorted(c for c in G.columns if c.startswith("r_"))
    wk = [c[2:] for c in rcols]
    R = G.set_index("adset_id")[rcols].apply(pd.to_numeric, errors="coerce")
    R.columns = wk
    osm = G.set_index("adset_id").os
    green = pd.DataFrame({w: [bar(w, o)["green"] for o in osm.reindex(R.index)] for w in wk}, index=R.index)
    under = (R < green) & R.notna()
    ok = (R >= green) & R.notna()
    D["context"] = ""
    run_now, before = {}, []
    for aid, g in D.groupby("adset_id", sort=False):
        k = 0
        prev_w = None
        for i, r in g.iterrows():
            w = r.w0
            wprev = (pd.to_datetime(w) - pd.Timedelta(weeks=1)).strftime("%Y-%m-%d")
            wprev2 = (pd.to_datetime(w) - pd.Timedelta(weeks=2)).strftime("%Y-%m-%d")
            if aid in ok.index and wprev in ok.columns and wprev2 in ok.columns and ok.at[aid, wprev] and ok.at[aid, wprev2]:
                k = 0
            turnaround = bool(aid in under.index and wprev in under.columns and under.at[aid, wprev])
            D.at[i, "context"] = "turnaround" if turnaround else "challenger"
            D.at[i, "strikes_before"] = k
            if r.counts_as_hit:
                k = 0
            elif turnaround and not str(r.verdict).startswith("Void"):
                k += 1
        # back on green since the last at-bat?
        last2 = [c for c in ok.columns][-2:]
        if aid in ok.index and all(ok.at[aid, c] for c in last2):
            k = 0
        run_now[aid] = k
    D.loc[(D.context == "challenger") & D.verdict.str.startswith("Strike"), "verdict"] = \
        D.verdict.str.replace("Strike", "Foul", regex=False)
    return run_now


def candidates(c, meta, names, adset_ids, recent_from):
    """J1: concepts that were #1 elsewhere (same persona first, then same language) and never ran in the adset."""
    tops = c[(c["rank"] == 1) & (c.week >= recent_from) & (c.as_s >= 500)].copy()
    tops["persona"] = tops.adset_id.map(meta.as_persona)
    tops["lang"] = tops.adset_id.map(meta.as_lang)
    won = tops.groupby(["concept_key", "persona", "lang"]).agg(spend_as_1=("spend", "sum"), weeks_as_1=("week", "size"),
                                                               last_as_1=("week", "max"),
                                                               rel=("rel", "median")).reset_index()
    won = won[~won.concept_key.str.startswith("name:")]
    norm = lambda k: str(names.get(k, "")).lower().replace(" ", "")
    ran = c[c.spend > 0].groupby("adset_id").concept_key.apply(set)
    rows = []
    for aid in adset_ids:
        p, l = meta.as_persona.get(aid), meta.as_lang.get(aid)
        here = ran.get(aid, set())
        here_l = {k.lower() for k in here}
        here_n = {norm(k) for k in here} - {""}
        w = won[~won.concept_key.str.lower().isin(here_l) & ~won.concept_key.map(norm).isin(here_n)].copy()
        w["fit"] = np.select([(w.persona == p) & (w.lang == l), w.persona == p, w.lang == l], [3, 2, 1], 0)
        w = w[w.fit > 0]
        if w.empty:
            continue
        g = w.groupby("concept_key").agg(fit=("fit", "max"), spend_as_1=("spend_as_1", "sum"),
                                         weeks_as_1=("weeks_as_1", "sum"), last_as_1=("last_as_1", "max"),
                                         where=("persona", lambda s: ", ".join(sorted(set(s))[:3]))).reset_index()
        g = g.sort_values(["fit", "spend_as_1"], ascending=False).head(3)
        for i, r in enumerate(g.itertuples(), 1):
            rows.append(dict(adset_id=aid, n=i, code=r.concept_key.replace("name:", ""), name=names.get(r.concept_key, ""),
                             fit={3: "same persona + language", 2: "same persona", 1: "same language"}[r.fit],
                             won_in=r.where, spend_as_1=r.spend_as_1, weeks_as_1=r.weeks_as_1, last_as_1=r.last_as_1))
    return pd.DataFrame(rows)


def short_label(row):
    sub = row.get("subangle") or ""
    return f"{row['persona']} · {row['os']} · {row['lang']}" + (f" · {sub}" if sub and sub not in ("General", "Mixed") else "")


def main():
    os.makedirs(OUT, exist_ok=True)
    c, A, meta, names = concept_weeks()
    D, last_ad_week = at_bats(c, A)
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"].copy()
    run_now = count_strikes(D, G)
    G["active_b"] = G.active.astype(str).isin(["True", "true"])
    G["judged_b"] = G.judged.astype(str).isin(["True", "true"])
    G["low_ceiling_b"] = G.low_ceiling.astype(str).isin(["True", "true"])
    for col in ("spend_last", "roas_last", "roas_prev", "reign_week", "top_creative_share", "severity", "leaking"):
        G[col] = pd.to_numeric(G[col], errors="coerce")
    live = G[G.active_b & G.judged_b & (G.spend_last >= W["min_spend"])].copy()
    # weeks under the bar in a row, up to the latest week (each week on its own ruler)
    rc = sorted(c_ for c_ in G.columns if c_.startswith("r_"))
    def weeks_under(row, span=False):
        n = 0
        for col in reversed(rc):
            v = pd.to_numeric(row[col], errors="coerce")
            if pd.isna(v) or v >= bar(col[2:], row["os"])["green"]:
                break
            if not span and incidents.affecting(col[2:], row["os"]):
                continue        # under the bar in an incident week: not counted, doesn't break the run
            n += 1
        return n
    live["weeks_under"] = live.apply(weeks_under, axis=1)
    live["under_span"] = live.apply(weeks_under, axis=1, span=True)     # calendar weeks since it went under
    last_ab = D.groupby("adset_id").w0.max()

    # challengers in test: at-bats in the last 2 ad weeks
    recent = D[D.age <= 1].groupby("adset_id").agg(test_codes=("codes", " | ".join), test_best_s1=("best_s1", "max"),
                                                   test_verdict=("verdict", "last"), test_since=("w0", "min"))
    last_hit = D[D.counts_as_hit].groupby("adset_id").w0.max()
    since8 = (pd.to_datetime(last_ad_week) - pd.Timedelta(weeks=8)).strftime("%Y-%m-%d")
    tried8 = D[D.w0 > since8].groupby("adset_id").size()
    rows = []
    for r in live.itertuples():
        aid = r.adset_id
        sev = int(r.severity)
        strikes = run_now.get(aid, 0)
        in_test = aid in recent.index
        reign = r.reign_week if pd.notna(r.reign_week) else 0
        falling = pd.notna(r.roas_prev) and pd.notna(r.roas_last) and r.roas_last < r.roas_prev
        if strikes >= W["review_strikes"]:
            typ, w = "3 strikes", W["review"]
        elif sev == 1:
            typ, w = "Decaying", W["critical"]
        elif sev == 2:
            typ, w = "Decaying", W["amber_falling"]
        elif sev == 3:
            typ, w = "Decaying", W["leading_signal"]
        elif sev == 4:   # under the bar, not falling: still Decaying (an old #1 makes it more urgent)
            typ, w = "Decaying", max(W["amber"], W["due"] if reign >= W["due_reign"] else 0)
        elif sev == 5:   # critical but under the alert floor (small)
            typ, w = "Decaying", W["critical_small"]
        elif reign >= W["due_reign"]:   # healthy: the #1 is ageing
            typ, w = "Due", W["due"] + (W["due_falling_bonus"] if falling else 0)
        else:
            typ, w = "Watch", 0.0
        if typ == "Watch":
            continue
        score = w * r.spend_last
        notes = []
        if in_test and typ != "3 strikes":
            score *= W["in_test_factor"]
            notes.append("challenger already in test")
        inc = incidents.affecting(rc[-1][2:], r.os)
        if inc:
            notes.append("incident in the latest week (" + ", ".join(inc) + "): read the drop with care")
        if r.low_ceiling_b:
            score *= W["low_ceiling_factor"]
            notes.append("🧱 low ceiling: check beyond creative first")
        state = ("REVIEW" if typ == "3 strikes" else "TESTING" if in_test else "NEED REFRESH")
        rows.append(dict(
            adset_id=aid, ticket=f"T-{aid[-10:-4]}", type=typ, state=state, score=round(score, 1),
            adset=short_label(r._asdict()), persona=r.persona, lang=r.lang, os=r.os, name=r.name,
            status=r.status, why=r.why, spend_last=r.spend_last, roas_last=r.roas_last, roas_prev=r.roas_prev,
            top_code=r.top_creative, top_name=r.top_creative_name, top_share=r.top_creative_share, reign_week=reign,
            strikes=strikes, last_hit=last_hit.get(aid, ""), tried_8w=int(tried8.get(aid, 0)),
            weeks_under=int(r.weeks_under),
            fading=bool(r.weeks_under >= 2 and not in_test and (aid not in last_ab.index or
                        (pd.to_datetime(last_ad_week) - pd.to_datetime(last_ab[aid])).days // 7 >= r.under_span)),
            in_test=recent.test_codes.get(aid, "") if in_test else "",
            test_week1_share=recent.test_best_s1.get(aid, np.nan) if in_test else np.nan,
            test_verdict=recent.test_verdict.get(aid, "") if in_test else "",
            low_ceiling=r.low_ceiling_b, notes="; ".join(notes)))
    Q = pd.DataFrame(rows)
    # Review tickets sit on top, then by score
    Q["pin"] = (Q.type == "3 strikes").astype(int)
    Q = Q.sort_values(["pin", "score"], ascending=False).drop(columns="pin").reset_index(drop=True)
    Q.insert(0, "rank", range(1, len(Q) + 1))
    # siblings: same persona + language, other adsets with a ticket → brief together
    Q["brief_with"] = [", ".join(Q[(Q.persona == p) & (Q.lang == l) & (Q.ticket != t)].ticket.head(3))
                       for p, l, t in zip(Q.persona, Q.lang, Q.ticket)]
    # J2 material: this adset's last 3 #1s
    tops = c[c["rank"] == 1].sort_values("week")
    hist, pastj = {}, {}
    for aid, g in tops.groupby("adset_id"):
        runs = (g.concept_key != g.concept_key.shift()).cumsum()
        rr = g.groupby(runs).agg(code=("concept_key", "first"), start=("week", "min"), weeks=("week", "size"))
        rr = rr.tail(4).iloc[:-1] if len(rr) > 1 else rr.iloc[0:0]
        hist[aid] = " · ".join(f"{k.replace('name:', '')[:14]} ({names.get(k, '')[:16]}, {n} wk)" for k, n in zip(rr.code, rr.weeks))
        pastj[aid] = json.dumps([dict(code=k.replace("name:", "")[:24], name=str(names.get(k, ""))[:24], weeks=int(n), start=st)
                                 for k, n, st in zip(rr.code, rr.weeks, rr.start)])
    Q["past_no1"] = Q.adset_id.map(hist).fillna("")
    # clocks: when the current #1 took over, and when a new concept last entered (a refresh)
    since = {}
    for aid, g in tops.groupby("adset_id"):
        runs = (g.concept_key != g.concept_key.shift()).cumsum()
        since[aid] = g[runs == runs.iloc[-1]].week.min()
    Q["reign_since"] = Q.adset_id.map(since).fillna("")
    cw = c[c.wk <= 1].groupby(["adset_id", "concept_key"]).agg(first=("first_in", "first"), sp=("spend", "sum")).reset_index()
    cw = cw[cw.sp >= ATBAT["concept_min"]]
    data_start = c.groupby("adset_id").week.min()
    lastnew = cw.groupby("adset_id")["first"].max()
    Q["last_refresh"] = Q.adset_id.map(lastnew).fillna("")
    Q["data_start"] = Q.adset_id.map(data_start).fillna("")
    Q["past_json"] = Q.adset_id.map(pastj).fillna("[]")
    recent_from = (pd.to_datetime(last_ad_week) - pd.Timedelta(weeks=8)).strftime("%Y-%m-%d")
    C = candidates(c, meta, names, Q.adset_id.tolist(), recent_from)
    if not C.empty:
        C = C.merge(Q[["adset_id", "ticket"]], on="adset_id")
        first = C[C.n == 1].set_index("adset_id")
        Q["j1_first"] = Q.adset_id.map(first.code + " " + first.name.str[:18] + " (" + first.fit + ")").fillna("")
    else:
        Q["j1_first"] = ""

    # capacity: at-bats the team lands per week (last 8 complete ad weeks)
    wk8 = sorted(D.w0.unique())[-8:]
    cap = D[D.w0.isin(wk8)].groupby("w0").size().mean()

    # resurrection: adsets switched off since the switch while at or above their OS average
    rz = pd.read_csv(os.path.join(OUT, "era_cuts.csv"), dtype={"adset_id": str})
    rz = rz[rz.rel_last4 >= 1.0].copy()
    rz["adset"] = rz.adset_id.map(lambda a: short_label(dict(persona=meta.as_persona.get(a, ""), os=meta.as_os.get(a, ""),
                                                             lang=meta.as_lang.get(a, ""), subangle="")))
    rz["mission"] = "Resurrection: relaunch with the persona's freshest winner, or write the obituary"
    rz = rz.sort_values("peak_wk", ascending=False)

    # silent deaths: adsets (v8, 6+ live weeks, peak $1k+/wk) switched off with no new concept in their last 6 live weeks
    newc = c[(c.wk == 0) & (c.spend >= 20)].groupby("adset_id").week.apply(set)
    born = c[c.as_s > 0].groupby("adset_id").week.min()
    scol = sorted(x for x in G.columns if x.startswith("s_"))
    gw = [x[2:] for x in scol]
    S = G.set_index("adset_id")[scol].apply(pd.to_numeric, errors="coerce").fillna(0)
    S.columns = gw
    dead, silent = 0, 0
    for aid, sv in S.iterrows():
        on = sv[sv > 0]
        if len(on) < 6 or on.index.max() >= gw[-3] or sv.max() < 1000 or G.set_index("adset_id").version.get(aid) != "v8" \
                or not G.set_index("adset_id").judged_b.get(aid):
            continue
        w6 = [w for w in gw if w <= on.index.max()][-6:]
        b = born.get(aid)
        dead += 1
        silent += not any(w6[0] <= w <= w6[-1] and b is not None and w > b for w in newc.get(aid, set()))

    # facts for the spec and the weekly note
    fin = D[(D.age >= ATBAT["final_week"]) & ~D.verdict.str.startswith("Void")]
    one = fin[fin.concepts == 1]
    multi = fin[fin.concepts >= 2]
    facts = [
        ("atbats_final", len(fin), "Refresh at-bats with a final verdict (adset 3+ weeks old, 4+ weeks of data)"),
        ("hit_rate", fin.verdict.isin(["Hit", "Home run"]).mean(), "Share that produced a new #1 within 4 weeks"),
        ("home_run_rate", (fin.verdict == "Home run").mean(), "Share that produced a new #1 and lifted the adset's relative ROAS (weeks 3–4)"),
        ("late_hit_rate", (fin.verdict == "Late hit").mean(), "Share whose concept became #1 only in weeks 5–12"),
        ("hit_rate_3var", fin[fin.variants_max >= 3].verdict.isin(["Hit", "Home run"]).mean(), "Hit rate, at-bats whose concept landed with 3+ variants"),
        ("hit_rate_12var", fin[fin.variants_max < 3].verdict.isin(["Hit", "Home run"]).mean(), "Hit rate, at-bats with only 1–2 variants per concept"),
        ("n_3var", int((fin.variants_max >= 3).sum()), "At-bats whose concept landed with 3+ variants"),
        ("share_3var_recent", (D[D.w0 >= sorted(D.w0.unique())[-8]].variants_max >= 3).mean(), "Share of at-bats in the last 8 weeks that landed with 3+ variants"),
        ("hit_rate_1concept", one.verdict.isin(["Hit", "Home run"]).mean(), "Hit rate, at-bats with one concept"),
        ("hit_rate_2plus", multi.verdict.isin(["Hit", "Home run"]).mean(), "Hit rate, at-bats with two or more concepts"),
        ("n_1concept", len(one), "At-bats with one concept"),
        ("n_2plus", len(multi), "At-bats with two or more concepts"),
        ("chance_3_misses_1concept", (1 - one.verdict.isin(["Hit", "Home run"]).mean()) ** 3, "Chance of 3 misses in a row by luck alone, one-concept at-bats"),
        ("chance_3_misses_2plus", (1 - multi.verdict.isin(["Hit", "Home run"]).mean()) ** 3, "Chance of 3 misses in a row by luck alone, 2+ concept at-bats"),
        ("v8_adsets_off", dead, "v8 adsets switched off (6+ live weeks, peak $1k+/week)"),
        ("v8_adsets_off_no_new_concept", silent, "... of which got no new concept in their last 6 live weeks"),
        ("turnaround_second_swing", (D[D.context == "turnaround"].strikes_before >= 1).sum(), "Turnaround at-bats that came after a missed turnaround at-bat"),
        ("turnaround_atbats", (D.context == "turnaround").sum(), "At-bats taken while the adset was under the green bar"),
        ("turnaround_hit_1concept", fin[(fin.context == "turnaround") & (fin.concepts == 1)].verdict.isin(["Hit", "Home run"]).mean(), "Turnaround hit rate, one concept"),
        ("turnaround_hit_2plus", fin[(fin.context == "turnaround") & (fin.concepts >= 2)].verdict.isin(["Hit", "Home run"]).mean(), "Turnaround hit rate, two or more concepts"),
        ("adsets_per_concept_median", at_bats.spread["adsets_per_concept_median"], "Established adsets a new concept lands in within 2 weeks (median)"),
        ("concepts_2plus_adsets", at_bats.spread["share_2plus"], "Share of concepts landing in 2+ established adsets"),
        ("landing_win_rate", at_bats.spread["landing_win_rate"], "Share of landings (concept × adset) that became the adset's #1 within 4 weeks"),
        ("won_anywhere_1", at_bats.spread["won_anywhere_1"], "Concepts in 1 adset: became #1 somewhere"),
        ("won_anywhere_5plus", at_bats.spread["won_anywhere_5plus"], "Concepts in 5+ adsets: became #1 somewhere"),
        ("capacity_per_week", cap, "At-bats landed per week, last 8 ad weeks"),
        ("tickets_open", len(Q), "Open tickets"),
        ("tickets_need_refresh", (Q.state == "NEED REFRESH").sum(), "Tickets with nothing in test"),
        ("tickets_fading", int(Q.fading.sum()), "Tickets under the bar 2+ weeks in a row with no new concept since it went under"),
        ("tickets_review", (Q.type == "3 strikes").sum(), "Tickets at 3+ turnaround strikes in a row"),
        ("brief_groups_need_refresh", Q[Q.state == "NEED REFRESH"].groupby(["persona", "lang"]).ngroups, "Persona × language groups among tickets that need a brief (one brief can serve the group)"),
        ("turnaround_hit_rate", fin[fin.context == "turnaround"].verdict.isin(["Hit", "Home run"]).mean(), "Hit rate of at-bats taken while the adset was under the green bar"),
        ("challenger_hit_rate", fin[fin.context == "challenger"].verdict.isin(["Hit", "Home run"]).mean(), "Hit rate of at-bats into adsets on green"),
        ("last_ad_week", 0, last_ad_week),
    ]
    Q.to_csv(os.path.join(OUT, "tk_queue.csv"), index=False, float_format="%.4f")
    D.to_csv(os.path.join(OUT, "tk_atbats.csv"), index=False, float_format="%.4f")
    C.to_csv(os.path.join(OUT, "tk_candidates.csv"), index=False, float_format="%.2f")
    rz[["adset_id", "adset", "name", "last_week", "peak_wk", "rel_last4", "persona_fate", "mission"]].to_csv(
        os.path.join(OUT, "tk_resurrect.csv"), index=False, float_format="%.4f")
    pd.DataFrame(facts, columns=["fact", "value", "label"]).to_csv(os.path.join(OUT, "tk_facts.csv"), index=False, float_format="%.4f")
    print(f"tickets: {len(Q)} open ({(Q.state == 'NEED REFRESH').sum()} need a brief), capacity ≈ {cap:.1f} at-bats/week")


if __name__ == "__main__":
    main()
