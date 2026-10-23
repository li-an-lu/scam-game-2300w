# 成就系統 v1（achievements.json）— 給「程式碼」的實作說明

產生：`python3 gen_achievements.py`；驗證：`python3 validate.py achievements.json`；`python3 build.py --all` 會自動跑兩者並複製到 `web/achievements.json`。
不要手改 achievements.json，改 gen_achievements.py 後重 build。

## 欄位
| 欄位 | 說明 |
|---|---|
| id | 唯一鍵，也是 localStorage 內的鍵 |
| category | `ending_codex` 結局圖鑑／`red_flag` 破綻辨識／`life` 人生成就 |
| name | ≤10 字，不劇透 |
| description | 解鎖後顯示的說明 |
| hidden | true＝未解鎖前只顯示「？？？」與 name，不顯示 description |
| tone | `positive`／`record`（受騙結局，用「圖鑑記錄」語氣，**不要播慶祝動畫/音效**）／`serious`（入獄、前科、崩潰、家庭破裂等：靜態顯示，並在詳情頁顯示該結局的 help_resources） |
| unlock | 結構化條件，見下 |
| source | 自動引用現有事件/結局的 sources（`ref`=`線:事件或結局id`）。沒有任何達成率數字，前端也**不要**自己算「X% 玩家達成」 |

## unlock 判定
所有引用格式：`線:id`，線＝`life|mule|shopping|investment`。
- `scope:"run"`：只看**同一輪人生**（一次 40 歲遊玩，含插入的詐騙線）的狀態。
- `scope:"collection"`：看**跨局累積**的圖鑑（localStorage 已記錄過的結局）。

條件全部 AND：
- `requires_endings`：清單內每個結局都要達成（run＝本輪 scam_history / 人生結局；collection＝曾經達成過）。
- `requires_any_endings`：至少一個（如「活到 40 歲」＝任一人生結局）。
- `requires_flags`：`線:flag` 在本輪被設過。詐騙線內部 flag 以該線 internal_flags 判斷；`life:` flag 含 return_map 帶回的（scam_money_lost、criminal_record…）。
- `requires_choices`：本輪玩家在 `line/event` 選了第 `choice_index` 個選項（`text` 供核對；random:true 選項在抽 outcome 前就算選了）。
- `forbids_flags`／`forbids_endings`：本輪不得出現。

建議實作：
```js
function check(a, run, store){            // run: {endings:Set, flags:Set, choices:Set("line:event:idx")}
  const u=a.unlock, E=u.scope==="collection"? new Set(store.endings): run.endings;
  return u.requires_endings.every(x=>E.has(x))
    && (u.requires_any_endings.length===0 || u.requires_any_endings.some(x=>E.has(x)))
    && u.requires_flags.every(x=>run.flags.has(x))
    && u.requires_choices.every(c=>run.choices.has(`${c.line}:${c.event}:${c.choice_index}`))
    && !u.forbids_flags.some(x=>run.flags.has(x))
    && !u.forbids_endings.some(x=>run.endings.has(x));
}
```
判定時機：每個詐騙線結局、人生結局（END_LIFE_*）出現後各跑一次；`forbids_*` 類（如「四十不受騙」）只在人生結局時判定。

## 跨局持久化（localStorage）
鍵 `scamgame.achievements.v1`，值：
```json
{"version":1,"endings":["mule:END_REFUSE"],"unlocked":{"ACH_SPOT_OTP":"2026-10-23T15:00:00+08:00"}}
```
- 先把本輪結局併入 `endings`（去重），再判定所有未解鎖成就，新解鎖寫入 `unlocked`。
- 解析失敗或 version 不符：保留舊值另存 `…v1.bak`，重建空物件，不要讓遊戲崩潰。
- 提供「清除紀錄」按鈕（需二次確認）。不上傳任何伺服器。
