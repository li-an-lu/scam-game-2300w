// stage.js（v7）：年齡階段抽池層。包在 Engine.createCombined 外面，不改人生線／詐騙線本身。
// 每個階段固定抽 draws 則（被動謊言 ≤ max_lies，且不會連續兩則謊言），依年齡插在人生線事件之前。
// 正面事件可埋伏筆 flag（fs_verify／reminded_family／talked_family_work），之後進入詐騙線時回扣一句。
const Stage = (() => {
  const rnd = a => a[Math.floor(Math.random() * a.length)];
  function wpick(list, w) { const t = list.reduce((s, x) => s + w(x), 0); let r = Math.random() * t; for (const x of list) if ((r -= w(x)) <= 0) return x; return list[list.length - 1]; }
  function plan(P) {
    const out = [];
    for (const st of P.stages) {
      const okA = x => (x.min_age == null || x.age >= x.min_age) && (x.max_age == null || x.age <= x.max_age);   // v8
      const lies = P.lies.filter(l => l.stage === st.id && okA(l)), pos = P.positive.filter(p => p.stage === st.id && okA(p));
      const nL = Math.min(st.max_lies, Math.floor(st.draws / 2)), nP = st.draws - nL;   // 約 1:1
      const pickL = [], pickP = [];
      const pool = [...lies];
      while (pickL.length < nL && pool.length) { const x = wpick(pool, l => l.core_flags.length ? P.core_lie_weight : 1); pickL.push(x); pool.splice(pool.indexOf(x), 1); }
      const pp = [...pos]; while (pickP.length < nP && pp.length) pickP.push(pp.splice(Math.floor(Math.random() * pp.length), 1)[0]);
      // 依年齡合併，並做冷卻：上一則是謊言時，下一則一定先放正面事件；正面事件用完就不再放謊言
      const L = pickL.sort((x, y) => x.age - y.age), Pq = pickP.sort((x, y) => x.age - y.age), seq = [];
      while (L.length || Pq.length) {
        const prev = seq.length ? seq[seq.length - 1] : out[out.length - 1], lastLie = prev?.kind === 'lie';
        const takeLie = L.length && !lastLie && (!Pq.length || L[0].age <= Pq[0].age);
        if (takeLie) seq.push({ kind: 'lie', item: L.shift() });
        else if (Pq.length) seq.push({ kind: 'pos', item: Pq.shift() });
        else break;
      }
      let lastAge = st.min_age;
      seq.forEach(x => { x.age = Math.max(lastAge, Math.min(st.max_age, x.item.age)); lastAge = x.age; x.stage = st.id; });
      out.push(...seq);
      if (st.id === 'child') out.push({ kind: 'mindset', age: 13, stage: 'student' });
    }
    return out;
  }
  function wrap(inner, P) {
    const lp = inner.lifePlayer, queue = plan(P), echoed = new Set();
    lp.firedLies = []; lp.stageLog = { child: { lie: 0, pos: 0 }, student: { lie: 0, pos: 0 }, adult: { lie: 0, pos: 0 } };
    let pending = null;
    const clamp = () => { for (const k of ['警覺', '人際', '心理']) lp.stats[k] = Math.max(k === '心理' ? 1 : 0, Math.min(100, lp.stats[k])); };   // 被動事件不會單獨造成提早結束
    const addEff = e => { const d = {}; for (const [k, v] of Object.entries(e || {})) { if (!(k in lp.stats)) continue; const b = lp.stats[k]; lp.stats[k] += v; clamp(); d[k] = lp.stats[k] - b; } return d; };
    function mindset() {
      const c = lp.stageLog.child;
      return P.childhood_mindset.find(m => (m.when.min_pos == null || c.pos >= m.when.min_pos) && (m.when.min_lies == null || c.lie >= m.when.min_lies));
    }
    const api = Object.create(inner);
    api.stagePlan = queue; api.pool = P;
    api.current = () => {
      if (pending) return pending;
      const s = inner.current();
      if (s.type === 'event' && s.line === 'life') {
        const a = s.event.age;
        if (queue.length && queue[0].age <= a) {
          const q = queue.shift();
          if (q.kind === 'mindset') { const m = mindset(); pending = { type: 'beat', kind: 'mindset', age: q.age, text: m.text, effects: m.effects, stage: q.stage }; }
          else pending = { type: q.kind === 'lie' ? 'beat' : 'pos', kind: q.kind, age: Math.max(q.age, lp.age), item: q.item, text: q.item.text, stage: q.stage, choices: q.item.choices };
          return pending;
        }
      }
      if (s.type === 'event' && s.line !== 'life') {
        const key = s.line + ':' + (s.event.age ?? '');
        const fs = Object.keys(P.foreshadow).filter(f => lp.flags.has(f));
        if (!echoed.has(key) && fs.length) { echoed.add(key); pending = { type: 'beat', kind: 'echo', age: s.event.age, text: P.foreshadow[rnd(fs)], effects: {} }; return pending; }
        echoed.add(key);
      }
      if (s.type === 'ending') queue.length = 0;   // 提早結束：剩下的被動事件不再出現
      return s;
    };
    api.beatAck = () => {   // 被動謊言／心態／回扣：沒有選項，按「繼續」
      const b = pending; pending = null; if (!b) return {};
      const d = addEff(b.kind === 'lie' ? b.item.effects : b.effects);
      if (b.kind === 'lie') {
        lp.stageLog[b.stage].lie++;
        if (b.stage === 'child') lp.flags.add(`lie_child_${lp.stageLog.child.lie}`);
        for (const f of b.item.core_flags) lp.flags.add(f);
        lp.firedLies.push({ id: b.item.id, age: b.age, text: b.item.text, flags: b.item.core_flags });
      }
      return d;
    };
    api.posChoose = i => {   // 正面事件
      const b = pending; pending = null; const c = b.item.choices[i];
      lp.stageLog[b.stage].pos++;
      for (const f of c.flags) lp.flags.add(f);
      return { choice: c, delta: addEff(c.effects), age: b.age };
    };
    // 謊言回顧卡：依實際結果分輕／重兩池，再依核心 flag 加權；有前置 flag 的卡沒 flag 不會出現
    api.lieEnding = () => {
      const F = lp.flags, core = P.core_flags.filter(f => F.has(f));
      const heavy = F.has('scam_money_lost') || F.has('lost_money') || F.has('life_halted') || [...F].some(f => /_lost$|^lost_/.test(f));
      const pool = P.lie_endings.filter(c => c.pool === (heavy ? 'heavy' : 'light') && c.requires.every(f => F.has(f)));
      const w = c => Math.max(c.base, ...Object.entries(c.boost).map(([f, v]) => (f === '_no_core' ? core.length === 0 : F.has(f)) ? v : 0));
      const forced = P.lie_endings.filter(c => c.force && c.requires.length && c.requires.every(f => F.has(f)));   // v8：force:true 且 requires 全成立就必出
      const card = forced.length ? forced[0] : wpick(pool, w);
      const linked = lp.firedLies.filter(l => l.flags.some(f => card.review_flags.includes(f)));
      const quotes = (linked.length ? linked : lp.firedLies).slice(0, 2);
      return { card, quotes, core };
    };
    return api;
  }
  return { wrap, plan };
})();
