"""Persona cards from the Notion Persona Card Library, mapped to the v8 persona taxonomy (spec §13).

Reads the newest data/raw/notion/notion_personas_*.html export. Each card is mapped to a canonical
persona from the persona field of its top-spender ad names (most reliable); otherwise by name
(marked "by name, confirm"). Cards that can't be mapped are kept and listed for the creative lead.
"""
from __future__ import annotations

import glob
import html
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adparse import parse_ad  # noqa: E402

ROOT = os.path.dirname(HERE)
BY_NAME = [  # (pattern in the card name, canonical persona)
    (r"turned to asian man", "AsianMaleLover"), (r"passport bro", "PassportBro"), (r"passport girl|relocate\)", "GirlWantsToRelocate"),
    (r"indian young", "EgoBoostForIndianBoy"), (r"muslim", "MuslimMatchWorldwide"), (r"single mom", "SingleMom"),
    (r"friend", "IntlFriendFinder"), (r"latina", "LatinaFemaleLover"), (r"lgbt", "LGBTQ"), (r"gringo", "GringoMaleLover"),
    (r"christian", "ChristianMatchWorldwide"), (r"asian dating", "AsianFemaleLover"), (r"40\+|second chance|304050|30\+ yolo", "MatureDating"),
    (r"interacial|interracial|black people", "InterracialDatingSeekers"),
]


def _txt(c):
    t = html.unescape(re.sub(r"<br\s*/?>", "\n", c))
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"[ \t]+", " ", t).strip()


def load_cards():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "notion", "notion_personas_*.html")))
    if not files:
        return []
    s = open(files[-1], encoding="utf-8").read()
    heads = [re.sub(r"<[^>]+>", "", h).strip() for h in re.findall(r"<th[^>]*>(.*?)</th>", s, flags=re.S)]
    cards = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", s, flags=re.S)[1:]:
        cells = [_txt(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S)]
        d = dict(zip(heads, cells))
        name = d.get("Persona Name", "").strip().strip("“”\"")
        if not name or name.lower() == "untitled":
            continue
        top = re.findall(r"[A-Za-z0-9]+-[A-Z]{2}-[A-Za-z0-9]{5,7}-[^\s]+?\.(?:mp4|png|jpg)", d.get("Top Spender with Status", ""))
        ps = [parse_ad(n.rsplit(".", 1)[0].replace(" (2)", "")).get("ad_persona") for n in top]
        ps = [p for p in ps if p and p != "Unknown"]
        if ps:
            persona, how = max(set(ps), key=ps.count), "from its top-spender ads"
        else:
            persona, how = "", "unmapped"
            for pat, canon in BY_NAME:
                if re.search(pat, name.lower()):
                    persona, how = canon, "by name, confirm"
                    break
        links = []
        for k in ("Content 1", "Content 2", "Content 3"):
            links += re.findall(r"https?://[^\s\"'<>]+", d.get(k, ""))
        clean = lambda v: re.sub(r"\s*\n\s*", "\n", v).strip()[:1200]
        cards.append(dict(
            card=name, persona=persona, mapped=how, status=d.get("Test Status", "").replace("Successs", "Success"),
            churn_app=d.get("Churn", ""), lore=clean(d.get("Persona Lore", "")), pattern=clean(d.get("Winning Pattern", "")),
            message=clean(d.get("Proven Message", "")), hook=clean(d.get("Hook-Word / Headline", "")),
            top_ads=[t.rsplit(".", 1)[0].replace(" (2)", "") for t in top][:4], links=[l.split("?")[0] for l in links][:3]))
    return cards


if __name__ == "__main__":
    for c in load_cards():
        print(f"{c['card'][:40]:40} → {c['persona'] or '—':26} ({c['mapped']}) · {c['status']} · {len(c['links'])} links")
