"""Singular (D7 cohort, the MMP's own attribution) vs Meta (what Meta credits itself, our stack) from April 2026."""
import glob, gzip, io, os, re, json
import numpy as np, pandas as pd, openpyxl
from scipy.stats import spearmanr, pearsonr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H = os.path.join(ROOT, 'output', 'data', 'singular'); os.makedirs(H, exist_ok=True)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, 'data', 'raw', 'singular') + '/'
R = os.path.join(ROOT, 'data', 'raw') + '/'
OUT = {}
pd.set_option('display.width', 200)


def os_of(name):
    m = re.search(r'/\s*(iOS|Android|Web|All)\s*/', str(name))
    if m:
        return m.group(1)
    for k in ('iOS', 'Android', 'Web'):
        if k.lower() in str(name).lower():
            return k
    return 'unknown'


def monday(d):
    d = pd.to_datetime(d)
    return (d - pd.to_timedelta(d.dt.dayofweek, unit='D')).dt.strftime('%Y-%m-%d')


# ---------------- weekly, account × OS ----------------
# Meta: adset weekly exports, newest file wins per adset-week
fs = sorted(glob.glob(R + 'adset/adset_*.csv.gz'))
parts = []
for f in fs:
    d = pd.read_csv(f, low_memory=False)
    d = d.loc[:, ~d.columns.duplicated()]
    d['file'] = f
    parts.append(d)
M = pd.concat(parts, ignore_index=True)
M['week'] = M['Week'].str[:10]
M = M.sort_values('file').drop_duplicates(['Ad set name', 'week'], keep='last')
M['os'] = M['Ad set name'].map(os_of)
M['rev'] = pd.to_numeric(M['In-app purchases conversion value'], errors='coerce').fillna(0)
M['cost'] = M['Amount spent (USD)']
M['installs'] = pd.to_numeric(M['App installs'], errors='coerce').fillna(0)
M['purch'] = pd.to_numeric(M['Purchases'], errors='coerce').fillna(0)
mw = M.groupby(['week', 'os'])[['cost', 'installs', 'purch', 'rev']].sum()

# Singular: CSV pieces (Mar–Jun, Oct) + Q3 daily by OS (Purchase Bug Check, section C)
s_adc = pd.read_csv(H + '/s_adc.csv', low_memory=False)
csv = s_adc[~s_adc.src.str.contains('xlsx')].copy()
csv['week'] = monday(csv.start)
csv['days'] = (pd.to_datetime(csv.end) - pd.to_datetime(csv.start)).dt.days + 1
cov = csv.drop_duplicates(['start', 'end']).groupby('week').days.sum()
sw1 = csv.groupby(['week', 'os'])[['cost', 'installs', 'rev7', 'meta_purch']].sum()
wb = openpyxl.load_workbook(sorted(glob.glob(A + 'singular_adset_country_*.xlsx'))[0], read_only=True)
rows = list(wb['Purchase Bug Check'].iter_rows(values_only=True))
i = next(k for k, r in enumerate(rows) if r and r[0] == 'Date')
daily = pd.DataFrame([r[:7] for r in rows[i + 1:] if r and r[0] is not None and r[1] in ('iOS', 'Android')],
                     columns=['date', 'os', 'cost', 'installs', 'meta_purch', 's_purch', 'rev7'])
daily['date'] = pd.to_datetime(daily.date)
daily['week'] = monday(daily.date)
cov_d = daily.drop_duplicates('date').groupby('week').date.count()
sw2 = daily.groupby(['week', 'os'])[['cost', 'installs', 'rev7', 'meta_purch', 's_purch']].sum()
cov_all = cov.add(cov_d, fill_value=0)
sw = sw1.add(sw2, fill_value=0)
full_weeks = cov_all[cov_all >= 7].index
sw = sw[sw.index.get_level_values(0).isin(full_weeks)]
daily.to_csv(H + '/s_daily_q3.csv', index=False)

# App Store proceeds, weekly
parts = []
for f in sorted(glob.glob(R + 'apple/apple_proceeds_*.csv*')):
    txt = (gzip.open(f, 'rt') if f.endswith('.gz') else open(f)).read().splitlines()
    k = next(j for j, l in enumerate(txt) if l.startswith('Date,'))
    d = pd.read_csv(io.StringIO('\n'.join(txt[k:])))
    d['Date'] = pd.to_datetime(d.Date, format='%m/%d/%y')
    parts.append(d.set_index('Date'))
AP = pd.concat(parts)
AP = AP[~AP.index.duplicated(keep='last')].sort_index()
store = AP.sum(axis=1)
store_w = store.groupby(store.index - pd.to_timedelta(store.index.dayofweek, unit='D')).agg(['sum', 'count'])
store_w = store_w[store_w['count'] == 7]['sum']
store_w.index = store_w.index.strftime('%Y-%m-%d')

W = sw.join(mw, lsuffix='_s', rsuffix='_m', how='inner').reset_index()
W = W[(W.week >= '2026-03-30') & W.os.isin(['iOS', 'Android'])]
W['roas_s'] = W.rev7 / W.cost_m
W['roas_m'] = W.rev / W.cost_m
W['rev_ratio'] = W.rev7 / W.rev
W['inst_ratio'] = W.installs_s / W.installs_m
W['spend_tie'] = W.cost_s / W.cost_m
W['store'] = W.week.map(store_w)
W.to_csv(H + '/weekly_os.csv', index=False)
print('\n== Weekly by OS (full Monday weeks from 30 Mar)')
print(W[['week', 'os', 'cost_m', 'spend_tie', 'inst_ratio', 'roas_m', 'roas_s', 'rev_ratio', 'store']].round(3).to_string())

for o in ('iOS', 'Android'):
    g = W[W.os == o]
    OUT[f'ratio_{o}'] = dict(median=g.rev_ratio.median(), lo=g.rev_ratio.quantile(.1), hi=g.rev_ratio.quantile(.9),
                             cv=g.rev_ratio.std() / g.rev_ratio.mean(), weeks=len(g),
                             inst_ratio=g.installs_s.sum() / g.installs_m.sum(),
                             roas_m=g.rev.sum() / g.cost_m.sum(), roas_s=g.rev7.sum() / g.cost_m.sum())
    if o == 'iOS':
        gg = g.dropna(subset=['store']).sort_values('week')
        for col in ('rev', 'rev7'):
            x = gg[col].values; y = gg.store.values
            OUT[f'store_level_corr_{col}'] = pearsonr(x, y)[0]
            OUT[f'store_change_corr_{col}'] = pearsonr(np.diff(np.log(x)), np.diff(np.log(y)))[0]
            OUT[f'store_per_{col}'] = (y / x).mean()
        OUT['store_weeks'] = len(gg)
print(json.dumps(OUT, indent=1, default=float))
