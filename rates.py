import json,random,sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from common import STAT_FLAGS,resolve
def ok(c,f,s):
    import operator
    if not all(x in f for x in c.get('flags_all',[])): return False
    if 'flags_any' in c and not any(x in f for x in c['flags_any']): return False
    if any(x in f for x in c.get('flags_none',[])): return False
    for k,cc in c.get('stats',{}).items():
        for op,v in cc.items():
            if not {'gte':s[k]>=v,'lte':s[k]<=v,'gt':s[k]>v,'lt':s[k]<v}[op]: return False
    if 'any_of' in c and not any(ok(x,f,s) for x in c['any_of']): return False
    return True
def run(path,N=200000,seed=1):
    d=json.load(open(path));ev={e['id']:e for e in d['events']};ps=d['player_init']['stats'];rg=random.Random(seed);cnt={}
    en=sorted(d['endings'],key=lambda x:x['priority'])
    for _ in range(N):
        s={k:rg.uniform(*ps[k]['init_range']) for k in ps};f=set();eid=d['player_init']['start_event']
        while True:
            c=resolve(rg.choice([c for c in ev[eid]['choices'] if all((q[1:] not in f) if q.startswith('!') else q in f for q in c['flags']['require'])]),rg)
            for k,v in c['effects'].items(): s[k]=max(ps[k].get('min',-1e18),min(ps[k].get('max',1e18),s[k]+v))
            f|=set(c['flags']['set'])
            if c['next']=='__EVAL__': break
            eid=c['next']
        for sf in d['ending_rules']['stat_flags']:
            if ok({'stats':sf['stats']},f,s): f.add(sf['flag'])
        x=next((x for x in en if ok(x['conditions'],f,s)),None); cnt[x['id']]=cnt.get(x['id'],0)+1
    return {k:f"{v/N*100:.2f}%" for k,v in sorted(cnt.items(),key=lambda t:-t[1])}
if __name__=='__main__': print(run(sys.argv[1]))
