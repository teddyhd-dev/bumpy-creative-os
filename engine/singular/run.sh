#!/usr/bin/env bash
# Singular vs Meta: rebuild the comparison from data/raw/singular + the Meta and App Store exports.
# Outputs in output/data/singular/ (weekly_os.csv, adset_week.csv, persona.csv, country.csv, name_map.csv, …).
set -euo pipefail
cd "$(dirname "$0")"
python3 load.py
python3 names.py
python3 compare.py
python3 compare2.py
