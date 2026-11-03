# Bumpy — Ads Intelligence Spec
version: 1.3.4
status: DRAFT — living document. Every piece of feedback gets fixed *in this file*, then logged in the changelog.
owner: Creative lead (ads creative) · maintained with Claude

> Purpose of this file: the single reference for what we are building, why, and the rules it runs on.
> Any new chat or session about Bumpy reporting should read this first instead of re-explaining context.
> Related docs: `core/naming-adset-v8.md` (campaign/adset names, v8) · `core/naming-ad-v5.md` (ad names, v5). Agent map: `AGENTS.md`. How the tools and the shared memory fit: `ARCHITECTURE.md`.

---

## Changelog

**1.3.4 (2026-11-03): many strategists, one memory; the strategists' files merged.**
- **Collaboration:** each strategist brainstorms in their own Claude or Codex account on this repo; a brainstorm never
  writes to `main` and ends with one pull request (also when there's no brief yet); the creative lead merges. How-to:
  `tools/brainstormer/SOP.md`.
- **One home per list:** angles in `core/angles.csv` (the brief writer's list + those in use); brand rules in
  `core/brand.md`; creator-program (`TIN`, `001`…) and TikTok One (`TT1`–`TT4`, `TTO`) codes in `core/team.csv`; old
  brief-writer persona spellings mapped in `core/persona_aliases.csv`. Ad names v5.1.0 (`core/naming-ad-v5.md`).
- **Variants vs concepts (clarified, §6.3 and §15):** a version that opens on a different scene is a new concept code
  (the naming rule); variants of a concept are new hook sub-types, text, re-cuts, V2 re-orders after the same opening
  and other languages.
- **Persona parsing fix:** v5 ad names written with the canonical persona (GringoMaleLover, KoreanMaleCultureLover,
  GirlWantsToRelocate, SexyMaleLover, IndianFemaleDreamingForAsianMale) were read as Unknown; the ad parser now reads
  canonical names first.

**1.3.3 (2026-11-02): the refresh read and the launch review (decided by the creative lead).**
- **Refresh read (§6.2b):** first question, did the new creative reach the adset's top 3 spenders? Yes → the adset's ROAS decides: **Worked** (up and 0.40+), **Almost** (up, still under 0.40), **Flat** (moved under 0.02), **Worse** (down). No → **Miss**, or **Miss (left)** when old creatives keep the adset at 0.40+.
- **Strikes:** Worse is a strike in any context (the batch took spend and the adset lost money: fix first). Miss under the bar in a turnaround is a strike. Almost and Flat are not strikes, but the ticket stays open to swing again. Miss (left) is no strike and no Due ticket: leave it. Worked resets the count.
- **Tickets:** Worse weighs 1.0 (as critical), Almost / Flat 0.7, and neither is halved for "challenger in test" (the read is in). `READ` and `TICKET_WEIGHTS.refresh_*` in `engine/settings.py`.
- **Launch review deck:** `tools/report/REFRESH-REVIEW.md` (structure, rules, design) and `tools/report/refresh_review.py` (the numbers, from daily ad rows). First run: Batch 40, `reports/2026-10-26/`.

**1.3.2 (2026-11-02): incident rules confirmed; when an effect ends.**
- The creative lead confirmed the incident rules (void refreshes, incident weeks not counted under the bar). Both known incidents were on **iOS**; the 5–6 Oct effect is estimated to 11 Oct.
- How the end of an incident's effect is defined (§3.5): measured from daily data (signal ratio for tracking, App Store money for bugs), capped at 14 days; until a daily Meta export by OS exists, the logged estimate is used. A weekly check (`incident_check.csv`) compares each incident with App Store money and Meta's iOS ROAS: on 5–6 Oct store money held (0.98× a normal day) while Meta iOS ROAS went 0.41 → 0.40 and back to 0.45 the week after, which points to tracking, over by about 11 Oct.

**1.3.1 (2026-11-02): app and tracking incidents.**
- `core/incidents.csv` (format: `contracts/incident.md`) logs app or tracking problems that hurt results for reasons outside the creative. Known so far: 5–6 Oct 2026 (effect lasting some days) and 20–21 Oct 2026 (effect until 22–24 Oct).
- In an incident week (for that OS): a refresh that landed and missed is **Void** (no strike, no foul; a hit still counts); a week under the bar isn't counted toward weeks under the bar or Fading (a week above the bar still counts); ticket stories mark the week ⚠; the report names the incident. Measured on today's data: 24 tickets count one fewer week under the bar, 7 are no longer Fading; no refresh landed in an incident week yet, so nothing is void.
- Incidents are a short-lived cousin of measurement eras (§3.3): an era changes the ruler for good, an incident spoils a few days.

**1.3.0 (2026-11-02): separate tools around one shared memory (decided by the creative lead).**
- **The repo is the home.** Rules in `core/`, shared formats in `contracts/` (checked by `checks/validate.py` on every push), memory in `brain/`, this week's tickets in `state/`, each tool in `tools/<tool>/`. Map: `AGENTS.md`; design and change process: `ARCHITECTURE.md`. Exports are kept compressed in git (230 MB → 24 MB; the rebuilt datasets are identical).
- **Minds: one per persona × language** (both OS together), replacing the per-persona library of §13. `mind.md` = the persona clone (beliefs with confidence and evidence, their words, what stops their thumb, inspiration) + a facts block the Monday run rewrites; `history.md` = append-only diary (decodes, belief changes, experiments, new #1s, results). 84 minds seeded from the exports and the Notion persona cards; 102 registered in `core/minds.csv`.
- **Creatives:** one file per concept with its decode (first second, hook, message, why it stops the thumb, snapshot) and where it ran; 97 seeded from every coded concept that led an adset.
- **Experiments (the hypothesis log, replaces `data/log/at_bats.csv`):** one record per agreed brief with move, hypothesis, checkable prediction, options not chosen, the brief, results per adset (filled every Monday) and the lesson. Refreshes before the log: `brain/experiments/detected-refreshes.csv`.
- **Brainstormer + Brief Maker** (`tools/brainstormer/`, run by the strategist in Claude or Codex with the repo): reads the ticket and the mind, asks for missing winner decodes and inspiration and saves them, proposes options by playbook move, writes the brief (copied into Notion by the strategist), logs the experiment.
- **Ticket board = tickets only.** Briefs move to the brainstorm + Notion, the report to a weekly PDF in the house style (`tools/report/STYLE.md`), signals and brain dumps to the brainstorm, persona files and logs to `brain/`. Tickets show the clocks (#1 since, last refresh) and the brief that covers them; statuses move from the records and the exports.

**1.2.4 (2026-10-27): the Tuesday report lives on the board; how the pieces fit.**
- **Report tab (§20.7):** the Tuesday deck is generated every Monday (`engine/report.py` → `reports/<week>` on the board) in the deck's order: account in one line, 01 Team output, 02 New personas, 03 Persona expansion, 04 Refresh and iteration (summary, then week-1 reads and week-4 verdicts, each with an Ads Manager-style table: this adset now, the same adset the week before the refresh, its siblings on the other OS / languages; spend, CTR, C>I, IPM, ROAS coloured against the OS average; top creatives; insight and action item), 05 TikTok, 06 This week and decisions. A week selector keeps every past report. Present mode shows one section per screen (arrow keys, Esc).
- **Insights and action items are drafts** the presenter edits on the page; edits are saved separately (`report_notes`), so the Monday run never overwrites them. Only Claude writes the generated report (`reports` is admin-only).
- **People at a glance:** each person's card shows what they're on, how long it has waited past its usual time (brief 3 days, production 7, upload 3) and their score (designers: won 20%+ in week 1 vs team, adsets won or became #1, days brief → handoff; strategists: adsets won, hypotheses answered, strikes on their briefs).
- **How it fits together (§0.1):** one engine, three views (account dashboard: why; Creative Board: do and remember; Report tab: tell) and one rulebook (this spec). The board and the dashboard link to each other.

**1.2.3 (2026-10-27): history that is never lost; strikes, fading and personas on the board.**
- **Where everything lives (§20.10):** the board's database keeps the work (briefs, hypotheses, people, status history, handoffs, per-adset results, retros, signals, team tickets) and the history (a copy of each week's queue, every refresh since December with its verdict, a week-by-week table, the Notion tracker's 420 briefs, the persona cards). The weekly update replaces only the current week's queue and numbers. Raw exports and the engine need a permanent folder (§19 Q23); everything else is rebuilt from them.
- **Turnaround strikes on every ticket:** 0–3 dots plus the last five refreshes as H / S / F (hit, strike, foul), in the queue, the persona groups, the board cards and the ticket.
- **Fading alarm:** a ticket under the bar 2+ weeks in a row with no new concept since is marked "Fading"; 16 have no brief today. A header count tracks them (the silent-death pattern: 16 of 20 v8 adsets switched off had no new concept in their last 6 weeks).
- **Types tightened:** any adset under the bar is Decaying; Due is only for healthy adsets whose #1 has led 2+ weeks (now 52 Decaying, 18 Due). The dashboard status "⏳ Refresh due" is renamed "🔻 Falling".
- **Personas tab:** the living persona file (live state, tickets, winners of the last 26 weeks, the Notion card, retro learnings, signals). The 26 Notion cards are mapped to v8 personas: 10 from their top-spender ads, 15 by name (to confirm), 1 unmapped ("Wedding and Relocate"). Their 27 reference links are in the signal bank.
- **Log tab:** briefs and experiments (board + Notion), refreshes since December, week by week.
- **People:** a Team output panel (last 7 / 28 days: videos, images, briefs, adsets covered, task counts per handoff, the same breakdown as the Team Output slide). Scorecards add adsets won on the board.
- **Creative tags on briefs:** content style, message theme, hook type, format, spokesperson, so the format-gap audit can run on our own data.
- **The analysis dashboard** was refreshed with the 0.40 bar (grid, account, weekly, checks, overview and era datasets, and its bar labels).

**1.2.2 (2026-10-27): grouped briefs, plain ticket names, the signal bank.**
- **Ticket names:** Refresh → **Decaying** (hurting now: under the bar, falling, or hook rate / IPM down 20%+), Due stays **Due** (healthy, but its #1 has led 2+ weeks: brief the successor now), Review → **3 strikes**.
- **A brief can cover many tickets.** The strategist groups adsets one concept can serve (other languages, both OS, sometimes another persona). The brief is the production unit; the adset is still the measurement unit. Evidence: concepts already land in a median 3 established adsets (66% in 2+); each landing keeps about a 20% chance of becoming that adset's #1, so a concept in 5+ adsets wins somewhere 71% of the time vs 25% in one. Results often differ by language (42% of concepts tried in 2+ languages won in some but not all) and rarely by OS (80% same result).
- **Signals:** a link, an optional note and any number of personas. Platform is read from the link. Claude fills views, likes, comments, shares, saves (and run length for ad-library links) on the weekly run; the bank sorts by any of them or by engagement.
- **Guide:** a Guide tab in the board (and `docs/board-guide.md`) for strategists, designers and the UA team / management.

**1.2.1 (2026-10-27): the creative lead's decisions.**
- **Bar set:** on today's (Singular) numbers, **0.40 and up is acceptable; under 0.40 needs a refresh**. Critical under 0.32 and deep red under 0.28 keep the old proportions. In pre-switch units 0.40 ≈ 0.57, so it is stricter than the old 0.50 in real money: 56% of Singular-era spend clears it, where 79% cleared 0.50 before the switch.
- **Variants, not a second concept.** One concept per refresh is fine; what matters is how many variants of it land in each adset (hook sub-types, text, re-cuts, V2 re-orders after the same opening, languages; a different opening scene is a new concept code). A brand-new concept with 3+ spending variants in the adset became its #1 40% of the time, vs 15% with 1–2 (30 vs 154 entries); proven concepts 40% vs 25%. Most concepts reach an adset with only 1–2 spending variants (median 2 ads per at-bat). Adding a proven concept from the queue's J1 list costs no production. Replaces the 1.2.0 "2+ distinct concepts" rule (the 2-concept effect appears only once an at-bat has 4+ ads: 1–3 ads 24% vs 26%).
- **Cycle:** about 1 week to make and 1 week to read, so Due tickets open at reign week 2 (spec §6.7: lifespan − 1).
- **Re-computed on the 0.40 bar:** turnaround at-bats 125, hit rate 43%; 29 of them came after a missed one. 70 tickets open, 66 need a brief (45 persona × language groups); capacity still about 8 at-bats a week.
- **Board:** a shared Claude page; designers and strategists get access. **Scorecards:** everyone sees everyone's. **Roster:** Yuli Nur Hakim = KIM, Hanna Dolhikh = HAN; Deyan Haider and Hussein Saleh Cabrera have left (kept in history only). **Exports:** a Drive folder or the creative lead's folder.

**1.2.0 (2026-10-27): the operating loop: tickets, re-tested verdicts, scorecards, the Tuesday report** (adds the Notion Ad Creative Tracker, 423 briefs Feb 2025 – Oct 2026; the Persona Card Library, 27 cards; an example brief; the weekly Canva reports).
- **ROAS and creative, stated precisely.** A fresh concept that wins 20%+ of an adset's spend in its first week is what restores the adset: its relative ROAS goes +2% (weeks 1–2) and +7% (weeks 3–4), then −5% by weeks 5–6 as the reign fades. With no new #1: −3%, −5%, −8%. Concepts that become #1 after a slow start hold the adset's spend but not its ROAS (−4% to −6%). Within a week an ad's own ROAS sits near its adset's (#1 vs the rest 1.03–1.11×), so a creative is judged by delivery and by what its adset does after it takes over, never by its own ROAS row (§6.2).
- **At-bats re-tested** (227 refresh at-bats with a final verdict, adsets 3+ weeks old): 31% produced a new #1 within 4 weeks; 12% were home runs (new #1 and the adset's relative ROAS up at weeks 3–4). **One concept: 24%; two or more: 52%.** In a turnaround (adset under green the week before): 46%; one concept 33%, two or more 76% (n = 21). New rule: every at-bat carries at least 2 distinct concepts (§6.1).
- **Late bloomers are real.** 35% of refresh winners had under 5% of adset spend in their first week; 12% of those quiet entries become #1 by week 4 and 17% by week 12. The old D3 strike would have struck a third of eventual winners. Verdicts are now provisional at week 1 and final at week 4; a #1 in weeks 5–12 turns a strike into a late hit (§6.2). Late reigns are about half the size ($3.6k vs $7.6k spend as #1).
- **Strikes count only in a turnaround.** A challenger that fails to unseat a healthy #1 is a foul: it stays in people and concept records, not on the adset's count. History: only 9 of 80 turnaround at-bats came after a missed one, and 16 of the 20 v8 adsets switched off got no new concept in their last 6 live weeks. The three-strike rule's first job is to make sure the second and third swings happen (§6.3).
- **Average watch time is already in the ad export** (`Video average play time`), but Meta rounds it to whole seconds: 79% of spending videos read 2 or 3 s, and it has no power to pick winners (0.49, where 0.50 is a coin flip; week-1 share 0.90 on the same entries). Count columns replace it (§3.1).
- **Designer records from the Notion tracker** (brief code + batch joined to ad data; concepts with 4+ weeks of results): Ostap 50% won 20%+ of an adset in week 1 (30 concepts), Hanna 50% (28), Usman 45% (22); team baseline 38% (84 coded concepts). The gaps are within noise: scorecards can't rank on hit rate alone for months (§9). (A first pass on 27 Oct read 27% / 27% / 19% with a looser join; the board uses this definition.)
- **Capacity vs demand:** about 8.4 refresh at-bats a week land in established Meta adsets; 60 tickets need a brief (42 persona × language groups).
- **Engine:** new step `engine/tickets.py` (tk_* datasets: queue, at-bats with verdicts, J1 candidates, resurrection candidates, facts). At-bat and ticket settings in `engine/settings.py` (`ATBAT`, `TICKET_WEIGHTS`), proposed, waiting for the creative lead. New §20 describes the loop.

**1.1.0 (2026-10-23): TikTok added; channels judged against App Store money** (adds the TikTok ad group × country × week export, 1 Dec 2025 – 18 Oct 2026, $1.22M spend, both OS).
- **Size and shape:** TikTok was $36k a week before mid-Feb, $17.5k in May – mid-Aug, $26.6k over the last 10 weeks (13% of paid spend). 59% iOS. 89% of it runs in broad General ad groups, so the creative carries the persona.
- **Its own measurement history:** TikTok's campaigns were rebuilt for MMP attribution (`| Migration` and v8 ad groups) in the week of 2 Feb 2026, three weeks before Meta's switch. Android purchases went unreported for 4 weeks after it (9 Feb – 8 Mar).
- **Value without spend:** since the MMP move TikTok is credited with purchase value on ad groups that didn't spend that week: 51% of its Android value and 10% of iOS since 16 Mar (4% before). 113 ad groups with no spend since December got $142k. Most likely renewals of users acquired earlier: real money, not bought by current spend. TikTok is judged on live ad groups only (§3.4).
- **Two channels, two rulers:** on Singular, TikTok's live iOS ROAS reads 0.70 and Android 0.60 (reported: 0.78 / 1.22); Meta's reads 0.43 / 0.40. Each network credits itself, so the levels are not compared.
- **What the store says:** with both channels in the same country × week model, each Meta iOS $ comes with $0.85 of App Store proceeds (unchanged), each TikTok iOS $ with $0.13 ± 0.12 (−$0.17 to $0.46 across models; −$0.03 comparing countries before vs now). Where TikTok was cut by $1–2k a week (Mexico, Colombia, Philippines, Indonesia), App Store money held or grew. TikTok's spend moves less than Meta's, so this is less precise: a geo test settles it (§19 Q13).
- **Meta's March drop is not TikTok taking credit:** Meta iOS fell to 0.77× where TikTok is 15%+ of iOS spend and 0.80× where it's under 5%.
- **The US is coming back on its own:** Meta US iOS spend went from $7.0k (June) to $20.9k a week (September) through worldwide English adsets, plus TikTok US from mid-August; US App Store proceeds went from $50.6k to $58.4k a week.
- **Dashboard:** new Channels tab (spend by channel vs App Store money, each channel's own ROAS, TikTok value with and without spend, store money per $ by channel, countries, TikTok ad groups vs TikTok's own average). Overview shows TikTok spend and credit. Actions: hold TikTok and run a geo test (#2).

**1.0.0 (2026-10-23): the March break was the Singular switch; the system now runs on measurement eras.**
- **Cause confirmed:** Meta's purchase and install numbers have come through Singular (our MMP) since the week of **23 Feb (iOS)** and **9 Mar (Android)** 2026. For the same App Store money, Singular credits Meta **0.67× (iOS)** and **0.71× (Android)** of what Meta's own attribution did. Proceeds per iOS ad dollar didn't change. The "break" is a smaller ruler, not a weaker business.
- **What the switch moved (§3.3):** Meta ROAS, purchases, installs, IPM and click → install stepped down in the switch week; CPM didn't. On iOS, click-through also jumped +26% and click → install fell 34% in the switch weeks: the iOS click path changed too. Hook rate fell from the week before (Meta counts it itself: creative mix).
- **Every relative finding holds on Singular data alone** (§12, Diagnosis §4): reign median 3 weeks; ROAS −6% by reign week 3; #1 vs rest; week-1 share predicts a new #1 (power 0.81 both ways); new creative winning 20%+ lifts the adset (+3–4%) vs −7% with none; luck fades ~40–47% a week. Spend elasticity is even smaller on Singular (−0.00 vs −0.05). App Store proceeds per iOS $: $0.86 on all weeks, $0.72 on Singular weeks alone (fewer weeks, noisier).
- **Decisions on the new ruler:** adset-level budget moves kept following relative results (70% → 76%), and strong adsets were cut less often (3.3 → 2.4 a week). The damage was at account level: spend fell from $160k to about $120k a week in May–June while account Meta ROAS read 0.37–0.40 (red on the old bar, green on a restated one), and App Store proceeds ran about $14k a week below March–April. 8 adsets were switched off while at or above their OS average (peak $56k/week combined; LGBTQ and General on Android are now dark). The US-only iOS adset was cut while green on a restated bar.
- **The bar is per ruler (§15):** 0.50 / 0.40 on Meta's own attribution; **0.35 / 0.28 on Singular (proposed = old × 0.70; waiting for the creative lead)**. On the old bar only 21% of Singular-era spend is green (was 79% before); on 0.35 it is 74%. The team's "under 0.39 is critical" equals 0.57 in pre-switch units, above the old green bar.
- **Relative = same OS, same week** everywhere (grid colour, reigns, takeovers, refreshes, spend test), because the two OS switched on different weeks.
- **The US may be under-read more:** inside the same worldwide iOS adsets, Singular credits US traffic 0.89× the rest of the world (was 1.05×). The US test (§19 Q7) settles it with store money.
- **Engine:** `engine/settings.py` holds switch dates and bars; new step `engine/eras.py` (era_* datasets). Funnel steps (§4.4) now compare within the Singular era. Markets table shows countries vs their OS average per window instead of raw ROAS across eras.
- **New data asks (§3.1, §19):** Google Play earnings by country; Singular export by campaign × country × week with revenue D7/D30, both OS; campaign name and ID added to the Meta exports so the two can be joined.

**0.9.0 (2026-10-23): one joined model, rebuilt around the objective** (adds adset × country weekly exports; all sources now joined on week, adset, ad and country).
- **The model (§0):** money moves in one chain: creative → adset → country → App Store money, with Meta's measurement on the side. Each lever acts on one link; the dashboard follows the chain.
- **Store money follows iOS spend, country by country:** across 92 countries, each $1 change in weekly iOS spend came with about $0.85 change in weekly App Store proceeds (before vs last 10 weeks), plus ~$750/week organic growth per country. Pooled country + week fixed effects (top 40 storefronts) give $0.86. Meta credits $0.43.
- **The structure moved the money:** moving from country-specific to worldwide language adsets took the US from 40% to 20% of English iOS spend (25% → 14% of all spend). US iOS spend −$15k/week, US App Store proceeds −$12k/week. Spend went to Western Europe, Türkiye, Japan and Mexico, where proceeds rose with it.
- **The March break was global:** Meta ROAS fell in 96% of country × OS combinations at once (median −30%).
- **Creative doesn't move country mix:** weeks when the #1 creative changes shift an adset's country mix no more than ordinary weeks (7% vs 7%). Country mix is set by the adset's structure (language, OS, geo), not by the creative.
- **Dashboard rebuilt:** Overview (money out vs in, this week's actions) · Markets (countries, US, dose–response) · Adsets & personas (grid + #1 creative, reign week, US share, top country, colour toggle bar/relative; dossier with concept and country relays) · Creatives · Diagnosis (break + funnel) · Data checks.

**0.8.1 (2026-10-23): creative layer, week by week** (ad exports spread into Mon–Sun weeks; 2,662 adset-weeks, 529 reigns).
- **Top spender:** an adset's #1 concept takes a median 56% of its weekly spend. Adsets with a clear #1 (70%+) run 6% above the account; adsets with no clear winner (under 35%) run 8% below.
- **Reign = decay clock, now measured:** a concept stays #1 for a median of 3 weeks (27% last 6+). Adset ROAS holds for weeks 1–2 of a reign, then slides about 3–4% a week to about −15% by week 6, while spend keeps rising. So the default lifespan stays 3 weeks, and "Refresh due" fires when the current #1 enters week 3 (§6.7).
- **Delivery is decided in week 1:** of concepts that took 20%+ of an adset's spend in their first week, 82% became #1; under 5%, 9%. Installs per impression is the next-best early signal; hook rate and CTR predict nothing (power ≈ 0.51). Week-1 share is the delivery verdict (§6.2 threshold unchanged at 20%).
- **Takeovers:** a fresh concept taking #1 holds the adset (+1% ROAS vs account, +2% spend); an older concept moving up comes with −10% spend (adset shrinking); no change in #1 drifts −6%.
- **Three codes run the account:** a2Ef3y (wanted; 1.15× account ROAS while #1, beats the rest of its adset by 17%), H7kM3N (airport; 1.05×), n6f2Wt (banner; 1.01×, led 70 adsets). i7P5Th was favoured by Meta although it ran 11% below the rest of its adsets.
- **March break, creative view:** adsets that kept the same #1 through the break fell as much (−39%) as those whose #1 changed (−34%); the same #1 creative went from 0.65 to 0.40 in the same adsets.
- **Naming:** code collisions that differ only in letter case or a typo: a2Ef3y / a2Ef3Y (different concepts), H7kM3N (airport) / h7km3n (wanted), n6f2Wt / n62Wt, P8c7ao / p8C7aO. Codes must be unique ignoring case.
- New dashboard tab **Creatives**; the grid's row dossier now shows the concept relay.

**0.8.0 (2026-10-23): root cause of the ROAS break** (adds 11 monthly ad-level exports and App Store Connect proceeds by country, 1 Dec 2025 – 18 Oct 2026).
- **Finding 1:** the late Feb – Mar 2026 break hit every adset structure, both OS and every creative cohort at once (creatives live before December fell from 0.56 to 0.42, the same as new ones). Purchases per million impressions fell about 40% with CPM flat. Not creative, not spend.
- **Finding 2:** App Store proceeds per iOS ad dollar did not change (0.98 → 0.95 in the main weekly model; 0.91×–1.31× after/before across 8 variants) while Meta iOS ROAS fell 0.64 → 0.43. Meta credits fewer purchases; the money didn't fall. Candidate causes to check: Meta's click-through attribution change (announced 3 Mar 2026, link clicks only; app campaigns not confirmed), or an app/SDK/paywall change near 23 Feb or 16 Mar.
- **Finding 3:** the real loss came afterwards. The US-only iOS adset (ROAS 0.83 Dec–Jan, $13.7 per purchase) fell with everything else, was read as red and cut to zero by mid-May; US App Store proceeds fell from about $72k to $51k a week while nearly every other market grew. India, the other country-only adset, also fell.
- **Spend:** scaling an adset costs almost no ROAS once luck is removed (elasticity −0.03); a week above average loses about 42% of its edge the next week anyway. Scale on 2-week averages, not one good week.
- **Refreshes:** new creative that wins 20%+ of an adset's spend lifts the adset's ROAS vs the account (+6% median vs −8% with no new creative); new creative that doesn't win spend does nothing. Proven concepts win spend on arrival twice as often as brand-new ones (9% vs 4%).
- **Creative vs ROAS:** within an adset, Meta keeps creatives close to the adset's ROAS (families index 0.90–1.08); creative decides how much spend an adset can take, not its ROAS.
- **New tab:** "Why ROAS fell" in the dashboard; App Store proceeds now feed it (the money check, §10, now runs on every upload instead of quarterly).
- **Export recipe fix (§3.1):** Meta's "Week" breakdown counts 7-day blocks from the report's start date, so monthly exports starting on the 1st don't line up with Mon–Sun weeks. Ad-level exports must start on a Monday.

**0.7.0 (2026-10-22): first run on real data** (adset export, 1 Dec 2025 – 18 Oct 2026, 46 weeks, 338 adsets).
- **Revenue = Purchase ROAS × spend.** The in-app conversion value column misses web purchases (87 rows, about $30k of spend), so it is only a cross-check.
- **IPM added** (installs per 1,000 impressions) as the install-rate / demand signal, with account ROAS split into its steps: ROAS = IPM × I>P × revenue per purchase ÷ CPM (IPM = CTR × C>I). New "What moved ROAS" view (§4.4).
- **Low ceiling refined** (§6.6): judged only where an adset had a 4-week window at alert-floor spend, and flagged only if that window never reached 0.50 *and* never matched the account's own ROAS over the same weeks. The absolute rule flagged 45 of 81 live adsets, because the whole account has been under 0.50 since March.
- **Stand-ins until ad-level data and budget arrive:** Refresh due also fires when a green adset's IPM or hook rate falls ≥ 20% vs its prior 4-week average; Scaling = spend up ≥ 15% vs 2 weeks ago; ↑ ↓ = spend ±20% week on week.
- Parser accepts adset names with spaced slashes (` / `), as Meta exports them. Non-purchase objectives (engagement, sign-up, install) are shown but not judged on ROAS.
- Naming drift found and listed on the Data checks tab: personas outside the taxonomy (e.g. `IntlFriendFinder` vs canonical `InternationalFriendFinder`) and non-ISO language codes (`JP`, `KR`, `CH`, `UA`, `PH`).

**0.6.1 (2026-10-22):** Export recipe added (§3.1): weekly time breakdown, raw counts, IDs, budget-history limitation.
**0.6.0 (2026-10-20): independent review merged in.**
- **Critical = ROAS < 0.40** (anything "0.39ish" is already critical). Zones are now green / amber / critical.
- **From rescue to supply** (§8): every slate has three lanes. **Defend** fixes flagged adsets. **Amplify** spreads fresh winners, and its slots are protected. **Explore** is J3 research. A supply calculation shows how many at-bats are needed to replace winners before they die, compared with the 8 slots available.
- **Foolproofing** (§6): a market-day check, so an account-wide drop isn't blamed on creative. A minimum-evidence rule, so tiny samples don't hand out strikes. A low-ceiling rule, so capacity isn't burned rescuing personas that were never profitable.
- **Survives a restructure:** the engine computes at ad level, with persona and language read from ad names. The adset view is the default, and a persona × language view also exists.
- **AI assistant strategist** (§11): Claude prepares each slate, drafts hypotheses and briefs, gives verdicts, maintains the bibles, and reminds the team about uploads. The 2 strategists approve and add taste. Shared ownership of all personas is fine because the engine watches every persona every upload.
- **Simpler grid:** 7 statuses plus 3 flags. The strike-points column was removed; points stay in the records.
- **Quarterly profit check** (§10): is 0.50 at 7-day click still the right bar everywhere? This is a ritual, not a dashboard.
- Decided: manual exports twice a week; Slack on hold (the update is a file for now); Google Sheet added later; app store reviews dropped into persona folders manually, with Claude reminding monthly.

**0.5.0:** Operating model: jurus, turnaround clock, twice-weekly rhythm, hypothesis gate, team layer, persona library, Claude Code.
**0.4.0:** ½-strike streak → check beyond creative. No owner back-fill.
**0.3.0:** Spend-first strikes. Events from ad names and numbers. History permanent. Ad naming v5.
**0.2.0:** Row = adset. One page. D3 verdicts. Decay clock. Kill events.
**0.1.0:** Initial proposal.

---

## 0. The model: how money moves

```
creative ──► adset / ad group ► country ─────────► App Store / Play money
 (how much the    (structure decides     (each country returns       (the truth)
  adset can spend; where spend lands:     its own amount of store
  decays from      language, OS, geo)     money per $)
  reign week 3)
                         Each channel (Meta, TikTok) credits itself beside the chain,
                         on its own ruler (§3.3, §3.4). App Store / Play money by
                         country is the one currency both are checked against.
```

| Link | Lever | Owner | Measured by |
|---|---|---|---|
| Creative → adset | refresh, jurus, delivery in week 1, decay clock | Strategists, designers | #1 share, reign week, week-1 share, relative ROAS |
| Adset → country | structure (language/OS/geo adsets), budgets, exclusions | Media buyer | country mix per adset, US share |
| Country → money | where to put budget | Media buyer + management | store proceeds per iOS $ by country, dose–response |
| Channel → money | how much goes to Meta vs TikTok | Media buyer + management | store proceeds per iOS $ by channel; geo tests |
| Measurement | the bar, per ruler (§3.3, §15) | Creative lead + management | Meta-credited vs store money, weekly; Singular vs Meta |

**Questions the system answers, in order:** (1) Are we scaling sustainably? spend vs store money. (2) Where does money go and come back? countries. (3) What needs action now? adsets, decay, actions. (4) What works in creative? (5) Why did things move? diagnosis. (6) Can we trust the data? checks.

### 0.1 How the pieces fit (since 1.2.4)
| Piece | Question it answers | Who opens it | When | Made from |
|---|---|---|---|---|
| **This spec** (Claude project) | What are the rules and why? | the creative lead; any Claude or Codex session | when a rule changes | decisions, back-tests |
| **The engine** (folder: `engine/`) | — (it's the machine) | Claude | every Monday | the raw exports + the spec's thresholds |
| **Account dashboard** | *Why* is the account moving? money vs store, markets, channels, eras, which adsets and creatives drive it | creative lead, management | weekly, before setting budget or the bar | the engine's datasets |
| **Creative Board** | *What do we do, who is on it, and what did we learn?* tickets, briefs, production, results, retro, scorecards, persona files, signals, the permanent log | strategists, designers, media buyer, everyone | daily | the engine's queue + what the team writes |
| **Report tab** (on the board) | *What happened and what's next?* the Tuesday deck | the UA team | Tuesday | the engine + the board's work, with edited notes |

The three goals map onto it: **easy reporting** = the Report tab (generated, edited, presented, kept per week); **easy view of people** = People tab (who's on what, waiting, score); **history to iterate on** = the Log tab, `history/<week>` and `reports/<week>` on the board, plus the raw exports in the permanent folder (§20.10).

The loop: Monday exports → engine → dashboard (why) and board queue (do) → briefs generate the ad names → ads run → next Monday's exports carry those names → the engine reads each covered adset's result → it lands on the brief, the persona file, the scorecards and the next report.

## 1. Goal

Scale Meta (later TikTok/Google) spend week after week, profitably.

- **Defence: zero critical adsets** (ROAS under the critical line of the current ruler at meaningful spend; §15). Amber-and-falling gets refreshed *before* it turns critical.
- **Offence: green spend grows** (weekly spend in adsets at or above the green bar of the current ruler).
- **Supply: winners are replaced faster than they die.** This is what makes defence and offence possible at the same time.

No adset or persona fades out silently. Anything retired is retired by a written decision.

---

## 2. Principles

1. **One page.** Separate only when it's impossible to combine.
2. **Readable by eye.** Colour = ROAS. Number = spend. Markers = something happened. Hover = why. Click = full story.
3. **The machine watches everything; humans decide.** Events come from ad names and numbers. Claude drafts the slate, hypotheses, and briefs; strategists approve.
4. **Act fast.** Two slates a week. Read at week 1, judged at week 4, and the next swing doesn't wait for the verdict.
5. **Supply over rescue.** Keep enough fresh winners coming that fewer adsets need rescuing.
6. **Every action is an experiment.** Hypothesis before, verdict after, one-line learning.
7. **History is permanent.** Once uploaded, data stays even if deleted in Meta.
8. **Updates dictate action.** What to do, who, by when. Nothing to do → one line.
9. **Simple to run.** If a rule doesn't change a decision, it gets removed.

---

## 3. Inputs

### 3.1 Manual exports, twice a week (saved report templates in Ads Manager)

| Upload | Covers | Used for |
|---|---|---|
| **Monday** | previous Mon–Sun | verdicts on Thursday-live at-bats · weekly grid · Slate A |
| **Thursday** | Mon–Wed (partial, marked) | verdicts on Monday-live at-bats · Slate B |

**Export recipe (saved report templates in Ads Manager):**
- Breakdown **By time → Week**, so one file holds many weeks. Date range starts on a Monday.
- Attribution **7-day click**. One currency. Filter: amount spent > 0 only, with **no status filter**, so turned-off adsets and ads are included. CSV.
- **One export per level covers the whole account** (all campaigns, adsets, ads): 2 files per upload, never one per adset.
- Raw counts, not ratios: C>I, I>P, hook rate and hold rate are computed by the engine so they're identical every week.
- IDs included: names can change, IDs can't.

**B. Ad level (main file; every adset number is the sum of its ads):** reporting starts · reporting ends · ad ID · ad name · ad set ID · ad set name · amount spent · impressions · link clicks · app installs · purchases · purchases conversion value · 3-second video plays · **ThruPlays · video plays at 25% · 50% · 75% · 95% · 100%** (from 1.2).
Watch time comes from these counts: hold rate = ThruPlays ÷ 3-second plays, and the drop-off curve from the quartile plays. Counts add up exactly across days, ads and adsets; an average doesn't. `Video average play time` is already in the export and is kept as context only: Meta rounds it to whole seconds (79% of spending videos read 2 or 3 s) and it doesn't pick winners (changelog 1.2.0).
Optional: frequency (fatigue context) · purchase ROAS (backfill only, to cross-check that computed ROAS matches Meta).
Use the combined **Purchases** and **Purchases conversion value** columns (not app-only), so web adsets aren't zero. Only ads with spend > $1 matter (~1,470 of ~2,253 a week).

**A. Adset level (slim; only what ads can't give):** reporting starts · reporting ends · ad set ID · ad set name · ad set budget · amount spent (checks that ad rows add up). CBO adsets have no adset budget; their budget changes are inferred from spend.

**Not needed (computed by the engine or unused):** CPM · CTR · C>I · I>P · cost per install · cost per purchase · ROAS · results · cost per result · reach · delivery status · hook/hold rate custom columns.

**Campaign name and campaign ID: needed from 1.0** in every Meta export. Singular doesn't report adsets, so campaign is the level where Meta and Singular numbers meet.

**Budget history:** Ads Manager exports show the *current* budget, not the budget in past weeks. For the backfill, budget changes are inferred from spend (budgets are normally fully spent). From the first live export on, each upload records that day's budget, so real budget history builds forward.

**File names:** `adset_YYYY-MM-DD_YYYY-MM-DD.csv` · `ad_YYYY-MM-DD_YYYY-MM-DD.csv` (start and end dates).

**Every export starts on a Monday.** Meta's "Week" breakdown counts 7-day blocks from the report's start date, not calendar weeks. If the ad file is too big for one export, split it into blocks that each start on a Monday and end on a Sunday (e.g. 29 Dec – 1 Feb, 2 Feb – 1 Mar), never by calendar month.

**F. Adset × country (weekly), every upload:** same columns as the adset file plus Country. Start on a Monday. It is what connects spend to App Store money by country.

**E. App Store proceeds by country (daily), every Monday:** App Store Connect → Proceeds, by territory, daily. Feeds the money check. Google Play revenue by country, when available, does the same for Android.
**G. Singular, every Monday (from 1.0):** campaign × country × OS × week: cost, installs, purchases, revenue (D0, D7, D30 if available). It checks what Singular sends Meta, and it is the only Android money we have until Google Play arrives. File name `singular_<start>_<end>.csv` in `data/raw/singular/`.
**I. TikTok, every Monday (from 1.1):** TikTok Ads Manager → Ad group report, breakdown **By week** and **Country/Region**, currency USD, both OS in one file. Columns: ad group name, ad group ID, campaign name, spend, impressions, clicks (destination), app installs, unique purchases (app), purchase value (app). File name `tiktok_<start>_<end>.csv` in `data/raw/tiktok/`. Later: the ad-level report with v5 ad names, so TikTok creatives join the concept relay.
**H. Google Play, monthly:** Play Console → Download reports → Financial → earnings by country → `data/raw/play/`.
**C. On request:** creative assets for flagged ads; country breakdown for one adset.
**D. Monthly, manual:** app store reviews and other customer voice → persona `voice/` folders (Claude reminds).

Every upload is validated first: missing columns, missing weeks, duplicate rows, and ad names that don't parse are reported before any number is used.

**Revenue rule:** revenue = Purchase ROAS (7-day click) × spend, which covers app and web purchases. The in-app conversion value column misses web purchases and is only a cross-check. Extra columns in an export (CTR, video play time, a Hook Rate custom column) are accepted and ignored or used where useful.

**Backfill:** weekly A + B from 2026-01-01. Survivorship bias: anything deleted before upload is missing.

### 3.2 Parsing

**Adset name (v8, 12 fields, `/`; Meta exports it with spaces, ` / `, and both are read):** `Level/Platform/Persona/SubAngle/OS/Geo/Language/Gender/Objective/BidStrategy/Modifier/LaunchDate`. Used to identify the adset; never used for event detection.

**Ad name, by field count (`-`):**
| Fields | Version | Note |
|---|---|---|
| 12 | v5 | `persona-audiencecode-conceptcode-conceptname-hook-headline-angle-modifier-VID/IMG-strategist-designer-batch` |
| 10 | v4 | no strategist/designer → *unknown* |
| other | — | naming error, listed in the update, not guessed |

- `conceptcode` = one concept. `batch` = production week → identifies a refresh. Codes must be unique **ignoring case**: the upload check flags codes that differ only by case or one character.
- Ad `modifier` = awareness stage (not the adset's lifecycle Modifier).
- `audiencecode` `US` = English; others = matching language.
- **The engine computes at ad level.** Persona and language come from the ad name, so the system keeps working if adsets are restructured or consolidated.

### 3.3 Measurement eras (since 1.0)

Meta's purchase, value and install numbers come from whoever reports conversions to Meta. That changed when Singular (our MMP) took over. Each era is a different ruler for the same money.

| Era | Weeks | What feeds Meta's numbers |
|---|---|---|
| Pre | to 16 Feb 2026 | Meta's own attribution (SDK / pixel) |
| Switching | 23 Feb – 15 Mar 2026 | iOS on Singular from 23 Feb, Android from 9 Mar |
| Singular | from 16 Mar 2026 | Singular |

**What changed with the ruler and what didn't** (Diagnosis §1; ratio = Singular era ÷ pre):

| Metric | iOS | Android | Use across eras? |
|---|---|---|---|
| Meta ROAS | 0.67× | 0.71× | Never compare absolute values. Each week judged on its own ruler's bar |
| Purchases per 1M impressions | 0.84× (step −33%) | 0.96× (step −35%) | No |
| Installs per 1k impressions (IPM) | 0.88× (step −17%) | 1.02× (step −16%) | No |
| Click → install | 0.51× (step −34%) | 0.85× | No; on iOS the click path changed too |
| Click-through rate | 1.73× (step +26%) | 1.19× | iOS: no; Android: yes |
| CPM | 1.11× (step −2%) | 1.39× | Yes (Meta's own count) |
| Hook rate | 0.79× | 0.80× | Yes (Meta's own count; fell with the creative mix) |
| App Store proceeds | unchanged per iOS $ | — | Yes: the truth |

**Rules:**
1. Never compare absolute Meta ROAS, purchases, installs, IPM or click → install across the switch. Baselines for these (decay, low ceiling, check beyond creative, leading signals) come from the same era.
2. Each week is judged on the bar of its own ruler (§15). The grid colours each cell that way; italic week headers mark the switching weeks.
3. Relative numbers are compared within the same OS and the same week (adset ÷ its OS account). The ruler cancels out, so relative findings use the full history. Diagnosis §4 recomputes every finding on Singular weeks alone, every upload, and flags any that stop holding.
4. Store money (App Store, later Google Play and Singular cohort revenue) is the check on every era.
5. Any future measurement change (MMP, SDK, attribution setting, conversion mapping) starts a new era: add its dates to `engine/settings.py`, restate the bar the same week from Meta ROAS for the same store money before and after, and log it in `core/decisions.md`.

Known gaps: Singular doesn't report adsets, so Meta's adset numbers remain the only adset view. The undercount may not be equal everywhere: inside the same worldwide iOS adsets, US traffic reads 0.89× the rest on Singular vs 1.05× before.

### 3.4 Channels (since 1.1)

| Channel | What its ROAS is | Ruler changes |
|---|---|---|
| Meta | Meta's credit, 7-day click; through Singular since 23 Feb (iOS) / 9 Mar (Android) | §3.3 |
| TikTok | TikTok's "purchase value (app)" through its MMP campaigns, live ad groups only | MMP campaigns from 2 Feb 2026; Android purchases missing 9 Feb – 8 Mar |

**Rules:**
1. Never compare one channel's ROAS level with another's. Each network credits itself, with its own windows and dedupe. Compare a channel with itself over time, and channels with each other only through store money.
2. **Store money decides the split between channels:** App Store proceeds by storefront and week against each channel's iOS spend in that country (Channels tab), and geo tests where that is too imprecise.
3. **TikTok live value:** an ad-group week counts from $20 of spend. Value TikTok credits to ad groups that didn't spend is reported separately ("value without spend") and never counts toward a TikTok ROAS.
4. TikTok ad groups are judged against TikTok's own OS average in the same week (relative), until a TikTok bar is set from store money.
5. TikTok runs broad General ad groups, so persona statuses and strikes stay Meta-only until TikTok ad-level exports with v5 names arrive.

---

### 3.5 App and tracking incidents (since 1.3.1)
Logged in `core/incidents.csv` (format: `contracts/incident.md`). An incident week (any day of the Mon–Sun week
inside `start`…`effect_until`, for that OS) can't count against an adset, a creative or a person: a refresh that
landed then and missed is Void; a week under the bar then doesn't count toward weeks under the bar or Fading.

**When the effect ends.** `start` and `end` are when the problem itself was live (from the dev team or the
release notes). The end of the *effect* is measured, not guessed, once a daily Meta export by OS is in
`data/raw/meta_daily/`:
- **tracking** (Meta saw less than really happened): the daily signal ratio = Meta-reported purchase value ÷
  App Store proceeds, for that OS. Baseline = its median over the 14 days before `start`. The effect ends on
  the first day after `end` from which the ratio stays at 90%+ of the baseline for 2 days in a row.
- **release bug, store or payments** (users really bought less): App Store proceeds per day ÷ the same weekday's
  average over the 4 weeks before `start`. The effect ends when it is back to 95%+ for 2 days in a row.
- **Cap: 14 days after `end`.** Not back by then means it isn't an incident but a lasting change: treat it as a
  measurement era (§3.3) and decide a restated bar.
- Until the daily export exists, `effect_until` is the logged estimate (`effect_basis: estimate`), and
  `output/data/incident_check.csv` shows whether App Store money held and whether Meta's weekly ROAS was back
  the week after.

## 4. The page

### 4.1 Grid
- **Views:** by adset (default, grouped by persona) · by persona × language (aggregated from ads).
- **Left columns:** Status · Adset · Budget now · Spend last week · ROAS last week · $ leaking · Scale lost · Turnaround clock · Last jurus + verdict · Decay clock · Flags
- **Right columns:** one per week, newest first, back to January. Partial weeks marked.
- **Cell:** spend on a ROAS colour, judged on the bar of that week's ruler (§15): **green · amber · critical · deep red** · grey = off. ↑ / ↓ = budget change. Toggle: colour vs the adset's own OS that week (relative).
- **Markers:** ● refresh (green = hit or home run, red = strike, grey = foul, hollow = pending week-1 read) · ✕ kill (good/bad) · ◌ under-delivery.
- **Sorts:** status severity (default) · $ leaking = spend × max(0, green bar − ROAS) · scale lost = 6-month peak weekly spend − last week · spend · ROAS · clocks.

### 4.2 Statuses (one per adset) and flags

| Status | Rule (v0) |
|---|---|
| 🆘 Critical | ROAS under the critical line (§15), spend above alert floor |
| ⚾ Strike 3 | 3 turnaround strikes in a row → Review (§6.3) |
| 🔻 Falling (was ⏳ Refresh due) | under the bar and falling · or on green with IPM / hook rate down ≥ 20%. On the board both are **Decaying** tickets; an old #1 on a healthy adset is a **Due** ticket |
| 🟠 Amber | ROAS between the critical line and the green bar, not falling |
| 🚀 Scaling | ROAS ≥ green bar, budget up vs. 2 weeks ago |
| ✅ Healthy | ROAS ≥ green bar |
| ⚫ Off | no spend; row kept with peak and last status |

| Flag | Rule |
|---|---|
| 📉 Shrinking | 2 budget cuts in a row, or ≥ 30% below 6-month peak |
| 🧱 Low ceiling | best 4 weeks in the last 6 months never reached the green bar of their ruler nor the adset's OS average, at alert-floor spend (§6.6) |
| 🌧 Market day | account-wide drop detected; clocks paused (§6.5) |

Alert floor: adset spend ≥ 1% of account spend in the period.

### 4.3 Row expansion (the dossier)
Spend + ROAS line with markers · concept relay (spend share by concept per week) · peak card (what carried the peak, and why) · at-bat log (jurus, source, hypothesis, verdict, learning, strategist, designer) · what works here (hit rate by jurus, angle, awareness, concept family) · now (top 3 spenders and age, clocks, Claude's suggested next jurus).

### 4.4 What moved ROAS (account level)
ROAS = IPM × I>P × revenue per purchase ÷ CPM, with IPM = CTR × C>I. The page compares the first 8 weeks on Singular with the last 4 weeks (same ruler) and splits the ROAS change across the four steps (log shares), plus each step week by week. It answers "is this creative, cost, or monetisation?" before anyone refreshes anything. IPM is the install-rate (demand) signal.

---

## 5. Jurus: the moves

| Code | Jurus | What it is | Requires | Lineage |
|---|---|---|---|---|
| **J1** | Cross-pollinate | Proven winner taken to another persona or language, new angle or small adjustments | A hit in the last 4 weeks, in a place the message hasn't run | records source concept |
| **J2** | Shape-shift | Same message, new form (new image, new video hook, carousel, screenshot, review style…) | A proven message (a hit, or a concept that won 20%+ delivery) that isn't fatigued | records source concept |
| **J3** | New concept | Research-led: pain points, their own words, ad library, organic | A logged signal in the persona library | starts a lineage |

**Choosing (Claude proposes, strategist decides):** proven unfatigued message here → J2 · own message fatigued, fresh winner elsewhere fits → J1 · neither, or Review after no-delivery failures → J3 · last 2 turnaround at-bats won delivery but the adset's ROAS didn't follow → check beyond creative first (§6.4).

**J2 stop rule:** stop shape-shifting a message in an adset after 2 failed shape-shifts in a row, or when the message's combined ROAS is ≥ 20% below its peak. It can still travel elsewhere via J1.

**Measured per jurus:** delivery rate · hit rate · time to live · winner lifespan · lineage green spend (J3: green spend of the J3 winner plus all its J1/J2 descendants). Targets come from the backfill baseline (history is tagged by inference: same code in a new persona/language ≈ J1, same headline in a new form ≈ J2, new code and new headline ≈ J3).

Future jurus (J4…) and non-creative moves (store page, settings, offer) get added the same way, with their own owner.

---

## 6. Verdicts, clocks, and safeguards

### 6.1 At-bat
New concepts entering an adset in the same week (their first week with spend there), once the adset is 3+ weeks old: launch weeks are not refreshes. Variants of one concept count as one concept.
- **3+ variants per adset** (since 1.2.1): every at-bat lands in each adset with at least 3 variants of its concept (hook sub-types, text, re-cuts, V2 re-orders; a different opening scene is a new code). A new concept with 3+ spending variants became the adset's #1 40% of the time, vs 15% with 1–2. Where the queue shows a proven concept from a sibling adset (J1), add it: no production cost, and proven concepts win more often (28% vs 19%).
- **Context:** *turnaround* if the adset was under the green bar of its ruler the week before; *challenger* if it was on green.
- One concept in many adsets = many at-bats, which builds the concept × persona fit matrix.
- Counted by the engine when the adset spent $1k+ that week and the concept $20+ (`ATBAT` in `engine/settings.py`).

### 6.2 Verdicts: provisional at week 1, final at week 4 (since 1.2)
| Verdict | Rule | Adset strike | Next move |
|---|---|---|---|
| **Home run** | one of its concepts became the adset's #1 within 4 weeks, and the adset's relative ROAS at weeks 3–4 ≥ the 2 weeks before | 0 | close the ticket · start the decay clock · queue Amplify (J1) |
| **Hit** | #1 within 4 weeks; adset ROAS didn't rise | 0 | close the ticket · J2 on the winning message · watch the adset |
| **Late hit** | #1 only in weeks 5–12 | removes the strike | logged as a late bloomer |
| **Strike** | no #1 within 4 weeks, turnaround context | 1 | next at-bat (after the week-1 read, not the week-4 verdict) |
| **Foul** | no #1 within 4 weeks, challenger context | 0 | counts in people and concept records only |

**Week-1 read (provisional):** 20%+ of adset spend = provisional hit (79% go on to become #1). Under 20% = provisional strike or foul, and the ads stay on: they cost little, and about 1 in 8 entries under 5% still becomes #1 (a third of refresh winners started that way).

**Why not the new ads' ROAS:** within a week an ad's ROAS sits near its adset's (#1 vs the rest 1.03–1.11×), so it can't separate creatives. The adset after the takeover can: fast winners (20%+ in week 1) lift its relative ROAS +7% at weeks 3–4, vs −5% with no new #1, and every lift fades by weeks 5–6 (the decay clock, §6.7). All comparisons are relative (same OS, same week), so a measurement switch can't distort a verdict.

### 6.2b Refresh read: the early call on every refresh (since 1.3.3)
Measured per adset from the day the batch first spent there (daily ad rows), against the 7 days before.
| Read | New creative in the adset's top 3? | Adset ROAS after vs before | Strike | Ticket |
|---|---|---|---|---|
| **Worked** | yes | up, and at the bar (0.40+) | resets | closes when the read holds; watch week 2 |
| **Almost** | yes | up, still under the bar | no | stays open: swing again (weight 0.7) |
| **Flat** | yes | moved less than 0.02 | no | stays open: swing again (weight 0.7) |
| **Worse** | yes | down | **yes, any context** | fix first (weight 1.0) |
| **Miss** | no | under the bar | yes in a turnaround, foul otherwise | stays open: a different concept |
| **Miss (left)** | no | at the bar | no | leave it: no Due ticket while old creatives carry it |
"Top 3" counts the batch's ads per concept, apart from older ads of the same concept, so new variants of a running concept count as new. A relaunched adset with no week before is Worse when it lands under the critical line. The week-4 verdict (§6.2) still decides hit / late hit for records; the read decides strikes and tickets while the at-bat is provisional.

### 6.3 Turnaround and three strikes (since 1.2)
- The turnaround starts when an adset goes under green (a Decaying ticket). At-bat 1 within a week; each next at-bat follows the previous one's week-1 read.
- **Strike 3 = 3 turnaround strikes in a row** (provisional strikes count; a late hit removes one; 2 weeks back on green resets the count). At the turnaround hit rate (43%) three misses in a row happen about 1 time in 5 by luck alone, so Review is a check, not a verdict on anyone. Raising the hit rate (3+ variants, J1 additions) is what makes three strikes mean more.
- **Review protocol (§20.6):** the ticket goes to REVIEW, pinned on top. The failure signature of the three at-bats shows which link broke: execution, message, the ticket call itself, or something beyond creative (§6.4). No blind fourth refresh. Then decide: new jurus, budget hold, structure change, or retire.
- **The first job is the second swing.** Only 29 of 125 turnaround at-bats came after a miss, and 16 of 20 v8 adsets switched off got no new concept in their last 6 live weeks. An open ticket stays in the queue until it gets its swings.
- **Retire only with an obituary.** The row stays greyed with that note.

### 6.4 Check beyond creative
Spend arrives but ROAS won't follow. Claude checks: measurement (did a ruler change? §3.3) · demand/seasonality (same persona, language, account down together?) · store page (C>I vs. own peak and persona average, same era only) · post-install funnel (I>P vs. baselines) · settings (budget, bid, geo changes near the decline) · audience mix (country breakdown request). Output: likely cause and which owner takes the next at-bat.

### 6.5 Market day: protect against blaming creative
If more than half of alert-floor spend sits in adsets whose ROAS fell ≥ 15% in the same period, the cause is probably market or platform (seasonality, an iOS or Meta change, a tracking break). Then:
- the update opens with a 🌧 banner for the media buyer
- turnaround clocks pause for one period
- slates continue with normal priorities, without panic-refreshing everything
- if the cause is a measurement change, the bar is restated the same week (§3.3 rule 5) and nobody cuts budgets on the old reading. The 23 Feb, 9 Mar and 16 Mar 2026 market days were the Singular switch

### 6.6 Low ceiling: protect capacity
An adset or persona whose best 4 weeks in the last 6 months never reached the green bar of their ruler, and never matched its OS average over the same weeks, at alert-floor spend, gets 🧱. It gets no Defend slots; it can only receive Explore at-bats or a retire decision. Rescue capacity goes where a profitable past proves it's possible.

### 6.7 Decay clock
Winner lifespan = weeks a concept stays an adset's #1 spender (median per adset and persona, from backfill; default 3 weeks). A **Due** ticket opens when the #1 concept's age ≥ lifespan − 1 week (2 weeks). Pulled forward by the top ad's C>I or hook rate down ≥ 20%, or CPM up ≥ 20% while ROAS holds.

### 6.8 Kills
A top spender (≥ 15% share) dropping to < 1% next period is a kill. Verdict: good if adset ROAS held/rose and spend held; bad otherwise. Media buyer confirms reason.

---

## 7. Hypothesis gate

No at-bat without a hypothesis. Claude drafts one for every slate item; the strategist edits or approves.

> **Lane:** Defend / Amplify / Explore · **Jurus:** J_ · **Source:** [concept code] · **Adsets:** [...]
> **Because** [evidence from the dossier] **we believe** [the change] **will** win 20%+ of the adset in week 1 and become its #1 by week 4, lifting the adset's relative ROAS,
> **because** [audience insight, in their words]. **If it fails:** [next move].

A detected batch with no hypothesis = **orphan at-bat**: listed in the update, and Claude writes a retroactive one (marked).

---

## 8. The slate: three lanes and the supply math

### 8.1 Lanes (8 persona slots a week, about 4 per slate; 1 slot = one persona's at-bats across its OS/language adsets)
| Lane | What | Default slots / week |
|---|---|---|
| **Defend** | Review → Refresh (critical, amber and falling, leading signal) → Due, by ticket score (§20.1) | 5 |
| **Amplify** (protected) | Spread a fresh hit (J1) within one slate of the verdict, to flagged adsets first when the fit exists | 2 |
| **Explore** (protected) | J3 research from the persona library signals | 1 |

- Defend may borrow the Explore slot for at most one week in a row. Amplify is never borrowed: spreading proven winners is the fastest way to scale and often the best defence.
- 🧱 low-ceiling adsets don't enter Defend.
- **Overflow is listed in every update:** flagged personas that got no slot.

### 8.2 Supply math (in every Monday update)
- **Live winners** per persona: concepts with ≥ 15% of their adset's spend at ROAS ≥ the green bar.
- **Due to expire** in the next 2 weeks: live winners whose age ≥ lifespan − 2 weeks.
- **At-bats needed** = winners due to expire ÷ measured hit rate (per jurus mix).
- **Gap** = at-bats needed vs. slots available. A persistent gap is the evidence for more designers, more AI production, or fewer, broader adsets.

---

## 9. Scorecards: designers, strategists, Claude (since 1.2)

- Every at-bat is credited to the strategist and designer in the ad name (v5). Before v5: designer from the Notion tracker (brief code + batch joins 267 of 423 briefs to ads); strategist unknown.
- **Designer:** productivity (weighted output per week from the handoff counts, start → finish days) · execution (hook, hold and CTR against sibling executions of the same concept, plus quality flags from retros: too AI, off-brief) · outcome (delivery and hits on their at-bats against the expected rate for that ticket type and context).
- **Strategist:** hypothesis answered (yes / no / not testable, from retros) · hits against expected · briefs grounded in a logged signal (a J1/J2 source or a persona signal) · learnings logged.
- **Claude:** ticket calls (did adsets it flagged Refresh or Due decline when nothing new won, vs adsets it didn't flag) · predictions (every brief carries a hit probability; scored for calibration) · its proposed concepts vs people's proposed concepts (hit rate) · drafted learnings overturned in retros.
- **Rewards and penalties map to things we can see:** spending = delivery · good ROAS = the adset's lift after takeover · good CTR and hold = execution vs siblings · didn't answer the hypothesis, too AI, bad quality = retro flags · not based on insight = brief without a source signal · spending at weak ROAS = noted, not penalised.
- Records are shown per jurus and context (turnaround / challenger) and always with counts. **No ranking of anyone with fewer than 10 at-bats in the window.** The three main designers are within noise of each other (22–30 concepts with results each), so execution and productivity carry the card until outcomes have the numbers.
- **Read hit rate together with volume.** Winners produced matters more than hit rate. Playing safe lowers discovery. A safe copy Meta won't spend on is a full strike or foul. Intended.
- At-bats on Review tickets are tagged **rescue** and shown separately.
- Records are for monthly coaching, not weekly judgement. Feedback happens in the retrospective (§20.4).

---

## 10. Rhythm

| When | What |
|---|---|
| **Mon** | Upload (full week) → validation → verdicts on Thursday-live at-bats · statuses · supply math · **Slate A** with drafted hypotheses and briefs → 20–30 min slate meeting |
| **Tue** | **UA meeting:** the Tuesday report (§20.7), generated Monday and edited by the creative lead |
| **Tue–Thu** | Design (2–3 days) → Slate A live Thursday |
| **Thu** | Upload (Mon–Wed) → verdicts on Monday-live at-bats → **Slate B** → short slate meeting |
| **Fri–Mon** | Design → Slate B live Monday |
| **Monthly** (1 h) | Persona bibles (3 learnings each) · records per jurus (coaching) · retire-or-rescue on Review tickets and 🧱 · resurrection candidates · threshold calibration · reminder to drop new reviews |
| **Every Monday** | **Money check** (since 0.8): App Store proceeds vs Meta-credited iOS revenue, proceeds per iOS ad dollar, US proceeds vs US delivery. Shown on the Why ROAS fell tab |
| **On any measurement change** | Restate the bar the same week (§3.3 rule 5); no budget cuts on the old reading |
| **Quarterly** (30 min) | **Profit check:** does ROAS ≥ the green bar at 7-day click still mean payback everywhere? Compare Meta-claimed vs. store-reported revenue for the top countries, and OS vs. OS. Adjust the bar per segment if the evidence says so |

---

## 11. Team

- **Strategists (2):** share all 18 core personas for now. The engine watches every persona every upload, so nothing can fade silently even with shared ownership. They approve slates, edit hypotheses and briefs, confirm jurus, and add the creative taste.
- **Designers (4):** ≈ 8 persona slots a week. May specialise by jurus (fast J1/J2 vs. J3); records are per jurus, so that's fair.
- **Media buyer:** budgets and settings; confirms kills and budget-change reasons; owns 🌧 market-day checks and non-creative at-bats.
- **Claude, assistant strategist:**
  - each upload: validate data and names · statuses, clocks, supply math · verdicts · draft slate (lane, jurus, adsets) · draft hypotheses · draft one-page briefs from the persona bible and winners · request assets
  - maintain bibles: auto sections every upload, proposed learnings monthly
  - draft obituaries for retire decisions
  - remind the team about uploads (twice weekly) and reviews (monthly)

---

## 12. Outputs

**Dashboard pages (since 0.9):** Overview · Markets · Adsets & personas · Creatives · Diagnosis · Data checks. Each page answers one question of §0.
**Channels (since 1.1):** spend by channel and OS vs App Store money · each channel's own ROAS over time · TikTok value with and without spend · App Store money per iOS $ by channel (several models) · countries by channel · TikTok ad groups against TikTok's own average.
**Diagnosis (since 1.0):** (1) what the switch moved and what it didn't · (2) App Store money · (3) decisions made on the new ruler: spend path, budget moves per era, launches per month, adsets switched off while at or above their OS average · (4) every key finding on all weeks vs Singular weeks only, with a verdict · (5) the US · (6) what we ruled out · (7) funnel steps within the Singular era.


| Output | Status | Content |
|---|---|---|
| **Dashboard page** | v1, creative lead only (screen share) | Grid, views, dossiers |
| **Action update** | v1 as a file after each upload; Slack later | (1) 🌧 banner if any · (2) Critical and Review tickets · (3) verdicts, one line each · (4) slate by lane: adset · problem · jurus · owner · due · (5) supply gap and overflow · (6) orphan at-bats, naming errors, data issues. Nothing to do → one line |
| **Google Sheet** | later | Slate & at-bat log (hypothesis, lane, jurus, source, owner, verdict, learning) |
| **Ticket queue** (since 1.2) | engine: `tk_queue.csv` every run; live on the **Creative Board** (https://claude.ai/artifact/MFtoxXwScrbATaY5jNhv2U), a shared Claude page: Queue · Board · People · Signals; page source in `tools/ticket-board/board.html` | One ticket per adset needing creative, ranked; state; current #1 and reign; challengers in test; strikes; J1 candidates; past #1s; brief-with siblings (§20) |
| **Tuesday report** (since 1.2) | generated each Monday | Team output · last week's results · new personas · expansion · refresh & iteration · TikTok · this week's queue · money check (§20.7) |

---

## 13. Persona library

> Since 1.3 the persona library is `brain/minds/` (one mind per persona × language; see `contracts/mind.md`). The text below is the original design, kept for reference.

One folder per core persona inside the project folder, not a separate tool.

```
personas/LatinaFemaleLover/
  bible.md     ← one page, read before every brief
  winners/     ← hook frame + thumbnail per winning concept, Drive link, peak numbers
  voice/       ← their words: reviews, ad comments, survey answers, organic quotes
  signals/     ← J3 queue: competitor ads, organic trends, link + date found
  research/    ← deeper notes when a J3 needs them
```

**bible.md:** auto section (status, peak, current winner and age, lifespan, hit rate per jurus) · who they are · pains and desires in their words · what wins (with lineage) · what fails, don't repeat · fatigued messages and where they could still travel · open J3 hypotheses · obituaries.
Rule: only what feeds a brief goes in. Videos stay in Drive.

**Living, and readable by anyone (since 1.2):** auto sections refresh every run (status, current winners and their age, days since last new winner, hit rate per jurus, proven messages); learnings confirmed in retros are appended with the date and the at-bat they came from. The 27 Notion persona cards seed the bibles once their names are mapped to the v8 taxonomy (§19 Q22). The dev team and anyone else reads a published copy; the folder stays the source.

---

## 14. Where it runs

A git repo, run by a coding agent or a Claude session with the repo (Codex reads `AGENTS.md`; Claude reads `CLAUDE.md`, which points to the same file). Since 1.3 the layout is:
```
bumpy-creative-os/
  AGENTS.md · ARCHITECTURE.md · README.md · CHECKPOINT.md · requirements.txt
  core/        spec (this file), naming-adset-v8.md, naming-ad-v5.md, team.csv, minds.csv, decisions.md
  contracts/   shared formats: mind, history, creative, experiment, state
  brain/       minds/<Persona>-<LANG>/ (mind.md, history.md) · creatives/ · experiments/
  state/       queue.json, week.json (this week)
  data/raw/    every export, compressed, never edited
  engine/      run_all.sh, settings.py and the Python steps; README.md = weekly routine and data rules
  tools/       brainstormer/ · ticket-board/ · report/ · dashboard/
  checks/      validate.py (runs on every push)
  reports/     <week>/report.json and the PDF
```

---

## 15. Thresholds (single place to tune)

| Parameter | v0 |
|---|---|
| Zones, Meta's own attribution (to 22 Feb iOS, 8 Mar Android) | green ≥ 0.50 · amber 0.40–0.49 · critical < 0.40 · deep red < 0.35 |
| Zones, Singular (from 23 Feb iOS, 9 Mar Android) | **acceptable ≥ 0.40 · refresh warning 0.32–0.39 · critical < 0.32 · deep red < 0.28** (set 27 Oct by the creative lead) |
| Relative zones (toggle) | vs own OS that week: green ≥ 1.00 · amber 0.85–0.99 · critical 0.75–0.84 · deep red < 0.75 |
| At-bat | new concepts entering an adset in one week; adset 3+ weeks old, $1k+ that week; concept $20+; **3+ variants per adset**, plus a J1 concept when the queue has one |
| Week-1 read | ≥ 20% of adset spend = provisional hit; under = provisional strike (turnaround) or foul (challenger) |
| Hit (final) | one concept became the adset's #1 within 4 weeks; home run if the adset's relative ROAS at weeks 3–4 ≥ the 2 weeks before |
| Late hit | #1 in weeks 5–12 (removes the strike) |
| Strike 3 → Review | 3 turnaround strikes in a row; reset by a hit or 2 weeks back on green |
| Ticket priority | weight × last week's spend: review 1.0 · critical 1.0 · amber and falling 0.8 · leading signal 0.6 · due (#1 in reign week 3+) 0.5 (+0.1 if falling) · amber 0.4 · critical under the alert floor 0.3; × 0.5 with a challenger in test or 🧱; no ticket under $300/week (proposed 27 Oct) |
| Market day | > 50% of alert-floor spend in adsets with ROAS down ≥ 15% together |
| Low ceiling | best 4 weeks in 6 months never ≥ green bar of their ruler at alert-floor spend |
| Live winner | ≥ 15% of adset spend at ROAS ≥ green bar |
| J1 freshness | source hit within 4 weeks |
| J2 stop | 2 failed shape-shifts in a row, or message ROAS ≥ 20% below peak |
| Kill | ≥ 15% share → < 1% next period |
| Alert floor | adset spend ≥ 1% of account spend |
| Shrinking | 2 budget cuts in a row, or ≥ 30% below 6-month peak |
| Under-delivery | spend < 85% of budget |
| Default lifespan | 3 weeks (measured: median reign 3 weeks; ROAS slides from week 3); Due ticket from reign week 2 (1 week to make, 1 to read) |
| Leading signal (stand-in) | green adset's IPM or hook rate ≥ 20% below its prior 4-week average → Falling (a Decaying ticket) |
| Scaling (stand-in) | spend ≥ 15% above 2 weeks ago, until budget history exists |
| Low ceiling | needs a 4-week window at alert-floor spend; flagged only if it never reached the green bar and never matched its OS over the same weeks |
| Measurement eras | switch weeks iOS 23 Feb 2026, Android 9 Mar 2026; switching window to 15 Mar; set in `engine/settings.py` |
| TikTok live ad-group week | spend ≥ $20 that week; value on other weeks = "value without spend" |
| TikTok ad-group status | vs TikTok's own OS average, last 4 weeks: ≥ 1.00 at/above · 0.85–0.99 · < 0.85 |
| Lanes | Defend 5 · Amplify 2 · Explore 1 (of 8 slots/week) |

---

## 16. Known limitations

- Meta-reported ROAS (7-day click) is for fast relative decisions, not proof of incremental revenue; the quarterly profit check is the counterweight.
- Meta's numbers are only as good as what Singular sends it. Singular reports campaigns, not adsets, so adset judgement stays on Meta's (smaller) number. The Singular undercount may differ by country (US traffic reads 0.89× the rest inside the same worldwide iOS adsets, was 1.05×).
- Android money can't be checked until Google Play or Singular revenue arrives (about 40% of spend).
- TikTok: no ad-level data yet (no creative view); its spend moves less than Meta's, so the store-money estimate per TikTok $ is imprecise (± $0.12); its credited value includes renewals posted to idle ad groups.
- Survivorship bias in the backfill.
- Thursday verdicts are early reads; re-checked Monday.
- A verdict shows what happened after an action, not proof it caused it; trust patterns across many at-bats.
- Pre-v5 ads have no strategist; designers come from the Notion tracker where the brief code + batch matches (267 of 423). Jurus tags on history are inferred.
- At-bats are counted only in adsets spending $1k+ that week, so refreshes of small adsets don't show in the back-test, and capacity (about 8 a week) counts only refreshes of established Meta adsets: new adsets, TikTok and non-ad work aren't in it.
- Strike-to-person attribution is a coaching aid: the ticket call, the brief and the execution share every outcome.

---

## 17. Parked

- Country revenue as a dashboard tab (the quarterly check covers the need for now).
- TikTok / Google, same structure.
- Non-creative jurus.
- **Structure test, for the media buyer:** a few broader adsets per language/OS where the creative carries the persona, run side by side with persona adsets. The engine already reads persona from ad names, so reporting survives either way.
- Slack delivery. (Team access moved into scope with the Tuesday report and the board, §19 Q17.)

---

## 18. Legacy mapping

New v5 ads need none. For older ads Claude maps by judgment and asks when unsure; confirmed mappings are added here.

| Ad persona (legacy) | Canonical (v8) |
|---|---|
| ChurnRaya | CelebrityCrushLookalikeLover |
| LatinaLover | LatinaFemaleLover |
| *(filled from the first upload)* | |

| Ad `audiencecode` | Adset `Language` |
|---|---|
| US | EN |
| other | same code |

---

## 19. Open questions

1. Profit bar: is 0.50 at 7-day click meant to be the same payback on iOS and Android and across languages? Is there any cohort revenue (D30/D60) by OS or country from finance/BI to calibrate it?
2. The brief-writer skill referenced in the naming doc: where does it live? Claude's draft briefs should follow it.
3. ~~What changed in late Feb – mid Mar 2026?~~ **Answered 23 Oct: the move to Singular (MMP).** Still to confirm: the exact switch dates per OS (the data says the weeks of 23 Feb iOS and 9 Mar Android), and what changed in the iOS click path in the same week (clicks per impression +26%, click → install −34%): tracking link, landing page, or custom product page?
4. Persona taxonomy: add or rename `IntlFriendFinder`, `LatinoMaleLover`, `ChatOnly`, `SexyFemaleLover`, `SexyBeachGuy`, `SoutheastAsianFemaleLover`, `AttractiveBlackFemale`, `AsianMaleLover`, `InstagramPost`, `Translation`, `InterlocalDating`, `BrandTest`?
5. ~~Next export: add budget and send the ad-level file.~~ Received 23 Oct (budget columns included, current value only). Keep both in every upload, starting on Mondays (§3.1).
6. ~~Confirm the Singular bar~~ **Set 27 Oct:** acceptable from 0.40, refresh under 0.40, critical under 0.32. The real profit bar (what a subscriber is worth after the first weeks, from Singular D30 / finance cohorts) stays the long-term answer (Q1).
7. **US test.** Restore a US-only iOS adset at about the old budget for 3–4 weeks and watch US App Store proceeds against the current baseline. Partly under way: worldwide English adsets tripled US iOS spend from June to September and US proceeds rose about $8k a week. A US-only adset makes it a clean read.
8. **Change log.** Singular explains 23 Feb / 9 Mar. Anything else in those weeks (app release, paywall, price, attribution setting, Meta conversion mapping)? From now on, log every such change in `core/decisions.md` the week it happens.
9. ~~Adset × country weekly export~~ received 23 Oct. Still missing: Google Play earnings by country.
10. **Singular → Meta check.** Which Singular events and values are sent to Meta as Purchase (gross or net, first purchase only or renewals, currency, SKAN / AEM for iOS)? MaxValue bidding learns from those values, so a mapping gap would change who Meta finds, not just what it reports. Proceeds per iOS $ held, so there's no sign of harm yet.
11. **Singular export** by campaign × country × OS × week, with D7 / D30 revenue (§3.1 G). Ask Singular whether Meta adset (sub-campaign) breakdowns are available for any traffic, e.g. Android.
12. **The May – June spend pullback** (about $120k/week vs $160k before): was it a reaction to the ROAS reading? If yes, record it as a decision made on the old ruler, and set the profit bar (Q1) before the next account-level cut.
13. **TikTok geo test.** Pause TikTok iOS for 4 weeks in 3–4 countries where it is a large share (e.g. Philippines, Indonesia), compare App Store proceeds with similar countries. Until then, hold TikTok at today's budget.
14. **Why does Singular post value to TikTok ad groups that stopped spending in 2024–25?** Check the TikTok postback settings in Singular (revenue events, renewals, re-attribution window). Meta shows none of this.
15. **TikTok ad-level export with v5 ad names**, so TikTok creatives join the concept relay and cross-channel J1 (a Meta winner tried on TikTok and the other way round).
16. What broke TikTok Android purchase reporting from 9 Feb to 8 Mar?
17. ~~Board home~~ **Answered:** a shared Claude page; designers and strategists get access.
18. ~~Scorecard visibility~~ **Answered:** everyone sees everyone's card.
19. ~~Roster codes~~ **Answered:** Yuli Nur Hakim = KIM, Hanna Dolhikh = HAN; Deyan Haider and Hussein Saleh Cabrera have left. Strategist per batch before v5 stays unknown.
20. **Exports without hands: yes**, into a Drive folder or the creative lead's own folder. Weekly inputs: Meta adset × country and ad level (with the §3.1 columns), App Store proceeds by country, Google Play by country, TikTok, and signals from the wild (IG, TikTok, ad library). Folder still to set up.
21. **Watch-time columns** in the ad export: ThruPlays and video plays at 25/50/75/95/100% (§3.1 B).
23. **A permanent home for raw exports and the engine.** Today they live in a temporary cloud workspace and the zip copy. Proposed: a folder on the creative lead's Mac (e.g. Documents/Bumpy Ads) linked to Claude, or a Drive folder; every weekly export is kept there forever.
22. **Persona cards → taxonomy.** The 27 Notion cards use other names ("Gringo Lover from Brazil", "40+ Singles Second Chance", "BLK"…); confirm the mapping to v8 personas.

---

## 20. The operating loop (since 1.2)

The ticket is the spine. The board (who works on what), the Tuesday report (what happened), the scorecards (who moved the needle) and the persona files (what we learned) are views of tickets. Ad names generated at brief time are the join key from ticket to Drive to export to verdict, so status moves itself.

### 20.1 Ticket = one adset; at-bats inside
One ticket per adset that needs creative. Its initiatives are at-bats (§6.1). One brief can serve several tickets: the same persona and language on the other OS (`brief_with`).

| Type | Opens when | Lane |
|---|---|---|
| **Decaying** | ROAS under the bar (critical under 0.32); or under it and falling; or on green with IPM / hook rate down 20%+ | Defend |
| **Due** | healthy, but the #1 concept is in week 2+ of its reign (a refresh takes ~1 week to make and ~1 to read) | Defend |
| **3 strikes** | 3 turnaround strikes in a row (pinned on top) | Defend |
| **Resurrection** | an adset switched off while at or above its OS average, or a persona gone dark with a profitable past | Explore |
| **New persona · Expansion · New format or channel** | opened by a person (new language or market; AppLovin / AXON, Google 30–60 s, Snapchat, TikTok) | Explore / Amplify |
| **Urgent fix** | opened by a person (broken asset, policy, tracking) | — |
| **Non-ad work** | opened by a person (ASO sets, onboarding videos); productivity only, no verdict | — |

**Ranking:** weight × last week's spend (§15). A challenger already in test halves the score; so does 🧱. The cut line is capacity: about 8 refresh at-bats a week today, against 66 tickets that need a brief. The gap is the case for more output per brief (one concept with 3+ variants into the iOS and Android adsets together, plus J1 additions), more production, or fewer, broader adsets.

### 20.1b One brief, many tickets (since 1.2.2)
- **The brief is the production unit; the adset is the measurement unit.** A brief has one concept, one hypothesis, one strategist, one designer, and covers any number of tickets. The strategist decides the group: usually one persona across its languages and both OS; sometimes another persona that shares the insight. Due adsets can ride a brief made for their Decaying siblings at no extra production.
- **Names:** one set per persona × language covered; each adset gets 3+ variants in its language.
- **Verdicts stay per adset.** Each covered adset gets its own week-1 read and week-4 verdict; the brief shows "won N of M adsets". A strike still lands on each turnaround adset that missed.
- **Reading a brief's result:** won in some languages but not others → a language or market fit, a localisation learning; missed everywhere → the concept or execution; won everywhere → spread it (J1).
- **Hypotheses** name where the concept should work ("in Latina adsets, strongest in ES"); the retro says where it did.
- **Scorecards count briefs, adsets covered and files**, so a designer on one six-adset brief isn't compared to one on six one-adset briefs by ticket count. Outcome = landings won vs the ~20% per-landing baseline; "won anywhere" is never compared across briefs of different spread.
- **Queue:** "By persona" view groups tickets with combined spend; the strategist ticks the adsets and briefs them in one go.

### 20.2 Statuses and who moves them
| Status (per at-bat) | Moved by | How |
|---|---|---|
| NEED REFRESH | engine | ticket opens (or a person opens a manual type) |
| BRIEF CREATED | strategist | accepts Claude's draft; ad names, Drive folder and file names are generated (v5 naming) |
| IN PRODUCTION | designer | picks it up; start date stamped |
| READY TO UPLOAD | designer | 30-second handoff: Drive link + production counts in the tracker's 10 task types; finish date stamped |
| TESTING | engine | first export where the generated ad names spend |
| RESULT READY | engine | week-1 read, then week-4 verdict; opens the retrospective |
| RETIRED | engine / person | ads off, or obituary written; post-mortem in the persona file |

The ticket closes on a hit or home run and stays open through strikes.

### 20.3 Brief: drafted from the ticket
Claude drafts; the strategist edits and accepts. Inputs: the adset's dossier (status, reign, past #1s and why, ROAS / CTR / IPM / hook week to week); J1 candidates (concepts winning in the same persona or language that never ran here); J2 material (this adset's past #1 messages); the persona file (proven messages, what fails); the creative audit (format gaps by content style, message theme, hook type, format, spokesperson; Gemini notes with timestamps); human inspiration (ad library, social). Output keeps the team's brief format (task, benchmark, hook and scene specs, anti-AI cues, per-variant ad names, task weight) and adds the hypothesis (§7) and Claude's hit probability.

### 20.4 Retrospective at RESULT READY
Feedback happens when the result arrives, with strategist and designer together. Claude pre-fills the verdict, the delivery path (week-1 share → #1?), the funnel against sibling executions (hook, hold, CTR, C>I, IPM), the adset's ROAS after, and a drafted learning. People confirm: hypothesis answered (yes / no / not testable), execution flags, and the learning in one line. Confirmed learnings go to the persona file and the experiment records (`brain/experiments/`).

### 20.5 Scorecards
See §9. Monthly coaching, counts always shown, history kept per person (tickets taken, at-bats, verdicts, productivity).

### 20.6 Review: whose link broke
The three at-bats' failure signature:
- **No delivery**, hook / hold below sibling executions → execution (designer) or concept (strategist).
- **Delivery, but the adset's ROAS didn't follow**; C>I or I>P off → message or audience (strategist), or beyond creative (§6.4: store page, measurement, bot clicks; e.g. iOS CTR 2.97% with C>I 0.05).
- **The adset was 🧱 or the market moved** → the ticket call (Claude, media buyer).

### 20.7 The Tuesday report
Lives in the board's **Report tab** (since 1.2.4): `engine/report.py` writes `output/board/report_<adset week>.json`, the weekly sync puts it in `reports/<adset week>`; the presenter's edits live in `report_notes` and are never overwritten. Generated each Monday after the exports, in the order of the team's deck, with Claude's drafted insight and action items for the presenter to edit:
1. **Team output:** videos, images, ASO sets by initiative type, with the concept breakdown (handoff counts), adsets covered, and who worked on what.
2. **Last week's results:** the summary first (at-bats landed, provisional hits, final verdicts, home runs, strikes, late hits), then one card per initiative: an Ads Manager-style table per OS adset (spend, CTR, C>I, IPM, ROAS), annotations, top creatives (thumbnails from Drive by ad name), learning, action item.
3. **New personas · Expansion · Refresh & iteration · TikTok** (other channels as they join).
4. **This week's queue:** tickets above the capacity line, Review tickets, resurrection candidates, decisions needed from the UA team.
5. **Money check** in one line: spend by channel, App Store proceeds, the bar.
Every number links back to the dashboard view it came from.

### 20.8 Persona file
Living and readable by anyone (§13).

### 20.10 Where history lives (since 1.2.3)
| Layer | Where | What | Written by |
|---|---|---|---|
| Work and experiments | board database: `work`, `signals`, `manual`, `team` | every brief (hypothesis, move, tags, people, adsets covered, generated names, status history with dates, handoff counts, per-adset results, retro) | the team; Claude adds results and signal numbers only |
| History | board database: `history/<week>`, `engine/log`, `engine/archive`, `engine/personas` | a copy of each week's queue; every refresh since Dec 2025 with its verdict; one row per week; the Notion tracker and persona cards | Claude, each Monday; never overwritten, only added to (except the current week) |
| Current state | board database: `engine/queue`, `engine/people`, `engine/codes`; the analysis dashboard's datasets | this week's tickets, roster and history scorecards, codes in use; the dashboard's tables | Claude, each Monday |
| Reports | board database: `reports/<week>`, `report_notes` | each Tuesday report as generated, and the presenter's edits | Claude (reports); the team (notes) |
| Rules and decisions | Claude project: spec, decisions log, board guide | every rule, threshold, decision and its evidence | Claude, when a rule changes |
| Raw data and engine | a permanent folder (§19 Q23) | every export ever received (never edited) and the code | the team drops exports; Claude runs the engine |

The engine recomputes every at-bat and verdict from the raw exports each week, so the refresh history can always be rebuilt as long as the exports are kept.

### 20.9 Signal bank
Anyone pastes a link (TikTok, Instagram, ad library, YouTube…) with an optional note and any number of personas. Claude fills the numbers on the weekly run where the page shows them (views, likes, comments, shares, saves; days running for ad-library links), and people can type them when a site hides them. Sort by views, likes, shares, comments, engagement ((likes + comments + shares + saves) ÷ views) or run length. Signals tagged with a persona appear in its tickets and in Claude's brief drafts, and briefs record which signal they used.
