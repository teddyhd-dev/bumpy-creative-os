# Mistakes log (Claude's)

Every time Claude gets something wrong, apologises ("that's on me", "sorry", "you're right"), or the creative lead
has to correct the work, it goes here: what happened, **why** it happened (the root cause, not the symptom), the
rule that stops it, and how that rule is checked. Newest first.

**Every session reads this file before starting work** (AGENTS.md says so) and checks its output against the rules
below before calling a task done. Adding an entry is part of fixing the mistake; it is not optional.

## The rules (the short list to check against)
1. **A presented deck is a record. Never edit it.** New rules apply from now on. Each Tuesday's deck is about
   **last week's batch** (the one that went live Mon–Sun before the meeting). Before building, write down in one
   line: the week, the batch, its first live day, read from the ad names.
2. **Every table row names the creative that landed there.** Never let a slide title stand in for the rows: a
   persona can get different concepts per language.
3. **When feedback changes a rule, ask where it applies.** Ask: this week's deck only, the system from now on, or
   past records too? The default is the system from now on, plus this week's deliverable. Past records stay.
4. **One source of truth per number.** If two tools compute the same thing (e.g. the read), make one feed the
   other before showing either.
5. **Check before numbering or naming anything shared** (spec versions, concept codes): read the latest file first.
6. **Before saying done, re-read the user's message and tick each ask.** Then check the slide against the data
   behind it (each row's concept, rank, share, before/after) and render it.

## Entries

### 2026-11-09 · The Local Dating slide implied iOS ES got colosseum
- **What happened:** the slide was titled "Local Dating Fatigue Refresh: Colosseum 50/50" and its rows did not say
  which creative each adset got. iOS ES and Android ES got talkinghead variants, not colosseum. The creative lead
  had to ask.
- **Why:** the persona slide template was built for one concept per persona (as in Batch 40). Batch 41 gave
  Local Dating two concepts split by language, and the template had nowhere to show that. I checked the numbers on
  each row but not "which creative is this row about".
- **Rule:** 2. **Check:** `tools/report/build_deck.py` now prints the creative on every row (persona and creator
  slides). The title names every concept, with its language when they differ.

### 2026-11-09 · Edited last week's (already presented) deck instead of reporting this week's batch
- **What happened:** after the creative lead said "for Gringo PH, yes, call it Watch", I edited the Week 44 deck,
  which had already been presented. That meant four slides (verdict, scoreboard, rules, creator). The real job for the next
  Tuesday was the Batch 41 launch review (live 4–6 Nov). The creative lead had to point out that Batch 41 existed.
- **Why (root cause):**
  1. I read "call it Watch" as "change the artifact we last worked on". I didn't read it as a rule for the system
     from now on.
  2. A week earlier the creative lead had said "apply everywhere" for the 80% rule. I carried that over without
     asking whether it covered past records.
  3. I never stated which week and which batch the next deck is about. The ad export already showed Batch 41 as
     new, and I didn't look.
  4. Nothing said a presented deck is frozen, so editing it felt like "keeping things consistent".
- **Rules:** 1 and 3. **Check:** `tools/report/REFRESH-REVIEW.md` → "How to make it" starts with the week/batch line.
  This file is read at the start of every session.

### 2026-11-09 · Board and deck gave different reads for the same adset
- **What happened:** caught before the creative lead saw it. The board's launch log showed the engine's
  whole-week read. The deck showed the launch review's read from the upload day. A few adsets disagreed
  (e.g. Latina iOS PT).
- **Why:** two tools computed the same read in two ways, and I built the new view on one without comparing.
- **Rule:** 4. **Check:** where a launch review exists, the engine now uses its read (`review_reads()` in
  `engine/tickets.py`, spec 1.3.6).

### 2026-11-03 · Spec version clash (1.3.4 used twice)
- **What happened:** I numbered my 80% rule spec 1.3.4. The strategists' merge had already used it, so I had to renumber it
  1.3.5.
- **Why:** I numbered from memory instead of reading the latest `core/spec.md` changelog first.
- **Rule:** 5.

### 2026-11-02 / 03 · Launch-review deck corrections (style and meaning)
Corrections the creative lead had to make on the first launch-review deck. All are now in
`tools/report/STYLE.md` ("How the creative lead wants decks presented") and `REFRESH-REVIEW.md`:
- Too wordy: one talking point per slide. Wave slides were confusing: persona slides only.
- "Worked" was shown while ROAS was still under 0.40, which was misleading. Added **Almost**. A #3 at 2% counted as "in the top 3": added the
  80% rule.
- "Top spender?" was ambiguous: now "New in top 3?" and "Current #1 spender". Codes (IFF, LDF) instead of
  audience names: names only.
- Action items were split by OS for creative and not sorted by owner. Now there is one creative row per persona ×
  language, Creative first, then Media buyer, with research rows where the cause is unclear.
- Creator content mixed into the refresh section: it now has its own section.
- **Why, in common:** I designed for completeness (show everything the data has) instead of for the person
  presenting (one point, plain words, a verdict that means what it says).
