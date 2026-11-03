# Bumpy — Learnings From Past Sessions
last updated: Nov 2026

Rules and findings that came out of working sessions but weren't yet written into the skill files. Read alongside `bumpy-knowledge.md`. If a rule here conflicts with a skill file, the newer date wins; flag it to the team.

---

## How to take feedback (the meta-rule)

Don't turn every correction into a hard rule. First understand *why* the feedback was given. Most corrections come back to the same thing: understand the signal. If you understand it, you won't overbuild. It's a simple job; don't overthink or overcomplicate.

- Stay close to the signal. If an option could exist without having seen the signal, it's wrong.
- Logic-check every line. Example of a rejected line: "Now I'm flying to 🇸🇪 to meet someone I met on there." It doesn't follow.
- Two scenes with the same text are one scene.
- Short and striking beats long and high-context, even when the structure has many scenes.

---

## Briefs and production

- **Mega-Brief:** a set that spans languages/markets is one file, grouped by asset type (Step 1 Generation, Step 2 Assembly). Never one file per language. Designers work in Premiere by visual and only swap text.
- **No rationale in briefs.** Cast, on-screen text, file name. That's it.
- **Re-sequenced scenes that open differently = separate concepts**, each with its own code. Same footage, so no extra generation; only video output goes up.
- **Statics from video stills** (same still + headline) cost 0 extra generation; they add to Image output only.
- **Reused clips with handwritten text** (a note, a sign) can't be translated by overlay. Flag to production if a language needs it changed.
- **Map Swipe / UI frames:** check the visible pins. One frame shipped centered on India; India and Russia must not appear.
- **Batch week** follows the launch date's ISO week. If an old file name carries an older batch, use the current batch and say so.

---

## Copy craft (on-screen and UGC scripts)

- **UGC talking-head scripts need natural imperfection.** Thoughts run into each other; no full stop that kills momentum mid-thought. Rejected drafts were "long and choppy, not human." Write like someone thinking out loud, not performing.
- **One small specific moment beats a list.** (One night, one topic, one reaction.)
- **One CTA, not two stacked** at the end.
- **The hook must touch the real wound.** A generic social dynamic ("popularity decides what's cool") was rejected as not triggering. Go one layer more personal.
- **Gender-neutral callouts in ES/PT:** masculine plural reads as mixed. Locked phrasing: `Mis cristianos solteros…` / `Meus cristãos solteiros…`.
- **Non-native languages** (Turkish especially): mark lines for a native check before shipping.
- **"Nearby" used contrastively** ("boys only date nearby, men date abroad") is still flagged. The user decides.

---

## Meta primary text & headlines (from Oct 2026 internal data + competitor review)

Metric order: **Spend → ROAS → IPM**. Meta Ad Library impression rank = proxy for what Meta chooses to spend on. Internal data (one week, ~$74k headline spend, account ROAS 0.18 / IPM 0.59) showed:

- **What Meta spends on ≠ what pays.** Top two spenders were among the worst payers. Target lines Meta spends on *and* that clear ROAS. Best general lines at scale: "Done With Local Dating? Try the World." (IPM 1.15), "Love Beyond Borders." (most installs).
- **Abstract borders/culture lines beat naming a nationality** in headlines (0.25 ROAS / 0.83 IPM vs 0.18 / 0.49).
- **"Not local" inversion is the strongest signal.** JP 運命の人は近くにいるとは限らない (1.07 ROAS / 2.57 IPM); PT "Talvez Ele Não Seja Local". "Not local" works; "foreigner" flopped (0.04).
- **Numbers don't work in headlines** ("200+ countries", "20M singles": weakest theme).
- **No CTA in the headline.** It sits beside the Install button; "Download Bumpy" in the headline did worse.
- **Three-word "X. Y. Z." lists fail** ("Loyalty. Beauty. Culture." 0.12).
- Emoji slight lift; questions get higher IPM at the same ROAS; brand name in headline adds nothing.
- **Natural sentence length beats a clipped slogan.** Don't cut lines short to sound punchy.
- **End on her, not on an instruction.** "Try dating in Asia" is flat; "She might be in Asia." keeps the possibility.
- **A "worth it" sacrifice must be specific and persona-true** ("worth learning a whole new alphabet for" > "worth the long flight").
- **Mix method:** keep the exact phrase from a current winner when it already matches a formula ("maybe she never was"); rebuild the rest.
- **"#1" claims need a source** or Meta may reject.
- Primary text: only ~125 characters show before "…more", so the first line must work alone.

---

## Numbers in use (verify before public use)

- US male match rate ~20% on Bumpy vs ~5% on local apps (CEO figure). Confirm Bumpy's calculation matches (matches ÷ likes sent) before it goes in public ads.
- Top 5 countries for US male: PH, BR, ID, CU, CO.

---

## Related files that live elsewhere (ask the owner if you need them)

- `bumpy-naming-convention.md` (v5) and `bumpy-ad-naming-from-screenshot.md` — full naming spec; the essentials are already in `bumpy-brief-writer-SKILL.md`
- Campaign/adset naming convention with the Persona Taxonomy
- `meta-copy-competitor-log.md` — full Meta copy log with per-persona lineups
- `okr-generator-SKILL.md` — weekly OKR table from a creative-team dump
- `aso-naming` skill — App Store screenshot file names
- Wonder (sister brand, gay international dating app) uses the same workflow; its endscreen is `Meet gay people worldwide` (PT: `Conheça pessoas gays do mundo todo`)
