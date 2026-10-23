# 階段最低事件次數整合狀態

完整修改片段已存於 `engine-stage-min-complete.js`。

## 已整合
- `STAGE_MIN` 常數（童年最少 6、學生最少 7）
- `getStage()` / `shouldStayInStage()` 輔助函式
- `create()` 的 `p` 初始化加入 `stageCounts: { childhood: 0, student: 0 }`

## 待完整接入（需依實際事件流調整）
- 進入非 pool_ 事件時計數（`onEventEnter`）
- 隨機池／next 選擇前用 `filterByStage` 過濾
- `createCombined()` 同步加入 `stageCounts`

目前常數與資料結構已就位，實際停留邏輯仍需依 `current()` 與 pool 選擇路徑補完，避免破壞現有流程。
