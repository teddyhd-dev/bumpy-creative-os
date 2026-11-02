# Refresh playbook

Every option the brainstormer proposes is one of these moves. The move is written into the experiment
record (`move:`), so over time we learn which move works for which mind.

| Move (`move:` value) | What changes | What stays | When it fits |
|---|---|---|---|
| **Same message, new visual** (`same-message-new-visual`) | The first-second visual: actor, setting, prop, framing | Concept, message, headline | The #1 is fading but its message still lands. Meta rewards ads that look different: a new visual reaches people the old one never stopped. E.g. *wanted*: new actor, same sign. |
| **Same message, new format** (`same-message-new-format`) | The format or style: UGC, carousel, product demo, founder, static, talking head, text-on-video | The winning message theme | The message is proven but the format is worn. Pick formats that won in other minds (see each creative's "Where it ran") or in strong ad-library / social references. |
| **Same visual, new angle** (`same-visual-new-angle`) | The angle or message theme | The hook visual or concept style | The visual still stops thumbs but the promise has tired. Ground the new angle in the mind's beliefs and its own words (forums, comments: quote them). |
| **New angle** (`new-angle`) | Everything | Only the mind | No winner to build on, or the mind's beliefs suggest an untested desire. Needs inspiration from the strategist (ad library, social, brain dump). |
| **Proven elsewhere** (`proven-elsewhere`, J1) | The audience | The concept, localised | A concept is #1 in another mind or language and never ran here (the ticket's `j1` list). Localise the words; keep the hook. |
| **Past winner, new form** (`past-winner-new-form`, J2) | The execution of a past #1 of this adset | Its core idea | A past #1 here faded long ago; its idea may be fresh again for new people. |

## Rules from our data (back-tests on our exports since Dec 2025)
- **One concept per refresh, 3+ variants per adset.** A new concept with 3+ variants in the adset became
  #1 40% of the time vs 15% with 1–2. Variants: new hook, new text, re-cut, re-sequenced opening.
- **Milk every generation.** Plan the extra cuts in the brief: start at the reveal, swap the on-screen text,
  reorder scenes, make the IMG from the strongest frame.
- **Spread one concept across the mind's adsets.** A concept lands in a median 3 adsets; in 5+ adsets it
  became #1 somewhere 71% of the time vs 25% in one. Each adset keeps its own result.
- **Localise per language; one brief covers both OS.** Results differed by language for 42% of concepts
  tried in 2+ languages; iOS and Android agreed 80% of the time.
- **Judge at week 1, decide at week 4.** 20%+ of the adset's spend in week 1 usually means a future #1.
  A third of winners started under 5%: keep quiet ads on.
- **Brief the successor early.** A #1 leads a median 3 weeks and ROAS slides from week 3; a refresh takes
  about 2 weeks. Due tickets exist for this.
- **Strikes count only when the adset was under the bar.** Missing against a healthy #1 is a foul.

## Rules learned
Add a line when a strategist corrects the brainstormer on something that will come up again
(date · who · rule).

- 2026-11-02 · TED · A concept moved into another persona's adset (proven elsewhere) gets its own copy named for
  that persona, same concept code, so each audience is credited correctly.
- 2026-11-02 · TED · Pick new concept codes from `core/concepts.csv` (unique ignoring letter case); write the
  concept name exactly as it is there, and put scene detail in the hook field.
