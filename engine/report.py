"""The Tuesday report: one document per week, in the order of the team's deck (spec §20.7).

  01 Team output        what the team made last week (board handoffs; Notion until the board has them)
  02 Results            refreshes that got their week-1 read, and final verdicts reached this week
  03 New personas and expansions   adsets launched in the last 4 weeks, read like the deck's persona slides
  04 Refresh and iteration          the refresh cards from 02 that landed in established adsets
  05 TikTok             channel numbers and ad groups (creative view needs the TikTok ad export)
  06 This week          the queue above the capacity line, fading tickets, persona groups, decisions
  Money check           spend by channel, store proceeds, ROAS vs the bar

Every insight and action is a *draft* written from the numbers; the presenter edits it on the board.
Output: output/board/report_<adset week>.json → board collection reports/<week>.
"""
from __future__ import annotations

import glob
import json
import os
import sys
from datetime import date, timedelta

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from settings import bar, BARS  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output", "data")
BOARD = os.path.join(ROOT, "output", "board")


def num(x, nd=3):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(v) else round(v, nd)


def s(x):
    return "" if x is None or (isinstance(x, float) and not np.isfinite(x)) or str(x) == "nan" else str(x)


def money(v):
    return "–" if v is None else (f"${v / 1000:.1f}k" if abs(v) >= 1000 else f"${v:,.0f}")


def pct(v):
    return "–" if v is None else f"{v * 100:.0f}%"


def main():
    import tickets as tk
    c, A, meta, names = tk.concept_weeks()
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"].set_index("adset_id")
    aw = pd.read_pickle(os.path.join(ROOT, "data", "model", "adset_week.pkl"))
    aw["adset_id"] = aw.adset_id.astype(str)
    aw["os"] = aw.adset_id.map(G.os)
    wk = sorted(aw.week.unique())
    W, Wp = wk[-1], wk[-2]
    ad_weeks = sorted(c.week.unique())
    AW = ad_weeks[-1]
    green = BARS["singular"]["green"]

    # account per OS per week (for relative funnel reads)
    acc = aw.groupby(["week", "os"]).agg(sp=("spend", "sum"), rv=("rev", "sum"), im=("impressions", "sum"),
                                         ins=("installs", "sum"), clk=("clicks", "sum"))
    def funnel(sp, rv, im, ins, clk):
        return dict(spend=num(sp, 0), roas=num(rv / sp) if sp else None, ctr=num(clk / im, 4) if im else None,
                    c2i=num(ins / clk) if clk else None, ipm=num(ins / im * 1000, 2) if im else None)
    def adset_row(aid, w):
        r = aw[(aw.adset_id == aid) & (aw.week == w)]
        if r.empty:
            return None
        r = r.iloc[0]
        f = funnel(r.spend, r.rev, r.impressions, r.installs, r.clicks)
        a = acc.loc[(w, r.os)] if (w, r.os) in acc.index else None
        if a is not None:
            fa = funnel(a.sp, a.rv, a.im, a.ins, a.clk)
            f["vs"] = {k: (num(f[k] / fa[k], 2) if f.get(k) and fa.get(k) else None) for k in ("roas", "ctr", "c2i", "ipm")}
        f["os"] = s(G.os.get(aid, ""))
        f["label"] = f"{G.persona.get(aid, '')} · {G.os.get(aid, '')} · {G.lang.get(aid, '')}"
        return f
    def flags(f):
        out = []
        v = (f or {}).get("vs") or {}
        if v.get("ctr") and v.get("c2i") and v["ctr"] >= 1.5 and v["c2i"] <= 0.6:
            out.append("Many clicks, few installs: check for bot clicks, the store page, or the install signal")
        elif v.get("c2i") and v["c2i"] <= 0.6:
            out.append("Click → install is low against its OS: the store page or the promise in the ad may not match")
        if v.get("ipm") and v["ipm"] <= 0.6 and not out:
            out.append("Few installs per impression: the creative isn't converting attention into installs")
        if v.get("c2i") and v["c2i"] >= 0.9 and v.get("roas") and v["roas"] <= 0.8:
            out.append("Installs arrive but don't buy: audience or offer, not the hook")
        return out
    def siblings(aid):
        p, l = G.persona.get(aid), G.lang.get(aid)
        sib = G[(G.persona == p) & (G.lang == l) & (G.index != aid) & G.active.astype(str).isin(["True", "true"])]
        return [x for x in (adset_row(i, W) for i in sib.index[:2]) if x]
    def top_creatives(aid, w=AW, n=3):
        x = c[(c.adset_id == aid) & (c.week == w)].sort_values("spend", ascending=False).head(n)
        return [dict(code=k.replace("name:", "")[:24], name=s(names.get(k, ""))[:24], share=num(sh), roas=num(rv / sp) if sp else None,
                     ctr=num(clk / im, 4) if im else None, ipm=num(ins / im * 1000, 2) if im else None)
                for k, sh, rv, sp, clk, im, ins in zip(x.concept_key, x.share, x.rev, x.spend, x.clk, x.imp, x.ins)]

    # ---- 02/04 results: week-1 reads in the last 2 ad weeks + final verdicts this week ----
    D = pd.read_csv(os.path.join(OUT, "tk_atbats.csv"), dtype={"adset_id": str})
    Q = pd.read_csv(os.path.join(OUT, "tk_queue.csv"), dtype={"adset_id": str})
    C = pd.read_csv(os.path.join(OUT, "tk_candidates.csv"), dtype={"adset_id": str})
    fin_w = (pd.to_datetime(AW) - pd.Timedelta(weeks=4)).strftime("%Y-%m-%d")
    recent = D[D.w0.isin(ad_weeks[-2:])].copy()
    final = D[D.w0 == fin_w].copy()
    def card(r, kind):
        aid = r.adset_id
        before = (pd.to_datetime(r.w0) - pd.Timedelta(weeks=1)).strftime("%Y-%m-%d")
        now = adset_row(aid, W)
        prev = adset_row(aid, before)
        v, s1 = s(r.verdict), num(r.best_s1)
        qrow = Q[Q.adset_id == aid]
        strikes = int(qrow.strikes.iloc[0]) if len(qrow) else None
        j1 = C[C.adset_id == aid].sort_values("n").head(2)
        j1t = ", ".join(f"{a} {b}" for a, b in zip(j1.code, j1.name.fillna("")))
        codes = s(r.codes)
        named = ", ".join(f"{k} {names.get(k, names.get('name:' + k, ''))}".strip() for k in codes.split())
        if v.startswith("Home run"):
            ins = f"Became the adset's #1 and its ROAS rose against its OS after the takeover."
            act = "Spread it: brief it into the same persona's other languages and the other OS (J1)."
        elif v.startswith("Hit") or v.startswith("Late hit"):
            wt = r.wk_top
            if pd.notna(wt):
                ins = f"Became the adset's #1 {'in its first week' if wt == 0 else f'in week {int(wt) + 1}'} (it took {pct(s1)} of spend in week 1)."
            else:
                ins = f"Took {pct(s1)} of the adset's spend in week 1: on track to become #1 (8 in 10 do)."
            act = "Keep it running; brief the next form of this message (J2) and offer it to sibling adsets (J1)."
        elif v.startswith("Void"):
            ins = f"{pct(s1)} of the adset's spend in week 1, but it landed during an app/tracking incident, so the miss doesn't count."
            act = "Give it a fair read: keep it on, or re-launch it once results are back to normal."
        elif v.startswith("Strike"):
            ins = f"Only {pct(s1)} of the adset's spend in week 1 while the adset is under the bar" + (f": strike {strikes} of 3." if strikes else ".")
            act = ("Next swing with a different concept" + (f", e.g. {j1t} (winning nearby, never run here)." if j1t else ".")
                   + " Keep this one on: about 1 in 8 quiet starters still become #1.")
        else:
            ins = f"{pct(s1)} of spend in week 1: it didn't unseat a healthy #1 (a foul, no strike)."
            act = "No action. Leave it on in case it blooms late."
        fl = flags(now)
        return dict(kind=kind, adset_id=aid, adset=f"{G.persona.get(aid, '')} · {G.os.get(aid, '')} · {G.lang.get(aid, '')}",
                    persona=s(G.persona.get(aid, "")), week_in=s(r.w0), concepts=named, variants=int(r.variants_max), s1=s1,
                    verdict=v, context=s(r.context), lift=num(r.adset_lift), now=now, before=prev, siblings=siblings(aid),
                    top=top_creatives(aid), flags=fl, insight=ins + (" " + fl[0] + "." if fl else ""), action=act)
    results = [card(r, "Week-1 read") for r in recent.itertuples()] + [card(r, "Final verdict") for r in final.itertuples()]

    # ---- 03 launches: new personas and expansions (adsets first spending in the last 4 weeks) ----
    G["first_week"] = G.first_week.astype(str)
    p_first = G[G.first_week != "nan"].groupby("persona").first_week.min()
    since = wk[-4]
    L = G[(G.first_week >= since) & G.active.astype(str).isin(["True", "true"]) & G.judged.astype(str).isin(["True", "true"])]
    launches = []
    for aid, g in L.iterrows():
        tot = pd.to_numeric(pd.Series({w: g.get(f"s_{w}") for w in wk if w >= g.first_week}), errors="coerce").fillna(0)
        if tot.sum() < 500:
            continue
        rv = sum((pd.to_numeric(g.get(f"r_{w}"), errors="coerce") or 0) * tot[w] for w in tot.index if pd.notna(pd.to_numeric(g.get(f"r_{w}"), errors="coerce")))
        kind = "New persona" if p_first.get(g.persona, "") >= since else "Expansion"
        now = adset_row(aid, W)
        roas_all = rv / tot.sum() if tot.sum() else None
        state = "above the bar" if (now or {}).get("roas") and now["roas"] >= green else "under the bar"
        fl = flags(now)
        weeks_live = len(tot)
        ins = (f"{weeks_live} week{'s' if weeks_live > 1 else ''} live, {money(tot.sum())} spent, ROAS {roas_all:.2f} since launch, "
               f"{(now or {}).get('roas', 0) or 0:.2f} last week ({state}).") if roas_all is not None else ""
        if fl:
            ins += " " + fl[0] + "."
        if state == "above the bar":
            act = "Scale carefully and line up the next concept before week 3; offer the winner to other languages." if kind == "New persona" else "Keep it; brief a local-language variant set next."
        else:
            act = ("Too early to kill: give it one more refresh with the persona's proven message." if weeks_live <= 2
                   else "Decide this week: one more swing with a different concept, or pause and write it up.")
        launches.append(dict(kind=kind, adset_id=aid, adset=f"{g.persona} · {g.os} · {g.lang}" + (f" · {g.subangle}" if s(g.subangle) not in ("", "General", "Mixed") else ""),
                             persona=s(g.persona), launched=s(g.first_week), weeks=weeks_live, spend_total=num(tot.sum(), 0), roas_total=num(roas_all),
                             now=now, siblings=siblings(aid), top=top_creatives(aid), flags=fl, insight=ins, action=act))
    launches.sort(key=lambda x: -(x["spend_total"] or 0))

    # ---- 05 TikTok ----
    CW = pd.read_csv(os.path.join(OUT, "ch_weekly.csv"))
    cw4 = CW.tail(4)
    tt_last = CW.iloc[-1]
    AG = pd.read_csv(os.path.join(OUT, "ch_adgroups.csv"), dtype={"adgroup_id": str})
    top_ag = AG.sort_values("spend_last", ascending=False).head(6)
    tiktok = dict(
        week=s(tt_last.week), spend_ios=num(tt_last.tt_ios_spend, 0), spend_and=num(tt_last.tt_and_spend, 0), share=num(tt_last.tt_share),
        roas_ios=num(tt_last.tt_ios_roas), roas_and=num(tt_last.tt_and_roas),
        trend=[dict(week=s(r.week), spend=num(r.tt_ios_spend + r.tt_and_spend, 0), share=num(r.tt_share)) for r in cw4.itertuples()],
        adgroups=[dict(name=s(r.name)[:70], os=s(r.os), spend=num(r.spend_last, 0), roas=num(r.roas_last), vs_avg=num(r.rel_4w, 2)) for r in top_ag.itertuples()],
        insight=(f"TikTok spent {money((tt_last.tt_ios_spend or 0) + (tt_last.tt_and_spend or 0))} in the week of {s(tt_last.week)} "
                 f"({pct(tt_last.tt_share)} of paid spend). On ad groups that were spending, it credits itself ROAS {tt_last.tt_ios_roas:.2f} on iOS "
                 f"and {tt_last.tt_and_roas:.2f} on Android; TikTok's own number, not comparable with Meta's. App Store money follows Meta iOS spend, "
                 f"barely TikTok's: hold the budget until the geo test."),
        action="Run the geo test (pause TikTok iOS in 3–4 countries for 4 weeks). Send the TikTok ad-level export with v5 names so its creatives get verdicts too.")

    # ---- money ----
    O = pd.read_csv(os.path.join(OUT, "ov_weekly.csv"))
    meta_last = aw[aw.week == W].agg({"spend": "sum", "rev": "sum"})
    meta_4 = aw[aw.week.isin(wk[-5:-1])].groupby("week").spend.sum().mean()
    ios = aw[(aw.week == W) & (aw.os == "iOS")]; andr = aw[(aw.week == W) & (aw.os == "Android")]
    lw = json.load(open(os.path.join(BOARD, "log.json")))["weeks"]
    under = next((x["under_share"] for x in lw if x["week"] == W), None)
    st = O.dropna(subset=["store_proceeds"]).iloc[-1]
    money_ = dict(week=W, meta_spend=num(meta_last.spend, 0), meta_vs_4w=num(meta_last.spend / meta_4 - 1) if meta_4 else None,
                  roas_ios=num(ios.rev.sum() / ios.spend.sum()) if ios.spend.sum() else None,
                  roas_and=num(andr.rev.sum() / andr.spend.sum()) if andr.spend.sum() else None, bar=green,
                  under_share=under, store_week=s(st.week), store=num(st.store_proceeds, 0), tt_spend=num((tt_last.tt_ios_spend or 0) + (tt_last.tt_and_spend or 0), 0))
    money_["insight"] = (f"Meta spent {money(money_['meta_spend'])} in the week of {W} ({'+' if (money_['meta_vs_4w'] or 0) >= 0 else ''}{pct(money_['meta_vs_4w'])} vs its 4-week average). "
                         f"Meta ROAS {money_['roas_ios']:.2f} on iOS and {money_['roas_and']:.2f} on Android against the {green:.2f} bar; {pct(under)} of Meta spend sits in adsets under the bar. "
                         f"App Store proceeds {money(money_['store'])} (week of {money_['store_week']}).")

    # ---- 06 this week ----
    F = pd.read_csv(os.path.join(OUT, "tk_facts.csv")).set_index("fact")["value"]
    top = Q.head(10)
    groups = Q.groupby("persona").agg(score=("score", "sum"), spend=("spend_last", "sum"), n=("ticket", "size"),
                                      decaying=("type", lambda x: (x == "Decaying").sum())).sort_values("score", ascending=False).head(4)
    acts = pd.read_csv(os.path.join(OUT, "ov_actions.csv"))
    week_ = dict(
        capacity=num(F["capacity_per_week"], 1), open=int(F["tickets_open"]), need_brief=int(F["tickets_need_refresh"]), fading=int(F["tickets_fading"]),
        strikes3=int(F["tickets_review"]),
        top=[dict(id=r.ticket, adset=r.adset, type=r.type, spend=num(r.spend_last, 0), roas=num(r.roas_last), reign=int(r.reign_week or 0),
                  strikes=int(r.strikes), fading=bool(r.fading), why=s(r.why)) for r in top.itertuples()],
        groups=[dict(persona=p, n=int(g.n), decaying=int(g.decaying), spend=num(g.spend, 0)) for p, g in groups.iterrows()],
        decisions=[dict(action=s(r.action), owner=s(r.owner)) for r in acts.head(4).itertuples()] + [
            dict(action="Confirm the ticket ranking weights and the at-bat rules (week-1 read, week-4 verdict, 3 strikes)", owner="Creative lead"),
            dict(action="Give the raw exports a permanent folder so history can always be rebuilt", owner="Creative lead")])
    fad = Q[Q.fading].sort_values("spend_last", ascending=False)
    week_["insight"] = (f"{week_['open']} open tickets, {week_['need_brief']} without a brief, against about {week_['capacity']:.0f} refreshes a week: group them. "
                        f"Biggest groups: " + ", ".join(f"{g['persona']} ({g['n']} adsets, {money(g['spend'])}/wk)" for g in week_["groups"][:3]) + ". "
                        f"{week_['fading']} adsets are fading with no new concept since they went under the bar"
                        + (f", led by {fad.adset.iloc[0]} ({money(fad.spend_last.iloc[0])}/wk)." if len(fad) else "."))

    # ---- 01 team output (Notion until the board has handoffs) ----
    today = pd.Timestamp(date.today())
    files = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "notion", "notion_tracker_*.csv")))
    notion = []
    if files:
        T = pd.read_csv(files[-1])
        T["fin"] = pd.to_datetime(T["Finish Date"], errors="coerce")
        lastwk = T[(T.fin > today - pd.Timedelta(days=7)) & (T.fin <= today)]
        for r in lastwk.itertuples():
            notion.append(dict(title=s(getattr(r, "_1", ""))[:70], designer=s(r.Designer), campaign=s(r.Campaign)[:50], finished=s(r.fin.date())))
    output = dict(window=f"{(today - pd.Timedelta(days=7)).date()} to {today.date()}", notion=notion,
                  note="From the next Monday on, this section counts the handoffs on the board: videos, images, task counts and adsets covered.")

    n_hit = sum(1 for x in results if x["kind"] == "Week-1 read" and x["verdict"].startswith(("Hit", "Home")))
    n_read = sum(1 for x in results if x["kind"] == "Week-1 read")
    n_fin = [x for x in results if x["kind"] == "Final verdict"]
    summary = (f"{n_read} refreshes got their week-1 read (landed {ad_weeks[-2]} – {AW}): {n_hit} early hit{'s' if n_hit != 1 else ''}. "
               f"{len(n_fin)} reached their week-4 verdict (landed {fin_w}): "
               + ", ".join(f"{n} {k.lower()}{'' if n == 1 else 's'}" for k in ("Home run", "Hit", "Strike", "Foul") for n in [sum(1 for x in n_fin if x['verdict'].startswith(k))]) + ".")
    import incidents
    inc = incidents.in_window((pd.to_datetime(W) - pd.Timedelta(weeks=4)).strftime("%Y-%m-%d"), W)
    inc_list = [dict(id=r.id, start=r.start, end=r.end, effect_until=r.effect_until, os=r.os, kind=r.kind, what=r.what) for r in inc.itertuples()]
    if inc_list:
        money_["insight"] += (" App/tracking incidents in the last 5 weeks: " + incidents.label(inc.id.tolist())
                              + ". Refreshes that landed in those weeks and missed are void, not strikes.")
        n_void = sum(1 for x in results if str(x["verdict"]).startswith("Void"))
        if n_void:
            summary += f" {n_void} landed in an incident week and missed: void, not counted."
    doc = dict(week=W, generated=date.today().isoformat(), ad_week=AW, incidents=inc_list, data_note=(
        f"Adsets to the week of {W}; ads (creatives) to the week of {AW}; TikTok to {tiktok['week']}; App Store to {money_['store_week']}. "
        "Every insight and action is a draft from the numbers, for the presenter to edit."),
        money=money_, output=output, results=dict(summary=summary, cards=results), launches=launches, tiktok=tiktok, week_ahead=week_)
    os.makedirs(BOARD, exist_ok=True)
    path = os.path.join(BOARD, f"report_{W}.json")
    with open(path, "w") as f:
        json.dump(doc, f, ensure_ascii=False, separators=(",", ":"))
    print(f"report_{W}.json {os.path.getsize(path) / 1024:.0f} KB · {len(results)} result cards · {len(launches)} launches")


if __name__ == "__main__":
    main()
