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
7. **Action items are contextual or they are not done.** Each creative row says: who leads the adset and for how
   long, what that creative shows and says and why it stops the thumb (from its decode in `brain/creatives/`), what
   we learn from it, and which jurus we use (J1 copy a winner from a sibling adset or language, J2 a past winner in a new
   form, same message with a new visual, new angle…). If the winner isn't decoded, **ask the creative lead for
   screenshots or the video before writing the action, and where the idea came from** (a reference ad, a competitor,
   a trend, a creator, our own brief), so patterns in what inspires winners show up. Store both in
   `brain/creatives/<code>-<name>.md`.
8. **The headline is a summary of the rows.** Every action named in an action slide's headline is a row on it.
9. **An action item says WHAT to make.** One line: the jurus (one of the six in `tools/brainstormer/playbook.md`) +
   the message + the visual + the format + the languages, with one piece of evidence. "Decode", "research", "learn",
   "new concept, 3+ variants" are homework, not actions: Claude does the homework before the deck (persona deep
   dive, winner decodes, the data) and asks the creative lead only for what the data can't show.
10. **Never show a ROAS move without its why.** For every adset that moved: was it the creative (who took the spend,
   and do its installers buy?), the audience (country mix), or media buying (budget, ads switched off)? This goes on
   the ticket, the launch log and the deck, not only the slide.
11. **Every word on a slide must earn its place.** A row that repeats the table before it, a number that doesn't
   change the decision, a label the room already knows: cut it.
12. **Fix the class, not the instance.** When a correction lands on one slide, sweep every slide (and the tools behind
   them) for the same flaw before replying, and say what else changed.
13. **"Took spend while ROAS fell" is not a cause.** Before blaming, pausing or keeping a creative, read its why
   (`why` in `refresh_review.json`): did its own ROAS fall, was the old #1 switched off, did the budget move?
14. **Lists that order work are computed, never typed.** The refresh order comes from the reads (worse → missed →
   flat → almost, spend inside), and every list says what it left out and why.
15. **A persona that keeps failing gets asked why it exists.** 3 strikes, or under the account for 2+ months: the
   deck shows its history, where it still works and the decisions for the creative lead.
16. **Compare like with like before naming where something breaks.** Video against video, image against image, same
   OS and days; and check the account-wide rate for the same days first (did everything move, or only this ad?).
   Then recompute the key numbers from the raw export before they go on a slide.
17. **After an interrupted turn, look before you touch.** `git status` and read every changed file first: work from
   the interrupted turn is on disk even when it isn't in the conversation.

## Entries

### 2026-11-10 (3) · "Five break at the store page" was a blended number; and I overwrote my own interrupted work
- **What happened:** the first funnel slide said five Worse/Miss sets "got the click but lost the install" and pointed
  at the store page. The creative lead asked whether the numbers were right. The arithmetic was right (recomputed
  from the raw export: 9 of 11 rows match to 0.1 point; the other 2 are "not tested" by design), but the comparison
  was wrong: it set each batch (videos and images together) against all the other ads. Like with like, video
  against video, no set breaks at the store page, and the account's C>I held at 33–38% on Android every day since
  1 Oct. What dragged C>I down was the batch's **iOS image** versions: 5% CTR and 1–2 installs per 100 clicks, with
  normal sales per impression (inflated clicks, not lost installs). The creator section also said "16 creator ads";
  it is 18 ads, 11 videos, 12 adsets. Separately: the turn was interrupted after much of this had been rebuilt
  (images check, funnel actions, creator funnel). Restarting, I edited `engine/why.py` without checking what was on
  disk and deleted those functions; I recovered them from the session log.
- **Why (root cause):**
  1. I named a cause ("store page") from one blended rate without splitting by format or checking whether the whole
     account moved. Images and videos have different funnels by nature (images: more clicks, fewer installs per click).
  2. I trusted counts carried over from an earlier slide instead of recounting.
  3. I assumed the files matched my context after an interruption.
- **Rules:** 16, 17. **Check:** `funnel_check()` compares video with video and image with image, payers against every
  other ad; `image_check()` puts the account-wide format split in `refresh_review.json`; the funnel slide's footer
  states the account-wide C>I for the same days.

### 2026-11-10 (2) · Fixed three slides, not the deck; two "pause" actions blamed the wrong creative
- **What happened:** after the creative lead's questions on Passport Bro, dancing and Mature, I fixed those three
  slides and stopped. The creative lead asked whether the fixes were logged and applied to the rest. They weren't:
  Loc. Dating still had a "Research: why does colosseum split by OS" row, Friends CH a "research" row, Gringo EN
  "new concept", the creator slide "decode it", account news "decode manyplaces" and "check them". Running the why on
  every row then showed two actions were wrong: **Latina PT "pause dancing"** (its #1 banner video had been switched
  off on 2 Nov, the day before dancing landed, and dancing did as well as that ad) and **Loc. Dating ES iOS "pause the
  creator talkinghead"** (the creator ad was the best thing there, 0.62; datingcontest fell). The refresh list was
  typed by hand in spend order, missed Gringo EN, and wasn't ordered by how bad. For Passport Bro Android I answered
  with week-on-week numbers while the slide used the review window (two numbers for one move). The Latina footer said
  "Android EN and PT" (PT is iOS); I caught that one. And nobody had asked why Latina exists until the creative lead did.
- **Why (root cause):**
  1. I treat a correction as a ticket about that slide, not as a symptom of how I built all of them.
  2. "Took spend while ROAS fell" read like a cause, so I blamed the creative that took spend. I never asked whether
     its own ROAS fell or whether someone switched something off. The exports show both; I had no step that looked.
  3. Ordered lists were written by hand, so they followed whatever order I happened to think in.
  4. The deck reviews batches, never a persona's health over months, so a persona can fail for weeks without the
     question "should it be here?".
- **Rules:** 12, 13, 14, 15. **Check:** `engine/why.py` puts a why on every launch-review and account-news row
  (spec §6.2c), and the board's launch log shows it; `build_deck.py` warns on homework words in any row and numbers the
  refresh list itself (`refresh_plan()`); `REFRESH-REVIEW.md` → "Refresh order".

### 2026-11-10 · Action items still weren't actions; the deck shows what happened but not why
- **What happened:** after the first rework, the creative lead still found the action slides weak and cluttered.
  Latina said "New concept, one set for both OS. Dancing is #1 at 76–78% but ROAS sits at 0.27–0.31": an observation
  with no instruction. Passport Bro said "decode datingcontest": homework handed back to the team. Friends repeated
  the result table. Account news showed 7 new #1s without saying why some adsets got better and others worse.
- **Why (root cause):**
  1. The system knows numbers, not creatives or people. 1 of 100 creatives is decoded, the Passport Bro mind is a
     copy of the Notion card, and no experiment is logged. So I can't say what to make, and I filled the row with
     "decode" and "research" instead of doing that work myself first.
  2. I used only two or three of the six jurus, and never checked history to see which jurus has worked for that
     persona (e.g. tweetoverlay's three visuals each reached 43–44% of Friends EN: "new visual" is proven there).
  3. The engine has no "why" step. It reads rank, share and ROAS before/after, but never asks whether a creative
     brings buyers (hook → click → install → purchase), or whether budget or paused ads moved the adset. The data
     for most of this is already in the exports (e.g. dancing has the best hook rate in Latina EN, but its
     installers buy about half as often as banner's or wanted's).
  4. I treated the slide as a place to show evidence instead of a place to give decisions.
- **Rules:** 9, 10, 11.

### 2026-11-09 · Action items were generic: no lesson from the incumbent, no jurus, headline not in the rows
- **What happened:** the Week 45 action slides said "new concept, 3+ variants" almost everywhere. They didn't say what
  the long-running #1s (datingcontest 5–7 weeks, tweetoverlay 12 weeks, banner 16 weeks) teach us, or what emotion
  or visual carries them. They missed the obvious jurus: copy colosseum (worked on Loc. Dating iOS EN) into Spanish,
  the same move that made datingcontest #1 in ES. On the Local Dating slide, the headline ("pull colosseum from
  Android, find out why it splits") didn't match the order of the rows, so the creative lead didn't find it.
- **Why (root cause):**
  1. I wrote actions from numbers only. Only 1 of our 100 creative files is decoded, so I had no idea what any winner
     looks like or says, and I didn't ask. I wrote around the gap instead of naming it.
  2. I didn't use the jurus playbook (`tools/brainstormer/playbook.md`) or the J1 and past-#1 lists the engine already
     puts on every ticket. That knowledge was in the repo and I skipped it.
  3. I wrote the headline and the rows separately and never checked one against the other.
- **Rules:** 7 and 8. **Check:** `tools/report/REFRESH-REVIEW.md` → "Action items" lists what every creative row must
  hold; `build_deck.py` warns when a creative row names no incumbent or move.

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
