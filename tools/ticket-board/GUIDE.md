# Ticket board: how to use it

Link: https://claude.ai/artifact/MFtoxXwScrbATaY5jNhv2U (the same guide is in the board's Guide tab).

**Since 2 Nov 2026 the board is the ticket system only.** Briefs are written in a brainstorm session
(tools/brainstormer) and pasted into Notion; the weekly report is a PDF (tools/report); persona knowledge,
signals and the experiment log live in the repo's `brain/`. Statuses move by themselves: No brief yet →
Briefed (an experiment record covers the ticket) → Live (its ads are in the export) → Week-1 read → final.
On each ticket, **Copy for the brainstormer** gives the line that starts a brainstorm.

The sections below describe the full board as it was on 27 Oct (kept for reference; the Board, Report,
Signals, Personas and Log tabs are now hidden).

## How it all fits together
- **Monday:** the exports (Meta adset × country, ad level, App Store and Play by country, TikTok) go into the engine. Claude runs it and applies the spec's rules.
- **Account dashboard (why):** money vs store, markets, channels, measurement eras and creative patterns. For the creative lead and management to set the bar, budgets and tests. Linked from the board header.
- **Creative Board (do and remember):** tickets, briefs, production, results, retros, scorecards, persona files, signals and the permanent log. Where the team works every day.
- **Report tab (tell):** the Tuesday deck, generated every Monday from the engine and the board, edited and presented from here. Every past week stays in the week picker.
- **The spec (rules):** what every word and threshold means, and every decision. In the Claude project.
- **The loop:** briefs make the ad names → the ads run → next Monday's exports carry those names → the engine reads each adset's result → it lands on the brief, the persona file, the scorecards and the next report.

## What the board is
Every Monday Claude reads the Meta, TikTok and store exports and opens a **ticket** for every adset that needs new creative, ranked by how badly it needs it × how much it spends. The team turns tickets into **briefs**, briefs into ads, and ads into results. One brief can cover several tickets. Everything done here feeds the Tuesday report and the scorecards.

NEED REFRESH → BRIEF CREATED → IN PRODUCTION → READY TO UPLOAD → TESTING → RESULT READY → RETIRED
(strategist creates the brief · designer starts production and hands off · media buyer marks it live · Claude reads the result from Monday's export · strategist and designer hold the retro, which retires it)

## Decaying, Due and 3 strikes
- **Decaying:** the adset is hurting now. ROAS under 0.40, or falling week on week, or its hook rate dropped 20%+. Needs new creative this week. Under 0.32 it's critical and ranks first.
- **Due:** the adset is fine today, but its #1 creative has led for 2+ weeks. Winners usually fade from week 3 and a refresh takes about 2 weeks (one to make, one to read), so the successor starts now. A Due adset can ride the same brief as a Decaying sibling at no extra production.
- **3 strikes:** three refreshes in a row didn't produce a new #1 while the adset was under the bar. Don't send a fourth blindly: check whether it's the concepts, the execution, the audience or the setup. A challenger that can't beat a healthy #1 is a foul, not a strike.

## The refresh read (how each refresh did, from 2 Nov 2026)
First question: did the new creative reach the adset's **top 3 spenders**, with a real share (the ads ranked above it take under 80% of spend)? Then: did the adset's ROAS move?
- **Worked:** top 3 with a real share, ROAS up and 0.40+. Resets the strikes.
- **Almost:** top 3 but ROAS still under 0.40, or top 3 with too small a share to have moved the adset (e.g. #3 at 2%). No strike; the ticket stays open to swing again.
- **Flat:** top 3, ROAS didn't move. No strike; swing again.
- **Worse:** top 3 and ROAS fell. A strike in any context, and the ticket jumps to the top: fix first.
- **Miss:** not in the top 3. Under 0.40 it's a strike while the adset is in a turnaround; at 0.40+ old creatives are carrying it, so leave it (no Due ticket).
On the board the last read shows as a coloured pill next to the strikes (hover for what it means), and each H/S/F letter shows its read on hover. Creator content is judged with the same read.

## Rules of thumb
- 0.40+ is acceptable, under 0.40 needs a refresh, under 0.32 is critical.
- A concept that takes 20%+ of its adset's spend in week 1 becomes #1 about 8 times in 10. Final call at week 4.
- Keep quiet ads on: a third of winners start under 5% of spend.
- 3+ variants per adset: about 47% vs 27% with 1–2. Re-cuts, new text and V2 re-orders count; a version that opens on a different scene is a new concept code.
- Spread wide, judge per adset: concepts land in a median 3 adsets; each keeps about a 20% chance; a concept in 5+ adsets wins somewhere 71% of the time. Languages often disagree; iOS and Android usually agree.
- About 8 adset refreshes land a week. Grouping tickets into one brief is how we cover more.

## Strategist
1. **Pick the work:** Queue → By persona. Start with groups holding Decaying or 3-strike tickets. Tick the adsets one concept can serve (other languages, both OS) → Brief the selected. Group what truly shares an insight.
2. **Write the brief:** pick the move (new concept, proven concept from nearby, new form of a past winner), the hypothesis (or Draft with Claude, then edit), 3+ variants, the designer.
3. **Create it:** the board makes the v5 ad names, Drive folder and file names.
4. **Retro at RESULT READY** with the designer: answered or not, flags, one line of learning. Say where it worked and where it didn't.

Your card: briefs, how many are grounded in a signal or proven concept, hits on the adsets you briefed, how often the hypothesis got a clear answer.

## Designer
1. Board → your briefs under BRIEF CREATED → Start production. One brief may cover many adsets: your card counts the files and adsets it covers.
2. Use the generated file names exactly: that's how the board finds your ads in Meta's export.
3. Milk every generation: 3+ variants per adset, in its language.
4. Hand off in 30 seconds: Drive link, videos and images, task counts if you can.
5. Retro with the strategist when results land.

What moves the needle: 20%+ of the adset's spend in week 1, strong hook and hold vs the other variants of the same concept, realistic visuals (nothing too AI), on-brief. Your card: output, days brief → handoff, results vs team baseline, retro flags. Nobody is ranked on fewer than 10 results.

## UA team and management
- **Report tab** on Tuesday: account in one line, 01 Team output, 02 New personas, 03 Persona expansion, 04 Refresh and iteration, 05 TikTok, 06 This week and decisions. Press **Present** for one section per screen (arrow keys, Esc). Every insight and action item is a draft: press Edit to rewrite it before the meeting; your edits are kept when Monday's run refreshes the numbers. Pick any past week from the menu.
- **People:** each card shows what the person is on, anything waiting past its usual time (brief 3 days, production 7, upload 3) and their score. Full tables underneath.
- Header: open tickets, no brief yet, in flight, fading with no brief, refreshes a week, the ROAS bar.
- Queue top 10: where money is at risk (how bad × how much it spends). The dashed line shows what fits this week.

## Personas and Log
- **Personas** is the living persona file: live state, open tickets, what wins (last 26 weeks), the Notion card, retro learnings and signals. Updated every Monday and with every retro.
- **Log** keeps everything permanently: briefs and experiments (board + Notion history), every refresh since December with its verdict, and week by week (plus a copy of each week's queue from 27 Oct).
- The weekly update only adds to history; it replaces this week's queue and numbers, never briefs, retros or signals.
- **Strikes on tickets:** dots show turnaround strikes (0–3); letters show the last five refreshes: H hit, S strike, F foul (hover a letter for its refresh read); the pill after them is the latest read. "Fading N wks" = under the bar N weeks with no new concept since.

## Signals
Paste a link and, optionally, one line on how we could use it. Tag one or more personas. Claude adds views, likes, shares and comments on the weekly run where the site shows them (run length for ad-library links), so the bank can be sorted. Tagged signals show up in that persona's tickets and in Claude's brief drafts.
