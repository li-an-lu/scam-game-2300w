# HANDOFF v8 引擎（分支 v8-engine，未 push、未部署、未跑測試）

所有欄位都是選填；缺少時行為與 v7 相同。

## 1. 年齡過濾
- 事件、選項、stage-pool 的 lies／positive 都可加 `min_age`、`max_age`（含端點）。
- 事件年齡不符 → 跳過，前往 `skip_next`（沒有就用第一個選項的 `next`）。
- 選項年齡不符 → 不顯示。stage-pool 項目以其 `age` 判斷。

## 2. 固定劇情 3 版本
```json
{ "id": "EV_X", "age": 25, "text": "預設", "choices": [...],
  "versions": [
    { "id": "A", "text": "版本A", "choices": [...] },
    { "id": "B", "text": "版本B" },
    { "id": "C", "text_variants": [...] } ] }
```
- 版本裡寫的欄位會覆蓋事件本身（沒寫的沿用）。`id` 省略時自動為 v1、v2…。
- 紀錄：`localStorage.storyVersions = {事件id: [玩過的版本id]}`。還有沒玩過的就只抽沒玩過的（前三輪不重複），三個都玩過後隨機。
- 本局抽到的版本在 `player.versions`。

## 3. 數值 0–10、再想一下、心理歸零
- 有 `max` 的數值（警覺／人際／心理）畫面顯示 `round(值/max×10)`；`player_init.stats.X.display_max` 可改 10。內部仍是 0–100。變化數字同樣換算（非零變化至少顯示 1），灰色字。
- 提醒彈窗設定放 `script-life.json` 的 `meta.rethink`（詐騙線沒寫就用人生線的）：
```json
"rethink": { "stats": {"警覺": 70, "人際": 70}, "probability": 0.3,
             "text": "要不要再想一下？", "back": "再想一下", "go": "就這樣決定" }
```
  任一數值 ≥ 門檻（內部 0–100 值）時，依機率跳出。沒有 `meta.rethink` 或 probability 未給＝0，不會出現。
  覆寫：`event.rethink_probability`、`choice.rethink_probability`、`choice.rethink_text`；`choice.rethink: false`＝此選項不提醒（建議用在安全選項）。
- 心理歸零：沿用 `meta.early_halt`。v8 新增詐騙線中途歸零也立刻結束（`early_halt.immediate_in_scam: false` 可關閉）。v7 的被動事件心理下限 1 仍保留。

## 4. 4 個選項
- CSS 已調整到 320px 可直排 4 顆。選項文字建議 ≤15 字。

## 5. 選後狀態畫面（mood_line）
- 結果卡按「繼續」後顯示一句，點一下才進下一步。來源優先序：
  1. `choice.mood_line`（字串或陣列＝隨機一句；stage-pool 正面選項也可用）
  2. `event.mood_line`
  3. `meta.mood_lines`: `[{"stat":"心理","max":30,"text":["..."]}, {"max":100,"text":"..."}]`（依序取第一個 值≤max）
- 都沒有就略過狀態畫面。

## 未決
- 換算後的變化會四捨五入（例 +3 → +0.3 → 顯示 +1），企劃若要精準請改用 10 的倍數。
- 超過 4 個選項（例如跨線解鎖多加一個）不會被截掉，只是排更長。
- 引擎內舊的 STAGE_MIN 規則仍未清理（v7 遺留）。
