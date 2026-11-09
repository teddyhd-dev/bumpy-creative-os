# Weekly report: house style

Taken from the team's Canva deck ("Reporting Bumpy", weeks 34–36 2026). The PDF generator follows this;
the strategist can still edit the drafted words before it goes out.

## Format
- 16:9 slides, 1440 × 810. Exported as one PDF per week: `reports/<week>/Bumpy-Creative-Report-Week<NN>.pdf`.
- Build-up slides: the same slide repeats with the annotation, then with the action items added (the deck
  reveals in steps). In the PDF, keep the build-up for the key slides only.

## Colours
| Use | Hex |
|---|---|
| Bumpy sky blue: cover panel, agenda title, "action items", new-persona tiles | `#53AFD4` |
| Orange: highlight boxes on tables, bracket lines, refresh tiles | `#FC6E3D` |
| Dark plum: Top Creatives and refresh-showcase slides | `#443A40` |
| Grey: format / other tiles | `#747275` |
| Text on white | near-black; slide background white `#FFFFFF` |

## Type
- Headlines and section titles: **Quicksand Bold** (agenda numbers bold, labels regular).
- Body and annotations: **Open Sauce One** (Regular / Bold); table text small.
- Showcase titles on plum (e.g. "SUCCESSFULL REFRESH:"): a condensed bold sans in white, all caps.
- Fallbacks if a font is missing: Quicksand and Open Sans from Google Fonts.

## Slide types
1. **Cover:** full-bleed travel photo (airport, suitcase, plane window), sky-blue rounded panel with the
   Bumpy logo, "Week NN YYYY / Creative Reporting", "Teddy Dassa © YYYY".
2. **Today's agenda:** "TODAY'S AGENDA" in sky blue; numbered 01., 02., 03. with the section names.
3. **01. Team Output Update:** headline count ("44 Videos, 33 Imgs, 50 ASO"), then rounded tiles per
   initiative: tile colour by type (sky blue = new persona, orange = refresh, grey = format/other), an icon
   top-right, the initiative name, and the breakdown at the bottom ("Selfie: 9 Vids 9 Imgs").
4. **Section opener:** "02. NEW PERSONA REPORT", "03. REFRESH AND ITERATION", "04. TIKTOK INSIGHT".
5. **Result slide:** title with the verdict word ("02. Successful New Persona", "03. Good & Bad Expansion",
   "Mixed Result Refresh", "Unsuccessful New Persona"), subtitle = persona or initiative. An Ads
   Manager-style table (Ad set, Amount spent, CTR (all), C>I, IPM, Purchase ROAS; flags for language), an
   orange rounded box around the columns that matter, an orange bracket to a short right-aligned
   annotation ("mid-bottom funnel metrics look strong, however CTR wasn't"), then "action items:" in sky
   blue.
6. **Top creatives:** plum background, "TOP CREATIVES" (or "SUCCESSFULL REFRESH: RAW BIG TEXT + PHOTO"),
   three 9:16 phone thumbnails with a mini metrics strip under each (CTR, C>I, IPM, ROAS), gold / silver /
   bronze rank badges when ranked, and on the right "LEARNING/VALIDATION" plus "Action items".
7. **Findings / hypothesis slides:** big claim as the title ("FINDINGS: MOST SPENT WENT TO IMAGE WITH 0.00
   C>I"), supporting screenshots, a "Hypothesis:" block.
8. **Closing:** "Thank You:)".

## How the creative lead wants decks presented (Nov 2026, any deck)
- **One talking point per slide.** The headline is the sentence you say out loud; no paragraphs. Tables are fine.
- **General first, then detail:** a scoreboard, then one slide per persona, each followed by its action slide.
- **Colour carries the judgement:** ROAS pills (blue 0.40+, peach 0.32–0.39, red under 0.32), ▲/▼ for the move,
  verdict pills, NEW / NEW-OLD tags, a yellow pill for a #1 younger than 2 weeks. Never colour alone: the word is on the pill.
- **Action slides look different:** navy background, so the room knows the talk turned to actions. Owner first
  (Creative before Media buyer), priority pill, one sentence per action with the number that justifies it.
  Creative actions are per persona × language (one creative set goes to both OS); only media-buyer rows name the OS.
- **Audience words, not codes:** Friends, Gringo, Loc. Dating, Passport Bro; concepts by name (dreamlife, banner).
- **Sorting:** rows where the new creative made it first (best → worst), then the rest (worst → best), so the bad rows meet in the middle.
- Leave room for the creative lead's own verdicts: don't pre-fill a "your verdict" column.
- The launch review deck (Tuesday) follows `REFRESH-REVIEW.md` in full; the last one is in `reports/2026-10-26/deck/`.

## Voice
- Few words, big claim, then evidence. Annotations are short and casual (lowercase is fine, ":)" allowed).
- Every result ends in an action item.
- Numbers as in Ads Manager: $1,018.73, 0.95%, 0.24, 2.24, 0.84.

## Where the content comes from
- Numbers and result cards: `reports/<week>/report.json` (engine/report.py).
- Thumbnails: the first-second snapshots in `brain/creatives/img/` (saved during decodes).
- Learnings: experiment records (`brain/experiments/`) and the minds' history entries of the week.
