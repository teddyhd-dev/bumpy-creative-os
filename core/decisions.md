# Decisions log

One entry per decision: date, decision, who decided, evidence, how we'll know it worked.
Log every measurement change (MMP, SDK, attribution setting, conversion mapping, tracking link) here the week it happens.

## Made

### 2026-11-02 · More naming decisions; briefs can't create clashes
- **Decided by:** creative lead.
- **Concepts:** `i48opT` = carousel, `d4osYW` = dancing (scene names go in the hook field); `j4g89om` is `4g89om` (iconicplaces).
- **Personas:** new `AttractiveBlackFemale`, `SexyFemaleLover`, `SexyMaleLover` (was written SexyBeachGuy), `Translation` (wants to date abroad but worries about the language barrier). Past personas: `PlusSizeWomen`, `MiddleEasternMaleLover` (was written MiddleEastern), `Divorcee`, `InterlocalDating` (another city or island), `ShortKings`. `InstagramPost` and `BrandTest` are tests, not personas: no mind, not flagged. Naming v8.2.0; spellings in `core/persona_aliases.csv`.
- **Guard at brief time:** the brief maker picks new codes with `checks/new_concept.py` (unique ignoring letter case, never one character from an existing code), checks the concept name against `core/concepts.csv`, and checks every ad name; the validator repeats it on every experiment record.

### 2026-11-02 · Code fixes, concept names and personas (naming audit)
- **Decided by:** creative lead.
- **Codes:** `n62Wt` is `n6f2Wt` (banner); `a2Ef3Y` is `a2Ef3y` (letter case); the *wanted* ads coded `h7km3n` or `H7kM3N` are the wanted concept `a2Ef3y` (`H7kM3N` stays *airport*). By the same rule (letter case is not a new concept) `H7kM3n`, `c0kM3N`, `k4rm9p`, `P8c7ao` merge into `H7kM3N`, `C0kM3N`, `k4Rm9p`, `p8C7aO`. Kept in `core/code_aliases.csv`; the engine merges confirmed rows. `j4g89om` → `4g89om` still to confirm.
- **Concept names:** `vh1kle` = vehicle (the other names are scenes), `v07e5T` = lovestory and `L2vM8Q` = manyhugs (*indianboydream* and *slavic* are persona names written in the wrong field). One home for concept names: `core/concepts.csv`.
- **Personas:** Friends / IntlFriendFinder / InternationalFriend = `InternationalFriendFinder`; GringoLover = GringoMaleLover; Chinese = AsianFemaleLover; LatinaLover = LatinaFemaleLover; 304050 = MatureDating; AngryWithLocalDating = ChurnLocal = LocalDatingFatigue. New canonical personas: AsianMaleLover, SoutheastAsianFemaleLover, LatinoMaleLover, ChatOnly (naming v8.1.0).
- **Creative moved to another persona** (e.g. the k4Rm9p LocalDatingFatigue ads put into PassportBro by the media buyer when PassportBro iOS was spending a lot at low ROAS): fine as a move, but the copy gets the adset's persona in its file name, same concept code.

### 2026-11-02 · Language codes: country-style for now
- **Decided by:** creative lead.
- **What:** names keep country-style codes in the Language field (JP, KR, UA, CH, VN; ads write US for English) until the planned move to ISO 639-1. Minds and the naming audit read legacy JA/KO/UK/ZH/VI as JP/KR/UA/CH/VN, so one language is one mind.

### 2026-11-02 · Separate tools around one shared memory
- **Decided by:** creative lead (Teddy).
- **What:** the board keeps the ticket system only; briefs are written in a brainstorm session and pasted into Notion by the strategist (no Notion connection); the report becomes a weekly PDF in the house style; signals and brain dumps happen in the brainstorm for now; persona knowledge and the experiment log live in the repo's `brain/`; the strategist runs the brainstormer (Claude project or Codex).
- **Unit of the persona clone:** one mind per persona × language, a single layer (both OS together). Latest understanding on top, every change kept in its history.
- **Evidence:** languages disagreed for 42% of concepts tried in 2+ languages, OS agreed 80%; 16 of 20 v8 adsets are switched off (lessons filed per adset would be lost).
- **How we'll know it worked:** briefs cite the mind and past experiments; no winner is decoded twice; the share of refreshes producing a new #1 rises above today's 31%.

### 2026-10-23 · The March 2026 ROAS break was the move to Singular (MMP)
- **Decided by:** creative lead (confirmed the Singular switch); dates found in the data.
- **What it means:** Meta's numbers are on a new ruler from the week of 23 Feb (iOS) and 9 Mar (Android). For the same App Store money, Meta ROAS reads 0.67× (iOS) and 0.71× (Android) of before. Absolute Meta ROAS, purchases, installs, IPM and click → install are not compared across the switch (spec §3.3).
- **Engine:** switch dates in `engine/settings.py`; each week judged on its own ruler; relative = same OS, same week.

### 2026-10-27 · Singular-era bar: acceptable from 0.40, refresh under 0.40
- **Decided by:** creative lead. "Below 0.4 is already a warning to refresh; 0.4–0.5 or above is acceptable", for adsets and creatives.
- **Engine:** `BARS["singular"]` = green 0.40, amber (critical below) 0.32, deep red 0.28; the last two keep the old proportions (0.8×, 0.7× of green). Replaces the proposed 0.35 / 0.28.
- **Note:** 0.40 on Singular ≈ 0.57 on Meta's old reporting. 56% of Singular-era spend clears it (79% cleared 0.50 before the switch).

### 2026-10-27 · Refresh = one concept with 3+ variants per adset
- **Decided by:** creative lead (one concept per refresh; every concept ships 2–3+ variants, re-cuts and re-sequences).
- **Evidence:** a new concept with 3+ spending variants in the adset became its #1 40% of the time vs 15% with 1–2. Add a proven J1 concept when the queue has one (no production).
- Replaces the proposed "2+ distinct concepts". Due tickets open at reign week 2 (1 week to make, 1 to read).

### 2026-10-27 · Board, scorecards, roster
- Board = shared Claude page (team gets access). Scorecards visible to everyone. Yuli Nur Hakim = KIM, Hanna Dolhikh = HAN; Deyan Haider and Hussein Saleh Cabrera have left.

## Proposed, waiting for the creative lead

### ~~2026-10-23 · Singular-era bar: green ≥ 0.35, critical < 0.28~~ (superseded 27 Oct by 0.40)
- **Why:** old bar 0.50 / 0.40 × 0.70 (measured ruler change). Keeps the same real-money standard: 79% of spend was green on the old bar before the switch; 74% is green on 0.35 since.
- **Applied provisionally** in the engine and dashboard so statuses mean something again. To change it, edit `BARS` in `engine/settings.py` and note it here.
- **Note:** "under 0.39 is critical" on Singular numbers equals 0.57 in pre-switch units, above the old green bar.

### 2026-10-27 · At-bats, verdicts and three strikes (spec §6, §15)
- **At-bat** = new concepts entering an adset in one week, adset 3+ weeks old (the variants rule above replaced the 2-concept proposal).
- **Verdicts:** week-1 read is provisional (20%+ of adset spend = provisional hit); week 4 is final (new #1 within 4 weeks = hit; home run if the adset's relative ROAS rose at weeks 3–4); #1 in weeks 5–12 = late hit. Ads under 20% in week 1 stay on: a third of refresh winners started under 5%.
- **Strikes** only in a turnaround (adset under green the week before); misses into healthy adsets are fouls. **3 turnaround strikes in a row → Review.** Replaces "Strike 3 = 2 failed at-bats or 7 days" and the D3 verdict.
- **Engine:** `ATBAT` in `engine/settings.py`, applied provisionally in `engine/tickets.py`.

### 2026-10-27 · Ticket priority weights (spec §15, §20.1)
- Priority = weight × last week's spend: review 1.0 · critical 1.0 · amber and falling 0.8 · leading signal 0.6 · due 0.5 (+0.1 if falling) · amber 0.4 · critical under the alert floor 0.3; × 0.5 with a challenger in test or 🧱. `TICKET_WEIGHTS` in `engine/settings.py`.

## Open
- TikTok: hold at today's budget and run a geo test (pause TikTok iOS 4 weeks in 3–4 countries where it's a big share; compare App Store proceeds with similar countries). Spec §19 Q13. TikTok's own ROAS can't decide this: half its Android value sits on ad groups that weren't spending.
- Profit bar: what a subscriber is worth after the first weeks (spec §19 Q1, Q6). Needs Singular D30 revenue or finance cohorts.
- US-only iOS test: budget, dates, success measure (spec §19 Q7).
- The 8 adsets switched off since the switch while at or above their OS average, and the dark personas: relaunch or obituary (Diagnosis §3).
- The May – June 2026 spend pullback: record whether it was a reaction to the ROAS reading (spec §19 Q12).
- Board home, scorecard visibility, roster codes, exports landing in Drive, watch-time columns, persona-card mapping (spec §19 Q17–Q22).
