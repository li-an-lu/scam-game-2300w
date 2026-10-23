# 人生日常線 劇本 v0.7（Round 4）
檔案：`script-life.json`，由 `gen_life.py` 產生。

**一鍵建置**：`python3 build.py --all`：
1. 重建故事庫。
2. 依序執行 gen_life → gen_investment → gen_mule → gen_shopping。人生線要先跑，因為詐騙線會讀它的 cross_line_flags。
3. 驗證三條詐騙線（DFS 窮舉），再驗證人生線（`--sample`，含 combined.py 的完整人生模擬）。
4. 全部通過才把 `script-*.json` 複製到 `web/`；任一步失敗就停下，不覆蓋 web/。

只想驗證人生線：`python3 validate.py script-life.json --sample`。只跑合併模擬：`python3 combined.py [N]`。

這條線是一局的主幹，從 0 歲演到 40 歲。三條詐騙線在中途插入，演完再回到人生線，數值和 flag 都會延續（見下方「詐騙線插入規格」）。每個事件都取材自 Dcard、PTT 的真實分享或新聞，來源寫在各事件的 sources。

## v0.5 詐騙線插入規格（給程式）
資料：`script-life.json` → `meta.scam_integration`；參考實作：`combined.py` 的 `play()`。web/engine.js 目前**還沒有實作**這個模式，以下規格以 combined.py 為準。

### 1. 插入點（v0.6 起；舊的固定年齡 19／27／37 已廢除）
每條詐騙線開局各抽一次進入年齡與是否遇到，細節見下方「v0.6 合併人生模擬」。
| 詐騙線 | entry_event | 年齡窗（base ± 偏移） | 進入機率 | 觸發 | 停留時間 |
|---|---|---|---|---|---|
| 求職車手 mule | broke | 20 ±2（18–22） | 0.6 | flags_any [cash_strapped, wage_unpaid] | 0 年；有 arrested 則 1 年 |
| 假網拍 shopping | ticket | 25 ±3（22–28） | 0.7 | 無 | 0 年 |
| 假投資 investment | work | 37 −3/+2（34–39） | 0.6 | 存款 > 0 | 0 年；有 borrowed 則 1 年 |

一生會遇到 0–3 條詐騙線（最新分布見 v0.6 結果）。年齡窗、機率、停留時間都是 **design_assumption**。進入前心理 +10、假投資金額依存款縮放，也都是 design_assumption。

### 2. 年齡依據（sourced 年齡層 ＋ design_assumption 具體年齡窗）
- **車手 18–22 歲**：警政署 114年第10週通報，113年9–12月 18–23 歲嫌疑犯涉詐欺 6,945 人，其中擔任車手 3,866 人（verified）。
- **假網拍 22–28 歲**：內政部 115年第36週通報，59 歲以下被害人以假網拍占比最高（verified）。
- **假投資 34–39 歲**：內政部 115年第36週表2，30–39 歲被害人最多（17,906 人，21.8%）（verified）。投資詐欺占比最高其實是 60 歲以上，但人生線只演到 40 歲。
- fromnineon 的年齡×手法百分比（例如 24–29 歲假網拍 31.44%、30–39 歲投資 23.42%）是二手整理，標 `verified:false`、`display:false`，**前台不顯示**，只供製作者參考。

### 3. 進入時
1. **不重新投胎**：忽略詐騙線自己的 player_init（init_range、family_pool、county_pool），沿用人生線當下的 4 項數值，以及縣市和家庭。
2. 詐騙線的 flags 從人生線目前所有 flag 開始。用 `common.apply_modifiers(scam, flags)` 取得改寫後的事件和 `__INIT__` 的數值變動，數值變動在進入當下套用。
3. 從 entry_event 開始播；詐騙線自己的童年事件（birth、teen）不播。

### 4. 離開、回到人生線
1. 詐騙線走到 `__EVAL__` 時，先重算 stat_flags，再依該線的 ending_rules 判定結局，並檢查 requires／forbids 前提。
2. exit_age = entry_age + 停留時間，必須 ≤ return_to 事件的年齡。
3. 人生線 flags 加上以下三類：
   - `_always`：scam_seen_<line>。
   - `return_map[line][ending_id].flags`（見下表）。
   - `_carry_internal` 對照到的 flag：kept_evidence／reported → evidence_habit，told_someone → has_told_someone。
4. 其他詐騙線內部 flag **不帶回**，只記錄在 scam_history。
5. 數值原樣帶回，不重複扣。return_map 的 stats_delta 欄位預設為空。
6. 前往 return_to，繼續人生線。
7. stat_flags（savings_depleted／mental_collapse／isolated／has_support）每次判定前都依當下數值重算，不跨線保存。

| 詐騙線 | 結局 → 帶回人生線的 flag |
|---|---|
| mule | CUT_OFF／CONVICTED／RECORD → criminal_record＋wary_of_easy_money；RESCUED／STOPPED_ALONE／ACCOUNT／REFUSE → wary_of_easy_money |
| shopping | SILENT_COLLAPSE／CS_DRAINED／TICKET_LOST → scam_money_lost；SMALL_FEE → （無）；SAFE → checks_first |
| investment | COLLAPSE／FAMILY_RIFT／DEBT／ALL_LOST → scam_money_lost＋scam_debt；BROKE → scam_money_lost；SMALL_LOSS／EARLY → wary_of_easy_money |

帶回的 flag 也會影響之後插入的詐騙線。例如 19 歲在車手線學到 wary_of_easy_money，37 歲的投資線會讀到它（inv_wary_*）。

### 5. 最終結局與分享卡
- 回到 LIFE_ROUTER（40）後，用經過所有詐騙線之後的數值和 flag，照人生線 ending_rules 判定。
- 新結局 **END_LIFE_RECORD**（priority 0.5，最先檢查）：條件 criminal_record，案例來源是自由時報〈18歲兼職變車手判4月〉。標 `combined_only`：單獨跑人生線到不了，可達性由 combined.py 檢查。
- 新文字變體：
  - END_LIFE_STRETCHED 的 `scammed`：需要 scam_money_lost＋savings_depleted。
  - END_LIFE_STEADY 的 `scammed`：需要 scam_money_lost。
  - 沒被騙過錢的玩家不會看到「被騙過」的文字。
- **recap**：scam_history 非空時，在結局本文之後、case_card 之前，依 entry_age 排序，每條一行：`{entry_age}歲｜{name}：{title_emoji} {title}`。
- **age_lived** = max(最後一個人生事件的年齡, 最後一條詐騙線的 exit_age)。目前恆為 40，因為所有 exit_age 都 ≤ 40。
- **life_grid**：每 5 歲一格。人生選項的 grid 和詐騙線結局的 grid_color 都放進 entry_age 所在的格子，同一格取最嚴重的（red>yellow>green）；最後一格用人生線結局的顏色。
- **share_card.fields** 新增 age_lived、scam_history。分享卡只顯示詐騙線結局的 emoji 和標題，維持 spoiler_free。

### 6. 沒有數字的統計
real_world_stat.value_pct 為 null 時，display 也是 null，前台**完全不顯示**統計列（v4.5 起取消「官方無此分類」佔位字）。null_reason 只留在資料裡給製作者看。validate.py 檢查：沒有數字時 display 必須是 null；有數字時 display 必須是非空字串。人生線 5 個結局目前都沒有數字。

### 7. combined.py 的檢查（validate --sample 會自動呼叫，N=20,000，seed 42，均勻初值、均勻選擇）
**錯誤**（任一項不符就報錯，建置不通過）：
- 整局年齡序列不遞減。
- exit_age ≤ return_to 事件的年齡。
- after_event 的所有選項都指向 return_to。
- entry_event 存在，entry_age 與 after_event 的年齡一致。
- trigger 需要的 flag 在 after_event 之前就可能被設定。
- return_map 涵蓋該線所有結局。
- 每條詐騙線結局、每個人生線結局（含文字變體）的 requires／forbids 前提都成立。
- 人生線每個結局都到得了。

**info**（只列出，不報錯）：
- 進入年齡時還不可能出現的 flag 所對應的 modifier（死 modifier）。
- 合併模式下沒被抽到的詐騙線結局（WARN）。

## 事件
| 年齡 | id | 類別 | 主要來源 |
|---|---|---|---|
| 0 | birth | 人生 | 縣市池依據：年度縣市分布（韭點開始整理165資料） |
| 8 | hongbao | 家庭與金錢 | PTT Gossiping〈媽媽幫你存起來是真的〉：媽媽過世後整理遺產，才知道每 |
| 12 | first_phone | 家庭與金錢 | ETtoday：10歲兒子用媽媽手機玩手遊，偷刷近30萬；點數已使用就難退款 |
| 14 | game_trade | 網路交易 | 巴哈姆特新楓之谷板：8591 買到與描述不符的裝備，賣家要付費才取消（stori |
| 17 | part_time | 工作 | Dcard 工作板：勞資調解心路歷程（文長） |
| 18 | hongbao_result | 家庭與金錢 | PTT Gossiping〈媽媽幫你存起來是真的〉：媽媽過世後整理遺產，才知道每 |
| 19 | student_loan | 家庭與金錢 | TVBS：畢業時學貸43萬，兩年還掉近20萬的心得 |
| 20 | rent | 租屋 | TVBS：退租驗收已過，房東仍以重新粉刷為由，19,200元押金只退8,700元 |
| 22 | mlm | 人際邀約 | Dcard 閒聊板：好朋友拉我直銷 |
| 24 | lend | 借錢 | Dcard 閒聊板：本來以為是兄弟，結果借錢不還 |
| 26 | insurance | 人際邀約 | Dcard 理財板：為何我不買儲蓄險 |
| 30 | rosca | 家庭與金錢 | PTT WomenTalk：請問現在還有人在跟會、標會嗎？ |
| 35 | elder | 長輩 | 內政部：LINE名稱與兒子相同的新帳號借39萬（stories #40） |
| 40 | LIFE_ROUTER | 人生 | 165全民防騙網（警政署，撥打165） |

## 紅包「媽媽幫你存」：正反兩面
8歲選擇「交給媽媽」（gave_hongbao）的玩家，18歲時由引擎隨機抽選結果A（真的存了→hongbao_returned）或結果B（拿不回來→hongbao_lost）。各50%在 JSON 標為 `design_assumption: true`（`random_weights`、`random_note`）：**設計設定，非統計，前台不顯示為統計**。
- 正面：PTT Gossiping M.1582284292、PTT C_Chat M.1772379094、TVBS 2390629／三立 1246155（Dcard 心情板）、ETtoday 2431672
- 反面：三立 351665、782179（PTT 轉述）、PTT C_Chat M.1772379094 推文、喆律法律事務所（民法1087、1088條）
- 待核實：反面的 Dcard 原文沒有直接找到，目前反面引用的是 PTT 和新聞轉述

## 結局（只用 flag 判定）
| priority | 結局 | 條件 |
|---|---|---|
| 1 | END_LIFE_STRETCHED | savings_depleted；或同時有 lent_money_lost、rosca_lost，且沒有 has_support（人際<20） |
| 2 | END_LIFE_HONGBAO_GONE | hongbao_lost |
| 3 | END_LIFE_HONGBAO_SAVED | hongbao_returned |
| 4 | END_LIFE_STEADY（fallback） | 兩個紅包 flag 都沒有 |

（v0.5 新增 END_LIFE_RECORD，priority 0.5，見上方規格。）

## 跨線 flag（舊版建議，已過時）
> v0.4 起三條詐騙線都已透過 `cross_line_modifiers` 讀取這些 flag，實際效果以各詐騙線 JSON 和 `meta.cross_line_flags` 為準。下方保留 v0.3 的原始建議，作為紀錄。

- `wary_of_easy_money`：建議：投資線、車手線中「高報酬／輕鬆打工」選項的警覺門檻降低（較容易識破）
- `evidence_habit`：建議：被騙後的「報案」選項更容易成功（有保留紀錄）
- `family_passphrase`：建議：假親友、AI 仿聲事件可直接識破
- `lent_money_lost`：建議：心理-、人際-；之後「朋友借錢」事件更容易觸發
- `cash_strapped`：建議：求職車手線「急需用錢」事件更容易觸發
- `game_scammed`：建議：假網拍線的警覺初始值+5（學過一次教訓）
- `mlm_joined`：建議：投資群組事件更容易觸發（人脈被當名單）
- `pressure_signer`：建議：「當場決定」類的假客服、假檢警事件更容易得逞

## 待核實
- 紅包結果A／B的比例（設計設定，非統計，前台不顯示為統計）
- 金管會保險契約撤銷期的細節
- Dcard、自由時報的來源因原站擋自動連線，依搜尋摘錄核對
- 遊戲金額（例如押金扣10,500元、倒會6萬元）是取材自案例的劇情設定，不是統計數字

## v0.3.1 平衡調整（2026-10-23）
- 初始存款 init_range 從 20,000–120,000 改成 70,000–200,000（×家庭加成）。理由：這條線從0歲到35歲只把打工欠薪做成收入事件，其他工作收入沒有逐一做成事件，所以用初始存款代表這段期間累積的基本存款。這是設計設定，不是統計數字。
- 「生活拮据」的觸發條件：「借錢沒拿回來＋倒會」改成還要「身邊沒有支援（人際<20）」才成立。理由：有人可以幫忙周轉時，兩筆損失不一定會把生活壓垮。
- 取材自案例的金額都沒改（押金扣10,500、倒會6萬、借款3萬等）。
- validate 結果（262,144 條路徑；紅包A／B各算一條路徑，沒有乘上機率）：

| 結局 | 路徑數 | 占比 |
|---|---|---|
| END_LIFE_STRETCHED（生活拮据） | 73,284 | 28.0% |
| END_LIFE_STEADY | 84,236 | 32.1% |
| END_LIFE_HONGBAO_SAVED | 62,720 | 23.9% |
| END_LIFE_HONGBAO_GONE | 41,904 | 16.0% |

## v0.4 童年 0–18 歲擴充（Leo 試玩回饋：童年太快）

新增 16 個事件，讓 4–18 歲幾乎每年都有 1–2 件事。設計原則：當下常常不知道自己被騙（之後才揭曉）；有大人善意的謊言、老師的文字遊戲、同學之間的小交易；也有**信任被回報**的結果（打勾勾成真、100分真的換到冰沙、同學畢業時還錢），讓玩家學會分辨，而不是什麼都不信。內容只寫受騙的過程和後果，不寫手法細節。

| 年齡 | id | 類別 | 開頭 | 延後揭曉 | 來源（核對方式） |
|---|---|---|---|---|---|
| 4 | shot | 長輩的善意謊言 | 打預防針。媽媽說：「不痛，像蚊子叮一下。」護理師阿姨已經拿起 | 否 | [妞新聞：黃瑽寧醫師「別告訴孩子不會痛」](https://www.niusnews.com/=P1rbval1)（2026-10-23 curl 開啟原文比對）<br>[PChome 個人新聞台：診所裡的小男孩大吼「妳騙人啦！打針明明就很痛！」](https://mypaper.pchome.com.tw/littlesuntaipei/post/1324600677)（2026-10-23 curl 開啟原文比對） |
| 5 | promise_park | 長輩的善意謊言 | 爸爸說：「把青菜吃完，週末就帶你去公園玩。」 | 是（7歲揭曉） | [華視：父母承諾「考上公立就去迪士尼」後食言，原PO說「大人人前說的跟事後做的不一樣」](https://news.cts.com.tw/cts/life/202307/202307202205175.html)（2026-10-23 curl 開啟原文比對）<br>[Dcard 閒聊板：考全校前5就買電腦，結局超心寒](https://www.dcard.tw/f/talk/p/235130284)（原站擋自動連線，依 WebSearch 搜尋摘錄核對） |
| 6 | school_gate | 校門口 | 放學時，校門口有人在賣毛茸茸的染色小雞。一隻二十塊，旁邊圍了 | 否 | [PTT Childhood〈學校旁文具店老闆的煉金術，你被坑多少〉：小雞、染色小雞、蠶寶寶（共同經驗：找不到單一來源，附上討論串）](https://www.pttweb.cc/bbs/Childhood/M.1703615356.A.A75)（2026-10-23 curl 開啟原文比對）<br>[PTT NHU_Talk：國小有人來擺攤賣套書，「買一套送小鳥」，小鳥後來死了](https://www.pttapp.cc/bbs/NHU_Talk/M.1301074112.A.61A.html)（2026-10-23 curl 開啟原文比對） |
| 7 | park_reveal | 揭曉 | （兩年前的那個週末） | 是，揭曉 promise_park(5) | [華視：父母承諾「考上公立就去迪士尼」後食言，原PO說「大人人前說的跟事後做的不一樣」](https://news.cts.com.tw/cts/life/202307/202307202205175.html)（2026-10-23 curl 開啟原文比對）<br>[Dcard 閒聊板：考全校前5就買電腦，結局超心寒](https://www.dcard.tw/f/talk/p/235130284)（原站擋自動連線，依 WebSearch 搜尋摘錄核對） |
| 7 | card_trade | 同學 | 同學拿出一張亮晶晶的「超限量卡」，說只要用你7張卡來換。 | 是（10歲揭曉） | [ETtoday：小一兒拿7張七龍珠卡換「限量寶可夢卡」，結果是一張商品吊牌](https://www.ettoday.net/news/20221025/2365423.htm)（2026-10-23 curl 開啟原文比對）<br>[未來親子：國小老師談「校園地下交易」](https://futureparenting.cwgv.com.tw/family/content/index/18810)（2026-10-23 curl 開啟原文比對） |
| 9 | lottery | 校門口 | 文具店的抽抽樂，5塊一抽，集滿「黑暗大法師」就能換怪獸對打機 | 是（16歲揭曉） | [PTT Childhood〈以前文具店有種抽籤集字換玩具〉：推文「永遠缺一個字」「大概是很多小朋友第一次被詐騙的東東」（共同經驗：找不到單一來源，附上討論串）](https://www.pttweb.cc/bbs/Childhood/M.1693736306.A.FC8)（2026-10-23 curl 開啟原文比對）<br>[PTT C_Chat 2026-04-26〈小時候玩過抽抽樂嗎〉：「黑暗大法，就是沒有師」（共同經驗：找不到單一來源，附上討論串）](https://www.pttweb.cc/bbs/C_Chat/M.1777180881.A.664)（依 WebSearch 摘錄核對）<br>[民視：YouTuber 實測柑仔店抽抽樂，花800元只換回250元，「童年充滿了謊言」](https://www.ftvnews.com.tw/news/detail/2021A07W0350)（2026-10-23 curl 開啟原文比對） |
| 9 | lend5 | 同學 | 隔壁同學說：「借我5塊買棒棒冰，明天一定還你！」 | 是（12歲揭曉） | [PTT StupidClown〈[童年] 所以是欠多少錢〉：借100元只還50元，理由是「只花了50」](https://www.pttweb.cc/bbs/StupidClown/M.1418036788.A.1DF)（2026-10-23 curl 開啟原文比對）<br>[Disp BBS ott 板〈[眼殘] 學弟，可以借我5塊錢嗎?〉（內文待核實）](https://disp.cc/b/ott/87Yu)（2026-10-23 curl 只確認標題，內文待核實） |
| 10 | card_reveal | 揭曉 | 你拿出那張「超限量卡」想給新同學看…… | 是，揭曉 card_trade(7) | [ETtoday：小一兒拿7張七龍珠卡換「限量寶可夢卡」，結果是一張商品吊牌](https://www.ettoday.net/news/20221025/2365423.htm)（2026-10-23 curl 開啟原文比對）<br>[未來親子：國小老師談「校園地下交易」](https://futureparenting.cwgv.com.tw/family/content/index/18810)（2026-10-23 curl 開啟原文比對） |
| 10 | pe_class | 老師的文字遊戲 | 體育課！全班衝到操場集合。班長跑來：「老師叫大家回教室，帶數 | 否 | [PTT Gossiping：體育課走到操場集合，又被班長叫回教室拿數學課本，老師說「走那麼遠，有運動到了」（共同經驗：找不到單一來源，附上討論串）](https://www.pttweb.cc/bbs/Gossiping/M.1627768020.A.7B7)（2026-10-23 curl 開啟原文比對）<br>[民視：國中音樂、體育課被借去上考科，監委申請自動調查（民間調查逾8成學生有被借課經驗）](https://www.ftvnews.com.tw/news/detail/2020A12W0053)（2026-10-23 curl 開啟原文比對） |
| 11 | honesty | 老師的文字遊戲 | 教室的窗戶破了。老師說：「是誰？說實話就不罰你。」其實是你踢 | 否 | [Disp BBS（PTT StupidClown 轉）〈[童年] 誠信的重要〉：誠實說「沒辦法保證」，被罰半蹲兩次](https://disp.cc/b/Stupid/9Bjz)（2026-10-23 curl 開啟原文比對）<br>[未來親子：乖孩子受的傷最重](https://futureparenting.cwgv.com.tw/family/content/index/5947)（2026-10-23 curl 確認標題） |
| 11 | slurpee | 兌現的約定 | 附近便利商店說：段考考100分，可以拿考卷換一杯思樂冰。 | 否 | [ETtoday（Dcard 轉述）：國小「100分換思樂冰」，98分當場哭，下次考到100分如願換到](https://www.ettoday.net/news/20230526/2507013.htm)（2026-10-23 curl 開啟原文比對） |
| 12 | lend_reveal | 揭曉 | （三年前那5塊錢） | 是，揭曉 lend5(9) | [PTT StupidClown〈[童年] 所以是欠多少錢〉：借100元只還50元，理由是「只花了50」](https://www.pttweb.cc/bbs/StupidClown/M.1418036788.A.1DF)（2026-10-23 curl 開啟原文比對）<br>[Disp BBS ott 板〈[眼殘] 學弟，可以借我5塊錢嗎?〉（內文待核實）](https://disp.cc/b/ott/87Yu)（2026-10-23 curl 只確認標題，內文待核實） |
| 13 | free_gift | 網友 | 遊戲社團有人說「免費送限定造型」，只要把手機收到的驗證碼傳給 | 是（15歲揭曉） | [TVBS：手遊FB社團說要「贈禮」，孩子傳了驗證碼，媽媽遭小額盜刷](https://news.tvbs.com.tw/life/1950036)（2026-10-23 curl 開啟原文比對）<br>[防詐雷達：遊戲點數詐騙](https://fraud.tw/guide/gaming-points)（2026-10-23 curl 確認標題） |
| 15 | quiz | 老師的文字遊戲 | 老師說：「明天只是小考，不用緊張。」 | 否 | [PTT PT-97〈驚天動地普化小考〉（共同經驗：找不到單一來源，附上討論串）](https://www.ptt.cc/bbs/PT-97/M.1222946647.A.310.html)（依 WebSearch 摘錄核對）<br>[Dcard 輔大板〈教授的嘴騙人的鬼〉：說「一定考」結果沒考（共同經驗：找不到單一來源，附上討論串）](https://www.dcard.tw/f/fju/p/239107778/b/7)（原站擋自動連線，依 WebSearch 搜尋摘錄核對） |
| 15 | otp_reveal | 揭曉 | （兩年前那串驗證碼） | 是，揭曉 free_gift(13) | [TVBS：手遊FB社團說要「贈禮」，孩子傳了驗證碼，媽媽遭小額盜刷](https://news.tvbs.com.tw/life/1950036)（2026-10-23 curl 開啟原文比對）<br>[防詐雷達：遊戲點數詐騙](https://fraud.tw/guide/gaming-points)（2026-10-23 curl 確認標題） |
| 16 | lottery_reveal | 揭曉 | 你看到 YouTuber 把一整盒抽抽樂抽完：花了800塊， | 是，揭曉 lottery(9) | [PTT Childhood〈以前文具店有種抽籤集字換玩具〉：推文「永遠缺一個字」「大概是很多小朋友第一次被詐騙的東東」（共同經驗：找不到單一來源，附上討論串）](https://www.pttweb.cc/bbs/Childhood/M.1693736306.A.FC8)（2026-10-23 curl 開啟原文比對）<br>[PTT C_Chat 2026-04-26〈小時候玩過抽抽樂嗎〉：「黑暗大法，就是沒有師」（共同經驗：找不到單一來源，附上討論串）](https://www.pttweb.cc/bbs/C_Chat/M.1777180881.A.664)（依 WebSearch 摘錄核對）<br>[民視：YouTuber 實測柑仔店抽抽樂，花800元只換回250元，「童年充滿了謊言」](https://www.ftvnews.com.tw/news/detail/2021A07W0350)（2026-10-23 curl 開啟原文比對） |

**揭曉事件**（category=揭曉）都不需要玩家選擇：引擎依 require flag 自動顯示其中一個結果，所以不會增加路徑分支。

**新增 flag**：checks_first（從小習慣確認，即任務中的 verify_habit；童年任一「先問／先確認」選項都會設定）、trusts_adults（容易相信大人）、park_promise／park_pinky、promise_broken／promise_kept、bought_chick、traded_card／card_scammed、chased_lottery／learned_odds、lent_5／trust_repaid、told_truth、gave_otp／otp_scammed。新增 missed_rigged_odds、missed_otp_share（已補 red_flag_texts）。（v0.5：promise_broken／promise_kept／bought_chick 已刪除，見下方「童年 flag 處理」。）既有人生 flag 與事件 id 全部保留。

**共同經驗**（標題含「共同經驗」的來源）：抽抽樂永遠缺一字、校門口小雞、體育課被借、老師說「只是小考」。**待核實**：Leo 舉的「小考變三張A4」沒有找到完全對應的單一貼文，目前附相近的討論串，標為共同經驗；Dcard（403）和 C_Chat 依搜尋摘錄核對；Disp ott〈學弟借5塊〉、防詐雷達、未來親子 5947 只用 curl 確認過標題，內文待核實。

**路由順序**：birth → shot(4) → promise_park(5) → school_gate(6) → park_reveal(7) → card_trade(7) → hongbao(8) → lottery(9) → lend5(9) → card_reveal(10) → pe_class(10) → honesty(11) → slurpee(11) → lend_reveal(12) → first_phone(12) → free_gift(13) → game_trade(14) → quiz(15) → otp_reveal(15) → lottery_reveal(16) → part_time(17) → hongbao_result(18) → …

**平衡**：初始存款下限從 70000 調到 80000，抵銷童年的小額支出和隨機性。

**驗證**：路徑數約 262,144 × 2^11 ≈ 5 億條，DFS 無法窮舉。validate.py 以加法新增 `--sample [N]` 模式：每一步從可選的選項中均勻隨機挑一個，跑 N 次（預設 20 萬次，seed 42）；同時檢查每個事件和每個選項都至少走到一次、沒有死路、四個結局都到得了。執行方式：`python3 validate.py script-life.json --sample`。（v4.3 起 --sample 不再提前 exit，v4 欄位檢查與前提抽樣都會執行；v0.5 起還會跑 combined.py。）

| 結局 | 抽樣比例（N=200,000） |
|---|---|
| END_LIFE_STEADY | 46.0% |
| END_LIFE_STRETCHED（生活拮据） | 26.4%（低於 30%） |
| END_LIFE_HONGBAO_SAVED | 16.2% |
| END_LIFE_HONGBAO_GONE | 11.4% |

總覽圖 overview.png：黃底虛線框代表揭曉事件。

## v0.4 規格升級（對齊詐騙線 v4 規範）
- `meta.version` 改為 `0.4`。
- **presentation**：lottery、free_gift、game_trade、part_time、rent、mlm、insurance 這 7 個事件改成 `chat`，用虛構 app 名稱或「面對面」對話呈現；6 個揭曉事件（含 hongbao_result）改成 `timeskip`；其餘事件是 `card`。每個選項都有 `grid`（green／yellow／red）。
- **red_flag_anchors**：7 個 missed_* 都對應到某個事件的訊息：missed_rigged_odds→lottery/m2、missed_otp_share→free_gift/m2、missed_fake_receipt→game_trade/m2、missed_payroll_account_ask→part_time/m2、missed_no_checkin_photos→rent/m2、missed_vague_job_offer→mlm/m2、missed_sign_on_spot→insurance/m2。
- **結局**：每個結局都補上 title、title_emoji、grid_color、rarity_key、share_text、share_card（共用 SHARE_CARD）。
  - real_world_stat：四個結局都對應不到 165 的詐騙類型，所以 value_pct 為 null，附上 null_reason（v0.5：display 改為 null，前台不顯示，見規格第 6 節）。
  - requires_flags／forbids_flags：HONGBAO_GONE 需要 hongbao_lost 與 gave_hongbao，不能有 hongbao_returned；HONGBAO_SAVED 需要 hongbao_returned 與 gave_hongbao，不能有 hongbao_lost；STEADY 不能有 hongbao_lost、hongbao_returned、savings_depleted；STRETCHED 沒有限制。
  - STRETCHED 的預設文字改為「存款一路見底……」。只有同時持有 lent_money_lost 和 rosca_lost 時，才顯示原本「借出去的錢沒回來，跟會又倒了」的 text_variant，避免結局文字和實際經歷不符。
- **stats**：目前是空陣列，已經由 finalize_v42 處理。之後新增的統計會自動加上 self_calculated（bool）。
- **品牌字**：依 brand_hits 規則，把玩家會看到的 IG、LINE、PTT、「全家」改成社群、訊息、網友、一家人。來源名稱和網址不受影響。
- **meta.cross_line_flags._note**：改寫為「三條詐騙線都已透過 cross_line_modifiers 讀取這些 flag」，並註明童年新增的 flag 目前還沒有被任何詐騙線引用。
- **驗證**：`python3 validate.py script-life.json --sample` 會跑 v4／v4.2 欄位檢查，以及 5 萬次抽樣的結局前提檢查，結果 ALL OK。結局分布和 v0.4 童年擴充時相同：STEADY 46.0%、STRETCHED 26.4%、SAVED 16.2%、GONE 11.4%。

## v0.5 童年 flag 處理（2026-10-23，詳見 meta.childhood_flag_decisions）
| flag | 處理 | 作法／理由 |
|---|---|---|
| learned_odds | 接線 | 投資線 small_win：回憶提醒＋警覺+5 |
| card_scammed | 接線 | 假網拍線 ticket：回憶提醒（吊牌）＋警覺+3 |
| trust_repaid | 接線 | 假網拍線 aftermath：人際+5（比較願意找朋友），避免遊戲只教「什麼都不信」 |
| told_truth | 接線 | 車手線 family_notice：「說實話」回憶提醒，不改數值 |
| promise_broken／promise_kept | 刪除 flag（保留數值效果） | 接到詐騙線會變成「不要相信家人」，和「家人是保護力」的設計相反 |
| bought_chick | 刪除 flag（保留數值效果） | 和三條詐騙線都沒有合理關聯 |
| lent_5／gave_otp | 只在人生線內部使用 | 分別用來觸發 lend_reveal、otp_reveal 揭曉；結果已經由 trust_repaid、otp_scammed 帶到詐騙線 |

## v0.5 驗證結果（`python3 build.py --all`，2026-10-23 台北時間）
- 三條詐騙線 DFS 驗證：ALL OK。
- 人生線 `--sample` 單線：結局分布不變（STEADY 46.0%／STRETCHED 26.4%／SAVED 16.2%／GONE 11.4%）。END_LIFE_RECORD 標 combined_only，單獨跑人生線到不了。
- combined（N=20,000）：每局 2 條詐騙線的有 10,052 局、3 條的有 9,948 局；age_lived 都是 40；年齡全部不遞減；前提全部成立。

| 人生線結局 | 合併模式比率 |
|---|---|
| END_LIFE_STRETCHED | 39.3% |
| END_LIFE_STEADY | 35.7% |
| END_LIFE_HONGBAO_SAVED | 13.5% |
| END_LIFE_HONGBAO_GONE | 9.0% |
| END_LIFE_RECORD | 2.6% |

- **已知平衡問題（WARN，沒有修）**：
  - 人生線演到 35 歲時，心理的中位數大約只剩 22，存款最多大約 27 萬。
  - 因此在合併模式裡，投資線「借錢＋忽略行員」這條路一定會掉進 COLLAPSE（心理≤20），END_DEBT 抽不到；END_FAMILY_RIFT 也接近 0%。
  - 存款不夠付 50 萬，所以 BROKE 偏高（36.9%）。
  - 可以考慮的修法：在 return_map 或 entry 加上數值回復、調整人生線的心理消耗、或依存款等比例調整投資金額。需要設計決定，所以本輪不動。
- 死 modifier（info）：
  - 19 歲進車手線時，family_passphrase、lent_money_lost、pressure_signer 都還不可能出現，所以 mule_family_pass、mule_lent(_stat)、mule_pressure_signer 不會生效。
  - 27 歲進假網拍線時，family_passphrase（35 歲才設定）還不可能出現，所以 shop_family_pass 不會生效。
  - 這些 modifier 都保留：單獨遊玩詐騙線（也就是舊流程）時仍然有效。

## v0.6 合併人生模擬（Round 4，2026-10-23 台北時間）
規格在 `meta.scam_integration`，模擬器是 `combined.py`（`build.py --all` 會以 N=20000、seed 42 跑）。

### 進入規則（下列數值都是 design_assumption）
- 開局時，每條線各抽一次：`entry_age = base_age + randint(offset_min, offset_max)`，再抽 U(0,1) < probability 決定這一生會不會遇到。
  | 線 | 年齡窗 | 機率 | 觸發條件 |
  |---|---|---|---|
  | 車手 mule | 20 ±2（18–22） | 0.6 | flags_any [cash_strapped, wage_unpaid] |
  | 假網拍 shopping | 25 ±3（22–28） | 0.7 | 無 |
  | 假投資 investment | 37 −3/+2（34–39） | 0.6 | 存款 > 0 |
- 插入點：在人生事件 E 之後、下一個事件 N 之前，處理 `a_E ≤ entry_age < a_N` 的計畫。進入時才檢查 trigger，結束後回到 N。
- 年齡單調（flexible slot）：實際進入年齡 = max(計畫年齡, 上一條線結束年齡)。如果進入年齡 +1 會超過 a_N，就順延到下一個空檔；到 40 歲（LIFE_ROUTER）前都沒排進去，就算沒遇到。duration ≤ 1，所以 exit_age ≤ a_N。
- 進入前心理恢復：心理 +10（`pre_entry.mental_recovery`；design_assumption：兩段經歷之間有喘息）。
- 假投資金額隨存款等比縮放（`amount_scaling`）：`factor = max(存款, 50000) / 425000`，套用在所有負的存款效果（含 on_enter）。425000 是劇本原始假設的存款基準，50000 是下限，兩個數字都是 design_assumption。
- 分享卡年齡 = max(最後一個人生事件年齡, 各線 exit_age)，模擬結果全部是 40。

### 年齡×手法百分比
fromnineon 第三方整理的年齡×手法百分比標為 `verified:false`、`display:false`，附 `verify_note`。`age_basis.unverified_figures` 也一樣。**前端遇到 `display:false` 一律不顯示，不可當成官方數字。**

### 選項即時回饋（試玩回饋：選完看不到後果）
四份劇本的每個選項（包含 cross_line_modifiers 的 unlock_choice）都有兩個欄位，內容集中在 `outcomes.py`：
- `outcome_text`：選完立刻顯示，1–3 句。延遲揭曉的事件（card_trade、lend5、free_gift、hongbao、promise_park 等）只寫當下看得到的，不劇透。
- `log_text`：寫進人生紀錄的短句，最多 20 字。
`validate.py` 會檢查兩個欄位都存在且非空、`log_text` 不超過 20 字、沒有 BRAND_BAN 品牌。

### 合併模擬結果（最新 `build.py --all`，2026-10-23 台北時間；N=20000，seed 42；目標：每條線每個結局在進入者中 2%–40%）
- 一生遇到幾條詐騙線：0 條 9.9%、1 條 38.2%、2 條 39.7%、3 條 12.1%
- 人生結局：STEADY 37.6%、STRETCHED 35.4%、HONGBAO_SAVED 13.2%、HONGBAO_GONE 9.2%、RECORD 4.6%
- 車手線（41.4% 進入）：REFUSE 33.1、RESCUED 28.7、ACCOUNT 23.1、RECORD 4.7、STOPPED_ALONE 4.1、CONVICTED 3.4、CUT_OFF 2.9
- 假網拍線（70.3% 進入）：SAFE 24.5、TICKET_LOST 23.2、CS_DRAINED 21.2、SMALL_FEE 21.0、SILENT_COLLAPSE 10.1
- 假投資線（42.3% 進入）：SMALL_LOSS 38.8、EARLY 38.1、ALL_LOST 6.7、BROKE 5.5、COLLAPSE 4.4、FAMILY_RIFT 4.1、DEBT 2.5
- 人生線單獨抽樣（N=200000）：STEADY 46.1、STRETCHED 26.0、HONGBAO_SAVED 16.2、HONGBAO_GONE 11.7。
- 單線模擬用 `python3 rates.py script-<line>.json`（均勻選擇、無人生 flag）。

## v0.7 選項標籤改寫與新童年事件（Round 4 追加）
### 選項標籤規則（四份劇本）
- 標籤只寫玩家做了什麼動作，例如「借他」「說我也只剩5塊」。不劇透結果，也不做道德評價。標籤表在 `outcomes.py` 的 `L`。
- 結果有兩種呈現：
  - 當下的結果寫在 `outcome_text`。
  - 延遲的結果由之後的揭曉事件（timeskip）呈現；揭曉事件的內容也寫在它自己的 `outcome_text`。
- 原本把結果寫在標籤裡的揭曉事件（park_reveal、card_reveal、lend_reveal、otp_reveal、lottery_reveal、hongbao_result、elder），結果都已搬到 outcome_text。
- `validate.py` 會檢查：
  - 標籤 ≤15 字。
  - 標籤不含 `LABEL_BLOCKLIST` 裡的字詞：騙、損失、賠、後悔、成功、失敗、才還、被抓、識破、真相、原來、結果、紅燈、警訊、＝、不合理、太緊張、正常工作、嚇壞、崩潰、倒會、已讀不回。
  - 檢查範圍包含 unlock_choice 和 rewrite_text(choice_text)。
- 本版沒有新增隨機結果分支：引擎格式尚不支援同一選項隨機分流，所有結果仍由選項和 flag 決定。

### 新事件：姐姐借100還50
- 來源：「Leo 提供的個人經驗」，kind: personal_experience，沒有網址，verified:false。
- 流程：
  - **sister_repay（8歲，接在 hongbao 之後）**：姐姐說「我只花了50，所以還你50」。
    - 「好喔，收下」：設 sister_short、missed_reasonable_talk。
    - 「等等，我算一下」：設 counted_change、checks_first，警覺+3、人際+2。
  - **sister_reveal（9歲，接在 lottery 之後，延遲揭曉）**：在房間數存錢筒。
    - 收下的人這時才發現少了50，心裡冒出「我姐壞壞欸」，姐姐吐吐舌頭補上。
    - 當場算的人發現一百元都在。
  - 兩條路的手足關係都維持溫暖。
- 紅旗與教訓：
  - 紅旗 missed_reasonable_talk：話術聽起來合理，不代表數字是對的。
  - 教訓：用輕鬆的語氣認真求證。
- 接到假網拍線：counted_change 觸發 `shop_sister_math`，在 fee_more m2 加一則回憶插話。只加提醒、不改數值，所以結局分布不受影響。

### v0.7.1 文字審稿（Round 4 收尾）
- 逐條檢查 140 個選項的 outcome_text／log_text。改寫 7 句：拿掉真實品牌（「思樂冰」→冰沙、「YouTuber」→網紅，事件內文同步改；來源標題保留原文）、避免劇透（insurance 當場簽不再寫「後來繳不起解約」，延後到結局呈現）、改掉說教或生硬句（slurpee 不去換、hongbao_result 回顧）。
- 已知限制：BRAND_BAN 沒擋到「思樂冰」「YouTuber」，建議之後加入清單。

## v4.7 補充
- **random:true 選項**：一個按鈕、結果隨機。`outcomes[]` 每項有 `probability`（總和＝1）、`outcome_text`、`log_text`、`effects`、`flags_set`、`grid`（可選 `next`）；`random_note.design_assumption: true` 標明機率是設計假設。引擎順序：先選選項，再抽一次 U(0,1) 決定分支。目前只用於人生線 35 歲「接爸媽的電話」（family_passphrase／elder_near_miss 各 0.5）。
- **cross_line_modifiers[].mode**：`all`（預設）或 `standalone_only`＋`mode_note`。standalone_only＝合併模式下進場年齡內拿不到該 flag（mule_lent、mule_lent_stat、mule_pressure_signer、mule_family_pass、shop_family_pass），只在單線模式觸發；validate／combined 只列為 info。合併模式觸發不了卻沒標記的修正，combined.py 會判為錯誤。
- **help_resources**：每個結局都必須有，第一筆是 165 反詐騙專線；有心理傷害的結局加 1925 安心專線、1995 生命線；車手線刑事結局加法律扶助基金會 412-8518（https://www.laf.org.tw/tel-ext）。
- 品牌黑名單新增「思樂冰」「YouTuber」。
