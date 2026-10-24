# HANDOFF v8（內容/資料）— 給程式碼
分支：`v8`（從 v8-engine b075f84 開出），只 commit 本地，未 push、未部署。grok-proposal.md 沒動。
資料欄位都照 HANDOFF-v8-engine.md 的規格。

## 資料怎麼產生
`python3 build.py --all` 會依序跑：
1. gen_*.py
2. `v8/apply_v8.py scripts`
3. 驗證器
4. gen_stage_pool
5. `v8/apply_v8.py pool`
6. `apply_v8.py manifest`
7. `v8/validate_v8.py`
8. 複製到 web/

v8 的內容都放在 `v8/content.py`，規則放在 `v8/rules.py`。腳本是冪等的，重跑不會重複套用。

## 欄位
- **年齡**：事件、選項、stage-pool 項目都有 `min_age`/`max_age`。
  - 人生線：依階段範圍（0–12 / 13–22 / 23–99），再依關鍵字提高下限。例如打工、薪水 15 歲以上；正職、租屋、信用卡 18 歲以上；婚育 22 歲以上。
  - 詐騙線：用進入的年齡範圍。
  - manifest 的 `year_filler` 改成 `{text,min_age,max_age}` 物件。
  - **v1 年齡 bug 的根因**：填空句原本沒有依年齡過濾，1–2 歲也會出現「出國旅行」這種句子。
- **versions**：part_time、student_loan、rent、a_move_out、a_first_salary 這 5 個固定事件，每個各有 3 版本。用 `localStorage.storyVersions` 記錄。
- **數值**：`display_max:10`，畫面顯示 round(v/max×10)。所有變化量都是 10 的倍數，由 r10 轉換：
  - 警覺/人際：.5 往上進位。
  - 心理：.5 往下捨去，用來保住原本的停止率。
  - stage-pool 原本 1 單位＝3 點，改成 10 點。
- **meta.rethink**（人生線，詐騙線沿用）：
  - 觸發門檻：警覺 60、人際 70。
  - **probability 0.6**。
  - 「正確」選項都標了 `rethink:false`，所以只有選錯時才會提醒。
- **心理歸 0**：`early_halt.immediate_in_scam=true`。
- **mood_line**：13 個關鍵事件的每個選項都有。
  - 原本有全域 `meta.mood_lines` 備援，**已拿掉**：每個小選擇都多一次點擊，太拖。
- **關鍵選擇**：13 個事件都改成 4 選項，保留 Leo 原有的選項，再加 2 個陷阱選項。選項標籤 ≤15 字，不劇透。原文保留在 `text_v7`/`outcome_text_v7`。
- **加害者線**：新增 perp_account_ask、perp_consequence（21 歲，接在 a_move_out 後面），以及結局 END_ACCOUNT_LENT。
  - 依據都是已查證的判決與法條，有 URL（洗錢防制法 §22、刑法 §339-4 相關、民法 §185、新聞判決報導）。
  - 不含任何操作細節。
- **結局卡**：6 個 lie_endings 的首句改成通用句，原文保留在 `text_v7`。

## 請程式碼處理
1. `meta.rethink.friend`：人際高時，改由「朋友」說出提醒。資料裡已經寫好，引擎還要支援（目前會顯示一般提醒文字）。
2. 我改到的引擎/驗證檔，請 review：
   - `web/ui.js`：填空句依年齡過濾，可以接受字串或物件。
   - `validate_stage_pool.py`：來源全部 verified 而且有 URL 時，豁免「待查證」標籤。
   - `build.py`：加上 v8 的掛鉤。
3. mule 的門檻調整：
   - 孤立：人際 ≤20。
   - has_support：人際 ≥30。
   - 用來讓 END_CUT_OFF 回到目標範圍 2–40%。
4. validate_v8 的警告（Leo 原文，我沒改）：
   - hongbao 只有 3 個選項。
   - 以下選項文字含 165：investment 的 date_refuse_video、bank_counter；mule 的 teen、job_offer；shopping 的 ticket_blocked、cs_call；romance 的 rm_ask_invest、rm_ask_loan、rm_ask_sick、rm_push。
   - 規則是求助專線只放在結局，請 Leo 決定要不要改。

## 待查證（沿用舊內容）
- customs_fee 的來源。
- lie_endings 中標註「寫手提供」的依據。
- 立法院報告標 verified:false 的部分。
- v8 新增的加害者內容全部已查證。

## v8.1（公開版清理）
- END_ACCOUNT_LENT force:true；10 個含 165 選項改為動作式文字，outcome 不含專線號碼（validate_v8 改為 ERR）。
- hongbao 第 4 選項「交給說會讓錢變多的表哥」+ mood_lines。
- 未查證 stats display:false；case_card 開發註記清空；14 個 lie_endings 待查證 case/source_note 移到 *_v7。
- validate_stage_pool.py 改讀 case_v7/source_note_v7。
- **待程式碼**：套用 v8/patches/ui-public.patch 到 web/ui.js（移除示範投稿、假計數器、除錯 flags、管理匯入改 ?review=1、隱藏待查證來源）。
