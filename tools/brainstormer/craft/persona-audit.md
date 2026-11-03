# Persona audit

Used when the strategist asks "what angles haven't we tried?", "audit this persona", or when a ticket's mind has
no clear winner to build on (playbook move: new angle). From the strategists' `persona-ad-audit` skill (original in
`archive/strategist-files-2026-11-03/`), adapted to read the shared memory instead of asking for it.

Four stages, held together: research must visibly show up in the gap analysis and in the copy, or it was
decoration. Beautiful research followed by generic options is a failed run.

```
1 Ad audit → 2 Deep persona research → 3 Gap analysis → 4 Angle and copy options
```

## 1. Ad audit
**Input:** the mind's ads ranked by spend. Take them from the mind's facts block (#1 history with full ad names),
the creatives' "Where it ran" tables and the ticket story; ask the strategist only for what's missing (snapshots,
scripts). When average watch time is very low (about 2 seconds), the first frame is the whole ad: say so and don't
invent a body breakdown.

For each ad, exactly two things:

| Ad (by spend) | Awareness | Angle |
|---|---|---|

- **Awareness:** the five levels, which are also the ad name's `modifier` values: `Unaware` (no problem, no
  category: pure fantasy) · `ProblemAware` (names the pain) · `SolutionAware` (says dating abroad works, no brand) ·
  `ProductAware` (Bumpy named or shown) · `MostAware` (Bumpy + clear claim + direct CTA).
- **Angle:** the psychological mechanism and what it lands on, as one thing: "grievance validation, no ask" vs
  "rational value comparison → direct CTA". Name it precisely, never "emotional". Most sets have very few angles
  landing on a concrete claim or CTA; say so when true, it's usually a gap.

Stay strategic here; hook mechanics are `craft/decode.md`.

## 2. Deep persona research
Start from the mind (`mind.md`: who they are, beliefs, their words) and add to it; don't start from zero.

**Required shape:**
1. **Segment split:** most personas are 2+ people under one label. A short handle each and one line on what makes
   their entry psychology different.
2. **Psychology zoomed in, one paragraph:** base human psychology → gender-specific if relevant → this persona.
3. **The true why, numbered and blunt:** 4–6 statements of the real motivation, past the flattering version. If a
   line still sounds noble, push one layer more honest.
4. **The engine:** one sentence naming the single driver everything connects back to. Every option in stage 4 is
   checked against it.

Also connect, as one picture: desires, dreams, pains; why the winning ads won (which driver they hit).

**Go where they talk, in their own words.** Search forums, subreddits, comment sections, niche publications by or
about them. Keep:
- their self-identity, and the labels they reject (misreading this repels them);
- their vocabulary, literally (it must survive into stage 4);
- who they really are, especially where it contradicts the stereotype our ads assume;
- the segment our ads serve today and the one they miss.

**Save it:** quotes with source and date (original language + English gloss) go to "Their words"; findings go into
a `research` entry in `history.md` with links; a changed belief goes through a `belief` entry first (contract
`contracts/mind.md`).

## 3. Gap analysis
A literal diff between what our ads said (stage 1) and what research says could be said:
1. Awareness coverage: which of the five levels are covered, empty or thin.
2. Angle coverage: every angle used, then every angle research shows as available but unused. Long, not 2–3 items.
   Call out the ratio ("5 fantasy angles landing on nothing, 1 landing on a concrete claim").
3. Segment coverage: which segments our visuals and tone serve, which are missing.
4. Vocabulary and trust: is their own language anywhere in our creative, or do we talk *about* them? Usually a
   free, high-leverage fix.

State the **single biggest gap in one plain sentence** first: the one the creative lead can repeat from memory.

## 4. Angle and copy options
As many as the gaps support. For every option:
- **Gap it fills** (one line, referencing stage 3) · **Awareness level** · **Angle** (mechanism + landing point,
  e.g. "SMV-mismatch grievance → risk-reversal offer") · **In-ad copy example** (an actual line, not a description).

Copy standards: use their real vocabulary where it fits (sparingly enough not to lose the quieter majority); never
write copy that could sell any dating app; name their situation or self-label. Group by awareness level, and say
when an option blends two levels or angles. Test: would this person feel called out, in a good way, or scroll past
thinking it's not for them?

Chosen options go on into `craft/options.md` (scenes) and the brief. The audit itself is summarised in the
experiment record's Evidence and "Options not chosen".
