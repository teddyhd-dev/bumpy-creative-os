# Bumpy — Ad Naming Convention
version: 5.1.0

> **Changelog 5.0.0 → 5.1.0 (3 Nov 2026, merged with the strategists' brief writer v5):**
> - Inside every field: letters A–Z and digits 0–9 only (no accents, emoji, apostrophes or other scripts).
> - Audience codes listed below (language of the on-screen text; country-style codes for now).
> - Angles have one list: `core/angles.csv` (the brief writer's list + the ones in use on the board).
> - Team codes: creator-program codes (`001`…) and TikTok One codes (`TT1`–`TT4`, `TTO`) are valid; all in `core/team.csv`.
> - Concept code rule spelled out: a different opening scene is a new code; V1/V2 reorder scenes after the same opening.
> - The brief writer no longer keeps its own persona list, roster or angle list: it reads this file, `core/team.csv`,
>   `core/angles.csv` and `core/naming-adset-v8.md`.
>
> **Changelog from v4.0.0**
> - Added **strategist** and **designer** 3-letter codes, placed right before `batch`. Every ad now says who briefed it and who made it, so refresh results can be credited automatically (see `core/spec.md` §5).
> - `persona` must now use the **canonical persona name** from the adset convention (`core/naming-adset-v8.md`, Persona Taxonomy), e.g. `LatinaFemaleLover`, not `LatinaLover`. Ad data and adset data then join on persona directly.
> - Ads made before v5 keep their v4 names. Reporting reads them as v4 (10 fields, no strategist/designer) and maps old persona spellings to canonical ones.

---

## Template

```
[persona]-[audiencecode]-[conceptcode]-[conceptname]-[hook]-[headline]-[angle]-[modifier]-[VID/IMG]-[strategist]-[designer]-[batch]
```

**Exactly 12 fields, separated by `-`.** Inside every field: letters A–Z and digits 0–9 only. No hyphens,
spaces, accents, apostrophes, emoji or non-Latin script, or the name can't be read.

**Real-world example:**
```
AsianFemaleLover-US-b7Kq4n-BoysVMen-ChineseChampagnePop-mendateasiangirlsbumpy-recommendation-ProductAware-IMG-TED-OST-Batch2026Week37
```

---

## Field Definitions

| # | Field | What it is | Case | Example |
|---|---|---|---|---|
| 1 | `persona` | Canonical persona name from the adset Persona Taxonomy | PascalCase | `LatinaFemaleLover` |
| 2 | `audiencecode` | Target audience language code. Use the real code (`US`, `ES`, `PT`…). Never invent regional proxies like `LATAM`. English = `US` | UPPERCASE | `ES` |
| 3 | `conceptcode` | 6-character alphanumeric, generated once per concept, reused across every variant of that concept | Mixed | `n6f2Wt` |
| 4 | `conceptname` | Generic visual hook family. Stays the same across sub-hook-types that share a code | PascalCase | `Banner` |
| 5 | `hook` | Compact descriptor: who + which hook variant. Sub-hook-types are differentiated here | PascalCase | `ColombianaBigTicket` |
| 6 | `headline` | Short slug of the on-screen copy | lowercase | `noviacolombiana` |
| 7 | `angle` | Ad angle type, from `core/angles.csv` | lowercase | `recommendation` |
| 8 | `modifier` | Awareness stage | PascalCase | `ProductAware` |
| 9 | `VID/IMG` | Output format | UPPERCASE | `VID` |
| 10 | `strategist` | 3-letter code of the strategist who wrote the brief (roster below) | UPPERCASE | `TED` |
| 11 | `designer` | 3-letter code of the designer who made the creative (roster below) | UPPERCASE | `OST` |
| 12 | `batch` | `BatchYYYYWeekWW` | as shown | `Batch2026Week27` |

**Modifier values:** `Unaware` · `ProblemAware` · `SolutionAware` · `ProductAware` · `MostAware`

Keep `hook` and `headline` short: two long descriptive fields make names far longer than production uses.

### Audience codes (field 2)
The code follows the **language of the on-screen text**, not the country. For now we use country-style codes:

| Language | Code | Language | Code |
|---|---|---|---|
| English | `US` | Japanese | `JP` |
| Spanish | `ES` | Korean | `KR` |
| Portuguese | `PT` | Ukrainian | `UA` |
| Indonesian | `ID` | Chinese | `CH` |
| Thai | `TH` | Vietnamese | `VN` |
| German | `DE` | Turkish | `TR` |

Any other language: ask the creative lead and add it here first. Example: an Uzbek Muslim audience with
Russian-language copy is `RU` (Russian casting stays banned, `core/brand.md`). Never invent regional codes like `LATAM`.

### Angles (field 7)
One list for every tool: `core/angles.csv` (angle + what it means). If none fits, use a short lowercase word and
tell the creative lead, who adds it to the list.

---

## Team Roster

The roster lives in `core/team.csv` (one place for every tool). New team member → add a row there **before** their
first ad goes live. Codes are 3 characters and never reused for a different person:
- staff: 3 uppercase letters (`TED`, `OST`);
- creator program: the strategist is `TIN`; the designer field holds the creator's code `001`, `002`… assigned by the
  program, never invented;
- TikTok One: `TT1`–`TT4` (brief project) as strategist, `TTO` as designer.

---

## Persona: write this, not that

Ad names before v5 used many spellings. From now on field 1 is always the canonical persona:

| Write | Not |
|---|---|
| `InternationalFriendFinder` | Friends, InternationalFriends, IntlFriendFinder |
| `GringoMaleLover` | GringoLover, Gringolover |
| `AsianFemaleLover` | Chinese, AsianLover, AsianDating |
| `LatinaFemaleLover` | LatinaLover, LatinaFemaleLoverES |
| `SlavicFemaleLover` | SlavicLover, Slavic |
| `MatureDating` | 304050, 3040, 5060 |
| `LocalDatingFatigue` | AngryWithLocalDating, ChurnLocal |
| `EgoBoostForIndianBoy` | IndianBoyDream |
| `InterracialDatingSeekers` | BlackAfrican, BLK |
| `GirlWantsToRelocate` | PassportGirl |
| `KoreanMaleCultureLover` | Koreaboo |
| `MuslimMatchWorldwide` | muslim, Muslim, MuslimMatch |
| `ChristianMatchWorldwide` | Christian |
| `NewLanguageLearner` | LearnLanguage |
| `LGBTQ` | LGBT |
| `LatinoMaleLover` | LatinoLover |
| `ChatOnly` | ChatPersona |

**Same creative in another persona's adset** (e.g. a LocalDatingFatigue concept moved into PassportBro):
duplicate the file and name the copy for the adset's persona, keeping the same concept code. The concept's
results then stay together, and each audience gets its own credit.

---

## Concept Code Rule

A concept = hook + video structure. New hook (different first 2 seconds) = new concept code, even if every other scene is reused footage. Never reuse a code across different concepts.

- **Re-sequenced openings are new concepts.** The same scenes cut so each version opens on a different scene
  (1-2-3-4, 2-4-1-3, 3-4-1-2…) = one code per opening scene. Shared footage, so no extra generation; only the
  code count and video output go up.
- **Versions (V1/V2) keep the code:** same opening 2 seconds, scenes reordered after it.
- **Variants keep the code:** new `hook` sub-type (same kind of opening, e.g. another actor or prop), new text,
  re-cut, another language.

Every code and its concept name are listed in `core/concepts.csv` (the engine adds new codes from the ad names every Monday; the creative lead confirms them). Check it before picking a new code: it must be unique ignoring letter case. Known typos of old codes are in `core/code_aliases.csv`.

Sub-hook-types that open the same way (e.g. Big Ticket and Fence Banner) may share one code. Confirm with whoever owns Meta reporting first.

---

## What Changes, What Stays

| Scope | Fields that change |
|---|---|
| Per variant (same concept) | `hook`, `headline` (plus `audiencecode` if a different language; `designer` if someone else made the variant) |
| Per concept | Everything, including a new code |
| VID vs IMG of the same variant | Only `VID` → `IMG` |

---

## Examples

**VID + IMG pair:**
```
LatinaFemaleLover-ES-n6f2Wt-Banner-ColombianaBigTicket-noviacolombiana-recommendation-ProductAware-VID-JAC-HAN-Batch2026Week27
LatinaFemaleLover-ES-n6f2Wt-Banner-ColombianaBigTicket-noviacolombiana-recommendation-ProductAware-IMG-JAC-HAN-Batch2026Week27
```

**Shared code, different sub-hooks** (differentiate in `hook` only, never in `conceptname`):
```
LatinaFemaleLover-ES-n6f2Wt-Banner-ColombianaBigTicket-noviacolombiana-recommendation-ProductAware-VID-JAC-HAN-Batch2026Week27
LatinaFemaleLover-ES-n6f2Wt-Banner-ColombianaFenceWhiteboard-noviacolombiana-recommendation-ProductAware-VID-JAC-HAN-Batch2026Week27
```

---

## Checklist

- [ ] Exactly 12 fields, no blanks, only A–Z and 0–9 inside a field
- [ ] `persona` is on the canonical Persona Taxonomy list
- [ ] `audiencecode` is a real code, not `LATAM`
- [ ] `conceptcode` is exactly 6 characters
- [ ] New hook got a new code
- [ ] `conceptname` is generic; sub-hook detail lives in `hook`
- [ ] `headline` and `angle` lowercase, `modifier` PascalCase
- [ ] `VID` / `IMG` uppercase
- [ ] `angle` is in `core/angles.csv` (or flagged to the creative lead)
- [ ] `strategist` and `designer` are codes from `core/team.csv`
- [ ] Checked with `python3 checks/new_concept.py names -`
