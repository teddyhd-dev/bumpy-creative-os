# Bumpy ads intelligence

Weekly engine and dashboard for scaling paid ads sustainably: Meta and TikTok spend, creatives,
countries and App Store money in one place. Instructions for the AI agent are in `AGENTS.md`. The full
design is in `docs/bumpy-ads-intelligence-spec.md`.

## First-time setup
1. Install **Python 3.11 or newer** (python.org, or `brew install python` on a Mac).
2. Install your agent, either **Codex** (`npm i -g @openai/codex` or `brew install codex`, then `codex login`) or **Claude Code**.
3. Unzip this folder somewhere permanent, for example `~/Work/bumpy-ads`.
4. Open a terminal in the folder and install the libraries once:
   `python3 -m pip install -r requirements.txt`
5. Build everything: `bash engine/run_all.sh`
6. See the dashboard: `python3 -m http.server 8000 -d output`, then open http://localhost:8000/dashboard/
7. Optional: `git init && git add -A && git commit -m "start"` so every weekly change can be undone.

## Every Monday (and Thursday if you do mid-week checks)
1. Export from Meta Ads Manager (columns are in spec §3.1, **start on a Monday**, 7-day click):
   - Ad sets, Breakdown → By time → Week → `data/raw/adset/adset_<start>_<end>.csv`
   - Ads, same → `data/raw/ad/ad_<start>_<end>.csv`. Include **3-second video plays, ThruPlays and video plays at 25 / 50 / 75 / 95 / 100%**: watch time is computed from these counts. (`Video average play time` is already there but rounded to whole seconds.)
   - Ad sets, Breakdown → By time → Week **and** By delivery → Country → `data/raw/country/country_<start>_<end>.csv`
2. Export TikTok Ads Manager → Ad group report, By week + Country/Region, USD, both OS → `data/raw/tiktok/tiktok_<start>_<end>.csv`
   Export App Store Connect → Proceeds → by territory, daily → `data/raw/apple/apple_proceeds_<start>_<end>.csv`
3. Singular: campaign × country × OS × week (cost, installs, revenue D7 / D30) → `data/raw/singular/singular_<start>_<end>.csv`
   Google Play earnings by country (monthly) → `data/raw/play/`
   Add **campaign name and campaign ID** to the Meta exports, so Meta and Singular can be joined.
4. Open the agent in this folder (`codex` or `claude`) and say: **"run the weekly update"**.
5. Read `output/updates/<date>.md`, the ticket queue (`output/data/tk_queue.csv`) and the dashboard. On Monday the agent also drafts the Tuesday report for the UA meeting (spec §20.7).

Overlapping exports are fine; the newest file wins. Never edit files in `data/raw/`.

If anything changes in how purchases reach Meta (MMP, SDK, attribution setting, tracking link), tell the agent the date the same week: Meta ROAS moves to a new ruler and the bar has to move with it (spec §3.3).

## Folder map
```
AGENTS.md  CLAUDE.md  README.md  requirements.txt
docs/        spec · naming-adset-v8.md · naming-ad-v5.md
data/raw/    adset/ ad/ country/ tiktok/ apple/ play/ singular/   (your exports, untouched)
data/model/  generated
data/log/    at_bats.csv · decisions.md
engine/      run_all.sh + Python steps
output/      data/ (generated) · dashboard/ · updates/
personas/    one folder per persona
```
