# Casting data (reference)

As received from the strategists on 3 Nov 2026 (`bumpy-casting-data.md`). A starting point for casting, not a rule:
the strategist decides (`craft/casting.md`). The RU and IN exclusions are brand rules (`core/brand.md`). Refresh this
file when new swipe, match or connection data comes in, and note the date here.

- Source 1: Attractiveness_country.txt — paid user swipe attractiveness scores (30d)
- Source 2: malefemale_top_country_Result_3.csv — mutual match volume (both swiped right)
- Source 3: male_female_proximity.csv — actual cross-border connections formed
- Rules: India (IN) excluded — board decision. Russia (RU) excluded — company policy (Bumpy is Ukrainian-based).
- RU and IN may still appear in raw data lines below for transparency; they are never recommended or cast.
- Usage: look up viewer segment → get bilateral casting recommendation

- HOW TO READ:
- attracted_to = one-sided paid swipe score (what they want)
- mutual_matches = both parties swiped right (what actually works both ways)
- proximity_connects = pairs that form real connections at highest volume
- RECOMMENDED = the bilateral sweet spot: high on at least 2 of 3 signals

---

## WHITE / WESTERN MALE (US, GB, CA, AU, DE, FR — English-speaking)

attracted_to (paid swipes, US Male): MA(1.45) KR(0.87) UA(0.86) TR(0.85) CR(0.85)
mutual_matches (US Male, excl. IN): BR(43,737) PH(37,180) CU(34,128) CO(15,334) MX(14,374)
proximity_connects (excl. IN): US↔PH(35,224) US↔BR(18,248) US↔MX(12,979)

RECOMMENDED female profiles: 🇧🇷 BR, 🇵🇭 PH, 🇨🇴 CO, 🇲🇽 MX
Reasoning: BR and PH dominate mutual matches AND proximity. One-sided attraction (KR/UA/MA)
doesn't convert to bilateral connection at the same volume. For ads: BR and PH are the
faces that both sides will recognize as desirable.

top_female_profiles:
  BR:[25033985,24719975,25124613,24454508,24509071,23449020,23359247,23400201]
  PH:[24127629,24969654,25000424,24454657,24158562]
  CO:[25026844,25032511,24527277,23696965,24592790,24148162]
  MX:[25435154,25668990,24242203]
  AR:[23540593,23351380,24279988,24561056]
  VE: no su_id data — generate full casting descriptions

---

## SOUTHEAST ASIAN FEMALE (PH, TH, ID)

### PH Female
attracted_to (paid swipes): MY(0.23) GB(0.22) US(0.21) CH(0.20) DE(0.19)
mutual_matches (excl. IN): US(37,797) TR(24,824) PH(17,855) SG(11,567) IT(8,775) KR(8,623)
proximity_connects (excl. IN): US↔PH(35,224) TR↔PH(19,103) KR↔PH(12,523)

RECOMMENDED male profiles: 🇺🇸 US, 🇹🇷 TR, 🇰🇷 KR, 🇮🇹 IT
Reasoning: US is #1 on all three signals. TR and KR confirmed bilateral.

top_male_profiles:
  US:[24063906,24225602,25499027,25148363,24147889]
  TR:[25193711,24472930,26440379]
  KR:[24437975,25239270,26114122]
  IT:[24138109,25153998,24755567]

### ID Female
attracted_to (paid swipes): DE(0.22) RU(0.22, excluded) GB(0.20) ES(0.19) FR(0.19)
mutual_matches (excl. IN): TR(37,120) US(10,539) CA(8,757) KR(6,744) AU(6,147)
proximity_connects (excl. IN): TR↔ID(23,620)

RECOMMENDED male profiles: 🇹🇷 TR, 🇺🇸 US, 🇰🇷 KR, 🇨🇦 CA
Reasoning: TR dominates mutual matches and proximity. US confirmed bilateral.

top_male_profiles:
  TR:[25193711,24472930,26440379]
  US:[24063906,24225602,25499027]
  KR:[24437975,25239270,26114122]
  CA:[25088163,25301570,25432856]

### TH Female
attracted_to (paid swipes): CH(0.20) DE(0.19) GB(0.18) FR(0.18) US(0.17)
mutual_matches: no direct TH Female data in mutual file
proximity_connects (excl. IN): TR↔TH(11,308)

RECOMMENDED male profiles: 🇺🇸 US, 🇬🇧 GB, 🇩🇪 DE, 🇰🇷 KR
Reasoning: Western males dominate paid attractiveness. KR added from regional pattern.

top_male_profiles:
  US:[24063906,24225602,25499027]
  GB:[24969516,25681529,25653762]
  DE:[25155938,25547289,24499838]
  KR:[24437975,25239270,26114122]

---

## LATAM FEMALE (BR, CO, MX, CU, VE, CL, AR, PE)

attracted_to (paid swipes, BR Female): KR(0.12) US(0.11) GB(0.10) DE(0.10)
mutual_matches (LATAM Female, excl. IN): US(92,496) MX(78,302) BR(58,315) TR(43,073) CL(32,496) ES(31,639)
proximity_connects (excl. IN): TR↔BR(19,713) CL↔BR(13,557) PT↔BR(13,778)

RECOMMENDED male profiles: 🇺🇸 US, 🇪🇸 ES, 🇹🇷 TR, 🇰🇷 KR
Reasoning: US is #1 bilateral. ES/TR confirmed mutual. KR confirmed by paid attractiveness.
Exclude IN (board rule) and same-country matches for international appeal.

top_male_profiles:
  US:[24063906,24225602,25499027]
  ES:[24859435,24731829,25553444]
  TR:[25193711,24472930,26440379]
  KR:[24437975,25239270,26114122]

---

## WESTERN FEMALE (US, GB, CA, AU)

attracted_to (paid swipes, US Female): KR(0.18) UA(0.11) RU(0.11, excluded) MA(0.10) HK(0.10)
mutual_matches: no direct US Female data in mutual file
proximity_connects: US↔PH(35k) US↔BR(18k) — these are male-led

RECOMMENDED male profiles: 🇰🇷 KR, 🇺🇦 UA, 🇺🇸 US, 🇮🇹 IT
Reasoning: Paid attractiveness is the primary signal here (mutual file has no US Female row).
KR is #1 by clear margin, UA #2. RU scores the same as UA but is excluded (company policy),
so US takes that slot. IT added — high in mutual patterns for other Western female segments.

top_male_profiles:
  KR:[24437975,25239270,26114122]
  UA:[25461999,25039610,25393679]
  US:[24063906,24225602,25499027]
  IT:[24138109,25153998,24755567]

---

## AFRICAN FEMALE (NG, KE, GH, ZA)

attracted_to (paid swipes, NG Female): CA(0.93) GB(0.81) US(0.80) AU(0.77) DE(0.55)
mutual_matches (NG Female, excl. IN): TR(21,601) GB(13,685) US(13,006) BR(9,655) CA(8,867)

RECOMMENDED male profiles: 🇬🇧 GB, 🇺🇸 US, 🇹🇷 TR, 🇨🇦 CA
Reasoning: GB/US confirmed on both signals. TR strong bilateral.

top_male_profiles:
  GB:[24969516,25681529,25653762]
  US:[24063906,24225602,25499027]
  TR:[25193711,24472930,26440379]
  CA:[25088163,25301570,25432856]

---

## US MALE — WHERE HE SUCCEEDS (for copy, not casting)

Top 5 countries for US male (team ranking, Sep 2026): 🇵🇭 PH, 🇧🇷 BR, 🇮🇩 ID, 🇨🇺 CU, 🇨🇴 CO
Match rate claim in use: US males ~20% match rate on Bumpy vs ~5% on local apps.
Check how Bumpy's 20% is calculated (matches ÷ likes sent?) before using it in public ads.

---

## KEY BILATERAL PAIRS — USE THESE FOR PAYOFF SCENES (airport/eating/car/proposal)

These are the most data-proven cross-cultural couples for Bumpy ads:

| Male | Female | Evidence strength |
|---|---|---|
| 🇺🇸 White American | 🇧🇷 Brazilian | ★★★ — #1 mutual match US Male, high proximity |
| 🇺🇸 White American | 🇵🇭 Filipina | ★★★ — #2 mutual match US Male, #1 proximity pair |
| 🇬🇧 British | 🇳🇬 Nigerian | ★★★ — #1 proximity GB↔NG, strong mutual |
| 🇹🇷 Turkish | 🇮🇩 Indonesian | ★★★ — #1 bilateral TR↔ID across all signals |
| 🇰🇷 Korean | 🇧🇷 Brazilian | ★★ — KR Male #1 mutual match is BR |
| 🇰🇷 Korean | 🇵🇭 Filipina | ★★ — strong bilateral, high proximity |

---

## EXCLUDED COUNTRIES

IN (India) — excluded from all casting per board decision
RU (Russia) — excluded from all casting, faces and locations (Bumpy is Ukrainian-founded). "Slavic" casting = UA and similar, never RU.
