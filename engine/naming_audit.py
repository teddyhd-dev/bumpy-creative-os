"""Naming audit: every ad and adset name checked against the conventions, weighted by spend.

Ad names: core/naming-ad-v5.md. Adset names: core/naming-adset-v8.md (persona taxonomy).
Language: for now the team writes country-style codes in names (JP, KR, UA, …; ads write US for English);
the audit compares languages after mapping US/ENG/IN→EN, BR→PT, JA→JP, KO→KR, UK→UA, ZH→CH, VI→VN.

Writes output/data/naming_audit.csv (one row per issue), naming_audit_summary.csv, naming_audit.md.
Never renames anything: renaming a live ad or adset resets its learning. Fix in the next batch; the engine
maps old names.
"""
from __future__ import annotations

import datetime as dt
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from adload import load_ads  # noqa: E402
from adparse import parse_ad  # noqa: E402
from build import JUDGED_OBJECTIVES  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output", "data")
LANG_SAME = {"US": "EN", "ENG": "EN", "BR": "PT", "IN": "EN", "JA": "JP", "KO": "KR", "UK": "UA", "ZH": "CH", "VI": "VN"}
AWARE = {"Unaware", "ProblemAware", "SolutionAware", "ProductAware", "MostAware"}
SEV = {"error": 0, "warn": 1, "info": 2}


def taxonomy():
    s = open(os.path.join(ROOT, "core", "naming-adset-v8.md"), encoding="utf-8").read()
    part = s[s.index("### Canonical Persona List"):s.index("### SubAngle")]
    return set(re.findall(r"^\| `([A-Za-z]+)` \|", part, flags=re.M))


def norm_lang(x):
    x = str(x or "").upper()
    return LANG_SAME.get(x, x)


def main():
    canon = taxonomy()
    team = set(pd.read_csv(os.path.join(ROOT, "core", "team.csv")).code)
    d = load_ads()
    d = d[d.spend.fillna(0) > 0].copy()
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), dtype={"adset_id": str}, low_memory=False)
    G = G[G.level == "adset"].set_index("adset_id")
    d["adset_id"] = d.adset_id.astype(str)
    d = d[d.adset_id.map(G.objective).isin(JUDGED_OBJECTIVES) | ~d.adset_id.isin(G.index)]
    P = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d.ad_name.unique()])
    d = d.merge(P, on="ad_name", how="left")
    d["copy"] = d.ad_name.str.contains(r"[–-]\s*Copy|\.(?:mp4|png|jpg|jpeg|mov)", case=False, regex=True)

    # one row per cleaned ad name × adset
    pa = d.groupby(["ad_clean", "adset_id"]).agg(spend=("spend", "sum"), first=("week", "min"), last=("week", "max")).reset_index()
    ad = d.groupby("ad_clean").agg(spend=("spend", "sum"), first=("week", "min"), last=("week", "max"),
                                   copies=("copy", "any"), raw=("ad_name", "nunique")).reset_index()
    ad = ad.merge(P.drop_duplicates("ad_clean").drop(columns=["ad_name"]), on="ad_clean", how="left")
    v5_start = ad[ad.ad_version == "v5"]["first"].min()
    ad["new"] = ad["first"] >= v5_start
    rows = []

    def add(sev, check, what, fix, r=None, **kw):
        base = dict(severity=sev, check=check, what=what, fix=fix)
        if r is not None:
            base.update(ad_name=r.ad_clean, code=r.concept, conceptname=r.conceptname, spend=round(r.spend, 2),
                        first_week=r.first, last_week=r.last)
        base.update(kw)
        rows.append(base)

    for r in ad.itertuples():
        v5 = r.ad_version == "v5"
        if r.new and not v5 and r.ad_version != "unstructured":
            add("warn", "not v5", f"launched {r.first}, after v5 started ({v5_start}), without strategist/designer codes",
                "Use the 12-field v5 name in the next batch", r)
        if r.ad_version == "unstructured" and r.spend >= 50:
            add("warn", "unreadable name", "no persona / code / format structure", "Rename in the next batch with the v5 template", r)
        if v5 and r.n_fields != 12:
            add("error", "field count", f"{r.n_fields} fields instead of 12 (a hyphen inside a field, or a field missing)",
                "Remove hyphens inside fields; every field present", r)
        if r.concept and not re.fullmatch(r"[A-Za-z0-9]{6}", r.concept):
            add("error" if v5 else "warn", "code format", f"concept code '{r.concept}' has {len(r.concept)} characters",
                "Concept codes are exactly 6 letters/digits", r)
        if not r.concept and r.ad_version in ("v5", "v4"):
            add("error", "code missing", "no concept code found in the name", "Put the 6-character code in field 3", r)
        if v5:
            bad = [x for x in (r.strategist, r.designer) if x and x not in team]
            if bad:
                add("error", "team code", f"{', '.join(bad)} not in core/team.csv", "Use a roster code (or add the person first)", r)
        if r.ad_version in ("v5", "v4") and r.awareness not in AWARE:
            add("warn", "modifier", "awareness stage missing or not one of the five", "Unaware · ProblemAware · SolutionAware · ProductAware · MostAware", r)
        if r.ad_version in ("v5", "v4") and r.fmt not in ("VID", "IMG"):
            add("warn", "format", "VID / IMG missing", "Add VID or IMG before the strategist code", r)
        if r.ad_version in ("v5", "v4"):
            if not r.batch:
                add("warn", "batch", "no BatchYYYYWeekWW", "Add the batch", r)
            elif pd.notna(r.batch_week) and pd.to_datetime(r.batch_week) > pd.to_datetime(r.first) + pd.Timedelta(days=7):
                add("warn", "batch", f"batch {r.batch} is after the ad's first spend ({r.first})", "Check the batch week", r)

    # persona as written in ad names (field 1), one row per spelling
    st = ad[(ad.ad_version != "unstructured") & (ad.ad_persona_raw != "")]
    for tok, g in st.groupby("ad_persona_raw"):
        if tok in canon:
            continue
        mapped = g.ad_persona.mode().iat[0]
        add("warn", "persona not canonical in ad name",
            f"'{tok}' in {len(g)} ad names (read as {mapped}{'' if mapped in canon else ', which is not on the taxonomy either'})",
            f"Write {mapped}" if mapped in canon else "Add this persona to the taxonomy, then use that name",
            ad_name=g.sort_values("spend").ad_clean.iloc[-1], ad_persona=mapped, spend=round(g.spend.sum(), 2),
            first_week=g["first"].min(), last_week=g["last"].max())
    cp = ad[ad.copies]
    if len(cp):
        add("info", "copy or file suffix", f"{len(cp)} ad names carry '- Copy' or a file extension (.mp4, .png)",
            "Name ads without '- Copy' / '.mp4' (the engine strips them, so this is cosmetic)", spend=round(cp.spend.sum(), 2))

    # codes: case collisions, typos, and one code used for different concepts
    cc = ad[ad.concept != ""].copy()
    cc["low"] = cc.concept.str.lower()
    for low, g in cc.groupby("low"):
        spell = g.groupby("concept").spend.sum().sort_values(ascending=False)
        names = sorted(set(g.conceptname.str.lower()) - {""})
        if len(spell) > 1:
            add("error", "code case collision", f"{' / '.join(spell.index)} differ only by letter case "
                f"(concepts: {', '.join(names)}; {', '.join(f'{k} ${v:,.0f}' for k, v in spell.items())})",
                "Same concept → use one spelling; different concepts → give one a new code",
                code=" / ".join(spell.index), conceptname=", ".join(names), spend=round(g.spend.sum(), 2))
        for code, h in g.groupby("concept"):
            nm = h.groupby(h.conceptname.str.lower()).spend.sum().sort_values(ascending=False)
            nm = nm[nm.index != ""]
            if len(nm) > 1:
                stem = lambda x: re.sub(r"\d+$", "", x)
                main = stem(nm.index[0])
                family = all(stem(k).startswith(main) or main.startswith(stem(k)) for k in nm.index)
                if family:
                    add("warn", "concept name written several ways", f"code {code}: {', '.join(f'{k} (${v:,.0f})' for k, v in nm.items())}",
                        "Keep one generic concept name; put the variant detail in the hook field",
                        code=code, conceptname=", ".join(nm.index), spend=round(h.spend.sum(), 2))
                else:
                    add("error", "one code, several concepts", f"code {code} is used for {', '.join(f'{k} (${v:,.0f})' for k, v in list(nm.items())[:6])}"
                        + (f" and {len(nm) - 6} more" if len(nm) > 6 else ""),
                        "One code per concept: keep the code for the main one, new codes for the others",
                        code=code, conceptname=", ".join(nm.index[:6]), spend=round(h.spend.sum(), 2))
    # likely typos: two codes, same concept name, one character apart (the concept gets split in two)
    def near(a, b):
        if a == b or abs(len(a) - len(b)) > 1:
            return False
        if len(a) == len(b):
            return sum(x != y for x, y in zip(a, b)) == 1
        lo, hi = (a, b) if len(a) < len(b) else (b, a)
        return any(hi[:i] + hi[i + 1:] == lo for i in range(len(hi)))
    byname = cc.groupby([cc.conceptname.str.lower(), "concept"]).spend.sum().reset_index()
    done = set()
    for nmx, g in byname[byname.conceptname != ""].groupby("conceptname"):
        codes = g.sort_values("spend", ascending=False).concept.tolist()
        for i, a in enumerate(codes):
            for b in codes[i + 1:]:
                if near(a, b) and (a, b) not in done:
                    done.add((a, b))
                    sa, sb = g.set_index("concept").spend[a], g.set_index("concept").spend[b]
                    add("error", "likely typo of another code", f"{b} (${sb:,.0f}) looks like a typo of {a} (${sa:,.0f}), both '{nmx}': "
                        "the data treats them as two concepts", f"Use {a} in new names; the engine should map {b} → {a} once confirmed",
                        code=f"{a} / {b}", conceptname=nmx, spend=round(sa + sb, 2))

    # ad vs its adset: persona and language
    pa = pa.merge(P.drop_duplicates("ad_clean")[["ad_clean", "ad_persona", "ad_persona_raw", "lang", "concept", "conceptname", "ad_version"]],
                  on="ad_clean", how="left")
    pa["adset_persona"] = pa.adset_id.map(G.persona)
    pa["adset_lang"] = pa.adset_id.map(G.lang)
    pa["adset"] = pa.adset_id.map(G.short)
    pa = pa[pa.adset_persona.notna()]
    pm = pa[(~pa.ad_persona.isin(["Unknown", ""])) & (~pa.adset_persona.isin(["General", "Unknown"])) & (pa.ad_persona != pa.adset_persona)]
    for (aid, ap), g in pm.groupby(["adset_id", "ad_persona"]):
        if g.spend.sum() < 50:
            continue
        top = g.sort_values("spend").iloc[-1]
        add("error", "persona mismatch", f"{len(g)} ad{'s' if len(g) > 1 else ''} named for {ap} ran in a {top.adset_persona} adset "
            f"(codes {', '.join(sorted(set(g.concept) - {''}))[:60]})",
            "A concept moved to another persona keeps working, but name the copies for the adset's persona so results credit the right audience",
            ad_name=top.ad_clean, code=top.concept, conceptname=top.conceptname, spend=round(g.spend.sum(), 2), first_week=g["first"].min(),
            last_week=g["last"].max(), adset=top.adset, adset_id=aid, ad_persona=ap, adset_persona=top.adset_persona)
    pa["al"], pa["sl"] = pa.lang.map(norm_lang), pa.adset_lang.map(norm_lang)
    lm = pa[(pa.al != "") & (~pa.sl.isin(["", "?", "ALL"])) & (pa.al != pa.sl)]
    for (aid, al), g in lm.groupby(["adset_id", "lang"]):
        if g.spend.sum() < 50:
            continue
        top = g.sort_values("spend").iloc[-1]
        add("warn", "language mismatch", f"{len(g)} ad{'s' if len(g) > 1 else ''} coded {al} ran in a {top.adset_lang} adset",
            "Check: localized copy for this adset's language, or the audience code in the ad name",
            ad_name=top.ad_clean, code=top.concept, conceptname=top.conceptname, spend=round(g.spend.sum(), 2), first_week=g["first"].min(),
            last_week=g["last"].max(), adset=top.adset, adset_id=aid, ad_lang=al, adset_lang=top.adset_lang)

    # adset names
    sc = [c for c in G.columns if c.startswith("s_")]
    G = G.copy()
    G["spend_total"] = G[sc].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    for aid, r in G[G.spend_total > 0].iterrows():
        kw = dict(adset=r.short, adset_id=aid, adset_persona=r.persona, adset_lang=r.lang, spend=round(r.spend_total, 2),
                  first_week=r.first_week, last_week=r.last_week, ad_name=r["name"])
        if r.persona not in canon and r.persona not in ("Unknown",):
            add("warn", "adset persona not on taxonomy", f"persona '{r.persona}' is not on the canonical list",
                "Add it to the taxonomy (core/naming-adset-v8.md) or use the canonical name", **kw)
        if r.lang in ("JA", "KO", "UK", "ZH", "VI"):
            add("warn", "language written two ways", f"legacy name read as {r.lang}; current names write {LANG_SAME[r.lang]}",
                f"Write {LANG_SAME[r.lang]} (country-style codes for now)", **kw)
        if r.lang in ("?", "") or pd.isna(r.lang):
            add("warn", "adset language unreadable", "no language in the adset name", "Use the v8 adset template", **kw)
        if "  " in str(r["name"]):
            add("info", "adset spacing", "double space in the name", "Single '/' separators, no double spaces", **kw)
    v8 = G[G["name"].astype(str).str.startswith("AS / ")]
    if len(v8):
        add("info", "adset separators", f"{len(v8)} v8 adset names use ' / ' with spaces; the convention says '/' with no spaces (128-character limit)",
            "Use '/' without spaces for new adsets", spend=round(v8.spend_total.sum(), 2))

    A = pd.DataFrame(rows)
    A["rank"] = A.severity.map(SEV)
    A = A.sort_values(["rank", "check", "spend"], ascending=[True, True, False]).drop(columns="rank")
    cols = ["severity", "check", "what", "fix", "ad_name", "code", "conceptname", "adset", "adset_id", "ad_persona",
            "adset_persona", "ad_lang", "adset_lang", "spend", "first_week", "last_week"]
    A = A.reindex(columns=cols)
    A.to_csv(os.path.join(OUT, "naming_audit.csv"), index=False)
    S = A.groupby(["severity", "check"]).agg(issues=("what", "size"), spend=("spend", "sum")).reset_index()
    S["rank"] = S.severity.map(SEV)
    S = S.sort_values(["rank", "spend"], ascending=[True, False]).drop(columns="rank")
    S.to_csv(os.path.join(OUT, "naming_audit_summary.csv"), index=False)
    tot = d.spend.sum()
    lines = [f"# Naming audit · {dt.date.today().isoformat()}", "",
             f"{ad.shape[0]} ad names with spend since {d.week.min()} (${tot / 1e6:.2f}M). "
             + (f"v5 names (with strategist and designer codes) since {v5_start}: {int((ad.ad_version == 'v5').sum())} ads."
                if pd.notna(v5_start) else "No v5 names yet (no strategist / designer codes in any ad name)."), "",
             "| Severity | Check | Issues | Spend |", "|---|---|---|---|"]
    lines += [f"| {r.severity} | {r.check} | {r.issues} | ${r.spend:,.0f} |" for r in S.itertuples()]
    open(os.path.join(OUT, "naming_audit.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
