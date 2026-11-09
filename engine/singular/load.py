"""Load the Singular exports (Mar–Oct 2026) and the Meta exports into tidy tables.

Outputs (in this folder):
  s_adc.csv  Singular, adset × country × period   (period = the export's own row dates)
  s_ad.csv   Singular, ad × adset × period
  m_adc.csv  Meta (our stack), adset × country × period
  m_ad.csv   Meta, ad × adset × period
"""
import glob, os, re, sys
import pandas as pd, numpy as np, openpyxl, pycountry

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, 'data', 'raw', 'singular') + '/'
R = os.path.join(ROOT, 'data', 'raw') + '/'
OUT = os.path.join(ROOT, 'output', 'data', 'singular'); os.makedirs(OUT, exist_ok=True)

ISO3 = {c.alpha_3: c.alpha_2 for c in pycountry.countries}
ISO3.update({'XKX': 'XK', 'XKS': 'XK'})


def iso2(x):
    x = str(x).strip()
    if len(x) == 3 and x.upper() in ISO3:
        return ISO3[x.upper()]
    return x if len(x) == 2 else 'unknown'


def os_of(name):
    m = re.search(r'/\s*(iOS|Android|Web|All)\s*/', str(name))
    if m:
        return m.group(1)
    for k in ('iOS', 'Android', 'Web'):
        if k.lower() in str(name).lower():
            return k
    return 'unknown'


def num(s):
    return pd.to_numeric(s, errors='coerce').fillna(0)


# ---------- Singular CSVs (Mar, Apr, May, Jun, Oct) ----------
def s_csv(files, level):
    out = []
    for f in files:
        d = pd.read_csv(A + f + ('.gz' if not os.path.exists(A + f) else ''))
        r = pd.DataFrame({
            'start': d['Start date'], 'end': d['End date'],
            'adset': d['Sub Campaign Name'].astype(str).str.strip(),
            'impr': num(d.Impressions), 'clicks': num(d.Clicks), 'installs': num(d.Installs),
            'cost': num(d.Cost), 'purch': num(d.Purchase), 'rev7': num(d['Revenue 7d']),
        })
        if level == 'adc':
            r['country'] = d['Country'].map(iso2)
        else:
            r['ad'] = d['Creative Name'].astype(str).str.strip()
        r['src'] = f
        out.append(r)
    return pd.concat(out, ignore_index=True)


ADC_CSV = sorted(os.path.basename(p)[:-3] if p.endswith('.gz') else os.path.basename(p) for p in set(glob.glob(A + 'singular_adset_country_*.csv*')))
ADC_CSV = sorted(set(ADC_CSV))
AD_CSV = sorted(set(os.path.basename(p)[:-3] if p.endswith('.gz') else os.path.basename(p) for p in glob.glob(A + 'singular_ad_2*.csv*')))


# ---------- Singular Q3 workbooks (Jul–Sep) ----------
def s_xlsx(f, level):
    wb = openpyxl.load_workbook(A + f, read_only=True)
    out = []
    for sh in ('Jul', 'Aug', 'Sep'):
        rows = wb[sh].iter_rows(values_only=True)
        hdr = list(next(rows))
        d = pd.DataFrame([r for r in rows if r and r[0] is not None], columns=hdr)
        wk = d['Week'].astype(str).str.split(' - ')
        r = pd.DataFrame({
            'start': wk.str[0], 'end': wk.str[1],
            'adset': d['Ad set name'].astype(str).str.strip(),
            'impr': num(d['Impressions']), 'clicks': num(d['Clicks (all)']), 'installs': num(d['App installs']),
            'cost': num(d['Amount spent (USD)']), 'purch': num(d['Purchases']),
            'rev7': num(d['In-app purchases conversion value']),
            'meta_purch': num(d['Meta purchases (Meta-reported)']),
        })
        if level == 'adc':
            r['country'] = d['Country'].map(iso2)
            r['adset_id'] = d['Ad set ID'].astype(str)
        else:
            r['ad'] = d['Ad name'].astype(str).str.strip()
            r['adset_id'] = d['Ad set ID'].astype(str)
        r['src'] = f + ':' + sh
        out.append(r)
    return pd.concat(out, ignore_index=True)


# ---------- Meta exports (our stack) ----------
def m_files(kind):
    fs = sorted(glob.glob(R + f'{kind}/{kind}_*.csv.gz'))
    out = []
    for f in fs:
        d = pd.read_csv(f)
        d['_file'] = os.path.basename(f)
        out.append(d)
    d = pd.concat(out, ignore_index=True)
    # newest file wins for the same row period
    d['_s'] = d['Reporting starts'].astype(str)
    d['_e'] = d['Reporting ends'].astype(str)
    return d


def m_tidy(d, level):
    name = d['Ad set name'].iloc[:, 0] if isinstance(d['Ad set name'], pd.DataFrame) else d['Ad set name']
    r = pd.DataFrame({
        'start': d['_s'], 'end': d['_e'], 'adset': name.astype(str).str.strip(),
        'impr': num(d['Impressions']), 'clicks': num(d.get('Link clicks', 0)), 'installs': num(d['App installs']),
        'cost': num(d['Amount spent (USD)']), 'purch': num(d['Purchases']),
        'rev': num(d['In-app purchases conversion value']), 'file': d['_file'],
    })
    if level == 'adc':
        r['country'] = d['Country'].astype(str).replace({'nan': 'unknown'})
    else:
        r['ad'] = d['Ad name'].astype(str).str.strip()
    return r


def dedupe_newest(r, keys):
    """One file per month: the file whose range covers the whole month (newest if several); rows inside that month."""
    keep = []
    r['month'] = r.start.str[:7]
    for m, g in r.groupby('month'):
        fr = g.file.str.extract(r'_(\d{4}-\d{2}-\d{2})_(\d{4}-\d{2}-\d{2})')
        full = g[(fr[0] <= m + '-01') & (fr[1] >= (pd.Period(m).end_time.strftime('%Y-%m-%d')))]
        if len(full):
            f = full.file.max()
            g = g[(g.file == f) & (g.end <= pd.Period(m).end_time.strftime('%Y-%m-%d'))]
        keep.append(g)
    return pd.concat(keep, ignore_index=True)


if __name__ == '__main__':
    s_adc = pd.concat([s_csv(ADC_CSV, 'adc'), *[s_xlsx(os.path.basename(p), 'adc') for p in sorted(glob.glob(A + 'singular_adset_country_*.xlsx'))]],
                      ignore_index=True)
    s_ad = pd.concat([s_csv(AD_CSV, 'ad'), *[s_xlsx(os.path.basename(p), 'ad') for p in sorted(glob.glob(A + 'singular_ad_2*.xlsx'))]],
                     ignore_index=True)
    for t in (s_adc, s_ad):
        t['os'] = t.adset.map(os_of)
        t['month'] = t.start.str[:7]
        q3 = t.src.str.contains('xlsx')
        # The CSV exports' "Purchase" is the Meta-mirrored count (ties to Meta within 0.3%); the Q3 workbooks'
        # "Purchases" is Singular's own D7 cohort count, with Meta's count in its own column.
        t['s_purch'] = np.where(q3, t.purch, np.nan)
        t['meta_purch'] = np.where(q3, t.meta_purch, t.purch)
    m_adc = dedupe_newest(m_tidy(m_files('country'), 'adc'), None)
    m_ad = dedupe_newest(m_tidy(m_files('ad'), 'ad'), None)
    for t in (m_adc, m_ad):
        t['os'] = t.adset.map(os_of)
        t['month'] = t.start.str[:7]
    s_adc.to_csv(OUT + '/s_adc.csv', index=False)
    s_ad.to_csv(OUT + '/s_ad.csv', index=False)
    m_adc.to_csv(OUT + '/m_adc.csv', index=False)
    m_ad.to_csv(OUT + '/m_ad.csv', index=False)
    agg = dict(cost=('cost', 'sum'), installs=('installs', 'sum'), purch=('purch', 'sum'))
    S = s_adc.groupby('month').agg(**agg, rev7=('rev7', 'sum'), meta_purch_x=('meta_purch', 'sum'))
    M = m_adc.groupby('month').agg(**agg, rev=('rev', 'sum'))
    print(S.join(M, lsuffix='_s', rsuffix='_m').round(0).to_string())
