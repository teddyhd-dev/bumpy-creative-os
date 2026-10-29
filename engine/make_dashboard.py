"""Builds the local dashboard: output/dashboard/index.html.

The page itself lives in output/dashboard/page.html (the same file that is
published to the claude.ai dashboard). This wraps it with a local data loader,
d3 and styles so it runs from your own computer:

    python3 -m http.server 8000 -d output
    open http://localhost:8000/dashboard/
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASH = os.path.join(ROOT, "output", "dashboard")

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bumpy ads command grid</title>
<link rel="stylesheet" href="dash-local.css">
<script src="vendor/d3.min.js"></script>
<script src="dash-local.js"></script>
</head>
<body>
<div class="local-bar">Local copy · data from output/data/ · rebuild with <code>bash engine/run_all.sh</code></div>
<div id="dash-root">
"""
TAIL = """
</div>
</body>
</html>
"""


def main():
    page = open(os.path.join(DASH, "page.html"), encoding="utf-8").read()
    with open(os.path.join(DASH, "index.html"), "w", encoding="utf-8") as f:
        f.write(HEAD + page + TAIL)
    print("wrote", os.path.join(DASH, "index.html"))


if __name__ == "__main__":
    main()
