"""Singular keeps the adset names from install time (old names before the v8 rename); Meta exports show today's
names. Match them by spend: Singular's cost is Meta's spend, so an adset's weekly spend is the same in both."""
import glob, os, re
import pandas as pd, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
H = os.path.join(ROOT, 'output', 'data', 'singular'); os.makedirs(H, exist_ok=True)
s = pd.read_csv(H + '/s_adc.csv', low_memory=False)
csv = s[~s.src.str.contains('xlsx')].copy()
d0 = pd.to_datetime(csv.start)
csv['week'] = (d0 - pd.to_timedelta(d0.dt.dayofweek, unit='D')).dt.strftime('%Y-%m-%d')
SW = csv.groupby(['adset', 'week']).cost.sum().unstack(fill_value=0)
parts = []
for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'raw', 'adset', 'adset_*.csv.gz'))):
    d = pd.read_csv(f, low_memory=False); d = d.loc[:, ~d.columns.duplicated()]; d['file'] = f; parts.append(d)
M = pd.concat(parts, ignore_index=True)
M['week'] = M['Week'].str[:10]
M = M.sort_values('file').drop_duplicates(['Ad set name', 'week'], keep='last')
MW = M.groupby(['Ad set name', 'week'])['Amount spent (USD)'].sum().unstack(fill_value=0)
weeks = [w for w in SW.columns if w in MW.columns and '2026-03-02' <= w <= '2026-06-22']
SWv, MWv = SW[weeks], MW[weeks]
SWv = SWv[SWv.sum(axis=1) > 0]; MWv = MWv[MWv.sum(axis=1) > 0]
mp, amb = {}, []
for n, v in SWv.iterrows():
    if n in MWv.index or n in MW.index:          # same name in both: it is the same adset
        mp[n] = n; continue
    on = v.values > 0
    exact = (np.abs(MWv.values[:, on] - v.values[on]) < 2).sum(axis=1)
    cover = (MWv.values[:, on] >= v.values[on] - 2).all(axis=1)
    need = min(2, on.sum())
    n_on = int(on.sum())
    big = (v.values[on] >= 200).sum()
    need = max(2, int(np.ceil(0.5 * n_on))) if n_on >= 2 else 1
    ok = cover & (exact >= need) & (big >= 1)
    hit = np.where(ok & (exact == exact[ok].max()))[0] if ok.any() else []
    GEN = {'ad', 'set', 'purchase', 'android', 'ios', 'install', 'eng', 'meta'}
    tok = lambda x: {t for t in re.findall(r'[a-z]{4,}', x.lower())} - GEN
    if len(hit) == 1 and not str(MWv.index[hit[0]]).startswith('AS /') and not (tok(n) & tok(MWv.index[hit[0]])):
        hit = []                                   # legacy → legacy with nothing in common: not trusted
    if len(hit) == 1:
        mp[n] = MWv.index[hit[0]]
    elif len(hit) > 1:
        amb.append(n)
tot = SWv.sum(axis=1)
matched = tot[tot.index.isin(mp)].sum() / tot.sum()
pd.Series(mp, name='meta_name').rename_axis('singular_name').to_csv(H + '/name_map.csv')
renamed = {k: v for k, v in mp.items() if k != v}
print(f'{len(mp)} names matched ({len(renamed)} renamed), {len(amb)} ambiguous, {len(SWv) - len(mp) - len(amb)} unmatched; '
      f'spend matched {matched:.1%}')
print(tot[~tot.index.isin(mp)].sort_values(ascending=False).head(8).round())
