# Launch review deck ("what we launched last week, and how it's going")

version: 1.1.0 (3 Nov 2026: row sorting, an action slide after every results slide; first run: Batch 40, `reports/2026-10-26/`)
Presented at the Tuesday UA meeting. Built as a Claude Slides artifact; the creative lead adds verdicts and
action items on top. Rules behind it: `core/spec.md` §6.2b (refresh read), §15 (bar).

## How to make it
1. Weekly update first (`engine/README.md`). The ad export must include **daily** rows (Day breakdown) for
   the review weeks: upload days and before / after are measured in days.
2. Ask (or read from the ad names) which batch is the refresh and which batches are pass-through (creator
   content, e.g. Batch 44). Only the refresh batch is judged.
3. `python3 tools/report/refresh_review.py --batch Batch2026WeekNN --creator Batch2026WeekMM --end <Sunday>`
   → `reports/<week>/refresh_review.json`: every adset the batch landed in, the read, the #1 before and after
   and its reign, action priorities, and Account news.
4. Build the deck from that file (Slides artifact type; the last deck's slide HTML is in
   `reports/2026-10-26/deck/` to copy the look). Check every number on the slides against the JSON.

## Structure: one talking point per slide, the headline is the sentence you say
Every results slide is followed by its own **action slide**, so the actions stay in context.
| # | Slide | Content |
|---|---|---|
| 1 | Cover | "What we launched last week, and how it's going" · week · batch |
| 2 | What we made | Big count ("69 new files, 4 concepts, 17 adsets"); one tile per concept: videos / images → persona × languages (adset count), upload day; sky tile = new concept, orange = new variants of a running concept. Footer: who briefed / designed; pass-through batches named, not counted |
| 3 | How to read | The two rules: ROAS colours and the refresh verdict (below), the NEW / NEW-OLD tags, yellow "#1 under 2 weeks" |
| 4 | Wave 1 results (one slide per upload day group) | One row per adset: ad set · 8-week ROAS sparkline (shaded under 0.40, dot on the upload week coloured by zone) · Before · After (+ ▲/▼) · "New creative in top 3?" (Yes · #rank, or No · #rank (old <name>)) · Verdict. Headline counts the verdicts |
| 5 | Wave 1 actions | Per-adset actions for that wave (creative briefs and media-buyer moves) |
| 6–7 | Wave 2 results + actions | same |
| next pairs | "<Persona> Refresh: <Concept>" + its actions | Results: Before · After · New top spender? · Batch share · Current #1 spender (NEW / NEW-OLD pill) · #1 for (yellow pill under 2 weeks); NEW rows tinted blue, NEW-OLD peach. Actions: what to do with the concept: keep / iterate where it won spend, stop variants where it didn't, a draft hypothesis, code fixes |
| next | Section 2 divider: Account news | |
| next | Account news + its actions | Adsets **outside** the refresh with $1.5k+ a week whose #1 changed or got a top-3 riser (+10 pts, 15%+ share), top 10 by spend: ad set · Before · After · change · previous winner (weeks) · new winner (NEW #1 / TOP 3 pill, share before → after). Actions: budgets to hold, winners to decode |

**Row order.** Results slides (waves and refreshes): first the adsets where the new creative made it (top 3 on wave
slides, new #1 on refresh slides), then the rest; inside each group, ROAS after from high to low. Account news:
ROAS after from high to low, ties by the biggest improvement (use the change between the rounded numbers shown).

**Action slides** all use one table: Priority pill · Ad sets · Owner (Creative / Media buyer / Creative lead pill) ·
Spend/wk · Action (one sentence, the number that justifies it inside). Priority numbers run across the whole deck
(1 · Urgent, 2 · High …) so the ranking survives being split; other pills: Watch (yellow), Leave / Stop (grey),
Opportunity (blue), Learn (light blue), Next batch / Check (sand). 4–6 rows per slide. Wave action slides are about
adsets; refresh action slides are about the concept, so the same adset can appear on both with different actions.

## Rules on the slides
**ROAS colour (pill):** 0.40+ blue `#53AFD4` "OK" · 0.32–0.39 peach `#FDD3C2` "needs refresh" · under 0.32 red
`#D9442B` "critical". Colour by the number shown (rounded to 2 decimals). ▲ blue `#1F6F94` / ▼ red / – grey when
the change is under 0.02.

**Refresh verdict (spec §6.2b):** first, did the new creative reach the top 3 spenders?
- ✓ **Worked** (dark blue `#1F7FA8`): yes, ROAS up and now 0.40+
- ↗ **Almost** (light blue `#D6EEF8`): yes, ROAS up but still under 0.40
- = **Flat** (sand `#E9E3D3`): yes, ROAS didn't move
- ✗ **Worse** (red): yes, ROAS down
- **Miss** (grey `#E2DFE1`): no; old creatives kept the spend. (Miss at 0.40+ = leave it.)

**Tags:** NEW = the batch's creative is now #1 (blue pill) · NEW-OLD = an older creative just became #1 (peach
pill) · `#1 for` under 2 weeks = yellow `#FFE9A8` pill (not proven yet).

**Action priority:** weekly spend × read weight: Worse 1.0 · Miss under 0.40 0.8 · Almost / Flat 0.6 ·
Worked and Miss (left) = leave. Pair same persona × language across OS into one brief. Media-buyer items:
critical adsets the batch is carrying (pause / check setup), creator or test ads that took spend while ROAS
crashed, falling adsets to hold, 0.50+ adsets with a stable #1 for a small budget test.

## Words and design
- Audience names, never codes: Friends (International Friend Finder), Loc. Dating (Local Dating Fatigue),
  Gringo (Gringo Lover), Passport Bro, Slavic Lover, Chat Only…; concepts by name (dreamlife, banner).
- House style (`STYLE.md`): Quicksand Bold headlines, Open Sans body, background `#F7F6F3`, plum `#443A40` for
  section dividers. Text 24px minimum, rows 26–30px. Footer (24px, grey) carries the windows, abbreviations and
  the incident note; speaker notes carry the 2–3 sentences to say.
- Always say how many days of data a wave has; mark iOS windows that include an incident (`core/incidents.csv`).
- Leave verdict / action columns for the creative lead to edit; don't add a "your verdict" column.

## Known gaps (2 Nov 2026)
- The engine's weekly at-bats count only concepts new to an adset; `refresh_review.py` judges new variants of a
  running concept as well. Code reuse (h7km3n for internationalfriends) is split out by concept name here.
- Account news compares Mon–Sun weeks; a week with an incident reads low on iOS.
