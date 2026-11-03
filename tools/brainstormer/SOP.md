# Strategist SOP: brainstorm → brief → submit

**How it works in one line:** the repo is the team's shared memory, your own Claude (or Codex) account is your
private workbench, and every job ends with one submission (a pull request) that the creative lead merges.

```
your account (workbench)   ── reads the latest ──►   repo main (the shared memory)
   brainstorm on a branch                                   ▲
   └──► pull request (your submission) ── creative lead merges ┘
weekly update (creative lead) ──► new tickets · results on every experiment and mind ──► the board
```

The conversation is not the record. Whatever you learn in a session (a decode, a belief, the audience's words, a good
signal, a correction) goes into the submission, so the next strategist starts from it.

---

## One-time setup (strategist, 10 minutes)
1. **GitHub:** send the creative lead your GitHub username. You'll get an invite to `teddyhd-dev/bumpy-creative-os`
   with write access: accept it from the email or github.com/notifications.
2. **Claude (or Codex):** make sure your account can start a session with a GitHub repository attached (the same kind
   of session the creative lead uses for the weekly update), signed in to GitHub with the account you were invited
   with. In Codex, connect GitHub and pick the repo.
3. **Your code:** check your 3-character code is in `core/team.csv` (ask the creative lead if not). Every ad name and
   submission carries it.
4. **The board:** open the ticket board link the creative lead shares.
5. **Remove old copies.** Delete the Bumpy `.md` files from your own Claude projects and any personal Bumpy skills
   in your account (e.g. an `ad-script-decoder` skill). The latest versions all live in the repo; an old copy is how
   wrong persona names and outdated rules sneak back in.

## Every brief
1. **Pick the ticket.** Tickets are shared out on Monday. On the board, open the ticket and press **Copy for the
   brainstormer**.
2. **Start a session** in your account with the repo attached. First message:
   `let's brainstorm T-691223` + paste the copied story, and say your code (`I'm JAC`).
   If the session doesn't pick it up by itself: `read tools/brainstormer/SKILL.md and follow it`.
   It checks nobody else has a branch for that ticket; if someone does, talk to them first.
3. **Brainstorm.** Claude opens with the situation, then asks you to decode any winner it doesn't know yet (send the
   first-second screenshot, or the video), reads the winners through the persona's mind, gives options scene by
   scene, and asks for inspiration: ad-library or social posts with good numbers (views, likes, shares, comments,
   days running) and how you'd turn them into an ad. Push back, brain-dump, correct it: corrections that will come up
   again become rules for everyone.
4. **Approve the brief.** Claude writes it in the Notion format, checks every ad name and the concept code against
   what exists, and fixes clashes before showing it.
5. **Submit.** Say `approved, submit it`. Claude saves the experiment (hypothesis, prediction, options not chosen,
   the brief), the persona diary entries and anything learned, runs the checks, and opens the pull request. If it
   can't open it, it gives you a link: open it and press **Create pull request**.
6. **Paste the brief into Notion** and add references there, as before.

That's it for you. After that:
- the creative lead merges the pull request; from then on every session sees your work;
- the next board sync shows the ticket as **Briefed**;
- once the ads run, Monday's update writes the week-1 read and the week-4 result onto your experiment and into the
  persona's mind;
- at the retro, ask a session `write the lesson for EXP-2026-11-09-k4Rm9p: …`; it submits that the same way.

**No brief today?** (no agreement yet, or you only decoded or researched) Say `submit what we learned`. It goes in as
a "learnings" pull request. Nothing learned stays in a chat.

## Rules
- Never push to `main`; a brainstorm always ends in a pull request.
- Lists every tool shares live in `core/` (personas, team, angles, naming, brand rules). Don't change or copy them;
  ask the creative lead.
- One ticket (or one group of tickets) = one branch = one pull request.
- Every ad name goes through the check Claude runs (`checks/new_concept.py`). A **note** (e.g. an angle not on the
  list yet) is fine; tell the creative lead.
- Brand rules (`core/brand.md`): never "nearby", never Russian or Indian casting, one persona per creative, confirm
  the endscreen CTA.

## When something goes wrong
| What you see | What to do |
|---|---|
| "Push rejected" or "conflict" | Ask the session: `rebase on main and keep both sides`. |
| A red ✗ on the pull request | In the same session: `the checks on the PR failed, fix them`. |
| The session can't reach the repo | Check your invite is accepted and GitHub is connected; or use the fallback below. |
| You worked in a plain chat without the repo | Fallback: on GitHub, Issues → New issue → **Brief submission**, paste the brief and what you learned. The weekly update files it. Use it rarely: without the repo you also don't see the latest mind. |

---

## Creative lead
**One-time**
1. Add each strategist: repo **Settings → Collaborators → Add people**, role **Write**. Add their code to
   `core/team.csv` before their first brief.
2. Protect `main`: **Settings → Branches** (or **Rules → Rulesets**) → require a pull request before merging, require
   review from Code Owners, require the **validate** check to pass. Allow yourself to bypass, for the weekly update.
3. Share the ticket board with the team.

**Each week**
- **Review submissions.** The checks are green; the hypothesis is one line and checkable; only `brain/`,
  `tools/brainstormer/` and at most one new row in `core/concepts.csv` changed (anything else in `core/` or
  `contracts/` belongs in its own pull request). Merge.
- **Two submissions clash** (both touched the same file): merge one, then comment on the other asking its strategist
  to have their session rebase on `main`.
- **Before the weekly update**, merge the approved submissions; the update session files any fallback issues.
- **Improving the brainstormer** (questions, craft files, playbook): also through pull requests, with a line in
  `tools/brainstormer/CHANGELOG.md`.
