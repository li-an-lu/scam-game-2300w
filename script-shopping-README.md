# 假網拍線 劇本 v0.3
檔案：`script-shopping.json`，由 `gen_shopping.py` 產生。驗證：`python3 validate.py script-shopping.json`。結構跟另外兩條線一樣。

## 流程
出生 → 17 歲加入二手、追星社團 → 20 歲演唱會票（社團有人原價讓票、只收匯款）→ 23 歲 Threads 限量商品（假賣貨便連結先付運費，接著跳出「未實名制」，收款戶名對不上）→ 26 歲「誤設分期」的假客服和假銀行專員來電 → 結局判定。
這條線只描述受騙者看到什麼、經歷什麼，不寫任何詐騙操作手法。

## 結局判定（依 priority 檢查；fallback 是 END_SAFE）
| priority | 結局 | 條件 |
|---|---|---|
| 1 | END_CS_DRAINED | 有 fake_cs_paid（reason_texts 會顯示 savings_depleted、mental_collapse、reported） |
| 2 | END_TICKET_LOST | 有 paid_ticket |
| 3 | END_SMALL_FEE | 有 paid_small |
| 4 | END_SAFE | 沒有 paid_ticket、paid_small、fake_cs_paid |

遊戲中的金額都取材自案例，屬於劇情設定，不是統計數字：11,400 元（#18）、38 元（#15），以及解除分期的 15,000 元。最後一筆已改為接近原案的「近 1.5 萬」（#19），原本的 150,000 元已刪除。

## v0.3 共通規則（三條線一致，由 common.py 套用）
- **stat_flags**：進入結局判定前，引擎先依數值設定 flag：`savings_depleted`（存款≤0）、`mental_collapse`（心理≤20）、`isolated`（人際≤15）、`has_support`（人際≥20）。結局條件只看 flag，不直接看數值。
- **reason_texts**：結局畫面會列出玩家實際擁有的 flag 所對應的說明，讓玩家知道為什麼走到這個結局。
- **red_flag_texts**：每個 `missed_*` flag 都有一句顯示文字，「你錯過的破綻」依玩家實際的走法逐條列出；如果玩家一個都沒錯過，就顯示 `missed_red_flags`（通用版）。
- 所有 `verified` 都是布林值，原本的說明文字移到 `verify_note`；所有來源都有 url，不會是 null。
- 驗證：`python3 validate.py <json>`。初始存款會乘上（1+家庭背景的存款加成），其他家庭加成直接加減；另外也會檢查 null url、verified 型別、`missed_*` 是否都有顯示文字、結局條件是否直接用了數值。

## v0.4 沉浸呈現（同投資線格式，由 common.apply_v4 套用；v0.3 判定邏輯不變）
- 聊天事件 6 個：ticket（倒數 30 秒，可關閉）、ticket_blocked、cheap_item（shop_like「拍拍集（虛構）」）、fee_more、fake_cs（phone_call）、cs_call（phone_call，倒數 25 秒，可關閉）。訊息裡不寫可照做的操作步驟。
- red_flag_anchors：7 個 missed_* flag，共 7 個錨點。
- 結局標題：被一通電話帶走的人、錯過演唱會的人、只付了運費的人、三關全破的人。每個結局都有 share_text 和 share_card。
- `real_world_stat`（kind=share_of_reported_cases，不是結局稀有度）：
  - 三個受騙結局：假網拍 3,513 ÷ 全國受理 10,775 × 100 = 32.6%，期間是 115 年 9 月，來源是 165 打詐儀表板（截圖 04、05）。display 是「115 年 9 月全國受理的詐騙案中，約 33% 是假網拍」。
  - END_CS_DRAINED 另外加註：儀表板沒有說明「假客服解除分期」是否歸在假網拍類，待核實。
  - END_SAFE 是 null：沒有受騙的人不會出現在受理統計中。
- 品牌文字修正：「Threads 上有人」改為「社群平台上有人」；「賣貨便連結」改為「超商寄貨平台連結」；案例卡同步修改。

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

### 本線規則（6 條）
| id | 條件 | 目標 | 效果 |
|---|---|---|---|
| shop_game_scammed | game_scammed | __INIT__ | 警覺 +5（依人生線 README 建議） |
| shop_game_scammed_msg | game_scammed | ticket | 插入內心話「跟國中買遊戲裝備被騙那次好像」 |
| shop_pressure_signer | pressure_signer | cs_call | 警覺 −8 |
| shop_family_pass | family_passphrase | cs_call | 解鎖「先掛斷，用通關密語跟家人確認，打165」，設定 stopped_early。本線沒有假親友事件，所以把通關密語「先掛斷、再查證」的習慣套用在假客服來電 |
| shop_evidence | evidence_habit | ticket_blocked 選項 0 | 改寫成「紀錄都在，報案」 |
| shop_lent | lent_money_lost | aftermath | 心理 −5 |

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
- **END_TICKET_LOST**：原文字一律寫「報案之後要等開庭」，但選「覺得丟臉，算了」的玩家沒有報案。現在拆成變體 reported（要等開庭）和 silent（沒有報案，錢就這樣不見了），條件不變。
- 其他結局只補上前提宣告。
- base 路徑數：CS_DRAINED 3072、TICKET_LOST 1280（reported 640／silent 640）、SMALL_FEE 768、SAFE 512。

### v0.4.2 新增人生線 flag 串接
| id | 條件 | 對象 | 效果 |
|---|---|---|---|
| shop_checks_first | checks_first | ticket（m2 後） | add_interrupt「查證提示」 |
| shop_otp_link | otp_scammed | cheap_item | 警覺 +5 |

## v4.4 重度負面結局
| 結局 | priority | 觸發 | 文字變體 |
|---|---|---|---|
| END_SILENT_COLLAPSE 一個人吞下所有自責的人 | 0.5 | fake_cs_paid + mental_collapse（心理≤20），排除 reported | friend_noticed（has_support） |
- 本線每條路徑都至少有 has_support，所以沒有做「完全沒人發現」的變體（那條路徑不可能到達）。
- 個案卡：v4.4 審查後移除 TVBS 個案（手法不明、當事人已離世）。找不到手法明確是假網購／假客服、又有求助後康復紀錄的公開個案，所以只放說明，沒有個案；「85,780 名大學生」數字只有新聞轉述，找不到警政署原始出處，沒有使用。輔助資料：中央社／公視醫師報導、華藝碩論（社會支持越多，創傷反應越輕）、立法院法制局報告。
- real_world_stat 沿用解除分期的比例，另加 consequence_note。

## v4.6
- 結構沒改，合併模擬已在 2%–40% 內。單線（rates.py）：SAFE 25.0、CS_DRAINED 25.0、TICKET_LOST 23.0、SMALL_FEE 20.8、SILENT_COLLAPSE 6.2。
- 每個選項都有 outcome_text／log_text（outcomes.py）。
- v4.7：新增 `shop_sister_math`（童年 flag counted_change → fee_more 回憶提醒，不改數值）。
- 四份劇本的選項標籤都改成只寫行動（≤15字），結果改由 outcome_text 呈現，規則見 life README v0.7。
- 合併模擬（最新 build）：進入 70.3%（年齡 22–28、機率 0.7）；SAFE 24.5、TICKET_LOST 23.2、CS_DRAINED 21.2、SMALL_FEE 21.0、SILENT_COLLAPSE 10.1。

## v4.7 補充
- **random:true 選項**：一個按鈕、結果隨機。`outcomes[]` 每項有 `probability`（總和＝1）、`outcome_text`、`log_text`、`effects`、`flags_set`、`grid`（可選 `next`）；`random_note.design_assumption: true` 標明機率是設計假設。引擎順序：先選選項，再抽一次 U(0,1) 決定分支。目前只用於人生線 35 歲「接爸媽的電話」（family_passphrase／elder_near_miss 各 0.5）。
- **cross_line_modifiers[].mode**：`all`（預設）或 `standalone_only`＋`mode_note`。standalone_only＝合併模式下進場年齡內拿不到該 flag（mule_lent、mule_lent_stat、mule_pressure_signer、mule_family_pass、shop_family_pass），只在單線模式觸發；validate／combined 只列為 info。合併模式觸發不了卻沒標記的修正，combined.py 會判為錯誤。
- **help_resources**：每個結局都必須有，第一筆是 165 反詐騙專線；有心理傷害的結局加 1925 安心專線、1995 生命線；車手線刑事結局加法律扶助基金會 412-8518（https://www.laf.org.tw/tel-ext）。
- 品牌黑名單新增「思樂冰」「YouTuber」。
