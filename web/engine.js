// 通用劇本引擎：只依 JSON 結構運作，新增劇本線不需改程式；不認得的欄位一律忽略
const Engine = (() => {
  const rnd = (a, b) => Math.floor(a + Math.random() * (b - a + 1));
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  const clone = o => JSON.parse(JSON.stringify(o));
  const OPS = { gt: (a, b) => a > b, gte: (a, b) => a >= b, lt: (a, b) => a < b, lte: (a, b) => a <= b };
  const GRID_RANK = { green: 0, yellow: 1, red: 2 };
  // 條件語法：flags_all / flags_any / flags_none / stats / any_of，另有 family_in / county_in（用於出生分配）
  function test(cond = {}, ctx) {
    const has = f => ctx.flags?.has(f);
    if (!(cond.flags_all || []).every(has)) return false;
    if (cond.flags_any && !cond.flags_any.some(has)) return false;
    if ((cond.flags_none || []).some(has)) return false;
    for (const [k, c] of Object.entries(cond.stats || {}))
      if (!Object.entries(c).every(([o, n]) => OPS[o]?.(ctx.stats?.[k] ?? 0, n))) return false;
    if (cond.family_in && !cond.family_in.includes(ctx.family)) return false;
    if (cond.county_in && !cond.county_in.includes(ctx.county)) return false;
    if (cond.any_of && !cond.any_of.some(c => test(c, ctx))) return false;
    return true;
  }
  // 跨線規則：移植 common.apply_modifiers(data, flags)；回傳 [套用後 events, 開局數值調整]
  function applyModifiers(script, flags, combined = false) {
    const evs = Object.fromEntries(script.events.map(e => [e.id, clone(e)])), init = {};
    for (const m of script.cross_line_modifiers || []) {
      const c = m.if_flags || {}, t = m.target || {}, ef = m.effect || {};
      if (combined && m.mode === 'standalone_only') continue;   // 只在單線模式套用
      if (!(c.all || []).every(f => flags.has(f)) || (c.none || []).some(f => flags.has(f))) continue;
      if (t.event === '__INIT__') { for (const [k, v] of Object.entries(ef.stats || {})) init[k] = (init[k] || 0) + v; continue; }
      const e = evs[t.event]; if (!e) { console.warn('cross_line target 不存在', m.id); continue; }
      if (ef.type === 'stats_delta') { e.on_enter_effects ||= {}; for (const [k, v] of Object.entries(ef.stats || {})) e.on_enter_effects[k] = (e.on_enter_effects[k] || 0) + v; }
      else if (ef.type === 'unlock_choice') e.choices.push(clone(ef.choice));
      else if (ef.type === 'add_interrupt') (e.interrupts ||= []).push(ef.interrupt);
      else if (ef.type === 'rewrite_text') { if (ef.field === 'text') e.text = ef.text; else if (e.choices[t.choice]) e.choices[t.choice].text = ef.text; }
    }
    return [Object.values(evs), init];
  }
  // 出生：縣市、家庭、各數值的百分位擲骰（0–1）
  function rollBirth(cfg = {}) {
    const rolls = {}; for (const k of cfg.rolls || []) rolls[k] = Math.random();
    return { county: pick(cfg.county_pool || ['臺灣']), family: pick(cfg.family_pool || ['一般']), stats: rolls };
  }
  // 依出生條件抽劇本線（劇本自帶 entry 優先於 manifest）
  function assignLine(lines, birth, entries = {}) {
    const ok = lines.map(l => {
      const e = entries[l.id] || l;
      if (e.conditions && !test(e.conditions, birth)) return [l, 0];
      let w = e.weight ?? 1;
      for (const m of e.weight_mods || []) if (test(m.if, birth)) w *= m.mul ?? 1;
      return [l, w];
    }).filter(([, w]) => w > 0);
    let r = Math.random() * ok.reduce((s, [, w]) => s + w, 0);
    for (const [l, w] of ok) if ((r -= w) <= 0) return l;
    return ok.length ? ok[ok.length - 1][0] : lines[0];
  }
  // opts.flags：人生線帶進來的 flag（或除錯注入）
  function create(script, birth, opts = {}) {
    const pi = script.player_init;
    const p = { stats: {}, flags: new Set([...(pi.flags || []), ...(opts.flags || [])]), lifeFlags: [...(opts.flags || [])], debt: 0, history: [], entered: [] };
    const [events, initMod] = applyModifiers(script, new Set(p.flags), !!opts.combined);
    const ev = Object.fromEntries(events.map(e => [e.id, e]));
    const en = Object.fromEntries(script.endings.map(e => [e.id, e]));
    // 出生縣市／家庭沿用 birth；家庭加成：存款_mod 乘、其他加；之後只夾 min/max（與 validate.py 一致）
    if (opts.stats) {   // 合併模式：不重新投胎，沿用人生線的數值／縣市／家庭
      p.county = opts.county; p.family = opts.family;
      for (const k in opts.stats) p.stats[k] = opts.stats[k];
      for (const [k, v] of Object.entries(initMod)) if (k in p.stats) { p.stats[k] += v; clamp(k); }
      p.initStats = { ...p.stats };
    } else {
    p.county = birth?.county || pick(pi.county_pool || ['臺灣']);
    const famName = birth?.family || pick(pi.family_pool || [{ name: '一般' }]).name;
    const fam = (pi.family_pool || []).find(f => f.name === famName) || { name: famName };
    p.family = famName;
    const IR = script.meta?.initial_stats_roll;
    if (IR) {   // v0.9：各數值均勻整數骰＋temperament（不套 family_pool，與 combined.py 一致）
      for (const k of Object.keys(pi.stats)) p.stats[k] = rnd(...IR.stats[k].range);
      p.rolled = { ...p.stats };
      const u = Math.random(); let acc = 0; p.tempU = u;
      for (const t of IR.temperament) { acc += t.p; if (u < acc) { p.temperament = t.id; p.stats['心理'] += t['心理'] || 0; clamp('心理'); break; } }
    } else {
    for (const [k, d] of Object.entries(pi.stats)) {
      const r = d.init_range;
      p.stats[k] = !r ? (d.min ?? 0) : birth?.stats?.[k] != null ? Math.round(r[0] + birth.stats[k] * (r[1] - r[0])) : rnd(...r);
    }
    for (const [k, v] of Object.entries(fam)) {
      if (k === 'name') continue;
      const s = k.endsWith('_mod') ? k.slice(0, -4) : k;
      if (!(s in p.stats)) continue;
      p.stats[s] = k.endsWith('_mod') ? Math.round(p.stats[s] * (1 + v)) : p.stats[s] + v;
    }
    for (const k in p.stats) clamp(k);
    }
    for (const [k, v] of Object.entries(initMod)) if (k in p.stats) { p.stats[k] += v; clamp(k); }   // __INIT__ 跨線調整
    p.initStats = { ...p.stats };
    }
    p.age = opts.age ?? 0;
    let cur = opts.start || pi.start_event, enteredId = null, randomPick = {}, prevAge = null, routerPick = null;
    const REC = opts.recovery;   // 人生線 meta.mental_time_recovery：前進到下一個事件時 +per_year×年齡差

    function clamp(k) {
      const d = pi.stats[k] || {};
      if (d.min != null && p.stats[k] < d.min) { if (!('max' in d)) p.debt += d.min - p.stats[k]; p.stats[k] = d.min; }
      if (d.max != null && p.stats[k] > d.max) p.stats[k] = d.max;
    }
    const has = f => f.startsWith('!') ? !p.flags.has(f.slice(1)) : p.flags.has(f);
    const reqOk = c => (c.flags?.require || []).every(has);
    function fill(t) { return (t || '').replace(/\{(\w+)\}/g, (m, k) => p[k] ?? p.stats[k] ?? m); }
    function routeEnding() {
      const sorted = [...script.endings].sort((a, b) => (a.priority ?? 999) - (b.priority ?? 999));
      return sorted.find(e => test(e.conditions, p)) || en[script.ending_rules?.fallback] || sorted[sorted.length - 1];
    }
    function addStats(eff) {
      const before = { ...p.stats }, debtBefore = p.debt;
      for (let [k, v] of Object.entries(eff || {})) { if (opts.scale && k === opts.scale.stat && v < 0) v *= opts.scale.fac; if (!(k in p.stats)) p.stats[k] = 0; p.stats[k] += v; clamp(k); }
      const delta = {}; for (const k in p.stats) if (p.stats[k] !== before[k]) delta[k] = p.stats[k] - before[k];
      if (p.debt !== debtBefore) delta['負債'] = p.debt - debtBefore;
      return delta;
    }
    // 隨機事件（random:true + random_weights{flag:w}）：在可選選項中依權重抽一個
    function randomChoice(e, choices) {
      if (randomPick[e.id] && choices.includes(randomPick[e.id])) return randomPick[e.id];
      const w = e.random_weights || {};
      const ws = choices.map(c => (c.flags?.set || []).reduce((s, f) => s + (w[f] ?? 0), 0) || (Object.keys(w).length ? 0 : 1));
      const tot = ws.reduce((a, b) => a + b, 0);
      let r = Math.random() * tot, k = 0;
      if (!tot) k = 0; else for (; k < ws.length - 1; k++) if ((r -= ws[k]) <= 0) break;
      return (randomPick[e.id] = choices[k]);
    }
    let enterDelta = null;
    function current() {
      for (let guard = 0; guard < 60; guard++) {
        if (cur === '__EVAL__') {
          for (const sf of script.ending_rules?.stat_flags || []) { p.flags.delete(sf.flag); if (test({ stats: sf.stats }, p)) p.flags.add(sf.flag); }   // 即時重算
          cur = routeEnding().id; continue;
        }
        if (en[cur]) return { type: 'ending', ending: en[cur], ...endingText(en[cur]) };
        const e = ev[cur];
        if (!e) { console.warn('找不到節點', cur); cur = routeEnding().id; continue; }
        if (opts.fixedAge != null) p.age = opts.fixedAge; else if (e.age != null) p.age = e.age;
        if (enteredId !== cur) {   // 進入事件：on_enter_effects 每次進入套用一次
          enteredId = cur; p.entered.push(cur); routerPick = null;
          if (REC && e.age != null) { if (prevAge != null && e.age > prevAge) { p.stats[REC.stat] += REC.per_year * (e.age - prevAge); clamp(REC.stat); } prevAge = e.age; }
          enterDelta = e.on_enter_effects ? addStats(e.on_enter_effects) : null;
        }
        if (e.router && opts.routerStep) {   // 合併模式：路由也算一步（空檔要插詐騙線、要檢查 early_halt）
          if (!routerPick) { const ok = e.choices.filter(reqOk); routerPick = (e.random ? ok[Math.floor(Math.random() * ok.length)] : ok[0]) || 'none'; }
          if (routerPick === 'none') { cur = routeEnding().id; continue; }
          return { type: 'router', event: e, choice: routerPick };
        }
        if (e.router) { const ok = e.choices.filter(reqOk); const c = e.random ? ok[Math.floor(Math.random() * ok.length)] : ok[0]; if (c) opts.trace?.push({ t: c.text, f: (c.flags?.set || []).join(','), n: c.next, u: null }); cur = c ? (apply(e, c), c.next) : routeEnding().id; continue; }
        let choices = e.choices.filter(reqOk);
        if (!choices.length) { cur = routeEnding().id; continue; }
        // 同一事件的可選選項文字完全相同（例如 elder）＝隨機事件：只顯示一個，避免出現兩顆一模一樣的按鈕
        if (e.random) choices = [randomChoice(e, choices)];
        // 揭曉事件（category 揭曉，選項全由 require 決定）：引擎自動顯示唯一成立的結果
        const reveal = e.category === '揭曉' || e.reveal === true;
        if (reveal) choices = choices.slice(0, 1);
        return { type: 'event', event: e, text: fill(((e.text_variants || []).find(v => (v.when?.flags_all || []).every(f => p.flags.has(f)) && !(v.when?.flags_none || []).some(f => p.flags.has(f))) || e).text), choices, enterDelta, reveal };
      }
      return { type: 'ending', ending: routeEnding() };
    }
    // 結局文字變體（移植 common.pick_text）＋前提檢查（requires_flags／forbids_flags，違反時 console.warn）
    function endingText(x) {
      const v = (x.text_variants || []).find(v => (v.when.flags_all || []).every(f => p.flags.has(f)) && !(v.when.flags_none || []).some(f => p.flags.has(f))) || null;
      const miss = [...(x.requires_flags || []), ...(v?.requires_flags || [])].filter(f => !p.flags.has(f));
      const bad = [...(x.forbids_flags || []), ...(v?.forbids_flags || [])].filter(f => p.flags.has(f));
      p.premise = { ending: x.id, variant: v?.when?.label || null, missing: miss, forbidden: bad };
      if (miss.length || bad.length) console.warn('結局前提不符', x.id, v?.when?.label || '', '缺', miss, '不該有', bad);
      return { text: fill(v ? v.text : x.text), variant: v?.when?.label || null };
    }
    function apply(e, c) {
      const delta = addStats(c.effects);
      (c.flags?.set || []).forEach(f => p.flags.add(f));
      p.history.push({ set: [...(c.flags?.set || [])], age: opts.fixedAge ?? e.age ?? p.age, id: e.id, choice: c.text, idx: e.choices.indexOf(c), grid: c.grid, router: !!e.router, delta });
      return delta;
    }
    // random:true 選項（移植 common.branches／resolve）：按下後抽一次 U(0,1)，依 outcomes 順序累加 probability
    function resolve(c) {
      p.lastU = null;
      if (!c.random || !c.outcomes?.length) return c;
      const u = Math.random(); p.lastU = u; let acc = 0, b = c.outcomes[c.outcomes.length - 1];
      for (const x of c.outcomes) { acc += x.probability; if (u < acc) { b = x; break; } }
      const eff = { ...(c.effects || {}) }; for (const [k, v] of Object.entries(b.effects || {})) eff[k] = (eff[k] || 0) + v;
      const m = { ...c, effects: eff, flags: { set: [...(c.flags?.set || []), ...(b.flags_set || [])], require: c.flags?.require || [] }, next: b.next ?? c.next, outcome_text: b.outcome_text, log_text: b.log_text, grid: b.grid ?? c.grid, branch: c.outcomes.indexOf(b), u };
      delete m.outcomes; delete m.random; return m;
    }
    function takeRouter() { const s = current(); if (s.type !== 'router') return null; const c = s.choice; opts.trace?.push({ t: c.text, f: (c.flags?.set || []).join(','), n: c.next, u: null }); p.lastChoice = c; const d = apply(s.event, c); cur = c.next; routerPick = null; return d; }
    function endingById(id) { cur = id; return current(); }
    function choose(i) { const s = current(); if (s.type !== 'event') return null; const c0 = s.choices[i]; let c = resolve(c0); opts.trace?.push({ t: c0.text, f: (c0.flags?.set || []).join(','), n: c0.next, u: c.u ?? null }); const ov = (c.outcome_variants || []).find(v => (v.when?.flags_all || []).every(f => p.flags.has(f)) && !(v.when?.flags_none || []).some(f => p.flags.has(f))); if (ov) c = { ...c, outcome_text: ov.text }; p.lastChoice = c; const d = apply(s.event, c); p.history[p.history.length - 1].idx = s.event.choices.indexOf(c0); cur = c.next; return d; }
    // 人生格子：每 bucket_years 一格，取區間內最嚴重的 choice.grid；沒有事件為 green；最後一格用 ending.grid_color
    function lifeGrid(ending) {
      const by = script.meta?.life_grid?.bucket_years || 5;
      const n = Math.floor(p.age / by) + 1, cells = Array(n).fill('green');
      for (const h of p.history) if (h.grid && !h.router) {
        const b = Math.min(n - 1, Math.floor(h.age / by));
        if ((GRID_RANK[h.grid] ?? 0) > GRID_RANK[cells[b]]) cells[b] = h.grid;
      }
      if (ending?.grid_color) cells[n - 1] = ending.grid_color;
      return cells;
    }
    return { get lastChoice() { return p.lastChoice; }, player: p, current, choose, takeRouter, endingById, script, fill, events: ev, lifeGrid };
  }
  // ---- 合併模式（移植 combined.py play()／play_scam()，scam_integration v2.0）----
  // 開局對每條線抽 entry_age 與機率；人生線每做完一個事件 E→N，處理 a_E ≤ entry_age < a_N 的線；詐騙線結束回到 N
  function createCombined(life, scams, birth, opts = {}) {
    const SI = life.meta.scam_integration, RM = SI.return_map, rec = SI.pre_entry?.mental_recovery;
    const MR = life.meta?.mental_time_recovery, HALT = life.meta?.early_halt;
    const L = create(life, birth, { ...opts, routerStep: true, recovery: MR?.per_year ? MR : null }), lp = L.player, endAge = L.events.LIFE_ROUTER?.age ?? 40;
    const lps = life.player_init.stats;
    const clampLife = () => { for (const [k, d] of Object.entries(lps)) { if (!(k in lp.stats)) continue; if (d.min != null && lp.stats[k] < d.min) lp.stats[k] = d.min; if (d.max != null && lp.stats[k] > d.max) lp.stats[k] = d.max; } };
    const randint = (a, b) => a + Math.floor(Math.random() * (b - a + 1));
    lp.scamHistory = [];
    const plan = opts.plan || SI.lines.map((h, i) => { const w = h.entry_window; return [w.base_age + randint(w.offset_min, w.offset_max), i, h, Math.random() < h.probability, false]; });
    let last = null, sub = null, subHook = null, pendingEnd = null, queue = [], slot = null, halted = false;
    const haltNow = () => HALT && lp.stats[HALT.stat] <= 0;
    function halt() { halted = true; lp.flags.add('life_halted'); queue = []; slot = null; }
    function afterLife(e, c) {   // 人生線每一步（含路由）之後：early_halt，然後處理 [這一步, 下一事件) 空檔裡的詐騙線
      if (haltNow()) { halt(); return; }
      const aN = c.next === '__EVAL__' ? endAge : L.events[c.next].age;
      slot = { cur: e.age, aN, eid: e.id };
      queue = plan.filter(p => !p[4] && e.age <= p[0] && p[0] < aN).sort((x, y) => x[0] - y[0] || x[1] - y[1]);
      advance();
    }
    function statflags(rules) { for (const sf of rules?.stat_flags || []) { lp.flags.delete(sf.flag); if (test({ stats: sf.stats }, lp)) lp.flags.add(sf.flag); } }
    function advance() {   // 依序處理這個空檔裡的線；進入一條就停，等它結束再繼續
      while (queue.length) {
        const p = queue.shift(), h = p[2], age0 = Math.max(p[0], slot.cur);
        if (age0 + 1 > slot.aN) { p[0] = Math.max(age0, slot.aN); continue; }   // 空檔被占用：順延
        p[4] = true;
        if (age0 >= endAge) continue;
        statflags(scams[h.line].ending_rules);
        if (!(p[3] && test(h.trigger || {}, lp))) continue;
        if (rec) { lp.stats[rec.stat] += rec.delta; clampLife(); }
        const sc = h.amount_scaling, fac = sc ? Math.max(lp.stats[sc.stat], sc.floor) / sc.ref : 1;
        sub = create(scams[h.line], null, { combined: true, trace: opts.trace, flags: [...lp.flags], stats: { ...lp.stats }, county: lp.county, family: lp.family, start: h.entry_event, age: age0, fixedAge: age0, scale: sc ? { stat: sc.stat, fac } : null });
        sub.player.lifeFlags = [...lp.flags]; subHook = h; sub.entryAge = age0; sub.after = slot.eid; sub.fac = fac;
        return;
      }
      slot = null;
    }
    function leave(end, variant) {
      const h = subHook, sp = sub.player, internal = new Set(sp.history.flatMap(x => x.set || []));
      let dur = h.duration?.default_years || 0;
      for (const r of h.duration?.rules || []) if (r.if_flags_any.some(q => internal.has(q))) { dur = r.years; break; }
      const m = RM[h.line]?.[end.id] || { flags: [] };
      if (!RM[h.line]?.[end.id]) console.warn('return_map 缺', h.line, end.id);
      for (const q of [...RM._always.flags, ...m.flags]) lp.flags.add(q.replace('{line}', h.line));
      for (const [k, v] of Object.entries(RM._carry_internal || {})) if (!k.startsWith('_') && internal.has(k)) lp.flags.add(v);
      for (const k in lp.stats) lp.stats[k] = sp.stats[k];
      for (const [k, v] of Object.entries(m.stats_delta || {})) lp.stats[k] += v;
      clampLife();
      const age1 = sub.entryAge + dur;
      lp.scamHistory.push({ line: h.line, name: h.name, ending_id: end.id, title: end.title, title_emoji: end.title_emoji, grid_color: end.grid_color, variant, entry_age: sub.entryAge, exit_age: age1, internal_flags: [...internal], choices: sp.history.map(x => [x.id, x.idx, x.choice]), after: sub.after, scale: sub.fac });
      slot.cur = age1; lp.age = Math.max(lp.age, age1);
      sub = null; subHook = null;
      if (haltNow()) halt();   // 詐騙線演完後心理 ≤ 0：不回人生線
    }
    const api = {
      get player() { return sub ? sub.player : lp; }, get lastChoice() { return last; }, get halted() { return halted; }, lifePlayer: lp, life: L, combined: true, plan,
      get line() { return sub ? subHook.line : 'life'; },
      get script() { return sub ? sub.script : life; },
      get events() { return sub ? sub.events : L.events; },
      fill: t => (sub || L).fill(t),
      current() {
        if (pendingEnd) return pendingEnd;
        if (sub) {
          const s = sub.current();
          if (s.type === 'ending') { const sp = sub.player, line = subHook.line, scr = sub.script; leave(s.ending, s.variant); pendingEnd = { ...s, type: 'scam_end', line, scamPlayer: sp, scamScript: scr }; return pendingEnd; }
          return { ...s, event: s.event && { ...s.event, age: sub.entryAge }, line: subHook.line };
        }
        if (halted) { const s = L.endingById(HALT.ending); s.ageLived = Math.max(lp.age, ...lp.scamHistory.map(x => x.exit_age)); return { ...s, halted: true, line: 'life' }; }
        let s = L.current();
        for (let g = 0; s.type === 'router' && g < 60; g++) { const e = s.event, c = s.choice; L.takeRouter(); afterLife(e, c); return api.current(); }
        if (s.type === 'ending') s.ageLived = Math.max(lp.age, ...lp.scamHistory.map(x => x.exit_age));
        return { ...s, line: 'life' };
      },
      ack() { pendingEnd = null; if (slot) advance(); },
      choose(i) {
        if (sub) { const d = sub.choose(i); last = sub.player.lastChoice; return d; }
        const s = L.current(), e = s.event, d = L.choose(i), c = last = lp.lastChoice;
        afterLife(e, c);
        return d;
      },
      lifeGrid(ending) {   // 人生選項 grid ＋ 詐騙線結局 grid_color（放進 entry_age 那格）
        const by = life.meta?.life_grid?.bucket_years || 5, top = Math.max(lp.age, ...lp.scamHistory.map(x => x.exit_age));
        const n = Math.floor(top / by) + 1, cells = Array(n).fill('green');
        const put = (age, g) => { if (!g) return; const b = Math.min(n - 1, Math.floor(age / by)); if ((GRID_RANK[g] ?? 0) > GRID_RANK[cells[b]]) cells[b] = g; };
        for (const h of lp.history) if (!h.router) put(h.age, h.grid);
        for (const x of lp.scamHistory) put(x.entry_age, x.grid_color);
        if (ending?.grid_color) cells[n - 1] = ending.grid_color;
        return cells;
      },
    };
    return api;
  }
  async function load(url) {
    const r = await fetch(url, { cache: 'no-cache' });
    if (!r.ok) throw new Error(`讀不到 ${url}（${r.status}）`);
    return r.json();
  }
  return { create, createCombined, load, rollBirth, assignLine, test, applyModifiers };
})();
