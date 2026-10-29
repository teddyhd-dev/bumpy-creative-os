import glob, os, re, sys
import pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from files import RAW, raw_files, supersede
def load_ads():
    fr=[]
    for p in raw_files('ad', 'ad'):
        f=pd.read_csv(p,encoding='utf-8-sig',dtype={'Ad ID':str,'Ad set ID':str}); f['_file']=os.path.basename(p); fr.append(f)
    d=pd.concat(fr,ignore_index=True)
    d=d.rename(columns={'Ad name':'ad_name','Ad set name':'adset_name','Amount spent (USD)':'spend','Purchase ROAS (return on ad spend)':'roas_meta',
      'In-app purchases conversion value':'value_inapp','Website purchases conversion value':'value_web','App installs':'installs','Link clicks':'clicks',
      'Purchases':'purchases','Impressions':'impressions','Frequency':'frequency','Hook Rate':'hook_rate','Video average play time':'avg_play',
      'Ad set budget':'adset_budget','Ad set budget type':'adset_budget_type','Campaign budget':'camp_budget','Campaign budget type':'camp_budget_type',
      'Ad ID':'ad_id','Ad set ID':'adset_id','Reporting starts':'start','Reporting ends':'end','CTR (all)':'ctr_all'})
    for c in ['spend','roas_meta','value_inapp','value_web','installs','clicks','purchases','impressions','frequency','hook_rate','avg_play','adset_budget','camp_budget']:
        d[c]=pd.to_numeric(d[c],errors='coerce')
    d['start']=pd.to_datetime(d['start']); d['end']=pd.to_datetime(d['end'])
    d['week']=(d['start']-pd.to_timedelta(d['start'].dt.weekday,unit='D')).dt.strftime('%Y-%m-%d')
    d['rev']=(d['roas_meta']*d['spend']).fillna(0)
    for c in ['installs','clicks','purchases','impressions']: d[c]=d[c].fillna(0)
    d['hook_x_imp']=d['hook_rate']*d['impressions']
    d=supersede(d,['spend','rev','impressions','installs','clicks','purchases','hook_x_imp','value_inapp','value_web'])
    return d
