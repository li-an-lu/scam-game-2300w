"""JS createCombined vs combined.play() 重播比對：用 JS 記錄的初值、plan、選項文字餵給 play()。"""
import json,sys,asyncio
sys.path.insert(0,'/workspace/scam-game'); import combined
from playwright.async_api import async_playwright
JS="""(N)=>{const out=[];const errs=[];const ow=console.warn;console.warn=(...a)=>{errs.push(a.join(' '));};
const sc={};for(const l of manifest.lines)sc[l.id]=scripts[l.id];
for(let n=0;n<N;n++){const b=Engine.rollBirth(manifest.birth);const tr=[];const g=Engine.createCombined(lifeScript,sc,b,{trace:tr});const lp=g.lifePlayer;
const init={...lp.rolled};const tu=lp.tempU;const plan=g.plan.map(p=>[p[0],p[3]]);const seq=[];let s,ends=[];
for(let k=0;k<400;k++){s=g.current();if(s.type==='scam_end'){ends.push([s.ending.id,s.variant]);g.ack();continue}if(s.type==='ending')break;
const i=Math.floor(Math.random()*s.choices.length);g.choose(i);}
out.push({init,tu,halted:!!s.halted,plan,seq:tr,end:s.ending.id,variant:s.variant,stats:lp.stats,flags:[...lp.flags].sort(),hist:lp.scamHistory.map(x=>({line:x.line,ending_id:x.ending_id,entry_age:x.entry_age,exit_age:x.exit_age})),lived:s.ageLived,ends,premise:lp.premise});}
console.warn=ow;return {out,errs};}"""
class FR:
    """開局數字（初值 randint、temperament u、plan offset/hit）依序吐出；之後 choice 依 JS trace，random 依 trace 的 u。"""
    def __init__(s,q,seq): s.q=list(q); s.uq=[]; s.seq=list(seq)
    def randint(s,a,b):
        v=s.q.pop(0); assert a<=v<=b,(a,v,b); return v
    def random(s):
        if s.q: v=s.q.pop(0); return v if not isinstance(v,bool) else (0.0 if v else 1.0)
        return s.uq.pop(0)
    def choice(s,seq):
        x=s.seq.pop(0); s.prev=getattr(s,"cur",None); s.cur=x
        if x['u'] is not None: s.uq.append(x['u'])
        m=[c for c in seq if c['text']==x['t'] and ','.join(c['flags']['set'])==x['f'] and c['next']==x['n']]
        if m: return m[0]
        raise Exception(f"nomatch {x} av={[(c['text'],c['next']) for c in seq]} prev={s.prev}")
CAP={}
_oj=combined.judge
def _j(d,f,s): CAP['s']=dict(s); return _oj(d,f,s)
combined.judge=_j
async def main():
    life=combined.L('web/script-life.json');lines=life['meta']['scam_integration']['lines'];scams={l['line']:combined.L('web/'+l['script']) for l in lines}
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page();jserr=[]
        pg.on('pageerror',lambda e:jserr.append(str(e)))
        await pg.goto('http://localhost:8765/');await pg.wait_for_selector('#go')
        r=await pg.evaluate(JS,int(sys.argv[1]) if len(sys.argv)>1 else 3000)
        await b.close()
    mm=0;E={};H={}
    for x in r['out']:
        err=set();fr=FR([x['init'][k] for k in life['player_init']['stats']]+[x['tu']]+[v for p,h in zip(x['plan'],lines) for v in (p[0]-h['entry_window']['base_age'],p[1])],x['seq']); CAP.clear()
        try: end,hist,lived,f=combined.play(life,scams,fr,err)
        except Exception as e: print('EXC',e);mm+=1;continue
        ph=[{k:h[k] for k in ('line','ending_id','entry_age','exit_age')} for h in hist]
        if end!=x['end'] or ph!=x['hist'] or lived!=x['lived'] or sorted(f)!=x['flags'] or fr.seq or err or (not x['halted'] and any(abs(CAP['s'][k]-x['stats'][k])>1e-6 for k in CAP['s'])):
            mm+=1
            if mm<4: print('MISMATCH',end,x['end'],ph,x['hist'],set(f)^set(x['flags']),err,CAP['s'],x['stats'])
        E[x['end']+'/'+str(x['variant'])]=E.get(x['end']+'/'+str(x['variant']),0)+1
        for h in x['hist']:H[h['line']+':'+h['ending_id']]=H.get(h['line']+':'+h['ending_id'],0)+1
    print('runs',len(r['out']),'mismatch',mm,'premise warns',set(r['errs']),'jserr',jserr)
    print('life endings',dict(sorted(E.items())));print('scam endings',dict(sorted(H.items())))
asyncio.run(main())
