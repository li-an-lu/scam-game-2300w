// ============================================================
// 階段最低事件次數 - 完整修改片段
// 請將以下內容整合進 web/engine.js
// ============================================================

// ---------- 1. 在檔案頂部（或其他常數區）加入 ----------
const STAGE_MIN = {
  childhood: { maxAge: 12, minEvents: 6 },
  student:   { maxAge: 22, minEvents: 7 }
};

function getStage(age) {
  if (age == null) return 'adult';
  if (age <= 12) return 'childhood';
  if (age <= 22) return 'student';
  return 'adult';
}

// ---------- 2. 在 create() 與 createCombined() 的 p 初始化處加入 ----------
// 找到類似這行：
//   const p = { stats: {}, flags: new Set(...), ... };
// 改為加入 stageCounts：
/*
const p = {
  stats: {},
  flags: new Set([...(pi.flags || []), ...(opts.flags || [])]),
  lifeFlags: [...(opts.flags || [])],
  debt: 0,
  history: [],
  entered: [],
  stageCounts: { childhood: 0, student: 0 }   // ← 新增
};
*/

// ---------- 3. 在 current() 函式內，進入事件時計數 ----------
// 在 current() 裡，當確定要進入某個事件（非 pool_、非 __EVAL__）時加入：
/*
function onEventEnter(event) {
  if (!event || event.id?.startsWith('pool_')) return;
  const stage = getStage(event.age ?? p.age);
  if (stage === 'childhood' || stage === 'student') {
    p.stageCounts[stage] = (p.stageCounts[stage] || 0) + 1;
  }
}
// 在設定 p.age = event.age 之後呼叫 onEventEnter(event);
*/

// ---------- 4. 階段停留判斷 ----------
function shouldStayInStage(currentAge, nextAge) {
  const cur = getStage(currentAge);
  const nxt = getStage(nextAge);
  if (cur === nxt || cur === 'adult') return false;
  const rule = STAGE_MIN[cur];
  if (!rule) return false;
  const count = p.stageCounts[cur] || 0;
  return count < rule.minEvents;
}

// ---------- 5. 修改隨機池選擇邏輯 ----------
// 找到處理 pool_ 或 random next 的地方，替換成類似下面的過濾：
function filterByStage(candidates, currentAge) {
  if (!candidates || !candidates.length) return candidates;
  const stay = [];
  const same = [];
  for (const c of candidates) {
    const age = c.age ?? currentAge;
    if (shouldStayInStage(currentAge, age)) {
      if (getStage(age) === getStage(currentAge)) same.push(c);
    } else {
      stay.push(c);
    }
  }
  // 未達最低次數時，優先留在同階段
  if (same.length && (p.stageCounts[getStage(currentAge)] || 0) < (STAGE_MIN[getStage(currentAge)]?.minEvents || 0)) {
    return same;
  }
  return stay.length ? stay : candidates;
}

// ---------- 6. 在決定下一個事件時使用 ----------
// 範例：原本可能是
//   const nextId = randomChoice(...);
// 改為先過濾：
/*
const rawCandidates = /* 原本的候選事件陣列 */;
const filtered = filterByStage(rawCandidates, p.age);
const chosen = filtered[Math.floor(Math.random() * filtered.length)];
*/

// ---------- 7. 除錯用（可選） ----------
function debugStage() {
  console.log('[Stage]', {
    age: p.age,
    stage: getStage(p.age),
    counts: p.stageCounts,
    childhoodNeed: STAGE_MIN.childhood.minEvents,
    studentNeed: STAGE_MIN.student.minEvents
  });
}

// ============================================================
// 整合檢查清單
// ============================================================
// [ ] p 初始化時有 stageCounts: { childhood: 0, student: 0 }
// [ ] 進入非 pool_ 事件時呼叫計數（onEventEnter）
// [ ] pool_ / 隨機 next 選擇前用 filterByStage 過濾
// [ ] 童年未滿 6 次時不會跳到 13 歲以後的事件
// [ ] 學生未滿 7 次時不會跳到 23 歲以後的事件
// [ ] 出社會階段不受限制
// ============================================================
