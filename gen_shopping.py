import json
from common import finalize,apply_v4,apply_cross,M,SHARE_CARD,stat_null,share_of_cases,HL,COUNTY_SRC,DASH_SRC,DASH_MONTH,DASH_TYPE,calc_avg,COUNTY_DASH,NO_OFFICIAL,DB as DB165
S={14:"https://www.ptt.cc/bbs/Bunco/M.1709868996.A.A05.html",15:"https://www.dcard.tw/f/mood/p/260348727",
16:"https://www.dcard.tw/f/entertainer/p/231476276",17:"https://www.dcard.tw/f/mayday/p/257524987",
18:"https://www.dcard.tw/f/anti_fraud/p/241739469",19:"https://www.ptt.cc/bbs/Bunco/M.1323108038.A.042.html",
20:"https://www.ptt.cc/bbs/Bunco/M.1188225370.A.3CC.html"}
FN="https://fromnineon.com/data/taiwan-fraud-statistics/"
def src(*k): return [{"story_id":x,"url":S[x]} if isinstance(x,int) else x for x in k]
ST={"name":"韭點開始整理165資料","url":FN}
def C(t,e,n,set_flags=None): return {"text":t,"effects":e,"next":n,"flags":{"set":set_flags or [],"require":[]}}
E=[]
def ev(i,a,t,c,s,**k): E.append({"id":i,"age":a,"text":t,"choices":c,"sources":s,**k})
R="END_ROUTER"
ev("birth",0,"你出生在{county}的{family}家庭。這一生只有一次，選擇無法重來。",[C("長大",{},"teen")],[COUNTY_SRC,COUNTY_DASH])
ev("teen",17,"你加入了好幾個二手拍賣和追星社團，每天都有人喊「私」。",
 [C("記住：交易盡量走有保障的官方管道",{"警覺":8},"ticket"),C("覺得私下交易比較便宜方便",{},"ticket")],src(16,ST))
ev("ticket",20,"你最愛的歌手開演唱會，官方一下就賣光。社團裡有人說：『臨時不能去，原價讓票，私訊。』還傳來訂單截圖。",
 [C("只透過官方轉售或主辦公告的管道買票",{"警覺":12},"cheap_item",set_flags=["spotted_ticket"]),
  C("仔細看截圖，發現字沒對齊、主辦根本沒有電子票，放棄",{"警覺":10},"cheap_item",set_flags=["spotted_ticket"]),
  C("怕被搶走，先匯款11,400元",{"存款":-11400,"心理":-10},"ticket_blocked",set_flags=["paid_ticket","missed_ticket_screenshot","missed_transfer_only"])],src(16,17,18))
ev("ticket_blocked",20,"匯款後，對方封鎖了你。你這才發現，社團裡還有好幾個人買了同一組票號。",
 [C("保留對話和匯款紀錄，打165、到派出所報案",{"警覺":10,"心理":-5},"cheap_item",set_flags=["reported"]),
  C("覺得丟臉，算了",{"心理":-10},"cheap_item")],src(16,17,18))
ev("cheap_item",23,"社群平台上有人用原價賣你找很久的限量商品。賣家說「常被放鳥」，要你先點他給的超商寄貨平台連結付運費。網址看起來很像，但又好像哪裡怪怪的。",
 [C("只從官方 App 進入下單，不點陌生連結",{"警覺":12},"fake_cs",set_flags=["spotted_link"]),
  C("付了38元運費",{"存款":-38},"fee_more",set_flags=["paid_small","missed_fake_link"])],src(15))
ev("fee_more",23,"付款後，畫面跳出「賣場未完成實名制，交易被凍結」，要你聯繫「客服」處理。付款的收款戶名竟然是某個基金會。",
 [C("戶名對不上就是警訊，停止並打給銀行和165",{"警覺":12},"fake_cs",set_flags=["stopped_early"]),
  C("聯繫「客服」看看",{"警覺":-5},"cs_call",set_flags=["missed_account_name"])],src(15,14))
ev("fake_cs",26,"某天，你接到自稱網購平台客服的電話，說你的訂單「誤設成分期」，接著又有「銀行專員」來電，來電顯示看起來很正式。",
 [C("掛斷，自己查官方客服電話回撥確認",{"警覺":12},R,set_flags=["spotted_cs"]),
  C("照著對方說的步驟處理",{"警覺":-10},"cs_call",set_flags=["missed_installment_call"])],src(19,20,14))
ev("cs_call",26,"「專員」語氣很急，說不處理每個月都會被扣款，要你到ATM或網銀照指示操作，還一直要你別掛電話。",
 [C("想起ATM和網銀根本沒有「解除分期」功能，掛斷打165",{"警覺":15,"心理":-5},R,set_flags=["stopped_early"]),
  C("照做，按了好幾次確認",{"存款":-15000,"心理":-25},"aftermath",set_flags=["fake_cs_paid","missed_atm_instruction","missed_stay_on_line"])],src(19,20))
ev("aftermath",26,"操作完後，餘額少了一大截。路人幫你打了165，但錢已經轉走，來不及攔下。",
 [C("報案，凍結帳戶申請",{"心理":5},R,set_flags=["reported"]),
  C("不想面對",{"心理":-10,"人際":-5},R)],src(19))
ev(R,30,"多年後回頭看這段經歷……（引擎依 ending_rules 自動判定結局，不顯示選項）",[C("回顧",{},"__EVAL__")],HL,router=True)
def card(i,t): return {"story_id":i,"summary":t,"url":S[i],"note":"去識別化改寫，細節以原文為準"}
EN=[
 {"id":"END_CS_DRAINED","priority":1,"conditions":{"flags_all":["fake_cs_paid"]},
  "text":"一通「解除分期」的電話，讓你在幾分鐘內損失了近1.5萬元。你本來以為自己很精明。",
  "reason_texts":[{"flag":"savings_depleted","text":"這筆錢是你全部的存款（存款≤0）。"},
   {"flag":"mental_collapse","text":"你一直責怪自己，心理狀態跌到谷底（心理≤20）。"},
   {"flag":"reported","text":"你報了案，但錢已經轉走，追不回來。"}],
  "case_card":card(19,"一位自認精明的網購者接到假客服說「誤設12期」，接著假銀行主任來電，要他到ATM操作「測試」，被騙近1.5萬；路人幫忙打165，但來不及凍結。"),
  "missed_red_flags":["ATM和網銀沒有「解除分期」功能","來電要你別掛電話、照步驟操作","客服和銀行輪流打來"],"sources":src(19,20,ST)+HL},
 {"id":"END_TICKET_LOST","priority":2,"conditions":{"flags_all":["paid_ticket"]},
  "text":"你沒看到那場演唱會，還損失了一萬多元。報案之後要等開庭，錢遲遲拿不回來。",
  "reason_texts":[{"flag":"reported","text":"你報了案，但訴訟很漫長。"}],
  "case_card":card(18,"一名大學生在網路上買原價讓票，匯款11,400元後被封鎖，報案後等待開庭；網友提醒收款的可能是人頭帳戶。"),
  "missed_red_flags":["原價讓熱門票，只收匯款","訂單截圖有修圖痕跡","沒有透過官方轉售"],"sources":src(18,16,17,ST)+HL},
 {"id":"END_SMALL_FEE","priority":3,"conditions":{"flags_all":["paid_small"]},
  "text":"你只損失了幾十元，但差一點就被一步步引到更大的陷阱裡。",
  "reason_texts":[{"flag":"stopped_early","text":"你在第二個警訊出現時就停下來了。"}],
  "case_card":card(15,"一位買家在社群平台看到有人用原價賣限量吊飾，被要求點假的超商寄貨平台連結先付運費38元；之後對方又說「沒有實名制」，要他繼續處理。他打給銀行，沒有再付款。"),
  "missed_red_flags":["賣家給的連結不是官方網址","收款戶名跟賣家對不上"],"sources":src(15,14,ST)+HL},
 {"id":"END_SAFE","priority":4,"conditions":{"flags_none":["paid_ticket","paid_small","fake_cs_paid"]},
  "text":"三次陷阱你都避開了。你把經驗分享到社團，提醒其他人。",
  "case_card":card(20,"一位網購者接到自稱網拍商店的電話說「設錯分期」，接著有顯示銀行真實號碼的來電，但他沒有照做，沒有受騙。"),
  "missed_red_flags":["你抓到了：原價讓票只收匯款、陌生付款連結、要求到ATM操作"],"sources":src(20,16,ST)+HL},
]
data={"meta":{"title":"80億分之1：假網拍線","version":"0.1","language":"zh-TW","one_life":True,
 "content_policy":"只描述受騙者看到什麼、經歷什麼，不寫詐騙的操作手法",
 "amount_note":"事件中的金額取材自對應案例：票款11,400元（#18）、運費38元（#15）、解除分期約1.5萬元（#19，原案「近1.5萬」）；均為劇情設定，但與原案相近。"},
 "ending_rules":{"evaluation":"依 priority 由小到大檢查，第一個成立者為結局","fallback":"END_SAFE",
  "condition_grammar":{"flags_all":"全部都要有","flags_any":"至少一個","flags_none":"都不能有","any_of":"子條件任一成立"}},
 "stats":[
  dict(DASH_TYPE["假網拍"],note="占當月件數32.6%、財損8.1%（10,775件、39億3,572.3萬換算後一致）",verify_note="2026-10-23 依儀表板截圖核對，與 fromnineon 的 3,513 件一致；官方來源改為 165 儀表板；截圖 165dashboard/04_fraud_type_top5_115-09.webp"),
  calc_avg("假網拍詐騙每件平均損失（自行換算）",32066,3513,"115年9月全月"),*DASH_MONTH[:2],
  {"label":"2025年7月起，假網拍每月件數都多於假投資","value":"敘述","period":"2025年7月至2026年9月","verified":True,"verify_note":"fromnineon 整理；"+NO_OFFICIAL+"（儀表板只有115-09、115-10月資料）","source":FN},
  {"label":"18–23歲詐欺被害人中，假網路拍賣（購物）占比","value":37.27,"unit":"%","period":"2026年1–7月，警政統計通報","verified":True,"verify_note":"fromnineon 整理；"+NO_OFFICIAL+"（儀表板沒有年齡分布）","source":FN}],
 "stats_sources":[ST,DASH_SRC],
 "player_init":{"stats":{"存款":{"min":0,"init_range":[20000,200000]},"警覺":{"min":0,"max":100,"init_range":[15,45]},
   "人際":{"min":0,"max":100,"init_range":[30,70]},"心理":{"min":0,"max":100,"init_range":[40,80]}},
  "county_pool":["臺北市","新北市","桃園市","臺中市","臺南市","高雄市","新竹市","新竹縣","基隆市","苗栗縣","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"],
  "family_pool":[{"name":"小康","存款_mod":0},{"name":"單親","存款_mod":-0.3,"心理":-5},{"name":"務農","人際":5},{"name":"經商","存款_mod":0.5}],
  "start_event":"birth","flags":[]},
 "events":E,"endings":EN}
RF={"missed_ticket_screenshot":"訂單截圖字沒對齊，主辦方也根本沒有電子票。",
 "missed_transfer_only":"原價讓熱門票卻只收匯款，不走官方轉售。",
 "missed_fake_link":"賣家給的付款連結不是官方網址。",
 "missed_account_name":"收款戶名是一個基金會，跟賣家對不上。",
 "missed_installment_call":"「誤設分期」的電話，是假網拍裡最常見的開場。",
 "missed_atm_instruction":"ATM和網銀根本沒有「解除分期」功能。",
 "missed_stay_on_line":"對方一直要你別掛電話，就是不讓你有時間查證。"}
finalize(data,RF)
# ================= v4：沉浸呈現 =================
SHOP={"app":"shop_like","app_display_name":"拍拍集（虛構）","theme":"fictional_orange_free"}
CHAT={"app":"line_like","app_display_name":"聊聊 Chatto（虛構）","theme":"fictional_green_free"}
V4={
 "ticket":{"presentation":"chat","pressure":{"timer_s":30,"can_disable":True,"label":"「很多人在問」"},"chat":{**CHAT,"contact":{"name":"讓票的小雨","avatar":"placeholder_silhouette","status":"在線上"},"messages":[
   M("m1","scammer","臨時不能去，原價讓票～"),M("m2","scammer","（傳來訂單截圖）",1000,"image"),
   M("m3","scammer","只收轉帳喔，很多人在問，先匯先贏",900),M("m4","player","截圖上的字好像有點歪……")]}},
 "ticket_blocked":{"presentation":"chat","chat":{**CHAT,"contact":{"name":"讓票的小雨","avatar":"placeholder_silhouette","status":"—"},"messages":[
   M("m1","player","我匯好了，票什麼時候給我？"),M("m2","system","你無法傳送訊息給此用戶",1500),
   M("m3","player","（社團裡好幾個人說買到同一組票號……）")]}},
 "cheap_item":{"presentation":"chat","chat":{**SHOP,"contact":{"name":"賣家 小晴","avatar":"placeholder_silhouette","status":"在線上"},"messages":[
   M("m1","scammer","限量款原價給你～我常被放鳥，要先付運費喔"),M("m2","scammer","（傳來一個看起來很像官方的超商寄貨連結）",1000,"link"),
   M("m3","player","網址好像跟平常的不太一樣？")]}},
 "fee_more":{"presentation":"chat","chat":{**SHOP,"contact":{"name":"賣家 小晴","avatar":"placeholder_silhouette","status":"在線上"},"messages":[
   M("m1","system","賣場未完成實名制，交易已凍結",800),M("m2","scammer","你要聯繫客服解凍喔，不然錢會卡住"),
   M("m3","player","（付款戶名怎麼是某個基金會？）")]}},
 "fake_cs":{"presentation":"chat","chat":{"app":"phone_call","app_display_name":"來電","theme":"neutral","contact":{"name":"自稱 網購平台客服","avatar":"placeholder_silhouette","status":"通話中"},"messages":[
   M("m1","scammer","您好，您的訂單被誤設成分期付款"),M("m2","scammer","等一下會有銀行專員打給您協助取消",1400),
   M("m3","player","（來電顯示看起來很正式……）")]}},
 "cs_call":{"presentation":"chat","pressure":{"timer_s":25,"can_disable":True,"label":"「今天不處理就會扣款」"},"chat":{"app":"phone_call","app_display_name":"來電","theme":"neutral","contact":{"name":"自稱 銀行專員","avatar":"placeholder_silhouette","status":"通話中"},"messages":[
   M("m1","scammer","不處理的話，每個月都會被扣款喔",900),M("m2","scammer","我現在一步一步帶您處理，很快的"),
   M("m3","scammer","過程中千萬不要掛電話",700),M("m4","player","（好急……可是哪裡怪怪的）")]}},
}
ANCH={"missed_ticket_screenshot":[{"event":"ticket","message":"m2"}],"missed_transfer_only":[{"event":"ticket","message":"m3"}],
 "missed_fake_link":[{"event":"cheap_item","message":"m2"}],"missed_account_name":[{"event":"fee_more","message":"m3"}],
 "missed_installment_call":[{"event":"fake_cs","message":"m1"}],"missed_atm_instruction":[{"event":"cs_call","message":"m2"}],
 "missed_stay_on_line":[{"event":"cs_call","message":"m3"}]}
SH=share_of_cases("假網拍","假網拍")
SH_CS=dict(SH,verify_note=SH["verify_note"]+"；儀表板沒有說明「假客服解除分期」案件是否歸在假網拍類，這裡依民間常見歸類引用，待核實")
EV4={
 "END_CS_DRAINED":{"title":"被一通電話帶走的人","title_emoji":"📞","grid_color":"red","real_world_stat":SH_CS,"share_text":"一通「解除分期」的電話，幾分鐘就騙走我的錢。"},
 "END_TICKET_LOST":{"title":"錯過演唱會的人","title_emoji":"🎫","grid_color":"red","real_world_stat":SH,"share_text":"我沒看到演唱會，還賠了一萬多。"},
 "END_SMALL_FEE":{"title":"只付了運費的人","title_emoji":"📦","grid_color":"yellow","real_world_stat":SH,"share_text":"我只損失幾十元，差點就掉進更大的坑。"},
 "END_SAFE":{"title":"三關全破的人","title_emoji":"🛡","grid_color":"green","real_world_stat":stat_null("沒有受騙的人不會出現在受理統計中，沒有對應的官方數字"),"share_text":"三個網購陷阱我都避開了。你呢？"}}
for k,v in EV4.items(): v.update({"rarity_key":"shop_"+k,"share_card":SHARE_CARD})
META4={"presentation_notes":"同投資線：presentation='chat' 以全螢幕仿聊天室呈現；畫面一律使用虛構 app 名稱與外觀。聊天內容只呈現詐團話術與受害者反應，不寫可照做的操作步驟。",
 "no_pressure_mode":{"available":True,"default":False,"effect":"關閉所有 pressure 倒數；不影響劇情與結局","min_timer_s":20},
 "life_grid":{"bucket_years":5,"colors":{"green":"安全","yellow":"有疑點","red":"受騙損失"},"rule":"同投資線"},
 "real_world_stat_notes":"real_world_stat 是假網拍占 115-09 全國受理件數的比例（3,513÷10,775），不是結局稀有度。"}
apply_v4(data,V4,ANCH,EV4,META4)
def CC(t,e,n,sf=None): return {"text":t,"effects":e,"next":n,"flags":{"set":sf or [],"require":[]},"grid":"green","cross_line":True}
apply_cross(data,[
 {"id":"shop_game_scammed","if_flags":{"all":["game_scammed"]},"target":{"event":"__INIT__"},"effect":{"type":"stats_delta","stats":{"警覺":5}},
  "note":"14歲遊戲交易被騙過，學過一次教訓（人生線 README 建議 +5）"},
 {"id":"shop_game_scammed_msg","if_flags":{"all":["game_scammed"]},"target":{"event":"ticket"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m3","from":"內心","text":"「先匯款」……跟國中買遊戲裝備被騙那次好像"}},"note":"喚起舊經驗"},
 {"id":"shop_pressure_signer","if_flags":{"all":["pressure_signer"]},"target":{"event":"cs_call"},"effect":{"type":"stats_delta","stats":{"警覺":-8}},
  "note":"容易在「當場決定」的壓力下照做"},
 {"id":"shop_family_pass","if_flags":{"all":["family_passphrase"]},"target":{"event":"cs_call"},
  "effect":{"type":"unlock_choice","choice":CC("想起家裡約好的規矩：接到要錢、要操作的電話，先掛斷，用通關密語跟家人確認。你掛斷了，打給家人和165",{"警覺":15,"人際":3},"END_ROUTER",["stopped_early"])},
  "note":"本線沒有假親友事件；通關密語的『先掛斷、再查證』習慣套用在假客服來電"},
 {"id":"shop_evidence","if_flags":{"all":["evidence_habit"]},"target":{"event":"ticket_blocked","choice":0},
  "effect":{"type":"rewrite_text","field":"choice_text","text":"你本來就有截圖存證的習慣：對話、截圖、匯款紀錄都在，打165、到派出所報案"},"note":"保留證據讓報案更完整（不保證追回）"},
 {"id":"shop_lent","if_flags":{"all":["lent_money_lost"]},"target":{"event":"aftermath"},"effect":{"type":"stats_delta","stats":{"心理":-5}},
  "note":"之前借錢被倒，再次損失更難承受"}])
data["cross_line_modifiers"]+=[
 {"id":"shop_checks_first","if_flags":{"all":["checks_first"]},"target":{"event":"ticket"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"查證提示","text":"小時候的習慣浮現：先確認再說。這張截圖能向主辦方查證嗎？"}},
  "note":"人生線 README 建議：第一個可疑訊息自動顯示查證提示"},
 {"id":"shop_otp_link","if_flags":{"all":["otp_scammed"]},"target":{"event":"cheap_item"},"effect":{"type":"stats_delta","stats":{"警覺":5}},
  "note":"小時候傳過驗證碼被騙；遇到連結題警覺 +5（人生線 README 建議）"}]
# ================= v4.2：結局前提（文字必須與實際路徑一致） =================
from common import finalize_v42
ENX={x["id"]:x for x in data["endings"]}
# 修正矛盾：原 END_TICKET_LOST 一律寫「報案之後要等開庭」，但選「覺得丟臉，算了」的玩家沒有報案
ENX["END_TICKET_LOST"].update({"text":"你沒看到那場演唱會，還損失了一萬多元。",
  "text_variants":[
   {"when":{"label":"reported","flags_all":["reported"]},"requires_flags":["reported"],
    "text":"你沒看到那場演唱會，還損失了一萬多元。報案之後要等開庭，錢遲遲拿不回來。"},
   {"when":{"label":"silent","flags_none":["reported"]},"forbids_flags":["reported"],
    "text":"你沒看到那場演唱會，還損失了一萬多元。你覺得丟臉沒有報案，這筆錢就這樣不見了。"}],
  "requires_flags":["paid_ticket"],"forbids_flags":["fake_cs_paid"]})
ENX["END_CS_DRAINED"].update({"requires_flags":["fake_cs_paid"],"forbids_flags":[]})
ENX["END_SMALL_FEE"].update({"requires_flags":["paid_small"],"forbids_flags":["paid_ticket","fake_cs_paid"]})
ENX["END_SAFE"].update({"requires_flags":[],"forbids_flags":["paid_ticket","paid_small","fake_cs_paid"]})
# ================= v4.4：更重的負面結局（家人失和／心理崩潰／被親友切割） =================
# 原則：只寫後果，不寫任何犯罪操作；提到輕生只用非畫面化描述，並附求助資源。
HELP3=[{"name":"1925安心專線（衛福部，24小時免付費）","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html","verified":True,"verify_note":"2026-10-23 curl HTTP 200"},
 {"name":"1995生命線協談專線","url":"https://www.life1995.org.tw/","verified":True,"verify_note":"2026-10-23 curl HTTP 200"},
 {"name":"165反詐騙諮詢專線（警政署）","url":"https://165.npa.gov.tw/","verified":True}]
HELP_LINE="如果你或身邊的人也有類似的感受：1925 安心專線（24小時免付費）、1995 生命線、165 反詐騙專線。被騙不是你的錯。"
DK={"shutien":{"name":"書田診所衛教新聞稿：誤信詐騙陷自責憂鬱（2024-05-14，含三名受害者個案）","url":"https://www.shutien.org.tw/pr_news_detail.aspx?newsid=1855&unitid=51","verified":True,"verify_note":"2026-10-23 curl HTTP 200，依原文核對"},
 "cna_dep":{"name":"中央社：女子網戀遭詐自責憂鬱 醫籲注意情緒變化（2024-05-14）","url":"https://www.cna.com.tw/news/ahel/202405140092.aspx","verified":True,"verify_note":"2026-10-23 curl HTTP 200，依原文核對"},
 "pts_dep":{"name":"公視新聞網：財產遭騙自我批判致身心症狀 精神科醫師：詐騙憂鬱症增（2024-05-14）","url":"https://news.pts.org.tw/article/694944","verified":True,"verify_note":"2026-10-23 curl HTTP 200，依原文核對"},
 "ly_report":{"name":"立法院法制局研究報告：詐欺案件中被害人保護制度之研究－以心理支持方案為中心","url":"https://www.ly.gov.tw/Pages/ashx/File.ashx?FilePath=%7E%2FFile%2FAttach%2F255779%2FFile_19861748.pdf","verified":False,"verify_note":"未取得原文：curl 逾時，只依 WebSearch 搜尋摘錄核對（摘錄提到詐騙造成心理創傷、家庭破裂與社會排擠，沒有量化統計）；請人工開啟 PDF 確認"},
 "nown_cutoff":{"name":"NOWnews：家屬公開切割涉嫌擔任車手的親人（2024-05-02）","url":"https://www.nownews.com/news/6418759","verified":True,"verify_note":"2026-10-23 curl HTTP 200；當事人當時為涉嫌、被捕階段，遊戲內去識別化"},
 "cna_parents":{"name":"中央社：少年詐騙車手獲2千 父母判賠157萬（2016-05-23）","url":"https://www.cna.com.tw/news/asoc/201605230144.aspx","verified":True,"verify_note":"2026-10-23 curl HTTP 200"},
 "civ187":{"name":"民法§187 未成年人侵權，法定代理人連帶賠償","url":"https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=187"}}
NO_CONSEQ="165 儀表板與官方統計只分詐騙類型與財損，沒有『受騙後憂鬱／家庭失和／被親友切割』的分類或人數；下方類型比例只代表詐騙類型，不代表這個結局有多常見"
def dcard(k,summary): return {"story_id":k[0],"summary":summary,"url":k[1],"note":"去識別化改寫，細節以原文為準"}
data["endings"].append({"id":"END_SILENT_COLLAPSE","priority":0.5,
 "conditions":{"flags_all":["fake_cs_paid","mental_collapse"],"flags_none":["reported"]},
 "text":"你沒有報案，也沒有告訴任何人。你一直重播那通電話，覺得自己怎麼這麼笨；開始睡不著、吃不下，上課上班都出錯，連訊息都不想回。後來你終於撐不住，去看了身心科，才知道這是被騙後很常見的創傷反應，需要治療，也需要有人陪。"+HELP_LINE,
 "text_variants":[
  {"when":{"label":"friend_noticed","flags_all":["has_support"]},"requires_flags":["has_support"],
   "text":"你沒有報案，也沒有告訴任何人。你一直重播那通電話，覺得自己怎麼這麼笨；開始睡不著、吃不下。是朋友發現你不對勁，一直追問，你才哭著說出來。朋友陪你去報案、去看身心科，你才知道這是被騙後很常見的創傷反應，不是你的錯。"+HELP_LINE}],
 "reason_texts":[{"flag":"fake_cs_paid","text":"你照「客服」的指示操作，錢被轉走。"},
   {"flag":"mental_collapse","text":"自責和羞愧讓你的心理狀態跌到谷底（心理≤20）。"},
   {"flag":"isolated","text":"你把自己關起來，沒有人能拉你一把（人際≤15）。"}],
 "case_card":{"summary":"這個結局目前沒有對應的真實個案：我們找不到手法明確是假網購或假客服、又記錄了求助後康復過程的公開報導，所以不放案例。精神科醫師的經驗是，多數詐騙受害者需要3個月到1年消化情緒，就醫並有親友陪伴會有幫助（見下方來源）。","note":"v4.4 審查修正：沒有合適的個案，不放案例"},
 "case_card_note":"找不到手法明確是假網購／假客服、又有求助後康復紀錄的公開個案，所以這個結局不放個案卡（v4.4 審查修正）",
 "missed_red_flags":["真的客服不會叫你到ATM或網銀「解除分期」","接到電話要掛掉，自己打官方客服或165查證","被騙後不報案、不說出來，只會讓你一個人越陷越深"],
 "sources":[DK["cna_dep"],DK["pts_dep"],DK["shutien"],DK["ly_report"],{"name":"台大社工所碩論：詐欺被害人之創傷反應與社會支持（華藝線上圖書館）","url":"https://www.airitilibrary.com/Article/Detail/U0023-0709201116234200","verified":True,"verify_note":"2026-10-23 curl HTTP 200；研究指出社會支持越多，創傷反應越輕"}]+src(19,20)+HELP3,
 "requires_flags":["fake_cs_paid","mental_collapse"],"forbids_flags":["reported"],
 "title":"一個人吞下所有自責的人","title_emoji":"🌫","grid_color":"red","rarity_key":"shop_END_SILENT_COLLAPSE",
 "real_world_stat":dict(SH_CS,consequence_note=NO_CONSEQ),"share_text":"被騙之後我什麼都沒說，這是最錯的一步。","share_card":SHARE_CARD,"help_resources":HELP3})
data["ending_rules"]["evaluation"]+="（v4.4：SILENT_COLLAPSE 0.5 → CS_DRAINED 1 …）"
# ================= v4.5：童年 flag（card_scammed、trust_repaid） =================
data["cross_line_modifiers"]+=[
 {"id":"shop_card_scammed","if_flags":{"all":["card_scammed"]},"target":{"event":"ticket"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"回憶","text":"你想起小時候換到的那張「超限量卡」，最後發現只是吊牌。沒親眼確認過的東西，先別急著換。"}},
  "note":"童年換卡被騙；私下交易、只看截圖的情境多一個提醒"},
 {"id":"shop_card_scammed_stat","if_flags":{"all":["card_scammed"]},"target":{"event":"ticket"},"effect":{"type":"stats_delta","stats":{"警覺":3}},"note":"同上，警覺 +3"},
 {"id":"shop_trust_repaid","if_flags":{"all":["trust_repaid"]},"target":{"event":"aftermath"},"effect":{"type":"stats_delta","stats":{"人際":5}},
  "note":"信任曾被好好回報過，被騙之後比較願意開口跟朋友說（人際 +5，較容易維持 has_support）"}]
# v4.7：童年 flag counted_change（姐姐借100還50）
data["cross_line_modifiers"].append({"id":"shop_sister_math","if_flags":{"all":["counted_change"]},"target":{"event":"fee_more"},
 "effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"回憶","text":"你想起姐姐那句「我只花了50，所以還你50」。聽起來合理的話，也要自己算一次。"}},
 "note":"童年當場算出姐姐少還50；付款後被要求「處理凍結」時多一個提醒（不改數值）"})
import outcomes; outcomes.apply(data,'shopping')
finalize_v42(data)
from common import ensure_help; ensure_help(data,mental={"END_CS_DRAINED","END_TICKET_LOST","END_SILENT_COLLAPSE"},legal=())
data["cross_line_modifiers"].append({"id":"shop_fake_toy","if_flags":{'all': ['fake_toy']},"target":{"event":"cheap_item"},"effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（你想起以前買到假玩具的事。）"}},"note":"t43u toy_seller v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"shop_fake_card","if_flags":{'all': ['card_scammed']},"target":{"event":"cheap_item"},"effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（你想起以前換卡片被騙的事。）"}},"note":"t43u card_swap v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"shop_fake_sticker","if_flags":{'all': ['fake_sticker']},"target":{"event":"ticket"},"effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（你想起以前用卡片換一整疊貼紙被騙的事。）"}},"note":"t43u sticker_trade v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"shop_group_buy","if_flags":{'all': ['paid_group_buy']},"target":{"event":"cheap_item"},"effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（你想起以前團購先付錢後貨沒到的事。）"}},"note":"t43u group_buy v1.2（寫手提供，待查證）"})
from common import mark_standalone; mark_standalone(data,{'shop_family_pass': '合併模式（人生線中途插入）下，這個 flag 在本線進場年齡範圍內還不可能拿到（family_passphrase 35歲才設定，假網拍線 22–28歲進場），所以只在單獨遊玩本線（standalone，人生線 flag 由前一局整段人生帶入）時生效；保留給單線模式。combined.py 會檢查：確實觸發不了才可標 standalone_only。'})
from common import apply_mental_wear; apply_mental_wear(data)
from common import set_title; set_title(data)  # v6
json.dump(data,open("script-shopping.json","w"),ensure_ascii=False,indent=2)
