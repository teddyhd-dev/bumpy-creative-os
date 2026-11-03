# Brief writer: the Notion brief for designers

Used in SKILL.md step 7. Version 6.0.0 (3 Nov 2026), from the strategists' `bumpy-brief-writer` v5.0.0 (original in
`archive/strategist-files-2026-11-03/`).

> **Changelog v5 → v6:** the persona list, team roster, audience codes and angle list are no longer copied here.
> They live once in `core/` and this file points to them, so a persona or designer added there reaches every
> strategist's next brief. The hypothesis, prediction and evidence go into the experiment record (the hypothesis
> log), never into the designer brief. Casting is a reference, not a rule (`craft/casting.md`).

**What it does:** turns the approved concept (scenes + on-screen text) into a scene-by-scene brief the strategist
pastes into Notion, with the v5 ad names and the task weight. One file per concept, or one Mega-Brief for a set that
spans languages. The skeleton is `brief-template.md`.

## Where the lists live (read them, never copy them)
| What | Where |
|---|---|
| Persona names (closed list) | `core/naming-adset-v8.md` → Canonical Persona List. Old spellings: `core/persona_aliases.csv` |
| Ad name fields, audience codes, concept code rule | `core/naming-ad-v5.md` |
| Angles | `core/angles.csv` |
| Strategist and designer codes | `core/team.csv` (active rows only) |
| Concept codes and names | `core/concepts.csv` (+ `core/code_aliases.csv` for old spellings) |
| Endscreen CTA per persona, brand rules | `core/brand.md` |

## Required inputs
Before writing, have all of these; ask for what's missing in one short message, one line per question:
1. The headline(s), exact, with emoji.
2. The scene structure (even rough).
3. The persona, from the canonical list. If the creative fits none or two, ask.
4. Casting: from `craft/casting.md` as a starting point, or the strategist's choice. Never blank: if there's no
   profile ID, write a full description.
5. Benchmark: a URL or a described visual reference. One per variant when the brief has more than one visual hook
   type or nationality.
6. Concept name and concept code (`python3 checks/new_concept.py new` / `check`; a past winner keeps its code).
7. Batch: `BatchYYYYWeekWW`, ISO week of the launch date, two digits. If an old file name carries an older batch, use
   the current one and say so.
8. Strategist and designer codes from `core/team.csv`. Ask; never guess.
9. Format: "Video only, or will any scene (e.g. the hook) also be a static image?" IMG → two file names + an IMG
   note on that scene.
10. Versions: "Do you want V2 versions (same hook, scenes reordered after it) to lower ad similarity?"
11. Endscreen CTA: confirm per persona (`core/brand.md`).

## Concept codes (summary of `core/naming-ad-v5.md`)
A concept = its hook + structure, not its footage. A different first 2 seconds = a new code, even with 100% reused
footage. The same scenes re-sequenced so each version opens differently = one code per opening (no extra
generation, only video output goes up). V1/V2 = same opening, scenes reordered after it, same code. Sub-hook types
that open the same way (e.g. Big Ticket and Fence Banner) may share a code if the team wants them reported together:
confirm with whoever owns Meta reporting.

## Mega-Brief (sets across languages or markets)
One file, never one per language. Designers work in Premiere by visual: they finish every language of one asset type
before the next, only swapping text.
1. How this brief is organised (3–4 lines).
2. Master casting and localisation reference: local casting per market, shared asset pools.
3. **Step 1 — Generation**, grouped by asset type (all wanted selfies, then all couple photos…). Each asset generated
   once; mark where it is reused.
4. **Step 2 — Assembly**: the final variants (file name + scene lines + text per language), using only Step 1 assets.
5. Task weight at the bottom.

## Asset reuse: baked-in vs overlay text
- **Baked-in / prop text** (boarding pass, painted banner, handwritten note) is shot separately per language. A
  reused clip with handwritten text can't be translated by overlay: flag it to production.
- **Overlay text** (POV caption, slider label, command line over a scene without a prop) is shot once per
  nationality and reused across languages.
- Mark reuse: `— existing asset, reused from <source>, no additional generation`.
- Statics cut from video stills (same still + headline) cost 0 generation; they only add to image output.

## Variant order
Group variant blocks by shared casting or visual identity, not by language: `Colombiana (ES → PT), Venezolana
(ES → PT), Brasileña (ES only)`, not all ES then all PT. Scenes with no model (a fence or whiteboard text shot) are
noted as such.

## Benchmark line
On every benchmark line, not once at the top: *match the benchmark's vibe, composition and energy, but change at least
one element (pose, outfit colour or detail, background prop, angle) so it looks similar side by side, not identical.*

## File names
`[persona]-[audiencecode]-[conceptcode]-[conceptname]-[hook]-[headline]-[angle]-[modifier]-[VID/IMG]-[strategist]-[designer]-[batch]`
Fields and rules: `core/naming-ad-v5.md`. Per variant only `hook` and `headline` change (plus the audience code for
another language, the designer if someone else makes it). VID and IMG of one variant differ only in `VID`/`IMG`.
Check every name with `python3 checks/new_concept.py names -` before showing the brief.

Examples:
```
LatinaFemaleLover-ES-n6f2Wt-Banner-ColombianaFenceSign-noviacolombiana-recommendation-ProductAware-IMG-CAM-MAR-Batch2026Week42
AsianFemaleLover-US-b7Kq4n-BoysVMen-ChineseChampagnePop-mendateasiangirlsbumpy-recommendation-ProductAware-VID-TIN-004-Batch2026Week44
```

## What goes in a brief, and what never does
In: the Notion task name, then app + persona + batch + concept + code; benchmark(s); the file-name template and the
structure table once at the top; one block per variant (full file name, cast line, scene lines), in variant order;
task weight.
Never: rationale of any kind (why this persona, why this casting, the angle logic, mood notes unless casting-critical),
casting data reasoning, secondary headline variants (separate task). **Cast, on-screen text, file name. That's it.**
The why lives in the experiment record.

## Scenes in a brief
- Every scene: `[SCENE TYPE — visual detail]` and `` `on-screen text` ``. The hook text = the approved headline, exactly.
- `[PROFILES]`/`[SLIDER]` always has text. `[ITS A BUMP]` is `[no text]`. `[CHAT]` = AE template, exact messages, 0 gen.
- `[AIRPORT]`/`[EATING]`/`[CAR]`/`[PROPOSAL]` share one payoff line, noted once.
- `[ENDSCREEN]` = `endscreen visual (existing template asset, not app UI)` + the confirmed CTA.
- Scene library and meanings: `craft/options.md`.

## V2 versions
Same cast, text and assets, a different order after the same opening. In the same file after V1 under
`# Version 2`. Adds video output only; no IMG unless asked.

## Task weight
```
Image generation: n
Image to video generation: n
Voice generation: n
Video output: n
Image output: n
```
- Image generation = unique new shoots only, after the reuse rule. Image-to-video: same logic. Voice = 0 unless
  there's voiceover. Video output = VID variants × versions. Image output = IMG variants.
- Hook with a physical prop: 1 image + 1 image-to-video **per language**. Hook without a prop (wake-up, POV, selfie):
  1 + 1 **per nationality**, reused across languages.
- Profiles/slider: 1 image per unique card (no video), reused across languages if only the label changes.
- Map swipe 0 · Its a Bump 0 · Chat 0 (AE) · Endscreen 0 · V2+ 0.
- Video call / airport / eating / car / proposal / travel: 1 + 1 per unique person or couple, de-duplicated.
- A scene reusing an asset from this or another brief: `existing asset — reused from <source>, no additional
  generation`, excluded from the counts.

## Quality check before showing the brief
- [ ] Notion task name is the first line; task weight (5 lines, reuse applied) is the last
- [ ] Header: app, persona, batch, concept, concept code
- [ ] Benchmark per variant where needed, with the tweak instruction on every line
- [ ] `checks/new_concept.py names` passes for every file name (12 fields, A–Z/0–9, canonical persona, team codes)
- [ ] New hook = new code; concept name generic across shared-code sub-hooks; detail in `hook`
- [ ] Multi-language = one Mega-Brief grouped by asset type; variants ordered by casting identity
- [ ] Reused assets marked; V2 only when the hook is unchanged
- [ ] VID + IMG names both present if IMG confirmed; hook carries the IMG note
- [ ] Every scene has `[visual]` and `` `text` ``; endscreen = template + confirmed CTA
- [ ] Brand rules (`core/brand.md`): no RU/IN casting, map frames checked, no "nearby"
- [ ] Cards with a profile ID have a name; cards without one have a full description
- [ ] No rationale anywhere in the brief
