# Bumpy — Ad Creative System
## Project Description

This project produces paid ad creatives for **Bumpy**, an international dating app. Every session starts somewhere in this chain:

**Analyze → Signal → Headline → Brief** (plus Localize and Humanize when needed)

---

## The App

**Bumpy** is an international dating and social app. Cross-border matching is the core mechanic — users from completely different countries connect. Distance is the feature, not a bug. **Never use "nearby" or "near you" in copy.**

Full app knowledge, personas, working headlines and proven formulas live in `bumpy-knowledge.md`. Casting data lives in `bumpy-casting-data.md`.

---

## The Workflow

### Stage 0 — Analyze winners
- **One ad, hook or script** ("why does this work?", "decode this") → `ad-script-decoder-SKILL.md`
- **A batch of top spenders for one persona** ("what angles haven't we tried?", "audit this persona") → `persona-ad-audit-SKILL.md`
- **Meta headline / primary text** performance → rules in `bumpy-learnings.md` (Spend → ROAS → IPM)

### Stage 1 — Signal
Signals are raw material: TikTok captions, comments, Reddit posts, ad library copy, organic posts, reviews, screenshots.

- **Refreshing an existing persona** — new hooks for a known angle
- **Opening a new persona** — building a new angle from scratch

Claude decodes the signal, maps the persona's desire + objection + dream outcome, and turns it into concept options with `bumpy-brief-brainstorm-SKILL.md` (3 options per signal, scene by scene).

### Stage 2 — Headline
Using `ad-copywriter-SKILL.md` (read its Bumpy override first):
- Viral phrase (formula shown)
- Headline options (winner + alts)
- Why it stops the scroll (one sentence)

Rules: 4–6 words, desire first, clear to a 7th grader, meta-safe, clear over clever, a distance word (never "nearby").

### Stage 3 — Brief
Using `bumpy-brief-writer-SKILL.md` (v5), Claude turns the approved concept into a Notion-ready `.md` brief: Notion task name, structure, scene lines with on-screen text, v5 file names, casting (via `bumpy-casting-SKILL.md`), task weight, V2 versions if asked. Multi-language sets go in one Mega-Brief grouped by asset type.

### Localize / Humanize
- Translating ad scripts → `ADS_LOCALIZATION-SKILL.md`
- Any copy before delivery → `humanizer_SKILL.md` (remove AI patterns)

---

## How to Start Any Session

**Analyzing winners:** paste the ads (ideally ranked by spend) and name the persona.

**Giving signals:** paste the raw copy/screenshots. Claude decodes them and produces concept options. No setup needed.

**Briefing an approved concept:** give the headline + scene structure + persona + concept name + benchmark + batch + VID/IMG + strategist/designer + V2 yes/no. Claude asks for anything missing, then delivers the brief.

**Refreshing a persona:** name it (e.g. "Passport Bro refresh") and give new signals.

---

## Key Files

| File | Purpose |
|---|---|
| `PROJECT.md` | This file. Workflow and file map |
| `bumpy-knowledge.md` | Personas, working headlines, proven formulas, brand rules |
| `bumpy-learnings.md` | Rules and findings from past sessions (feedback, Meta copy data, production lessons) |
| `bumpy-casting-data.md` | su_ids, bilateral pairs, recommended nationalities per audience |
| `bumpy-casting-SKILL.md` | How to pick profiles and payoff couples from the data |
| `ad-script-decoder-SKILL.md` | Decode one signal/ad: hook, mechanism, conversion gap, persona |
| `persona-ad-audit-SKILL.md` | Audit a persona's winners, research, gap analysis, new angles |
| `bumpy-brief-brainstorm-SKILL.md` | Signal → 3 concept options, full scene library and named sequences |
| `ad-copywriter-SKILL.md` | On-screen headline rules and viral phrase formula |
| `bumpy-brief-writer-SKILL.md` | Brief format, v5 file naming, persona list, roster, task weight |
| `ADS_LOCALIZATION-SKILL.md` | Translating ad scripts per language/platform |
| `humanizer_SKILL.md` | Remove AI writing patterns before delivery |

---

## What Claude Should Never Do

- Use "nearby" or "near you" in any copy or brief
- Cast Russian (RU) or Indian (IN) profiles, faces or locations
- Mix personas in one creative
- Invent a persona name outside the Canonical Persona List
- Assume the endscreen CTA — confirm it per persona
- Write headlines longer than 6 words without flagging it
- Leave any field blank in a delivered brief, or guess a strategist/designer code
- Reuse a concept code across different hooks
- Split a multi-language brief into one file per language
- Put persona logic, casting reasoning or other rationale inside a designer brief
