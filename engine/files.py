"""Raw-file helpers shared by every loader.

Rule: every export covers the whole account for its date range. When two exports
overlap, the newer one wins for the overlapping days ("newer" = later end date,
then later start date, then file name). Rows from an older file are scaled down by
the share of their days a newer file covers, and dropped when fully covered.
"""
from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")


def raw_files(source: str, prefix: str) -> list[str]:
    return sorted(glob.glob(os.path.join(RAW, source, f"{prefix}_*.csv")))


def supersede(df: pd.DataFrame, additive: list[str], file_col: str = "_file",
              start_col: str = "start", end_col: str = "end") -> pd.DataFrame:
    if df.empty or df[file_col].nunique() < 2:
        return df
    df = df.copy()
    cov = df.groupby(file_col).agg(cs=(start_col, "min"), ce=(end_col, "max")).reset_index()
    cov = cov.sort_values(["ce", "cs", file_col]).reset_index(drop=True)
    day0 = cov.cs.min()
    n = int((cov.ce.max() - day0).days) + 1
    after = np.zeros((len(cov), n), dtype=bool)
    for i in range(len(cov) - 2, -1, -1):
        after[i] = after[i + 1]
        a = int((cov.cs[i + 1] - day0).days)
        b = int((cov.ce[i + 1] - day0).days)
        after[i, a:b + 1] = True
    rank = {f: i for i, f in enumerate(cov[file_col])}
    s_idx = (df[start_col] - day0).dt.days.to_numpy()
    e_idx = (df[end_col] - day0).dt.days.to_numpy()
    factor = np.ones(len(df))
    for f, i in rank.items():
        m = (df[file_col] == f).to_numpy()
        if not m.any() or not after[i].any():
            continue
        cs = np.concatenate([[0], np.cumsum(after[i])])
        covered = cs[e_idx[m] + 1] - cs[s_idx[m]]
        days = e_idx[m] - s_idx[m] + 1
        factor[m] = 1 - covered / days
    for c in additive:
        if c in df:
            df[c] = df[c] * factor
    return df[factor > 0]
