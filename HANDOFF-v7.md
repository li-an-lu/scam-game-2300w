# HANDOFF v7（未 push、未部署）

## 新增／修改檔案
- 新增：gen_stage_pool.py → stage-pool.json（含 web/）、validate_stage_pool.py、web/stage.js
- 修改（只有新增）：build.py（--all 會跑上面兩支並複製）、gen_achievements.py（v7 區塊）、validate.py（認得 stage-pool 的 flag 與結局卡、requires_flags_min）、web/ui.js、web/index.html（stage.js、Noto Serif TC）、web/style.css（檔尾 v7 區塊）
- 沒有動：grok-proposal.md、Leo 的 md／json、人生線與詐騙線劇本、結局比例

## 1–6 項（之前 → 之後）
1. 核心謊言 flag 與結局權重
   - 之前：heard_stranger、obey_authority 沒有任何謊言會設定，14 張結局卡沒有接上。
   - 之後：6 個核心 flag 都能觸發（用關鍵字連結：虎姑婆→stranger、主管／公司像家→obey…）。
   - 每張卡有 base／boost／requires 權重。重池或輕池依「這一生有沒有實際損失」決定。
   - 結局頁新增「這一生的謊言回顧」卡，「回顧連結」只引用這一局實際出現過的謊言。
2. 階段抽池
   - 之前：Leo 的 STAGE_MIN 沒有接上。
   - 之後：童年 4–12、學生 13–22、出社會 23–42，各抽 6 則；謊言 ≤3，正負約 1:1。
   - 冷卻：跨階段也不會連續兩則謊言。
   - 13 歲有「長大」心態轉場：童年正面 ≥3 → 警覺+3、心理+3；謊言 ≥3 → 警覺−3。
   - 正面選項會埋伏筆 flag，進入詐騙線時回扣一句。
   - 被動謊言的心理下限是 1，不會因被動事件而提前結束。
3. 成就：107 → 131。
   - 新增 Leo 的 12 個（補上 life: 前綴與來源，SPOT_AUTHORITY 改對應 fake_police）。
   - 補 7 張卡的圖鑑。
   - 新增 CORE3、ALMOST_FAMILY、TOLD_DESPITE，以及隱藏成就 ALL_CORE、QUIET_STORM。
4. 分布檢查：已取消（Leo 更正）。不跑大量模擬、不做分布統計。
5. 分享短句
   - 結局可留一句，存在 localStorage.sharedPending。
   - 開始頁輪播只顯示 localStorage.sharedApproved；沒有匯入時顯示示範短句，並註明「非真實投稿」。
   - 管理用：可以匯入 JSON 審核清單，也可以匯出待審短句。
6. 視覺延伸：開始頁的暗金／酒紅基調套到事件卡（新增「童年・大人的話」等標籤）、正面卡、回扣卡和結局卡。

## 開始頁還原清單
meta 行、襯線大標（紅色 1）、副標、兩個動態數字、事實輪播、說明段落、四數值「隨機」格、無壓力切換、「開始這一生 →」、成就按鈕、頁尾句、分享經驗輪播（← → 和圓點）、備註、色盤與字體。

## 規則處理與待決
- 動態數字
  - 設計稿的 1,284 和 47 件／天是虛構的。
  - 現在「被說出的小謊」標示「示意動畫，非實際統計」。
  - 案件數依已查證的每天約 359 件 × 今日已過時間換算，並附 165 打詐儀表板來源。
- 事實輪播：第一則已查證，其餘標示「寫手提供，待查證」。「2025 財損近 900 億」未查證，沒有放入。
- 示範短句：帶縣市與年齡，是示範，已標示。
- 14 張結局卡
  - 沒有網址，來源為「寫手提供，待查證」，END_ALMOST 的「約六成」未查證。
  - 卡片文字是固定句，例如「你記得老師說過…」，那句謊言不一定在這一局出現過。實際出現過的謊言另外列在「回顧連結」。建議 Leo 改寫成通用句。
- 卡片的 help 欄位沒有顯示。救助專線維持只在原本的結局區出現，遊戲過程中沒有。K9 沒有放入。
- design-adjustments-final.md 寫「負面不做上限／視覺延伸暫不處理／分享暫不實裝」，與 Leo 最新指示衝突，這次依最新指示實作。請 Leo 確認。
- 單位：Leo 的 1 單位 = 3 點（0–100 制）。
- 選項都 ≤15 字；沒有品牌、死亡或犯罪細節（validate_stage_pool 有檢查）。

## 驗證
- build --all：BUILD ALL OK（log 在 logs/build_v7.log）。
- 瀏覽器實玩一局（Playwright，log 在 logs/play_v7.log）：走到結局，沒有 JS 錯誤；謊言卡、正面卡、心態轉場都出現過；回顧卡是 END_SHOPPING_LINK，引用 30 歲主管那句。
- 截圖在 /workspace/scam-game/shots-v7/：start、event-lie、event-pos、event-mindset、event-life、ending、ending-lie-review。
- 加 ?stage=0 可以關閉階段抽池。
