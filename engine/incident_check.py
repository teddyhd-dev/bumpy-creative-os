"""Checks each incident in core/incidents.csv against the store and Meta numbers we have.

Writes output/data/incident_check.csv: App Store money per day against a normal day (same weekday, the 4
weeks before the incident) during the incident and its effect, and Meta's iOS ROAS the week before, during
and after. Store money that held while Meta got worse points to tracking (what Meta saw); store money that
dropped points to a bug users hit.

When a daily Meta export by OS is in data/raw/meta_daily/ (meta_daily_<start>_<end>.csv: date, OS, spend,
purchases, purchase value), the measured end of effect will come from it (spec §3.5); until then
effect_until is the logged estimate.
"""
from __future__ import annotations

import glob
import gzip
import io
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import incidents  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output", "data")


def store_daily():
    files = sorted(glob.glob(os.path.join(ROOT, "data", "raw", "apple", "apple_proceeds_*.csv*")))
    if not files:
        return pd.Series(dtype=float)
    parts = []
    for f in files:
        txt = (gzip.open(f, "rt") if f.endswith(".gz") else open(f)).read().splitlines()
        i = next(k for k, l in enumerate(txt) if l.startswith("Date,"))
        d = pd.read_csv(io.StringIO("\n".join(txt[i:])))
        d["Date"] = pd.to_datetime(d.Date, format="%m/%d/%y")
        parts.append(pd.Series(d.drop(columns="Date").sum(axis=1).values, index=d.Date))
    s = pd.concat(parts)
    return s[~s.index.duplicated(keep="last")].sort_index()


def main():
    s = store_daily()
    G = pd.read_csv(os.path.join(OUT, "grid.csv"), low_memory=False)
    G = G[G.level == "adset"]
    rows = []
    for r in incidents.INC.itertuples():
        a, e = r.s, r.e
        base = s[(s.index >= a - pd.Timedelta(days=28)) & (s.index < a)]
        norm = base.groupby(base.index.dayofweek).mean()
        win = s[(s.index >= a) & (s.index <= e)]
        ratio = win / win.index.dayofweek.map(norm).values if len(win) and len(norm) else pd.Series(dtype=float)
        os_ = r.os if r.os in ("iOS", "Android") else None
        g = G[G.os == os_] if os_ else G
        wk = lambda d: (d - pd.Timedelta(days=d.weekday())).strftime("%Y-%m-%d")

        def roas(w):
            sc, rc = f"s_{w}", f"r_{w}"
            if sc not in g or rc not in g:
                return np.nan
            sp = pd.to_numeric(g[sc], errors="coerce").fillna(0)
            ro = pd.to_numeric(g[rc], errors="coerce").fillna(0)
            return (sp * ro).sum() / sp.sum() if sp.sum() else np.nan
        wb, wd, wa = wk(a - pd.Timedelta(days=7)), wk(a), wk(e + pd.Timedelta(days=7))
        store_held = len(ratio) and ratio.min() >= 0.9
        rows.append(dict(id=r.id, os=r.os, start=r.start, end=r.end, effect_until=r.e.date(), basis=r.effect_basis or "assumed",
                         store_days=len(ratio), store_min=round(float(ratio.min()), 2) if len(ratio) else np.nan,
                         store_mean=round(float(ratio.mean()), 2) if len(ratio) else np.nan,
                         meta_roas_week_before=round(roas(wb), 3), meta_roas_week_of=round(roas(wd), 3), meta_roas_week_after=round(roas(wa), 3),
                         reading=("no store data for these days yet" if not len(ratio) else
                                  "store money held: points to tracking (what Meta saw), not lost purchases" if store_held else
                                  "store money dropped: points to a bug users hit")))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT, "incident_check.csv"), index=False)
    for r in out.itertuples():
        print(f"{r.id} ({r.os}, effect to {r.effect_until}, {r.basis}): store {r.store_mean}× a normal day (lowest {r.store_min}×) · "
              f"Meta ROAS {r.meta_roas_week_before} → {r.meta_roas_week_of} → {r.meta_roas_week_after} · {r.reading}")


if __name__ == "__main__":
    main()
