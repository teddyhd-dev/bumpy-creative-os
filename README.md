# Bumpy creative OS

The system behind Bumpy's paid creative: which adsets need new creative, what each audience responds to,
every experiment and its result, and the tools the team uses on top. Built so spend can grow week after week
without losing real return.

## The tools
| Tool | For | Where |
|---|---|---|
| **Ticket board** | What to refresh next, how urgent, the clocks (#1 since, last refresh), strikes, the brief covering each ticket | https://claude.ai/artifact/MFtoxXwScrbATaY5jNhv2U · `tools/ticket-board/` |
| **Brainstormer + Brief Maker** | Strategist + Claude turn a ticket into options, then a Notion-ready brief; the hypothesis is logged | Claude or Codex session with this repo · `tools/brainstormer/` |
| **Weekly report (PDF)** | The Tuesday report in the house style | `tools/report/` (generator next) |
| **Account dashboard** | Why the account moves: money vs store, markets, channels, measurement eras | https://claude.ai/artifact/QJnA8xeAWjv2D8NVozMp8X · `tools/dashboard/` |
| **Engine** | The Monday run that feeds all of the above | `engine/` |

## The memory (`brain/`)
- **Minds** (`brain/minds/<Persona>-<LANG>/`): one per persona × language. `mind.md` is the persona clone
  (who they are, beliefs with evidence and confidence, their words, what stops their thumb, inspiration) plus
  live facts; `history.md` is its diary: every decode, belief change, experiment and result, never deleted.
- **Creatives** (`brain/creatives/`): what each winning concept shows in its first second, its hook and
  message, why it works, and where it ran.
- **Experiments** (`brain/experiments/`): one record per brief: hypothesis, prediction, options not chosen,
  the brief, results per adset, lesson.

## As a strategist
1. Ticket board → open a ticket → **Copy for the brainstormer**.
2. Paste it into a brainstorm session (Claude or Codex with this repo): "Let's brainstorm T-691223 …".
3. Answer what it asks (winner snapshots it hasn't seen, inspiration with numbers), pick an option, give
   your direction, approve the brief. It saves everything and commits.
4. Paste the brief into Notion and add references. Results arrive on the experiment every Monday.

## As a designer
Work from the Notion brief and use the generated v5 file names exactly: that is how results find you.

## Every Monday
"Run the weekly update" in a session with this repo: see `engine/README.md`.

## For agents and builders
Start at `AGENTS.md` (the map) and `ARCHITECTURE.md` (how the pieces fit, how to tune a tool, how to change
the shared foundation without breaking the others). `CHECKPOINT.md` describes the 29 Oct state (tag
`checkpoint-2026-10-29`).
