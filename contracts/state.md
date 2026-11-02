---
contract: state
version: 1
path: state/queue.json, state/week.json
written_by: engine/brain_sync.py, every Monday (overwritten; history is in git)
read_by: [brainstormer, ticket-board, report]
queue_ticket_fields: [id, rank, type, mind, adset, adset_id, os, why, spend, roas, top_code, top_name, reign, reign_since, last_refresh, strikes, past_no1, j1, brief]
---
# Contract: state (version 1)

This week's working state, rewritten by the Monday run. It is what the brainstormer reads when a
strategist says "let's brainstorm T-691223", and what the ticket board shows.

- `state/week.json`: the weeks covered (adsets, ads, store), the bar, capacity, counts.
- `state/queue.json`: `{"week": ..., "tickets": [...]}` with one entry per open ticket. `mind` links the
  ticket to `brain/minds/<mind>/`; `top_code` and `past_no1[].code` link to `brain/creatives/`; `j1` lists
  proven concepts from nearby minds that never ran here; `brief` is the latest experiment covering the
  ticket (`{id, strategist, date, status}`) or null.

Never edit these files by hand: change the engine.
