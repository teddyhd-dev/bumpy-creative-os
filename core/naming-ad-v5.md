# Bumpy — Ad Naming Convention
version: 5.0.0

> **Changelog from v4.0.0**
> - Added **strategist** and **designer** 3-letter codes, placed right before `batch`. Every ad now says who briefed it and who made it, so refresh results can be credited automatically (see `core/spec.md` §5).
> - `persona` must now use the **canonical persona name** from the adset convention (`core/naming-adset-v8.md`, Persona Taxonomy), e.g. `LatinaFemaleLover`, not `LatinaLover`. Ad data and adset data then join on persona directly.
> - Ads made before v5 keep their v4 names. Reporting reads them as v4 (10 fields, no strategist/designer) and maps old persona spellings to canonical ones.

---

## Template

```
[persona]-[audiencecode]-[conceptcode]-[conceptname]-[hook]-[headline]-[angle]-[modifier]-[VID/IMG]-[strategist]-[designer]-[batch]
```

**Exactly 12 fields, separated by `-`.** No hyphens inside any field, or the name can't be read.

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
| 7 | `angle` | Ad angle type | lowercase | `recommendation` |
| 8 | `modifier` | Awareness stage | PascalCase | `ProductAware` |
| 9 | `VID/IMG` | Output format | UPPERCASE | `VID` |
| 10 | `strategist` | 3-letter code of the strategist who wrote the brief (roster below) | UPPERCASE | `TED` |
| 11 | `designer` | 3-letter code of the designer who made the creative (roster below) | UPPERCASE | `OST` |
| 12 | `batch` | `BatchYYYYWeekWW` | as shown | `Batch2026Week27` |

**Modifier values:** `Unaware` · `ProblemAware` · `SolutionAware` · `ProductAware` · `MostAware`

Keep `hook` and `headline` short.

---

## Team Roster

The roster lives in `core/team.csv` (one place for every tool). New team member → add a row there **before** their first ad goes live. Codes are exactly 3 uppercase letters and never reused for a different person.

---

## Concept Code Rule

A concept = hook + video structure. New hook (different first 2 seconds) = new concept code, even if every other scene is reused footage. Never reuse a code across different concepts.

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

- [ ] Exactly 12 fields, no blanks, no hyphens inside a field
- [ ] `persona` is on the canonical Persona Taxonomy list
- [ ] `audiencecode` is a real code, not `LATAM`
- [ ] `conceptcode` is exactly 6 characters
- [ ] New hook got a new code
- [ ] `conceptname` is generic; sub-hook detail lives in `hook`
- [ ] `headline` and `angle` lowercase, `modifier` PascalCase
- [ ] `VID` / `IMG` uppercase
- [ ] `strategist` and `designer` are 3-letter codes from the roster
