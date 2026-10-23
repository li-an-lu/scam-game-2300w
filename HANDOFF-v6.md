# HANDOFF v6（2026-10-23 21:45 台北時間）

## 文件
- 全劇本文字：STORY-TEXT-ALL.md／STORY-TEXT-ALL.docx（tools/export_story.py 產生；目錄、固定必出 vs 隨機池、131 事件、跨線插話、結局＋案件卡）
- 建置 log：logs/build_v6b.log（EXIT 0）；組合模擬：logs/c_v6a.log（N=3000，調參前）、logs/c_v6b.log（N=10000，通過）

## B 改動
- common.py：GAME_TITLE="2300萬分之1"、set_title()；各 gen 存檔前呼叫，原「…：X」移到 meta.subtitle
- gen_achievements.py：ACH_LIFE_CLEAN40.unlock.min_age_lived=40（僅此一項修改）
- gen_family.py：romance/marriage/parent 結局案件卡依 url 對應 research-romance-marriage-parent.md 列編號 → story_id=research_R#/M#/K#；查不到時 story_id 與 url 標「待查」（目前全部都對上了）。K9（未查證的性影像處理中心專線）沒有放進去
- v6.1 人工核對（gen_family.py `_FIX`，摘要只取研究列文字）：
  - END_RM_DEEP：R4（未匯出案）→ 換成 R2（高雄、非官方 App 儲值、損失約 320 萬）
  - END_MR_COLLAPSE：維持 M2，摘要改成 M2 的內容（偽簽連帶保證人）
  - END_MR_PAID：維持 M1，摘要改成 M1 的內容（婚後討債上門、丈夫隱瞞婚前債務）
  - END_MR_DIVORCE：M3（假單身借款）→ 換成 M2（偽簽保證人、提告判刑），跟原本的摘要一致
- card_trade 的情境變體由 7張 改成 5張（ETtoday 原標題的 7張保留，那是來源原文）

## C 新事件（gen_life.py「v2.0（v6）」區塊，meta.v6_additions）
童年（隨機池 p=0.5，有標註的除外）：c_lost_wallet 6 (p .67)、c_share_lunch 6、c_pinky_promise 7（必出）、c_temple_fair 8、c_stranger_pickup 9（必出）、c_lost_kid 9、c_survey_gift 10、c_chain_msg 11、c_online_friend 11 (p .67)、c_donation_box 12、c_link_drink 13、c_friend_repay 14、c_grandma_call 14（必出）
成年里程碑（必出）：a_move_out 21、a_first_salary 23；part_time／student_loan／rent 補上具體場景文字（判定沒動）
真誠線：a_help_stranger 27（必出）、a_still_kind 37（被騙過的人經 family_talk 才會到；附 1925/165）
伏筆回收：lend←kid_kept_promise（text_variant）／kid_lent_friend（outcome_variant）；lend5←kid_shares；elder←kid_verified_for_grandma；fake_police←kid_trusts_adult；a_help_stranger←kid_helps；a_still_kind←kid_kept_promise
來源：一律標「原創情境（依…）」（165、警政署兒少安全、衛福部公益勸募、勞基法、租賃條例）；部分 url 標 url_status 待查
最小修正：新事件不設 checks_first，警覺增幅上限 +2，心理/人際正向增幅上限 +1（不這樣的話 investment/mule/romance/parent COLLAPSE 會跌破 2%）

## 分布（build 內建 combined）
人生：STRETCHED 35.9／STEADY 31.2／HALTED 12.2／SAVED 10.7／GONE 7.3／RECORD 2.7
最低：投資 COLLAPSE 2.2、車手 CUT_OFF 2.6、交往 2.6、家長 2.6（都在邊緣，改數值前要重跑）；最高：投資 SMALL_LOSS 39.0


## v6.1（2026-10-23 22:30 台北時間）
- 遊戲過程中不再出現求助電話：a_still_kind、sleep_issue 的結果文字移除了 1925／1995／165 專線。求助電話只留在結局（END_ROUTER 的 help）。另外，劇情裡「打165確認」這類玩家行動選項還保留（那是遊戲機制，不是附加的專線資訊）
- 新事件來源全部換成可以開啟的具體頁面：刑事局〈猜猜我是誰〉、刑事局〈釣魚簡訊〉、警政署兒童網站〈自我保護〉、金門縣警察局〈預防教育篇〉（暗語）、衛福部〈捐款獻愛心注意事項〉、勞動部〈工讀生權益〉、租賃條例第7條、聯合新聞網〈諮商心理師：羞愧、自責〉。設計假設類事件與套圈圈事件找不到具體來源，改成 165 首頁，並在 note 註明是泛用頁。新事件已經沒有「待查」字樣（寫手來源的「寫手提供，待查證」照舊保留）
- 建置：logs/build_v61.log EXIT 0；分布與 v6 相同（只改了文字），所有結局都 ≥2%
