from playwright.sync_api import sync_playwright
import time
O='/workspace/scam-game/shots-v7/'; errs=[]; seen=set(); kinds=[]
with sync_playwright() as p:
    try: b=p.chromium.launch()
    except Exception: b=p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg=b.new_page(viewport={'width':430,'height':900},device_scale_factor=2)
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:m.type=='error' and errs.append(m.text))
    pg.goto('http://127.0.0.1:18433/index.html?np=1'); pg.wait_for_selector('#go'); time.sleep(2)
    pg.screenshot(path=O+'start.png',full_page=True)
    pg.click('#go')
    for i in range(600):
        time.sleep(0.25)
        if pg.query_selector('#again'): break
        k=pg.query_selector('[data-stage-kind]')
        if k:
            kd=k.get_attribute('data-stage-kind'); kinds.append(kd)
            if kd not in seen: seen.add(kd); pg.screenshot(path=O+f'event-{kd}.png',full_page=True)
        elif 'life' not in seen and pg.query_selector('.choice'):
            seen.add('life'); pg.screenshot(path=O+'event-life.png',full_page=True)
        for sel in ['#beat-go','[data-si]','button.choice:not([disabled])','.choices button:not([disabled])','#next','button.primary:not([disabled])']:
            el=pg.query_selector(sel)
            if el and el.is_visible():
                try: el.click(timeout=2000)
                except Exception: pass
                break
    time.sleep(1.5)
    pg.screenshot(path=O+'ending.png',full_page=True)
    le=pg.query_selector('#lie-end')
    if le: le.screenshot(path=O+'ending-lie-review.png')
    print('ended',bool(pg.query_selector('#again')),'lieCard',le and le.get_attribute('data-card'))
    print('quotes',[q.inner_text() for q in pg.query_selector_all('#lie-end .quote')])
    print('kinds',kinds.count('lie'),'lie',kinds.count('pos'),'pos',set(kinds))
    print('errors',errs[:10])
    b.close()
