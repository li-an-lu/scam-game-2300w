import asyncio
from playwright.async_api import async_playwright
async def m():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (390,320):
      pg=await b.new_page(viewport={'width':w,'height':800});errs=[]
      pg.on('pageerror',lambda e:errs.append(str(e)+' '+(e.stack or '')[:300]));pg.on('console',lambda c:c.type=='error' and errs.append(c.text))
      await pg.goto('http://localhost:8765/');await pg.evaluate("localStorage.setItem('lives','[{\"end\":\"x\",\"t\":1}]')");await pg.reload();await pg.wait_for_selector('#go')
      t=await pg.inner_text('#screen');ov=await pg.evaluate('document.documentElement.scrollWidth>innerWidth')
      print(w,'skip' in await pg.content() and await pg.locator('#skipseen').count(),'人生線已啟用' in t,'假交友' in t,await pg.locator('#intro-fact').inner_text(),await pg.locator('#intro-fact a').get_attribute('href'),'ov',ov)
      if w==390: await pg.screenshot(path='web/screens/v13_start.png',full_page=True)
      await pg.check('#skipseen')
      seen=0
      for rnd in range(2):
        await pg.click('#go') if rnd==0 else None
        for i in range(25):
          await pg.wait_for_timeout(250)
          seen+=await pg.locator('details.seen').count()
          if await pg.locator('details.seen').count() and seen==1:
            await pg.click('details.seen summary');print(' expand ok',await pg.locator('details.seen[open]').count())
          bt=pg.locator('#screen button[data-i], #r-go, #screen .chat button, #screen button.primary')
          if await bt.count(): await bt.first.click()
        if rnd==0:
          await pg.evaluate("localStorage.setItem('seenEvents',JSON.stringify(JSON.parse(localStorage.getItem('seenEvents'))))");
          n=await pg.evaluate("JSON.parse(localStorage.getItem('seenEvents')).length");print(' seen stored',n)
          await pg.evaluate('start()');await pg.click('#go')
      print(' collapsed shown',seen,'ov',await pg.evaluate('document.documentElement.scrollWidth>innerWidth'),'errs',errs)
asyncio.run(m())
