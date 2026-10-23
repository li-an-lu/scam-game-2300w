import sys as _s0
if len(_s0.argv)>1 and _s0.argv[1].endswith("achievements.json"):
    # ---- achievements v1：所有引用都必須真實存在於 script-*.json ----
    import json as _j, re as _re
    from common import BRAND_BAN_TEXT as _BBA
    L=["life","mule","shopping","investment","romance","marriage","parent"]; D={l:_j.load(open(f"script-{l}.json")) for l in L}
    EV={l:{e["id"]:e for e in D[l]["events"]} for l in L}; EN={l:{e["id"] for e in D[l]["endings"]} for l in L}
    FL={l:set() for l in L}
    for l in L:
        for e in D[l]["events"]:
            for c in e.get("choices",[]):
                FL[l]|=set(c.get("flags",{}).get("set",[]))
                for o in c.get("outcomes",[]): FL[l]|=set(o.get("flags_set",[]))
        for e in D[l]["endings"]: FL[l]|=set(e.get("requires_flags",[]))|set(e.get("forbids_flags",[]))
    for k,v in D["life"]["meta"]["scam_integration"]["return_map"].items():
        if isinstance(v,dict):
            for x in v.values():
                if isinstance(x,dict): FL["life"]|=set(x.get("flags",[]))
                elif isinstance(x,str): FL["life"].add(x)
    A=_j.load(open(_s0.argv[1]))["achievements"]; E=[]; ids=set()
    for a in A:
        i=a["id"]
        if i in ids: E.append(f"{i}: duplicate id")
        ids.add(i)
        for k in ("id","name","description","unlock","hidden","category","source"):
            if k not in a: E.append(f"{i}: missing {k}")
        if a["category"] not in ("ending_codex","red_flag","life"): E.append(f"{i}: bad category")
        if len(a["name"])>10: E.append(f"{i}: name >10")
        if not isinstance(a["hidden"],bool): E.append(f"{i}: hidden not bool")
        if not a["source"]: E.append(f"{i}: no source")
        txt=a["name"]+a["description"]
        if _re.search(r"\d+(\.\d+)?\s*%|玩家達成|達成率",txt): E.append(f"{i}: 疑似達成率數字")
        for b in _BBA:
            if b in txt: E.append(f"{i}: brand {b}")
        u=a["unlock"]
        if u.get("scope") not in ("run","collection"): E.append(f"{i}: bad scope")
        for key in ("requires_endings","requires_any_endings","forbids_endings"):
            for r in u.get(key,[]):
                l,_,x=r.partition(":")
                if l not in EN or x not in EN[l]: E.append(f"{i}: {key} {r} 不存在")
        for key in ("requires_flags","forbids_flags"):
            for r in u.get(key,[]):
                l,_,x=r.partition(":")
                if l not in FL or x not in FL[l]: E.append(f"{i}: {key} {r} 不存在")
        for c in u.get("requires_choices",[]):
            ev=EV.get(c["line"],{}).get(c["event"])
            if not ev: E.append(f"{i}: event {c['line']}:{c['event']} 不存在"); continue
            ch=ev["choices"]
            if c["choice_index"]>=len(ch) or ch[c["choice_index"]]["text"]!=c["text"]: E.append(f"{i}: choice {c} 不符")
        if not any(u.get(k) for k in ("requires_endings","requires_any_endings","requires_flags","requires_choices")): E.append(f"{i}: 無解鎖條件")
        for s_ in a["source"]:
            l,_,x=s_.get("ref","").partition(":")
            if s_.get("ref")!="all" and (l not in EN or (x not in EN[l] and x not in EV[l])): E.append(f"{i}: source ref {s_.get('ref')} 不存在")
    for l in L:
        need={f"{l}:{k}" for k in EN[l]}; got={a["unlock"]["requires_endings"][0] for a in A if a["category"]=="ending_codex" and len(a["unlock"]["requires_endings"])==1}
        if need-got: E.append(f"codex 缺 {need-got}")
    print("achievements",len(A),"ERRORS "+str(E) if E else "OK"); _s0.exit(1 if E else 0)
import json,itertools,sys
fn=sys.argv[1] if len(sys.argv)>1 else 'script-investment.json'
d=json.load(open(fn)); ev={e['id']:e for e in d['events']}; en={e['id']:e for e in d['endings']}
err=[]; R=d['ending_rules']; RF=d.get('red_flag_texts',{})
from common import branches,resolve,set_flags_all
def walk(o,path=""):
    if isinstance(o,dict):
        if 'url' in o and not o['url']: err.append(f"null url at {path}")
        if 'verified' in o and not isinstance(o['verified'],bool): err.append(f"verified not bool at {path}")
        for k,v in o.items(): walk(v,path+"/"+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,f"{path}[{i}]")
walk(d)
for e in d['events']:
    if not e.get('sources'): err.append(f"{e['id']} no sources")
    for c in e['choices']:
        if c['next']!='__EVAL__' and c['next'] not in ev: err.append(f"{e['id']}->{c['next']} missing")
        for f in set_flags_all(c):
            if f.startswith('missed_') and f not in RF: err.append(f"no red_flag_text for {f}")
# ---- v0.6/v4.6：每個選項（含 unlock_choice 解鎖選項）都要有 outcome_text 與 log_text ----
from common import BRAND_BAN as _BB
_BB=list(_BB)+["思樂冰","YouTuber"]  # v4.7：前台文字也不可出現這兩個真實品牌／平台稱呼
_chs=[(e['id'],(i if not c.get('random') else f"{i}.{j}"),m) for e in d['events'] for i,c in enumerate(e['choices']) for j,(_p,m) in enumerate(branches(c))]
# ---- v4.7：random:true 選項（一個按鈕、結果隨機） ----
_rerr=[]; _rn=0
for e in d['events']:
    for i,c in enumerate(e['choices']):
        if not c.get('random'): continue
        _rn+=1; tag=f"{e['id']}[{i}] random"
        O_=c.get('outcomes') or []
        if len(O_)<2: _rerr.append(f"{tag}: needs >=2 outcomes")
        if any(not isinstance(b.get('probability'),(int,float)) or not 0<b['probability']<=1 for b in O_): _rerr.append(f"{tag}: probability must be in (0,1]")
        elif abs(sum(b['probability'] for b in O_)-1)>1e-9: _rerr.append(f"{tag}: probabilities sum {sum(b['probability'] for b in O_)} != 1")
        if (c.get('random_note') or {}).get('design_assumption') is not True: _rerr.append(f"{tag}: random_note.design_assumption must be true")
        for j,b in enumerate(O_):
            for k in b.get('effects',{}):
                if k not in d['player_init']['stats']: _rerr.append(f"{tag}.{j}: unknown stat {k}")
            if not isinstance(b.get('flags_set',[]),list): _rerr.append(f"{tag}.{j}: flags_set not list")
            nx=b.get('next',c['next'])
            if nx!='__EVAL__' and nx not in ev: _rerr.append(f"{tag}.{j}: next {nx} missing")
            for f in b.get('flags_set',[]):
                if f.startswith('missed_') and f not in RF: _rerr.append(f"{tag}.{j}: no red_flag_text for {f}")
    if sum(1 for c in e['choices'] if not c.get('random') and c.get('text') and [x['text'] for x in e['choices']].count(c['text'])>1 and not c['flags']['require']):
        _rerr.append(f"{e['id']}: duplicate choice labels without require (use random:true)")
err+=_rerr
print("random choice checks: random choices",_rn,"OK" if not _rerr else "ERRORS "+str(_rerr))
# ---- v4.7：每個結局都要有非空 help_resources（每筆有 name、url） ----
_herr=[]
for x in d['endings']:
    H_=x.get('help_resources')
    if not H_: _herr.append(f"{x['id']} help_resources empty")
    elif any(not h.get('name') or not h.get('url') for h in H_): _herr.append(f"{x['id']} help_resources item lacks name/url")
    elif not any('165' in h['url'] or '165' in h['name'] for h in H_): _herr.append(f"{x['id']} help_resources lacks 165")
err+=_herr
print("help_resources checks: endings",len(d['endings']),"OK" if not _herr else "ERRORS "+str(_herr))
# ---- v4.7：standalone_only 跨線修正只列 info ----
for m in d.get('cross_line_modifiers',[]):
    if m.get('mode')=='standalone_only':
        if not m.get('mode_note'): err.append(f"{m['id']} standalone_only without mode_note")
        print(f"info: {m['id']} mode=standalone_only（合併模式觸發不了，保留給單線模式）")
    elif m.get('mode') not in (None,'all'): err.append(f"{m['id']} bad mode {m.get('mode')}")
_chs+=[('unlock:'+m['id'],0,m['effect']['choice']) for m in d.get('cross_line_modifiers',[]) if m['effect'].get('type')=='unlock_choice']
for _eid,_i,_c in _chs:
    for _k in ('outcome_text','log_text'):
        if not isinstance(_c.get(_k),str) or not _c[_k].strip(): err.append(f"{_eid}[{_i}] missing {_k}")
        elif any(b in _c[_k] for b in _BB): err.append(f"{_eid}[{_i}] brand in {_k}")
    if isinstance(_c.get('log_text'),str) and len(_c['log_text'])>20: err.append(f"{_eid}[{_i}] log_text >20 chars")
print("choice feedback checks: choices",len(_chs),"OK" if not any('outcome_text' in x or 'log_text' in x for x in err) else "ERRORS")
# ---- v0.7：選項標籤只描述行動：≤15 字、不含結果字詞（outcomes.LABEL_BLOCKLIST） ----
from outcomes import LABEL_MAX as _LM, LABEL_BLOCKLIST as _LB
_labs=[(f"{_e}[{_i}]",_c['text']) for _e,_i,_c in _chs]
_labs+=[('rewrite:'+m['id'],m['effect']['text']) for m in d.get('cross_line_modifiers',[]) if m['effect'].get('type')=='rewrite_text' and m['effect'].get('field')=='choice_text']
_lerr=[]
for _k,_v in _labs:
    if len(_v)>_LM: _lerr.append(f"{_k} label >{_LM} chars: {_v}")
    _hit=[b for b in _LB if b in _v]
    if _hit: _lerr.append(f"{_k} label has outcome word {_hit}: {_v}")
err+=_lerr
print("choice label checks: labels",len(_labs),"OK" if not _lerr else "ERRORS")
for x in en.values():
    for k in ('conditions','text','case_card','missed_red_flags','sources','priority'):
        if k not in x: err.append(f"{x['id']} lacks {k}")
if R['fallback'] not in en: err.append("bad fallback")
pi=d['player_init']; ps=pi['stats']
def cmp(v,c): return all({'gt':v>n,'gte':v>=n,'lt':v<n,'lte':v<=n}[o] for o,n in c.items())
def ok(cond,f,s):
    if not all(x in f for x in cond.get('flags_all',[])): return False
    if 'flags_any' in cond and not any(x in f for x in cond['flags_any']): return False
    if any(x in f for x in cond.get('flags_none',[])): return False
    if not all(cmp(s[k],c) for k,c in cond.get('stats',{}).items()): return False
    if 'any_of' in cond and not any(ok(c,f,s) for c in cond['any_of']): return False
    return True
def clamp(k,v): return max(ps[k].get('min',-1e18),min(ps[k].get('max',1e18),v))
# ---- v4.3 additive: --sample 模式也跑 v4／v4.2 檢查（下方 --sample 區塊會直接 exit，所以先在這裡檢查；前提檢查改用抽樣） ----
if '--sample' in sys.argv and (any('presentation' in e for e in d['events']) or 'red_flag_anchors' in d or d['meta'].get('version','').startswith('0.4')):
    import random as _r
    from common import CHAT_APP_TYPES,BRAND_BAN,MIN_TIMER_S,brand_hits,NO_CATEGORY,pick_text
    serr=[]
    for e in d['events']:
        if e.get('presentation') not in ('card','chat','notification','timeskip'): serr.append(f"{e['id']} bad presentation")
        ch=e.get('chat')
        if e.get('presentation')=='chat' and not ch: serr.append(f"{e['id']} chat missing")
        if ch:
            if ch.get('app') not in CHAT_APP_TYPES: serr.append(f"{e['id']} chat.app not a generic type")
            blob=json.dumps({k:ch.get(k) for k in ('app_display_name','theme','contact','messages')},ensure_ascii=False)+json.dumps(e.get('interrupts',[]),ensure_ascii=False)
            for b in BRAND_BAN:
                if b in blob: serr.append(f"{e['id']} brand name '{b}' in chat")
            ids=[m['id'] for m in ch.get('messages',[])]
            if len(ids)!=len(set(ids)) or not ids: serr.append(f"{e['id']} message ids empty/dup")
            for it in e.get('interrupts',[]):
                if it.get('at') not in ids: serr.append(f"{e['id']} interrupt at unknown msg")
        pr=e.get('pressure')
        if pr:
            if pr.get('timer_s',0)<MIN_TIMER_S: serr.append(f"{e['id']} timer_s<{MIN_TIMER_S}")
            if pr.get('can_disable') is not True: serr.append(f"{e['id']} timer not disableable")
        for c in [_m for _c0 in e['choices'] for _p,_m in branches(_c0)]:
            if c.get('grid') not in ('green','yellow','red'): serr.append(f"{e['id']} choice grid missing")
    if not d['meta'].get('no_pressure_mode',{}).get('available'): serr.append("meta.no_pressure_mode missing")
    A=d.get('red_flag_anchors',{})
    for f in RF:
        if f not in A: serr.append(f"no anchor for {f}")
    for f,lst in A.items():
        for a in lst:
            e=ev.get(a['event'])
            if not e or a['message'] not in [m['id'] for m in e.get('chat',{}).get('messages',[])]: serr.append(f"bad anchor {f}->{a}")
    for x in en.values():
        for k in ('title','title_emoji','grid_color','rarity_key','real_world_stat','share_text','share_card','requires_flags','forbids_flags'):
            if k not in x: serr.append(f"{x['id']} lacks {k}")
        r=x.get('real_world_stat') or {}
        if r.get('kind')!='share_of_reported_cases': serr.append(f"{x['id']} real_world_stat.kind must be share_of_reported_cases")
        if 'rarity' in x: serr.append(f"{x['id']} still has legacy 'rarity' field")
        if r.get('value_pct') is None:
            if not r.get('null_reason'): serr.append(f"{x['id']} real_world_stat null without reason")
            if r.get('display') is not None: serr.append(f"{x['id']} null stat must have display=None (v4.5: omit, never show placeholder)")
        elif not (r.get('formula') and r.get('source') and r.get('display')): serr.append(f"{x['id']} real_world_stat lacks formula/source/display")
        for v in x.get('text_variants',[]):
            if 'when' not in v or not v.get('text'): serr.append(f"{x['id']} bad text_variant")
    for st_ in d.get('stats',[]):
        if not isinstance(st_.get('self_calculated'),bool): serr.append(f"stat '{st_.get('label')}' self_calculated not bool")
    for h in brand_hits(d): serr.append(f"brand in player text: {h}")
    # 前提檢查（抽樣版）：每次隨機走到結局，確認 requires_flags／forbids_flags（含 text_variant）成立
    rg=_r.Random(7); NP=50000; pcnt={}
    for _ in range(NP):
        fam=rg.choice(pi['family_pool']); s_=dict(zip(ps,[rg.choice(ps[k]['init_range']) for k in ps]))
        s_['存款']=clamp('存款',round(s_['存款']*(1+fam.get('存款_mod',0))))
        for k in ps:
            if k!='存款' and k in fam: s_[k]=clamp(k,s_[k]+fam[k])
        eid=pi['start_event']; f=set()
        for _dep in range(300):
            av=[c for c in ev[eid]['choices'] if all((q[1:] not in f) if q.startswith('!') else (q in f) for q in c['flags']['require'])]
            if not av: break
            c=resolve(rg.choice(av),rg); s_={k:clamp(k,s_[k]+c['effects'].get(k,0)) for k in s_}; f|=set(c['flags']['set'])
            if c['next']!='__EVAL__': eid=c['next']; continue
            for sf in R['stat_flags']:
                if ok({"stats":sf['stats']},f,s_): f.add(sf['flag'])
            x=next((x for x in sorted(en.values(),key=lambda x:x['priority']) if ok(x['conditions'],f,s_)),en[R['fallback']])
            v=pick_text(x,f); key=x['id']+("#"+v['when'].get('label','v') if v else ""); pcnt[key]=pcnt.get(key,0)+1
            for src_ in [x]+([v] if v else []):
                for q in src_.get('requires_flags',[]):
                    if q not in f: serr.append(f"{key} reached without required flag {q}")
                for q in src_.get('forbids_flags',[]):
                    if q in f: serr.append(f"{key} reached with forbidden flag {q}")
            break
    serr=sorted(set(serr)); err+=serr
    print("v4/v4.2 checks (sample mode): events",len(d['events']),"anchors",sum(len(v) for v in A.values()),f"premise sample N={NP}",dict(sorted(pcnt.items())),"ERRORS" if serr else "OK")
    if serr: print(serr[:15])
# ---- v4.2 additive: --sample 模式（路徑爆炸時以 Monte Carlo 取代 DFS 窮舉）----
if '--sample' in sys.argv:
    import random
    N=int(sys.argv[sys.argv.index('--sample')+1]) if len(sys.argv)>sys.argv.index('--sample')+1 and sys.argv[sys.argv.index('--sample')+1].isdigit() else 200000
    rng=random.Random(42); hit={}; seen_c=set(); seen_e=set()
    for _ in range(N):
        fam=rng.choice(pi['family_pool']); s=dict(zip(ps,[rng.choice(ps[k]['init_range']) for k in ps]))
        s['存款']=clamp('存款',round(s['存款']*(1+fam.get('存款_mod',0))))
        for k in ps:
            if k!='存款' and k in fam: s[k]=clamp(k,s[k]+fam[k])
        eid=pi['start_event']; f=set(); dep=0
        while True:
            dep+=1
            if dep>200: err.append("loop "+eid); break
            seen_e.add(eid)
            av=[(i,c) for i,c in enumerate(ev[eid]['choices']) if all((r[1:] not in f) if r.startswith('!') else (r in f) for r in c['flags']['require'])]
            if not av: err.append("dead end (no available choice) "+eid); break
            i,c=rng.choice(av); seen_c.add((eid,i)); c=resolve(c,rng)
            s={k:clamp(k,s[k]+c['effects'].get(k,0)) for k in s}; f|=set(c['flags']['set'])
            if c['next']!='__EVAL__': eid=c['next']; continue
            for sf in R['stat_flags']:
                if ok({"stats":sf['stats']},f,s): f.add(sf['flag'])
            end=next((x['id'] for x in sorted(en.values(),key=lambda x:x['priority']) if ok(x['conditions'],f,s)),R['fallback'])
            hit[end]=hit.get(end,0)+1; break
    for e in d['events']:
        if e['id'] not in seen_e: err.append(f"event never reached {e['id']}")
        for i,_c in enumerate(e['choices']):
            if (e['id'],i) not in seen_c: err.append(f"choice never taken {e['id']}[{i}]")
    if {k for k in en if not en[k].get('combined_only')}-set(hit): err.append("unreachable endings "+str({k for k in en if not en[k].get('combined_only')}-set(hit)))
    err=sorted(set(err))
    print(f"SAMPLE N={N} (uniform random choice per step, seed 42)")
    for k,v in sorted(hit.items(),key=lambda x:-x[1]): print(f"  {k}: {v} ({v/N:.1%})")
    print("SAMPLE checks","OK" if not err else "ERRORS (see below)")
    SAMPLE_HIT=dict(hit)  # 繼續執行其餘檢查；完整窮舉改用抽樣結果
hit={}; paths=0; fallback_hits=0; stat_only=[]
SAMPLED='--sample' in sys.argv
if SAMPLED: hit=SAMPLE_HIT; paths=N
for fam in ([] if SAMPLED else pi['family_pool']):
  for init in itertools.product(*[ps[k]['init_range'] for k in ps]):
    s0=dict(zip(ps,init))
    s0['存款']=clamp('存款',round(s0['存款']*(1+fam.get('存款_mod',0))))
    for k in ps:
        if k!='存款' and k in fam: s0[k]=clamp(k,s0[k]+fam[k])
    stack=[(pi['start_event'],s0,frozenset(),0)]
    while stack:
        eid,s,f,dep=stack.pop()
        if dep>100: err.append("loop "+eid); break
        if not ev[eid]['choices']: err.append("dead end "+eid)
        for c in [_m for _c0 in ev[eid]['choices'] for _p,_m in branches(_c0)]:
            if not all((r[1:] not in f) if r.startswith('!') else (r in f) for r in c['flags']['require']): continue
            s2={k:clamp(k,s[k]+c['effects'].get(k,0)) for k in s}
            f2=set(f)|set(c['flags']['set'])
            if c['next']!='__EVAL__': stack.append((c['next'],s2,frozenset(f2),dep+1)); continue
            for sf in R['stat_flags']:
                if ok({"stats":sf['stats']},f2,s2): f2.add(sf['flag'])
            paths+=1; end=None
            for x in sorted(en.values(),key=lambda x:x['priority']):
                if ok(x['conditions'],f2,s2): end=x['id']; break
            if end is None: end=R['fallback']; fallback_hits+=1
            hit[end]=hit.get(end,0)+1
            # ending conditions must never test stats directly (v3 rule 4)
for x in en.values():
    if '"stats"' in json.dumps(x['conditions']): err.append(f"{x['id']} uses raw stats; use stat_flags")
if {k for k in en if not en[k].get('combined_only')}-set(hit): err.append("unreachable endings "+str({k for k in en if not en[k].get('combined_only')}-set(hit)))

# ---- v4 additive checks (only when v4 fields exist) ----
if any('presentation' in e for e in d['events']) or 'red_flag_anchors' in d:
    from common import CHAT_APP_TYPES,BRAND_BAN,MIN_TIMER_S
    v4n=0
    for e in d['events']:
        if e.get('presentation') not in ('card','chat','notification','timeskip'): err.append(f"{e['id']} bad presentation")
        ch=e.get('chat')
        if e.get('presentation')=='chat' and not ch: err.append(f"{e['id']} chat missing")
        if ch:
            if ch.get('app') not in CHAT_APP_TYPES: err.append(f"{e['id']} chat.app not a generic type")
            blob=json.dumps({k:ch.get(k) for k in ('app_display_name','theme','contact','messages')},ensure_ascii=False)+json.dumps(e.get('interrupts',[]),ensure_ascii=False)
            for b in BRAND_BAN:
                if b in blob: err.append(f"{e['id']} brand name '{b}' in chat")
            ids=[m['id'] for m in ch.get('messages',[])]
            if len(ids)!=len(set(ids)) or not ids: err.append(f"{e['id']} message ids empty/dup")
            for it in e.get('interrupts',[]):
                if it.get('at') not in ids: err.append(f"{e['id']} interrupt at unknown msg")
        pr=e.get('pressure')
        if pr:
            if pr.get('timer_s',0)<MIN_TIMER_S: err.append(f"{e['id']} timer_s<{MIN_TIMER_S}")
            if pr.get('can_disable') is not True: err.append(f"{e['id']} timer not disableable")
        for c in [_m for _c0 in e['choices'] for _p,_m in branches(_c0)]:
            if c.get('grid') not in ('green','yellow','red'): err.append(f"{e['id']} choice grid missing")
        v4n+=1
    if not d['meta'].get('no_pressure_mode',{}).get('available'): err.append("meta.no_pressure_mode missing")
    A=d.get('red_flag_anchors',{})
    for f in RF:
        if f not in A: err.append(f"no anchor for {f}")
    for f,lst in A.items():
        for a in lst:
            e=ev.get(a['event'])
            if not e or a['message'] not in [m['id'] for m in e.get('chat',{}).get('messages',[])]: err.append(f"bad anchor {f}->{a}")
    for x in en.values():
        for k in ('title','title_emoji','grid_color','rarity_key','real_world_stat','share_text','share_card'):
            if k not in x: err.append(f"{x['id']} lacks {k}")
        r=x.get('real_world_stat') or {}
        if r.get('kind')!='share_of_reported_cases': err.append(f"{x['id']} real_world_stat.kind must be share_of_reported_cases")
        if 'rarity' in x: err.append(f"{x['id']} still has legacy 'rarity' field")
        if r.get('value_pct') is None:
            if not r.get('null_reason'): err.append(f"{x['id']} real_world_stat null without reason")
        elif not (r.get('formula') and r.get('source') and r.get('display')): err.append(f"{x['id']} real_world_stat lacks formula/source/display")
    from common import brand_hits
    for h in brand_hits(d): err.append(f"brand in player text: {h}")
    print("v4 checks: events",v4n,"anchors",sum(len(v) for v in A.values()),"ERRORS" if err else "OK")
    if err: print(err[:10]); sys.exit(1)

# ---- v4.1 additive: cross_line_modifiers ----
if 'cross_line_modifiers' in d:
    from common import life_flags,apply_modifiers,CROSS_TYPES
    LF=life_flags(); M=d['cross_line_modifiers']; used=set(); cerr=[]
    for m in M:
        for k in ('id','if_flags','target','effect','note'):
            if k not in m: cerr.append(f"modifier lacks {k}: {m.get('id')}")
        for f in m['if_flags'].get('all',[])+m['if_flags'].get('none',[]):
            if m['effect'].get('type')!='add_interrupt' or any(f in (x['if_flags'].get('all',[])+x['if_flags'].get('none',[])) for x in M if x['effect'].get('type')!='add_interrupt'): used.add(f)  # v1.2：純插話（不改狀態/路徑）的 flag 不展開組合
            if f not in LF: cerr.append(f"{m['id']} flag {f} not defined in script-life.json")
        t=m['target']; ef=m['effect']
        if ef.get('type') not in CROSS_TYPES: cerr.append(f"{m['id']} bad effect type")
        if t['event']!='__INIT__' and t['event'] not in ev: cerr.append(f"{m['id']} target event {t['event']} missing")
        elif t['event']=='__INIT__' and ef.get('type')!='stats_delta': cerr.append(f"{m['id']} __INIT__ only allows stats_delta")
        if 'choice' in t and t['event'] in ev and not (0<=t['choice']<len(ev[t['event']]['choices'])): cerr.append(f"{m['id']} target choice out of range")
        for k in ef.get('stats',{}):
            if k not in ps: cerr.append(f"{m['id']} unknown stat {k}")
        if ef.get('type')=='unlock_choice':
            c=ef['choice']
            if c['next']!='__EVAL__' and c['next'] not in ev: cerr.append(f"{m['id']} unlocked choice next missing")
            for f in c['flags']['set']:
                if f.startswith('missed_') and f not in RF: cerr.append(f"{m['id']} unlock sets {f} w/o red_flag_text")
        if ef.get('type')=='add_interrupt' and ev.get(t['event']) and ef['interrupt'].get('at') not in [x['id'] for x in ev[t['event']].get('chat',{}).get('messages',[])]:
            cerr.append(f"{m['id']} interrupt at unknown msg")
        if ef.get('type')=='rewrite_text' and ef.get('field')=='choice_text' and 'choice' not in t: cerr.append(f"{m['id']} choice_text needs target.choice")
    used=sorted(used); xpaths=0; xhit={}
    if not cerr:
      # v1.2：flag 多時改測「全關／全開／每個單獨開／每個單獨關」（線性），避免 2^n 窮舉卡住
      _B=list(itertools.product([0,1],repeat=len(used))) if len(used)<=4 else ([tuple([0]*len(used)),tuple([1]*len(used))]+[tuple(int(j==i) for j in range(len(used))) for i in range(len(used))]+[tuple(int(j!=i) for j in range(len(used))) for i in range(len(used))])
      for bits in _B:
        LFS=frozenset(f for f,b in zip(used,bits) if b)
        evs,ini=apply_modifiers(d,LFS); E={e['id']:e for e in evs}
        for fam in pi['family_pool'][:1]+pi['family_pool'][-1:]:
          for init in itertools.product(*[ps[k]['init_range'] for k in ps]):
            s0=dict(zip(ps,init)); s0['存款']=clamp('存款',round(s0['存款']*(1+fam.get('存款_mod',0))))
            for k in ps:
                if k!='存款' and k in fam: s0[k]=clamp(k,s0[k]+fam[k])
                s0[k]=clamp(k,s0[k]+ini.get(k,0))
            st=[(pi['start_event'],s0,LFS,0)]
            while st:
                eid,s,f,dep=st.pop(); e=E[eid]
                if dep>100: cerr.append("loop "+eid); break
                s={k:clamp(k,s[k]+e.get('on_enter_effects',{}).get(k,0)) for k in s}
                av=[c for c in [_m for _c0 in e['choices'] for _p,_m in branches(_c0)] if all((r[1:] not in f) if r.startswith('!') else (r in f) for r in c['flags']['require'])]
                if not av: cerr.append(f"dead end {eid} with life flags {sorted(LFS)}"); continue
                for c in av:
                    s2={k:clamp(k,s[k]+c['effects'].get(k,0)) for k in s}; f2=set(f)|set(c['flags']['set'])
                    if c['next']!='__EVAL__': st.append((c['next'],s2,frozenset(f2),dep+1)); continue
                    for sf in R['stat_flags']:
                        if ok({"stats":sf['stats']},f2,s2): f2.add(sf['flag'])
                    xpaths+=1; end=next((x['id'] for x in sorted(en.values(),key=lambda x:x['priority']) if ok(x['conditions'],f2,s2)),R['fallback'])
                    xhit[end]=xhit.get(end,0)+1
    err+=sorted(set(cerr))
    print("cross_line checks: modifiers",len(M),"life flags used",used,"flag-combos",2**len(used),"paths",xpaths,"endings",xhit,"ERRORS" if cerr else "OK")

# ---- v4.3 additive: --sample 模式下，前提窮舉改由上方 v4.3 抽樣檢查負責（避免 5 億條路徑窮舉）----
if '--sample' in sys.argv: pi['family_pool']=[]
# ---- v4.2 additive: ending premises (requires_flags / forbids_flags / text_variants) & stats rule ----
if any('requires_flags' in x or 'forbids_flags' in x for x in en.values()) or d['meta'].get('version','').startswith('0.4'):
    from common import apply_modifiers,pick_text,NO_CATEGORY
    perr=[]
    for x in en.values():
        if 'requires_flags' not in x or 'forbids_flags' not in x: perr.append(f"{x['id']} lacks requires_flags/forbids_flags")
        for v in x.get('text_variants',[]):
            if 'when' not in v or not v.get('text'): perr.append(f"{x['id']} bad text_variant")
    for st_ in d.get('stats',[]):
        if not isinstance(st_.get('self_calculated'),bool): perr.append(f"stat '{st_.get('label')}' self_calculated not bool")
    for x in en.values():
        r=x.get('real_world_stat')
        if r is not None:
            if r.get('value_pct') is None:
                if r.get('display') is not None: perr.append(f"{x['id']} null stat must have display=None (v4.5)")
            elif not isinstance(r.get('display'),str) or not r['display']: perr.append(f"{x['id']} real_world_stat.display null/empty")
    MODS=d.get('cross_line_modifiers',[]); U=sorted({f for m in MODS if m['effect'].get('type')!='add_interrupt' for f in m['if_flags'].get('all',[])+m['if_flags'].get('none',[])})  # v1.2：純插話 flag 不影響路徑/結局，不展開
    pcount={}; pbad=set()
    if not perr:
      _PB=list(itertools.product([0,1],repeat=len(U))) if len(U)<=6 else ([tuple([0]*len(U)),tuple([1]*len(U))]+[tuple(int(j==i) for j in range(len(U))) for i in range(len(U))]+[tuple(int(j!=i) for j in range(len(U))) for i in range(len(U))])  # v1.2：flag 多時線性抽測
      for bits in _PB:
        LFS=frozenset(f for f,b in zip(U,bits) if b)
        evs,ini=apply_modifiers(d,LFS); E={e['id']:e for e in evs}
        for fam in pi['family_pool']:
          for init in itertools.product(*[ps[k]['init_range'] for k in ps]):
            s0=dict(zip(ps,init)); s0['存款']=clamp('存款',round(s0['存款']*(1+fam.get('存款_mod',0))))
            for k in ps:
                if k!='存款' and k in fam: s0[k]=clamp(k,s0[k]+fam[k])
                s0[k]=clamp(k,s0[k]+ini.get(k,0))
            st=[(pi['start_event'],s0,LFS)]
            while st:
                eid,s_,f=st.pop(); e=E[eid]
                s_={k:clamp(k,s_[k]+e.get('on_enter_effects',{}).get(k,0)) for k in s_}
                for c in [_m for _c0 in e['choices'] for _p,_m in branches(_c0)]:
                    if not all((r[1:] not in f) if r.startswith('!') else (r in f) for r in c['flags']['require']): continue
                    s2={k:clamp(k,s_[k]+c['effects'].get(k,0)) for k in s_}; f2=set(f)|set(c['flags']['set'])
                    if c['next']!='__EVAL__': st.append((c['next'],s2,frozenset(f2))); continue
                    for sf in R['stat_flags']:
                        if ok({"stats":sf['stats']},f2,s2): f2.add(sf['flag'])
                    x=next((x for x in sorted(en.values(),key=lambda x:x['priority']) if ok(x['conditions'],f2,s2)),en[R['fallback']])
                    key=x['id']; v=pick_text(x,f2)
                    if v: key+="#"+v['when'].get('label',str(x['text_variants'].index(v)))
                    if not LFS: pcount[key]=pcount.get(key,0)+1
                    for src_ in [x]+([v] if v else []):
                        for q in src_.get('requires_flags',[]):
                            if q not in f2: pbad.add(f"{key} reached without required flag {q} (life flags {sorted(LFS)})")
                        for q in src_.get('forbids_flags',[]):
                            if q in f2: pbad.add(f"{key} reached with forbidden flag {q} (life flags {sorted(LFS)})")
    perr+=sorted(pbad)
    print("premise checks: base paths per ending(+variant)",dict(sorted(pcount.items())),"ERRORS" if perr else "OK")
    if perr: print(perr[:15])
    err+=perr
print(fn,"events",len(ev),"endings",len(en),"paths",paths,"fallback",fallback_hits,"hits",hit)
# ---- v4.5 additive: 人生線 --sample 時跑「完整人生」合併模擬（combined.py；規格 meta.scam_integration）----
if '--sample' in sys.argv and 'scam_integration' in d['meta']:
    import os; sys.path.insert(0,os.path.dirname(os.path.abspath(fn)) or '.')
    import combined; err+=combined.run_checks(20000)
print("ERRORS" if err else "ALL OK",err[:10]); sys.exit(1 if err else 0)
