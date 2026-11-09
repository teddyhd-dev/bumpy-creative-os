"""Adset, persona, country and ad level: does Singular rank things the same way Meta does?"""
import os, re, json
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H = os.path.join(ROOT, 'output', 'data', 'singular'); os.makedirs(H, exist_ok=True)
pd.set_option('display.width', 220)
OUT = {}
W = pd.read_csv(H + '/weekly_os.csv')
RATIO = {o: W[W.os == o].rev7.sum() / W[W.os == o].rev.sum() for o in ('iOS', 'Android')}
OUT['ratio_total'] = RATIO


def persona(n):
    f = [x.strip() for x in str(n).split('/')]
    if len(f) >= 12 and f[0] == 'AS':
        return f[2]
    return 'legacy'


def os_of(name):
    m = re.search(r'/\s*(iOS|Android|Web|All)\s*/', str(name))
    if m:
        return m.group(1)
    for k in ('iOS', 'Android', 'Web'):
        if k.lower() in str(name).lower():
            return k
    return 'unknown'


# ---------- weekly adset level (full Monday weeks inside Singular's CSV months: Apr–Jun, Oct) ----------
NM = pd.read_csv(H + '/name_map.csv').set_index('singular_name').meta_name.to_dict()
s = pd.read_csv(H + '/s_adc.csv', low_memory=False)
s['adset'] = s.adset.map(lambda x: NM.get(x, x))   # Singular keeps install-time (old) adset names
csv = s[~s.src.str.contains('xlsx')].copy()
d0 = pd.to_datetime(csv.start)
csv['week'] = (d0 - pd.to_timedelta(d0.dt.dayofweek, unit='D')).dt.strftime('%Y-%m-%d')
sa = csv.groupby(['week', 'adset'])[['cost', 'installs', 'rev7']].sum()
import glob
parts = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'raw', 'adset', 'adset_*.csv.gz'))):
    d = pd.read_csv(f, low_memory=False); d = d.loc[:, ~d.columns.duplicated()]; d['file'] = f; parts.append(d)
M = pd.concat(parts, ignore_index=True)
M['week'] = M['Week'].str[:10]
M = M.sort_values('file').drop_duplicates(['Ad set name', 'week'], keep='last')
M['adset'] = M['Ad set name'].str.strip()
M['rev'] = pd.to_numeric(M['In-app purchases conversion value'], errors='coerce').fillna(0)
M['cost'] = M['Amount spent (USD)']
ma = M.groupby(['week', 'adset'])[['cost', 'rev']].sum()
weeks = sorted(set(W.week))
J = ma.join(sa, lsuffix='_m', rsuffix='_s', how='left').reset_index()
J = J[J.week.isin(weeks) & J.week.isin(sa.index.get_level_values(0))]
OUT['adset_week_spend_matched'] = J.cost_s.notna().mul(J.cost_m).sum() / J.cost_m.sum()
J = J.dropna(subset=['cost_s'])
J['os'] = J.adset.map(os_of)
J = J[J.os.isin(['iOS', 'Android']) & (J.cost_m >= 300)]
J['roas_m'] = J.rev / J.cost_m
J['roas_s'] = J.rev7 / J.cost_m
tot = J.groupby(['week', 'os']).agg(cm=('cost_m', 'sum'), rm=('rev', 'sum'), rs=('rev7', 'sum'))
J = J.join(tot, on=['week', 'os'])
J['rel_m'] = J.roas_m / (J.rm / J.cm)
J['rel_s'] = J.roas_s / (J.rs / J.cm)
J['persona'] = J.adset.map(persona)
J.to_csv(H + '/adset_week.csv', index=False)
OUT['adset_weeks'] = len(J)
OUT['adset_week_spearman_roas'] = spearmanr(J.roas_m, J.roas_s)[0]
OUT['adset_week_spearman_rel'] = spearmanr(J.rel_m, J.rel_s)[0]
# within-week ranking agreement (what a ticket queue does)
rk = []
for (w, o), g in J.groupby(['week', 'os']):
    if len(g) >= 5:
        rk.append(spearmanr(g.roas_m, g.roas_s)[0])
OUT['within_week_rank_corr_median'] = float(np.median(rk))
# the bar: Meta 0.40 vs the same money on Singular (0.40 × that OS's ratio) and vs a flat 0.40 on Singular
J['green_m'] = J.roas_m >= 0.40
J['green_s_eq'] = J.roas_s >= 0.40 * J.os.map(RATIO)
J['green_s_flat'] = J.roas_s >= 0.40
OUT['bar_agree_equivalent'] = (J.green_m == J.green_s_eq).mean()
OUT['bar_agree_equivalent_spendw'] = ((J.green_m == J.green_s_eq) * J.cost_m).sum() / J.cost_m.sum()
OUT['green_share_spend_meta'] = (J.green_m * J.cost_m).sum() / J.cost_m.sum()
OUT['green_share_spend_sing_flat'] = (J.green_s_flat * J.cost_m).sum() / J.cost_m.sum()
OUT['green_share_spend_sing_eq'] = (J.green_s_eq * J.cost_m).sum() / J.cost_m.sum()
flip = J[J.green_m != J.green_s_eq]
OUT['flips'] = dict(n=len(flip), red_on_meta_green_on_sing=int((~flip.green_m).sum()), green_on_meta_red_on_sing=int(flip.green_m.sum()))

# ---------- persona: ratio Singular ÷ Meta revenue (Apr–Oct, all months, adset × country files) ----------
m = pd.read_csv(H + '/m_adc.csv', low_memory=False)
mon = ['2026-04', '2026-05', '2026-06', '2026-07', '2026-08', '2026-09']
sm = s[s.month.isin(mon)].groupby(['month', 'adset']).agg(cost_s=('cost', 'sum'), rev7=('rev7', 'sum'), inst_s=('installs', 'sum'),
                                                        s_purch=('s_purch', 'sum'), meta_purch=('meta_purch', 'sum'))
mm = m[m.month.isin(mon)].groupby(['month', 'adset']).agg(cost_m=('cost', 'sum'), rev=('rev', 'sum'), inst_m=('installs', 'sum'), purch_m=('purch', 'sum'))
P = mm.join(sm, how='inner').reset_index()
P['os'] = P.adset.map(os_of)
P['persona'] = P.adset.map(persona)
P = P[P.os.isin(['iOS', 'Android'])]
pp = P.groupby(['persona', 'os']).agg(cost=('cost_m', 'sum'), rev=('rev', 'sum'), rev7=('rev7', 'sum'))
pp = pp[pp.cost >= 40000]
pp['roas_m'] = pp.rev / pp.cost
pp['roas_s'] = pp.rev7 / pp.cost
pp['ratio'] = pp.rev7 / pp.rev
pp['ratio_vs_os'] = pp.ratio / pp.index.get_level_values(1).map(RATIO)
pp['rank_m'] = pp.groupby(level=1).roas_m.rank(ascending=False)
pp['rank_s'] = pp.groupby(level=1).roas_s.rank(ascending=False)
pp = pp.sort_values(['ratio_vs_os'])
pp.to_csv(H + '/persona.csv')
print('\n== Persona × OS, Apr–Sep (spend ≥ $40k)\n', pp.round(3).to_string())
OUT['persona_rank_corr'] = {o: spearmanr(g.roas_m, g.roas_s)[0] for o, g in pp.groupby(level=1)}

# ---------- country: Singular = user's country at install; Meta = where the ad was shown ----------
C = (m[m.month.isin(mon)].assign(os=lambda x: x.adset.map(os_of)).groupby(['country', 'os']).agg(cost_m=('cost', 'sum'), rev=('rev', 'sum'))
     .join(s[s.month.isin(mon)].assign(os=lambda x: x.adset.map(os_of)).groupby(['country', 'os']).agg(cost_s=('cost', 'sum'), rev7=('rev7', 'sum')), how='outer')).fillna(0)
C = C[C.index.get_level_values(1).isin(['iOS', 'Android'])]
C['ratio'] = C.rev7 / C.rev
C['ratio_vs_os'] = C.ratio / C.index.get_level_values(1).map(RATIO)
C['spend_ratio'] = C.cost_s / C.cost_m
top = C[C.cost_m >= 60000].sort_values('ratio_vs_os')
top.to_csv(H + '/country.csv')
print('\n== Country × OS, Apr–Sep (Meta spend ≥ $60k)\n', top.round(3).to_string())

# ---------- installs and purchases (Q3: Singular's own D7 purchase count) ----------
q3 = P[P.month.isin(['2026-07', '2026-08', '2026-09'])]
OUT['q3_purchases'] = dict(meta=q3.meta_purch.sum(), singular_d7=q3.s_purch.sum(), meta_per_singular=q3.meta_purch.sum() / q3.s_purch.sum(),
                           rev_per_purchase_meta=q3.rev.sum() / q3.purch_m.sum(), rev_per_purchase_singular=q3.rev7.sum() / q3.s_purch.sum())

# ---------- ad level: same creative, two rulers ----------
sad = pd.read_csv(H + '/s_ad.csv', low_memory=False)
sad['adset'] = sad.adset.map(lambda x: NM.get(x, x))
mad = pd.read_csv(H + '/m_ad.csv', low_memory=False)
key = lambda x: x.str.replace(r'\.(mp4|png|jpg|jpeg|mov)$', '', regex=True, flags=re.I).str.strip()
sad['k'] = key(sad.ad); mad['k'] = key(mad.ad)
A1 = sad[sad.month.isin(mon)].groupby(['month', 'adset', 'k']).agg(cost_s=('cost', 'sum'), rev7=('rev7', 'sum'))
A2 = mad[mad.month.isin(mon)].groupby(['month', 'adset', 'k']).agg(cost_m=('cost', 'sum'), rev=('rev', 'sum'))
AD = A2.join(A1, how='inner').reset_index()
OUT['ad_spend_matched'] = AD.cost_m.sum() / A2.cost_m.sum()
AD = AD[AD.cost_m >= 500]
AD['roas_m'] = AD.rev / AD.cost_m
AD['roas_s'] = AD.rev7 / AD.cost_m
OUT['ad_rows'] = len(AD)
OUT['ad_spearman_roas'] = spearmanr(AD.roas_m, AD.roas_s)[0]
best = []
for (mo, a), g in AD.groupby(['month', 'adset']):
    if len(g) >= 3 and g.cost_m.sum() >= 3000:
        best.append(g.roas_m.idxmax() == g.roas_s.idxmax())
OUT['ad_best_payer_same'] = float(np.mean(best)); OUT['ad_best_payer_groups'] = len(best)
print(json.dumps(OUT, indent=1, default=float))
