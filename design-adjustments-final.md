# 設計調整最終版（依確認方向）

## 1. 核心謊言旗標（只加 flag，5～6 句可被引用）

只為下列核心謊言加 flag，其餘被動謊言維持純敘事（心 -1），不加 flag。  
負面密度維持原設計，不做上限。

| Flag | 階段 | 核心敘事 | 主要連結結局 |
|------|------|----------|--------------|
| `heard_stranger` | 童年 | 不要隨便跟陌生人說話 | END_TRUST_LONG |
| `heard_police` | 童年 | 不去的話警察會來抓你 | END_AUTHORITY_CALL |
| `heard_everyone` | 學生 | 別人都在補／別人都在做 | END_GROUP_PROFIT |
| `said_its_fine` | 出社會 | 跟家人說「還好」 | END_DONT_WORRY、END_FAMILY_IMPERSONATE |
| `heard_miss_chance` | 出社會 | 現在不試以後就沒機會 | END_INVEST_SMALL、END_GROUP_PROFIT |
| `obey_authority` | 跨階段 | 不要搞複雜／照做就好 | END_SHOPPING_LINK、END_CUSTOMER_SERVICE、END_JOB_FEE |

---

## 2. 正面事件輕微伏筆（有驚無險承接）

### p_remind_family　｜　有人提醒你
*隨機池*
**情境：**
> 你正在考慮要不要轉那筆錢。朋友傳訊息：「先打給家人確認一下。」
**選項：**
1. 【先打給家人】 心+1 警+2　旗標：`reminded_family`
   - 結果：你打了。對方說先不要。你把頁面關掉。
2. 【說再看看】 心+0
   - 結果：訊息留著，你沒有立刻打。

### p_colleague_pause　｜　同事多問一句
*隨機池*
**情境：**
> 同事說：「你有跟家人講過嗎？」
**選項：**
1. 【後來有講】 心+1 人+1　旗標：`talked_family_work`
2. 【沒有講】 心+0

---

## 3. 主要結局前置條件與權重

| 結局 | 基礎權重 | 加強條件（有 flag 時） | 備註 |
|------|----------|------------------------|------|
| END_TRUST_LONG | 8 | `heard_stranger` → 18 | |
| END_AUTHORITY_CALL | 6 | `heard_police` → 16 | |
| END_GROUP_PROFIT | 10 | `heard_everyone` 或 `heard_miss_chance` → 20 | |
| END_DONT_WORRY | 8 | `said_its_fine` → 18 | |
| END_INVEST_SMALL | 10 | `heard_miss_chance` → 18 | |
| END_SHOPPING_LINK | 12 | `obey_authority` → 16 | |
| END_ALMOST | 6 | 有 `reminded_family` → 22 | 輕度池 |
| END_QUIET | 15 | 無核心負面 flag → 25 | 輕度池 |
| END_HELPED_OTHERS | 4 | 有提醒相關 flag → 12 | 正向輕度 |

**分流規則：**
- 高損失結局與輕度結局（ALMOST／QUIET／HELPED）分開池子抽取。
- 有 `reminded_family` 時，強制將 END_ALMOST 加入輕度候選。
- 無核心 flag 時，提高 END_QUIET 比例。

---

## 4. 不採納
開始頁視覺延伸到事件／結局頁：暫不處理。

---

## 5. 過程型成就（已對應調整）

- 同一局觸發 ≥3 個核心謊言 flag
- 被提醒後聯絡家人並進入 END_ALMOST
- 在「不想擔心」情境選擇告知家人
- 觸發 ≥2 個核心 flag 後進入 END_QUIET（隱藏）
- 進入 END_HELPED_OTHERS

（分享句子相關成就已移除，暫不實裝）

---

## 6. 其他確認
- 負面過載：維持原密度，故意設計。
- 分享句子：暫不實裝，之後再議。
