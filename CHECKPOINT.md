# Checkpoint · 29 Oct 2026 · "v1: ticket board + report + dashboard"

The state of the Bumpy ads system before it is split into separate tools (ticket board, brainstormer and
brief maker, persona library, hypothesis log, PDF report). Everything here can be restored from this folder.

## What exists
| Piece | Where | Version at this checkpoint |
|---|---|---|
| Rulebook | `docs/bumpy-ads-intelligence-spec.md` (also in the Claude project "Bumpy Reporting") | 1.2.4 |
| Engine | `engine/` (`bash engine/run_all.sh`) | builds tickets, at-bats, verdicts, scorecards, report data |
| Creative Board (tickets, board, report, people, signals, personas, log, guide) | https://claude.ai/artifact/MFtoxXwScrbATaY5jNhv2U · source `output/board/board.html` | page version 9 |
| Board database snapshot | `checkpoints/2026-10-29/board-db/` (signals, history, reports, engine docs) | work, manual, team, report_notes were empty |
| Account dashboard (command grid) | https://claude.ai/artifact/QJnA8xeAWjv2D8NVozMp8X · source `output/dashboard/page.html` | page doc version 9 |
| Decisions | `data/log/decisions.md` (also in the project) | bar 0.40 / 0.32; one concept + 3+ variants |
| Raw exports | `data/raw/` (not in git: 230 MB; kept in the zip and the permanent folder) | Meta adset/ad/country to 12 Oct, TikTok to 18 Oct, App Store to 5 Oct |

## Restore
1. `python3 -m pip install -r requirements.txt` and put the raw exports back in `data/raw/`.
2. `bash engine/run_all.sh` rebuilds every dataset and `output/board/*.json`.
3. Republish `output/board/board.html` (capabilities: db rules engine/history/reports read view write admin; user profile; sample) and write the engine docs per `AGENTS.md` step 6, or restore them from `checkpoints/`.

## What changes next (29 Oct)
The board keeps the ticket system only. Briefs stay in Notion for now; the report becomes a weekly PDF;
signals, persona knowledge and the logs move next to a Brainstormer + Brief Maker. See the plan in the conversation of 29 Oct.
