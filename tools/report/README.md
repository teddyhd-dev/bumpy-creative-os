# Weekly report (PDF)

**Status: style captured, generator not built yet** (next session for this tool).

- Data: `reports/<week>/report.json`, written every Monday by `engine/report.py` (copied by `engine/brain_sync.py`).
- Style: `STYLE.md` (from the team's Canva deck).
- Output: `reports/<week>/Bumpy-Creative-Report-Week<NN>.pdf`.
- Reads: `brain/experiments/` (results, lessons), `brain/minds/*/history.md` (the week's new #1s and verdicts),
  `brain/creatives/img/` (thumbnails). Writes only into `reports/<week>/`.
