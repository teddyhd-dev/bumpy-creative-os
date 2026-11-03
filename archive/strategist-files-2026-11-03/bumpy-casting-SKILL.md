---
name: bumpy-casting
version: 2.0.0
description: |
  Determines which profile nationalities and specific su_ids to use in Bumpy ad briefs.
  Uses three data signals combined: one-sided attractiveness (paid swipes), mutual match
  volume (both swiped right), and proximity connections (actual couples formed).
  India excluded from all casting per board decision. Use bumpy-casting-data.md as lookup.
---

# Casting Skill — Bumpy Profile Selection

---

## The Core Principle: Bilateral > One-sided

There are two types of attraction signals in the data:

**One-sided** (attractiveness scores): what a viewer swipes right on — desire, but not necessarily returned.
**Bilateral** (mutual matches + proximity): both parties swiped right AND formed connections. This is what actually converts in the real product.

**For ads, bilateral beats one-sided.** A profile that both the viewer finds attractive AND would realistically match with is more believable and more likely to convert. Use one-sided data only when bilateral data is absent.

---

## The Three Signals

| Signal | File | What it measures |
|---|---|---|
| Attractiveness score | bumpy-casting-data.md `attracted_to` | Paid users swiping right — desire |
| Mutual matches | bumpy-casting-data.md `mutual_matches` | Both swiped right — bilateral interest |
| Proximity connections | bumpy-casting-data.md `proximity_connects` | Actual cross-border couples formed |

**Priority:** mutual_matches + proximity > attracted_to alone.

---

## Casting Rule: Think in Audience Types, Not Just Countries

The hook person's nationality doesn't matter as much as their **look type**. A white male from US, GB, CA, AU, or DE reads the same to a Southeast Asian female viewer. Cast by audience type:

| Audience type | Countries it covers |
|---|---|
| White / Western Male | US, GB, CA, AU, DE, FR, IT, NL, SE, NO |
| Southeast Asian Female | PH, TH, ID, MY, VN |
| Latina Female | BR, CO, MX, CU, CL, AR, PE, VE |
| Western Female | US, GB, CA, AU |
| African Female | NG, KE, GH, ZA |

Apply the audience type → look up that segment in bumpy-casting-data.md → get RECOMMENDED profiles.

---

## Step by Step

### Step 1: Identify the viewer segment
- What is the hook person's type? → determines what profiles to show opposite them
- What is the target audience? → determines which data row to look up

### Step 2: Look up RECOMMENDED profiles in bumpy-casting-data.md
Find the viewer's segment. Read RECOMMENDED first — this is the bilateral sweet spot.
Fall back to attracted_to only if no bilateral data exists for that segment.

### Step 3: Pick 3–4 profile countries
Use RECOMMENDED nationalities. Pick the top ones by evidence strength.
Exclude IN (India) and RU (Russia) always.

### Step 4: Pick su_ids
For each country, randomly select 1 su_id from the top 3–5 listed.
Rotate across briefs — don't always pick #0. Pair each su_id with a generated first name.
If a nationality has no su_ids, write a full casting description instead (name, body type, hair, outfit, background).

### Step 5: Write the casting line
```
[PROFILES — 4 cards: Valentina (su_id 25033985) 🇧🇷 | Angel (su_id 24969654) 🇵🇭 | Camila (su_id 25032511) 🇨🇴 | Sofía (su_id 25668990) 🇲🇽]
```

---

## Payoff Scene Casting (AIRPORT, EATING, CAR, PROPOSAL)

Use the KEY BILATERAL PAIRS table in bumpy-casting-data.md.
These are the most proven cross-cultural couples on the platform — pick the pair that
matches your hook person's type and your audience's desired partner.

For a White/Western male hook targeting English-speaking audiences:
→ Payoff couple: White American male + Brazilian female OR White American male + Filipina female

For a SEA female hook:
→ Payoff couple: [SEA female] + White American/British male

For relatability personas aimed at men (Latina Lover, Passport Bro, Dating Fatigue):
→ the male is an everyday, average-build guy the viewer can see himself in, not a model.

---

## Hard Rules

- **Never cast IN (India)** in profiles, payoff scenes, or any generated face.
- **Never cast RU (Russia)** — Bumpy is a Ukrainian-founded company. Russia is excluded from all casting. "Slavic" = UA and similar.
- **Never use one-sided attraction alone** when bilateral data exists for that segment.
- **Rotate su_ids** — don't use the same profile IDs in every brief.
- **4 profiles is the standard** for a profile slider — one per recommended nationality.
- **Payoff scenes use one couple** — pick the single strongest bilateral pair for that audience.

---

## Quick Reference: Recommended Profiles by Audience Type

### White/Western Male viewer → show FEMALE profiles
🇧🇷 BR, 🇵🇭 PH, 🇨🇴 CO, 🇲🇽 MX
(bilateral sweet spot — top mutual matches AND proximity)

### Southeast Asian Female viewer (PH/ID/TH) → show MALE profiles
🇺🇸 US, 🇹🇷 TR, 🇰🇷 KR, 🇮🇹 IT
(US bilateral #1, TR strong for ID, KR confirmed proximity)

### Latina Female viewer → show MALE profiles
🇺🇸 US, 🇪🇸 ES, 🇹🇷 TR, 🇰🇷 KR
(US #1 bilateral by massive margin)

### Western Female viewer → show MALE profiles
🇰🇷 KR, 🇺🇦 UA, 🇺🇸 US, 🇮🇹 IT
(paid attractiveness primary signal — no mutual file data for this segment)

### African Female viewer → show MALE profiles
🇬🇧 GB, 🇺🇸 US, 🇹🇷 TR, 🇨🇦 CA
(bilateral confirmed GB + US)

---

## Key Bilateral Couples for Payoff Scenes

| Couple | Use when |
|---|---|
| 🇺🇸 White American male + 🇧🇷 Brazilian female | Hook = Western male, audience = English-speaking |
| 🇺🇸 White American male + 🇵🇭 Filipina female | Hook = Western male, audience = English-speaking (alt) |
| 🇬🇧 British male + 🇳🇬 Nigerian female | Hook = British male, audience = UK or African female |
| 🇹🇷 Turkish male + 🇮🇩 Indonesian female | Hook = Turkish/Middle Eastern male, audience = ID female |
| 🇰🇷 Korean male + 🇧🇷 Brazilian female | Hook = Korean male |
| 🇰🇷 Korean male + 🇵🇭 Filipina female | Hook = Korean male (alt) |
