"""App Store Connect proceeds by territory, daily.

Reads every data/raw/apple/apple_proceeds_*.csv (App Store Connect → Proceeds →
by territory, daily). When files overlap, the file that ends latest wins for the
overlapping days.
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from files import raw_files  # noqa: E402


def _read(p):
    a = pd.read_csv(p, skiprows=4, encoding="utf-8-sig")
    a["Date"] = pd.to_datetime(a["Date"], format="%m/%d/%y")
    a = a.set_index("Date")
    a.columns = [c.replace(" Proceeds", "") for c in a.columns]
    return a.apply(pd.to_numeric, errors="coerce").fillna(0)


def load_apple():
    frames = []
    for p in raw_files("apple", "apple_proceeds"):
        a = _read(p)
        frames.append((a.index.max(), a.index.min(), p, a))
    if not frames:
        raise FileNotFoundError("No App Store proceeds file in data/raw/apple/")
    frames.sort(key=lambda t: (t[0], t[1], t[2]))
    out = pd.concat([f[3] for f in frames])
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out.fillna(0)
