# Ticket board

The live board: https://claude.ai/artifact/MFtoxXwScrbATaY5jNhv2U (page source: `board.html`; user guide: `GUIDE.md`).

- **Reads:** the board's own database, filled every Monday from `output/board/*.json` (see AGENTS.md, weekly
  routine). Each ticket carries its mind and, when a brief covers it, the experiment id from `brain/experiments/`.
- **Writes:** nothing into the repo. People can open manual tickets on the page.
- **Links to the other tools:** "Copy for the brainstormer" on each ticket gives the line to start a brainstorm;
  the brief status comes from the experiment records.
