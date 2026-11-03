"""Shared settings: measurement eras and the ROAS bar (spec §3.4 and §15).

Meta's purchase and install numbers have been fed by Singular (our MMP) since
late February 2026. Singular credits Meta with about 0.7× the purchase value
Meta's own attribution did, for the same App Store money. So Meta ROAS before
and after the switch are two different rulers:

  * never compare absolute Meta ROAS, purchases, installs, IPM or C>I across the switch;
  * judge every week against the bar of its own ruler;
  * relative numbers (adset vs its OS account in the same week) are comparable across eras.

Changing a date or a bar is a decision for the creative lead: record it in
data/log/decisions.md and the spec changelog.
"""
from __future__ import annotations

# First week (Monday) each OS was measured through Singular.
# Found in the data (purchases per million impressions and click→install stepped down);
# confirm against the Singular / Meta Events Manager change log (spec §19).
SWITCH = {"iOS": "2026-02-23", "Android": "2026-03-09"}

# TikTok's campaigns were rebuilt for MMP attribution ("| Migration" and v8 ad groups) in the
# week of 2 Feb 2026; TikTok Android purchases went unreported for about 4 weeks after it (9 Feb – 8 Mar).
TIKTOK_MMP_START = "2026-02-02"

PRE_END = "2026-02-16"          # last week both OS were on Meta's own attribution
SINGULAR_START = "2026-03-16"   # first week both OS were settled on Singular
ERA_LABEL = {"pre": "Meta's own attribution", "transition": "Switching", "singular": "Singular (MMP)"}

# (green from, amber from) on each ruler. Below green = refresh warning; below amber = critical; below deep = deep red.
# Singular bar set by the creative lead on 27 Oct 2026: 0.40 and up is acceptable, under 0.40 needs a refresh.
# Critical and deep red keep the old proportions (0.8× and 0.7× of green). In pre-switch units 0.40 ≈ 0.57.
BARS = {"meta": {"green": 0.50, "amber": 0.40, "deep": 0.35},
        "singular": {"green": 0.40, "amber": 0.32, "deep": 0.28}}
BAR_STATUS = "Singular bar set 27 Oct 2026 by the creative lead: acceptable from 0.40, refresh warning under 0.40; critical under 0.32 (same proportions as the old bar)"


# ---- At-bats and tickets (spec §6 and §20). Proposed 27 Oct 2026, waiting for the creative lead. ----
# At-bat = new concepts entering an adset in the same week, once the adset is 3+ weeks old.
ATBAT = {
    "adset_min": 1000,      # adset spend that week ($) for the at-bat to count
    "concept_min": 20,      # concept spend in its first adset week ($)
    "adset_age": 3,         # weeks since the adset's first spend (launch weeks are not refreshes)
    "w1_hit_share": 0.20,   # week-1 share of adset spend for a provisional hit (79% become #1)
    "final_week": 4,        # final verdict: became the adset's #1 within 4 weeks
    "late_week": 12,        # #1 in weeks 5–12 = late hit (a third of refresh winners start under 5%)
}
# Ticket priority = weight × last week's spend. Review tickets (3 strikes in a row) are pinned on top.
TICKET_WEIGHTS = {
    "min_spend": 300,           # live adsets below this weekly spend get no ticket
    "review_strikes": 3,
    "review": 1.0,
    "critical": 1.0,            # under the critical bar, above the alert floor
    "amber_falling": 0.8,
    "leading_signal": 0.6,      # green, but IPM or hook rate down 20%+
    "due_reign": 2,             # #1 concept in week 2+ of its reign: a refresh takes ~1 week to make and ~1 week to read,
                                # and reigns last a median 3 weeks (spec §6.7: due at lifespan − 1)
    "due": 0.5,
    "due_falling_bonus": 0.1,   # ... and ROAS lower than the week before
    "amber": 0.4,
    "critical_small": 0.3,      # critical but below the alert floor
    "in_test_factor": 0.5,      # a challenger already entered in the last 2 weeks
    "low_ceiling_factor": 0.5,  # 🧱: creative may not be the fix
    "refresh_worse": 1.0,       # last refresh reached the top 3 and the adset's ROAS fell: fix first (2 Nov)
    "refresh_again": 0.7,       # last refresh almost / flat: swing again (2 Nov)
}
# Refresh read (spec §6.2b, creative lead 2 Nov 2026): did the new creative reach the top N spenders,
# was it inside the ads making 80% of the adset's spend (else Almost), then did the adset's ROAS move by more
# than `flat`?
READ = {"top_n": 3, "flat": 0.02, "affect": 0.80}   # affect: inside the ads making 80% of spend (3 Nov)


def ruler(week: str, os: str | None = None) -> str:
    """'meta' or 'singular': which ruler measured this week for this OS."""
    start = SWITCH.get(os, SWITCH["iOS"])  # mixed / unknown OS: switches with iOS (the bigger half)
    return "singular" if str(week) >= start else "meta"


def bar(week: str, os: str | None = None) -> dict:
    return BARS[ruler(week, os)]


def era(week: str) -> str:
    w = str(week)
    if w <= PRE_END:
        return "pre"
    if w < SINGULAR_START:
        return "transition"
    return "singular"
