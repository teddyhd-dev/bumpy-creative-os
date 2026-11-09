"""Build the Tuesday launch-review deck (Slides artifact files) from the review data.

    python3 tools/report/build_deck.py reports/2026-11-02

Reads, in that folder:
  refresh_review.json   the batch's read per adset, the creator read, account news (tools/report/refresh_review.py)
  followup_*.json       optional: last week's batch re-read to this week's end (`--out followup_batchNN.json`)
  deck_text.json        the words a person decides: titles, subtitles, speaker notes, action rows, "what we made" cards
Writes deck/project/deck.json and deck/project/slides/<id>.html in the same folder: publish them to a new Slides
artifact (root = deck/). The layout, colours and row order follow REFRESH-REVIEW.md; every number comes from the JSON.
"""
from __future__ import annotations

import html
import json
import os
import sys
from datetime import date, timedelta

OS_FONT = "'Open Sans', Arial, sans-serif"
QS_FONT = "Quicksand, Arial, sans-serif"
INK, MUTED, LINE, PAPER, HEAD_BG = "#2b2428", "#5e5c60", "#dcd8d2", "#f7f6f3", "#eae7e2"
NAVY, NAVY_TXT, NAVY_H, NAVY_HEAD, NAVY_LINE, NAVY_FOOT = "#1b2a44", "#f2f4f8", "#8fd0ea", "#2a3d5e", "#33496e", "#a9b4c6"
AUD = {"InternationalFriendFinder": "Friends", "GringoMaleLover": "Gringo", "LocalDatingFatigue": "Loc. Dating",
       "PassportBro": "Passport Bro", "LatinaFemaleLover": "Latina", "MatureDating": "Mature", "SexyFemaleLover": "Sexy",
       "SlavicFemaleLover": "Slavic", "InterracialDatingSeekers": "Interracial", "SoutheastAsianFemaleLover": "SEA Lover",
       "AsianFemaleLover": "Asian Lover", "ChristianMatchWorldwide": "Christian", "ChatOnly": "Chat Only",
       "CelebrityCrushLookalikeLover": "Celeb Crush", "SexyMaleLover": "Sexy Male", "InstagramPost": "Instagram post",
       "General": "General", "ChatPersona": "Chat Persona"}
PERSONA_TITLE = {"InternationalFriendFinder": "International Friend", "GringoMaleLover": "Gringo Lover",
                 "LocalDatingFatigue": "Local Dating Fatigue", "PassportBro": "Passport Bro",
                 "LatinaFemaleLover": "Latina Lover", "MatureDating": "Mature Dating", "SexyFemaleLover": "Sexy Female Lover"}
READ_PILL = {"Worked": ("#ffffff", "#1f7fa8", "✓ Worked"), "Almost": ("#1f5f7a", "#d6eef8", "↗ Almost"),
             "Flat": ("#5a4a1e", "#e9e3d3", "= Flat"), "Watch": ("#5a4500", "#ffe9a8", "◎ Watch"),
             "Worse": ("#ffffff", "#d9442b", "✗ Worse"), "Miss": ("#4f4d51", "#e2dfe1", "Miss"),
             "Miss (left)": ("#4f4d51", "#e2dfe1", "Miss")}
PRIO = {"Urgent": ("#ffffff", "#d9442b", ""), "High": ("#6b2a12", "#fdd3c2", ""), "Medium": ("#5a4a1e", "#e9e3d3", ""),
        "Research": ("#5a4a1e", "#e9e3d3", ""), "Next batch": ("#5a4a1e", "#e9e3d3", ""), "Decide": ("#5a4a1e", "#e9e3d3", ""),
        "Watch": ("#5a4500", "#ffe9a8", ""), "Keep": ("#5a4500", "#ffe9a8", ""), "Stop": ("#4f4d51", "#e2dfe1", ""),
        "Leave": ("#4f4d51", "#e2dfe1", ""), "Opportunity": ("#1b2a33", "#53afd4", ""),
        "Learn": ("#1f5f7a", "#ffffff", "border:2px solid #1f7fa8; ")}
OWNER = {"Creative": "color:#443a40; background:#ede6ea; ", "Creative lead": "color:#443a40; background:#ede6ea; ",
         "Media buyer": "color:#1f5f7a; background:#ffffff; border:2px solid #53afd4; "}
e = html.escape


def zone(v):
    """ROAS zone on the value as shown: 2 decimals, except a value just under a line never rounds up onto it
    (0.398 shows 0.39, not 0.40), so the colour and the read always agree with the number."""
    if v is None:
        return None
    s = round(v + 1e-9, 2)
    for line in (0.40, 0.32):
        if v < line <= s:
            s = round(line - 0.01, 2)
    return s, ("#1b2a33", "#53afd4") if s >= 0.40 else ("#6b2a12", "#fdd3c2") if s >= 0.32 else ("#ffffff", "#d9442b")


def roas_pill(v, fs=24, pad="2px 14px"):
    if v is None or v != v or v == 0:
        return f'<p style="font-family:{OS_FONT}; font-size:{fs}px; color:#9a969b">–</p>'
    s, (fg, bg) = zone(v)
    return (f'<p style="padding:{pad}; font-family:{OS_FONT}; font-size:{fs}px; font-weight:700; color:{fg}; '
            f'background:{bg}; border-radius:256px">{s:.2f}</p>')


def arrow(b, a, fs=26, delta=False):
    if b is None or a is None or b != b or a != a or b == 0:
        return ""
    d = a - b
    if abs(d) < 0.02:
        return f'<p style="font-family:{OS_FONT}; font-size:{fs}px; color:#9a969b">–</p>'
    c, s = ("#1f6f94", "▲") if d > 0 else ("#d9442b", "▼")
    return f'<p style="font-family:{OS_FONT}; font-size:{fs}px; color:{c}">{s}{f" {d:+.2f}" if delta else ""}</p>'


def pill(text, fg, bg, fs=24, pad="2px 14px", extra=""):
    return (f'<p style="padding:{pad}; font-family:{OS_FONT}; font-size:{fs}px; font-weight:700; color:{fg}; '
            f'background:{bg}; {extra}border-radius:256px; white-space:nowrap">{e(text)}</p>')


def spark(weekly, label, w=210, h=42):
    """Last 8 weeks of adset ROAS: dashed line = 0.40, peach band = under it, dot = latest week in its zone colour."""
    ks = sorted(weekly)[-8:]
    xs = [8 + i * 37.7 for i in range(8)]
    pts = []
    for i, k in enumerate(ks[-8:]):
        v = weekly.get(k)
        y = None if v is None else max(4, min(52, 28 - (v - 0.40) * 80))
        pts.append((xs[i + 8 - len(ks)], y, v))
    d, pen = "", False
    for x, y, v in pts:
        if y is None:
            pen = False
            continue
        d += f"{'L' if pen else 'M'}{x:.0f} {y:.0f} "
        pen = True
    last = [p for p in pts if p[1] is not None][-1:] or [(272, 28, 0.4)]
    x, y, v = last[0]
    dot = "#1F7FA8" if v >= 0.40 else "#F4A582" if v >= 0.32 else "#D9442B"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" aria-label="ROAS trend {e(label)}" viewBox="0 0 280 56" '
            f'style="width:{w}px; height:{h}px"><rect x="0" y="28" width="280" height="28" fill="#FBE1D6"/>'
            f'<line x1="0" y1="28" x2="280" y2="28" stroke="#9A969B" stroke-width="2" stroke-dasharray="6 6"/>'
            f'<path d="{d.strip()}" fill="none" stroke="#2B2428" stroke-width="3"/>'
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="8" fill="{dot}"/></svg>')


MEDAL = {1: "🥇", 2: "🥈", 3: "🥉"}
SHORT = {"colosseum5050": "colosseum 50/50"}


def place(rank):
    """Rank in the adset: medals for the top 3 (easier to scan), #N below."""
    return MEDAL.get(int(rank), f"#{int(rank)}")


def creative(r):
    return ", ".join(SHORT.get(c, c) for c in (r.get("concepts") or []))


def share(s):
    return f"{s * 100:.1f}%" if s < 0.01 else f"{round(s * 100)}%"


def reign(r, days):
    tag = r.get("no1_tag") or ""
    if tag in ("NEW", "NEW-OLD"):
        return pill(f"{days} day{'s' if days != 1 else ''}", "#5a4500", "#ffe9a8")
    w = int(r.get("no1_weeks") or 0)
    if w < 2:
        return pill(f"{max(w, 1)} week", "#5a4500", "#ffe9a8")
    return f'<p style="font-family:{OS_FONT}; font-size:24px; color:{INK}">{w} weeks</p>'


def no1(r):
    tag, name, s = r.get("no1_tag") or "", r.get("no1_after") or "–", r.get("no1_share") or 0
    if tag == "NEW":
        return pill(f"NEW · {name}", "#1b2a33", "#53afd4", fs=22, pad="2px 12px")
    if tag == "NEW-OLD":
        return pill(f"NEW-OLD · {name}", "#6b2a12", "#fdd3c2", fs=22, pad="2px 12px")
    return f'<p style="font-family:{OS_FONT}; font-size:24px; color:{INK}">{e(name)}{f" ({round(s * 100)}%)" if s >= 0.6 else ""}</p>'


def cell(width, inner, flex=True, align="", gap=""):
    if not flex:
        return inner.replace('<p style="', f'<p style="width:{width}px; ', 1)
    j = f" justify-content:{align};" if align else ""
    g = f" gap:{gap}; align-items:center;" if gap else ""
    return f'<div style="width:{width}px; display:flex; flex-direction:row;{j}{g}">{inner}</div>'


def txt(width, s, fs=26, color=INK, weight="", align=""):
    a = f" text-align:{align};" if align else ""
    w = f" font-weight:{weight};" if weight else ""
    return f'<p style="width:{width}px; font-family:{OS_FONT}; font-size:{fs}px;{w}{a} color:{color}">{s}</p>'


def header_row(cols, bg=HEAD_BG, color=INK, fs=24, pad="8px 16px"):
    inner = "".join(txt(w, e(l), fs=fs, color=color, weight="700", align="right" if l == "Verdict" else "") for l, w in cols)
    return f'<div style="display:flex; flex-direction:row; align-items:center; padding:{pad}; background:{bg}; border-radius:12px">{inner}</div>'


def section(sid, body, bg=PAPER, gap=40, pad="128px 128px 160px"):
    return (f'<section id="{sid}" data-transition="fade" style="display:flex; flex-direction:column; gap:{gap}px; '
            f'padding:{pad}; background:{bg}">\n{body}\n</section>\n')


def head(eyebrow, title, sub=None, size=64, navy=False):
    c_e, c_t, c_s = (NAVY_H, NAVY_TXT, NAVY_FOOT) if navy else ("#1f7fa8", INK, MUTED)
    h = '<div style="display:flex; flex-direction:column; gap:12px">'
    if eyebrow:
        h += (f'<p style="font-family:{QS_FONT}; font-size:28px; font-weight:700; letter-spacing:3px; '
              f'text-transform:uppercase; color:{c_e}">{e(eyebrow)}</p>')
    h += f'<h2 style="font-family:{QS_FONT}; font-size:{size}px; font-weight:700; line-height:1.1; color:{c_t}">{title}</h2>'
    if sub:
        h += f'<p style="font-family:{OS_FONT}; font-size:30px; color:{c_s}">{sub}</p>'
    return h + "</div>"


def foot(s, navy=False, bottom=64):
    return (f'<p style="position:absolute; bottom:{bottom}px; left:128px; width:1664px; font-family:{OS_FONT}; '
            f'font-size:24px; color:{NAVY_FOOT if navy else MUTED}">{s}</p>')


def aside(s):
    return f"<aside>{e(s)}</aside>"


def dlabel(d):
    x = date.fromisoformat(d)
    return x.strftime("%a ") + str(x.day) + x.strftime(" %b")


def order(rows):
    """Rows in the top 3 first (ROAS after, best → worst), then the rest (worst → best)."""
    top = sorted([r for r in rows if r["rank"] <= 3], key=lambda r: -(r["after"] or 0))
    rest = sorted([r for r in rows if r["rank"] > 3], key=lambda r: (r["after"] or 0))
    return top + rest


def adset_labels(rows):
    lab = {}
    for r in rows:
        lab.setdefault((r["persona"], f'{r["os"]} · {r["lang"]}'), []).append(r)
    out = {}
    for k, rs in lab.items():
        rs = sorted(rs, key=lambda r: str(r.get("launch") or ""))
        for i, r in enumerate(rs):
            out[r["adset_id"]] = k[1] + (" (new)" if len(rs) > 1 and i == len(rs) - 1 else "")
    return out


def counts(rows):
    c = {"Worked": 0, "Almost": 0, "Flat": 0, "Watch": 0, "Worse": 0, "Miss": 0}
    for r in rows:
        c["Miss" if r["read"].startswith("Miss") else r["read"]] += 1
    return c


def result_line(c):
    words = [("Worked", "worked"), ("Almost", "almost"), ("Flat", "flat"), ("Watch", "watch"), ("Worse", "got worse"), ("Miss", "missed")]
    return ", ".join(f"{c[k]} {w}" for k, w in words if c[k])


def persona_slide(sid, persona, rows, end, T):
    rows = order(rows)
    labels = adset_labels(rows)
    up = min(r["upload"] for r in rows)
    days = (date.fromisoformat(end) - date.fromisoformat(up)).days + 1
    cols = [("Ad set", 210), ("ROAS, 8 weeks", 190), ("Before", 120), ("After", 170), ("New creative", 220),
            ("In top 3? · share", 190), ("Current #1 spender", 250), ("#1 for", 120), ("Verdict", 162)]
    pad = "8px 16px" if len(rows) <= 7 else "4px 16px"
    body = [head(f"Live: {dlabel(up)} · {days} days of data", e(T["title"]), e(T.get("sub") or "Result: " + result_line(counts(rows)))),
            '<div style="display:flex; flex-direction:column">', header_row(cols)]
    for i, r in enumerate(rows):
        hl = " background:#e3f2f9;" if r.get("no1_tag") == "NEW" else ""
        bd = "" if i == len(rows) - 1 else f" border-bottom:1px solid {LINE};"
        d = (date.fromisoformat(end) - date.fromisoformat(r["upload"])).days + 1
        top = r["rank"] <= 3
        intop = (f'<b>Yes</b> · {place(r["rank"])} · {share(r["batch_share"])}' if top else f'No · {place(r["rank"])} · {share(r["batch_share"])}')
        fg, bg, word = READ_PILL[r["read"]]
        body.append(
            f'<div style="display:flex; flex-direction:row; align-items:center; padding:{pad};{hl}{bd}">'
            + txt(210, e(labels[r["adset_id"]]))
            + f'<div style="width:190px; display:flex; flex-direction:column">{spark(r["weekly_roas"], AUD.get(persona, persona) + " " + labels[r["adset_id"]], w=170, h=40)}</div>'
            + cell(120, roas_pill(r["before"]))
            + cell(170, roas_pill(r["after"]) + arrow(r["before"], r["after"]), gap="10px")
            + txt(220, e(creative(r)), fs=22)
            + txt(190, intop, color=INK if top else MUTED)
            + cell(250, no1(r)) + cell(120, reign(r, d))
            + cell(162, pill(word, fg, bg), align="end") + "</div>")
    body.append("</div>")
    body.append(foot(T["foot"]))
    body.append(aside(T["note"]))
    return section(sid, "\n".join(body))


MOVE_WORDS = ("J1", "J2", "same message", "new visual", "new form", "decode", "learn", "new angle", "copy")


def check_actions(sid, T):
    """core/mistakes.md rules 7-8: a creative row names a move or what we learn from the incumbent."""
    for a in T.get("rows", []):
        if a.get("owner", "").startswith("Creative") and a.get("level") not in ("Keep", "Research", "Decide"):
            if not any(w.lower() in a.get("action", "").lower() for w in MOVE_WORDS):
                print(f"  ! {sid}: creative row with no incumbent lesson or jurus move: {a.get('adsets', '')}")


def action_slide(sid, T):
    check_actions(sid, T)
    cols = [("Owner", 210), ("Priority", 190), ("Ad sets", 320), ("Spend/wk", 140), ("Action", 772)]
    hdr = "".join(txt(w, l, fs=24, color=NAVY_TXT, weight="700", align="right" if l == "Spend/wk" else "")
                  .replace("width:140px;", "width:140px; padding:0 24px 0 0;") for l, w in cols)
    body = [head(None, e(T["title"]), None, size=60, navy=True).replace(
                '<div style="display:flex; flex-direction:column; gap:12px">',
                f'<div style="display:flex; flex-direction:column; gap:12px"><h3 style="font-family:{QS_FONT}; font-size:48px; '
                f'font-weight:700; color:{NAVY_H}">Action items · {e(T["persona"])}</h3>', 1),
            '<div style="display:flex; flex-direction:column">',
            f'<div style="display:flex; flex-direction:row; align-items:center; padding:8px 16px; background:{NAVY_HEAD}; border-radius:12px">{hdr}</div>']
    rows = T["rows"]
    for i, a in enumerate(rows):
        bd = "" if i == len(rows) - 1 else f" border-bottom:1px solid {NAVY_LINE};"
        if a["owner"] == "Leave":
            body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:14px 16px;{bd}">'
                        + cell(210, pill("Leave", "#4f4d51", "#e2dfe1", fs=22, pad="2px 12px"))
                        + txt(1422, a["action"], color="#c3cbd8") + "</div>")
            continue
        fg, bg, ex = PRIO[a["level"]]
        label = f'{a["n"]} · {a["level"]}' if a.get("n") else a["level"]
        own = OWNER[a["owner"]]
        body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:14px 16px;{bd}">'
                    + cell(210, f'<p style="padding:2px 12px; font-family:{OS_FONT}; font-size:22px; font-weight:700; {own}border-radius:256px">{e(a["owner"])}</p>')
                    + cell(190, pill(label, fg, bg, extra=ex))
                    + txt(320, a["adsets"], fs=28, color=NAVY_TXT)
                    + txt(140, e(a.get("spend") or "—"), fs=28, color=NAVY_TXT, align="right").replace("width:140px;", "width:140px; padding:0 24px 0 0;")
                    + txt(772, a["action"], color=NAVY_TXT) + "</div>")
    body.append("</div>")
    body.append(foot(T["foot"], navy=True))
    body.append(aside(T["note"]))
    return section(sid, "\n".join(body), bg=NAVY, gap=48)


def scoreboard(sid, groups, end, T):
    cols = [("Refresh", 452), ("Live", 230), ("Adsets", 110)] + [(k, 140) for k in ("Worked", "Almost", "Flat", "Watch", "Worse", "Miss")]
    hdr = "".join(txt(w, l, fs=26, weight="700", align="" if l in ("Refresh", "Live · data") else "center") for l, w in cols)
    pad = "16px" if len(groups) <= 5 else "12px 16px"
    body = [head(None, T["title"], None, size=72 if len(groups) <= 5 else 60), '<div style="display:flex; flex-direction:column">',
            f'<div style="display:flex; flex-direction:row; align-items:center; padding:10px 16px; background:{HEAD_BG}; border-radius:12px">{hdr}</div>']
    tot = {k: 0 for k in ("Worked", "Almost", "Flat", "Watch", "Worse", "Miss")}
    n = 0
    colours = {k: (READ_PILL[k][0], READ_PILL[k][1]) for k in tot}
    for persona, rows, concept in groups:
        c = counts(rows)
        up = min(r["upload"] for r in rows)
        days = (date.fromisoformat(end) - date.fromisoformat(up)).days + 1
        n += len(rows)
        cells = ""
        for k in tot:
            tot[k] += c[k]
            cells += (cell(140, pill(str(c[k]), *colours[k], fs=28, pad="2px 22px"), align="center") if c[k]
                      else txt(140, "–", fs=30, color="#9a969b", align="center"))
        body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:{pad}; border-bottom:1px solid {LINE}">'
                    + txt(452, f"<b>{e(PERSONA_TITLE.get(persona, persona))}</b>", fs=28)
                    + txt(230, f"{days} days", fs=28, align="center") + txt(110, str(len(rows)), fs=28, align="center") + cells + "</div>")
    body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:{pad}; background:{INK}; border-radius:0 0 12px 12px">'
                + txt(452, "Total", fs=28, color=PAPER, weight="700") + txt(230, T.get("days", ""), fs=26, color="#d9d4d7", align="center")
                + txt(110, str(n), fs=28, color=PAPER, weight="700", align="center")
                + "".join(txt(140, str(v), fs=28, color=PAPER, weight="700", align="center") for v in tot.values()) + "</div>")
    body.append("</div>")
    body.append(foot(T["foot"]))
    body.append(aside(T["note"]))
    return section(sid, "\n".join(body), gap=56)


def followup_slide(sid, groups, T):
    """Last week's batch: read then vs read now, per refresh, as pill counts."""
    def pills(c):
        out = ""
        for k in ("Worked", "Almost", "Flat", "Watch", "Worse", "Miss"):
            if c[k]:
                fg, bg, w = READ_PILL[k]
                out += pill(f"{c[k]} {w.split(' ')[-1].lower()}", fg, bg, fs=24, pad="2px 14px")
        return out
    cols = [("Refresh", 420), ("Adsets", 120), ("Last Tuesday", 520), ("Now", 604)]
    body = [head(T["eyebrow"], e(T["title"]), e(T.get("sub", "")), size=64), '<div style="display:flex; flex-direction:column">',
            header_row([(l, w - (32 if i == 0 else 0)) for i, (l, w) in enumerate(cols)], fs=26, pad="10px 16px")]
    for i, (name, a, b) in enumerate(groups):
        bd = "" if i == len(groups) - 1 else f" border-bottom:1px solid {LINE};"
        body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:18px 16px;{bd}">'
                    + txt(388, name, fs=30) + txt(120, str(len(b)), fs=30)
                    + f'<div style="width:520px; display:flex; flex-direction:row; flex-wrap:wrap; gap:10px">{pills(counts(a))}</div>'
                    + f'<div style="width:604px; display:flex; flex-direction:row; flex-wrap:wrap; gap:10px">{pills(counts(b))}</div></div>')
    body.append("</div>")
    if T.get("points"):
        body.append(f'<div style="display:flex; flex-direction:column; gap:10px">' + "".join(
            f'<p style="font-family:{OS_FONT}; font-size:28px; color:{INK}">{p}</p>' for p in T["points"]) + "</div>")
    body.append(foot(T["foot"]))
    body.append(aside(T["note"]))
    return section(sid, "\n".join(body), gap=40)


def creator_slide(sid, rows, end, T):
    rows = order(rows)
    labels = adset_labels(rows)
    cols = [("Ad set", 330), ("ROAS, 8 weeks", 210), ("Before", 120), ("After", 170), ("In top 3? · share", 220),
            ("Creator ad", 190), ("Current #1", 240), ("Verdict", 152)]
    body = [head(T["eyebrow"], e(T["title"]), e(T["sub"]), size=60).replace("gap:12px", "gap:10px"),
            '<div style="display:flex; flex-direction:column">', header_row(cols)]
    for i, r in enumerate(rows):
        bd = "" if i == len(rows) - 1 else f" border-bottom:1px solid {LINE};"
        top = r["rank"] <= 3
        lab = f'{AUD.get(r["persona"], r["persona"])} · {r["os"]} · {r["lang"]}' + (" (new)" if labels[r["adset_id"]].endswith("(new)") else "")
        fg, bg, word = READ_PILL[r["read"]]
        name = r.get("no1_after") or "–"
        tag = r.get("no1_tag") or ""
        cur = (pill(f"NEW · {name}", "#1b2a33", "#53afd4", fs=20, pad="2px 10px") if tag == "NEW" else
               pill(f"NEW-OLD · {name}", "#6b2a12", "#fdd3c2", fs=20, pad="2px 10px") if tag == "NEW-OLD" else
               f'<p style="font-family:{OS_FONT}; font-size:24px; color:{INK}">{e(name)}</p>')
        body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:4px 16px;{bd}">'
                    + txt(330, e(lab), fs=24)
                    + f'<div style="width:210px; display:flex; flex-direction:column">{spark(r["weekly_roas"], lab, w=190, h=38)}</div>'
                    + cell(120, roas_pill(r["before"], fs=22, pad="2px 12px"))
                    + cell(170, roas_pill(r["after"], fs=22, pad="2px 12px") + arrow(r["before"], r["after"], fs=24), gap="8px")
                    + txt(220, (f'<b>Yes</b> · {place(r["rank"])} · {share(r["batch_share"])}' if top else f'No · {place(r["rank"])} · {share(r["batch_share"])}'), fs=24, color=INK if top else MUTED)
                    + txt(190, e(creative(r)), fs=24)
                    + cell(240, cur) + cell(152, pill(word, fg, bg, fs=22, pad="2px 12px"), align="end") + "</div>")
    body.append("</div>")
    body.append(foot(T["foot"], bottom=56))
    body.append(aside(T["note"]))
    return section(sid, "\n".join(body), gap=28, pad="96px 128px 152px")


def news_slide(sid, rows, T):
    cols = [("Ad set", 360), ("Before", 140), ("After · change", 280), ("Previous winner", 390), ("New winner (share)", 462)]
    body = [head(T["eyebrow"], e(T["title"]), None, size=60), '<div style="display:flex; flex-direction:column">', header_row(cols)]
    for i, r in enumerate(rows):
        bd = "" if i == len(rows) - 1 else f" border-bottom:1px solid {LINE};"
        lab = f'{AUD.get(r["persona"], r["persona"])} · {r["os"]} · {r["lang"]}'
        ev = (pill("NEW #1", "#1b2a33", "#53afd4", fs=22, pad="2px 10px") if r["event"] == "new #1"
              else pill("TOP 3", "#5a4a1e", "#e9e3d3", fs=22, pad="2px 10px"))
        pw = int(r.get("prev_winner_weeks") or 0)
        mover = str(r["mover"])[:22]
        prev = str(r["prev_winner"])[:22]
        body.append(f'<div style="display:flex; flex-direction:row; align-items:center; padding:6px 16px;{bd}">'
                    + txt(360, e(lab)) + cell(140, roas_pill(r["roas_before"]))
                    + cell(280, roas_pill(r["roas_after"]) + arrow(r["roas_before"], r["roas_after"], delta=True), gap="10px")
                    + txt(390, f"{e(prev)} · {pw} week{'s' if pw != 1 else ''}")
                    + cell(462, ev + f'<p style="font-family:{OS_FONT}; font-size:26px; color:{INK}">{e(mover)} '
                           f'{round((r.get("mover_before") or 0) * 100)}% → {round(r["mover_share"] * 100)}%</p>', gap="10px") + "</div>")
    body.append("</div>")
    body.append(foot(T["foot"], bottom=56))
    body.append(aside(T["note"]))
    return section(sid, "\n".join(body), gap=32, pad="104px 128px 152px")


def made_slide(sid, T):
    cards = ""
    for c in T["cards"]:
        bg = "#53afd4" if c.get("kind", "").startswith("New concept") else "#fc6e3d"
        cards += (f'<div style="display:flex; flex-direction:column; gap:8px; padding:24px 28px; background:{bg}; border-radius:24px">'
                  f'<p style="font-family:{OS_FONT}; font-size:18px; font-weight:700; letter-spacing:2px; text-transform:uppercase; color:{INK}">{e(c["kind"])}</p>'
                  f'<h3 style="font-family:{QS_FONT}; font-size:34px; font-weight:700; line-height:1.1; color:{INK}">{e(c["title"])}</h3>'
                  f'<p style="font-family:{OS_FONT}; font-size:24px; color:{INK}">{c["text"]}</p></div>')
    cols = 4 if len(T["cards"]) > 6 else 3
    body = [head(T["eyebrow"], e(T["title"]), None, size=72),
            f'<div style="display:grid; gap:20px; grid-template-columns:repeat({cols}, 1fr)">{cards}</div>',
            foot(T["foot"]), aside(T["note"])]
    return section(sid, "\n".join(body), gap=48)


def cover(T):
    return (f'<section id="cover" data-transition="fade" style="background:#F7F6F3;color:#2B2428;font-family:{OS_FONT};padding:128px;display:flex;flex-direction:column;justify-content:center">\n'
            f'<div style="position:absolute;left:0;top:0;width:24px;height:1080px;background:#FC6E3D"></div>\n'
            f'<div style="background:#53AFD4;border-radius:48px;padding:96px 112px;display:flex;flex-direction:column;gap:32px;width:1300px">\n'
            f'<p style="font-family:Quicksand, Arial, sans-serif;font-size:36px;font-weight:700;color:#2B2428;letter-spacing:4px;text-transform:uppercase">{e(T["eyebrow"])}</p>\n'
            f'<h1 style="font-family:Quicksand, Arial, sans-serif;font-size:112px;font-weight:700;line-height:1.05;color:#2B2428">{e(T["title"])}</h1>\n</div>\n'
            f'<p style="position:absolute;left:128px;bottom:64px;width:1200px;font-size:24px;color:#5E5C60">{e(T["foot"])}</p>\n</section>\n')


def divider(sid, T):
    return (f'<section id="{sid}" data-transition="fade" style="background:#443A40;color:#F7F6F3;font-family:{OS_FONT};padding:128px;display:flex;flex-direction:column;justify-content:center;gap:32px">\n'
            f'<p style="font-family:Quicksand, Arial, sans-serif;font-size:36px;font-weight:700;color:#8FD0EA;letter-spacing:4px;text-transform:uppercase">{e(T["eyebrow"])}</p>\n'
            f'<h1 style="font-family:Quicksand, Arial, sans-serif;font-size:120px;font-weight:700;line-height:1.05;color:#F7F6F3">{e(T["title"])}</h1>\n'
            f'<p style="font-size:40px;color:#E6E1E4;width:1300px">{e(T["text"])}</p>\n<aside>{e(T["note"])}</aside>\n</section>\n')


def main(folder):
    R = json.load(open(os.path.join(folder, "refresh_review.json")))
    T = json.load(open(os.path.join(folder, "deck_text.json")))
    end = R["end"]
    out = os.path.join(folder, "deck", "project", "slides")
    os.makedirs(out, exist_ok=True)
    slides = {"cover": cover(T["cover"]), "made": made_slide("made", T["made"])}
    if T.get("rules_html"):
        slides["rules"] = open(os.path.join(os.path.dirname(folder.rstrip("/")), T["rules_html"])).read()
    by = {}
    for r in R["adsets"]:
        by.setdefault(r["persona"], []).append(r)
    order_p = [p["persona"] for p in T["personas"]]
    slides["scoreboard"] = scoreboard("scoreboard", [(p, by[p], next(x["concept"] for x in T["personas"] if x["persona"] == p)) for p in order_p], end, T["scoreboard"])
    seq = ["cover", "made", "rules", "scoreboard"] if "rules" in slides else ["cover", "made", "scoreboard"]
    for P in T["personas"]:
        sid = P["id"]
        slides[sid] = persona_slide(sid, P["persona"], by[P["persona"]], end, P)
        seq.append(sid)
        if P.get("actions"):
            slides["act" + sid] = action_slide("act" + sid, {**P["actions"], "persona": PERSONA_TITLE.get(P["persona"], P["persona"])})
            seq.append("act" + sid)
    sections = {"s1": {"description": "What we made and where it went", "start": "cover"},
                "s2": {"description": "How it went: the scoreboard, then one slide per persona refresh, each followed by its action items", "start": "scoreboard"}}
    if T.get("followup"):
        F = T["followup"]
        a = json.load(open(os.path.join(os.path.dirname(folder.rstrip("/")), F["then"])))["adsets"]
        b = json.load(open(os.path.join(folder, F["now"])))["adsets"]
        groups = []
        for p in F["order"]:
            groups.append((F["names"][p], [x for x in a if x["persona"] == p], [x for x in b if x["persona"] == p]))
        slides["followdiv"] = divider("followdiv", F["divider"])
        slides["followup"] = followup_slide("followup", groups, F)
        seq += ["followdiv", "followup"]
        sections["s5"] = {"description": "Last week's refresh one week on", "start": "followdiv"}
        if F.get("actions"):
            slides["actfollowup"] = action_slide("actfollowup", {**F["actions"], "persona": F["actions"].get("persona", "last week's refresh")})
            seq.append("actfollowup")
    if T.get("creator") and R.get("creator"):
        C = T["creator"]
        slides["creatordiv"] = divider("creatordiv", C["divider"])
        slides["creator"] = creator_slide("creator", R["creator"], end, {**C, "title": C.get("title") or R["creator_summary"]["title"]})
        seq += ["creatordiv", "creator"]
        sections["s4"] = {"description": "Creator creative as ads", "start": "creatordiv"}
        if C.get("actions"):
            slides["actcreator"] = action_slide("actcreator", {**C["actions"], "persona": "Creator Creative as Ads"})
            seq.append("actcreator")
    if T.get("news"):
        N = T["news"]
        rows = sorted(R["account_news"], key=lambda r: (-round(r["roas_after"], 2), -(r["roas_after"] - r["roas_before"])))
        slides["newsdiv"] = divider("newsdiv", N["divider"])
        seq.append("newsdiv")
        for k, ev in (("news", "new #1"), ("news2", "new in top 3")):
            if N.get(k):
                slides[k] = news_slide(k, [r for r in rows if r["event"] == ev], N[k])
                seq.append(k)
        if N.get("actions"):
            slides["actnews"] = action_slide("actnews", {**N["actions"], "persona": "Account news"})
            seq.append("actnews")
        sections["s3"] = {"description": "Account news: adsets outside the refresh whose top spenders moved, then actions", "start": "newsdiv"}
    for sid, h in slides.items():
        with open(os.path.join(out, sid + ".html"), "w") as f:
            f.write(h)
    from datetime import datetime, timezone
    deck = {"v": 4, "createdOnFiles": {"v": 1, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
            "lists": "css", "title": T["title"], "order": seq, "sections": sections,
            "faces": {"quicksand": {"family": "Quicksand", "href": "https://fonts.googleapis.com/css2?family=Quicksand:wght@500;700&display=swap"},
                      "open-sans": {"family": "Open Sans", "href": "https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap"}},
            "designSystems": []}
    with open(os.path.join(folder, "deck", "project", "deck.json"), "w") as f:
        json.dump(deck, f)
    print(len(seq), "slides:", " ".join(seq))


if __name__ == "__main__":
    main(sys.argv[1])
