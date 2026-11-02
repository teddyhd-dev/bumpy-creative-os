# Brainstormer changelog

Bump `version` in SKILL.md with every change. Experiment records carry `made_with: brainstorm/<version>`.

## 0.3.0 · 2026-11-02
No clashes with what exists: new codes come from `checks/new_concept.py new` and are checked against the concept
registry (letter case, one-character typos, a name already used by another code); every ad name in the brief
passes `checks/new_concept.py names` (canonical persona, registered concept name, format); a new code is added
to `core/concepts.csv` on approval. The validator runs the same checks on every experiment record.

## 0.2.0 · 2026-11-02
Starts from the ticket's full story (`prebrief`: metrics by week, funnel vs OS, current and previous #1s with
full ad names, recent refreshes and verdicts, proven concepts nearby, sibling tickets). Asks for decodes by
full ad name.

## 0.1.0 · 2026-11-02
First version, from the strategist's flow: read the ticket and the mind → close the decode gap (snapshot,
hook, why) and save it → read winners through the mind → first snippet of options by playbook move → ask
for inspiration → iterate → brief with v5 names → save the experiment, history entries, commit.
