import re, sys
import pandas as pd, numpy as np
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from build import parse_name as parse_adset

AWARE = {'unaware':'Unaware','completelyunaware':'Unaware','problemaware':'ProblemAware','solutionaware':'SolutionAware',
         'productaware':'ProductAware','mostaware':'MostAware'}
LANGS = {'US','EN','ES','PT','BR','TH','ID','RU','UA','TR','PL','JP','KR','CH','PH','FR','DE','IT','IN','AR','VN','ENG','MX','NL'}
# ad persona token -> canonical persona (by judgment; spec §18)
PMAP = [
 (r'^passportgirl', 'GirlWantsToRelocate'), (r'^passportbro', 'PassportBro'),
 (r'^gringolover', 'GringoMaleLover'), (r'^slavic', 'SlavicFemaleLover'),
 (r'^latina', 'LatinaFemaleLover'), (r'^tiktoksafelatino|^latino', 'LatinoMaleLover'),
 (r'^friends|^internationalfriend|^intlfriend', 'InternationalFriendFinder'),
 (r'^chinese|^asianfemale|^asianlover|^asiandating|^koreanfemale', 'AsianFemaleLover'),
 (r'^southeastasian', 'SoutheastAsianFemaleLover'), (r'^asianmale', 'AsianMaleLover'),
 (r'^indianboy|^egoboost', 'EgoBoostForIndianBoy'), (r'^christian', 'ChristianMatchWorldwide'),
 (r'^muslim', 'MuslimMatchWorldwide'), (r'^blk|^blackafrican|^blackdating|^interracial', 'InterracialDatingSeekers'),
 (r'^attractiveblack', 'AttractiveBlackFemale'), (r'^koreaboo', 'KoreanMaleCultureLover'),
 (r'^matur|^304050|^3040|^5060|^3060', 'MatureDating'), (r'^lgbt', 'LGBTQ'), (r'^singlemom', 'SingleMom'),
 (r'^churnlocal|^angrywithlocal|^localdating', 'LocalDatingFatigue'), (r'^churnraya|^celebrity', 'CelebrityCrushLookalikeLover'),
 (r'^learnlanguage|^newlanguage', 'NewLanguageLearner'), (r'^chat', 'ChatOnly'), (r'^plussize', 'PlusSizeWomen'),
 (r'^beachgirl', 'BeachGirl'), (r'^beachboy|^sexybeach', 'SexyBeachGuy'), (r'^womanmarriage|^richhusband', 'RichHusbandFinder'),
 (r'^divorcee', 'Divorcee'), (r'^middleeast', 'MiddleEastern'), (r'^sexyfemale', 'SexyFemaleLover'),
 (r'^general', 'General'),
]

def clean(n):
    n = str(n)
    n = re.sub(r'\s*[–-]\s*Copy(\s*\d+)?\s*$', '', n)
    n = re.sub(r'(\.(mp4|png|jpg|jpeg|mov|gif|webp))+$', '', n, flags=re.I)
    n = re.sub(r'(\.(mp4|png|jpg|jpeg|mov|gif|webp))+', '', n, flags=re.I)
    return n.strip()

def parse_ad(name):
    n = clean(name)
    toks = [t.strip() for t in n.split('-')]
    out = dict(ad_clean=n, n_fields=len(toks), ad_persona_raw='', ad_persona='Unknown', lang='', concept='', conceptname='', hook='',
               headline='', angle='', awareness='', fmt='', strategist='', designer='', batch='', batch_week=None, ad_version='other')
    if len(toks) < 5:
        out['ad_version'] = 'unstructured'
        m = re.search(r'\b(VID|IMG|video|static)\b', n, re.I)
        return out
    # format
    for i, t in enumerate(toks):
        if t.upper() in ('VID', 'IMG'):
            out['fmt'] = t.upper(); fi = i
            break
    else:
        fi = None
    # batch
    for t in toks:
        m = re.match(r'Batch(\d{4})Week(\d{1,2})', t, re.I)
        if m:
            out['batch'] = f'{m.group(1)}W{int(m.group(2)):02d}'
            out['batch_week'] = pd.Timestamp.fromisocalendar(int(m.group(1)), max(1, min(52, int(m.group(2)))), 1)
            break
    # concept code: first token in first 4 that is 5-7 alnum with a digit and a letter
    ci = None
    pos = 1 if (toks[0].upper() in LANGS) else 2
    if len(toks) > pos and re.fullmatch(r'[A-Za-z0-9]{5,7}', toks[pos]) and (re.search(r'\d', toks[pos]) or (re.search(r'[a-z]', toks[pos]) and re.search(r'[A-Z]', toks[pos][1:]))):
        ci = pos; out['concept'] = toks[pos]
    for i, t in enumerate(toks[:4] if ci is None else []):
        if re.fullmatch(r'[A-Za-z0-9]{5,7}', t) and re.search(r'\d', t) and re.search(r'[A-Za-z]', t) and not re.fullmatch(r'\d+', t):
            ci = i; out['concept'] = t; break
    # persona + lang
    first = toks[0]
    if first.upper() in LANGS or re.fullmatch(r'\d{4,6}', first) and False:
        out['lang'] = first.upper()
    else:
        out['ad_persona_raw'] = first
        if len(toks) > 1 and toks[1].upper() in LANGS:
            out['lang'] = toks[1].upper()
    low = first.lower()
    for pat, p in PMAP:
        if re.search(pat, low):
            out['ad_persona'] = p; break
    if out['lang'] in ('US', 'ENG'): out['lang'] = 'EN'
    if out['lang'] == 'BR': out['lang'] = 'PT'
    # fields after concept
    if ci is not None:
        rest = toks[ci + 1:(fi if fi is not None else len(toks))]
        if rest: out['conceptname'] = rest[0].lower()
        if len(rest) > 1: out['hook'] = rest[1]
        # awareness
        aw = [t for t in rest if t.lower() in AWARE]
        if aw:
            out['awareness'] = AWARE[aw[0].lower()]
            ai = rest.index(aw[0])
            if ai >= 1 and ai - 1 >= 2: out['angle'] = rest[ai - 1].lower()
            if ai >= 3: out['headline'] = rest[2].lower() if ai > 3 else ''
        elif len(rest) > 2:
            out['headline'] = rest[2].lower()
    # v5 strategist/designer
    if fi is not None and len(toks) > fi + 3 and re.fullmatch(r'[A-Z]{3}', toks[fi + 1]) and re.fullmatch(r'[A-Z]{3}', toks[fi + 2]):
        out['strategist'], out['designer'] = toks[fi + 1], toks[fi + 2]
        out['ad_version'] = 'v5'
    elif out['awareness']:
        out['ad_version'] = 'v4'
    elif ci is not None:
        out['ad_version'] = 'early'
    return out
