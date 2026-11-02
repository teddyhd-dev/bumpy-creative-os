# Architecture

## The idea
One shared memory, several small tools, one foundation underneath.

```
            ┌──────────────── tools (each tuned in its own session) ────────────────┐
            │  ticket board    brainstormer + brief maker    weekly PDF    dashboard │
            └───────┬───────────────────┬─────────────────────────┬──────────────────┘
                    │ read/write only through the brain, in the shared formats
            ┌───────▼───────────────────▼─────────────────────────▼──────────────────┐
  exports → │ engine  →  brain/ (minds · creatives · experiments)  +  state/ (tickets)│
            └───────────────────────────────▲────────────────────────────────────────┘
            ┌───────────────────────────────┴────────────────────────────────────────┐
            │ foundation: core/ (rules, naming, team, minds registry) · contracts/ · checks/ │
            └─────────────────────────────────────────────────────────────────────────┘
```

Tools never call each other. They meet in `brain/` and `state/`, in formats fixed by `contracts/`. That is
why you can rebuild the brainstormer without touching the report: the report only cares that experiment
files keep their format.

## Units and IDs (what links everything)
| Thing | ID | Example | Lives in |
|---|---|---|---|
| Mind (an audience) | `<Persona>-<LANG>` | `LatinaFemaleLover-ES` | `brain/minds/<id>/`, `core/minds.csv` |
| Concept (a creative and its variants) | concept code from the v5 ad name | `k4Rm9p` | `brain/creatives/k4rm9p-datingcontest.md` |
| Experiment (one agreed brief) | `EXP-<date>-<code>` | `EXP-2026-11-09-Zq7Lm2` | `brain/experiments/` |
| Ticket (an adset needing creative) | `T-` + 6 digits of the adset id | `T-691223` | `state/queue.json`, the ticket board |
| Adset | Meta adset id | `120246656912230469` | the exports |
| Person | 3-letter code | `TED`, `OST` | `core/team.csv`, the v5 ad name |

The v5 ad name carries persona, language, concept code, strategist, designer and batch, so the Monday run
can attach every result to its experiment, mind and people without anyone typing a status.

**Why persona × language is the unit.** Adsets are containers that get rebuilt and switched off (16 of 20
v8 adsets are gone); a lesson filed under an adset dies with it. Languages behave differently (42% of
concepts tried in 2+ languages won in some and not others) while iOS and Android mostly agree (80%). So one
mind per persona × language, both OS together, and the adset history is rebuilt from the exports every week.

## Data principles
1. **One home per fact.** Every fact is written in one place; every other place is a generated view.
2. **Latest on top, nothing lost.** `mind.md` holds the current understanding; `history.md` keeps every
   observation and change of belief, oldest first, append-only (the validator fails any edit to an old line).
   Git keeps every version of every file.
3. **Human and machine parts are separated.** Inside a file, the engine writes only between
   `<!-- generated:start x -->` and `<!-- generated:end x -->`; people and the brainstormer write the rest.
   Each contract's `written_by` says who owns which part.
4. **Events, then beliefs.** Results (new #1s, verdicts) are appended to the mind's history automatically.
   Beliefs change only with a human in the loop (a `belief` entry, then the row in mind.md).
5. **One file per record** (experiment, creative) so several people can work at once without conflicts.

## Flows
- **Monday (engine):** exports → tickets and verdicts → `state/queue.json` → ticket board;
  facts block of every mind and creative; results and status of every experiment; `new-1` and `result`
  entries in the minds' histories; `reports/<week>/report.json` → the PDF.
- **Brainstorm (strategist + brainstormer):** ticket → read mind, winners, experiments → ask for missing
  decodes and inspiration → options by playbook move → brief → `EXP-…md`, `experiment` / `decode` /
  `belief` / `inspiration` entries, decodes in `brain/creatives/` → commit. The ticket shows "Briefed".
- **Result → learning:** next Mondays fill the experiment's results and the mind's history; at the retro the
  strategist and designer write the Lesson; the next brainstorm on that mind starts from it.

## Tuning a tool (the normal path)
Open a session on one tool ("work on tools/brainstormer"). Change anything inside `tools/<tool>/`: prompts,
steps, questions, templates, style. Bump the tool's `version`, add a line to its `CHANGELOG.md`, run
`python3 checks/validate.py`, commit as `<tool>: …`. Other tools are untouched by construction. Records
carry `made_with: <tool>/<version>`, so later we can compare which version's briefs won.

## Changing the foundation (affects every tool)
Needed when a tool must store something new or differently, or when a rule in `core/` changes.
1. Edit the contract in `contracts/` (bump `version`) or the rule in `core/` (log it in `core/decisions.md`).
2. Update `checks/validate.py` only if the change needs a new kind of check (field and section lists are read
   from the contracts themselves).
3. Migrate existing files with a one-off script (keep it in `archive/migrations/`), so old records follow the
   new format.
4. Update every tool listed in the contract's `read_by` / `written_by`.
5. The validator runs on GitHub for every push and pull request; the creative lead reviews changes to
   `core/`, `contracts/` and `checks/` (`.github/CODEOWNERS`).
That is how a change in one place can update the others without breaking them: the shared part is small,
written down, versioned and checked; everything else is private to each tool.

## Harness engineering: where each job lives
| Harness job | Here |
|---|---|
| Turn the request into a contract | Each tool's SKILL/README states input, output, "done when"; data contracts in `contracts/` |
| Give the agent a map | `AGENTS.md` (short) → the tool's own folder; nothing loads the whole repo |
| Right tools in the right place | the engine scripts, the validator, the ticket board; each tool writes only what it owns |
| Externalize memory | `brain/`, `state/`, `core/decisions.md`; the chat is never the record |
| Sensors before autonomy | `checks/validate.py` (contracts, links, append-only), engine `checks.csv`, CI on every push |
| Permissions outside the model | CODEOWNERS on the foundation; the strategist approves every brief and belief change; raw data is read-only |
| Traces and recovery | git history (every change, rollback to any commit or tag), `made_with` on records, history entries |

We are at level 1–2 (project guide + tools + structured state + checks). No autonomous agents, budgets or
retry loops yet; add them only when a task earns it (e.g. a Monday run that executes unattended).

## Where sessions run
The memory is files in this repo, so any agent that can open the repo can use it: a Claude session with the
repo attached (Claude app or Claude Code) or Codex (reads `AGENTS.md`). A chat that can only *read*
project files can brainstorm but cannot save what it learns; use one that can write and commit.
If two people push at the same time, pull with rebase and push again; history files only grow, so keep both
sides' entries.
