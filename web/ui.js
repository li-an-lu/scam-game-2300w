const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const money = n => Math.round(n).toLocaleString('zh-TW') + ' 元';
const Q = new URLSearchParams(location.search);
const sleep = ms => new Promise(r => setTimeout(r, ms));
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const SPEED = Q.get('fast') ? 0.05 : REDUCED ? 0.4 : 1;          // ?fast=1 測試用：聊天訊息加速
const CHOICE_PAUSE_MS = 600;                                       // 選擇後停 0.6 秒才揭露後果
const MIN_TIMER_S = 25;                                            // 倒數下限（不論 JSON 寫多少）
const ICON = { 存款: '💰', 警覺: '👁', 人際: '🤝', 心理: '🫀' };
const icon = k => ICON[k] || k[0];
// v8：0–10 顯示。有 max 的數值（警覺／人際／心理）換算成 0–10；display_max 可在 player_init.stats 覆寫
const statTop = k => { const d = script?.player_init?.stats?.[k] || lifeScript?.player_init?.stats?.[k] || {}; return d.max != null ? d.max : null; };
const dispMax = k => (script?.player_init?.stats?.[k] || lifeScript?.player_init?.stats?.[k] || {}).display_max ?? 10;
const disp = (k, v) => { const t = statTop(k); return t ? Math.round(v / t * dispMax(k)) : v; };
const dispD = (k, v) => { const t = statTop(k); if (!t || !v) return v; const r = Math.round(v / t * dispMax(k)); return r || Math.sign(v); };
const noEmoji = t => String(t ?? '').replace(/[\p{Extended_Pictographic}\u{1F1E6}-\u{1F1FF}][\u{FE0F}\u{200D}\p{Extended_Pictographic}]*/gu, '').replace(/^\s+/, '');
const HOTLINES = [{ tel: '165', label: '📞 165 反詐騙專線' }, { tel: '1925', label: '💬 1925 安心專線（24 小時）' }];
// 虛構 App 外觀（只用自訂配色，不用任何真實 App 的品牌色或 logo）
const APPS = {
  line_like: { cls: 'app-chatto', name: '聊聊 Chatto' }, dating_like: { cls: 'app-spark', name: '心動 Spark' },
  shop_like: { cls: 'app-paipai', name: '拍拍集' }, sms_like: { cls: 'app-feed', name: '社群動態' },
  phone_call: { cls: 'app-call', name: '來電' }, in_person: { cls: 'app-scene', name: '現場' } };
const FALLBACK_FILLER = ['平凡地過了一年。'];
let G, script, lastAge = 0, manifest, scripts = {}, lifeScript = null, timer = null, birth = null;
const fillerPool = () => script?.year_filler || script?.meta?.year_filler || manifest?.year_filler || FALLBACK_FILLER;
const verifiedOk = s => s.source && s.verified === true;
const statLine = s => {
  const v = s.display ?? `${typeof s.value === 'number' ? s.value.toLocaleString() : s.value} ${s.unit || ''}`;
  return `${esc(s.label)}：<b>${esc(v)}</b>${s.period ? `<span class="tag">${esc(s.period)}</span>` : ''}${s.self_calculated ? '<span class="tag calc">自行換算</span>' : ''} <a href="${esc(s.source)}" target="_blank" rel="noopener">來源</a>${note(s)}`;
};
const note = s => s.verify_note ? `<span class="src">（${esc(s.verify_note)}）</span>` : '';
const allStats = () => Object.values(scripts).flatMap(x => x.stats || []).filter(s => verifiedOk(s) && !('display' in s && (s.display == null || s.display === false)));
// 無壓力模式：localStorage > ?nopressure > meta.no_pressure_mode.default
const noPressure = () => Q.get('nopressure') === '1' || (localStorage.getItem('noPressure') ?? String(!!script?.meta?.no_pressure_mode?.default)) === 'true';
// 除錯：?flags=a,b 直接注入人生線 flag
const debugFlags = () => (Q.get('flags') || '').split(',').map(s => s.trim()).filter(Boolean);

// 匿名統計：只送事件種類＋本機隨機 ID＋本機第幾局；不收 IP／指紋。任何錯誤都吞掉，不影響遊戲
function track(e) {
  try {
    if (/^(localhost|127\.)/.test(location.hostname) && !Q.get('track')) return;
    let id = localStorage.getItem('anonId');
    if (!id) { id = Array.from(crypto.getRandomValues(new Uint8Array(12)), b => b.toString(16).padStart(2, '0')).join(''); localStorage.setItem('anonId', id); }
    let n = +localStorage.getItem('gamesStarted') || 0;
    if (e === 'start') localStorage.setItem('gamesStarted', ++n);
    const body = JSON.stringify({ e, id, n });
    if (navigator.sendBeacon) navigator.sendBeacon('/api/track', new Blob([body], { type: 'application/json' }));
    else fetch('/api/track', { method: 'POST', body, keepalive: true }).catch(() => {});
  } catch (_) {}
}
function toast(t) { const d = document.createElement('div'); d.className = 'toast'; d.textContent = t; document.body.append(d); setTimeout(() => d.remove(), 1800); }
function srcHtml(sources = []) {
  return sources.map(s => {
    const label = s.name || (s.story_id != null ? `案例 #${s.story_id}` : '來源') + (s.url ? `（${new URL(s.url).hostname}）` : '');
    return s.url ? `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(label)}</a>` : esc(label);
  }).join('、');
}
// Reigns 式量表：圖示＋由下往上填滿；變動時閃爍
function statHtml(delta = {}) {
  const p = G.player, def = script.player_init.stats;
  $('#h-age').textContent = p.age + ' 歲';
  $('#h-bio').textContent = `${p.county}・${p.family}家庭`;
  $('#h-stats').innerHTML = Object.keys(p.stats).map(k => {
    const v = p.stats[k], d = def[k] || {};
    const top = d.max ?? d.bar_max ?? d.init_range?.[1] ?? 1e6;
    const w = Math.max(0, Math.min(100, v / top * 100));
    const fx = delta[k] ? (delta[k] > 0 ? ' flash-up' : ' flash-down') : '';
    const sub = d.max ? '' : `<small>${money(v)}${p.debt ? `<br><span class="down">負債 ${money(p.debt)}</span>` : ''}</small>`;
    const num = d.max ? `<small class="g-num">${disp(k, v)} / ${dispMax(k)}</small>` : '';
    return `<div class="gauge${fx}" title="${esc(k)}"><div class="g-ring"><i style="height:${w}%"></i><span>${icon(k)}</span></div><em>${esc(k)}</em>${sub}${num}</div>`;
  }).join('');
}
function deltaHtml(d) {
  if (!d || !Object.keys(d).length) return '';
  return '<div class="delta">' + Object.entries(d).map(([k, v]) => {
    const good = k === '負債' ? v < 0 : v > 0;
    return `<span class="${good ? 'up' : 'down'}">${icon(k)} ${esc(k)} ${v > 0 ? '▲' : '▼'} ${k === '存款' || k === '負債' ? wan(Math.abs(v)) : Math.abs(dispD(k, v))}</span>`;
  }).join('　') + '</div>';
}
// 選項：只顯示會影響哪些數值（圖示），不顯示數字
function choiceHtml(c, i) {
  const ks = Object.entries(c.effects || {}).filter(([, v]) => v).map(([k]) => k);
  return `<button data-i="${i}" class="choice">${c.cross_line ? '<span class="tag unlock">人生經驗解鎖</span>' : ''}${esc(noEmoji(c.text))}</button>`;
}
// 成就（achievements.json）：存在 localStorage『ach』；run＝這一局內達成，collection＝跨局累積
let ACH = null, STAGE_POOL = null;
const achStore = () => { let s = {}; try { s = JSON.parse(localStorage.getItem('ach') || '{}'); } catch (_) {} s.endings ||= []; s.flags ||= []; s.choices ||= []; s.got ||= {}; return s; };
const achCount = () => { const g = achStore().got; return ACH.filter(a => g[a.id]).length; };
function achRecord(en, ses = {}) {
  if (!ACH) return [];
  const lp = G.lifePlayer || G.player, l0 = G.combined ? 'life' : (document.body.dataset.line || 'life');
  const R = { endings: new Set([`${l0}:${en.id}`]), flags: new Set(), choices: new Set() };
  if (ses.lieCard) R.endings.add(`life:${ses.lieCard}`);   // v7 謊言回顧卡
  const addC = (line, id, idx, text) => { R.choices.add(`${line}|${id}|#${idx}`); R.choices.add(`${line}|${id}|${text}`); };
  for (const f of lp.flags) R.flags.add(`${l0}:${f}`);
  for (const h of lp.history) addC(l0, h.id, h.idx, h.choice);
  for (const x of lp.scamHistory || []) {
    R.endings.add(`${x.line}:${x.ending_id}`);
    for (const f of x.internal_flags || []) R.flags.add(`${x.line}:${f}`);
    for (const [id, idx, t] of x.choices || []) addC(x.line, id, idx, t);
  }
  const st = achStore();
  const A = { endings: new Set([...st.endings, ...R.endings]), flags: new Set([...st.flags, ...R.flags]), choices: new Set([...st.choices, ...R.choices]) };
  const fresh = [];
  for (const a of ACH) {
    if (st.got[a.id]) continue;
    const u = { requires_endings: [], requires_any_endings: [], requires_flags: [], requires_choices: [], forbids_flags: [], forbids_endings: [], ...a.unlock }, S = u.scope === 'collection' ? A : R;
    const fm = u.requires_flags_min, anyN = u.min_count ? u.requires_any_endings.filter(e => S.endings.has(e)).length >= u.min_count : true;
    const ok = anyN && (!fm || fm.flags.filter(f => S.flags.has(f)).length >= fm.n) && u.requires_endings.every(e => S.endings.has(e)) && (!u.requires_any_endings.length || u.requires_any_endings.some(e => S.endings.has(e)))
      && u.requires_flags.every(f => S.flags.has(f)) && !u.forbids_flags.some(f => S.flags.has(f)) && !u.forbids_endings.some(e => S.endings.has(e))
      && u.requires_choices.every(c => S.choices.has(`${c.line}|${c.event}|#${c.choice_index}`) || S.choices.has(`${c.line}|${c.event}|${c.text}`));
    // 年齡門檻：unlock.min_age_lived；沒有欄位時從描述「活到 N 歲」推（achievements.json 本身沒有年齡條件）
    const minAge = u.min_age_lived ?? +((a.description.match(/^活到 ?(\d+) ?歲/) || [])[1] || 0);
    if (ok && (ses.ageLived ?? G.player.age ?? 0) >= minAge) { st.got[a.id] = Date.now(); fresh.push(a); }
  }
  st.endings = [...A.endings]; st.flags = [...A.flags]; st.choices = [...A.choices];
  try { localStorage.setItem('ach', JSON.stringify(st)); } catch (_) {}
  return fresh;
}
function achNewHtml(list) {
  return list.length ? `<div class="card act ach-new"><h3>新成就（${list.length}）</h3><ul class="flags">${list.map(a => `<li><b>${esc(a.name)}</b>：${esc(a.description)}</li>`).join('')}</ul></div>` : '';
}
const ACH_CAT = { life: '人生', red_flag: '看出破綻', ending_codex: '結局圖鑑' };
function showAchievements() {
  const got = achStore().got, cats = [...new Set(ACH.map(a => a.category))];
  $('#screen').innerHTML = `<h2>成就 ${achCount()} / ${ACH.length}</h2>
  ${cats.map(c => `<div class="card ach-list"><h3>${esc(ACH_CAT[c] || c)}</h3><ul>${ACH.filter(a => a.category === c).map(a => got[a.id]
    ? `<li class="ach-got"><b>${esc(a.name)}</b><br><span class="src">${esc(a.description)}</span></li>`
    : `<li class="ach-lock"><b>${a.hidden ? '？？？' : esc(a.name)}</b><br><span class="src">${a.hidden ? '尚未解鎖' : esc(a.description)}</span></li>`).join('')}</ul></div>`).join('')}
  <button id="ach-back">返回</button>`;
  $('#ach-back').onclick = start; window.scrollTo(0, 0);
}
// 開始頁的一句事實：之後在這裡填入（可含 HTML 來源連結）；空字串＝隱藏 #intro-fact
const INTRO_FACT = '2026年9月，台灣平均每天約359件詐騙案，一天被騙走1.3億元。<br><small><a href="https://165dashboard.tw" target="_blank" rel="noopener">資料：165打詐儀表板，2026年9月</a></small>';
// 跳過已看過的劇情：seenEvents 存在 localStorage；只摺疊文字，選擇照常（不碰 RNG）
const seenStore = () => { try { return new Set(JSON.parse(localStorage.getItem('seenEvents') || '[]')); } catch (_) { return new Set(); } };
const skipSeen = () => localStorage.getItem('skipSeen') === 'true';
function markSeen(id) { if (!id) return; const st = seenStore(); if (st.has(id)) return; st.add(id); try { localStorage.setItem('seenEvents', JSON.stringify([...st])); } catch (_) {} }
function textHtml(e, txt, seen) {
  if (!seen) return `<div class="text">${esc(txt)}</div>`;
  const one = txt.replace(/\s+/g, ' ');
  return `<details class="seen"><summary><span class="seen-tag">已看過</span> ${esc(one.length > 22 ? one.slice(0, 22) + '…' : one)}</summary><div class="text">${esc(txt)}</div></details>`;
}
// v7 開始頁：依 leo-design/start-page.html（動態數字、事實輪播、警語、四數值、分享經驗輪播、暗金／酒紅基調）
const FACTS = [   // 第一則已查證（165 打詐儀表板）；其餘為寫手提供，待查證
  { t: '2026年9月，台灣平均每天約359件詐騙案，一天被騙走1.3億元。', src: 'https://165dashboard.tw', note: '165打詐儀表板，2026年9月' },
  { t: '多數人一天說 0～2 個謊，其中約 90% 是無傷大雅的小謊。' }, { t: '10 分鐘的日常對話裡，約 60% 的成年人會至少說一次謊。' },
  { t: '超過 95% 的民眾曾收過假訊息，投資理財類最常出現。' }, { t: '孩子大約 2～3 歲就會開始有意識地說第一個謊。' },
  { t: '履歷裡約有 30～40% 含有不同程度的誇大。' }, { t: '假投資詐騙雖然件數不一定最多，但財損金額往往最高。' }];
const factHtml = f => `${esc(f.t)}${f.src ? ` <small><a href="${esc(f.src)}" target="_blank" rel="noopener">${esc(f.note)}</a></small>` : ' <small>（寫手提供，待查證）</small>'}`;
const DEMO_EXP = [   // 示範短句（非真實投稿）；之後由審核清單取代
  { tag: '受騙', quote: '「對方說再轉一次就解凍。我真的轉了。」', who: '高雄 · 45 歲' }, { tag: '有驚無險', quote: '「差點匯出去，後來打給家人確認才停手。」', who: '台中 · 32 歲' },
  { tag: '風平浪靜', quote: '「這一生沒遇過什麼大事。薪水不多，但每個月都過得去。」', who: '台南 · 58 歲' }, { tag: '懊悔', quote: '「我一直覺得自己不會上當。結果還是轉了。」', who: '台北 · 29 歲' },
  { tag: '受騙', quote: '「他每天跟我說早安。三個月後，我把積蓄都給了他。」', who: '新北 · 51 歲' }, { tag: '有驚無險', quote: '「網拍賣家一直催我私下交易。我沒理他，後來他消失了。」', who: '桃園 · 27 歲' },
  { tag: '風平浪靜', quote: '「沒有人騙過我，也沒有人特別幫過我。這樣也好。」', who: '彰化 · 64 歲' }, { tag: '懊悔', quote: '「我媽叫我不要點那個連結。我還是點了。」', who: '台中 · 23 歲' },
  { tag: '受騙', quote: '「投資群組裡每個人都在曬獲利。我進去的隔天，群組就不見了。」', who: '高雄 · 38 歲' }, { tag: '有驚無險', quote: '「假警察打來時，我掛掉後打給真正的派出所。他們說沒這回事。」', who: '台北 · 41 歲' }];
// 分享短句暫行方案：玩家留言存 localStorage.sharedPending；輪播只顯示 localStorage.sharedApproved（手動匯入審核後的 JSON）
const lsJ = (k, d) => { try { return JSON.parse(localStorage.getItem(k) || '') ?? d; } catch (_) { return d; } };
const approvedExp = () => { const a = lsJ('sharedApproved', []); return Array.isArray(a) && a.length ? a.filter(x => x && x.quote && x.approved !== false) : DEMO_EXP; };
let startTimers = [];
function start() {
  startTimers.forEach(clearInterval); startTimers = [];
  if ($('#log').parentElement !== $('#app')) $('#app').append($('#log'));
  closePhone(); $('#hud').hidden = true; $('#log').hidden = true;
  const prev = JSON.parse(localStorage.getItem('lives') || '[]');
  const dbg = debugFlags(), EXP = approvedExp(), demo = EXP === DEMO_EXP;
  const title = lifeScript?.meta?.title || manifest?.title || '2300萬分之1';
  const tm = title.match(/^(.*萬)分之(\d+)$/);
  $('#screen').innerHTML = `<div class="start-v7">
  <div class="meta">台灣人生模擬 · 取材自真實資料</div>
  <div class="start-hero"><h1>${tm ? `${esc(tm[1])}<span class="of">分之</span><span class="one">${esc(tm[2])}</span>` : esc(title)}</h1>
    <p class="sub">你是其中一個。<br>大多數謊言很小，但有些會變成轉機。</p></div>
  <div class="live-row">
    <div class="live-card"><div class="num" id="live-lies">0</div><div class="lbl">打開這個頁面後<br>被說出的小謊<small>示意動畫，非實際統計</small></div></div>
    <div class="live-card"><div class="num" id="live-cases">0</div><div class="lbl">今天到現在全台約受理<br>的詐騙案件<small>依每天約359件換算（165打詐儀表板，2026年9月）</small></div></div>
  </div>
  <div class="fact-ticker" id="fact-ticker">${factHtml(FACTS[0])}</div>
  <p class="desc">一出生，四個數值就已經決定。接下來你會遇到家人、同學、同事說的話，也會遇到<strong>看起來很真</strong>的訊息與機會。遊戲裡的事件取材自 165 統計與真實經驗。<br><b>人生只有一次，選了就不能重來。</b></p>
  <div class="card main-card">
    <div class="stat-row">${['存款', '警覺', '人際', '心理'].map(k => `<div class="stat"><span>${k}</span><b>隨機</b></div>`).join('')}</div>
    ${prev.length ? `<p class="src">你已經活過 ${prev.length} 次人生。</p>` : ''}
    <label class="np"><input type="checkbox" id="np" ${noPressure() ? 'checked' : ''}> 無壓力模式（關閉所有倒數）</label>
    ${prev.length ? `<label class="np"><input type="checkbox" id="skipseen" ${skipSeen() ? 'checked' : ''}> 跳過已看過的劇情</label>` : ''}
    ${dbg.length ? `<p class="debug">🧪 除錯 flags：${esc(dbg.join(', '))}</p>` : ''}
    <button class="primary" id="go">開始這一生 →</button>
    ${ACH ? `<button class="ghost" id="ach">成就 ${achCount()} / ${ACH.length}</button>` : ''}</div>
  <p class="footer">上當的人不笨，往往只是太真誠。</p>
  <div class="shared-section"><h2>他們分享的經驗</h2><p class="sub">走完一生的人，留下一句話。沒有名字，只有當時的感覺。</p>
    <div class="carousel" id="exp-carousel"></div>
    <div class="nav-row"><button id="exp-prev">←</button><div class="dots" id="exp-dots"></div><button id="exp-next">→</button></div>
    <div class="shared-note"><strong>備註：</strong>${demo ? '目前為預設示範短句（非真實投稿），一次顯示 3 則並輪播。' : '以下為審核通過的玩家短句。'}玩家在結局時可留下「一句想說的話」，經審核後才會出現在這裡。
      <details><summary>審核清單匯入（管理用）</summary><p class="src">貼上 JSON 陣列：[{"tag":"有驚無險","quote":"「…」","who":"台中 · 32 歲"}]</p>
      <textarea id="exp-json" rows="3" style="width:100%"></textarea><button id="exp-import">匯入審核清單</button><button id="exp-export">匯出待審短句</button></details></div></div>
  </div>`;
  if (ACH) $('#ach').onclick = showAchievements;
  $('#skipseen') && ($('#skipseen').onchange = e => localStorage.setItem('skipSeen', String(e.target.checked)));
  $('#np').onchange = e => localStorage.setItem('noPressure', String(e.target.checked));
  // 動態數字
  let lies = 0; const casesNow = () => { const d = new Date(), f = (d.getHours() * 3600 + d.getMinutes() * 60 + d.getSeconds()) / 86400; return Math.floor(359 * f); };
  $('#live-cases').textContent = casesNow().toLocaleString();
  startTimers.push(setInterval(() => { lies += Math.random() > 0.4 ? 1 : 2; const el = $('#live-lies'); if (el) el.textContent = lies.toLocaleString(); }, 1600));
  startTimers.push(setInterval(() => { const el = $('#live-cases'); if (el) el.textContent = casesNow().toLocaleString(); }, 3200));
  let fi = 0; startTimers.push(setInterval(() => { const el = $('#fact-ticker'); if (!el) return; fi = (fi + 1) % FACTS.length; el.style.opacity = 0; setTimeout(() => { el.innerHTML = factHtml(FACTS[fi]); el.style.opacity = 1; }, 280); }, 4200));
  // 經驗輪播
  let page = 0; const per = 3, pages = Math.max(1, Math.ceil(EXP.length / per));
  const draw = () => { $('#exp-carousel').innerHTML = EXP.slice(page * per, page * per + per).map(e => `<div class="exp-card"><div class="tag">${esc(e.tag)}</div><p class="quote">${esc(e.quote)}</p><div class="who">${esc(e.who || '')}</div></div>`).join('');
    $('#exp-dots').innerHTML = Array.from({ length: pages }, (_, i) => `<span class="${i === page ? 'on' : ''}"></span>`).join(''); };
  $('#exp-next').onclick = () => { page = (page + 1) % pages; draw(); }; $('#exp-prev').onclick = () => { page = (page - 1 + pages) % pages; draw(); };
  draw(); startTimers.push(setInterval(() => { if ($('#exp-carousel')) { page = (page + 1) % pages; draw(); } }, 7000));
  $('#exp-import').onclick = () => { try { const a = JSON.parse($('#exp-json').value); if (!Array.isArray(a)) throw 0; localStorage.setItem('sharedApproved', JSON.stringify(a.filter(x => x && x.quote).map(x => ({ tag: String(x.tag || ''), quote: String(x.quote).slice(0, 60), who: String(x.who || '') })))); toast('已匯入審核清單'); start(); } catch (_) { toast('JSON 格式不正確'); } };
  $('#exp-export').onclick = () => { $('#exp-json').value = JSON.stringify(lsJ('sharedPending', []), null, 1); toast('待審短句已放入文字框'); };
  $('#go').onclick = () => {
    startTimers.forEach(clearInterval); startTimers = [];
    track('start');
    birth = Engine.rollBirth(manifest.birth); $('#log-list').innerHTML = '';
    if (lifeScript && !dbg.length && !Q.get('line')) return beginCombined();
    beginScam(dbg);
  };
}
function beginScam(flags) {
  const entries = Object.fromEntries(manifest.lines.map(l => [l.id, scripts[l.id]?.entry]).filter(([, e]) => e));
  const line = manifest.lines.find(l => l.id === Q.get('line')) || Engine.assignLine(manifest.lines, birth, entries);
  beginLine(scripts[line.id], line.id, flags);
}
function beginLine(sc, id, flags) {
  script = sc; document.body.dataset.line = id;
  G = Engine.create(script, birth, { flags }); lastAge = 0;
  $('#hud').hidden = false; $('#log').hidden = false; render();
}
// 合併模式（預設）：人生線為主幹，詐騙線在 19／27／37 歲插入（engine.createCombined，移植 combined.py）
function beginCombined() {
  G = Engine.createCombined(lifeScript, scripts, birth); script = lifeScript; lastAge = 0;
  if (STAGE_POOL && Q.get('stage') !== '0') G = Stage.wrap(G, STAGE_POOL);   // v7 階段抽池
  document.body.dataset.line = 'life';
  $('#hud').hidden = false; $('#log').hidden = false; render();
}
function render(delta) {
  stopTimer();
  const s = G.current();
  if (G.combined) { script = s.type === 'scam_end' ? s.scamScript : G.script; document.body.dataset.line = s.line || 'life'; }
  if (s.type === 'scam_end') return scamEnd(s);
  if (s.type === 'beat' || s.type === 'pos') return stageCard(s, delta);
  const d = { ...(delta || {}) }; for (const [k, v] of Object.entries(s.enterDelta || {})) d[k] = (d[k] || 0) + v;
  statHtml(d);
  if (s.type === 'ending') return script === lifeScript && !G.combined ? lifeEnd(s.ending, s) : ending(s.ending, s);
  const e = s.event;
  let fill = '';
  if (e.age - lastAge > 1) {
    const years = [...Array(Math.min(3, e.age - lastAge - 1))].map(() => lastAge + 1 + Math.floor(Math.random() * (e.age - lastAge - 1))).sort((a, b) => a - b);
    fill = [...new Set(years)].map(y => `<div class="yearfill">${y} 歲　${(p => p[Math.floor(Math.random() * p.length)])(fillerPool())}</div>`).join('');
  }
  lastAge = e.age;
  const seen = skipSeen() && seenStore().has(e.id); markSeen(e.id);
  if (s.reveal) {   // 揭曉：沒有選擇，直接顯示結果
    $('#screen').innerHTML = `${deltaHtml(d)}${fill}<div class="card pres-reveal flip-in"><div class="age-tag">${e.age} 歲・揭曉</div>
      ${textHtml(e, s.text, seen)}<div class="text reveal-r">${esc(G.fill(s.choices[0].text))}</div>
      <div class="choices"><button class="btn choice reveal-go" data-i="0">繼續 ›</button></div>
      <div class="src">依據：${srcHtml(e.sources)}</div></div>`;
    return bindChoices($('#screen'), s, e);
  }
  const pres = e.presentation || 'card';
  if (pres === 'chat' && e.chat) {
    $('#screen').innerHTML = `${deltaHtml(d)}${fill}<div class="card dim"><div class="age-tag">${e.age} 歲</div><div class="text">📱 手機響了……</div></div>`;
    return playChat(e, s);
  }
  const head = pres === 'notification'
    ? `<div class="notif"><b>${esc(e.chat?.app_display_name || e.notification?.app || '通知')}</b><span>現在</span></div>`
    : pres === 'timeskip' ? `<div class="timeskip">— ${e.age} 歲 —</div>` : `<div class="age-tag">${e.age} 歲</div>`;
  $('#screen').innerHTML = `${deltaHtml(d)}${fill}<div class="card pres-${pres} flip-in">${head}
    ${textHtml(e, s.text, seen)}
    <div class="choices">${s.choices.map(choiceHtml).join('')}</div>
    <div class="src">依據：${srcHtml(e.sources)}</div></div>`;
  bindChoices($('#screen'), s, e);
  if (e.pressure) startTimer(e.pressure, $('#screen .card:last-child'));
}
// v7：被動謊言（敘事、無選項）／心態轉場／伏筆回扣／正面事件
const STAGE_LABEL = { child: '童年', student: '學生', adult: '出社會' };
function stageCard(s, delta) {
  statHtml(delta || {});
  const tag = s.kind === 'pos' ? '正面' : s.kind === 'lie' ? '大人的話' : s.kind === 'echo' ? '想起' : '長大';
  const cls = s.kind === 'pos' ? 'pos' : s.kind === 'echo' ? 'beat echo' : 'beat';
  if (s.age > lastAge) lastAge = s.age;
  $('#h-age').textContent = s.age + ' 歲';
  $('#screen').innerHTML = `<div class="card ${cls} flip-in" data-stage-kind="${esc(s.kind)}"><div class="age-tag">${esc(s.age)} 歲<span class="stage-tag">${esc(STAGE_LABEL[s.stage] || '')}${STAGE_LABEL[s.stage] ? '・' : ''}${tag}</span></div>
    <div class="text" style="white-space:pre-line">${esc(s.text)}</div>
    <div class="choices">${s.kind === 'pos' ? s.choices.map((c, i) => `<button class="btn choice" data-si="${i}">${esc(c.text)}</button>`).join('') : '<button class="primary" id="beat-go">繼續 ›</button>'}</div></div>`;
  if (s.kind !== 'pos') return $('#beat-go').onclick = () => {
    const d = G.beatAck();
    if (s.kind === 'lie') $('#log-list').insertAdjacentHTML('afterbegin', `<li>${esc(s.age)} 歲：${esc(s.text.split('\n')[0].slice(0, 28))}…</li>`);
    window.scrollTo(0, 0); render(d);
  };
  document.querySelectorAll('[data-si]').forEach(b => b.onclick = async () => {
    document.querySelectorAll('[data-si]').forEach(x => { x.disabled = true; x.classList.toggle('picked', x === b); });
    await sleep(CHOICE_PAUSE_MS);
    const r = G.posChoose(+b.dataset.si);
    $('#log-list').insertAdjacentHTML('afterbegin', `<li>${esc(r.age)} 歲：${esc(r.choice.text)}</li>`);
    resultCard({ age: r.age }, { outcome_text: r.choice.outcome_text, mood_line: r.choice.mood_line }, r.delta);
  });
}
function bindChoices(root, s, e, onPicked) {
  root.querySelectorAll('button[data-i]').forEach(b => b.onclick = async () => {
    if (b.disabled) return;
    root.querySelectorAll('button[data-i]').forEach(x => { x.disabled = true; x.classList.toggle('picked', x === b); });
    stopTimer();
    const c0 = s.choices[b.dataset.i];
    if (!s.reveal && await rethink(e, c0)) { root.querySelectorAll('button[data-i]').forEach(x => { x.disabled = false; x.classList.remove('picked'); }); return; }
    onPicked?.(c0);
    await sleep(CHOICE_PAUSE_MS);
    const d = G.choose(+b.dataset.i);
    const c = G.lastChoice || c0;   // random 選項：用抽中的分支文字
    $('#log-list').insertAdjacentHTML('afterbegin', `<li>${e.age} 歲：${esc(G.fill(c.log_text || c.text))}</li>`);
    closePhone(); window.scrollTo(0, 0);
    if (s.reveal && !c.outcome_text) return render(d);
    resultCard(e, c, d || {});
  });
}
// v8：「要不要再想一下？」——觀察（警覺）或人際高於門檻時，依資料機率跳出；回傳 true＝玩家要改選
// 設定：script.meta.rethink（詐騙線沒有就用人生線的）＝{ stats:{警覺:70,人際:70}, probability:0, text, back, go }
// 覆寫：event.rethink_probability、choice.rethink_probability；choice.rethink === false 表示這個選項不提醒
function rethink(e, c) {
  const R = script?.meta?.rethink || lifeScript?.meta?.rethink; if (!R || c.rethink === false) return Promise.resolve(false);
  const st = G.player.stats, th = R.stats || { 警覺: 70, 人際: 70 };
  const high = Object.entries(th).some(([k, t]) => (st[k === '觀察' ? '警覺' : k] ?? -1) >= t);
  const pr = c.rethink_probability ?? e.rethink_probability ?? R.probability ?? 0;
  if (!high || !(Math.random() < pr)) return Promise.resolve(false);
  return new Promise(res => {
    const ov = document.createElement('div'); ov.className = 'rethink-ov';
    ov.innerHTML = `<div class="rethink"><div class="text">${esc(c.rethink_text || R.text || '要不要再想一下？')}</div>
      <div class="choices"><button class="choice" data-r="1">${esc(R.back || '再想一下')}</button><button class="primary" data-r="0">${esc(R.go || '就這樣決定')}</button></div></div>`;
    document.body.append(ov);
    ov.querySelectorAll('[data-r]').forEach(b => b.onclick = () => { ov.remove(); res(b.dataset.r === '1'); });
  });
}
// v8：選後狀態畫面。mood_line 來源：choice.mood_line（字串或陣列）→ event.mood_line → meta.mood_lines[{stat,max,text}]（依數值區間）；都沒有就略過
function moodLine(e, c) {
  const one = x => Array.isArray(x) ? x[Math.floor(Math.random() * x.length)] : x;
  if (c?.mood_line) return one(c.mood_line);
  if (e?.mood_line) return one(e.mood_line);
  const st = G.player.stats;
  for (const m of script?.meta?.mood_lines || lifeScript?.meta?.mood_lines || []) if ((st[m.stat || '心理'] ?? 0) <= (m.max ?? 1e9)) return one(m.text);
  return '';
}
function moodScreen(e, line, next) {
  if (!line) return next();
  $('#screen').innerHTML = `<div class="card mood flip-in" id="mood"><div class="age-tag">${esc(e.age ?? '')} 歲</div><div class="text mood-line">${esc(noEmoji(G.fill(line)))}</div><div class="mood-tap">點一下繼續</div></div>`;
  $('#mood').onclick = () => { window.scrollTo(0, 0); next(); };
}
// 選擇後的結果卡：outcome_text（沒有就用紀錄文字）＋數值變化動畫（選前不顯示數字，選後才顯示）→「繼續」才進下一年
const wan = n => n >= 10000 ? `${+(n / 10000).toFixed(1)} 萬` : `${Math.round(n).toLocaleString('zh-TW')} 元`;
const fmtDelta = (k, v) => `${k} ${v > 0 ? '+' : '−'}${k === '存款' || k === '負債' ? wan(Math.abs(v)) : Math.abs(dispD(k, v))}`;
function resultCard(e, c, d) {
  stopTimer(); statHtml(d);
  const ks = Object.entries(d).filter(([, v]) => v);
  $('#screen').innerHTML = `<div class="card result flip-in" id="result"><div class="age-tag">${e.age} 歲</div>
    <div class="text">${esc(noEmoji(G.fill(c.outcome_text || c.log_text || c.text)))}</div>
    ${ks.length ? `<div class="r-deltas">${ks.map(([k, v], i) => `<span class="r-d ${v > 0 ? 'up' : 'down'}" style="animation-delay:${i * 0.15}s" data-k="${esc(k)}" data-v="${v}">${esc(fmtDelta(k, 0 * v || v))}</span>`).join('<span class="r-sep">・</span>')}</div>` : ''}
    <div class="choices"><button class="primary" id="r-go">繼續 ›</button></div></div>`;
  document.querySelectorAll('.r-d').forEach(el => {   // 數字從 0 數到實際變化
    const k = el.dataset.k, v = +el.dataset.v, t0 = performance.now(), dur = REDUCED ? 0 : 600;
    const step = now => { const f = dur ? Math.min(1, (now - t0) / dur) : 1; el.textContent = fmtDelta(k, Math.round(v * f) || Math.sign(v)); if (f < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
  $('#r-go').onclick = () => { window.scrollTo(0, 0); moodScreen(e, moodLine(e, c), () => render()); };
}
// ---- 倒數：至少 25 秒、隨時可關、無壓力模式不顯示 ----
function startTimer(pr, host) {
  if (noPressure() || !host) return;
  const total = Math.max(MIN_TIMER_S, pr.timer_s || 0, script.meta?.no_pressure_mode?.min_timer_s || 0);
  host.insertAdjacentHTML('afterbegin', `<div class="timer" id="timer"><div class="t-row"><span>⏳ ${esc(pr.label || '倒數')}</span><b id="t-left">${total}</b><button class="t-off" id="t-off" aria-label="關閉倒數">關閉倒數 ✕</button></div><div class="t-bar"><i id="t-bar"></i></div></div>`);
  const t0 = Date.now();
  $('#t-off').onclick = () => { stopTimer(); $('#timer')?.remove(); };
  timer = setInterval(() => {
    const left = Math.max(0, total - (Date.now() - t0) / 1000);
    if (!$('#t-left')) return stopTimer();
    $('#t-left').textContent = Math.ceil(left); $('#t-bar').style.width = (left / total * 100) + '%';
    if (!left) { stopTimer(); $('#timer').innerHTML = '<div class="t-row"><span>時間到了。其實沒有人能逼你現在決定，慢慢想。</span></div>'; }
  }, 250);
}
function stopTimer() { clearInterval(timer); timer = null; }
// ---- 仿聊天室（全螢幕；虛構 App）----
const AVATAR = '<svg viewBox="0 0 40 40" aria-hidden="true"><circle cx="20" cy="15" r="8"/><path d="M4 40c2-10 9-14 16-14s14 4 16 14z"/></svg>';
function appOf(chat) { return APPS[chat.app] || { cls: 'app-feed', name: '訊息' }; }
function bubble(m, ev) {
  const side = m.from === 'player' ? 'me' : m.from === 'system' ? 'sys' : 'them';
  const who = side === 'them' && !['scammer', 'contact'].includes(m.from) ? `<span class="who">${esc(roleName(m.from, ev))}</span>` : '';
  const body = m.type === 'image' ? `<div class="img">🖼</div>${esc(m.text)}` : m.type === 'link' ? `<span class="lnk">🔗 ${esc(m.text)}</span>` : esc(m.text);
  return `<div class="msg ${side}" data-mid="${esc(m.id)}">${who}<div class="b">${body}</div></div>`;
}
function roleName(f, ev) { return { shill: '群組成員', teller: '行員', police: '警察', friend: '朋友', family: '家人', scammer: ev?.chat?.contact?.name || '對方' }[f] || f; }
function phoneShell(e, inner, extra = '') {
  const ch = e.chat, a = appOf(ch), c = ch.contact || {};
  const call = ch.app === 'phone_call';
  return `<div class="phone ${a.cls} theme-${esc(ch.theme || '')}" ${extra}>
    <div class="ph-top"><span class="back">‹</span><div class="av">${AVATAR}</div><div class="who"><b>${esc(c.name || '對方')}</b><small>${esc(call ? '通話中' : c.status || '')}</small></div><span class="appname">${esc(ch.app_display_name || a.name)}</span></div>
    <div class="ph-body">${inner}</div></div>`;
}
async function playChat(e, s) {
  const ch = e.chat;
  const ov = document.createElement('div'); ov.id = 'phone-ov'; document.body.append(ov); document.body.classList.add('phone-open');
  ov.innerHTML = phoneShell(e, `<div class="sys-line">${e.age} 歲・${esc(s.text)}</div><div class="thread" id="thread"></div><div class="typing" id="typing" hidden><i></i><i></i><i></i></div>`) +
    `<div class="ph-choices" id="ph-choices"></div><div class="intr" id="intr" hidden></div>`;
  const th = $('#thread'), body = ov.querySelector('.ph-body'), ints = e.interrupts || [];
  const scroll = () => body.scrollTop = body.scrollHeight;
  for (const m of ch.messages || []) {
    if (!document.body.contains(ov)) return;
    if (m.from !== 'player' && m.from !== 'system') { $('#typing').hidden = false; scroll(); }
    await sleep((m.delay_ms ?? 1000) * SPEED);
    if (!document.body.contains(ov)) return;
    $('#typing').hidden = true;
    th.insertAdjacentHTML('beforeend', bubble(m, e)); scroll();
    for (const it of ints.filter(i => i.at === m.id)) await interrupt(it, th, scroll);
  }
  const box = $('#ph-choices');
  box.innerHTML = `<div class="qr">💬 你要怎麼回？</div>${s.choices.map(choiceHtml).join('')}`;
  scroll();
  bindChoices(box, s, e, c => th.insertAdjacentHTML('beforeend', `<div class="msg me sent"><div class="b">${esc(c.text)}</div></div>`) || scroll());
  if (e.pressure) startTimer(e.pressure, box);
}
async function interrupt(it, th, scroll) {
  const b = $('#intr'); b.innerHTML = `<b>${esc(it.from)}</b>${esc(it.text)}`; b.hidden = false; b.classList.remove('show'); void b.offsetWidth; b.classList.add('show');
  th.insertAdjacentHTML('beforeend', `<div class="msg ext"><div class="b"><b>${esc(it.from)}：</b>${esc(it.text)}</div></div>`); scroll();
  await sleep(1600 * SPEED); b.hidden = true;
}
function closePhone() { $('#phone-ov')?.remove(); document.body.classList.remove('phone-open'); }
// ---- 人生線結束：帶 flag 進入詐騙線 ----
function lifeEnd(en, s = {}) {
  const keys = Object.keys(lifeScript.meta?.cross_line_flags || {}).filter(k => !k.startsWith('_'));
  const carry = [...G.player.flags].filter(f => keys.includes(f));
  const missed = [...G.player.flags].filter(f => f.startsWith('missed_'));
  const reasons = (en.reason_texts || []).filter(r => G.player.flags.has(r.flag)).map(r => r.text);
  $('#screen').innerHTML = `<div class="card act" id="life-end" data-id="${esc(en.id)}" data-variant="${esc(s.variant || '')}"><h3>人生的上半場</h3>
    <div class="t-emoji">${esc(en.title_emoji || '')}</div><h2 class="e-title">${esc(en.title || '')}</h2>
    <p class="e-text">${esc(s.text ?? en.text)}</p>${gridHtml(G.lifeGrid(en))}
    ${reasons.length ? `<ul class="flags reasons">${reasons.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}
    ${en.real_world_stat?.display ? `<p class="src">📊 ${esc(en.real_world_stat.display)}</p>` : ''}</div>
  ${missed.length ? `<div class="card act"><h3>回頭看，這些對話有破綻</h3>${anchorsReplay(missed)}</div>` : ''}
  <div class="card"><p class="src">這些經驗會跟著你：${carry.length ? carry.map(esc).join('、') : '（沒有特別的經驗）'}</p>
    <button class="primary" id="cont">日子繼續過下去 →</button></div>`;
  $('#cont').onclick = () => beginScam(carry);
}
// ---- 結局：落幕＋人生格子 → 破綻回顧（回到聊天室圈紅框）→ 真實案件卡 ----
const GRID_EMOJI = { green: '🟩', yellow: '🟨', red: '🟥' };
function gridHtml(cells) { return `<div class="lgrid">${cells.map((c, i) => `<i class="g-${c}" title="${i * 5}–${i * 5 + 4} 歲"></i>`).join('')}</div>`; }
function anchorsReplay(missed, P = G.player, EV = G.events) {
  const anchors = script.red_flag_anchors || {}, map = script.red_flag_texts || {}, seen = new Set(P.entered);
  return missed.map(f => {
    const list = (anchors[f] || []).filter(a => seen.has(a.event) && EV[a.event]?.chat);
    if (!list.length) return `<div class="rf"><p class="rf-t">🚩 ${esc(map[f] || f)}</p></div>`;
    return list.map(a => {
      const e = EV[a.event];
      const msgs = (e.chat.messages || []).map(m => bubble(m, e).replace(`data-mid="${esc(m.id)}"`, `data-mid="${esc(m.id)}"${m.id === a.message ? ' data-anchor="1"' : ''}`)).join('');
      return `<div class="rf">${phoneShell(e, `<div class="thread">${msgs}</div>`, 'data-replay="1"')}<p class="rf-t">🚩 ${esc(map[f] || f)}</p></div>`;
    }).join('');
  }).join('');
}
function helpHtml(en) {   // help_resources：電話號碼取自 name 開頭數字；一律附上 165
  const list = [...(en.help_resources || [])];
  if (!en.help_resources) list.push({ name: '165反詐騙諮詢專線（警政署）', url: 'https://165.npa.gov.tw/' });
  return `<div class="card help" id="help"><h3>${list.some(h => /^19[29]5/.test(h.name)) ? '🫂 需要有人陪你談談' : '🛡 求助資源'}</h3>${list.map(h => {
    const tel = (h.name.match(/^(\d{3,4})/) || [])[1];
    return `<div class="help-r">${tel ? `<a class="btn hotline help-tel" href="tel:${tel}">📞 ${esc(h.name)}</a>` : `<b>${esc(h.name)}</b>`}${h.url ? `<a class="src" href="${esc(h.url)}" target="_blank" rel="noopener">官方網站 ↗</a>` : ''}</div>`;
  }).join('')}</div>`;
}
// 詐騙線在人生中途結束：顯示這段的結局，再回到人生線
function scamEnd(s) {
  const en = s.ending, P = s.scamPlayer, h = G.lifePlayer.scamHistory.at(-1), EV = Object.fromEntries(s.scamScript.events.map(e => [e.id, e]));
  const map = script.red_flag_texts || {}, missed = [...new Set(P.history.flatMap(x => x.set || []))].filter(f => f.startsWith('missed_'));   // 只列這條線裡錯過的
  const reasons = (en.reason_texts || []).filter(r => P.flags.has(r.flag)).map(r => r.text);
  const cc = en.case_card || {}, caught = flagTitle(en).caught, bad = en.grid_color && en.grid_color !== 'green';
  $('#screen').innerHTML = `<div class="card act" id="scam-end" data-id="${esc(en.id)}" data-line="${esc(s.line)}" data-variant="${esc(s.variant || '')}">
    <div class="age-tag">${h.entry_age} 歲｜${esc(h.name || s.line)}</div>
    <div class="t-emoji">${esc(en.title_emoji || '')}</div><h2 class="e-title">${esc(en.title || '')}</h2>
    <p class="e-text">${esc(s.text ?? en.text)}</p>
    ${reasons.length ? `<ul class="flags reasons">${reasons.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}</div>
  <div class="card act"><h3>${esc(flagTitle(en).title)}</h3>
    ${missed.length ? anchorsReplay(missed, P, EV) : `<ul class="flags">${(en.missed_red_flags || []).map(f => `<li>${esc(f)}</li>`).join('')}</ul>`}</div>
  ${bad ? `<div class="card act destig"><b>你不是笨，是話術太專業。</b>被騙不是你的錯，最重要的是盡快求助、止損。</div>` : ''}
  <div class="card act"><h3>📁 真實案件卡</h3><p>${esc(cc.summary || '')}</p>
    ${cc.url && cc.story_id != null ? `<a class="btn" href="${esc(cc.url)}" target="_blank" rel="noopener">閱讀原文（案例 #${esc(cc.story_id)}）↗</a>` : ''}
    ${en.real_world_stat?.display ? `<p class="rws">📊 ${esc(en.real_world_stat.display)}</p>` : ''}</div>
  <div class="card"><button class="primary" id="cont">${h.exit_age > h.entry_age ? `${h.exit_age - h.entry_age} 年後……` : ''}日子繼續過下去 →</button></div>`;
  document.querySelectorAll('[data-anchor]').forEach((m, i) => setTimeout(() => m.classList.add('circled'), 400 + i * 800 * (REDUCED ? 0 : 1)));
  $('#cont').onclick = () => { G.ack(); lastAge = h.exit_age; render(); };
  window.scrollTo(0, 0);
}
function recapHtml() {
  const hs = [...(G.lifePlayer?.scamHistory || [])].sort((a, b) => a.entry_age - b.entry_age);
  return hs.length ? `<div class="recap" id="recap">${hs.map(x => `<p>${x.entry_age}歲｜${esc(x.name || x.line)}：${esc(x.title_emoji || '')} ${esc(x.title || '')}</p>`).join('')}</div>` : '';
}
const ageLived = s => s?.ageLived ?? G.player.age;
// 作者的話＋投稿／聯絡表單（Netlify Forms：index.html 內有同名隱藏表單供偵測；不顯示作者 email）
function authorHtml() {
  return `<div class="card act author" id="author"><h3>作者的話</h3>
    <p>做這個遊戲，是因為我最親近的家人，曾經在找兼職時被騙去當車手；身邊也有好幾位朋友，在網路上遇過各種詐騙。</p>
    <p>我才發現，詐騙離我們一點都不遠，它就藏在日常的某一則訊息、某一通電話裡。</p>
    <p>希望你玩完之後，可以把這個遊戲分享給在乎的人。多一個人看懂話術，就少一個人受騙。</p>
    <p class="src">聯絡作者：請用下方表單</p>
    <form name="contact" id="contact-form" class="contact" autocomplete="on">
      <h3>投稿劇情／聯絡作者</h3>
      <p hidden><label>別填這格 <input name="bot-field" tabindex="-1"></label></p>
      <label>類型 <select name="kind"><option>投稿劇情</option><option>聯絡作者</option></select></label>
      <label>暱稱（選填）<input name="nickname" maxlength="40"></label>
      <label>詐騙類型（選填）<input name="scam_type" maxlength="60"></label>
      <label>內容（必填）<textarea name="message" required rows="5" maxlength="5000" placeholder="請去除可辨識個資（姓名、電話、帳號、地址）"></textarea></label>
      <label>是否同意改編收錄 <select name="consent"><option>是</option><option>否</option></select></label>
      <label>回覆用 email（選填）<input name="email" type="email" maxlength="120"></label>
      <button class="primary" type="submit" id="contact-go">送出</button>
      <p class="src" id="contact-msg" role="status"></p>
    </form></div>`;
}
function bindContact() {
  const f = $('#contact-form'); if (!f) return;
  f.onsubmit = async ev => {
    ev.preventDefault(); const b = $('#contact-go'), m = $('#contact-msg');
    if (!f.message.value.trim()) { m.textContent = '請填寫內容'; return; }
    b.disabled = true; m.textContent = '送出中…';
    try {
      const r = await fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams({ 'form-name': 'contact', ...Object.fromEntries(new FormData(f)) }).toString() });
      if (!r.ok) throw new Error(r.status);
      f.reset(); m.textContent = '已送出，謝謝你'; b.disabled = false;
    } catch (_) { m.textContent = '送出失敗，請稍後再試'; b.disabled = false; }
  };
}
function lieEndHtml(LE) {   // 謊言回顧卡：回顧連結只引用這一局實際出現過的謊言
  const c = LE.card;
  return `<div class="card act lie-end" id="lie-end" data-card="${esc(c.id)}"><h3>這一生的謊言回顧</h3><h2>${esc(c.name)}</h2>
    <p class="e-text">${esc(c.text)}</p>
    ${LE.quotes.length ? `<p class="src">回顧連結：${esc(c.review)}</p>${LE.quotes.map(q => `<div class="quote">${esc(q.age)} 歲・${esc(q.text.split('\n')[0])}</div>`).join('')}` : `<p class="src">回顧連結：這一局沒有聽到相關的話。</p>`}
    <details><summary class="src">真實案件卡與破綻</summary><p class="src" style="white-space:pre-line">${esc(c.case)}</p><ul class="flags">${c.missed.map(m => `<li>${esc(m)}</li>`).join('')}</ul><p class="src">（${esc(c.source_note)}）</p></details></div>`;
}
function ending(en, s = {}) {
  const p = G.player;
  const lives = JSON.parse(localStorage.getItem('lives') || '[]'); lives.push({ end: en.id, t: Date.now() }); localStorage.setItem('lives', JSON.stringify(lives));
  const isHelpSrc = x => /^(165|1925|1995)/.test(x.name || '') || /^https?:\/\/(165\.npa\.gov\.tw\/?$|dep\.mohw\.gov\.tw\/DOMHAOH\/cp-4906-54077)/.test(x.url || '');
  const srcs = (en.sources || []).filter(x => !isHelpSrc(x));
  const HL = /^tel:|mohw\.gov\.tw|1925|1995/i;   // 案件卡不放指向求助專線的連結／說明
  const LE = G.lieEnding && !G._lieShown ? (G._lieShown = G.lieEnding()) : G._lieShown || null;
  const cc0 = en.case_card || {}, cc = { ...cc0, url: cc0.url && !HL.test(cc0.url) ? cc0.url : '', note: (cc0.note || '').split(/[；;]/).filter(t => !/專線|^tel:/.test(t.trim())).join('；') }, cells = G.lifeGrid(en), achNew = achRecord(en, { ...s, lieCard: LE?.card.id });
  const caught = flagTitle(en).caught;
  const map = script.red_flag_texts || {};
  const reasons = (en.reason_texts || []).filter(r => p.flags.has(r.flag)).map(r => r.text);
  const missed = [...p.flags].filter(f => f.startsWith('missed_'));
  const mapped = missed.map(f => map[f]).filter(Boolean);
  const rws = en.real_world_stat;
  const st = (script.stats || []).filter(verifiedOk);
  const bad = en.grid_color && en.grid_color !== 'green';
  // v11 結局頁順序：①分享卡（含 165／1925）＋結局說明 ②不是你的錯 ③真實案件卡 ④破綻 ⑤人生年表
  $('#screen').innerHTML = `
  <div class="card act share-first">
  <h3>分享你的人生（不劇透）</h3><canvas id="cv" width="1080" height="1920" aria-label="${esc((en.title_emoji || '') + ' ' + (en.title || '結局'))}"></canvas>
  <div id="ending" data-id="${esc(en.id)}" data-variant="${esc(s.variant || '')}">
    <p class="e-text">${esc(s.text ?? en.text)}</p>
    ${reasons.length ? `<ul class="flags reasons">${reasons.map(t => `<li>${esc(t)}</li>`).join('')}</ul>` : ''}
    <p class="src">${p.county}・${p.family}家庭・活到 ${ageLived(s)} 歲・存款 ${money(p.stats['存款'] ?? 0)}${p.debt ? `・負債 ${money(p.debt)}` : ''}</p>
    ${p.lifeFlags.length ? `<p class="src">帶著的人生經驗：${p.lifeFlags.map(esc).join('、')}</p>` : ''}</div>
    <button class="primary" id="sh">分享</button><button id="dl">下載結果圖</button><button id="cp">複製分享文字</button></div>
  ${LE ? lieEndHtml(LE) : ''}
  <div class="card act destig">你不是笨，是話術太專業。詐騙集團有劇本、有分工、會針對每個人的弱點設計。被騙不是你的錯，最重要的是盡快求助、止損。</div>
  <div class="card act"><h3>📁 真實案件卡</h3><p>${esc(cc.summary || '')}</p>
    ${cc.url && cc.story_id != null ? `<a class="btn" href="${esc(cc.url)}" target="_blank" rel="noopener">閱讀原文（案例 #${esc(cc.story_id)}）↗</a>` : ''}
    <p class="src">${esc(cc.note || '')}</p>
    ${rws?.display ? `<p class="rws">📊 ${esc(rws.display)}${rws.source ? ` <a href="${esc(rws.source)}" target="_blank" rel="noopener">來源</a>` : ''}</p>` : ''}</div>
  <div class="card act"><h3>${esc(flagTitle(en).title)}</h3>
    ${!caught && missed.length ? `<p class="src">回到當時的對話，紅框是你沒注意到的破綻：</p>${anchorsReplay(missed)}` :
      `<ul class="flags">${(en.missed_red_flags || []).map(f => `<li>${esc(f)}</li>`).join('')}</ul>`}
    ${caught && missed.length ? `<h3>途中你也曾略過</h3>${anchorsReplay(missed)}` : ''}
    ${!caught && missed.length && en.missed_red_flags?.length ? `<details><summary class="src">這類案件常見的破綻</summary><ul class="flags">${en.missed_red_flags.map(f => `<li>${esc(f)}</li>`).join('')}</ul></details>` : ''}</div>
  <div id="log-slot"></div>
  ${achNewHtml(achNew)}
  ${st.length ? `<div class="card"><h3>📊 真實數據</h3>${st.map(s => `<p class="src">${statLine(s)}</p>`).join('')}</div>` : ''}
  ${srcs.length ? `<div class="card"><h3>資料來源</h3><p class="src">${srcHtml(srcs)}</p></div>` : ''}
  ${LE ? `<div class="card share-box"><h3>留下一句想說的話</h3><p class="src">不用留名字。只存在這台裝置，經審核後才可能出現在開始頁。</p>
    <textarea id="say" maxlength="40" placeholder="例如：差點匯出去，後來打給家人確認才停手。"></textarea><button id="say-go">送出這一句</button></div>` : ''}
  ${authorHtml()}
  <button id="again">開始另一段新人生（這一生不能重來）</button>`;
  { const lg = $('#log'); lg.hidden = false; $('#log-slot').replaceWith(lg); }
  // 破綻回顧：紅框逐一圈出（每個 0.8 秒）
  document.querySelectorAll('[data-anchor]').forEach((m, i) => setTimeout(() => m.classList.add('circled'), 400 + i * 800 * (REDUCED ? 0 : 1)));
  document.fonts.load('bold 40px "Noto Sans TC"').catch(() => {}).then(() => document.fonts.ready).then(() => drawCard(en, cells, s));
  $('#dl').onclick = async () => {
    $('#cv').toBlob(async b => {
      const f = new File([b], 'my-life.png', { type: 'image/png' });
      if (navigator.canShare?.({ files: [f] })) { try { await navigator.share({ files: [f], text: shareText(en, cells) }); return; } catch (e) {} }
      const a = document.createElement('a'); a.href = URL.createObjectURL(b); a.download = 'my-life.png'; a.click();
    });
  };
  $('#sh').onclick = async () => {
    track('share');
    const url = siteUrl(), text = shareText(en, cells).replace(url, '').trim();
    const mobile = matchMedia('(pointer:coarse)').matches || /Android|iPhone|iPad/i.test(navigator.userAgent);
    if (mobile && navigator.share) {
      const blob = await new Promise(r => { try { $('#cv').toBlob(r, 'image/png'); } catch (_) { r(null); } });
      const f = blob && new File([blob], 'my-life.png', { type: 'image/png' });
      try {
        if (f && navigator.canShare?.({ files: [f], text, url })) await navigator.share({ files: [f], text, url });
        else await navigator.share({ title: lifeScript?.meta?.title || manifest?.title || '2300萬分之1', text, url });
        return;
      } catch (e) { if (e?.name === 'AbortError') return; }
    }
    try { await navigator.clipboard.writeText(`${text}\n${url}`); toast('已複製連結和分享文字，可以貼給朋友'); }
    catch (_) { toast('無法自動複製，請改用「複製分享文字」'); }
  };
  $('#cp').onclick = () => navigator.clipboard?.writeText(shareText(en, cells)).then(() => toast('已複製'), () => toast('複製失敗，請手動選取'));
  bindContact();
  $('#say-go') && ($('#say-go').onclick = () => {
    const q = $('#say').value.trim().slice(0, 40); if (!q) return toast('先寫一句話');
    const pend = lsJ('sharedPending', []); pend.push({ tag: LE.card.pool === 'heavy' ? '受騙' : LE.card.id === 'END_QUIET' ? '風平浪靜' : '有驚無險', quote: `「${q}」`, who: `${p.county} · ${ageLived(s)} 歲`, t: Date.now() });
    localStorage.setItem('sharedPending', JSON.stringify(pend));
    (G.lifePlayer || p).flags.add('shared_sentence'); const n = achRecord(en, { ...s, lieCard: LE.card.id });
    $('#say-go').disabled = true; toast(n.length ? `已送出・新成就：${n.map(x => x.name).join('、')}` : '已送出，等待審核');
  });
  $('#again').onclick = start;
  window.scrollTo(0, 0);
}
const siteUrl = () => location.href.split(/[?#]/)[0];
function shareText(en, cells) {
  const hs = [...(G.lifePlayer?.scamHistory || [])].sort((a, b) => a.entry_age - b.entry_age).map(x => `${x.entry_age}歲｜${x.name || x.line}：${x.title_emoji || ''} ${x.title || ''}`);
  return `${en.title_emoji || ''} ${en.title || ''}\n${hs.length ? hs.join('\n') + '\n' : ''}${cells.map(c => GRID_EMOJI[c] || '⬜').join('')}\n${en.real_world_stat?.display ? en.real_world_stat.display + '\n' : ''}${en.share_text || ''}\n${siteUrl()}`;
}
function wrap(ctx, text, x, y, w, lh, maxLines = 99, center = false) {
  const lines = []; let line = '';
  for (const ch of text) { if (ctx.measureText(line + ch).width > w) { lines.push(line); line = ch; } else line += ch; }
  lines.push(line);
  for (const l of lines.slice(0, maxLines)) { ctx.fillText(l, center ? x - ctx.measureText(l).width / 2 : x, y); y += lh; }
  return y;
}
// 分享卡 1080×1920：只有稱號、人生格子、真實統計說明、分享文案、網址（不含劇情）
function drawCard(en, cells, s = {}) {
  const c = $('#cv').getContext('2d'), p = G.player, F = '"Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif', W = 1080, H = 1920, cx = W / 2;
  const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#141833'); g.addColorStop(1, '#2d1838'); c.fillStyle = g; c.fillRect(0, 0, W, H);
  c.textBaseline = 'alphabetic';
  c.fillStyle = '#ffb347'; c.font = `800 56px ${F}`; wrap(c, lifeScript?.meta?.title || manifest?.title || '2300萬分之1', cx, 180, 900, 70, 1, true);
  c.fillStyle = '#9aa3c7'; c.font = `40px ${F}`; wrap(c, `我在台灣活了 ${ageLived(s)} 年`, cx, 290, 900, 50, 1, true);
  c.font = `160px ${F}`; wrap(c, en.title_emoji || '', cx, 520, 900, 160, 1, true);
  c.fillStyle = '#fff'; c.font = `800 88px ${F}`; let y = wrap(c, en.title || '', cx, 680, 960, 100, 2, true);
  // 人生格子
  const n = cells.length, per = Math.min(10, n), sz = Math.min(80, Math.floor(880 / per) - 12), gap = 12;
  const rows = Math.ceil(n / per); y += 40;
  const COL = { green: '#43c47a', yellow: '#f2c94c', red: '#eb5757' };
  cells.forEach((col, i) => {
    const r = Math.floor(i / per), k = i % per, cnt = Math.min(per, n - r * per), x0 = cx - (cnt * (sz + gap) - gap) / 2;
    c.fillStyle = COL[col] || '#555'; roundRect(c, x0 + k * (sz + gap), y + r * (sz + gap), sz, sz, 14); c.fill();
  });
  y += rows * (sz + gap) + 30;
  c.fillStyle = '#9aa3c7'; c.font = `30px ${F}`; wrap(c, `每格 5 年　🟩安全 🟨有疑點 🟥受騙損失`, cx, y + 20, 960, 40, 1, true); y += 110;
  const hs = [...(G.lifePlayer?.scamHistory || [])].sort((a, b) => a.entry_age - b.entry_age);   // 只放 emoji＋稱號（不劇透）
  if (hs.length) { c.fillStyle = '#cfd6f5'; c.font = `40px ${F}`; for (const x of hs) y = wrap(c, `${x.entry_age}歲｜${x.name || x.line}：${x.title_emoji || ''} ${x.title || ''}`, cx, y, 960, 54, 2, true); y += 30; }
  if (en.real_world_stat?.display) { c.fillStyle = '#ffd8a0'; c.font = `40px ${F}`; y = wrap(c, en.real_world_stat.display, cx, y, 900, 56, 3, true) + 30; }
  c.fillStyle = '#eef'; c.font = `bold 52px ${F}`; y = wrap(c, en.share_text || '', cx, Math.max(y + 30, 1280), 900, 72, 3, true);
  c.fillStyle = '#ff6b6b'; roundRect(c, 90, 1540, 900, 105, 24); c.fill();
  c.fillStyle = '#5b8def'; roundRect(c, 90, 1665, 900, 105, 24); c.fill();
  c.fillStyle = '#fff'; c.font = `bold 46px ${F}`; wrap(c, '可疑就打 165 反詐騙專線', cx, 1609, 900, 60, 1, true);
  wrap(c, '情緒低落打 1925 安心專線', cx, 1734, 900, 60, 1, true);
  c.fillStyle = '#9aa3c7'; c.font = `32px ${F}`; wrap(c, '你會比我更好嗎？ ' + siteUrl().replace(/^https?:\/\//, ''), cx, 1820, 960, 40, 1, true);
}
function roundRect(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
function flagTitle(en) {
  const guess = typeof en.caught === 'boolean' ? en.caught : en.outcome ? en.outcome === 'good' : /^你抓到/.test(en.missed_red_flags?.[0] || '');
  return { caught: guess, title: en.red_flags_title || (guess ? '✅ 你抓到的破綻' : '🚩 你錯過的破綻') };
}
(async () => {
  manifest = Q.get('script') ? { lines: [{ id: 'custom', file: Q.get('script') }] } : await Engine.load(Q.get('manifest') || 'manifest.json');
  manifest.birth ||= {};
  const loaded = await Promise.all(manifest.lines.map(l => Engine.load(l.file)));
  manifest.lines.forEach((l, i) => scripts[l.id] = loaded[i]);
  // 人生線（選用）：manifest.life.file 存在且（enabled 或 ?life=1）時先玩人生線；讀不到就當沒有
  const lf = manifest.life;
  if (lf?.file && (lf.enabled || Q.get('life') === '1') && Q.get('life') !== '0') lifeScript = await Engine.load(Q.get('lifefile') || lf.file).catch(() => null);
  if (!manifest.birth.county_pool) Object.assign(manifest.birth, { county_pool: loaded[0].player_init.county_pool, family_pool: loaded[0].player_init.family_pool.map(f => f.name) });
  ACH = (await Engine.load('achievements.json').catch(() => null))?.achievements || null;
  STAGE_POOL = await Engine.load('stage-pool.json').catch(() => null);
  start();
})()
  .catch(e => { $('#screen').innerHTML = `<div class="card">${esc(e.message)}<br>請用本機伺服器開啟（python3 -m http.server）。</div>`; });
