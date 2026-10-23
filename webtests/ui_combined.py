"""合併模式 UI 走查：結果卡、詐騙線結局、最終結局 recap、分享卡、320px 溢出、JS 錯誤。"""
import asyncio,sys,random
from playwright.async_api import async_playwright
OV=[];HELP=[];EM=[];SH=[]
OUT='/workspace/scam-game/web/screens/'
async def play(b,w,h,tag,forceplan=None,shots=True):
    pg=await b.new_page(viewport={'width':w,'height':h});errs=[];warns=[]
    pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:m.type in('error','warning') and warns.append(m.text))
    await pg.goto('http://localhost:8888/?fast=1&nopressure=1&track=1');await pg.wait_for_selector('#go')
    if forceplan: await pg.evaluate("p=>{const o=Engine.createCombined;Engine.createCombined=(l,s,b,op={})=>{const g=o(l,s,b,op);g.plan.forEach((x,i)=>{x[0]=p[i];x[3]=true});return g}}",forceplan)
    await pg.click('#go');res=0;over=0;n=0;res_ok=0
    for step in range(500):
        await pg.wait_for_timeout(60)
        st=await pg.evaluate("""()=>({r:!!document.querySelector('#r-go'),se:!!document.querySelector('#scam-end'),end:!!document.querySelector('#ending'),
          em:[...document.querySelectorAll('button.choice,#result')].map(e=>e.innerText).filter(t=>/\p{Extended_Pictographic}/u.test(t)).slice(0,2),ch:[...document.querySelectorAll('button[data-i]:not([disabled])')].length,ov:document.documentElement.scrollWidth>innerWidth,ovel:[...document.querySelectorAll('body *')].filter(e=>e.getBoundingClientRect().right>innerWidth+1).slice(0,3).map(e=>e.tagName+'.'+e.className+':'+(e.textContent||'').slice(0,20))})""")
        over+=st['ov']
        if st['em'] and len(EM)<5: EM.append(st['em'])
        if st['ov'] and len(OV)<5: OV.append(st['ovel'])
        if st['end']:
            await pg.wait_for_timeout(1500)
            if shots: await pg.screenshot(path=OUT+f'v13_{tag}_ending.png',full_page=True)
            info=await pg.evaluate("()=>{const e=document.querySelector('#ending');return {id:e.dataset.id+'/'+e.dataset.variant,recap:document.querySelector('#recap')?.innerText||'',hist:G.lifePlayer.scamHistory.map(x=>x.line+':'+x.ending_id+'@'+x.entry_age),share:shareText(G.current().ending,G.lifeGrid(G.current().ending))}}")
            if shots: await (await pg.query_selector('#cv')).screenshot(path=OUT+f'v13_{tag}_share.png')
            await pg.context.grant_permissions(['clipboard-read','clipboard-write']); await pg.click('#sh'); await pg.wait_for_timeout(300)
            SH.append(await pg.evaluate("()=>[document.querySelector('.toast')?.textContent, navigator.clipboard.readText()]"))
            await pg.close(); return info,errs,warns,res,res_ok,over
        if st['se'] or st['end']:
            h=await pg.evaluate("()=>[[...document.querySelectorAll('a[href^=\"tel:\"]')].map(a=>a.getAttribute('href')).join(',')+(document.querySelector('#help')?'+HELP':''), [...document.querySelectorAll('a.btn')].filter(a=>a.textContent.includes('閱讀原文')).length]")
            HELP.append(h)
        if st['se']:
            if shots: await pg.screenshot(path=OUT+f'v13_{tag}_scamend{n}.png',full_page=True)
            n+=1; await pg.click('#cont');continue
        if st['r']:
            res+=1
            await pg.wait_for_timeout(800)
            t=await pg.evaluate("()=>[...document.querySelectorAll('.r-d')].map(x=>x.textContent)")
            if all(any(ch.isdigit() for ch in x) for x in t): res_ok+=1
            if shots and res in (3,25,45): await pg.screenshot(path=OUT+f'v13_{tag}_result{res}.png')
            await pg.click('#r-go');continue
        if st['ch']:
            bs=await pg.query_selector_all('button[data-i]:not([disabled])')
            bt=random.choice(bs)
            try: await bt.click(timeout=3000)
            except Exception: await bt.click(force=True)
            await pg.wait_for_timeout(700); continue
    await pg.screenshot(path=OUT+f'v13_{tag}_STUCK.png'); await pg.close(); return 'STUCK',errs,warns,res,res_ok,over
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for tag,w,h,fp in [('c390',390,844,[19,23,37,27,31,43]),('c320',320,640,[21,26,35,28,33,42])]:
            r=await play(b,w,h,tag,fp); print(tag,r[0]['id'] if r[0]!='STUCK' else r[0],'errs',r[1],'overflow',r[5],flush=True)
        for i in range(int(sys.argv[1]) if len(sys.argv)>1 else 4):
            r=await play(b,390,844,'r',None,False); print('rand',r[0] if r[0]=='STUCK' else (r[0]['id'],r[0]['hist']),r[1],set(r[2]),'results',r[3],'withnums',r[4],'overflow',r[5],flush=True)
asyncio.run(main())
print('OVERFLOW samples',OV);print('EMOJI in play',EM);print('SHARE',[(a,(b or '')[-40:]) for a,b in SH]);print('tel sets',HELP and [h[0] for h in HELP],len(HELP),'readorig counts',[h[1] for h in HELP])
