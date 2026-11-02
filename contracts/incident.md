---
contract: incident
version: 1
path: core/incidents.csv
fields: [id, start, end, effect_until, os, kind, what, source, logged_by, logged_at]
kinds: [tracking, release-bug, store, payments, unknown]
written_by: "anyone, through any session (log an incident …), or the creative lead on GitHub"
read_by: [engine, brainstormer, report, ticket-board]
---
# Contract: incident (version 1)

An app or tracking problem that made results worse for reasons that have nothing to do with the creative:
broken tracking or Singular/Meta signal, a release with a bug, a store or payment outage. One row per
incident, never deleted (add to `what` or fix dates if you learn more, and say so in the commit).

| Field | Meaning |
|---|---|
| `id` | `INC-<start date>`, add `-b` for a second one on the same day |
| `start`, `end` | first and last day the problem itself was live (YYYY-MM-DD) |
| `effect_until` | last day results were still hurt (Meta relearns after a signal break); blank = assumed to the end of that week |
| `os` | `all`, `iOS` or `Android` |
| `kind` | `tracking` (what Meta / TikTok saw was wrong; store money fine), `release-bug` (users hit a bug; store money hurt too), `store`, `payments`, `unknown` |
| `what` | one line: what broke and what it did |
| `source`, `logged_by`, `logged_at` | who knew, who logged it (team code), when |

**What the engine does with an incident week** (any day of the Mon–Sun week inside `start`…`effect_until`,
for that OS):
- a refresh that **landed** that week and missed is **Void**, not a strike or a foul (a hit still counts);
- a week under the bar during an incident isn't counted toward "weeks under the bar" or Fading (a week
  above the bar still counts as healthy);
- the ticket's story marks the week ⚠ and names the incident; the brainstormer doesn't read those weeks as
  the persona's reaction; the report mentions it; `new-1` events that week are marked "read with care".
