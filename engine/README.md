# Engine: the weekly pipeline

Turns the exports in `data/raw/` into tickets, verdicts, the account dashboard's datasets, the report data
and the facts in `brain/`. Rules: `core/spec.md` §0 (the model), §6 (verdicts), §15 (thresholds), §19 (open
questions). Settings: `engine/settings.py` (measurement eras, the bar per ruler, at-bat and ticket weights).

## The model in one line
creative → adset / ad group → country → App Store / Play money, with each channel's own reporting beside
the chain. Since Singular started feeding Meta (iOS 23 Feb, Android 9 Mar 2026), Meta's share of the
same store money reads about 0.7× what it did: a different ruler, not a weaker business (spec §3.3). Store
money is the one currency for both channels (§3.4).

## Commands (from the repo root)
- Install once: `python3 -m pip install -r requirements.txt`
- Rebuild everything: `bash engine/run_all.sh` (about 40 seconds). Order: `build.py` → `rootcause.py` →
  `creative_relay.py` → `model.py` → `eras.py` → `channels.py` → `holistic.py` → `tickets.py` →
  `board_export.py` → `report.py` → `make_dashboard.py` → `brain_sync.py` → `checks/validate.py`
  (`naming_audit.py` runs right after `build.py`).
- Local dashboard: `python3 -m http.server 8000 -d output`, then open http://localhost:8000/dashboard/

## Export file names
`<prefix>_<YYYY-MM-DD>_<YYYY-MM-DD>.csv` (start and end dates). Prefixes: `adset_`, `ad_`, `country_`,
`tiktok_`, `apple_proceeds_`, `play_`, `singular_`. Exports must start on a Monday. Overlaps are fine: the
newest file wins for overlapping days (`engine/files.py`). Rename files that arrive with other names from
their `Reporting starts`/`Reporting ends` columns. In git the exports are stored compressed: after adding a
file, run `gzip -k -n data/raw/<source>/<file>.csv` and commit the `.csv.gz` (the `.csv` stays local).

## Weekly routine ("run the weekly update")
1. Put the new exports in `data/raw/<source>/` (named as above, starting on a Monday) and compress them.
2. `bash engine/run_all.sh`. If a step fails, fix the code, not the data. The last step is the validator.
3. Read `output/data/checks.csv` and `output/data/naming_audit.md` (+ `naming_audit.csv`): naming errors, code
   typos and collisions, persona and language mismatches, unmapped countries, missing columns. Code fixes the
   creative lead confirms go into `core/code_aliases.csv` (`status: confirmed`); the engine then merges them.
4. Write `output/updates/<today>.md`: money (spend by channel vs App Store proceeds), actions
   (`ov_actions.csv`), adsets and tickets (`tk_queue.csv` above the capacity line, with type, #1 and
   reign, strikes, first J1 candidate), new week-1 reads and week-4 verdicts (`tk_atbats.csv`), new batches
   (draft a one-line hypothesis each, marked *draft*), data checks (`era_compare.csv` rows not "Holds").
5. Sync the ticket board (https://claude.ai/artifact/MFtoxXwScrbATaY5jNhv2U): read the `engine`
   collection with ArtifactData for versions, write `output/board/queue.json`, `prebriefs.json`, `people.json`,
   `codes.json`, `log.json`, `archive.json`, `personas.json` to `engine/<name>` in one batch with `if_version`
   (each document must stay under 256 KB: the ticket stories live in `prebriefs` for that reason); create
   `history/<adset week>` from `output/board/history_<week>.json` (never overwrite an older week).
6. Refresh the account dashboard (https://claude.ai/artifact/QJnA8xeAWjv2D8NVozMp8X): upload each changed
   CSV from `output/data/` as an asset (one call per CSV), point `datasets/<name>` at the new `/_blob/` url;
   if `tools/dashboard/page.html` changed, write it to `files/index.html` as `{text}`.
7. Commit: `engine: weekly update <adset week>` (new `.csv.gz`, `brain/`, `state/`, `core/minds.csv`,
   `reports/<week>/`). Then the report tool makes the PDF.

## Data rules
- **Measurement eras (spec §3.3).** Never compare absolute Meta ROAS, purchases, installs, IPM or
  click → install across a measurement switch. Judge each week on the bar of its own ruler. Relative numbers
  compare an adset with its own OS in the same week. Store money is the check on every era. A new
  measurement change goes into `settings.py`, with a restated bar proposed and logged in `core/decisions.md`;
  apply it only after the creative lead confirms.
- **Channels (spec §3.4).** Never compare Meta's ROAS level with TikTok's. Compare channels only through App
  Store money (`ch_store.csv`) and geo tests. TikTok value counts only on ad-group weeks with $20+ spend.
- **Judging creatives (spec §6.2).** By delivery (week-1 share, became #1 within 4 weeks) and the adset's
  relative ROAS after it took over, never by the creative's own ROAS row. Provisional at week 1, final at
  week 4, late hit in weeks 5–12. Strikes count only in a turnaround (adset under the bar the week before).
- Watch time from counts (3-second plays, ThruPlays, plays at 25–100%), never `Video average play time`.
- Revenue = Purchase ROAS (7-day click) × spend. Only Purchase and Sales objectives are judged on ROAS.
- Weeks run Monday to Sunday. Meta country codes map to App Store storefronts in `model.py` (`OVERRIDE`).
- Persona and language values from `core/naming-adset-v8.md`; legacy names mapped in `build.py` and
  `adparse.py`. For now names use country-style language codes (JP, KR, UA, CH, VN); legacy names read as
  JA, KO, UK, ZH, VI are mapped to those in `brain_sync.py` and `naming_audit.py`.
- Concept codes must be unique ignoring case. Flag collisions; never merge them silently.
- Keep claims honest: App Store proceeds include renewals and organic users; per-dollar figures are
  correlations unless a test says otherwise; Android can't be judged until Play data is in `data/raw/play/`.

## Account context (27 Oct 2026)
- Bar on Singular, set by the creative lead: acceptable from 0.40, refresh warning under 0.40, critical under 0.32.
- 31% of refresh at-bats produce a new #1. A new concept with 3+ variants wins 40% vs 15% with 1–2. A third
  of winners start under 5% of spend in week 1. 16 of 20 v8 adsets switched off got no new concept in their
  last 6 live weeks. Reigns last a median 3 weeks; ROAS slides from week 3.
- The move to worldwide language adsets cut the US from 40% to 20% of English iOS spend; US App Store
  proceeds fell about $12k a week.
- TikTok (13–15% of paid spend): App Store money follows Meta iOS spend ($0.85 per $) and barely TikTok's;
  hold TikTok until a geo test.
- Open: the profit bar, the US test, the TikTok geo test, Google Play and Singular exports, campaign IDs in
  Meta exports (spec §19).
