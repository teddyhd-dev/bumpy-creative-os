---
name: bumpy-brief-writer
version: 5.0.0
description: |
  Turns approved Bumpy headlines + a scene structure into Notion-ready, scene-by-scene
  creative briefs for designers and video editors, with v5 file names and task weight.
  Use when the user gives a headline/concept and asks for a brief, file names, or a
  designer handoff.
---

# Brief Writer Skill — Bumpy Creative Briefs
version: 5.0.0

> **Changelog v4 → v5 (Nov 2026):** file naming moved to the v5 convention (12 fields, adds `strategist` and `designer`), persona names now come from the closed Canonical Persona List, added the Mega-Brief rule (one file across languages, grouped by asset type), endscreen CTA is confirmed per persona, removed references to `bumpy-proximity.md` (retired; casting lives in `bumpy-casting-data.md`).
>
> **Changelog v3 → v4:** Concept Code Rule (concept = hook + structure), identity-first variant sequencing, per-variant benchmarks, Benchmark Matching Rule, baked-in vs. overlay asset reuse, endscreen is not "app UI", su_id + name casting, male relatability casting. All from real brief feedback, marked **[v4]** inline.

---

## What This Skill Does

Turns headlines into scene-by-scene creative briefs for designers and video editors.

Input: headline(s) + scene structure + angle + naming inputs
Output: one `.md` brief file per concept (or one Mega-Brief for multi-language sets), Notion-ready

---

## When to Use This Skill

- User provides headlines (from organic signals, competitor ads, user comments, or copy sessions)
- User provides a scene structure (even rough — "hook → profiles → video call → travel → endscreen")
- Headline stays the same but language or gender swaps across variants

---

## Concept Code Rule **[v4]**

**A concept is defined by its hook + video structure combined — not by its underlying visual assets.**

This means:
- If two creatives use 100% reused footage/casting but open with a **different hook** (different first 2 seconds), they are **different concepts** and need **different concept codes**. Meta/ad platforms read the first 2 seconds as the concept signature — reusing a code across two different hooks will corrupt analytics even if every other scene is identical.
- This applies even when the reuse is total: a brief that's just "old Airport Hug footage, now used as the hook instead of scene 2" still gets a brand new concept code, not a Version (V1/V2) of the old one.
- Re-sequencing the same scenes so each order opens on a different scene (e.g. 1-2-3-4, 2-4-1-3, 3-4-1-2, 4-1-2-3) = one concept per opening scene, each with its own code. Shared footage means no extra generation; only code count and video output go up.
- **Versions (V1/V2) are reserved for reordering the *same* hook's structure** — same opening 2 seconds, reordered scenes after it. If the hook itself changes, it is never a Version; it's a new concept.
- Multiple *hook sub-types* that open the same way conceptually (e.g. "Big Ticket" boarding-pass prop and "Fence Banner" — both are static command-style hooks with the brand named immediately) **can** share one concept code if the team wants unified reporting for that creative family — but confirm this with whoever owns Meta reporting before assuming it's fine, since it's a judgment call, not a hard rule.

---

## Required Inputs

Before writing any brief, Claude must have:

1. **The headline(s)** — exact copy, including emoji
2. **The scene structure** — order of scenes, even if rough
3. **The persona** — a name from the Canonical Persona List below
4. **The app name** — default is Bumpy
5. **Casting** — pull from `bumpy-casting-data.md` via `bumpy-casting-SKILL.md`. If no su_id data exists for a nationality, generate a full casting description instead (see Casting Guidance) — never leave it blank.
6. **Benchmark** — a TikTok/video URL or described visual reference. **[v4] One benchmark per variant/creative**, whenever a brief contains more than one visual hook type or more than one nationality. Ask if not provided.
7. **Concept name** — the visual hook family (e.g. "Fidgeting", "Mirror", "Banner", "Airport", "WakeUp"). **[v4] Keep it generic across sub-hook-types that share a code**; differentiate those in `[hook]`.
8. **Concept code** — 6-character alphanumeric, generated once per concept, reused across all variants of that concept.
9. **Batch** — `BatchYYYYWeekWW`, ISO week, two-digit week (e.g. `Batch2026Week07`). Ask if not provided.
10. **Strategist + designer codes** — from the Roster below. Ask if not provided. Never guess.
11. **Format** — Ask: "Video only, or will any scenes (e.g. the HOOK) also be delivered as static images?" If IMG exists → dual file names + IMG note on the scene.
12. **Versions** — Ask: "Do you want reordered scene sequence versions to reduce ad similarity score?" Only valid if the hook itself is unchanged (see Concept Code Rule).
13. **Endscreen CTA** — confirm per persona (see Brand Rules).

If any are missing, ask before writing — in one short message, one line per question.

---

## Mega-Brief Rule (multi-language / multi-market sets)

When one creative set spans several languages or markets, deliver **one file**, not one file per language. Designers edit in Premiere by visual: they finish every version of one asset type (all languages) before moving to the next, only swapping text. Separate per-language files force them to close the project and restart for each language.

Structure a Mega-Brief as:

1. **How this brief is organized** (3–4 lines at the top)
2. **Master casting & localization reference** — local casting per market, shared asset pools
3. **STEP 1 — GENERATION**, grouped by asset type (e.g. all Wanted selfies, then all Couple photos, then all Window scenes). Each asset generated once; mark where it is reused.
4. **STEP 2 — ASSEMBLY**, the final variants (file name + scene lines + text per language), using only Step 1 assets
5. **Task Weight** at the bottom

---

## Asset Reuse Rule: Baked-in Text vs. Overlay Text **[v4]**

Before assuming a scene needs fresh generation per language, check whether the on-screen text is **physically part of the visual** or just an **overlay caption**:

- **Baked-in / physical prop text** (boarding pass, painted banner, handwritten note) — **must be shot separately per language**, because the text can't be swapped without regenerating the image. If a reused clip has handwritten text and needs translating, flag it to production.
- **Overlay caption text** (POV caption, slider label, command line over a scene with no prop) — **shoot once per nationality, reuse across every language**.

Mark reused scenes explicitly: `— existing asset, reused from [source], no additional generation`.

Static IMG ads cut from video stills (same still + headline overlay) cost 0 extra generation; they only add to Image output.

---

## Variant Sequencing **[v4]**

**Sequence variant blocks by shared casting/visual identity first, not by language block.**

Wrong (language-blocked):
```
ES Colombiana, ES Venezolana, ES Brasileña, PT Colombiana, PT Venezolana, PT Argentina
```

Right (identity-blocked — same girl's ES and PT versions back-to-back):
```
Colombiana (ES → PT), Venezolana (ES → PT), Brasileña (ES only), Argentina (PT only)
```

Scenes that need no model at all (e.g. a fence/whiteboard text shot) are noted as such.

---

## Benchmark Matching Rule **[v4]**

Instruction to designers on every benchmark line: **match the benchmark's vibe, composition and energy, but change at least one element (pose, outfit color/detail, background prop, angle) so it looks similar side-by-side, not identical.** State it on every benchmark line, not once at the top.

---

## File Naming Convention **[v5]**

```
[persona]-[audiencecode]-[conceptcode]-[conceptname]-[hook]-[headline]-[angle]-[modifier]-[VID/IMG]-[strategist]-[designer]-[batch]
```

Exactly 12 fields separated by `-`. **Inside every field: letters A–Z and digits 0–9 only** — no spaces, hyphens, accents, apostrophes, emoji or non-Latin script.

**Examples:**
```
LatinaFemaleLover-ES-r4Tx9k-Banner-ColombianaFenceSign-noviacolombiana-recommendation-ProductAware-IMG-CAM-MAR-Batch2026Week42
AsianFemaleLover-US-Hp82mQ-Selfie-AsianWomanCarSelfie-dateasiangirlbumpy-recommendation-ProductAware-VID-TIN-004-Batch2026Week44
```

### Field definitions

| # | Field | What it is | Case | Example |
|---|---|---|---|---|
| 1 | `persona` | Canonical persona name (closed list below) | PascalCase | `LatinaFemaleLover` |
| 2 | `audiencecode` | Language of the on-screen text (table below). Never invent regional codes like `LATAM` | UPPERCASE | `ES` |
| 3 | `conceptcode` | 6 characters, once per concept (Concept Code Rule) | Mixed | `r4Tx9k` |
| 4 | `conceptname` | Generic visual family of the first frame | PascalCase | `Banner` |
| 5 | `hook` | Compact: who is on screen + what they do/hold. Sub-hook-types differ here | PascalCase | `ColombianaFenceSign` |
| 6 | `headline` | Short lowercase slug of the on-screen copy | lowercase | `noviacolombiana` |
| 7 | `angle` | From the Angle list below | lowercase | `recommendation` |
| 8 | `modifier` | Awareness stage | PascalCase | `ProductAware` |
| 9 | `VID/IMG` | Output format (carousel = `IMG`) | UPPERCASE | `VID` |
| 10 | `strategist` | From the Roster | 3 chars | `TED` |
| 11 | `designer` | From the Roster | 3 chars | `OST` |
| 12 | `batch` | `BatchYYYYWeekWW` (ISO week of launch, 2-digit) | as shown | `Batch2026Week42` |

Keep `hook` and `headline` short — two long descriptive fields make names far longer than production uses.

**Changes per variant (within one concept):** `[hook]` and `[headline]`. Everything else changes only with a new concept. For IMG versions of a variant, only `VID`→`IMG` changes.

### Roster (fields 10–11)

| Source | `strategist` | `designer` |
|---|---|---|
| Ad creative team | `TED` (Teddy), `JAC` (Jacqueline), `CAM` (Camile) | `OST` (Ostap), `HAN` (Anna), `USM` (Usman), `KIM` (Hakim), `MAR` (Marvon) |
| Social media | `CAM` | `MAR` |
| Creator program | `TIN` (Fatin) | creator code `001`, `002`… (assigned by the program, never invented) |
| TTO (TikTok One) | `TT1`–`TT4` (brief project) | `TTO` |

New strategist/designer → add to the roster before their first ad goes live.

### Audience codes

English `US` · Spanish `ES` · Portuguese `PT` · Indonesian `ID` · Thai `TH` · German `DE` · Japanese `JP` · Turkish `TR`. Any other language: ask. The code follows the **language** of the text, not the country (e.g. an Uzbek Muslim audience with Russian-language copy is `RU` with Uzbek casting — RU casting is still banned).

### Angles

`recommendation` (try it / highly recommend) · `pov` (POV / viewer's own moment) · `testimonial` (someone's own result) · `morethanyouthink` · `twoslide` (setup → payoff slide) · `timeline` (dated story) · `mythbreak` (kills a belief or another app's promise) · `celebcrush` (lookalike) · `friends` · `language`. If none fits, use a short lowercase word and flag it.

### Modifiers (judge from first-frame text only)

| Modifier | The text… |
|---|---|
| `Unaware` | Names no problem and no solution. Pure vibe/fantasy |
| `ProblemAware` | Names the pain, no solution |
| `SolutionAware` | Says dating abroad works, no brand |
| `ProductAware` | Names or shows Bumpy |
| `MostAware` | Names Bumpy + clear offer or direct CTA |

### Canonical Persona List (closed)

Never invent a persona name. If a creative fits none of these, or fits two, ask.

| Persona | Pattern | Old names it replaces | Typical gender |
|---|---|---|---|
| `GringoMaleLover` | Partner preference | Gringo Lover (BR/TH/ID/PH/LatAm) | Female |
| `AsianFemaleLover` | Partner preference | Asian Lover, Asian Dating | Male |
| `LatinaFemaleLover` | Partner preference | Latina Lover | Male |
| `SlavicFemaleLover` | Partner preference | Slavic Lover, Slavic Girl Lover | Male |
| `KoreanMaleLover` | Partner preference | Korea Boo (Male), Korean Guy and Culture Lover | Female |
| `MuslimMatch` | Shared identity | Muslim Dating, Muslim Match | Both |
| `ChristianMatch` | Shared identity | Christian Dating, Christian Worldwide | Both |
| `PassportBro` | Situational | Passport Bro | Male |
| `GirlWantsToRelocate` | Situational | Girl Who Wants to Relocate | Female |
| `MatureDating` | Situational | 40+ / Second Chance, Dating on 30-40+/50-60 | Both |
| `InterracialDating` | Situational | Black Women Interracial, Black Dating | Female |
| `SingleMom` | Situational | Single Mom | Female |
| `IntlFriendFinder` | Situational | International Friend (Finder) | Both |
| `LanguageLearner` | Situational | Language Learner | Both |
| `IndianMaleDream` | Situational | Indian Boy Dream | Male |
| `RichHusbandFinder` | Situational | Rich Husband Finder | Female |
| `LGBTQ` | Situational | LGBTQ+ | Both |
| `DatingFatigue` | Situational | Dating App Refugee, Angry with Local Dating, ChurnLocal | Both |
| `ChurnRaya` | Situational | Churn Raya | Both |
| `General` | — | Non-persona / infrastructure campaigns | Both |

---

## Casting Guidance **[v4]**

- Pull nationalities/profiles from `bumpy-casting-data.md` per `bumpy-casting-SKILL.md`.
- **When su_id data exists:** list it with a generated first name per card — e.g. `Valentina (su_id 23696965)`.
- **When no su_id data exists:** generate a full casting description per card — name, body type, hairstyle, outfit, background setting — enough for a designer to shoot without a reference photo. Photos read as dating-app profile photos.
- **Male casting note:** for relatability personas (viewer should see himself), specify an everyday/average-build, slightly imperfect guy, not a polished model. State it once in Casting Notes and reference it from each scene.
- **Map/UI frames:** check visible pins and profiles before shipping — no India or Russia in frame.

---

## What goes in a brief

- Notion task name, then app + persona + batch + concept + concept code
- Benchmark (per-variant when the brief spans multiple hook types/nationalities)
- File naming template (once at top)
- Structure table (once at top)
- One block per variant: full file name + cast line + scene lines, sequenced by shared casting identity

## What does NOT go in a brief

- Proximity/casting data reasoning or why a nationality was chosen
- Execution mood/tone notes (unless casting-critical)
- Secondary headline variants (separate task)
- Any explanation of the angle or persona logic
- Rationale in general: cast, text, file name. Nothing else.

---

## Brief Format

### File header (once per file)
```
**NOTION TASK NAME:** `[Batch]-[6charcode]-[ConceptName]-[Persona]`

---

# Creative Brief — [Headline or Angle Name]
**App:** Bumpy | **Persona:** [Canonical persona] | **Format:** [Video Ad / Static]
**Batch:** [BatchYYYYWeekWW] | **Concept:** [Concept name] | **Concept Code:** [6charcode]

---

## Benchmark
[URL or 1–2 sentence visual description] — match vibe/composition, tweak at least one element, don't copy exactly

---

## Structure

| Scene | Name | What It Is |
|---|---|---|
| 1 | HOOK | [Hook concept description] |
| 2 | ... | ... |

---

## File Naming Convention
`[Persona]-[audiencecode]-[conceptcode]-[ConceptName]-[hook]-[headline]-[angle]-[Modifier]-[VID/IMG]-[strategist]-[designer]-[batch]`

---
```

### Endscreen guidance **[v4]**

Don't describe the endscreen as "Bumpy app UI." It is the existing endscreen visual (brand template). Write `endscreen visual (existing template asset, not app UI)` unless told otherwise.

### Per variant block (repeat, sequenced per Variant Sequencing)
```
## [Nationality/Identity] — [Language]

**Cast:** [details, reused-asset note if applicable]
**File name (VID):** `[full file name — VID]`
**File name (IMG):** `[full file name — IMG]` ← only if IMG confirmed

[SCENE TYPE — visual detail | also shoot as standalone IMG] `on-screen text`

[repeat for each scene]

---
```

If no IMG version: a single `**File name:**` line.

### V2 versions (same hook, reordered scenes)

Same cast, same on-screen text, same assets, different edit order. Lives in the same file after V1 under a `# Version 2` header. Adds video output only. No IMG unless asked.

---

## Task Weight

```
Image generation: [n]
Image to video generation: [n]
Voice generation: [n]
Video output: [n]
Image output: [n]
```

**Image generation** = unique new shoots only, after applying the Asset Reuse Rule.
**Image to video generation** = same reuse logic.
**Voice generation** = 0 unless voiceover is part of the brief.
**Video output** = VID variants × versions.
**Image output** = IMG variants.

Per scene:
- Hook with physical prop (boarding pass/banner/note): 1 image gen + 1 image-to-video per **language**.
- Hook without prop (wake-up, POV, selfie): 1 + 1 per **nationality**, reused across languages.
- Profiles/Slider: 1 image gen per unique su_id or generated card (no video). Reused across languages if only the label changes.
- Map Swipe: existing template asset, 0.
- Video call / Airport / Eating / Car / Proposal / Travel: 1 + 1 per unique individual/pairing, deduplicated.
- Its a Bump: 0 (existing UI asset). Chat: 0 (After Effects template). Endscreen: 0.
- V2+: 0 extra gen.

**Existing asset rule:** a scene reusing an asset from this or another brief is marked `existing asset — reused from [source], no additional generation` and excluded from gen counts.

---

## Scene Type Library

See `bumpy-brief-brainstorm-SKILL.md` for the full library (HOOK variants, PROFILES/SLIDER, MAP SWIPE, VIDEO CALL, MANY DM, CHAT, TRAVEL, ENDSCREEN, ITS A BUMP, AIRPORT, EATING, CAR, PROPOSAL) and named sequences. Defaults this skill relies on:
- PROFILES/SLIDER always has on-screen text (e.g. `Women on Bumpy 🥵 >>>`, `Meet them on Bumpy 🌍`). Never blank.
- AIRPORT / EATING / CAR / PROPOSAL share one payoff line, noted once (e.g. `Try international dating, you won't regret it`).

---

## Bumpy Brand Rules (apply to every brief)

- **Endscreen CTA — confirm per persona.** Default: `Find your international soulmate. Bumpy.` Persona-specific CTAs already in use: `Meet Christian Singles Worldwide` (ChristianMatch), `Find Latina Worldwide` (LatinaFemaleLover), `Find your international friends` (IntlFriendFinder). Localize the CTA for non-English variants. Ask which applies; never assume.
- **Never "nearby" or "near you."** If a user's line uses it contrastively ("boys only date nearby"), flag it and let them decide.
- **Russia (RU) excluded** from casting, faces and locations. Bumpy is Ukrainian-founded. "Slavic" casting = UA and similar, never RU.
- **India (IN) excluded** from casting. Board decision.
- **[ITS A BUMP] has no text.** ~1 second animation.
- **[CHAT] is an After Effects template.** Designer edits in AE. Gen: 0.
- **Non-native languages** (e.g. Turkish): flag lines for a native speaker check before shipping.

---

## Quality Check

- [ ] NOTION TASK NAME is the first line
- [ ] Task Weight is at the bottom, all 5 lines, Asset Reuse Rule applied
- [ ] Header has app, persona, batch, concept, concept code
- [ ] Benchmark per variant when needed, with the tweak instruction on every line
- [ ] Every file name has exactly 12 fields, A–Z/0–9 only inside fields
- [ ] Persona is on the Canonical Persona List
- [ ] Strategist and designer codes are from the Roster (asked, not guessed)
- [ ] Concept code is per-concept (new hook = new code)
- [ ] Conceptname generic across shared-code sub-hooks; differences live in `[hook]`
- [ ] Multi-language set = one Mega-Brief grouped by asset type
- [ ] Variants sequenced by casting identity
- [ ] Reused assets marked; V2 only when the hook is unchanged
- [ ] VID + IMG names both present if IMG confirmed; HOOK has the IMG note
- [ ] Every scene has `[visual]` and `` `text` ``; HOOK text = approved headline exactly
- [ ] Endscreen = endscreen visual (not app UI), CTA confirmed for this persona
- [ ] No RU or IN casting; map frames checked
- [ ] su_id cards have names; no-su_id cards have full descriptions
- [ ] [ITS A BUMP] `[no text]`; [CHAT] marked AE template, 0 gen
- [ ] No rationale, proximity reasoning or persona explanation in the brief
