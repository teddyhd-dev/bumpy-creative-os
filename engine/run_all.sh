#!/usr/bin/env bash
# Rebuild every dataset from data/raw, in dependency order.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 engine/build.py          # adset grid, account, checks, drivers
python3 engine/naming_audit.py   # naming_audit.csv: ad and adset names vs the conventions, weighted by spend
python3 engine/rootcause.py      # rc_*  (diagnosis)
python3 engine/creative_relay.py # cr_*  (creatives)
python3 engine/model.py          # data/model/*.pkl (joined model)
python3 engine/eras.py           # era_*  (Singular switch: what moved, decisions, findings both ways)
python3 engine/channels.py       # ch_*   (Meta vs TikTok against App Store money; TikTok ad groups)
python3 engine/holistic.py       # ov_*, mk_*, ct_relay, grid enrichment, extra checks
python3 engine/incident_check.py # incident_check.csv: each incident against store money and Meta ROAS
python3 engine/tickets.py        # tk_*   (ticket queue, at-bat verdicts, strikes, resurrection candidates)
python3 engine/board_export.py   # output/board/*.json (engine documents for the Creative Board)
python3 engine/report.py         # output/board/report_<week>.json (the Tuesday report, drafts included)
python3 engine/make_dashboard.py # output/dashboard/index.html (local dashboard)
python3 engine/brain_sync.py     # brain/ (minds, creatives, experiment results), state/, reports/<week>/
python3 checks/validate.py       # the sensor: contracts, links, append-only history
