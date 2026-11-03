"""Brief-time guard: new concept codes and v5 ad names that can't clash with what already exists.

    python3 checks/new_concept.py new                       # a fresh 6-character code, safe to use
    python3 checks/new_concept.py check --code k4Rm9p --name DatingContest
    python3 checks/new_concept.py names brief_names.txt     # or pipe names in: ... names -

Reads core/concepts.csv (every code and its name), core/code_aliases.csv, brain/experiments/, core/team.csv
and the persona list in core/naming-adset-v8.md. Exit code 1 when something must be fixed.
The brainstormer runs it before showing a brief; checks/validate.py runs the same checks on every
experiment record.
"""
from __future__ import annotations

import argparse
import csv
import glob
import os
import random
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
AWARE = {"Unaware", "ProblemAware", "SolutionAware", "ProductAware", "MostAware"}
SAFE_LOWER, SAFE_UPPER, SAFE_DIGIT = "abcdefghjkmnpqrstuvwxyz", "ABCDEFGHJKLMNPQRSTUVWXYZ", "23456789"


def norm_name(x):
    return re.sub(r"[^a-z]", "", str(x).lower())


def existing():
    """code → name, from the registry, confirmed aliases (the alias spelling is taken too) and experiments."""
    codes = {}
    p = os.path.join(ROOT, "core", "concepts.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            codes[r["code"]] = r["name"]
    p = os.path.join(ROOT, "core", "code_aliases.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p)):
            codes.setdefault(r["alias"], codes.get(r["code"], "") + " (old spelling of " + r["code"] + ")")
    for f in glob.glob(os.path.join(ROOT, "brain", "experiments", "EXP-*.md")):
        m = re.search(r"^concept_code:\s*(\S+)", open(f).read(), flags=re.M)
        n = re.search(r"^concept_name:\s*(.+)$", open(f).read(), flags=re.M)
        if m:
            codes.setdefault(m.group(1).strip("'\""), n.group(1).strip("'\" ") if n else "")
    return codes


def near(a, b):
    a, b = a.lower(), b.lower()
    if a == b or abs(len(a) - len(b)) > 1:
        return a == b
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) <= 1
    lo, hi = (a, b) if len(a) < len(b) else (b, a)
    return any(hi[:i] + hi[i + 1:] == lo for i in range(len(hi)))


def check_code(code, name, codes=None):
    """Returns (errors, notes). An existing code with the same concept name is fine (new variants)."""
    codes = codes if codes is not None else existing()
    errs, notes = [], []
    if not re.fullmatch(r"[A-Za-z0-9]{6}", code or ""):
        errs.append(f"code '{code}' must be exactly 6 letters/digits")
    if "(old spelling of" in codes.get(code, ""):
        errs.append(f"{code} is an old spelling of {codes[code].split('old spelling of ')[1].rstrip(')')}: use that code")
    elif code in codes:
        if norm_name(codes[code]).startswith(norm_name(name)) or norm_name(name).startswith(norm_name(codes[code])):
            notes.append(f"{code} is the existing concept '{codes[code]}': fine for new variants of it (move: past-winner-new-form)")
        else:
            errs.append(f"{code} already belongs to '{codes[code]}': pick a new code for '{name}'")
    else:
        for c, n in codes.items():
            if c.lower() == code.lower():
                errs.append(f"{code} differs only by letter case from {c} ('{n}')")
            elif near(c, code):
                errs.append(f"{code} is one character away from {c} ('{n}'): it would look like a typo")
        same = [c for c, n in codes.items() if norm_name(n) and norm_name(n) == norm_name(name)]
        if same:
            notes.append(f"the name '{name}' is already concept {', '.join(same)}: if it is the same idea, reuse that code; "
                         "if not, give this one a distinct name")
    return errs, notes


def new_code(codes=None):
    codes = codes if codes is not None else existing()
    for _ in range(10000):
        c = (random.choice(SAFE_LOWER) + random.choice(SAFE_DIGIT) + random.choice(SAFE_UPPER) + random.choice(SAFE_LOWER)
             + random.choice(SAFE_DIGIT) + random.choice(SAFE_LOWER))
        if not any(near(c, x) for x in codes):
            return c
    raise SystemExit("no free code found")


def angles():
    p = os.path.join(ROOT, "core", "angles.csv")
    return {r["angle"] for r in csv.DictReader(open(p))} if os.path.exists(p) else set()


def check_names(names, codes=None):
    """v5 ad names (core/naming-ad-v5.md). Returns {name: [problems]}; a problem starting with "note:" doesn't block."""
    from naming_audit import taxonomy, test_labels
    current, tests = taxonomy(include_past=False), test_labels()
    past = taxonomy() - current
    team = {r["code"]: r for r in csv.DictReader(open(os.path.join(ROOT, "core", "team.csv")))}
    codes = codes if codes is not None else existing()
    known_angles = angles()
    ap = os.path.join(ROOT, "core", "persona_aliases.csv")
    persona_alias = {r["spelling"]: r["persona"] for r in csv.DictReader(open(ap))} if os.path.exists(ap) else {}
    out = {}
    for n in names:
        n = n.strip()
        if not n:
            continue
        e = []
        if " " in n or re.search(r"\.(mp4|png|jpg|jpeg|mov)$", n, re.I) or "Copy" in n:
            e.append("no spaces, file extensions or '- Copy' in the name")
        if not re.fullmatch(r"[A-Za-z0-9-]+", n):
            e.append("only letters A–Z and digits 0–9 inside fields (no accents, emoji, apostrophes or other scripts)")
        f = n.split("-")
        if len(f) != 12:
            e.append(f"{len(f)} fields instead of 12 (a hyphen inside a field, or a field missing)")
            out[n] = e
            continue
        persona, aud, code, cname, hook, headline, angle, mod, fmt, strat, des, batch = f
        if persona in tests:
            e.append(f"'{persona}' is a test label, not a persona")
        elif persona in past:
            e.append(f"'{persona}' is a past persona: use a current one")
        elif persona not in current and persona in persona_alias:
            e.append(f"'{persona}' is an old spelling: write {persona_alias[persona]}")
        elif persona not in current:
            e.append(f"persona '{persona}' is not on the canonical list (core/naming-adset-v8.md, spellings in core/persona_aliases.csv)")
        if not re.fullmatch(r"[A-Z]{2}", aud):
            e.append(f"audience code '{aud}' must be 2 capital letters (US for English)")
        if not re.fullmatch(r"[A-Za-z0-9]{6}", code):
            e.append(f"concept code '{code}' must be exactly 6 letters/digits")
        elif "(old spelling of" in codes.get(code, ""):
            e.append(f"{code} is an old spelling: write {codes[code].split('old spelling of ')[1].rstrip(')')}")
        elif code in codes and norm_name(codes[code]).split("(")[0] and not (
                norm_name(cname).startswith(norm_name(codes[code])) or norm_name(codes[code]).startswith(norm_name(cname))):
            e.append(f"concept name '{cname}' doesn't match the registry: {code} is '{codes[code]}'")
        elif code not in codes:
            ce, _ = check_code(code, cname, codes)
            e += ce
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", cname):
            e.append(f"concept name '{cname}' should be PascalCase")
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", hook):
            e.append(f"hook '{hook}' should be PascalCase")
        if headline != headline.lower() or not headline:
            e.append(f"headline '{headline}' should be lowercase")
        if angle != angle.lower() or not angle:
            e.append(f"angle '{angle}' should be lowercase")
        elif known_angles and angle not in known_angles:
            e.append(f"note: angle '{angle}' isn't in core/angles.csv yet: fine if none fits, but tell the creative lead "
                     "so it can be added")
        if mod not in AWARE:
            e.append(f"modifier '{mod}' must be one of {', '.join(sorted(AWARE))}")
        if fmt not in ("VID", "IMG"):
            e.append("format must be VID or IMG")
        for k, v in (("strategist", strat), ("designer", des)):
            r = team.get(v)
            if not r or r["active"].lower() != "true":
                e.append(f"{k} '{v}' is not an active code in core/team.csv")
            elif r["role"] != k:
                e.append(f"{v} is a {r['role']}, not a {k}")
        if not re.fullmatch(r"Batch20\d\dWeek(0[1-9]|[1-4]\d|5[0-3])", batch):
            e.append(f"batch '{batch}' must be BatchYYYYWeekWW")
        out[n] = e
    return out


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("new")
    c = sub.add_parser("check")
    c.add_argument("--code", required=True)
    c.add_argument("--name", required=True)
    nm = sub.add_parser("names")
    nm.add_argument("file", help="file with one ad name per line, or - for stdin")
    a = ap.parse_args()
    if a.cmd == "new":
        print(new_code())
        return
    if a.cmd == "check":
        errs, notes = check_code(a.code, a.name)
        for x in notes:
            print("note:", x)
        for x in errs:
            print("FIX:", x)
        print("OK" if not errs else "NOT OK")
        sys.exit(1 if errs else 0)
    lines = (sys.stdin if a.file == "-" else open(a.file)).read().splitlines()
    res = check_names(lines)
    bad = 0
    for n, e in res.items():
        fix = [x for x in e if not x.startswith("note:")]
        if fix:
            bad += 1
            print(f"FIX {n}\n    " + "\n    ".join(e))
        elif e:
            print(f"OK  {n}\n    " + "\n    ".join(e))
    print(f"{len(res) - bad} of {len(res)} names OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
