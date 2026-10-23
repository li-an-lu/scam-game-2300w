# 求職變車手線 劇本 v0.3

檔案：`script-mule.json`，由 `gen_mule.py` 產生。驗證：`python3 validate.py script-mule.json`（validate.py 兩條線共用）。

## 結構
跟投資線一樣：`meta`、`ending_rules`、`stats`（這條線放的是法條刑度，全部逐字核對過）、`stats_sources`、`player_init`、`events[]`、`endings[]`。
- 選項的 `next: "__EVAL__"` 表示進入結局判定，只出現在 `END_ROUTER`。

## 流程
出生 → 16 歲學校反詐宣導 → 20 歲缺錢（可以向家人或學校求助）→ 看到「居家輕鬆、日領三千」的徵才 →（查證公司）→ 對方要金融卡、密碼或帳戶 →（朋友提醒）→ 帳戶出現陌生款項，對方邀你「升級外出收款」→ 家人察覺 → 被警方攔下、起訴、民事求償；或是帳戶被警示、到案說明。

這條線只呈現玩家被誘入的過程和後果，不描寫任何操作方法。

## 結局判定（依 priority 檢查，fallback 是 END_ACCOUNT）
| priority | 結局 | 條件 |
|---|---|---|
| 1 | END_CONVICTED | 有 `convicted`、沒有 `settled`，而且（`civil_judgment` 或 `savings_depleted` 或 `mental_collapse`） |
| 2 | END_RECORD | 有 `convicted`（坦承並和解賠償） |
| 3 | END_ACCOUNT | 有 `gave_account`、沒有 `became_mule` |
| 4 | END_RESCUED | 有 `family_stopped` 或 `self_reported`，而且有 `has_support` |
| 5 | END_REFUSE | 有 `refused`、沒有 `gave_account` |

## 法條（2026-10-23 在 law.moj.gov.tw 逐字核對）
- 刑法 §339-4
- 洗錢防制法 §19、§22
- 組織犯罪防制條例 §3
- 民法 §185

## v0.3 共通規則（三條線一致，由 common.py 套用）
- **stat_flags**：進入結局判定前，引擎先依數值設定 flag：`savings_depleted`（存款≤0）、`mental_collapse`（心理≤20）、`isolated`（人際≤15）、`has_support`（人際≥20）。結局條件只看 flag，不直接看數值。
- **reason_texts**：結局畫面會列出玩家實際擁有的 flag 所對應的說明，讓玩家知道為什麼走到這個結局。
- **red_flag_texts**：每個 `missed_*` flag 都有一句顯示文字，「你錯過的破綻」依玩家實際的走法逐條列出；如果玩家一個都沒錯過，就顯示 `missed_red_flags`（通用版）。
- 所有 `verified` 都是布林值，原本的說明文字移到 `verify_note`；所有來源都有 url，不會是 null。
- 驗證：`python3 validate.py <json>`。初始存款會乘上（1+家庭背景的存款加成），其他家庭加成直接加減；另外也會檢查 null url、verified 型別、`missed_*` 是否都有顯示文字、結局條件是否直接用了數值。

## v0.3.1 審核補件
- 判決改用司法院官方連結（judgment.judicial.gov.tw，已用 WebFetch 核對）。
- 前科段落：加入警察刑事紀錄證明核發條例§6、公務人員任用法§28，兩條均已逐字核對；劇本文字改為「可能影響」的語氣。
- 自由時報 3 篇：都加上 verify_note「依搜尋摘錄核對」。

## v0.4 沉浸呈現（同投資線格式，由 common.apply_v4 套用；v0.3 判定邏輯不變）
- 聊天事件 7 個：job_ad（社群貼文）、job_check、job_offer（倒數 30 秒，可關閉）、friend_warn、account_used（插入系統通知）、family_notice（in_person）、police_call（phone_call）。App 名稱都是虛構的（「聊聊 Chatto（虛構）」「社群動態（虛構）」）。
- 內容原則：訊息只呈現詐團話術和受害者反應，不描述任何提領、交付款項或規避查緝的做法。
- red_flag_anchors：4 個 missed_* flag，共 6 個錨點。
- 結局標題：替上游扛下一切的人、留下紀錄的人、帳戶被借走的人、被拉回來的人、第一步就說不的人。每個結局都有 share_text 和 share_card。
- `real_world_stat` 全部是 null。`null_reason`：165 儀表板依被害人遭遇的詐騙手法分類，沒有「求職被吸收成車手／提供帳戶」這一類（車手和人頭帳戶在法律上是共犯或被告，不是被害類型），所以不硬套其他類別。
- 品牌文字修正：私訊LINE改為私訊加好友；上104改為上正規求職網站；直接加LINE改為直接加好友私聊；案例卡的「臉書」改為「社群網站」。

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

### 本線規則（10 條）
| id | 條件 | 目標 | 效果 |
|---|---|---|---|
| mule_cash_broke | cash_strapped | broke | 改寫成「存款只剩幾百塊」 |
| mule_cash_lure | cash_strapped | job_ad | 警覺 −8、心理 −5（高薪誘惑更強） |
| mule_cash_lure_msg | cash_strapped | job_ad | 插入「本期房租已逾期 3 天」 |
| mule_wary | wary_of_easy_money | job_ad | 警覺 +10 |
| mule_wary_unlock | wary_of_easy_money | job_ad | 解鎖「不回覆，向165通報」，設定 refused，接到 END_ROUTER |
| mule_pressure_signer | pressure_signer | job_offer | 警覺 −5 |
| mule_lent / mule_lent_stat | lent_money_lost | friend_warn | 插入內心話（不信任朋友）；人際 −5 |
| mule_evidence | evidence_habit | police_call 選項 0 | 改寫成「帶完整紀錄到案說明」 |
| mule_family_pass | family_passphrase | family_notice | 人際 +5（家裡有互相確認的習慣） |

## v0.4.2 結局前提與統計標記（三條線共用規則）
- 每個結局都宣告 `requires_flags` 和 `forbids_flags`，也就是結局文字預設的前提。
- `text_variants[]`：`{when:{label, flags_all, flags_none}, text, requires_flags?, forbids_flags?}`。引擎依序取第一個 `when` 成立的變體取代 `text`，都不成立就用 `text`。參考實作是 `common.pick_text`。
- `stats[]` 每筆都有 `self_calculated`（boolean）：自己用官方數字換算的是 true，官方或第三方直接提供的是 false。
- `real_world_stat.display`：沒有數字（value_pct 為 null）時 display 為 null，前台不顯示統計列（v4.5 起取消「官方無此分類」佔位字）。
- validate.py 新增（加法擴充）：
  - 窮舉所有路徑，包括所有 family、所有人生線 flag 組合，確認到達結局時的 flag 符合結局本身和被選中變體的 requires/forbids。
  - 檢查 self_calculated 是 boolean。
  - 檢查：value_pct 為 null 時 display 必須是 null；有數字時 display 必須是非空字串。

### 本線結局規則重整（v0.4.2）
| priority | 結局 | 條件 | 前提（requires／forbids） |
|---|---|---|---|
| 1 | END_CONVICTED | convicted，沒有 settled，任一：civil_judgment／savings_depleted／mental_collapse | 需要 convicted、arrested、civil_judgment；不能有 settled |
| 2 | END_RECORD | convicted | 需要 convicted、arrested、settled；變體 confessed（坦承）和 denied（堅稱只是打工） |
| 3 | END_RESCUED | gave_account＋has_support，任一：family_stopped／self_reported，沒有 convicted | 不能有 convicted、arrested；變體 family（已接升級任務、被家人拉回）和 self（主動說明、沒接升級任務） |
| 3.5（v4.5 改為 2.9） | **END_STOPPED_ALONE（新增）** | became_mule＋family_stopped，沒有 has_support（v4.5 改為：沒有 has_support，或曾忽略朋友警告 ignored_friend） | 被家人阻止，但已經接過升級任務，又沒有人支持 |
| 4 | END_ACCOUNT | gave_account，沒有 became_mule | 不能有 became_mule、convicted、arrested（文字寫「你沒有去收款」） |
| 5 | END_REFUSE | refused，沒有 gave_account | 不能有 gave_account |

修正內容：
- **自己報警又有人支持的玩家**，以前被 END_ACCOUNT（priority 3）攔走，現在 RESCUED 排在 ACCOUNT 之前。
- **當了車手、被家人阻止、人際 <20 的玩家**，以前掉進 fallback END_ACCOUNT，文字和劇情矛盾；現在進新結局 END_STOPPED_ALONE。
- 數值微調：friend_warn「覺得朋友太緊張，還是照做」從人際 −5 改為 **−10**。原本的數值下，base 路徑到不了 STOPPED_ALONE，只有人生線帶入 lent_money_lost 才到得了；調整後 validate.py 的舊檢查「所有結局都可到達」才能通過。
- END_RECORD 原本寫死「你坦承犯行」，但堅稱只是打工、後來和解的玩家也會到這裡，所以拆成兩個變體。

base 路徑數：CONVICTED 2048、RECORD 2048（confessed 1024／denied 1024）、RESCUED 3456（family 1856／self 1600）、ACCOUNT 2496、STOPPED_ALONE 192、REFUSE 1280，合計 11,520 條，0 條 fallback。

## v4.4 重度負面結局
| 結局 | priority | 觸發 | 文字變體 |
|---|---|---|---|
| END_CUT_OFF 被所有人切割的人 | 0.5 | convicted + isolated（人際≤15），排除 has_support | civil（全額判賠）／settled（和解）／collapse（mental_collapse，附求助資源） |
- 個案：stories #70（NOWnews，家屬公開切割；報導時尚未判決，已去識別化）、#71（中央社，少年車手的父母判賠157萬，民法§187）。
- real_world_stat：stat_null，display 為 null，前台不顯示統計列。
- v4.4 審查：所有版本都附 1925／1995／165，以及法律扶助基金會 412-8518（手機加02，https://www.laf.org.tw/tel-ext）。

## v4.5（2026-10-23）
- **END_STOPPED_ALONE 重調**：原條件只靠人際<20，人生線初值 20–70 下均勻抽樣只有約 0.04%。改為 became_mule＋family_stopped，沒有 convicted，且「忽略朋友警告（ignored_friend）」或「沒有 has_support」任一成立；priority 2.9（排在 RESCUED 3 之前）。文字變體：ignored_friend（新文字：想起那個警告過你的朋友）、alone（原文字）。
  - 目標比率：約 2%（均勻初值、均勻選擇，`python3 /tmp/rate.py script-mule.json` 實測 2.05%）。理由：這是「被家人攔下、但身邊朋友已經疏遠」的少數結局，應該和 RECORD／CONVICTED／CUT_OFF（約 1.8–2.5%）同一量級，可以玩到但不搶主線；它只從原本的 RESCUED 分走一部分（18.31%→16.30%），其他結局比率不變。
  - 上方 v4.4 的「base 路徑數」是舊數字，現在以 validate.py 輸出為準。
- 新增 modifier mule_told_truth：童年 told_truth → family_notice 多一則回憶提醒（不改數值）。

## v4.6 平衡調整（合併模擬每個結局 2%–40%）
- job_check「查不到登記」不再直接結束，改成記下疑點（flag `checked_company`），繼續聽工作內容。
- job_offer 的直接拒絕需要 `checked_company`（兩個疑點加起來才拒絕）；沒查公司的人要靠朋友提醒。
- friend_warn 新增第三個選項「只給帳號、不給密碼應該沒關係吧」→ account_used（設 ignored_friend）。
- arrest「堅稱只是打工」人際 −15（家人疏遠，CUT_OFF 需要人際 ≤15）。
- 單線（rates.py）：RESCUED 32.5、ACCOUNT 26.1、REFUSE 23.8、CUT_OFF 5.5、STOPPED_ALONE 5.1、RECORD 4.2、CONVICTED 2.9。合併模擬見 life README v0.6。
- 每個選項都有 outcome_text／log_text（outcomes.py）。
- v0.7：選項標籤都改成只寫行動（≤15字、不劇透），結果改由 outcome_text 呈現，規則見 life README v0.7。
- 合併模擬（最新 build）：進入 41.4%（年齡 18–22、機率 0.6、需缺錢）；REFUSE 33.1、RESCUED 28.7、ACCOUNT 23.1、RECORD 4.7、STOPPED_ALONE 4.1、CONVICTED 3.4、CUT_OFF 2.9。
- 注意：friend_warn「只給帳號不給密碼」的 outcome_text 只寫對方一口答應，不暗示這樣安全；後果在 account_used 呈現（帳戶仍會被用、可能凍結或被追訴）。

## v4.7 補充
- **random:true 選項**：一個按鈕、結果隨機。`outcomes[]` 每項有 `probability`（總和＝1）、`outcome_text`、`log_text`、`effects`、`flags_set`、`grid`（可選 `next`）；`random_note.design_assumption: true` 標明機率是設計假設。引擎順序：先選選項，再抽一次 U(0,1) 決定分支。目前只用於人生線 35 歲「接爸媽的電話」（family_passphrase／elder_near_miss 各 0.5）。
- **cross_line_modifiers[].mode**：`all`（預設）或 `standalone_only`＋`mode_note`。standalone_only＝合併模式下進場年齡內拿不到該 flag（mule_lent、mule_lent_stat、mule_pressure_signer、mule_family_pass、shop_family_pass），只在單線模式觸發；validate／combined 只列為 info。合併模式觸發不了卻沒標記的修正，combined.py 會判為錯誤。
- **help_resources**：每個結局都必須有，第一筆是 165 反詐騙專線；有心理傷害的結局加 1925 安心專線、1995 生命線；車手線刑事結局加法律扶助基金會 412-8518（https://www.laf.org.tw/tel-ext）。
- 品牌黑名單新增「思樂冰」「YouTuber」。
