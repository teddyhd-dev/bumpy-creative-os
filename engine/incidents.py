"""App and tracking incidents (core/incidents.csv): weeks that shouldn't count against an adset, a creative
or a person.

An incident covers [start, effect_until]; when effect_until is blank its effect is assumed to last to the
end of that week (Sunday). A week is affected when any of its 7 days falls inside, for the incident's OS
(`all`, `iOS` or `Android`; Web adsets follow `all` only).
"""
from __future__ import annotations

import os

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    p = os.path.join(ROOT, "core", "incidents.csv")
    if not os.path.exists(p):
        return pd.DataFrame(columns=["id", "start", "end", "effect_until", "os", "kind", "what"])
    d = pd.read_csv(p, dtype=str).fillna("")
    d["s"] = pd.to_datetime(d.start)
    e = pd.to_datetime(d.end.where(d.end != "", d.start))
    sunday = e + pd.to_timedelta(6 - e.dt.weekday, unit="D")
    d["e"] = pd.to_datetime(d.effect_until.where(d.effect_until != "", None)).fillna(sunday)
    return d


INC = load()


def affecting(week, os_="all"):
    """Incident ids affecting the Mon–Sun week starting `week` for an adset on `os_`."""
    if INC.empty or not week:
        return []
    w0 = pd.to_datetime(week)
    w1 = w0 + pd.Timedelta(days=6)
    hit = INC[(INC.s <= w1) & (INC.e >= w0) & (INC.os.isin(["all", "", os_]))]
    return hit.id.tolist()


def label(ids):
    if not ids:
        return ""
    rows = INC[INC.id.isin(ids)]
    return "; ".join(f"{r.id} ({pd.to_datetime(r.start):%b %-d}–{pd.to_datetime(r.end or r.start):%b %-d}"
                     + (f", effect to {pd.to_datetime(r.effect_until):%b %-d}" if r.effect_until else "") + f"): {r.what}"
                     for r in rows.itertuples())


def in_window(w_from, w_to):
    """Incidents overlapping the weeks from w_from to w_to (inclusive), any OS."""
    if INC.empty:
        return INC
    a, b = pd.to_datetime(w_from), pd.to_datetime(w_to) + pd.Timedelta(days=6)
    return INC[(INC.s <= b) & (INC.e >= a)]
