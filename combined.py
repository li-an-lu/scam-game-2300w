"""一局完整人生（人生線＋中途插入的詐騙線）的參考實作與抽樣檢查。
規格：script-life.json meta.scam_integration（說明見 script-life-README.md）。
用法：python3 combined.py [N]；validate.py script-life.json --sample 也會呼叫 run_checks()。"""
import json,os,random,sys
from common import apply_modifiers,pick_text,resolve,set_flags_all
H=os.path.dirname(os.path.abspath(__file__))
def L(n): return json.load(open(os.path.join(H,n)))
def cmp(v,c): return all({'gt':v>n,'gte':v>=n,'lt':v<n,'lte':v<=n}[o] for o,n in c.items())
def ok(c,f,s):
    if not all(x in f for x in c.get('flags_all',[])): return False
    if 'flags_any' in c and not any(x in f for x in c['flags_any']): return False
    if any(x in f for x in c.get('flags_none',[])): return False
    if not all(cmp(s[k],v) for k,v in c.get('stats',{}).items()): return False
    if 'any_of' in c and not any(ok(x,f,s) for x in c['any_of']): return False
    return True
def avail(c,f): return all((r[1:] not in f) if r.startswith('!') else (r in f) for r in c['flags']['require'])
def clampf(ps):
    return lambda k,v: max(ps[k].get('min',-1e18),min(ps[k].get('max',1e18),v)) if k in ps else v
def statflags(R,f,s):
    for sf in R['stat_flags']:
        f.discard(sf['flag'])
        if ok({"stats":sf['stats']},f,s): f.add(sf['flag'])
def judge(d,f,s):
    R=d['ending_rules']; statflags(R,f,s)
    en=sorted(d['endings'],key=lambda x:x['priority'])
    return next((x for x in en if ok(x['conditions'],f,s)),next(x for x in en if x['id']==R['fallback']))
def premise(x,f,where,err):
    v=pick_text(x,f)
    for obj,tag in ((x,''),(v,'/variant '+(v or {}).get('when',{}).get('label','?')) if v else (None,None)):
        if obj is None: continue
        for r in obj.get('requires_flags',[]):
            if r not in f: err.add(f"premise: {where} {x['id']}{tag} requires {r}")
        for r in obj.get('forbids_flags',[]):
            if r in f: err.add(f"premise: {where} {x['id']}{tag} forbids {r}")
def play_scam(h,sd,s,f,cl,rng,err,halt=False):
    """在人生線的數值 s、flags f 上演一條詐騙線；回傳 (結局, 新數值, 內部 flags, duration)。"""
    sev,init=apply_modifiers(sd,f); sev={x['id']:x for x in sev}; scl=clampf(sd['player_init']['stats'])
    sc=h.get('amount_scaling'); fac=1.0
    if sc: fac=max(s[sc['stat']],sc['floor'])/sc['ref']
    def eff(e):
        return {k:(v*fac if (sc and k==sc['stat'] and v<0) else v) for k,v in e.items()}
    s={k:scl(k,s[k]+init.get(k,0)) for k in s}; sf=set(f); internal=set(); x=sev[h['entry_event']]; d2=0
    while True:
        d2+=1
        if d2>500: err.add("scam loop"); break
        oe=eff(x.get('on_enter_effects',{})); s={k:scl(k,s[k]+oe.get(k,0)) for k in s}
        ca=[c2 for c2 in x['choices'] if avail(c2,sf)]
        if not ca: err.add(f"scam dead end {h['line']}:{x['id']}"); break
        c2=resolve(rng.choice(ca),rng); e2=eff(c2['effects']); s={k:scl(k,s[k]+e2.get(k,0)) for k in s}
        sf|=set(c2['flags']['set']); internal|=set(c2['flags']['set'])
        if c2['next']=='__EVAL__': break
        x=sev[c2['next']]
    end=judge(sd,sf,s); premise(end,sf,'scam:'+h['line'],err)
    dur=h['duration']['default_years']
    for r in h['duration']['rules']:
        if any(q in internal for q in r['if_flags_any']): dur=r['years']; break
    return end,s,internal,dur
def play(life,scams,rng,err):
    SI=life['meta']['scam_integration']; RM=SI['return_map']; rec=SI['pre_entry']['mental_recovery']
    pi=life['player_init']; ps=pi['stats']; cl=clampf(ps)
    IR=life['meta'].get('initial_stats_roll')
    if IR:  # v0.9：均勻整數骰＋temperament
        s={k:rng.randint(*IR['stats'][k]['range']) for k in ps}
        u=rng.random(); acc=0
        for t in IR['temperament']:
            acc+=t['p']
            if u<acc: s['心理']=cl('心理',s['心理']+t.get('心理',0)); break
    else: s={k:rng.choice(ps[k]['init_range']) for k in ps}
    HALT=life['meta'].get('early_halt'); halted=False
    REC_Y=float(os.environ.get('REC_Y',life['meta'].get('mental_time_recovery',{}).get('per_year',0))); ages_prev=None
    ev={e['id']:e for e in life['events']}; eid=pi['start_event']; f=set(); ages=[]; hist=[]; dep=0
    end_age=ev['LIFE_ROUTER']['age']
    plan=[]  # 開局就抽好：(entry_age, 順序, line, 是否抽中機率)
    for i,h in enumerate(SI['lines']):
        w=h['entry_window']; plan.append([w['base_age']+rng.randint(w['offset_min'],w['offset_max']),i,h,rng.random()<h['probability'],False])
    while True:
        dep+=1
        if dep>500: err.add("loop "+eid); break
        e=ev[eid]; ages.append(('life:'+eid,e['age']))
        if REC_Y and ages_prev is not None and e['age']>ages_prev: s['心理']=cl('心理',s['心理']+REC_Y*(e['age']-ages_prev))
        ages_prev=e['age']
        av=[c for c in e['choices'] if avail(c,f)]
        c=resolve(rng.choice(av),rng); s={k:cl(k,s[k]+c['effects'].get(k,0)) for k in s}; f|=set(c['flags']['set'])
        if HALT and s['心理']<=0: halted=True; f.add('life_halted'); break
        aN=end_age if c['next']=='__EVAL__' else ev[c['next']]['age']
        if c['next']=='__EVAL__' and eid!='LIFE_ROUTER': err.add("life ends before LIFE_ROUTER")
        cur=e['age']
        for p in sorted([p for p in plan if not p[4] and e['age']<=p[0]<aN],key=lambda p:(p[0],p[1])):
            age0,_,h,hit=max(p[0],cur),p[1],p[2],p[3]
            if age0+1>aN:  # 同一空檔已被前一條線佔用：順延到下一個空檔（v0.6 flexible slot）
                p[0]=max(age0,aN); continue
            p[4]=True
            if age0>=end_age: err.add(f"entry_age {age0} >= LIFE_ROUTER"); continue
            statflags(scams[h['line']]['ending_rules'],f,s)
            if not (hit and ok(h.get('trigger',{}),f,s)): continue
            ages.append((f"enter:{h['line']}",age0))
            s=dict(s); s[rec['stat']]=cl(rec['stat'],s[rec['stat']]+rec['delta'])
            end,s,internal,dur=play_scam(h,scams[h['line']],s,f,cl,rng,err,halt=bool(HALT))
            age1=age0+dur; cur=age1; ages.append((f"exit:{h['line']}",age1))
            if age1>aN: err.add(f"exit_age {age1} > next life event age {aN}")
            m=RM[h['line']].get(end['id'])
            if m is None: err.add(f"return_map missing {h['line']}:{end['id']}"); m={"flags":[]}
            f|={q.format(line=h['line']) for q in RM['_always']['flags']+m['flags']}
            f|={v for k,v in RM['_carry_internal'].items() if not k.startswith('_') and k in internal}
            for k,v in m.get('stats_delta',{}).items(): s[k]=s[k]+v
            s={k:cl(k,v) for k,v in s.items()}
            hist.append({"line":h['line'],"ending_id":end['id'],"entry_age":age0,"exit_age":age1,"after":eid,"return_to":c['next']})
            if HALT and s['心理']<=0: halted=True; f.add('life_halted'); break
        if halted or c['next']=='__EVAL__': break
        eid=c['next']
    if halted:
        end=next(x for x in life['endings'] if x['id']==HALT['ending']); premise(end,f,'life',err)
        return end['id'],hist,max([e['age']]+[x['exit_age'] for x in hist]),f
    end=judge(life,f,s); premise(end,f,'life',err)
    a=[v for _,v in ages]
    if any(a[i]>a[i+1] for i in range(len(a)-1)): err.add("age not monotonic: "+str(ages))
    lived=max([ev[eid]['age']]+[x['exit_age'] for x in hist])
    return end['id'],hist,lived,f
def static_checks(life,scams,err,info):
    SI=life['meta']['scam_integration']; ev={e['id']:e for e in life['events']}
    lf=set(life['meta']['cross_line_flags']); end_age=ev['LIFE_ROUTER']['age']
    setters={}
    for e in life['events']:
        for c in e['choices']:
            for q in set_flags_all(c): setters.setdefault(q,[]).append(e['age'])
    for h in SI['lines']:
        w=h['entry_window']; lo,hi=w['base_age']+w['offset_min'],w['base_age']+w['offset_max']
        if [lo,hi]!=w['range']: err.add(f"{h['line']} entry_window range mismatch")
        if hi>=end_age: err.add(f"{h['line']} entry window reaches LIFE_ROUTER")
        if not 0<=h['probability']<=1: err.add(f"{h['line']} bad probability")
        if max(r['years'] for r in h['duration']['rules']+[{'years':h['duration']['default_years']}])>1: err.add(f"{h['line']} duration>1 breaks exit_age<=next event guarantee")
        sd=scams[h['line']]; ids={e['id'] for e in sd['events']}
        if h['entry_event'] not in ids: err.add(f"entry_event {h['entry_event']} not in {h['line']}")
        tr=h.get('trigger',{}); fl=tr.get('flags_all',[])+tr.get('flags_any',[])
        for q in fl:
            if q not in setters: err.add(f"trigger flag {q} never set in life line")
        if fl and not any(g<=hi for q in fl for g in setters.get(q,[])): err.add(f"{h['line']} trigger can never be met in window")
        miss={x['id'] for x in sd['endings']}-set(SI['return_map'][h['line']])
        if miss: err.add(f"return_map {h['line']} missing {miss}")
        internal={q for e in sd['events'] for c in e['choices'] for q in set_flags_all(c)}
        col=internal&lf-set(SI['return_map']['_carry_internal'])
        if col: info.add(f"{h['line']}: internal flags also life flags (shared meaning) {sorted(col)}")
        for m in sd.get('cross_line_modifiers',[]):
            dead=[q for q in m['if_flags'].get('all',[]) if q in setters and not any(x<=hi for x in setters[q])]
            so=m.get('mode')=='standalone_only'
            if dead and so: info.add(f"standalone_only (ok): {h['line']}:{m['id']} needs {dead[0]} (set at {min(setters[dead[0]])}), window {lo}-{hi}")
            elif dead: err.add(f"dead modifier in window {lo}-{hi}: {h['line']}:{m['id']} needs {dead[0]} — mark mode:standalone_only")
            elif so: err.add(f"{h['line']}:{m['id']} marked standalone_only but can fire in combined mode")
TARGET_MIN,TARGET_MAX=0.02,0.40
def run_checks(N=20000,seed=42,verbose=True):
    life=L('script-life.json'); SI=life['meta']['scam_integration']
    scams={l['line']:L(l['script']) for l in SI['lines']}
    err=set(); info=set(); static_checks(life,scams,err,info)
    rng=random.Random(seed); ends={}; per={l:{} for l in scams}; cnt={}; lived={}; entry={l:{} for l in scams}
    for _ in range(N):
        e,hist,a,_f=play(life,scams,rng,err); ends[e]=ends.get(e,0)+1; lived[a]=lived.get(a,0)+1
        cnt[len(hist)]=cnt.get(len(hist),0)+1
        for x in hist:
            if x['ending_id']=='HALTED': continue
            per[x['line']][x['ending_id']]=per[x['line']].get(x['ending_id'],0)+1
            entry[x['line']][x['entry_age']]=entry[x['line']].get(x['entry_age'],0)+1
    for x in life['endings']:
        if x['id'] not in ends: err.add(f"combined: life ending unreachable {x['id']}")
    for l,sd in scams.items():
        n=sum(per[l].values())
        for x in sd['endings']:
            r=per[l].get(x['id'],0)/max(n,1)
            if not TARGET_MIN<=r<=TARGET_MAX: err.add(f"combined target: {l} {x['id']} {r:.1%} not in [2%,40%] (among {n} lives that entered)")
    if verbose:
        print(f"COMBINED N={N} seed {seed}")
        print("  scams per life:",{k:f"{v/N:.1%}" for k,v in sorted(cnt.items())},"age_lived:",lived)
        print("  life endings:",{k:f"{v/N:.1%}" for k,v in sorted(ends.items(),key=lambda x:-x[1])})
        for l in scams:
            n=sum(per[l].values())
            print(f"  {l}: entered {n/N:.1%} of lives; entry ages {dict(sorted(entry[l].items()))}")
            print("    ",{k:f"{v/n:.1%}" for k,v in sorted(per[l].items(),key=lambda x:-x[1])})
        for i in sorted(info): print("  info:",i)
        print("COMBINED checks","OK" if not err else "ERRORS"); [print("  ERR",x) for x in sorted(err)]
    return sorted(err)
if __name__=="__main__": sys.exit(1 if run_checks(int(sys.argv[1]) if len(sys.argv)>1 else 20000) else 0)
