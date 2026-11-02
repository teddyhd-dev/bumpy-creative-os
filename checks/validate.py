"""The repo's sensor: every shared file obeys its contract and every link resolves.

    python3 checks/validate.py                 # compare history files with the last commit (HEAD)
    python3 checks/validate.py --base main     # compare with another ref (CI uses the PR base)

Rules come from contracts/*.md (their front matter lists the required fields and sections), so the
guide a person reads and the check a machine runs are the same file. Exit code 1 on any error.
Run it before every commit; GitHub runs it on every push and pull request.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import re
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from new_concept import check_names  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
errors, warnings = [], []


def err(path, msg):
    errors.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def warn(path, msg):
    warnings.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def front(path):
    s = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", s, flags=re.S)
    if not m:
        return None, s
    try:
        return yaml.safe_load(m.group(1)) or {}, m.group(2)
    except yaml.YAMLError as e:
        return {"__yaml_error__": str(e)}, m.group(2)


def contracts():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "contracts", "*.md")):
        fm, _ = front(p)
        out[fm["contract"]] = fm
    return out


def check_fields(path, fm, C, expect):
    if fm is None:
        return err(path, "no front matter (--- block at the top)")
    if "__yaml_error__" in fm:
        return err(path, f"front matter is not valid YAML: {fm['__yaml_error__']}")
    if fm.get("contract") != expect:
        err(path, f"contract should be '{expect}', found '{fm.get('contract')}'")
    for k in C.get("front_matter", []):
        if k not in fm or fm[k] in (None, ""):
            err(path, f"missing front matter field '{k}'")


def check_sections(path, body, C):
    heads = set(re.findall(r"^## (.+?)\s*$", body, flags=re.M))
    for s in C.get("sections", []):
        if s not in heads:
            err(path, f"missing section '## {s}'")
    for b in C.get("generated_blocks", []):
        a, z = body.count(f"<!-- generated:start {b} -->"), body.count(f"<!-- generated:end {b} -->")
        if a != 1 or z != 1:
            err(path, f"the generated block '{b}' must appear exactly once (start and end markers)")


def git_show(base, path):
    try:
        return subprocess.run(["git", "show", f"{base}:{os.path.relpath(path, ROOT)}"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD", help="git ref to compare append-only files with")
    base = ap.parse_args().base
    C = contracts()

    # core registries
    minds_csv = os.path.join(ROOT, "core", "minds.csv")
    registry = {r["mind"]: r for r in csv.DictReader(open(minds_csv))} if os.path.exists(minds_csv) else {}
    if not registry:
        err(minds_csv, "missing or empty")
    team = {r["code"]: r for r in csv.DictReader(open(os.path.join(ROOT, "core", "team.csv")))}

    # minds
    for p in sorted(glob.glob(os.path.join(ROOT, "brain", "minds", "*", "mind.md"))):
        mid = os.path.basename(os.path.dirname(p))
        fm, body = front(p)
        check_fields(p, fm, C["mind"], "mind/1")
        check_sections(p, body, C["mind"])
        if fm and fm.get("mind") != mid:
            err(p, f"mind '{fm.get('mind')}' doesn't match its folder '{mid}'")
        if mid not in registry:
            err(p, f"'{mid}' is not in core/minds.csv")
        if fm and fm.get("mind") and f"{fm.get('persona')}-{fm.get('language')}" != fm.get("mind"):
            err(p, "mind must be <persona>-<language>")
        hist = os.path.join(os.path.dirname(p), "history.md")
        if not os.path.exists(hist):
            err(p, "history.md is missing next to mind.md")

    # history: format and append-only
    kinds = set(C["history"]["kinds"])
    for p in sorted(glob.glob(os.path.join(ROOT, "brain", "minds", "*", "history.md"))):
        fm, body = front(p)
        check_fields(p, fm, C["history"], "history/1")
        for h in re.findall(r"^## (.+)$", body, flags=re.M):
            m = re.match(r"^(\d{4}-\d{2}-\d{2}) · ([a-z0-9-]+) · (.+)$", h)
            if not m:
                err(p, f"entry header '## {h}' should be '## YYYY-MM-DD · <kind> · <who>'")
            elif m.group(2) not in kinds:
                err(p, f"unknown entry kind '{m.group(2)}' (allowed: {', '.join(sorted(kinds))})")
        old = git_show(base, p)
        if old is not None and not open(p, encoding="utf-8").read().startswith(old.rstrip("\n")):
            err(p, f"history is append-only: lines that existed in {base} were changed or removed "
                   "(add a 'correction' entry instead)")

    # creatives
    cpath = os.path.join(ROOT, "core", "concepts.csv")
    concepts = {r["code"]: r["name"] for r in csv.DictReader(open(cpath))} if os.path.exists(cpath) else {}
    seen, exact = {}, {}
    for p in sorted(glob.glob(os.path.join(ROOT, "brain", "creatives", "*.md"))):
        fm, body = front(p)
        check_fields(p, fm, C["creative"], "creative/1")
        check_sections(p, body, C["creative"])
        code = str((fm or {}).get("code", ""))
        slug = re.sub(r"[^a-z0-9]+", "-", str((fm or {}).get("name", "")).lower()).strip("-") or "untitled"
        if os.path.basename(p) != f"{code.lower()}-{slug}.md":
            err(p, f"file name should be {code.lower()}-{slug}.md")
        if concepts.get(code) and str((fm or {}).get("name", "")) != concepts[code]:
            err(p, f"name '{(fm or {}).get('name')}' differs from core/concepts.csv ('{concepts[code]}')")
        for k in [code]:
            if k in exact:
                err(p, f"code '{k}' is also in {exact[k]}")
            exact[k] = os.path.basename(p)
            if k.lower() in seen and seen[k.lower()] != os.path.basename(p):
                warn(p, f"code '{k}' differs only by letter case from one in {seen[k.lower()]} (old ad names; don't reuse)")
            seen.setdefault(k.lower(), os.path.basename(p))
        if fm and fm.get("decoded") is True:
            for f in ("First second", "Hook", "Message", "Why it stops the thumb"):
                m = re.search(rf"^- {re.escape(f)}:[ \t]*(.*)$", body, flags=re.M)
                if not m or not m.group(1).strip():
                    err(p, f"decoded is true but '{f}' is empty")
        snap = re.search(r"^- Snapshot:[ \t]*(\S+)", body, flags=re.M)
        if snap and not snap.group(1).startswith("http") and not os.path.exists(os.path.join(os.path.dirname(p), snap.group(1))):
            err(p, f"snapshot '{snap.group(1)}' not found (put images in brain/creatives/img/)")

    # experiments
    E = C["experiment"]
    for p in sorted(glob.glob(os.path.join(ROOT, "brain", "experiments", "EXP-*.md"))):
        fm, body = front(p)
        check_fields(p, fm, E, "experiment/1")
        check_sections(p, body, E)
        if not fm:
            continue
        exp_id = f"EXP-{fm.get('date')}-{fm.get('concept_code')}"
        if fm.get("id") != exp_id or os.path.basename(p) != f"{exp_id}.md":
            err(p, f"id and file name should be {exp_id}")
        if fm.get("move") not in E["moves"]:
            err(p, f"move '{fm.get('move')}' is not one of: {', '.join(E['moves'])}")
        if fm.get("status") not in E["statuses"]:
            err(p, f"status '{fm.get('status')}' is not one of: {', '.join(E['statuses'])}")
        for m in fm.get("minds") or []:
            if m not in registry:
                err(p, f"mind '{m}' is not in core/minds.csv")
            elif not os.path.exists(os.path.join(ROOT, "brain", "minds", m, "mind.md")):
                err(p, f"mind '{m}' has no file in brain/minds/")
        for t in fm.get("tickets") or []:
            if not re.match(r"^T-[0-9A-Za-z]{6}$", str(t)):
                err(p, f"ticket '{t}' should look like T-123456")
        for k in ("strategist", "designer"):
            if fm.get(k) and fm[k] not in team:
                err(p, f"{k} '{fm[k]}' is not a code in core/team.csv")
        cc = str(fm.get("concept_code", ""))
        if cc not in exact and cc.lower() in seen:
            err(p, f"concept code '{cc}' differs only by letter case from one in brain/creatives/{seen[cc.lower()]}: pick another code")
        reg = concepts.get(cc)
        if reg is None:
            err(p, f"concept code {cc} is not in core/concepts.csv: register it (code, name, confirmed) when the brief is approved")
        elif re.sub(r"[^a-z]", "", reg.lower()) != re.sub(r"[^a-z]", "", str(fm.get("concept_name", "")).lower()):
            err(p, f"concept_name '{fm.get('concept_name')}' differs from core/concepts.csv ('{reg}')")
        brief = body.split("## Brief", 1)[1].split("\n## ", 1)[0] if "## Brief" in body else ""
        names = re.findall(r"\b[A-Za-z]+-[A-Z]{2}-[A-Za-z0-9]{6}-[^\s`|]+-Batch20\d\dWeek\d\d\b", brief)
        for n, problems in check_names(names).items():
            for x in problems:
                err(p, f"ad name {n}: {x}")
        if not re.search(r"^## Prediction\s*\n+\s*\S", body, flags=re.M):
            err(p, "Prediction is empty: say how the exports will show it worked")

    # state
    q = os.path.join(ROOT, "state", "queue.json")
    if os.path.exists(q):
        data = json.load(open(q))
        need = C["state"]["queue_ticket_fields"]
        for t in data.get("tickets", []):
            miss = [k for k in need if k not in t]
            if miss:
                err(q, f"ticket {t.get('id')} is missing {', '.join(miss)}")
                break
    else:
        warn(q, "missing (run bash engine/run_all.sh)")

    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("ERROR:", e)
    n = len(glob.glob(os.path.join(ROOT, "brain", "**", "*.md"), recursive=True))
    print(f"{'FAILED' if errors else 'OK'}: {n} brain files checked, {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
