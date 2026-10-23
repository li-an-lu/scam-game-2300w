# 2300萬分之1 — 網頁試玩版

純靜態檔案（HTML/CSS/JS + JSON），無建置步驟，所有路徑皆相對，可放在任何子資料夾（GitHub Pages、Netlify、Cloudflare Pages 等）。
本機測試：`python3 -m http.server 8000` 後開 http://localhost:8000 （直接雙擊 file:// 會因瀏覽器限制讀不到 JSON）。

## 檔案
- `manifest.json`：劇本線清單、出生池、分配權重（weight / weight_mods / conditions）、year_filler。新增劇本線只要加一筆。劇本 JSON 若有 `entry` 欄位（同格式）會優先使用。
- `script-*.json`：由上層 `gen_*.py` 產生，**不要手改**；重新產生後複製過來即可。
- `engine.js`：通用引擎（條件、stat_flags、__EVAL__、priority 結局判定、出生分配）。
- `ui.js` / `style.css` / `index.html`：介面。

## 測試用參數
- `?line=mule` 指定劇本線（跳過隨機分配）
- `?script=xxx.json` 只載入單一劇本
- `?manifest=xxx.json` 換清單

## 外部依賴
Google Fonts（Noto Sans TC）。離線時退回系統字型。

## v4（本機，未重新部署）
- 流程：人生線（script-life.json，0–50 歲，揭曉事件自動顯示結果）→ 人生小結（結局標題／格子／破綻回放／帶走的經驗）→ 依 manifest 隨機分派詐騙線，人生 flag（meta.cross_line_flags）經 cross_line_modifiers 套用。
- 同步劇本：`python3 ../build.py && python3 ../validate.py && python3 ../validate.py ../script-life.json --sample`，再 `cp ../script-*.json .`（build.py 不會複製到 web/）。
- 網址參數：`?line=investment|mule|shopping`（直接進該線，跳過人生線）、`?life=0|1`、`?lifefile=`、`?flags=a,b`（除錯注入人生 flag，跳過人生線）、`?fast=1`（聊天加速）、`?nopressure=1`（不顯示倒數）。
- 引擎：Engine.applyModifiers 對齊 common.apply_modifiers；結局文字變體對齊 common.pick_text；requires_flags／forbids_flags 違反時 console.warn，並存在 G.player.premise。

## v5（2026-10-23）
- 遊戲名稱改為《2300萬分之1》。
- 開局數值：meta.initial_stats_roll（均勻整數骰＋temperament）。
- 心理 ≤ 0：meta.early_halt → END_LIFE_HALTED（人生線每步後檢查；詐騙線演完才檢查）。
- 時間回復：meta.mental_time_recovery.per_year（2.6／年，只在人生線前進時）。
- 事件池：random 路由（均勻抽），合併模式中路由也算一步（可插詐騙線、檢查停止）。
- 新線：romance／marriage／parent（scam_integration 插入；manifest weight 0）。
- 成就：achievements.json，localStorage「ach」，首頁「成就」按鈕可看清單。
