---
name: bumpy-brief-brainstorm
version: 2.1.0
description: |
  Takes raw signals (screenshots, social trends, viral content, organic posts, images)
  and turns them into structured creative concept options ready to hand off to the
  bumpy-brief-writer skill. Input: screenshot(s) + user direction notes.
  Output: signal-by-signal options, each with exact on-screen text + scene-by-scene
  visual description using lego pieces from the scene library.
---

# Brief Brainstorm Skill — Signal → Bumpy Ad Concepts

---

## The One Job

The audience has **zero knowledge of Bumpy**. They don't know what it is, what it does,
or why they should care. They are mid-scroll. They have 1.5 seconds.

Every option must pass: **"Would a complete stranger immediately understand what's
happening and feel something in under 2 seconds?"**

If not, rewrite it.

---

## The Signal Is the Brief

Stay close to the signal. The reason signals work is the exact format, energy, and
emotion they carry. Options A and B should be close adaptations — same visual mechanic,
same emotional entry point, minimum distance from the original. Option C can take a
creative leap but must still be rooted in the signal's exact emotion, not invented from scratch.

**If your option could exist without having seen the signal, it's wrong.**

---

## Step 1: Decode Before Writing

Before writing any option, extract:

| What to find | Question |
|---|---|
| **The emotion** | What does the viewer feel in the first 1.5 seconds? |
| **Why the platform surfaces it** | Loopable? Relatable confession? Visual metaphor? Reaction-bait? |
| **The exact complaint or joke** | One sentence, precise |
| **The implied escape** | What is the content suggesting the viewer should do? |
| **Conversion gap** | How far is that implied escape from "try Bumpy"? |

Smaller gap = fewer scenes. Larger gap = more scenes to bridge it naturally.

---

## Step 2: Scene Count Follows the Narrative

No fixed number. Each scene earns its place or gets cut.

- **1 scene** — signal so directly implies Bumpy that one visual + one line closes it
- **2 scenes** — hook (pure relatable, zero brand) → redirect (Bumpy as answer)  
- **3 scenes** — hook → bridge → resolution (when the gap needs one more beat)
- **4+ scenes** — hook → bridge → lego sequence (proof, profiles, travel, payoff)

**Every scene must move the story forward exactly one step.**
If removing a scene doesn't break the narrative, remove it.

---

## Scene Library — The Lego Pieces

These are reusable scene building blocks. Mix and match based on what the narrative needs.
Do not default to any sequence — use pieces contextually.

### Hook Scenes (organic-feeling, no Bumpy branding)
- `[HOOK-WALK]` — walking feet or full body, airport or street, candid
- `[HOOK-SELFIE]` — talking to camera, car, room, plane — confessional energy
- `[HOOK-PLANE]` — person on plane, window seat, coffee, looking out
- `[HOOK-BALCONY]` — person staring from hotel/apartment balcony
- `[HOOK-POOL]` — filthy green pool, visual metaphor for local dating scene
- `[HOOK-POV]` — feet-first walking POV, face not shown
- New hook types can be created — name and describe them clearly

### Bumpy UI Scenes
- `[MAP SWIPE]` — world map swiping through countries, profile thumbnails pop up as you land on each country. Existing template asset, no generation needed.
- `[PROFILES]` — horizontal slider of 3–5 profile cards. Each card: photo + name + country flag. Casting depends on target audience — specify gender and nationality.
- `[ITS A BUMP]` — animation equivalent of "It's a Match" — appears after profile(s) are shown. Signals mutual interest. Existing UI asset.
- `[CHAT]` — in-app messages appearing one at a time. Specify sender/receiver and exact messages.
- `[MANY DM]` — scrolling inbox full of unread messages from multiple countries. Shows volume of interest.
- `[VIDEO CALL]` — split screen in-app video call. Specify who is large (main) and small (secondary).

### Payoff / Real-Life Scenes
- `[AIRPORT]` — two people meeting or reuniting at airport. Emotional, couple energy.
- `[EATING]` — couple eating local food together. Natural, warm, specific to a location.
- `[CAR]` — couple in car together, candid, intimate.
- `[TRAVEL]` — two people at a real-world location, landmark or local setting.
- `[PROPOSAL]` — guy proposing. High emotional payoff. Can be hook or endgame.

### End Scene
- `[ENDSCREEN]` — the existing endscreen visual + CTA text (CTA confirmed per persona). Always last. Never counted in gen tasks.

---

## Named Sequences

When a narrative calls for a longer arc, these named sequences can be dropped in as a block.
They are not mandatory — use them when the story calls for it.

### Love Story Arc
After the hook and redirect, shows the full relationship journey:
`[PROFILES] → [ITS A BUMP] → [CHAT] → [AIRPORT] → [EATING] → [CAR] → [PROPOSAL] → [ENDSCREEN]`

### Map Discovery Arc
Hook leads into the world map discovery, then profiles, then connection:
`[MAP SWIPE] → [PROFILES] → [ITS A BUMP] → [CHAT] → [ENDSCREEN]`

### Quick Proof Arc
Fast social proof without the full love story:
`[PROFILES] → [ITS A BUMP] → [CHAT] → [ENDSCREEN]`

These are lego groupings, not rules. Any piece can be removed, reordered, or replaced.
The proposal can be the hook. The chat can come before profiles. Read the narrative — don't serve the template.

---

## Step 3: Write the Options

For each signal: **3 options**. Each is a complete concept — visual + text, every scene.

```
### Option [Letter] — [2–3 word concept name]

Scene 1 — [SCENE TYPE]:
Visual: [specific, not vague]
Text: `[exact on-screen copy]`

Scene 2 — [SCENE TYPE]:
Visual: [specific]
Text: `[exact on-screen copy]`

[continue only as many scenes as the narrative needs]
```

**Option roles:**
- **Option A** — closest literal adaptation. Same format, same visual energy, minimum distance from the signal.
- **Option B** — same emotion, slightly different structural approach. Still clearly from the same signal.
- **Option C** — creative leap rooted in the signal's emotion. Bolder, unexpected — but still traceable back to what made the signal work. Not a different concept. Not an invention.

---

## Hard Rules — Clarity

- **Zero Bumpy knowledge assumed.** The redirect must explain what Bumpy is and what it does, cold.
- **No high-context lines.** "They're already on Bumpy" fails to a stranger. "Date someone from another country. Bumpy." works.
- **7th grader test.** Read every line out loud. Zero-context stranger immediately understands? If not, rewrite.
- **Logic check every transition.** Each scene must feel like a natural next step to someone who has never heard of Bumpy.
- **One idea per scene.**

## Hard Rules — Headlines

- **4–8 words per line.** Short. Fast. Striking.
- **Specificity converts.** Name a country. Use a flag 🇧🇷🇳🇴🇮🇹. Generic = invisible.
- **Never "nearby" or "near you."** Bumpy is international.
- **No vague verbs.** "Date someone from another country" beats "go international" every time.

## Hard Rules — Visuals

- **Scene 1 = organic energy.** No Bumpy logo, no brand colors, no polished production. Raw = trusted.
- **Match the signal's energy exactly.** Walking footage → walking footage. Car selfie → car selfie. Do not upgrade production — it kills the hook.
- **Visual and text amplify each other.** Not the same thing twice. Not contradictory.

---

## What Makes a Bad Option

| Bad pattern | Why it fails |
|---|---|
| "So I went international instead" | "International" is not a verb. Means nothing cold. |
| Scene 1 pitches Bumpy | Kills the relatability — it's just an ad immediately |
| Redirect assumes Bumpy knowledge | "They're on Bumpy" only works if you know what Bumpy is |
| Option C invents a new concept | Must still be from the signal's emotion, not a free idea |
| 2 scenes, same text | That's 1 scene's worth of content stretched thin |
| Generic destination ("abroad", "another country") when a flag works | 🇧🇷 always beats "abroad" |
| Upgraded production in hook scene | Polished = ad. Raw = trusted. Never upgrade Scene 1. |
| Illogical line ("flying to 🇸🇪 to meet someone I met on there") | A stranger stops believing it |

---

## After Approval → What Goes to Brief Writer

1. Approved concept (exact scenes + text)
2. Persona (canonical name)
3. Target audience code
4. Gender variant(s)
5. Specific country/flag for destination scenes
6. Batch identifier
7. VID only or VID + IMG on hook
8. V2 wanted or not
9. Strategist + designer codes
10. Endscreen CTA for this persona

---

## Concept Naming for File System

2–3 words, no spaces, describes the visual mechanic of the hook — not the headline:

`AirportWalk` · `PlaneSelfie` · `BalconyStare` · `CarConfession` · `DirtyPool` · `WalkingFeet` · `ReactionStitch` · `PlaneWindow`
