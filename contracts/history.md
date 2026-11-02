---
contract: history
version: 1
path: brain/minds/<Mind>/history.md
front_matter: [contract, mind]
entry_header: "## YYYY-MM-DD · <kind> · <who>"
kinds: [seed, belief, decode, experiment, result, new-1, research, inspiration, correction]
append_only: true
written_by:
  belief, decode, experiment, research, inspiration, correction: brainstormer, with the strategist
  seed, new-1, result: engine/brain_sync.py
read_by: [brainstormer, report]
---
# Contract: history (version 1)

The mind's diary: every observation and every change of belief, oldest first, **never edited or deleted**
(the validator fails any change that removes or rewrites an existing line). To fix a mistake, add a
`correction` entry that points at the wrong one.

## Entry
```markdown
## 2026-11-09 · belief · TED + Claude
Changed: "They want a woman who will relocate to them" — confidence high → medium.
Why: EXP-2026-10-19-k4Rm9p (relocation promise) lost in ES and PT (4% of spend in week 1);
the "she chose you" framing in a2Ef3y kept 68% of spend for 22 weeks.
Before: "Relocation is the core fantasy" (high, since 2026-08-03).
```

Kinds:
- `seed` — the file was created (by the engine or the brainstormer).
- `belief` — a row in "What they want, fear and believe" was added, changed or dropped.
- `decode` — why a creative works (or stopped working) for this mind, from a decode session.
- `experiment` — a brief was agreed; its hypothesis about this mind is now under test (link the EXP id).
- `result` — the Monday run read a verdict for an experiment in this mind (provisional week 1, final week 4).
- `new-1` — a new creative became #1 in one of this mind's adsets: how fast, from which share.
- `research` — forum, comment or survey findings, with quotes.
- `inspiration` — a brain dump or reference that shaped thinking.
- `correction` — fixes an earlier entry (quote its header).

Machine entries end with an `<!-- event:... -->` marker so a re-run never writes the same event twice.
