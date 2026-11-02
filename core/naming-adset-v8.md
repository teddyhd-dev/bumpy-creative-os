# Bumpy — Campaign & Adset Naming Convention
version: 8.1.0
status: FOUNDATIONAL — do not deviate without updating this doc first

> Copied from the Claude project file `bumpy-naming-convention UPDATED.md`. Note: Meta exports show
> the separator as ` / ` (with spaces); the engine reads both.

> **Changelog 8.1.0 (2 Nov 2026, creative lead):** four live personas added to the canonical list —
> `AsianMaleLover`, `SoutheastAsianFemaleLover`, `LatinoMaleLover`, `ChatOnly`. `IntlFriendFinder`,
> `Friends` and `InternationalFriend` are all `InternationalFriendFinder` (adsets already named
> `IntlFriendFinder` keep their names; the engine reads them as the canonical persona).
>
> **Changelog from v7.0.0 (team correction round 5):**
> - **Added a dedicated BidStrategy field**, separate from BudgetStrategy and separate from
>   Modifier. BudgetStrategy answers *where the money is pooled* (CBO/ABO). BidStrategy
>   answers *how the algorithm spends it* (tROAS, target CPA, Maximize Conversions/Value, Cost
>   Cap). These were being conflated before, which is what forced Campaign's Modifier to a
>   single-value cap — bid-strategy detail and real lifecycle tags were competing for the same
>   slot.
> - **Removed the single-value cap on Campaign's Modifier** (BidStrategy having its own field
>   made that cap unnecessary) — then capped Modifier stacking at 2 values max everywhere, and
>   tightened the delimiter and Geo/SubAngle formatting, specifically to fit a 128-character
>   limit. See the new Character Limit section.
> - **BidStrategy lives at both Campaign and Adset level** — Meta typically decides this at
>   the adset level, TikTok's own campaign names show it decided at campaign level. Rather than
>   force one answer, both levels carry it.

---

## Why this exists

The same audience gets named three different ways depending on who set it up and which
platform it's on — you can't aggregate spend across them because the strings don't match.
**The fix is one identical field formula, used the same way on Meta, TikTok, Google, and
anything added later.** Every slot is always present — if it doesn't apply, it gets a real
default value (`General`, `Normal`, `WW`), never blank, never a placeholder that looks broken.

---

## Delimiter rules

- **Field separator:** `/` (single slash, no spaces) — tightened from the earlier `" / "` to fit the 128-character limit; see the Character Limit section.
- **Multi-word values within a field:** PascalCase, no spaces (`GirlWantsToRelocate`) — same
  casing as the `persona` field in `bumpy-brief-writer-SKILL.md`'s creative file naming, so
  spend data and creative data join on `Persona` directly.
- **Sub-parts within one field** (BidStrategy or Modifier holding more than one real value):
  joined with `-` (e.g. `CostCap-CPA`, `tROAS-Challenger`).
- **Never use `|`** — the old names use it as a loose, unstructured suffix, which is exactly
  the ambiguity this replaces.
- **Never use `?`.** If a real value isn't known yet when converting a legacy name, use the
  field's defined default (`Normal`, `Standard*`, `ABO*`) and confirm the actual setting from
  the platform before the rename goes live — don't ship a name with a placeholder in it.

---

## The Formula

### Campaign name (11 fields)
```
[Level]/[Platform]/[Persona]/[OS]/[Geo]/[Language]/[Objective]/[BudgetStrategy]/[BidStrategy]/[Modifier]/[LaunchDate]
```
Example: `CM/Meta/CelebrityCrushLookalikeLover/iOS/WW/EN/Purchase/ABO/Standard/Normal/20260101`

### Adset name (12 fields)
```
[Level]/[Platform]/[Persona]/[SubAngle]/[OS]/[Geo]/[Language]/[Gender]/[Objective]/[BidStrategy]/[Modifier]/[LaunchDate]
```
Example: `AS/Meta/InterracialDatingSeekers/General/Android/WW/EN/BothGender/Purchase/Standard/Normal/20260101`

**BudgetStrategy stays Campaign-only** — CBO vs. ABO is decided once for the whole campaign,
so every adset underneath already shares it; naming it again on each adset would just repeat
the same fact.

**BidStrategy lives at both levels.** Real platforms disagree on where this is decided — Meta
usually sets it per adset, TikTok's own campaign names show it set at the campaign level. Both
levels carry the field so whichever level actually made the decision can state it.

**Modifier lives at both levels and can stack up to 2 values at either level.** The earlier
version of this convention capped Campaign's Modifier to one value specifically because
bid-strategy detail and real lifecycle/test tags were competing for the same slot; now that
BidStrategy has its own field, that crowding is gone, so 2 is the new ceiling everywhere — not
because of crowding, but to keep the whole name inside the 128-character limit. See the
Character Limit section.

---

## Field Glossary

| Field | Campaign | Adset | Default | Format |
|---|---|---|---|---|
| **Level** | ✓ | ✓ | *(never blank)* | `CM` (Campaign) · `AS` (Adset) |
| **Platform** | ✓ | ✓ | *(never blank)* | `Meta` · `TikTok` · `Google` · `Snapchat` · `Reddit` · `X` |
| **Persona** | ✓ | ✓ | `General` | PascalCase, canonical list only — see Persona Taxonomy |
| **SubAngle** | — | ✓ | `General` | PascalCase, persona-dependent, free-form where noted |
| **OS** | ✓ | ✓ | `All` | `iOS` · `Android` · `Web` · `All` |
| **Geo** | ✓ | ✓ | `WW` | `WW` · country codes joined `-` (`US-CA-GB`) · region groups `T1`/`T2`/`EU` · exclusions prefixed `x` (`WW-xUS`) |
| **Language** | ✓ | ✓ | `All` | ISO 639-1 (`EN`, `ES`, `PT`...) + one exception (`TX` for Taglish) |

> **Current practice (2 Nov 2026, creative lead):** names still write country-style codes in the Language field (`JP`, `KR`, `UA`, `CH`, `VN`…; ads write `US` for English). The move to ISO 639-1 comes later. Until then the engine reads `JA/KO/UK/ZH/VI` as `JP/KR/UA/CH/VN`.

| **Gender** | — | ✓ | `BothGender` | `BothGender` · `Male` · `Female` |
| **Objective** | ✓ | ✓ | `Purchase*` if unstated | `Purchase` · `Install` · `Signup` · `Sales` · `Retention` · `Awareness` |
| **BudgetStrategy** | ✓ | — | `ABO*` (Meta/TikTok) · `Auto` (Google) | `CBO` · `ABO` · `Auto` |
| **BidStrategy** | ✓ | ✓ | `Standard*` if unstated | `tROAS` · `CPA` · `MaxConversions` · `MaxValue` · `CostCap` · `BidCap` · `Standard`. Join with `-` if two related terms are both genuinely stated (`CostCap-CPA`) |
| **Modifier** | ✓ (stack `-`) | ✓ (stack `-`) | `Normal` | Lifecycle tag, seasonal tag, A/B flag, format tag — never bid-strategy info |
| **LaunchDate** | ✓ | ✓ | *(never blank)* | `YYYYMMDD` — the platform's real recorded creation date, not a guess |

**Why Persona sits third, right after Level and Platform:** Level and Platform are
constant within any single dashboard view — Meta's Campaigns tab only ever shows Meta
campaigns, so those two fields don't actually differentiate rows when you're sorting
alphabetically inside a platform's UI. Whatever comes next *is* the practical sort key. Putting
OS/Geo/Language there (as an earlier version of this convention did) meant campaigns
alphabetized by OS first — not useful for a creative team that thinks in personas. Persona (and
SubAngle right behind it) now leads, matching the same principle `bumpy-brief-writer-SKILL.md`
already uses for creative file names — persona first, so a persona-based sort or search groups
everything together instantly, in any dashboard, on any platform.

**BudgetStrategy vs. BidStrategy — the distinction that matters:** BudgetStrategy answers
*where the money is pooled* (campaign-level CBO vs. per-adset ABO). BidStrategy answers *how
the algorithm spends it* (chasing a target CPA, a target ROAS, maximizing conversions with no
target, etc.). Conflating these was the root of the original gap that forced a single-value
cap on Modifier.

**Why Platform/OS/Gender/BudgetStrategy spell out in full, but Level and Geo/Language use
short codes:** two different reasons for the same-looking abbreviation. Geo/Language codes
(`US`, `EN`) are an external ISO standard everyone already knows — no legend needed. `Level`
(`CM`/`AS`) is abbreviated purely for the character budget — it only has two possible values,
so the abbreviation costs nothing to memorize and never causes the ambiguity that made the
CEO unable to read persona names before. `Platform`/`OS`/`Gender`/`BudgetStrategy` stay spelled
out because those are things Bumpy defines itself with more possible values, and a custom
abbreviation there would need its own lookup table — the exact problem this convention exists
to remove.

---

## Staying Under 128 Characters

Both Campaign and Adset names must fit within a **128-character hard limit**. Under the
earlier version of this convention, a realistic worst case (long persona + long SubAngle +
a multi-country Geo list + a stacked Modifier) could hit **173 characters** — well over. Four
changes bring the realistic worst case down to roughly 115-120:

1. **Delimiter tightened from `" / "` to `"/"`** — saves 2 characters per field boundary
   (roughly 20 characters across a full name), at essentially no readability cost since every
   field is already PascalCase/code-style with no internal spaces.
2. **SubAngle uses short canonical forms** — `Serious` instead of `SeriousRelationship`,
   etc. (already reflected in the SubAngle table above).
3. **Modifier caps at 2 stacked values, at both Campaign and Adset level.** BidStrategy and
   BudgetStrategy having their own fields means Modifier rarely needs more than 1-2 real tags
   anyway — if a legacy name has more than 2 genuine candidates, keep the 2 most operationally
   important and note the rest in the campaign brief, not the name.
4. **Geo caps at 4 individual country codes.** Beyond that, use a named region group (`T1`,
   `T2`, `EU`, or a new one worth adding to the Geo glossary if the same combo recurs) — or, for
   a genuine one-off combination, `Custom‡` with the real country list tracked in the
   platform's actual audience settings, not spelled out in the name. A geo list long enough to
   need this isn't scannable at a glance anyway, which was the whole point of putting it in the
   name in the first place.

**If a name still exceeds 128 characters after applying all four rules above** — flag it for
manual review rather than silently truncating something. This should be rare; if it's
happening often, that's a signal one of the four rules needs revisiting, not that this specific
name should be handled as a one-off exception.

---

## The one rule that keeps Persona, Modifier, and the two strategy fields straight

**If it describes WHO you're targeting → Persona. If it's specifically about budget pooling →
BudgetStrategy. If it's specifically about bidding mechanics → BidStrategy. Anything else
that's a test, setting, or measurement method → Modifier.**

- `CelebrityCrushLookalikeLover` → Persona (an audience)
- `CBO` / `ABO` → BudgetStrategy (where the budget lives)
- `tROAS` / `Cost Cap` / `Maximize Conversions` → BidStrategy (bidding mechanics)
- `IncrementalAttribution` / `Migration` / `Challenger` → Modifier (test/lifecycle flags)

---

## Persona Taxonomy

**Coverage check:** all 15 of the CEO's core personas map onto the list below.
`SingleMom` and `NewLanguageLearner` exist in `bumpy-knowledge.md` but aren't on that
15-persona spend slide. `LocalDatingFatigue` ("Angry with Local Dating") has real, current
spend under two live Meta campaigns and isn't tracked as a persona anywhere the CEO would see
it.

Two rules:
1. **Persona and SubAngle values only ever come from the tables below.** New one needed → add
   the row here first, then launch.
2. **Every partner-preference persona name states the desired partner's gender explicitly.**

### The naming pattern — three fixed shapes

| Pattern | Shape | Meaning |
|---|---|---|
| **A — Partner Preference** | `[Ethnicity/Nationality][DesiredGender]Lover` | Audience wants to date a partner of this ethnicity/nationality and this gender |
| **B — Shared Identity** | `[Identity]Match` | Audience wants a partner who shares their own faith/identity |
| **C — Situational** | Plain descriptive name | Audience is defined by their own life situation, a specific market pairing, or a specific creative concept |

### Canonical Persona List — finalized by the team

| Persona (canonical) | Pattern | Old names it replaces | Typical Gender* |
|---|---|---|---|
| `GringoMaleLover` | A | Gringo Lover | Female |
| `AsianFemaleLover` | A | Asian Dating, Asian Lover | Male |
| `LatinaFemaleLover` | A | Latina Lover | Male |
| `SlavicFemaleLover` | A | Slavic Lover, Slavic Girl Lover | Male |
| `KoreanMaleCultureLover` | A | Korea Boo, Korean Guy and Culture Lover, Korean Male Lover | Female |
| `IndianFemaleDreamingForAsianMale` | C¹ | Gringo Lover IN | Female |
| `MuslimMatchWorldwide` | B | Muslim, Muslim Dating, Muslim Match | BothGender |
| `ChristianMatchWorldwide` | B | Christian, Christian Dating, Christian Worldwide | BothGender |
| `PassportBro` | C | Passport Bro | Male |
| `GirlWantsToRelocate` | C | Girl who want to relocate, Passport Girl | Female |
| `MatureDating` | C | 30-40-50, 50-60, Dating on 50-60, Dating on 30-40+ | BothGender |
| `InterracialDatingSeekers` | C | Inter racial dating, Interracial Dating, Black Women Interracial, Black Dating | Female |
| `SingleMom` | C | Single Mom | Female |
| `InternationalFriendFinder` | C | International Friend, Friends, IntlFriendFinder | BothGender |
| `NewLanguageLearner` | C | Learn Language, Language Learner | BothGender |
| `EgoBoostForIndianBoy` | C | Indian Boy, Indian Boy Dream | Male |
| `RichHusbandFinder` | C | Woman Marriage, Rich Husband Finder | Female |
| `LGBTQ` | C | LGBTQ+ | BothGender |
| `LocalDatingFatigue` | C | Local Dating, Angry with Local Dating | BothGender |
| `CelebrityCrushLookalikeLover` | C² | Churn Raya | BothGender |
| `AsianMaleLover` | A | Asian Male Lover | Female |
| `SoutheastAsianFemaleLover` | A | Southeast Asian Lover | Male |
| `LatinoMaleLover` | A | Latino Lover, TikTok Safe Latino | Female |
| `ChatOnly` | C | Chat Persona, Talk only, Chat/Talk-only persona | BothGender |
| `General` | — | Incremental Attribution, Spark Ads Organic Content | BothGender |

*Typical Gender = default for the adset's `Gender` field only when the old name doesn't
explicitly state one.

¹ *`IndianFemaleDreamingForAsianMale` bakes in both the audience's nationality (Indian) and
the desired partner's (Asian male) — that's a step beyond what Pattern A normally encodes
(which only states the desired partner's side, since the app is cross-border by default for
any audience nationality). Filed under Pattern C rather than forcing a fourth pattern shape
for one entry.*

² *`CelebrityCrushLookalikeLover` doesn't fit Pattern A/B either — it's about physical
resemblance to a specific celebrity, not ethnicity/nationality or shared identity. Filed under
Pattern C as "specific creative concept," same bucket as anything else that doesn't cleanly
fit A or B.*

**Two of the three previously-flagged open items are now resolved by this list:**
- ~~`InterracialDating` — may or may not unify with "Black Dating"~~ → **Resolved.** Confirmed
  as one unified audience: `InterracialDatingSeekers`.
- ~~`IndianMaleDream` — inferred from casting exclusion, not confirmed~~ → **Resolved.**
  Confirmed: Indian men are the audience (matches the earlier inference), now named
  `EgoBoostForIndianBoy`.

**Still open — needs a real team decision:**
- **`BeachGirl`** — cast against TR/NG/AE/EG/SA/IQ in one adset; may be an aspirational
  "Western beach girl" angle aimed at Middle East/North Africa (Pattern A) rather than its own
  persona. Not part of this round's revisions — still pending.

### SubAngle

| Persona | What SubAngle encodes | Example values |
|---|---|---|
| `LatinaFemaleLover` | Relationship intent | `Serious`, `Hookup`, `Marriage`, `General` |
| `AsianFemaleLover` | Relationship intent or country | `Serious`, `Hookup`, `Country-KR`, `General` |
| `GringoMaleLover` | Target market | `BR`, `TH`, `ID`, `PH`, `LatAm` |
| `SlavicFemaleLover` | Relationship intent | `Serious`, `Hookup`, `General` |
| `KoreanMaleCultureLover` | Relationship intent | `Serious`, `Hookup`, `General` |
| `IndianFemaleDreamingForAsianMale` | Relationship intent | `Serious`, `Hookup`, `General` |
| `MatureDating` | Age band — free-form | `30to40`, `40to60`, `50to60`, `40Plus` |
| `NewLanguageLearner` | Target language | `Spanish`, `Korean`, `French` |
| `MuslimMatchWorldwide` / `ChristianMatchWorldwide` | Target market | `ID`, `TR`, `MA` |
| `CelebrityCrushLookalikeLover` | Which celebrity/lookalike category | `KPop`, `Hollywood`, `Bollywood`, `General` |
| Anything else | Whatever the meaningful test split is, or `General` | |

---

## Governance

1. **Persona and SubAngle values only come from the tables above.**
2. **Never silently rename or delete a canonical Persona once campaigns are live under it.**
3. **Keep Persona spelled identically to the `persona` field in `bumpy-brief-writer-SKILL.md`.**
4. **`General`/`Normal`/`BothGender`/`Auto`/`Standard` are information, not cop-outs.**
5. **New platforms slot in for free** — add a new Platform name, done.
6. **When migrating a historical name, never guess a value the old name didn't state.** Default
   appropriately and mark with `*`, but confirm the real setting before the rename goes live.
7. **Once live, treat a name as fixed.** Renaming a running Meta/TikTok adset can reset its
   ad-learning phase. Launch a new object with a new LaunchDate instead of editing in place.
8. **Don't let BudgetStrategy, BidStrategy, and Modifier crowd each other.** Each has a clear
   job — see "The one rule" above. If in doubt, it's more likely a Modifier than a mis-filed
   bid setting.

---

## Full Migration Reference — Every Example, Old → New

`†` = best-guess mapping, flagged for team confirmation. `*` = inferred from context, not
directly stated in the old name. `‡` = Geo compressed to `Custom` because the original targeted
more than 4 individual countries — the real country list stays in the platform's audience
settings, not the name (see Staying Under 128 Characters).

### Meta — Campaign level

| Old | New |
|---|---|
| `WW-ENG / iOS / Purchase \| Churn Raya` | `CM/Meta/CelebrityCrushLookalikeLover/iOS/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `WW-ENG / Web / Sales \| Incremental Attribution` | `CM/Meta/General/Web/WW/EN/Sales/ABO*/Standard*/IncrementalAttribution/20260101` |
| `WW-ENG / Android / Purchase \| Angry with Local Dating` | `CM/Meta/LocalDatingFatigue/Android/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `WW-ENG / Android / Purchase \| Korean Guy and Culture Lover` | `CM/Meta/KoreanMaleCultureLover/Android/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `NL-ENG / Android / Purchase` | `CM/Meta/General/Android/NL/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `WW-ENG / iOS / Purchase \| Beach Girl` | `CM/Meta/BeachGirl†/iOS/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `WW-ENG / Android / Purchase \| 30-60 \| Relaunch` | `CM/Meta/MatureDating/Android/WW/EN/Purchase/ABO*/Standard*/Relaunch/20260101` |
| `WW-ENG / Android / Purchase \| Slavic Girl Lover` | `CM/Meta/SlavicFemaleLover/Android/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `WW-ENG / iOS / Purchase \| Girl who want to relocate` | `CM/Meta/GirlWantsToRelocate/iOS/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |
| `WW-ENG / iOS / Purchase \| Angry with Local Dating` | `CM/Meta/LocalDatingFatigue/iOS/WW/EN/Purchase/ABO*/Standard*/Normal/20260101` |

*(Age band "30-60" still moves to the Adset's SubAngle field — Campaign has no SubAngle.)*

### Meta — Adset level

| Old | New |
|---|---|
| `Ad Set / Churn Raya / WW-ENG / iOS / Purchase` | `AS/Meta/CelebrityCrushLookalikeLover/General/iOS/WW/EN/BothGender/Purchase/Standard*/Normal/20260101` |
| `AS/WW-ENG/Web/Sales \| Incremental Attribution` | `AS/Meta/General/General/Web/WW/EN/BothGender/Sales/Standard*/IncrementalAttribution/20260101` |
| `Ad Set / Interracial Dating / US-ENG / iOS / Purchase` | `AS/Meta/InterracialDatingSeekers/General/iOS/US/EN/Female/Purchase/Standard*/Normal/20260101` |
| `Ad Set / Dating on 50-60 / WW-ENG / Android / Purchase` | `AS/Meta/MatureDating/50to60/Android/WW/EN/BothGender/Purchase/Standard*/Normal/20260101` |
| `Ad Set / Korean Guy and Culture Lover / WW-ENG / Android / Purchase` | `AS/Meta/KoreanMaleCultureLover/General/Android/WW/EN/Female/Purchase/Standard*/Normal/20260101` |
| `Ad Set / Angry with Local Dating / WW-ENG / Android / Purchase` | `AS/Meta/LocalDatingFatigue/General/Android/WW/EN/BothGender/Purchase/Standard*/Normal/20260101` |
| `Ad Set / ES-ES / iOS / Purchase` | `AS/Meta/General/General/iOS/ES/ES/BothGender/Purchase/Standard*/Normal/20260101` |
| `Ad set / NL-ENG / Android / Purchase` | `AS/Meta/General/General/Android/NL/EN/BothGender/Purchase/Standard*/Normal/20260101` |
| `Ad Set / Beach Girl / WW-ENG / iOS / Purchase \| TR NG UAE EG SA IQ` | `AS/Meta/BeachGirl†/General/iOS/Custom‡/EN/BothGender/Purchase/Standard*/Normal/20260101` |
| `Ad Set / Beach Girl / WW-ENG / iOS / Purchase` | `AS/Meta/BeachGirl†/General/iOS/WW/EN/BothGender/Purchase/Standard*/Normal/20260101` |

### TikTok — Campaign level

| Old | New |
|---|---|
| `WW-ALL / iOS / CPA / Purchase \| Spark Ads Organic Content` | `CM/TikTok/General/iOS/WW/All/Purchase/ABO*/CPA/SparkAdsOrganic/20260101` |
| `WW-ENG / iOS / Purchase \| Migration` | `CM/TikTok/General/iOS/WW/EN/Purchase/ABO*/Standard*/Migration/20260101` |
| `US-ENG / iOS / CBO / tROAS` | `CM/TikTok/General/iOS/US/EN/Purchase*/CBO/tROAS/Normal/20260101` |
| `WW-ES / iOS / CBO / tROAS` | `CM/TikTok/General/iOS/WW/ES/Purchase*/CBO/tROAS/Normal/20260101` |
| `WW-ALL / iOS / Purchase \| Spark Ads \| Cost Cap \| CPA` | `CM/TikTok/General/iOS/WW/All/Purchase/ABO*/CostCap-CPA/SparkAds/20260101` |
| `EU-ALL / iOS / CBO / tROAS` | `CM/TikTok/General/iOS/EU/All/Purchase*/CBO/tROAS/Normal/20260101` |
| `WW-ENG / iOS / CBO / tROAS \| Challenger` | `CM/TikTok/General/iOS/WW/EN/Purchase*/CBO/tROAS/Challenger/20260101` |
| `WW-PT / iOS / Purchase \| Migration` | `CM/TikTok/General/iOS/WW/PT/Purchase/ABO*/Standard*/Migration/20260101` |
| `T2-ENG / iOS / CBO / tROAS` | `CM/TikTok/General/iOS/T2/EN/Purchase*/CBO/tROAS/Normal/20260101` |

*(Note row 7 — this is the exact case that exposed the original gap. Budget strategy, bid
strategy, and the lifecycle tag are now all preserved simultaneously; nothing had to be
sacrificed to fit a single-value cap.)*

### TikTok — Adset level

| Old | New |
|---|---|
| `Ad Set / WW-ALL / iOS / CPA / Purchase \| Spark Ads Organic Content` | `AS/TikTok/General/General/iOS/WW/All/BothGender/Purchase/CPA/SparkAdsOrganic/20260101` |
| `Ad Set / WW-ENG / iOS / Purchase \| Migration` | `AS/TikTok/General/General/iOS/WW/EN/BothGender/Purchase/Standard*/Migration/20260101` |
| `Ad Set / WW-ES / iOS / CBO / tROAS` | `AS/TikTok/General/General/iOS/WW/ES/BothGender/Purchase*/tROAS/Normal/20260101` |
| `Ad Set / US-ENG / iOS / CBO / tROAS / Female Audience` | `AS/TikTok/General/General/iOS/US/EN/Female/Purchase*/tROAS/Normal/20260101` |
| `Ad Set / WW-ALL / iOS / Purchase \| Spark Ads \| Cost Cap \| CPA` | `AS/TikTok/General/General/iOS/WW/All/BothGender/Purchase/CostCap-CPA/SparkAds/20260101` |
| `Ad Set / EU-ALL / iOS / CBO / tROAS` | `AS/TikTok/General/General/iOS/EU/All/BothGender/Purchase*/tROAS/Normal/20260101` |
| `Ad Set / WW-ENG / iOS / CBO / tROAS / Challenger` | `AS/TikTok/General/General/iOS/WW/EN/BothGender/Purchase*/tROAS/Challenger/20260101` |
| `Ad Set / WW-PT / iOS / Purchase` | `AS/TikTok/General/General/iOS/WW/PT/BothGender/Purchase/Standard*/Normal/20260101` |
| `Ad Set / US-ENG / iOS / CBO / tROAS / Passport Bro` | `AS/TikTok/PassportBro/General/iOS/US/EN/Male/Purchase*/tROAS/Normal/20260101` |
| `Ad Set / T2-ENG / iOS / CBO / tROAS` | `AS/TikTok/General/General/iOS/T2/EN/BothGender/Purchase*/tROAS/Normal/20260101` |

*(The `WW-PT/Purchase` adset's parent campaign was tagged `Migration`, but this adset's old
name didn't repeat it. Confirm whether this adset genuinely belongs to that push before
deciding its Modifier.)*

### Google — Campaign level

| Old | New |
|---|---|
| `ExUS / Android / English / Install` | `CM/Google/General/Android/WW-xUS/EN/Install/Auto/Standard*/Normal/20260101` |
| `PH / Android / EN-Taglish / Install` | `CM/Google/General/Android/PH/TX/Install/Auto/Standard*/Normal/20260101` |
| `WW / iOS / English / Install` | `CM/Google/General/iOS/WW/EN/Install/Auto/Standard*/Normal/20260101` |
| `WW / Android / Spanish / Install` | `CM/Google/General/Android/WW/ES/Install/Auto/Standard*/Normal/20260101` |
| `US / Android / English / Install` | `CM/Google/General/Android/US/EN/Install/Auto/Standard*/Normal/20260101` |
| `WW / Android / Japanese / Install` | `CM/Google/General/Android/WW/JA/Install/Auto/Standard*/Normal/20260101` |
| `WW / Android / Indonesian / Install` | `CM/Google/General/Android/WW/ID/Install/Auto/Standard*/Normal/20260101` |
| `CA-AE-CH / Android / English / Install` | `CM/Google/General/Android/CA-AE-CH/EN/Install/Auto/Standard*/Normal/20260101` |
| `WW / Android / Portuguese / Install` | `CM/Google/General/Android/WW/PT/Install/Auto/Standard*/Normal/20260101` |
| `WW / Android / French / Install` | `CM/Google/General/Android/WW/FR/Install/Auto/Standard*/Normal/20260101` |
| `WW / Android / German / Install` | `CM/Google/General/Android/WW/DE/Install/Auto/Standard*/Normal/20260101` |

*(`Auto` for BudgetStrategy is a genuine fact — Google App Campaigns have no CBO/ABO-equivalent
choice at all. `Standard*` for BidStrategy is different: Google App Campaigns *do* let you set
a Target CPA/ROAS goal, it just isn't visible in these old names — confirm the real setting.)*

### Google — Ad group level (= Adset)

*Geo/OS/Objective aren't shown at this level in your screenshot — inherited from the parent
campaign, marked `*`. Confirm against the actual parent before finalizing.*

| Old | New |
|---|---|
| `English / International` | `AS/Google/General/General/Android*/WW*/EN/BothGender/Install*/Standard*/Theme-International†/20260101` |
| `English / Gringo Lover` | `AS/Google/GringoMaleLover/General/Android*/WW*/EN/BothGender/Install*/Standard*/Normal/20260101` |
| `English / Safety` | `AS/Google/General/General/Android*/WW*/EN/BothGender/Install*/Standard*/Theme-Safety†/20260101` |
| `English / Generic` | `AS/Google/General/General/Android*/WW*/EN/BothGender/Install*/Standard*/Normal/20260101` |
| `English / Travel` | `AS/Google/General/General/Android*/WW*/EN/BothGender/Install*/Standard*/Theme-Travel†/20260101` |
| `English / Life-changing` | `AS/Google/General/General/Android*/WW*/EN/BothGender/Install*/Standard*/Theme-LifeChanging†/20260101` |
| `English / Friends` | `AS/Google/InternationalFriendFinder/General/Android*/WW*/EN/BothGender/Install*/Standard*/Normal/20260101` |
| `English / Story-Telling` | `AS/Google/General/General/Android*/WW*/EN/BothGender/Install*/Standard*/Theme-StoryTelling†/20260101` |
| `English / Passport Bro v2` | `AS/Google/PassportBro/General/Android*/WW*/EN/Male/Install*/Standard*/V2/20260101` |

**Real finding, not just a mapping exercise:** Google's ad groups mix real personas
(`Gringo Lover`, `Passport Bro`) with what are actually **creative themes**
(`Safety`, `Travel`, `Life-changing`, `Story-Telling`) — those aren't personas. Routed through
Modifier as `Theme-X` for now.

---

## Quick Reference Card

```
CAMPAIGN:
Level/Platform/Persona/OS/Geo/Language/Objective/BudgetStrategy/BidStrategy/Modifier/LaunchDate

ADSET:
Level/Platform/Persona/SubAngle/OS/Geo/Language/Gender/Objective/BidStrategy/Modifier/LaunchDate

Level:          CM (Campaign) / AS (Adset)
Platform:       Meta / TikTok / Google / Snapchat / Reddit / X
Persona:        [canonical list — see Persona Taxonomy] / General
SubAngle:       [persona-dependent — see SubAngle table] / General          (Adset only)
OS:             iOS / Android / Web / All
Geo:            WW / [ISO codes joined with -] / [x-prefixed exclusions, e.g. WW-xUS] / T1 / T2 / EU
Language:       EN / ES / PT / ID / JA / FR / DE / TR / TH / AR / RU / KO / IT / NL / All (ISO 639-1) + TX (Taglish exception)
Gender:         BothGender / Male / Female                                    (Adset only)
Objective:      Purchase / Install / Signup / Sales / Retention / Awareness
BudgetStrategy: CBO / ABO / Auto                                              (Campaign only)
BidStrategy:    tROAS / CPA / MaxConversions / MaxValue / CostCap / BidCap / Standard
Modifier:       Normal / [lifecycle tag, seasonal tag, A/B flag] — stack with - at either level
LaunchDate:     YYYYMMDD
```
