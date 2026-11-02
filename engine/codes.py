"""Concept codes: one key per concept across the engine.

Confirmed fixes (typos, letter case, a concept filed under the wrong code) live in core/code_aliases.csv;
concept names live in core/concepts.csv. Every step that groups ads by concept builds its key here.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def code_aliases():
    p = os.path.join(ROOT, "core", "code_aliases.csv")
    if not os.path.exists(p):
        return pd.DataFrame(columns=["alias", "conceptname", "code", "status", "note"])
    a = pd.read_csv(p, dtype=str).fillna("")
    return a[a.status.str.lower() == "confirmed"]


def apply_code_aliases(code, conceptname):
    """code / conceptname: Series. Rules with a concept name apply first and only to ads with that name."""
    code = pd.Series(code).copy()
    al = code_aliases()
    low = pd.Series(conceptname, index=code.index).fillna("").str.lower()
    for r in al[al.conceptname != ""].itertuples():
        code[(code == r.alias) & (low == r.conceptname.lower())] = r.code
    gen = al[al.conceptname == ""]
    return code.replace(dict(zip(gen.alias, gen.code)))


def concept_keys(d):
    """The concept key of each ad row: its (fixed) concept code, or 'name:<ad>' when the name has no code."""
    key = pd.Series(np.where(d["concept"] != "", d["concept"], "name:" + d["ad_clean"]), index=d.index)
    return apply_code_aliases(key, d["conceptname"] if "conceptname" in d else pd.Series("", index=d.index))


def concept_names():
    """core/concepts.csv: code → the concept's name."""
    p = os.path.join(ROOT, "core", "concepts.csv")
    if not os.path.exists(p):
        return {}
    c = pd.read_csv(p, dtype=str).fillna("")
    return dict(zip(c.code, c.name))
