---
contract: mind
version: 1
path: brain/minds/<Mind>/mind.md
id_format: "<Persona>-<LANG>, e.g. LatinaFemaleLover-ES (persona and language values from core/naming-adset-v8.md)"
front_matter: [contract, mind, persona, language, status, updated]
sections:
  - Who they are
  - What they want, fear and believe
  - Their words
  - What stops their thumb
  - Messages that land and messages that tire
  - Open questions
  - Inspiration bank
generated_blocks: [facts]
written_by:
  sections: brainstormer, with the strategist (every change also gets a history.md entry)
  facts block: engine/brain_sync.py, every Monday
  status: engine/brain_sync.py
read_by: [brainstormer, report, ticket-board]
---
# Contract: mind (version 1)

One audience = one mind = **persona × language** (both OS together; iOS and Android agree 80% of the
time, languages disagree 42% of the time). It is the "brain clone": what we currently believe about how
this audience thinks, feels and reacts. Adsets come and go; the mind stays.

**Latest on top, nothing lost.** `mind.md` always holds the current understanding. Every change to it is
written to `history.md` first (old → new, why, evidence), so the past is never deleted. Git keeps every
version of both files as well.

## Rules
- Front matter `contract: mind/1`. `updated` = the date anything outside the facts block last changed.
- Each belief in "What they want, fear and believe" is a table row: belief · confidence (low / medium /
  high) · evidence (EXP ids, creative codes, quotes) · since (date). Change a row only together with a
  `belief` entry in history.md.
- "Their words" holds verbatim quotes with source and date, in the original language plus an English gloss.
- The facts block sits between `<!-- generated:start facts -->` and `<!-- generated:end facts -->`.
  Nobody edits inside it: the Monday run rewrites it.
- A new mind is created from this template the first time a brainstorm needs it (or by the Monday run
  when an adset for it goes live) and registered in `core/minds.csv`.

## Template
```markdown
---
contract: mind/1
mind: LatinaFemaleLover-ES
persona: LatinaFemaleLover
language: ES
status: live
updated: 2026-11-02
---
# LatinaFemaleLover · ES

## Who they are
## What they want, fear and believe
| Belief | Confidence | Evidence | Since |
|---|---|---|---|
## Their words
## What stops their thumb
## Messages that land and messages that tire
## Open questions
## Inspiration bank
<!-- generated:start facts -->
<!-- generated:end facts -->
```
