import asyncio
from playwright.async_api import async_playwright
OUT='/workspace/scam-game/web/screens/'
async def run(b,w,h):
    pg=await b.new_page(viewport={'width':w,'height':h});errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('http://localhost:8765/?fast=1&nopressure=1');await pg.wait_for_selector('#go');await pg.click('#go')
    for i in range(60):
        await pg.wait_for_timeout(300)
        if await pg.query_selector('#ending'): break
        if await pg.query_selector('#r-go'): await pg.click('#r-go');continue
        bs=await pg.query_selector_all('button[data-i]:not([disabled])')
        if bs:
            await pg.evaluate("()=>{G.lifePlayer.stats['心理']=-50}")
            try: await bs[0].click(timeout=3000)
            except Exception: await bs[0].click(force=True)
    await pg.wait_for_timeout(1200)
    info=await pg.evaluate("()=>({id:document.querySelector('#ending')?.dataset.id,order:[...document.querySelectorAll('#screen > *')].map(e=>e.id||(e.querySelector('h3,h2')?.textContent||e.textContent).slice(0,10)),tels:[...document.querySelectorAll('a[href^=tel]')].map(a=>a.getAttribute('href')),titles:document.querySelectorAll('#screen .e-title,#screen .t-emoji').length,has1995:document.body.innerText.includes('1995'),destig:document.querySelector('.destig')?.textContent,srcs:[...document.querySelectorAll('.card')].find(c=>c.textContent.startsWith('資料來源'))?.innerText||'NONE',cc:[...document.querySelectorAll('.card')].find(c=>c.textContent.includes('真實案件卡'))?.innerText,ach:document.querySelector('.ach-new')?.innerText||'',ov:document.documentElement.scrollWidth>innerWidth})")
    await pg.screenshot(path=OUT+(f'v14_halt{w}.png'),full_page=True)
    await pg.locator('#author').screenshot(path=OUT+f'v14_author{w}.png'); print('author form',await pg.locator('#contact-form textarea[required]').count())
    await pg.click('#again');await pg.wait_for_selector('#ach');t=await pg.inner_text('#ach');await pg.click('#ach');await pg.wait_for_timeout(300)
    ov2=await pg.evaluate("()=>document.documentElement.scrollWidth>innerWidth")
    await pg.screenshot(path=OUT+f'v14_ach{w}.png',full_page=False)
    print(w,info,'btn',t,'achview_overflow',ov2,'errs',errs)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for w,h in [(390,844),(320,640)]: await run(b,w,h)
asyncio.run(main())
