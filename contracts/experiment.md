---
contract: experiment
version: 1
path: brain/experiments/EXP-<YYYY-MM-DD>-<code>.md
id_format: "EXP-<date the brief was agreed>-<concept code>"
front_matter: [contract, id, date, strategist, tickets, minds, concept_code, concept_name, move, status, made_with]
moves: [same-message-new-visual, same-message-new-format, same-visual-new-angle, new-angle, proven-elsewhere, past-winner-new-form]
statuses: [briefed, live, week-1, final]
sections: [Hypothesis, Prediction, Evidence, Options not chosen, Inspiration used, Brief, Lesson]
generated_blocks: [results]
written_by:
  everything except results and status: brainstormer, with the strategist, when the brief is agreed
  core/concepts.csv row for a new code: brainstormer, when the brief is approved (checks/new_concept.py first)
  designer: brainstormer or the strategist, when known
  results block and status: engine/brain_sync.py, every Monday
  Lesson: strategist + designer at the retro (the brainstormer can write it for them)
read_by: [brainstormer, report, ticket-board, scorecards]
---
# Contract: experiment (version 1)

One file per agreed brief. This is the **hypothesis log**: what we tried, why, what we predicted, what
happened, and what it taught us. A brief can cover several tickets, adsets and minds; each adset still
gets its own result row.

- `move` is one of the playbook moves (tools/brainstormer/playbook.md). It lets us learn which kind of
  refresh works for which mind.
- `concept_code` is picked with `python3 checks/new_concept.py new` and checked with `... check`; a new code
  is added to `core/concepts.csv` (code, name, confirmed, date, EXP id) when the brief is approved. The
  validator fails a record whose code isn't registered, whose name differs from the registry, or whose ad
  names in the Brief break core/naming-ad-v5.md (same checks as `... names`).
- `Prediction` must be checkable from the exports: e.g. "takes 20%+ of spend in week 1 in at least 2 of
  the 3 adsets, and SlavicFemaleLover · iOS · EN is back at 0.40+ by week 4".
- `Options not chosen` keeps the other options with their hypotheses, for the next round.
- `Brief` is the exact text pasted into Notion (the strategist may add references there).
- The Monday run finds the ads by concept code (and the generated v5 names), fills the results block,
  moves `status` along (briefed → live → week-1 → final) and writes a `result` entry into each mind's
  history. The ticket board shows the brief on each covered ticket.

Refreshes before this log existed (detected from the exports, no hypothesis recorded) are in
`brain/experiments/detected-refreshes.csv`, regenerated every Monday.
