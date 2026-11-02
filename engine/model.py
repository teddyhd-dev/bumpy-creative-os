"""One joined data model for every source.

Spine: Mon–Sun weeks × adset (adset export). Joined on the same keys:
  - adset × country × week   (monthly country exports, spread evenly over days)
  - ad × adset × week        (monthly ad exports, spread evenly over days)
  - country × week App Store proceeds (daily App Store Connect file)

Run:  python3 engine/model.py      -> writes data/model/*.pkl
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build import load_raw, parse_name, JUDGED_OBJECTIVES  # noqa: E402
from adload import load_ads  # noqa: E402
from adparse import parse_ad  # noqa: E402
from apple import load_apple  # noqa: E402
from files import raw_files, supersede  # noqa: E402
from codes import concept_keys  # noqa: E402

ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
MODEL = os.path.join(ROOT, "data", "model")
ADD = ["spend", "rev", "impressions", "installs", "clicks", "purchases", "hook_x_imp"]

# Meta ISO-2 -> App Store storefront name (territories folded into the storefront they buy from)
OVERRIDE = {
    "CN": "China mainland", "BN": "Brunei", "CV": "Cape Verde", "CD": "Congo, Democratic Republic of the",
    "CG": "Congo, Republic of the", "CI": "Côte d’Ivoire", "XK": "Kosovo", "MO": "Macau", "FM": "Micronesia",
    "RU": "Russia", "ST": "São Tomé and Príncipe", "KN": "St. Kitts and Nevis", "LC": "St. Lucia",
    "VC": "St. Vincent and the Grenadines",
    "PR": "United States", "GU": "United States", "VI": "United States", "AS": "United States", "MP": "United States",
    "RE": "France", "GP": "France", "MQ": "France", "GF": "France", "PF": "France", "NC": "France", "YT": "France",
    "PM": "France", "BL": "France", "MF": "France", "JE": "United Kingdom", "GG": "United Kingdom",
    "IM": "United Kingdom", "GI": "United Kingdom", "FO": "Denmark", "GL": "Denmark",
}


def week_of(day: pd.Series) -> pd.Series:
    return (day - pd.to_timedelta(day.dt.weekday, unit="D")).dt.strftime("%Y-%m-%d")


def spread_weeks(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    """Spread each export bucket evenly over its days, then sum into Mon–Sun weeks."""
    df = df.copy()
    df["days"] = (df["end"] - df["start"]).dt.days + 1
    rep = df.loc[df.index.repeat(df["days"])].copy()
    rep["off"] = rep.groupby(level=0).cumcount()
    rep["day"] = rep["start"] + pd.to_timedelta(rep["off"], unit="D")
    for c in ADD:
        if c in rep:
            rep[c] = rep[c].fillna(0) / rep["days"]
    rep["week"] = week_of(rep["day"])
    cols = [c for c in ADD if c in rep]
    return rep.groupby(keys + ["week"])[cols].sum().reset_index()


def iso_to_store(codes, store_names):
    try:
        import pycountry
    except ImportError:  # pragma: no cover
        pycountry = None
    out = {}
    for c in codes:
        if c in OVERRIDE:
            out[c] = OVERRIDE[c]
            continue
        name = None
        if pycountry is not None:
            o = pycountry.countries.get(alpha_2=c)
            if o is not None:
                for n in (getattr(o, "common_name", None), o.name, getattr(o, "official_name", None)):
                    if n and n in store_names:
                        name = n
                        break
        out[c] = name
    return out


def build_model():
    os.makedirs(MODEL, exist_ok=True)
    # ---- spine: adset × week ------------------------------------------------
    a = load_raw()
    P = a["name"].map(parse_name).apply(pd.Series)
    a = pd.concat([a, P], axis=1)
    a["judged"] = a["objective"].isin(JUDGED_OBJECTIVES)
    adset_dim = a.sort_values("week").groupby("adset_id")[
        ["name", "version", "persona", "subangle", "os", "geo", "lang", "gender", "objective", "modifier", "launch", "judged"]].last()
    a_week = a[["adset_id", "week", "spend", "rev", "impressions", "installs", "clicks", "purchases", "frequency", "hook_rate"]].copy()

    # name+week -> id (11 names were reused; pick the id that spent most that week)
    nm = a[a.spend > 0].sort_values("spend", ascending=False).drop_duplicates(["name", "week"])[["name", "week", "adset_id"]]
    nm_any = a.groupby(["name", "adset_id"]).spend.sum().reset_index().sort_values("spend", ascending=False).drop_duplicates("name").set_index("name")["adset_id"]

    # ---- adset × country × week ---------------------------------------------
    fr = []
    for p in raw_files("country", "country"):
        f = pd.read_csv(p, encoding="utf-8-sig", keep_default_na=False, na_values=[""],
                        usecols=lambda c: c in ["Ad set name", "Country", "Impressions", "Amount spent (USD)",
                                                "Purchase ROAS (return on ad spend)", "App installs", "Link clicks",
                                                "Purchases", "Hook Rate", "Reporting starts", "Reporting ends"])
        f["_file"] = os.path.basename(p)
        fr.append(f)
    c = pd.concat(fr, ignore_index=True).rename(columns={
        "Ad set name": "name", "Country": "country", "Impressions": "impressions", "Amount spent (USD)": "spend",
        "Purchase ROAS (return on ad spend)": "roas_meta", "App installs": "installs", "Link clicks": "clicks",
        "Purchases": "purchases", "Hook Rate": "hook_rate", "Reporting starts": "start", "Reporting ends": "end"})
    for col in ["impressions", "spend", "roas_meta", "installs", "clicks", "purchases", "hook_rate"]:
        c[col] = pd.to_numeric(c[col], errors="coerce")
    c["rev"] = (c["roas_meta"] * c["spend"]).fillna(0)
    c["hook_x_imp"] = c["hook_rate"] * c["impressions"]
    c["start"] = pd.to_datetime(c["start"])
    c["end"] = pd.to_datetime(c["end"])
    c = c[c["spend"].fillna(0) > 0]
    c = supersede(c, ["spend", "rev", "impressions", "installs", "clicks", "purchases", "hook_x_imp"])
    cw = spread_weeks(c, ["name", "country"])
    cw = cw.merge(nm, on=["name", "week"], how="left")
    cw["adset_id"] = cw["adset_id"].fillna(cw["name"].map(nm_any))
    cw = cw.dropna(subset=["adset_id"])
    cw = cw.groupby(["adset_id", "country", "week"])[[x for x in ADD if x in cw]].sum().reset_index()

    # ---- ad × adset × week ----------------------------------------------------
    d = load_ads()
    Pa = pd.DataFrame([dict(ad_name=n, **parse_ad(n)) for n in d["ad_name"].unique()])
    d = d.merge(Pa, on="ad_name", how="left")
    d["concept_key"] = concept_keys(d)
    ad_dim = d.sort_values("start").groupby("ad_id")[[
        "ad_name", "ad_clean", "ad_version", "ad_persona", "lang", "concept_key", "conceptname", "hook", "headline", "angle",
        "awareness", "fmt", "strategist", "designer", "batch"]].last()
    aw = spread_weeks(d, ["ad_id", "adset_id"])
    aw = aw.join(ad_dim[["concept_key"]], on="ad_id")

    # ---- App Store proceeds × country × week -----------------------------------
    ap = load_apple()
    apw = ap.groupby(week_of(pd.Series(ap.index, index=ap.index))).sum()
    apw.index.name = "week"
    apw = apw.reset_index().melt(id_vars="week", var_name="store", value_name="proceeds")
    iso = iso_to_store(sorted(cw["country"].unique()), set(ap.columns))
    cw["store"] = cw["country"].map(iso)

    # weeks fully covered by every source
    last_full = min(pd.Timestamp(d["end"].max()), pd.Timestamp(c["end"].max()), ap.index.max())
    full_weeks = [w for w in sorted(a_week.week.unique()) if pd.Timestamp(w) + pd.Timedelta(days=6) <= last_full]

    out = dict(adset_week=a_week, adset_dim=adset_dim, country_week=cw, ad_week=aw, ad_dim=ad_dim,
               apple_week=apw, meta=pd.DataFrame({"full_weeks": full_weeks}))
    for k, v in out.items():
        v.to_pickle(os.path.join(MODEL, f"{k}.pkl"))
    # reconciliation
    rec = pd.DataFrame({
        "adset_export": a_week.groupby("week").spend.sum(),
        "country_files": cw.groupby("week").spend.sum(),
        "ad_files": aw.groupby("week").spend.sum()}).loc[full_weeks]
    rec["country_vs_adset"] = rec.country_files / rec.adset_export - 1
    rec["ad_vs_adset"] = rec.ad_files / rec.adset_export - 1
    rec.to_csv(os.path.join(MODEL, "reconcile.csv"))
    unm = cw[cw.store.isna()].groupby("country").spend.sum().sort_values(ascending=False)
    return rec, unm, full_weeks


if __name__ == "__main__":
    rec, unm, fw = build_model()
    print(rec.round(3).to_string())
    print("full weeks", fw[0], "→", fw[-1], len(fw))
    print("spend in countries with no App Store storefront:", round(unm.sum()), unm.head(10).round(0).to_dict())
