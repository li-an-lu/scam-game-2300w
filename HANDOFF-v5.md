# HANDOFF v5（v1.2 整合）— 2026-10-23 Asia/Taipei
`python3 build.py --all` → EXIT 0（logs/build_r27.log，約 2 分鐘）。產物已複製到 web/。grok-proposal.md 未動。

## 1. 檔案
- 新增原文：expansion-r4.md、expansion-flagtext.md、expansion-childhood-fix.md（Leo 原文）；先前已有 expansion-r2/r3.md、research-romance-marriage-parent.md
- 改動的產生器：gen_life.py（81 事件、6 結局）、gen_investment.py、gen_mule.py、gen_shopping.py、gen_family.py（romance/marriage/parent）、gen_achievements.py（只新增）
- validate.py：跨線檢查與前提檢查改為只展開「非純插話」flag，flag 數 >4/>6 時改線性抽測（全關、全開、單開、單關），避免 2^n 卡住
- 備份：/tmp/*.pre_v12.py、/tmp/*.pre_tune.py、/tmp/validate.pre_v12.py、/tmp/engine.pre_pool.js
- 分段 log：logs/

## 2. 給程式碼的機制（JSON 規格 → web/engine.js 狀態）
| 機制 | 規格位置 | engine.js |
|---|---|---|
| 開局骰子 | player_init.stats.*.init_range：存款 80k–200k、警覺 15–45、人際 30–70、心理 35–80 | 已有（L74 init_range） |
| 心理歸零 → END_LIFE_HALTED | meta.early_halt：每次選擇套用後，心理 ≤ 0 就立即結束；詐騙線會先演完，回人生線前再判定 | **未實作，需補** |
| 時間回復 | meta.mental_time_recovery.per_year = **2.6**（v1.2 從 1.8 調高）× 年齡差；詐騙線內不回復 | **未實作，需補** |
| 進線前回復 | scam_integration.pre_entry.mental_recovery +10 | 已有（L188） |
| 心理磨耗 | common.apply_mental_wear（-2） | 已經寫進 JSON |
| 事件池（童年/成人） | router:true + random:true 會在可用選項中均勻抽一個；pool_* 決定可選區塊出不出現（比例見 meta.event_pool.childhood）；VAR 場景變體；honesty↔slurpee 會互換順序 | **已改**（L134） |
| 條件分流 | router 沒有 random 時取第一個符合 require 的選項（route_sleep、route_family_talk、route_loan_use） | 已有 |
| flag 文字變體 | event.text_variants[{when:{flags_all,flags_none},text}] | **已改**（L142） |
| 結果變體 | choice.outcome_variants；用選擇「之前」持有的 flag 判斷；只放在正確選項，錯的選項仍是原本的被騙結果 | **已改**（L171） |
| 跨線「你想起以前…」 | 各詐騙線的 cross_line_modifiers add_interrupt；flag 已登記在 life meta.cross_line_flags | 已有（L24） |
| 新線 romance/marriage/parent | script-romance/marriage/parent.json；romance 與 parent 為必出；人生線延長到 50 歲 | 照 scam_integration 規格；UI 請確認已經列出 |
| 成就 | achievements.json 107 筆（新增 10 筆 ACH_SPOT_*：sticker、toy、permission、points、rent_deposit、customs、insurance、gold、loanuse、sleep），屬收集型，事件可能抽不到 | UI 讀 json |

## 3. v1.2 採用
- 童年：移除 chick_seller/chick_result、school_gate；新增 sticker_trade(7)、toy_seller(8)、teacher_permission(10)、points_help(12)；group_buy 移到 11 歲、200 元；card_trade 改為 5 張；ice_lend 併入 lend
- 成人：loan_use(20)、rent_deposit(22)、customs_fee(25)、fake_insurance(32)、sleep_issue(34，附 1925/1995/165)、family_talk(36)、gold_delivery(40，-80000，設計假設，原稿 -500000)；pool_mule_variant(17) 會設定 mv_* 五種車手入口之一
- flag 文字：新增 fake_sticker、fake_toy、fake_permission、points_not_returned、paid_group_buy、chased_lottery、mv_*，對應後面事件的「你想起以前…」插話與 outcome_variants
- 修正：8591 → 「交易平台」；_rewire 會一併改 random outcomes 的 next（原本 family_talk 到不了）
- 調分布（全部標為設計假設）：per_year 1.8→2.6；gold -150000→-80000；investment bank_counter[1] 心理 -7→-14、withdraw_block[2] -7→-10、pressure[1] -15→-18；parent 先罵 -8→-10、出錢壓下 -12→-14
- 來源：寫手新增的內容標「寫手提供，待查證」；沒有放未查證的性影像處理中心號碼

## 4. 待決
- flagtext 沒有後續事件可接的列：1、2、3、4、5、6、7、10、13、15、16、17、18、20、21、22、25、26、29、30（2 和 30 與 hongbao_result 揭曉衝突）
- r4 尚未建立：aftermath_police、END_GOLD_LOST、END_DELIVERY_MULE（後者與 mule END_ACCOUNT 重疊）
- 已合併、不另建：second_delivery/recovery_scam → second_scam；guess_who_morning/bank_counter_elder → guess_who；fake_police_call → fake_police；investment_group → 投資線
- 警覺小加成（flagtext 選配）未做
- 邊界值：investment END_COLLAPSE 2.0%（N=20000）剛好在下限，再改投資線心理數值要重測
- engine.js 需補 early_halt 與 per_year 回復，網頁分布才會等於模擬結果

## 5. 分布（combined.py N=20000，seed 42；N=10000 確認相同範圍）
- 人生：STRETCHED 36.3%、**STEADY 31.8%**、SAVED 10.9%、**HALTED 10.7%**、GONE 7.5%、RECORD 2.7%
- 車手（進入 41.9%）：RESCUED 31.3、REFUSE 28.3、ACCOUNT 23.4、STOPPED_ALONE 5.2、RECORD 5.2、CONVICTED 3.7、CUT_OFF 2.9
- 網購（68.2%）：CS_DRAINED 25.9、SAFE 25.2、TICKET_LOST 22.9、SMALL_FEE 20.9、SILENT_COLLAPSE 5.1
- 投資（36.6%）：SMALL_LOSS 38.3、EARLY 38.3、ALL_LOST 6.4、BROKE 6.1、DEBT 4.6、FAMILY_RIFT 4.2、COLLAPSE 2.0
- 交往（94.7%）：CHECKED 31.2、STOPPED 24.0、DEEP 21.0、HOTLINE 15.2、SISTER 6.1、COLLAPSE 2.6
- 婚姻（93.6%）：ANNUL 23.7、SILENT 21.4、DIVORCE 16.8、LEGAL 16.4、PAID 15.3、COLLAPSE 6.4
- 家長（89.4%）：OPEN 26.3、SILENT 25.2、HUSH 25.0、BROKE_CYCLE 20.9、COLLAPSE 2.6
- 單跑人生線（不經詐騙線，只供除錯）：STEADY 44.2%；目標以合併模擬為準（r25 時這個數字是 54.3%）
