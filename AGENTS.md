# Bumpy creative OS: map for agents

Bumpy is an international dating app. This repo turns weekly ad and store exports into tickets, a shared
memory of every audience ("minds") and every experiment, and the tools the team uses on top. Keep this
file short: it points to where things are. Read only what your task needs.

## Where things are
| Folder | What | Who writes |
|---|---|---|
| `core/` | The foundation every tool reads: `spec.md` (rules, the 0.40 bar, verdicts), `brand.md` (brand rules), `naming-adset-v8.md` (personas), `naming-ad-v5.md`, `team.csv`, `angles.csv`, `minds.csv` (registry of minds), `concepts.csv` (every concept code and its name), `code_aliases.csv` / `persona_aliases.csv` (confirmed fixes), `incidents.csv` (app/tracking incidents), `decisions.md` | the creative lead (changes reviewed); the engine adds new rows to `minds.csv` and `concepts.csv` (from ad names); the brainstormer adds a new code to `concepts.csv` when a brief is approved |
| `contracts/` | The formats tools share (mind, history, creative, experiment, state). Front matter = the rules `checks/validate.py` enforces | the creative lead (changes reviewed) |
| `brain/minds/<Persona>-<LANG>/` | The persona clone: `mind.md` (current understanding + facts block) and `history.md` (append-only diary) | brainstormer + engine |
| `brain/creatives/` | One file per concept: decode (first second, hook, message, why) + where it ran; snapshots in `img/` | brainstormer + engine |
| `brain/experiments/` | `EXP-<date>-<code>.md`: hypothesis log, one per brief; `detected-refreshes.csv` | brainstormer + engine |
| `state/` | This week's tickets (`queue.json`) and week facts | engine |
| `data/raw/` | Every export, compressed, never edited or deleted | the team drops files |
| `engine/` | The weekly pipeline (`bash engine/run_all.sh`) | engine work sessions |
| `tools/<tool>/` | Each tool's own instructions and files: `brainstormer/`, `ticket-board/`, `report/`, `dashboard/` | that tool's sessions |
| `reports/<week>/` | Report data and PDFs | engine + report tool |
| `archive/` | Snapshots of earlier versions | nobody (read only) |

## Tasks → what to read
- **Brainstorm, decode a signal, audit a persona or write a brief** ("let's brainstorm T-…"): `tools/brainstormer/SKILL.md`. Work on a branch; finish with a pull request, never a push to `main`. People: `tools/brainstormer/SOP.md`.
- **Weekly update** ("run the weekly update"): `engine/README.md`.
- **Work on one tool**: that tool's folder only, plus `contracts/` for anything it reads or writes.
- **Change a rule, a threshold or a shared format**: `ARCHITECTURE.md` → "Changing the foundation".
- **Log an app or tracking incident** ("tracking broke on…", "the release on … had a bug"): add a row to `core/incidents.csv` per `contracts/incident.md`, run `python3 checks/validate.py`, commit as `core: incident …`.

## Golden rules
1. The conversation is not the record. Anything learned goes into `brain/` (and `core/decisions.md` for decisions).
2. Write only what your tool owns (see each contract's `written_by`). Never edit inside `<!-- generated -->` blocks; never edit an existing line of a `history.md`.
3. Never edit, move or delete anything in `data/raw/`. Don't upload data anywhere outside this repo; no credentials in the repo.
4. Don't change thresholds, the bar or ROAS zones without the creative lead; log decisions in `core/decisions.md` and the spec changelog.
5. Never compare Meta ROAS across the Singular switch (iOS 23 Feb, Android 9 Mar 2026) or Meta's ROAS with TikTok's (`core/spec.md` §3.3–3.4). Judge creatives by delivery (week-1 share, became #1) and the adset's relative ROAS, never by their own ROAS row.
6. New concept codes and ad names go through `python3 checks/new_concept.py` before they reach a brief. Before committing: `python3 checks/validate.py` must pass. Commit messages say which tool: `brainstorm: …`, `engine: …`, `report: …`, `core: …`.
7. Strategists' sessions never push to `main`: they open a pull request and the creative lead merges. Shared lists (personas, team, angles, naming, brand) live only in `core/`; tools point to them, never copy them.
