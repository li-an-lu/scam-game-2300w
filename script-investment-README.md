# 投資詐騙線 劇本 v0.4

檔案：`script-investment.json`，由 `gen_investment.py` 產生。修改劇本時請改生成器再重新產生。

## 結構
- `meta`：標題、版本、內容原則與引擎說明
- `stats` / `stats_sources`：統計數字，每筆都有 `verified` 和來源
- `player_init`：四項數值（存款／警覺／人際／心理）的初始範圍、縣市池、家庭背景池、`start_event`
- `events[]`：`id, age, text, choices[{text, effects, next, flags{set, require}}], sources`
  - `next` 可以指向事件 id，也可以指向結局 id
  - `require` 裡以 `!` 開頭的 flag 代表「這個 flag 不能存在」
  - `next: "__EVAL__"` 表示到這裡進入結局判定（只出現在 `END_ROUTER`，它的 `router:true`，不會顯示給玩家）
- `endings[]`：`id, conditions, text, case_card, missed_red_flags, sources`
  - `case_card` 是改寫過、去識別化的真實案例，附原文連結

## 流程
出生（隨機縣市與家庭）→ 17 歲接觸股票影片 → 25 歲分兩條入口：
1. 交友軟體：對方不能視訊 → 主動談投資 → 推薦陌生 App
2. FB 廣告 → LINE 股票群組：群組裡有暗樁 → 助教私訊催促

兩條線之後會合：小額獲利而且能出金（誘餌）→ 加碼 → 出金受阻、被要求先繳費 → 施壓、借貸 → 銀行臨櫃關懷。

## 結局（5 個，詳見上表）
- `END_EARLY`：及早識破
- `END_SMALL_LOSS`：小額損失後止血
- `END_ALL_LOST`：報案了，但借貸後全部損失
- `END_DEBT`：借貸加碼，連行員的提醒也沒聽

## 結局判定（依 priority 檢查；fallback 是 END_SMALL_LOSS）
| priority | 結局 | 條件 |
|---|---|---|
| 1 | END_DEBT | 有 borrowed，而且（missed_bank_warning 或 mental_collapse 或 isolated）；觸發原因會用 reason_texts 顯示 |
| 2 | END_ALL_LOST | 有 borrowed |
| 2.5 | END_BROKE | 有 savings_depleted、沒有 borrowed（沒借錢，但存款歸零） |
| 3 | END_SMALL_LOSS | 有 stopped_loss，沒有 borrowed 也沒有 savings_depleted |
| 4 | END_EARLY | 有 spotted、沒有 savings_depleted |

## 驗證
執行 `python3 validate_investment.py`。它會檢查：
- JSON 合法
- 每個 `next` 都存在
- 沒有死路、沒有無窮迴圈
- 用初始數值範圍的兩端組合窮舉所有路徑，確認每個結局都至少能走到一次

## 原則
- 每一個事件都有 `sources`，內容取自 stories.json 的 #1–7、#23
- 只寫受騙的過程和後果，不寫任何可以照做的操作細節

## v0.3 共通規則（三條線一致，由 common.py 套用）
- **stat_flags**：進入結局判定前，引擎先依數值設定 flag：`savings_depleted`（存款≤0）、`mental_collapse`（心理≤20）、`isolated`（人際≤15）、`has_support`（人際≥20）。結局條件只看 flag，不直接看數值。
- **reason_texts**：結局畫面會列出玩家實際擁有的 flag 所對應的說明，讓玩家知道為什麼走到這個結局。
- **red_flag_texts**：每個 `missed_*` flag 都有一句顯示文字，「你錯過的破綻」依玩家實際的走法逐條列出；如果玩家一個都沒錯過，就顯示 `missed_red_flags`（通用版）。
- 所有 `verified` 都是布林值，原本的說明文字移到 `verify_note`；所有來源都有 url，不會是 null。
- 驗證：`python3 validate.py <json>`。初始存款會乘上（1+家庭背景的存款加成），其他家庭加成直接加減；另外也會檢查 null url、verified 型別、`missed_*` 是否都有顯示文字、結局條件是否直接用了數值。

## v0.4 新增欄位（沉浸呈現範例；只加欄位，v0.3 的判定邏輯和 ending_rules 都沒有變）
由 `gen_investment.py` 的 V4／ANCH／EV4／META4 定義，經 `common.apply_v4()` 套用。

### event
- `presentation`：`card | chat | notification | timeskip`。本版有 9 個事件是 `chat`，其餘是 `card`。
- `chat`：
  - `app`：只寫類型（`line_like | dating_like | shop_like | sms_like | phone_call | in_person`）。
  - `app_display_name`：虛構名稱，例如「聊聊 Chatto（虛構）」「心動 Spark（虛構）」。
  - `theme`：虛構外觀鍵（例如 `fictional_green_free`，前端不能使用真實 App 的配色）。
  - `contact {name, avatar, status}`：avatar 用占位剪影。
  - `messages[] {id, from, text, delay_ms, type}`：`from` 是 scammer／shill／player／system／teller；`type` 是 text／image／link。訊息只寫詐騙話術和受害者的反應，不寫可以照做的細節（連結一律以「（傳來一個陌生平台連結）」描述）。
- `interrupts[] {at, from, text}`：在 `messages` 中 id 等於 `at` 的那條訊息之後插入外部訊息（好友、媽媽）。
- `pressure {timer_s, can_disable, label}`：`timer_s` 至少 20 秒（本版為 25–30 秒），`can_disable` 一定是 true。
- `choices[].grid`：`green | yellow | red`，用來畫人生格子。自動計算：設定 missed_* 而且存款減少＝red，只設定 missed_*＝yellow，其餘＝green。

### 頂層
- `red_flag_anchors {missed_flag: [{event, message}]}`：結局回顧時，回到該事件的那條訊息畫紅框。8 個 missed_* flag 共 10 個錨點。

### ending
- `title`、`title_emoji`：結局稱號。
- `grid_color`：人生格子的最後一格。
- `share_text`：不劇透的分享文案。
- `share_card {format, fields, spoiler_free}`：分享卡規格。
- `rarity_key`：保留給第二階段的玩家統計。
- `real_world_stat`（v0.4.1 由 `rarity` 改名）：`kind:"share_of_reported_cases"`，是**投資類詐騙占 115 年 9 月全國受理件數的比例**。它不是結局稀有度，也不代表多少玩家拿到這個結局。畫面顯示 `display`：「115 年 9 月全國受理的詐騙案中，約 16% 是投資類」。
  - 受騙結局：`value_pct = (假投資 913 + 假交友投資詐財 814) / 全國受理 10,775 × 100 = 16.0%`，期間是 115 年 9 月，來源是 165 打詐儀表板截圖；附 `formula`、`source`、`verify_note`、`display`。儀表板沒有依損失程度細分，所以 4 個受騙結局共用這個類型層級的數字（`note` 有說明）。
  - `END_EARLY`：`value_pct: null`。`null_reason`：識破而沒有報案的人不會出現在受理統計裡。

### meta
- `no_pressure_mode {available, default:false, effect, min_timer_s:20}`：無壓力模式，關閉所有倒數。
- `life_grid`：每 5 歲一格，取該區間最嚴重的 `choice.grid`；最後一格用 `ending.grid_color`。
- `presentation_notes`、`real_world_stat_notes`（取代 `rarity_notes`）。
- `phase2_todo`：daily_seed、npc_parallel、badges（本版不做）。

### 文字修正
- `ad_group` 的「LINE股票群組」改為「通訊軟體上的股票群組」。
- `work` 選項的「臉書」改為「社群網站」。
- 案例卡的「從臉書廣告進入LINE投資群」改為「從社群網站廣告進入通訊軟體上的投資群組」。

### 驗證（validate.py 以加法擴充，舊的檢查全部保留；只有 JSON 含 v4 欄位時才執行）
新增的檢查：presentation 合法；chat.app 屬於通用類型；chat 和 interrupts 不含真實品牌名（LINE、Tinder、臉書、蝦皮等）；message id 唯一；interrupt 指向的訊息存在；timer_s 至少 20 而且可以關閉；meta 有無壓力模式；每個 missed_* 都有錨點，而且錨點指向的訊息存在；每個結局都有分享卡欄位；real_world_stat 的 kind 必須是 share_of_reported_cases，不能留下舊的 rarity 欄位；有數值時要有 formula、source、display，是 null 時要有 null_reason。v0.4.1 加上全文品牌掃描（common.brand_hits）：事件文字、選項、聊天、插話、結局文字、案例卡、破綻、分享文案、red_flag_texts，都不能出現 LINE、臉書、Threads、賣貨便、104 等真實品牌（url 和來源名稱不掃）。

## v0.4.1 跨線 flag：cross_line_modifiers（三條線共用格式，定義在 common.py）
人生線（script-life.json）結束時，玩家身上會帶著 flag。三條詐騙線用 JSON 頂層的 `cross_line_modifiers[]` 讀取這些 flag，規則全部寫在資料裡，引擎不需要為每條線寫特例。

### 格式
```json
{"id":"...", "if_flags":{"all":["cash_strapped"],"none":[]},
 "target":{"event":"job_ad","choice":0},
 "effect":{"type":"stats_delta|unlock_choice|add_interrupt|rewrite_text", ...},
 "note":"設計理由"}
```
| effect.type | 參數 | 引擎行為 |
|---|---|---|
| `stats_delta` | `stats:{數值:±n}` | 進入 target.event 時加減一次，並夾在 min/max 之間。`event:"__INIT__"` 表示在開局、family 調整之後套用 |
| `unlock_choice` | `choice:{text,effects,next,flags,grid}` | 加在該事件 choices 的最後面，`cross_line:true` 可以用來顯示「人生經驗解鎖」標記 |
| `add_interrupt` | `interrupt:{at,from,text}` | 在聊天室指定訊息之後插入一則外部訊息 |
| `rewrite_text` | `field:"text"` 或 `"choice_text"`（需要 target.choice 索引）、`text` | 取代事件敘述或選項文字 |

### 引擎讀取流程
1. 進入詐騙線前，把人生線結束時的 flags 併入 `player.flags`。
2. 依陣列順序逐條檢查：`if_flags.all` 都要有，`if_flags.none` 都不能有，兩者都成立才套用。
3. 參考實作是 `common.apply_modifiers(data, flags)`：回傳套用後的 events 和開局數值調整（`on_enter_effects` 是進入事件時的加減）。validator 用的就是這支函式，引擎可以照著移植。
4. 結局判定（ending_rules）不讀人生線 flag；人生線 flag 只透過數值、選項、文字影響過程。

### validate.py 新增檢查（加法擴充）
- 每條規則都有 id、if_flags、target、effect、note。
- 用到的 flag 都必須定義在 script-life.json 的 `meta.cross_line_flags`。
- target 事件和 choice 索引都存在。`__INIT__` 只能用 stats_delta。
- unlock_choice 的 next 存在；如果它設定 missed_*，必須有 red_flag_text。add_interrupt 的 at 指向的訊息存在。
- 列舉這條線用到的人生 flag 的所有組合（2^k），套用規則後重走全部路徑，確認沒有死路（沒有可選選項的事件）或迴圈，並列出結局分布。

### 本線規則（7 條）
| id | 條件 | 目標 | 效果 |
|---|---|---|---|
| inv_wary_ad | wary_of_easy_money | ad_group | 警覺 +8 |
| inv_wary_unlock | wary_of_easy_money | small_win | 解鎖選項「獲利太漂亮反而可疑，全部領回、不再投入」，接到 END_ROUTER |
| inv_mlm_group | mlm_joined | ad_group | 改寫成「以前直銷認識的朋友拉你進群」 |
| inv_mlm_trust | mlm_joined | ad_group | 警覺 −5 |
| inv_lent_mental | lent_money_lost | temptation | 插入內心話「上次借出去的錢也沒拿回來……」 |
| inv_pressure_signer | pressure_signer | withdraw_block | 警覺 −5 |
| inv_evidence | evidence_habit | report | 改寫報案文字，強調保留紀錄（不保證追回） |

## v0.4.2 結局前提與統計標記（三條線共用規則）
- 每個結局都宣告 `requires_flags` 和 `forbids_flags`，也就是結局文字預設的前提。
- `text_variants[]`：`{when:{label, flags_all, flags_none}, text, requires_flags?, forbids_flags?}`。引擎依序取第一個 `when` 成立的變體取代 `text`，都不成立就用 `text`。參考實作是 `common.pick_text`。
- `stats[]` 每筆都有 `self_calculated`（boolean）：自己用官方數字換算的是 true，官方或第三方直接提供的是 false。
- `real_world_stat.display`：沒有數字（value_pct 為 null）時 display 為 null，前台不顯示統計列（v4.5 起取消「官方無此分類」佔位字）。
- validate.py 新增（加法擴充）：
  - 窮舉所有路徑，包括所有 family、所有人生線 flag 組合，確認到達結局時的 flag 符合結局本身和被選中變體的 requires/forbids。
  - 檢查 self_calculated 是 boolean。
  - 檢查：value_pct 為 null 時 display 必須是 null；有數字時 display 必須是非空字串。

### 本線矛盾修正（v0.4.2）
- **END_DEBT**：原條件是「borrowed，且有 missed_bank_warning／mental_collapse／isolated 其中之一」，但文字寫「連行員的提醒也沒聽」。聽了行員提醒（bank_saved）但心理崩潰的玩家也會到這裡，造成矛盾。現在條件改為 borrowed＋missed_bank_warning，不能有 bank_saved；文字刪掉「心理狀態跌到谷底」，這部分由 reason_texts 依 flag 顯示。
- **END_ALL_LOST**：原文字「你最後報了案」沒有說明怎麼報的。實際上到這裡的一定是行員協助報警，所以條件改為 borrowed、沒有 missed_bank_warning，並要求 bank_saved，文字也改寫成和路徑一致。
- 其他結局（EARLY、SMALL_LOSS、BROKE）只補上前提宣告，條件不變。
- base 路徑數：DEBT 768、ALL_LOST 768、BROKE 768、SMALL_LOSS 1152、EARLY 640（以前是 DEBT 1284、ALL_LOST 252）。

### v0.4.2 新增人生線 flag 串接
| id | 條件 | 對象 | 效果 |
|---|---|---|---|
| inv_trusts_adults | trusts_adults | pressure（平台法務部威脅） | 警覺 −5 |

## v4.4 重度負面結局
| 結局 | priority | 觸發 | 文字變體 |
|---|---|---|---|
| END_COLLAPSE 錢之後，連自己也差點失去的人 | 0.5 | borrowed + missed_bank_warning + mental_collapse（心理≤20），排除 bank_saved | supported（has_support）／alone（無 has_support） |
| END_FAMILY_RIFT 借走了家人信任的人 | 0.7 | borrowed + isolated（人際≤15），排除 mental_collapse、has_support | bank（行員擋下）／ignored_bank |
- 個案：stories #67（書田診所，宋媽媽）、#68（中央社，陳小姐）。輕生只用非畫面化描述，並附 1925／1995／165 求助資源（help_resources）。
- real_world_stat 沿用投資詐騙的類型比例，另加 consequence_note：官方沒有「受騙後憂鬱／家庭失和」的分類。
- v4.4 審查：END_FAMILY_RIFT 補上求助專線；END_COLLAPSE 個案卡改成「一度狀態很危急」，著重家人求助與治療後康復。立法院法制局報告標為 verified:false。

## v4.6 平衡調整（合併模擬每個結局 2%–40%）
- date_invest／group_assistant 的查證選項改成「有疑點，但只放最低 1,000 元」→ small_win（看到疑點不等於停手）。
- withdraw_block 新增「辦信貸、刷卡湊解凍費」→ bank_counter（borrowed）。
- pressure 新增「偷偷動用家裡的存款」→ bank_counter（borrowed、took_family_money，人際 −30）。
- FAMILY_RIFT 條件改為 borrowed 且（isolated 或 took_family_money），並新增 family_money 文字變體。
- 深層心理扣分減輕：pressure 借錢 −10、bank_counter 堅持提領 −5，讓 DEBT 和 COLLAPSE 都可能出現。
- 合併模式下金額隨存款縮放，見 life README v0.6 amount_scaling。
- 單線（rates.py）：EARLY 37.5、SMALL_LOSS 28.2、ALL_LOST 10.2、DEBT 9.6、BROKE 8.3、FAMILY_RIFT 5.5、COLLAPSE 0.6（低於 2%；目標只要求合併模擬）。
- 每個選項都有 outcome_text／log_text（outcomes.py）。
- v0.7：選項標籤都改成只寫行動（≤15字、不劇透），結果改由 outcome_text 呈現，規則見 life README v0.7。
- v4.7：偷動家裡存款（took_family_money）的路徑一律判 FAMILY_RIFT，COLLAPSE 排除此旗標（修正合併模擬 FAMILY_RIFT 1.8% < 2%）。
- 合併模擬（最新 build）：SMALL_LOSS 38.8、EARLY 38.1、ALL_LOST 6.7、BROKE 5.5、COLLAPSE 4.4、FAMILY_RIFT 4.1、DEBT 2.5；進入年齡 34–39、機率 0.6、進入前心理 +10、金額 factor = max(存款,50000)/425000（皆 design_assumption）。單線：COLLAPSE 0.6（只在合併模擬要求 ≥2%）。

## v4.7 補充
- **random:true 選項**：一個按鈕、結果隨機。`outcomes[]` 每項有 `probability`（總和＝1）、`outcome_text`、`log_text`、`effects`、`flags_set`、`grid`（可選 `next`）；`random_note.design_assumption: true` 標明機率是設計假設。引擎順序：先選選項，再抽一次 U(0,1) 決定分支。目前只用於人生線 35 歲「接爸媽的電話」（family_passphrase／elder_near_miss 各 0.5）。
- **cross_line_modifiers[].mode**：`all`（預設）或 `standalone_only`＋`mode_note`。standalone_only＝合併模式下進場年齡內拿不到該 flag（mule_lent、mule_lent_stat、mule_pressure_signer、mule_family_pass、shop_family_pass），只在單線模式觸發；validate／combined 只列為 info。合併模式觸發不了卻沒標記的修正，combined.py 會判為錯誤。
- **help_resources**：每個結局都必須有，第一筆是 165 反詐騙專線；有心理傷害的結局加 1925 安心專線、1995 生命線；車手線刑事結局加法律扶助基金會 412-8518（https://www.laf.org.tw/tel-ext）。
- 品牌黑名單新增「思樂冰」「YouTuber」。
