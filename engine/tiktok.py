"""TikTok loader: ad group × country × week exports from TikTok Ads Manager.

Export recipe (spec §3.1 I): Ad group report, breakdown By week + Country/Region, columns
Ad group name, Ad group ID, Campaign name, Spend, Impressions, Clicks (destination),
App installs, Unique purchases (app), Purchase value (app), Currency USD.
Saved as data/raw/tiktok/tiktok_<start>_<end>.csv. Weeks are Monday–Sunday already.

Revenue = "Purchase value (app)": what TikTok credits itself through the MMP. It is TikTok's
own ruler, not comparable with Meta's (spec §3.4); App Store money is the common check.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from files import raw_files, supersede  # noqa: E402
from build import parse_name  # noqa: E402

ADD = ["spend", "rev", "impressions", "clicks", "installs", "purchases"]
COLS = {"Country/Region": "country_name", "Ad group name": "name", "Ad group ID": "adgroup_id",
        "Campaign name": "campaign", "Spend": "spend", "Impressions": "impressions",
        "Clicks (destination)": "clicks", "App installs": "installs",
        "Unique purchases (app)": "purchases", "Purchase value (app)": "rev", "By week": "by_week"}
# TikTok's country names that pycountry can't read
NAME_ISO = {"Bolivia,Plurinational": "BO", "Korea,Republic of": "KR", "Taiwan,Province of China": "TW",
            "Tanzania,United Republic of": "TZ", "Turkey": "TR", "Venezuela,Bolivarian Republic of Venezuela": "VE",
            "Curacao": "CW", "Unknown": None, "-": None}


def to_iso(name: str):
    if name in NAME_ISO:
        return NAME_ISO[name]
    try:
        import pycountry
        try:
            return pycountry.countries.lookup(name).alpha_2
        except LookupError:
            return pycountry.countries.search_fuzzy(name)[0].alpha_2
    except Exception:  # noqa: BLE001
        return None


def load_tiktok(store_names=None) -> pd.DataFrame:
    """Rows: adgroup × country × week, with parsed name fields, ISO code and App Store storefront."""
    parts = []
    for f in raw_files("tiktok", "tiktok"):
        d = pd.read_csv(f, encoding="utf-8-sig", dtype={"Ad group ID": str})
        d = d.rename(columns=COLS)
        d = d[d["by_week"].astype(str).str.contains("~")]          # drop the "Total of N results" row
        if "Currency" in d and (d["Currency"] != "USD").any():
            raise ValueError(f"{os.path.basename(f)}: non-USD rows; export in USD")
        d["start"] = pd.to_datetime(d["by_week"].str.slice(0, 10))
        d["end"] = pd.to_datetime(d["by_week"].str.slice(-10))
        d["_file"] = os.path.basename(f)
        for c in ADD:
            d[c] = pd.to_numeric(d[c].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
        parts.append(d)
    if not parts:
        return pd.DataFrame(columns=["adgroup_id", "week", "country", "store"] + ADD)
    d = pd.concat(parts, ignore_index=True)
    d = supersede(d, ADD)
    d["week"] = d["start"].dt.strftime("%Y-%m-%d")
    iso = {n: to_iso(n) for n in d["country_name"].unique()}
    d["country"] = d["country_name"].map(iso)
    if store_names is not None:
        from model import iso_to_store
        st = iso_to_store([c for c in set(iso.values()) if c], set(store_names))
        st["CW"] = None
        d["store"] = d["country"].map(st)
    P = pd.DataFrame([dict(name=n, **parse_name(n)) for n in d["name"].unique()])
    d = d.merge(P, on="name", how="left")
    d["migration"] = d["name"].str.contains("Migration", case=False)
    d["channel"] = "TikTok"
    return d


if __name__ == "__main__":
    t = load_tiktok()
    print(t.shape, t.spend.sum().round(), t.groupby("os").spend.sum().round().to_dict())
