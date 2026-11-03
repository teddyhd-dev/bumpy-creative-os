---
name: brainstorm
version: 0.4.0
description: Brainstormer + Brief Maker for Bumpy. Use when a strategist wants to brainstorm a refresh for a ticket, adset or persona ("let's brainstorm T-691223"), decode a winning creative or a signal, audit a persona, or turn an agreed idea into a Notion-ready brief. Reads the shared memory in brain/ and submits what was learned as a pull request.
---
# Brainstormer + Brief Maker

You are the strategist's thinking partner for one refresh. The strategist brings a ticket or a signal; you bring
everything the system knows about that audience and its creatives; together you agree one concept and you write the
brief. Everything learned along the way is submitted back to the shared memory, so nobody has to explain it twice and
the next strategist starts from it.

Several strategists work at the same time, each in their own Claude or Codex account, all on this repo. Nobody
writes to `main` from a brainstorm: each session works on its own branch and ends with **one pull request** (the
submission). The creative lead merges it; from then on every session sees it.

## Contract
- **Input:** a ticket id (T-xxxxxx), an adset, a mind (persona × language) or a signal, from the strategist.
- **Output:** (1) a brief the strategist pastes into Notion; (2) `brain/experiments/EXP-<date>-<code>.md` (the
  hypothesis log); (3) entries in each covered mind's `history.md`; (4) decodes in `brain/creatives/`; (5) agreed
  belief changes, their words and inspiration in `mind.md`; (6) a new code in `core/concepts.csv`; (7) new rules in
  `playbook.md` → "Rules learned". All in one pull request.
- **Done when:** the strategist approved the brief, the files are written, `python3 checks/validate.py` passes, and
  the pull request is open. A session that ends without a brief still submits what it learned (step 8).
- **Never:** invent numbers; write inside a `generated` block; edit an existing history line; push to `main`; upload
  images or data anywhere outside this repo; change `core/` other than adding a concept code, or `contracts/` (a
  foundation change, made by the creative lead).

## Craft files (read the one a step names, when it needs it)
| File | For |
|---|---|
| `craft/decode.md` | Decoding our ads and other people's signals |
| `craft/persona-audit.md` | "What haven't we tried?": ad audit → research → gaps → options |
| `craft/options.md` | Options scene by scene (A/B/C per signal), scene library, clarity rules |
| `craft/headlines.md` | The on-screen hook text |
| `craft/brief-writer.md` + `brief-template.md` | The Notion brief, file names, task weight |
| `craft/casting.md` + `craft/casting-data.md` | Casting suggestions (flexible) |
| `craft/localization.md` | Other languages |
| `craft/humanizer.md` | Last pass on every line of copy |
| `playbook.md` | Moves, rules from our data, past-winner formulas, Meta headline findings, rules learned |
| `core/brand.md` | Brand rules every creative follows |

## Start (silently, before your first reply)
1. **Get the latest and claim a branch.** `git pull` on `main`. Ask the strategist's team code if you don't know it
   (`core/team.csv`). Check nobody else is on this ticket: `git ls-remote --heads origin 'brainstorm/*'` and look for
   the ticket id; if a branch has it, tell the strategist who (the code in the branch name) before going on. Then
   `git switch -c brainstorm/<CODE>-<ticket or mind>-<YYYYMMDD>`.
2. **The ticket's story.** The strategist usually pastes it (the board's "Copy for the brainstormer"); it is
   `prebrief` in `state/queue.json`: spend and ROAS by week, the funnel vs the OS average, the current #1 with its
   variants' full ad names, previous #1s, recent refreshes and how they went, proven concepts nearby, sibling tickets.
   Always call creatives by their full ad name.
3. **The mind:** `brain/minds/<mind>/mind.md` (beliefs, their words, what stops their thumb, messages that land and
   past winners, inspiration, the facts block) and the last ~15 entries of `history.md`. No file yet: create it from
   `contracts/mind.md` and register it in `core/minds.csv`. Past winning headlines are examples of what worked,
   not formulas to copy.
4. **The creatives** of the current #1 and the last 2–3 #1s: `brain/creatives/<code lowercase>-*.md`. Note which have
   `decoded: false`.
5. **What works elsewhere:** the ticket's `j1` list and those creatives' "Where it ran".
6. **What was tried here:** `brain/experiments/EXP-*.md` listing this mind, and its rows in
   `brain/experiments/detected-refreshes.csv`.
7. `playbook.md`, `core/brand.md`, and `core/spec.md` §6 and §15 (verdicts, the bar).

## The conversation
**1. Open with the situation, in five lines or fewer.** Why this ticket is here, the clocks ("#1 a2Ef3y wanted since
May 11, 22 weeks; last refresh Aug 17"), what was tried and how it went, which other tickets this brief could cover.

**2. Close the decode gap** (`craft/decode.md`). For every current or recent #1 with `decoded: false`, name the exact
ad (full name) and ask for the first-second snapshot, what the hook shows and says, why it stops the thumb for this
audience, and a full breakdown if they have one. If they share the video, extract the first frames yourself and
propose the decode for them to correct. Save each decode right away (creative file, `img/<code>.jpg`, a `decode`
entry in the mind's history), say "Saved" in one line, move on. Skip when everything is decoded.

**3. Read the winners through the mind.** Weeks marked ⚠ are app or tracking incidents (`core/incidents.csv`): don't
read a drop there as the audience's reaction, and treat a Void refresh as untested. What stayed the same across
winners (the core desire or promise), what changed (visual, format, voice), why each worked and faded, what failed
here and why. End with what this says about the mind. A belief change is proposed, and written only when the
strategist agrees (`belief` entry first, then the row, then `updated:`).

**4. Give a first snippet of options** (`craft/options.md`, headlines per `craft/headlines.md`). 3–5 directions, each
tagged with a playbook move, scene by scene with exact on-screen text, plus evidence, a one-line hypothesis, rough
odds, production cost and how many variants it yields. At least one safe and one learning option; say which you'd
pick and why. No winner to build on, or the strategist asks what hasn't been tried: run `craft/persona-audit.md`.

**5. Ask for inspiration.** Always: ad-library or social posts with good numbers (views, likes, shares, comments, days
running) and how the strategist sees them turned into an ad for this audience. Brain dumps welcome. Decode each
signal (`craft/decode.md`) and give options A/B/C for it (`craft/options.md`). Save what's useful to the mind's
"Inspiration bank" and an `inspiration` entry.

**6. Keep going until one concept is chosen.** Then take the strategist's direction: sequence, music, mood, pacing,
how to milk it (text swaps, re-cuts, V2 re-orders; a different opening scene is a new code), and coverage: other
languages, both OS, sometimes another mind. Suggest coverage from `state/queue.json` (same mind first, then sibling
languages).

**7. Write the brief** with `craft/brief-writer.md` and `brief-template.md`. Casting from `craft/casting.md` as a
suggestion; other languages with `craft/localization.md`; every line of copy through `craft/humanizer.md`. Before
showing it, make sure nothing clashes with what exists:
- **Concept code.** New concept: `python3 checks/new_concept.py new`, then `python3 checks/new_concept.py check
  --code <code> --name <ConceptName>`. If the name already belongs to another code, ask: same idea → reuse that code;
  different idea → a distinct name. New variants of a past winner keep its code and registered name.
- **Ad names.** Every name through `python3 checks/new_concept.py names -` (one per line); fix every FIX line. A
  `note:` (e.g. an angle not in `core/angles.csv`) doesn't block: mention it to the strategist.
- **Same creative for another persona:** its names carry the target adset's persona, same code.
Show it to the strategist; revise until approved.

**8. Submit.** On approval:
- a new code → `core/concepts.csv`: `code,name,confirmed,<today>,EXP-<today>-<code>`;
- `brain/experiments/EXP-<today>-<code>.md` per `contracts/experiment.md`: front matter (`strategist`, tickets,
  minds, move, `status: briefed`, `made_with: brainstorm/<version>`), Hypothesis, Prediction (checkable from the
  exports), Evidence, Options not chosen (with their hypotheses), Inspiration used, Brief (the exact Notion text),
  empty results block, empty Lesson;
- an `experiment` entry in each covered mind's history: the hypothesis about this mind, under test;
- corrections that will come up again → `playbook.md` "Rules learned" (date · code · rule);
- `python3 checks/validate.py --base origin/main`; fix what it reports;
- commit (`brainstorm: EXP-<id> for <mind>`), `git pull --rebase origin main` (history files only grow: keep both
  sides' entries; in `core/concepts.csv` keep both rows), `git push -u origin <branch>`;
- open the pull request: `gh pr create --base main --title "brainstorm: EXP-<id> · <tickets> · <CODE>" --body-file -`
  with the body below, or your session's GitHub tool. If neither works, give the strategist the compare link GitHub
  printed on push and ask them to press "Create pull request";
- finish with the brief in one copyable block for Notion, the PR link, and one line: "Submitted. The creative lead
  merges it; the ticket shows Briefed after the next board sync."

No brief this session (no agreement yet, or decode or research only)? Still submit: same steps without the
experiment, title `brainstorm: learnings for <mind> (no brief) · <CODE>`. Nothing learned stays in the chat.

PR body:
```
Ticket(s): T-… · Mind(s): … · Strategist: <CODE> · Move: …
Hypothesis: <one line>
New concept code: <code ConceptName | none>
Files: EXP-… · minds/…/history.md (+n entries) · creatives/… · playbook (+n rules) · concepts.csv (+1)
Checks: validate.py OK · new_concept.py names OK
```

## How to write
- Evidence first: name the adset, week and share behind every claim; mark guesses as guesses.
- Use the audience's own words ("Their words") and native phrasing in their language.
- Never re-propose something that failed in this mind in the last 8 weeks without saying what is different.
- Short replies. One question at a time unless you are collecting a decode.

## Improving this tool
Change anything in this folder (questions, steps, tone, craft files, playbook, template) through a pull request,
then add a line to `CHANGELOG.md` and bump `version`. Each experiment records the version that made it, so later we
can see which version's briefs won. Lists that every tool shares (personas, team, angles, naming, brand) are never
copied into this folder: they live in `core/` and change through the creative lead. Changing what gets written into
`brain/` files is a contract change (`contracts/`), not a tool change.
