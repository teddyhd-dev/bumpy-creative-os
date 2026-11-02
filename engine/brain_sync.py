"""Keeps the shared memory (brain/) and this week's state (state/) in step with the exports.

Runs last in engine/run_all.sh. It only ever writes the parts the engine owns (contracts/*.md):
  * core/minds.csv            registry of minds (persona × language); keeps the human columns
  * brain/minds/<mind>/       creates mind.md + history.md for minds with a live adset (seeded from the
                              Notion persona card), removes untouched seed-only files of minds gone dormant, rewrites the facts block, appends new-#1 and result
                              events to history.md (never edits existing lines)
  * brain/creatives/<code>.md creates a stub for every coded concept that became an adset's #1,
                              rewrites its facts block
  * brain/experiments/        fills the results block and status of each EXP-*.md;
                              regenerates detected-refreshes.csv
  * state/queue.json, week.json  this week's tickets (with the brief that covers each one)
  * reports/<week>/report.json   copy of the Tuesday report data
  * output/board/queue.json   adds each ticket's brief, for the ticket board sync
"""
from __future__ import annotations

import datetime as dt
import glob
import json
import os
import re
import shutil
import sys

import numpy as np
import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from personas import load_cards  # noqa: E402
from settings import BARS  # noqa: E402
from tickets import concept_weeks, short_label  # noqa: E402
from creative_relay import load_variants  # noqa: E402
from naming_audit import taxonomy  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output", "data")
BOARD = os.path.join(ROOT, "output", "board")
MINDS = os.path.join(ROOT, "brain", "minds")
CRE = os.path.join(ROOT, "brain", "creatives")
EXP = os.path.join(ROOT, "brain", "experiments")
STATE = os.path.join(ROOT, "state")
CORE = os.path.join(ROOT, "core")
CREATIVE_MIN_SPEND = 200     # a coded concept gets a creative file once it spent this much as an adset's #1
TODAY = dt.date.today().isoformat()
BAR = BARS["singular"]["green"]
LANG_OK = re.compile(r"^[A-Z]{2}(-[A-Z]{2})?$")
# For now the team writes country-style codes in the Language field (JP, KR, UA, CH, VN…). Older names were
# read as ISO codes; map them to the codes in use so one language is one mind.
LANG_ALIAS = {"JA": "JP", "KO": "KR", "UK": "UA", "ZH": "CH", "VI": "VN"}


# ---------- markdown helpers ----------
def creative_file(code, name):
    slug = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-") or "untitled"
    return f"{str(code).lower()}-{slug}.md"



def read_md(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", s, flags=re.S)
    return (yaml.safe_load(m.group(1)) or {}, m.group(2)) if m else ({}, s)


def write_md(path, fm, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    head = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False, width=1000).strip()
    new = f"---\n{head}\n---\n{body.lstrip(chr(10))}"
    if not os.path.exists(path) or open(path, encoding="utf-8").read() != new:
        open(path, "w", encoding="utf-8").write(new)


def set_block(body, name, content):
    a, b = f"<!-- generated:start {name} -->", f"<!-- generated:end {name} -->"
    block = f"{a}\n{content.strip()}\n{b}"
    if a in body and b in body:
        return re.sub(re.escape(a) + r".*?" + re.escape(b), lambda _: block, body, flags=re.S)
    return body.rstrip() + "\n\n" + block + "\n"


def append_event(path, header, text, key):
    """Append one history entry unless an entry with this event key is already there."""
    s = open(path, encoding="utf-8").read()
    if f"<!-- event:{key} -->" in s:
        return False
    with open(path, "a", encoding="utf-8") as f:
        f.write(("" if s.endswith("\n\n") else "\n" if s.endswith("\n") else "\n\n")
                + f"{header}\n{text.strip()}\n<!-- event:{key} -->\n")
    return True


def money(v):
    v = float(v or 0)
    return f"${v / 1000:.1f}k" if abs(v) >= 1000 else f"${v:.0f}"


def pct(v):
    return "–" if v is None or pd.isna(v) else f"{v * 100:.0f}%"


def r2(v):
    return "–" if v is None or pd.isna(v) else f"{v:.2f}"


# ---------- load ----------
def load():
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"].copy()
    scols = [c for c in G.columns if c.startswith("s_")]
    G["spend_total"] = G[scols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    G["live"] = G.active.astype(str).isin(["True", "true"])
    G["label"] = [short_label(r) for r in G[["persona", "os", "lang", "subangle"]].fillna("").to_dict("records")]
    G["lang"] = G.lang.astype(str).replace(LANG_ALIAS)
    G["mind"] = G.persona.astype(str) + "-" + G.lang
    G["mind_ok"] = G.lang.astype(str).str.match(LANG_OK) & ~G.persona.isin(["BrandTest", "Unknown", ""])
    c, A, meta, names = concept_weeks()
    D = pd.read_csv(os.path.join(OUT, "tk_atbats.csv"), dtype={"adset_id": str})
    return G, c, meta, names, D


def no1_runs(c, names, V):
    """Every reign: adset × concept that was the adset's #1 for consecutive weeks, with its top ad (full name)."""
    t = c[c["rank"] == 1].sort_values(["adset_id", "week"])
    rows = []
    for aid, g in t.groupby("adset_id"):
        run = (g.concept_key != g.concept_key.shift()).cumsum()
        for _, r in g.groupby(run):
            k = r.concept_key.iloc[0]
            rows.append(dict(adset_id=aid, code=k.replace("name:", ""), key=k, name=str(names.get(k, ""))[:40],
                             start=r.week.min(), end=r.week.max(), weeks=len(r), share=r.share.mean(),
                             spend=r.spend.sum(), coded=not k.startswith("name:"),
                             top_ad=top_ad(V, aid, k, r.week.min(), r.week.max())))
    return pd.DataFrame(rows)


def top_ad(V, aid, key, w_from=None, w_to=None):
    """The ad (full name) that spent most for this concept in this adset, optionally within weeks."""
    x = V[(V.adset_id == aid) & (V.concept_key == key)]
    if w_from is not None:
        x = x[(x.week >= w_from) & (x.week <= (w_to or w_from))]
    if x.empty:
        return ""
    return x.groupby("ad_clean").spend.sum().idxmax()


def variants_now(V, aid, key, week, as_spend):
    x = V[(V.adset_id == aid) & (V.concept_key == key) & (V.week == week)].sort_values("spend", ascending=False)
    return [(r.ad_clean, r.spend / as_spend if as_spend else np.nan) for r in x.itertuples()]


# ---------- minds ----------
def card_for(cards, persona):
    hits = [x for x in cards if x["persona"] == persona]
    hits.sort(key=lambda x: (x["mapped"] != "from its top-spender ads", x["status"] != "Success"))
    return hits[0] if hits else None


def seed_mind(mid, persona, lang, card):
    fm = dict(contract="mind/1", mind=mid, persona=persona, language=lang, status="live", updated=TODAY)
    who, beliefs, thumb, insp = "", "", "", ""
    if card:
        src = f'Notion persona card "{card["card"]}" (written for the persona across languages; confirm for {lang})'
        who = f"{card['lore'] or '–'}\n\n_Source: {src}._"
        rows = []
        if card["pattern"]:
            rows.append(f"| Winning pattern (Notion): {card['pattern'].replace(chr(10), ' ')} | low (not tested in {lang} yet) | Notion card | {TODAY} |")
        if card["message"]:
            rows.append(f"| Proven message (Notion): {card['message'].replace(chr(10), ' ')} | low (not tested in {lang} yet) | Notion card | {TODAY} |")
        beliefs = "\n".join(rows)
        if card["hook"]:
            thumb = f"- Hook words from the Notion card: {card['hook'].replace(chr(10), ' · ')}"
        insp = "\n".join(f"- {u} — reference on the Notion card (added {TODAY})" for u in card["links"])
    body = f"""# {persona} · {lang}

## Who they are
{who}

## What they want, fear and believe
| Belief | Confidence | Evidence | Since |
|---|---|---|---|
{beliefs}

## Their words

## What stops their thumb
{thumb}

## Messages that land and messages that tire

## Open questions

## Inspiration bank
{insp}

<!-- generated:start facts -->
<!-- generated:end facts -->
"""
    path = os.path.join(MINDS, mid, "mind.md")
    write_md(path, fm, body)
    hist = os.path.join(MINDS, mid, "history.md")
    if not os.path.exists(hist):
        seed_note = (f"Created from the exports and the Notion persona card \"{card['card']}\". Nothing in it is tested "
                     f"for {lang} yet: beliefs start at low confidence.") if card else "Created from the exports. No persona card found."
        write_md(hist, dict(contract="history/1", mind=mid),
                 f"# {persona} · {lang} — history\n\nEvery observation and change of belief, oldest first. Never edited or deleted.\n\n"
                 f"## {TODAY} · seed · Claude\n{seed_note}\n<!-- event:seed -->\n")


def mind_facts(mid, G, runs, D, Q, exps, last_ad_week):
    a = G[G.mind == mid]
    live = a[a.live]
    sp = live.spend_last.sum()
    roas = (live.spend_last * live.roas_last).sum() / sp if sp else np.nan
    lines = [f"## From the data (updated {TODAY}; adsets to {G.last_week.max()}, ads to {last_ad_week})",
             f"**Now:** {len(live)} live adset{'s' if len(live) != 1 else ''} · {money(sp)} last week · ROAS {r2(roas)} (bar {BAR:.2f})", ""]
    if len(live):
        lines += ["| Adset | Status | Spend | ROAS | #1 now (since) |", "|---|---|---|---|---|"]
        for r in live.sort_values("spend_last", ascending=False).itertuples():
            cur = runs[(runs.adset_id == r.adset_id)].sort_values("end").tail(1)
            no1 = f"{cur.code.iloc[0]} {cur.name.iloc[0]} (since {cur.start.iloc[0]}, {cur.weeks.iloc[0]} wk)" if len(cur) else "–"
            lines.append(f"| {r.label} | {r.status} | {money(r.spend_last)} | {r2(r.roas_last)} | {no1} |")
    tk = Q[Q.adset_id.isin(a.adset_id)]
    if len(tk):
        lines += ["", "**Open tickets:** " + "; ".join(f"{t.ticket} {t.type} ({t.adset.split(' · ', 1)[-1]}: {t.why})" for t in tk.itertuples())]
    r = runs[runs.adset_id.isin(a.adset_id)].copy()
    if len(r):
        r["adset"] = r.adset_id.map(a.set_index("adset_id").label)
        lines += ["", "### #1 history (latest first)"]
        for x in r.sort_values("start", ascending=False).head(15).itertuples():
            lines.append(f"- {x.start} · {x.adset} · {x.code} {x.name} · {x.weeks} wk at {pct(x.share)} of spend"
                         + (f"  \n  top ad: `{x.top_ad}`" if x.top_ad else ""))
        done = r[r.end < last_ad_week]
        if len(done):
            top = r.sort_values("weeks").iloc[-1]
            lines += ["", "### Fatigue clock",
                      f"A #1 here has led a median {done.weeks.median():.0f} weeks ({len(done)} finished reigns). "
                      f"Longest: {top['code']} {top['name']}, {top['weeks']} weeks from {top['start']}."]
    d = D[D.adset_id.isin(a.adset_id)].copy()
    if len(d):
        fin = d[~d.verdict.str.contains("provisional")]
        hits = fin.verdict.isin(["Hit", "Home run", "Late hit"]).sum()
        d["adset"] = d.adset_id.map(a.set_index("adset_id").label)
        lines += ["", "### Refreshes read from the exports",
                  f"{len(d)} since Dec: {hits} hits of {len(fin)} with a final verdict"
                  + (f" ({hits / len(fin) * 100:.0f}%)" if len(fin) else "") + ", "
                  f"{(fin.verdict == 'Strike').sum()} strikes, {(fin.verdict == 'Foul').sum()} fouls.",
                  "| Landed | Adset | Concepts | Variants | Week-1 share | Verdict |", "|---|---|---|---|---|---|"]
        for x in d.sort_values("w0", ascending=False).head(8).itertuples():
            lines.append(f"| {x.w0} | {x.adset} | {x.codes} | {x.variants_max} | {pct(x.best_s1)} | {x.verdict} |")
    mine = [e for e in exps if mid in (e["fm"].get("minds") or [])]
    lines += ["", "### Experiments logged"]
    lines += [f"- {e['fm']['id']} · {e['fm'].get('move', '')} · {e['fm'].get('status', '')}" for e in mine] or ["- none yet"]
    return "\n".join(lines)


# ---------- the story of an adset, for the brainstormer ----------
def fmt_d(d):
    try:
        return pd.to_datetime(d).strftime("%b %-d")
    except Exception:
        return str(d or "–")


def funnel(r):
    if r is None or not r.get("spend"):
        return None
    return dict(roas=r["rev"] / r["spend"], ctr=r["clicks"] / r["impressions"] if r["impressions"] else np.nan,
                c2i=r["installs"] / r["clicks"] if r["clicks"] else np.nan,
                ipm=r["installs"] / r["impressions"] * 1000 if r["impressions"] else np.nan)


def prebrief(t, n_tickets, G, runs, V, D, aw, acc, last_ad_week, bar, tickets_by_mind):
    aid = t["adset_id"]
    g = G.set_index("adset_id")
    os_ = g.os.get(aid, "")
    L = [f"Let's brainstorm {t['id']}: {t['adset']} (mind {t['mind']})",
         f"Adset name: {t.get('name', '')}",
         f"Ticket: {t['type']} · rank {t['rank']} of {n_tickets} · {str(t.get('status', '')).lstrip('✅🔻🆘🚀⚠️ ')} · {t['why']}"]
    h = t.get("hist") or {}
    if h.get("w"):
        L.append(f"Spend and ROAS, last {len(h['w'])} weeks (bar {bar:.2f}): " + " · ".join(
            f"{fmt_d(w)} {money(sv)} / {r2(rv)}" for w, sv, rv in zip(h["w"], h["s"], h["r"])))
    rows = aw[aw.adset_id == aid].sort_values("week").tail(4)
    if len(rows):
        parts = []
        for r in rows.to_dict("records"):
            f = funnel(r)
            if f:
                parts.append(f"{fmt_d(r['week'])} CTR {f['ctr'] * 100:.2f}% · C>I {r2(f['c2i'])} · IPM {r2(f['ipm'])}")
        L.append("Funnel, last 4 weeks: " + " | ".join(parts))
        last = rows.iloc[-1].to_dict()
        fa = funnel(acc.get((last["week"], os_))) if (last["week"], os_) in acc else None
        fl = funnel(last)
        if fa and fl:
            L.append(f"Last week vs the {os_} average: " + " · ".join(
                f"{k} ×{fl[key] / fa[key]:.2f}" for k, key in (("CTR", "ctr"), ("C>I", "c2i"), ("IPM", "ipm"), ("ROAS", "roas"))
                if fa[key] and not pd.isna(fa[key]) and not pd.isna(fl[key])))
    L.append(f"Weeks under the bar in a row: {t.get('weeks_under', 0)}"
             + (" · FADING: no new concept since it went under" if t.get("fading") else "")
             + f" · turnaround strikes {t.get('strikes', 0)}/3")
    r = runs[runs.adset_id == aid].sort_values("start")
    if t.get("top_code"):
        L.append(f"Current #1: {t['top_code']} {t.get('top_name', '')} · {pct(t.get('top_share'))} of spend · "
                 f"#1 since {fmt_d(t.get('reign_since'))} ({t.get('reign', 0)} wk)")
        key = r.key.iloc[-1] if len(r) else t["top_code"]
        sp = V[(V.adset_id == aid) & (V.week == last_ad_week)].spend.sum()
        for ad, sh in variants_now(V, aid, key, last_ad_week, sp)[:4]:
            L.append(f"  - {ad} ({pct(sh)} of the adset, week of {fmt_d(last_ad_week)})")
    prev = r.iloc[:-1].tail(4).iloc[::-1] if len(r) > 1 else r.iloc[0:0]
    if len(prev):
        L.append("Previous #1s here:")
        for x in prev.itertuples():
            L.append(f"  - {fmt_d(x.start)}–{fmt_d(x.end)} ({x.weeks} wk, {pct(x.share)} of spend): {x.code} {x.name}"
                     + (f" · top ad {x.top_ad}" if x.top_ad else ""))
    lr = t.get("last_refresh")
    if lr:
        ago = (pd.to_datetime(last_ad_week) - pd.to_datetime(lr)).days // 7
        L.append(f"Last refresh: {fmt_d(lr)} ({ago} wk ago){' (the adset launched then)' if lr == t.get('data_start') else ''}")
    d = D[D.adset_id == aid].sort_values("w0").tail(5).iloc[::-1]
    if len(d):
        L.append("Recent refreshes (Hit = became #1 · Strike = no new #1 while under the bar · Foul = didn't unseat a healthy #1):")
        for x in d.itertuples():
            ads = [top_ad(V, aid, k, x.w0, (pd.to_datetime(x.w0) + pd.Timedelta(days=7)).strftime("%Y-%m-%d")) for k in str(x.codes).split()]
            L.append(f"  - {fmt_d(x.w0)}: {x.codes} · {int(x.variants_max)} variant{'s' if x.variants_max != 1 else ''} · "
                     f"{pct(x.best_s1)} of spend in week 1 → {x.verdict}" + (f" · top ad {', '.join(a for a in ads if a)}" if any(ads) else ""))
    if t.get("in_test"):
        L.append(f"In test now: {t['in_test']} ({t.get('test_verdict', '')}, {pct(t.get('test_s1'))} of spend in week 1)")
    if t.get("j1"):
        L.append("Proven nearby, never run here: " + "; ".join(
            f"{j['code']} {j['name']} (#1 in {j['won_in']}, {money(j.get('spend_as_1'))} as #1)" for j in t["j1"][:3]))
    sib = [x for x in tickets_by_mind.get(t["mind"], []) if x["id"] != t["id"]]
    if sib:
        L.append("Same mind, other open tickets (one brief can cover them): " + "; ".join(f"{x['id']} {x['adset']} ({x['type']})" for x in sib[:5]))
    if t.get("brief"):
        b = t["brief"]
        L.append(f"Brief already logged: {b['id']} ({b['status']}, {b['strategist']})")
    return "\n".join(L)


# ---------- experiments ----------
def load_exps():
    out = []
    for p in sorted(glob.glob(os.path.join(EXP, "EXP-*.md"))):
        fm, body = read_md(p)
        out.append(dict(path=p, fm=fm, body=body))
    return out


def exp_results(e, c, G, D, last_ad_week):
    code = str(e["fm"].get("concept_code", ""))
    x = c[(c.concept_key == code) & (c.spend > 0)]
    if x.empty:
        return "Not seen in the exports yet.", "briefed", []
    lab = G.set_index("adset_id")
    rows, events, ages = [], [], []
    for aid, g in x.groupby("adset_id"):
        g = g.sort_values("week")
        w0 = g.first_in.iloc[0]
        age = (pd.to_datetime(last_ad_week) - pd.to_datetime(w0)).days // 7
        ages.append(age)
        s1 = g[g.wk == 0].share.max()
        top = g[g["rank"] == 1].wk.min()
        hit = D[(D.adset_id == aid) & (D.w0 == w0) & D.codes.str.split().map(lambda v: code in v)]
        verdict = hit.verdict.iloc[0] if len(hit) else ("Became #1" if pd.notna(top) else "Running")
        mind = lab.mind.get(aid, "")
        rows.append(f"| {lab.label.get(aid, aid)} | {mind} | {w0} | {pct(s1)} | "
                    f"{'week ' + str(int(top) + 1) if pd.notna(top) else '–'} | {pct(g.share.iloc[-1])} | {verdict} |")
        events.append(dict(mind=mind, adset=lab.label.get(aid, aid), w0=w0, s1=s1, verdict=verdict, age=age))
    status = "final" if min(ages) >= 4 else "week-1" if max(ages) >= 1 else "live"
    table = "\n".join(["| Adset | Mind | Live from | Week-1 share | Became #1 | Share now | Verdict |",
                       "|---|---|---|---|---|---|---|"] + rows)
    return table, status, events


# ---------- main ----------
def main():
    G, c, meta, names, D = load()
    last_ad_week = c.week.max()
    V = load_variants()
    runs = no1_runs(c, names, V)
    canon = taxonomy()
    Q = pd.read_csv(os.path.join(OUT, "tk_queue.csv"), dtype={"adset_id": str})
    cards = load_cards()
    exps = load_exps()
    G_ok = G[G.mind_ok]

    # registry
    reg = G_ok.groupby("mind").agg(persona=("persona", "first"), language=("lang", "first"),
                                   live_adsets=("live", "sum"), spend_last_week=("spend_last", "sum"),
                                   spend_since_dec=("spend_total", "sum"), first_seen=("first_week", "min"),
                                   last_seen=("last_week", "max")).reset_index()
    reg["status"] = np.where(reg.live_adsets > 0, "live", "dormant")
    seed = set(reg[reg.live_adsets > 0].mind)     # a mind gets a file when it has a live adset (or an experiment)
    for e in exps:
        seed |= set(e["fm"].get("minds") or [])
    created = 0
    for m in sorted(seed):
        if m not in set(reg.mind):
            continue
        if not os.path.exists(os.path.join(MINDS, m, "mind.md")):
            r = reg[reg.mind == m].iloc[0]
            seed_mind(m, r.persona, r.language, card_for(cards, r.persona))
            created += 1
    # drop seed-only files nobody has written in yet: minds gone dormant, or renamed by a code fix
    for path in glob.glob(os.path.join(MINDS, "*", "history.md")):
        m = os.path.basename(os.path.dirname(path))
        untouched = len(re.findall(r"^## ", open(path, encoding="utf-8").read(), flags=re.M)) <= 1
        if untouched and m not in seed:
            shutil.rmtree(os.path.dirname(path))
    reg["check"] = np.where(reg.persona.isin(canon), "", "persona not on the taxonomy (core/naming-adset-v8.md)")
    reg["has_file"] = reg.mind.map(lambda m: os.path.exists(os.path.join(MINDS, m, "mind.md")))
    reg["notion_card"] = reg.persona.map(lambda p: (card_for(cards, p) or {}).get("card", ""))
    old = os.path.join(CORE, "minds.csv")
    keep = pd.read_csv(old)[["mind", "markets", "notes"]] if os.path.exists(old) else pd.DataFrame(columns=["mind", "markets", "notes"])
    reg = reg.merge(keep, on="mind", how="left")
    cols = ["mind", "persona", "language", "status", "live_adsets", "spend_last_week", "spend_since_dec",
            "first_seen", "last_seen", "has_file", "notion_card", "check", "markets", "notes"]
    reg = reg[cols].sort_values(["status", "spend_last_week"], ascending=[False, False])
    reg.to_csv(old, index=False, float_format="%.0f")

    # facts blocks, status, new-#1 events
    for m in reg[reg.has_file].mind:
        p = os.path.join(MINDS, m, "mind.md")
        fm, body = read_md(p)
        fm["status"] = reg.set_index("mind").status[m]
        write_md(p, fm, set_block(body, "facts", mind_facts(m, G, runs, D, Q, exps, last_ad_week)))
        hist = os.path.join(MINDS, m, "history.md")
        a = G[G.mind == m].set_index("adset_id")
        for aid in a.index:
            r = runs[runs.adset_id == aid].sort_values("start")
            if len(r) >= 2 and r.start.iloc[-1] == last_ad_week:
                new, prev = r.iloc[-1], r.iloc[-2]
                g = c[(c.adset_id == aid) & (c.concept_key == new.key)].sort_values("week")
                s1 = g[g.wk == 0].share.max()
                append_event(hist, f"## {last_ad_week} · new-1 · data",
                             f"{new['code']} {new['name']} became #1 in {a.label[aid]} with {pct(new.share)} of spend "
                             f"(it entered on {g.first_in.iloc[0]} with {pct(s1)} in its first week), replacing "
                             f"{prev['code']} {prev['name']} after {prev.weeks} week{'s' if prev.weeks != 1 else ''} as #1.",
                             f"new1:{aid}:{last_ad_week}")

    # creatives: one file per concept (lowercase file names stay safe on a Mac). Code fixes and names come from
    # core/code_aliases.csv and core/concepts.csv, already applied to the concept keys.
    from codes import code_aliases
    al = code_aliases()
    aliases_of = {}
    for r in al.itertuples():
        aliases_of.setdefault(r.code, []).append(r.alias + (f" (when named {r.conceptname})" if r.conceptname else ""))
    cc = runs[runs.coded].groupby("code").agg(spend=("spend", "sum")).reset_index()
    cc = cc[cc.spend >= CREATIVE_MIN_SPEND]
    cc["name"] = cc.code.map(lambda k: str(names.get(k, "")))
    lab = G.set_index("adset_id")
    existing = {}
    for p in glob.glob(os.path.join(CRE, "*.md")):
        fm, _ = read_md(p)
        existing[str(fm.get("code", ""))] = p
    live_keys = set(c.concept_key)
    for code, p in list(existing.items()):
        fm, body = read_md(p)
        if code not in live_keys and not fm.get("decoded"):
            os.remove(p)                       # merged into another code, nothing written in it yet
            existing.pop(code)
    for r in cc.itertuples():
        want = os.path.join(CRE, creative_file(r.code, r.name))
        fm0 = dict(contract="creative/1", code=r.code, name=r.name, decoded=False)
        if r.code in existing and existing[r.code] != want:
            fm, body = read_md(existing[r.code])
            os.remove(existing[r.code])
            fm["name"] = r.name
            write_md(want, fm, re.sub(r"^# .*$", f"# {r.code} · {r.name}", body, count=1, flags=re.M))
        elif r.code not in existing:
            write_md(want, fm0, f"# {r.code} · {r.name}\n\n## Decode\n- First second:\n- Hook:\n- Message:\n- Format:\n"
                     f"- Why it stops the thumb:\n- Full breakdown:\n- Snapshot:\n- Decoded by:\n\n"
                     "<!-- generated:start facts -->\n<!-- generated:end facts -->\n")
    for p in sorted(glob.glob(os.path.join(CRE, "*.md"))):
        fm, body = read_md(p)
        code = str(fm.get("code", ""))
        keys = [code]
        if aliases_of.get(code):
            fm["aliases"] = aliases_of[code]
        else:
            fm.pop("aliases", None)
        x = c[c.concept_key.isin(keys)]
        rr = runs[runs.key.isin(keys)]
        lines = [f"## Where it ran (updated {TODAY}; ads to {last_ad_week})"]
        if fm.get("aliases"):
            lines.append(f"Includes ads written as {', '.join(fm['aliases'])} (confirmed fixes in core/code_aliases.csv).")
        if len(x):
            agg = x.groupby("adset_id").agg(first=("first_in", "first"), last=("week", "max"), spend=("spend", "sum"),
                                            peak=("share", "max")).reset_index()
            agg["weeks1"] = agg.adset_id.map(rr.groupby("adset_id").weeks.sum()).fillna(0).astype(int)
            agg["sp1"] = agg.adset_id.map(rr.groupby("adset_id").spend.sum()).fillna(0)
            agg = agg.sort_values(["weeks1", "spend"], ascending=False)
            lines += [f"#1 in {int((agg.weeks1 > 0).sum())} of {len(agg)} adsets it ran in · {money(agg.sp1.sum())} spent as #1 · "
                      f"{money(agg.spend.sum())} in total.", "",
                      "| Mind | Adset | First week | Last week | Weeks as #1 | Peak share | Spend |", "|---|---|---|---|---|---|---|"]
            for r in agg.head(20).itertuples():
                lines.append(f"| {lab.mind.get(r.adset_id, '')} | {lab.label.get(r.adset_id, r.adset_id)} | {r.first} | {r.last} | "
                             f"{r.weeks1} | {pct(r.peak)} | {money(r.spend)} |")
            vv = V[V.concept_key.isin(keys)].groupby("ad_clean").agg(spend=("spend", "sum"), adsets=("adset_id", "nunique"))
            vv = vv.sort_values("spend", ascending=False)
            lines += ["", f"### Variants (full ad names, {len(vv)} in total, top 10 by spend)"]
            lines += [f"- `{n}` · {money(x.spend)} · {int(x.adsets)} adset{'s' if int(x.adsets) != 1 else ''}" for n, x in vv.head(10).iterrows()]
        else:
            lines.append("Not in the ad exports.")
        write_md(p, fm, set_block(body, "facts", "\n".join(lines)))

    # experiments: results, status, result events
    for e in exps:
        table, status, events = exp_results(e, c, G, D, last_ad_week)
        e["fm"]["status"] = status
        write_md(e["path"], e["fm"], set_block(e["body"], "results",
                 f"## Results (updated {TODAY}; ads to {last_ad_week})\n{table}"))
        for ev in events:
            if ev["age"] < 1 or not ev["mind"]:
                continue
            stage = "final" if ev["age"] >= 4 else "week-1"
            hist = os.path.join(MINDS, ev["mind"], "history.md")
            if os.path.exists(hist):
                append_event(hist, f"## {last_ad_week} · result · data",
                             f"{e['fm']['id']} in {ev['adset']}: {pct(ev['s1'])} of spend in week 1 → {ev['verdict']} ({stage} read). "
                             f"Hypothesis: see the experiment file.", f"result:{e['fm']['id']}:{ev['adset']}:{stage}")
    # detected refreshes
    code_to_exp = {str(e["fm"].get("concept_code", "")): e["fm"]["id"] for e in exps}
    det = D.copy()
    det["mind"] = det.adset_id.map(lab.mind)
    det["adset"] = det.adset_id.map(lab.label)
    det["experiment"] = det.codes.map(lambda s: " ".join(v for k, v in code_to_exp.items() if k in str(s).split()))
    os.makedirs(EXP, exist_ok=True)
    det[["w0", "mind", "adset", "adset_id", "codes", "concepts", "variants_max", "best_s1", "wk_top", "verdict", "context",
         "adset_lift", "experiment"]].sort_values("w0").to_csv(os.path.join(EXP, "detected-refreshes.csv"), index=False, float_format="%.3f")

    # state + board link
    qpath = os.path.join(BOARD, "queue.json")
    q = json.load(open(qpath))
    brief_of = {}
    for e in sorted(exps, key=lambda e: str(e["fm"].get("date", ""))):
        for t in e["fm"].get("tickets") or []:
            brief_of[t] = dict(id=e["fm"]["id"], strategist=e["fm"].get("strategist", ""), date=str(e["fm"].get("date", "")),
                               status=e["fm"].get("status", ""), concept=f"{e['fm'].get('concept_code', '')} {e['fm'].get('concept_name', '')}")
    aw = pd.read_pickle(os.path.join(ROOT, "data", "model", "adset_week.pkl"))
    aw["adset_id"] = aw.adset_id.astype(str)
    aw["os"] = aw.adset_id.map(lab.os)
    accdf = aw.groupby(["week", "os"])[["spend", "rev", "impressions", "installs", "clicks"]].sum()
    acc = {k: v.to_dict() for k, v in accdf.iterrows()}
    for t in q["tickets"]:
        t["mind"] = f"{t['persona']}-{LANG_ALIAS.get(t['lang'], t['lang'])}"
        t["brief"] = brief_of.get(t["id"])
        rr = runs[runs.adset_id == t["adset_id"]].sort_values("start")
        t["top_ad"] = rr.top_ad.iloc[-1] if len(rr) else ""
        for pp in t.get("past") or []:
            m = rr[rr.code == pp.get("code")]
            pp["top_ad"] = m.top_ad.iloc[-1] if len(m) else ""
    by_mind = {}
    for t in q["tickets"]:
        by_mind.setdefault(t["mind"], []).append(t)
    for t in q["tickets"]:
        t["prebrief"] = prebrief(t, len(q["tickets"]), G, runs, V, D, aw, acc, last_ad_week, BAR, by_mind)
    # the board's database caps a document at 256 KB: the stories go in their own document
    json.dump({t["id"]: t["prebrief"] for t in q["tickets"]}, open(os.path.join(BOARD, "prebriefs.json"), "w"),
              separators=(",", ":"), ensure_ascii=False)
    qb = dict(q, tickets=[{k: v for k, v in t.items() if k != "prebrief"} for t in q["tickets"]])
    json.dump(qb, open(qpath, "w"), separators=(",", ":"))
    os.makedirs(STATE, exist_ok=True)
    keys = ["id", "rank", "type", "mind", "adset", "adset_id", "os", "why", "spend", "roas", "top_code", "top_name", "top_share",
            "top_ad", "reign", "reign_since", "last_refresh", "strikes", "weeks_under", "fading", "past_no1", "j1", "brief", "prebrief"]
    json.dump(dict(week=q.get("adset_week"), ad_week=q.get("ad_week"), generated=TODAY,
                   tickets=[{k: t.get("past" if k == "past_no1" else k) for k in keys} for t in q["tickets"]]),
              open(os.path.join(STATE, "queue.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(dict(adset_week=q.get("adset_week"), ad_week=q.get("ad_week"), generated=TODAY, bar=q.get("bar"),
                   capacity=q.get("capacity"), tickets_open=len(q["tickets"]), facts=q.get("facts")),
              open(os.path.join(STATE, "week.json"), "w"), indent=1)
    rp = os.path.join(BOARD, f"report_{q.get('adset_week')}.json")
    if os.path.exists(rp):
        os.makedirs(os.path.join(ROOT, "reports", str(q.get("adset_week"))), exist_ok=True)
        shutil.copy(rp, os.path.join(ROOT, "reports", str(q.get("adset_week")), "report.json"))
    print(f"minds: {int(reg.has_file.sum())} files ({created} new) of {len(reg)} in core/minds.csv · "
          f"creatives: {len(glob.glob(os.path.join(CRE, '*.md')))} · experiments: {len(exps)} · tickets: {len(q['tickets'])}")


if __name__ == "__main__":
    main()
