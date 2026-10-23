import json
from common import finalize,apply_v4,HL as CHL,COUNTY_SRC,DASH_SRC,DASH_MONTH,DASH_TYPE,calc_avg,COUNTY_DASH,NO_OFFICIAL,DB as DB165
P="https://www.ptt.cc/bbs/"; D="https://www.dcard.tw/f/anti_fraud/p/"
S={1:P+"Bilk/M.1635396083.A.F45.html",2:P+"Stock/M.1673027393.A.567.html",3:P+"Stock/M.1673501356.A.D80.html",
4:P+"Stock/M.1768319780.A.310.html",5:D+"257083929",6:D+"260128103",7:D+"254197335",23:"https://www.threads.com/@denden.travel/post/DSG1hUqEivN"}
FN="https://fromnineon.com/data/taiwan-fraud-statistics/"; DB="https://165dashboard.tw/"; DG="https://data.gov.tw/dataset/172159"
LAW="https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=339-4"
def src(*ids): return [{"story_id":i,"url":S[i]} for i in ids]
def st(): return [{"name":"165打詐儀表板（經韭點開始整理）","url":FN}]
def C(text,effects,nxt,flags=None,set_flags=None): 
    return {"text":text,"effects":effects,"next":nxt,"flags":{"set":set_flags or [],"require":flags or []}}
E=[]
def ev(id,age,text,choices,sources): E.append({"id":id,"age":age,"text":text,"choices":choices,"sources":sources})

ev("birth",0,"你出生在{county}的{family}家庭。這一生只有一次，選擇無法重來。",
 [C("長大",{},"teen")],[COUNTY_SRC,COUNTY_DASH])
ev("teen",17,"高三那年，同學在群組轉傳「穩賺不賠」的股票影片。你……",
 [C("覺得好奇，但問了家人",{"警覺":5,"人際":3},"work"),
  C("沒多想就滑過去",{},"work")],st())
ev("work",25,"你開始工作，存下第一筆錢。看著房價，你想讓錢「動起來」。",
 [C("下載交友軟體，想認識新朋友",{"心理":3},"date_match",set_flags=["route_dating"]),
  C("在社群網站點了一則名人推薦的投資廣告",{},"ad_group",set_flags=["route_group"])],st()+src(1))
# dating route
ev("date_match",26,"你配對到一位自稱在國外工作的「工程師業務」。他每天早安晚安，很懂你，但總說鏡頭壞了不能視訊。",
 [C("堅持要先視訊才繼續聊",{"警覺":10},"date_refuse_video"),
  C("覺得他忙，沒關係",{"心理":5,"警覺":-5},"date_invest",set_flags=["missed_no_video"])],src(5,6))
ev("date_refuse_video",26,"他一再找藉口，接著突然說：『我學長帶我做投資，想讓你也一起過好日子。』",
 [C("網友主動談投資＝紅燈，封鎖並撥165查詢",{"警覺":15},"END_ROUTER",set_flags=["spotted"]),
  C("聽聽看也無妨",{"警覺":-5},"date_invest",set_flags=["missed_no_video"])],src(6))
ev("date_invest",27,"他傳來一個你沒聽過的投資App，說『我學長是內部人，先放一點點試試』。",
 [C("查金管會合法業者名單，查無此平台，停止",{"警覺":15},"END_ROUTER",set_flags=["spotted"]),
  C("先放1,000元試試",{"存款":-1000},"small_win",set_flags=["missed_unknown_platform"])],src(5,6))
# group route
ev("ad_group",26,"廣告把你加進一個通訊軟體上的股票群組。「老師」每天報明牌，幾百人整齊地回「感謝老師」「老師好準」。",
 [C("覺得回覆整齊得詭異，退群並檢舉",{"警覺":15},"END_ROUTER",set_flags=["spotted"]),
  C("觀望幾週，看起來真的很準",{"警覺":-5,"人際":2},"group_assistant",set_flags=["missed_shills"])],src(1,23))
ev("group_assistant",26,"「助教」私訊你，邀你到一個專屬平台跟單，說名額有限、今天截止。",
 [C("回絕：合法投資不會私訊催促、也不用陌生平台",{"警覺":12},"END_ROUTER",set_flags=["spotted"]),
  C("先放1,000元試試",{"存款":-1000},"small_win",set_flags=["missed_unknown_platform","missed_urgency"])],src(1,23))
# shared
ev("small_win",27,"一週後畫面顯示賺了30%，你試著提領，真的拿回一點錢。你開始相信了。",
 [C("見好就收，不再加碼",{"警覺":5},"temptation"),
  C("加碼30萬，把存款大半投進去",{"存款":-300000,"心理":-5},"withdraw_block",set_flags=["missed_bait_withdraw"])],src(2,7))
ev("temptation",28,"對方持續傳截圖：『別人都翻倍了，你只放這樣太可惜。』",
 [C("告訴好友，朋友提醒這像新聞裡的案例；你停手",{"人際":5,"警覺":10},"END_ROUTER",set_flags=["told_someone","stopped_loss"]),
  C("忍不住加碼30萬",{"存款":-300000},"withdraw_block",set_flags=["missed_bait_withdraw"])],src(2,7))
ev("withdraw_block",28,"帳面變成好幾百萬。你想領出來，平台說要先繳「稅金／保證金／解凍費」，或「交易量未達標」。",
 [C("出金前要先付錢＝詐騙。停止匯款，撥165、到派出所報案",{"警覺":15,"心理":-10},"report",set_flags=["stopped_loss"]),
  C("再繳一次費用就好",{"存款":-200000,"心理":-15},"pressure",set_flags=["missed_prepay_fee"])],src(1,2,7))
ev("pressure",29,"費用繳了，又來新名目。對方態度轉為強硬，甚至有「法務」說不繳就要告你。存款見底。",
 [C("向家人坦白，一起報警",{"人際":5,"心理":-5},"report",set_flags=["stopped_loss","told_someone"]),
  C("刷卡、信貸、向親友借錢湊款",{"存款":-500000,"人際":-20,"心理":-20},"bank_counter",set_flags=["borrowed","missed_legal_threat"])],src(2,3,5))
ev("bank_counter",29,"你到銀行要提領大筆現金，行員關心問：『這筆錢要做什麼用途？』",
 [C("說出實情，行員協助報警",{"警覺":10,"心理":5},"report",set_flags=["stopped_loss","bank_saved"]),
  C("照對方教的說法敷衍，堅持提領",{"存款":-500000,"心理":-20},"END_ROUTER",set_flags=["missed_bank_warning"])],src(4))
ev("report",29,"你報了案。警方說錢多半難追回，但及時報案能凍結部分帳戶、也避免你再被「假檢警／協助追回」二次詐騙。",
 [C("繼續過日子",{"心理":5},"END_ROUTER")],src(2,3)+[{"name":"刑法339-4 加重詐欺（1–7年）","url":LAW}])
ev("END_ROUTER",30,"多年後回頭看這段經歷……（引擎依 ending_rules 自動判定結局，不顯示選項）",
 [C("回顧",{},"__EVAL__")],st())
E[-1]["router"]=True
HL=[{"name":"165全民防騙網（撥打165）","url":"https://165.npa.gov.tw/"},{"name":"1925安心專線","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html"}]
def card(i,summary): return {"story_id":i,"summary":summary,"url":S[i],"note":"去識別化改寫，細節以原文為準"}
EN=[
 {"id":"END_EARLY","priority":4,"conditions":{"flags_any":["spotted"],"stats":{"存款":{"gt":0}}},"text":"你在第一個破綻就停下來。存款完好，你把經驗分享給朋友。",
  "case_card":card(6,"一位女性與網路交往對象聊到USDT投資，查證後及時抽身，損失0元。"),
  "missed_red_flags":["你抓到了：陌生人／網友主動談投資、不能視訊、群組回覆整齊劃一、陌生平台。"],
  "sources":src(6,23)+st()+HL},
 {"id":"END_SMALL_LOSS","priority":3,"conditions":{"flags_any":["stopped_loss"],"flags_none":["borrowed"],"stats":{"存款":{"gt":0}}},"text":"你損失了一筆錢，但及時止血。心痛，但人生還能前進。",
  "case_card":card(1,"上班族從社群網站廣告進入通訊軟體上的投資群組，小額試水後加碼；出金時被要求繳各種費用，損失約22萬後報案。"),
  "missed_red_flags":["小額出金成功是誘餌","平台不在金管會合法名單","出金前要先付費"],"sources":src(1,7)+st()+HL},
 {"id":"END_ALL_LOST","priority":2,"conditions":{"any_of":[{"flags_all":["borrowed"]},{"stats":{"存款":{"lte":0}}}]},"text":"你最後報了案，但存款和借來的錢都沒了，還背著債。和親友的關係需要很久修補。",
  "case_card":card(5,"年輕女性在交友App認識對象，被引介投資，從1,000元到數萬，再被要求鉅額服務費並遭恐嚇，借貸湊款後對方消失。"),
  "missed_red_flags":["不能視訊","網友介紹『學長』教投資","以法律恐嚇要求付款","借錢投資是最危險的訊號"],"sources":src(5,2)+st()+HL},
 {"id":"END_DEBT","priority":1,"conditions":{"flags_all":["borrowed"],"any_of":[{"flags_all":["missed_bank_warning"]},{"stats":{"心理":{"lte":20}}},{"stats":{"人際":{"lte":15}}}]},"text":"你借貸加碼、連行員的提醒也沒聽。存款歸零、負債累累，心理狀態跌到谷底。這一生無法重來。",
  "case_card":card(2,"工作穩定的家人先小額出金建立信任，大額出金被以各種名目拖延，借貸200萬加碼後於高槓桿平台爆倉，損失約300萬。"),
  "missed_red_flags":["大額出金受阻","要求現金面交或大額提領","忽視行員關懷提問（對照案例4：行員攔下503萬）","借貸加碼"],
  "sources":src(2,3,4)+st()+[{"name":"1925安心專線（衛福部心理健康司，24小時免付費）","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html","verified":True},{"name":"165全民防騙網（警政署，撥打165）","url":"https://165.npa.gov.tw/","verified":True,"verify_note":"WebFetch 可開；curl 曾回 429 限流"}]},
]
data={"meta":{"title":"80億分之1：投資詐騙線","version":"0.1","language":"zh-TW","one_life":True,
 "content_policy":"只呈現受騙過程與後果，不含可照做的犯罪操作細節","engine_notes":"next 指向 events id；next=='__EVAL__' 表示依 ending_rules 判定結局；choice.flags.require 中以!開頭表示該flag不可存在；數值套用後夾在 min/max 之間"},
 "ending_rules":{"note":"stat_flags 見 common.py","evaluation":"依 priority 由小到大檢查 endings[].conditions，第一個成立者為結局；都不成立用 fallback",
  "fallback":"END_SMALL_LOSS",
  "condition_grammar":{"flags_all":"全部 flag 都要有","flags_any":"至少一個","flags_none":"都不能有","stats":"{數值:{gt|gte|lt|lte:數字}} 全部成立","any_of":"子條件任一成立；與同層其他鍵為 AND"}},
 "stats":[
  {"label":"2025年全年165受理詐騙案件","value":176242,"unit":"件","period":"2025年（民國114年）全年","verified":True,"verify_note":"fromnineon 整理數字；"+NO_OFFICIAL,"source":FN},
  {"label":"2025年全年詐騙財損","value":893.3,"unit":"億元","period":"2025年（民國114年）全年","verified":True,"verify_note":"fromnineon 整理數字；"+NO_OFFICIAL,"source":FN},
  {"label":"投資詐騙平均每件損失","value":135.4,"unit":"萬元","period":"2026年1–9月（2025全年為136.2萬）","verified":True,"verify_note":"fromnineon 整理數字；"+NO_OFFICIAL+"（儀表板沒有每件平均損失）","source":FN},
  {"label":"2025年投資詐騙占電信網路詐騙財損","value":70.9,"unit":"%","period":"2025年全年","verified":True,"verify_note":"fromnineon 整理數字；"+NO_OFFICIAL,"source":FN},
  {"label":"加重詐欺刑度","value":"1年以上7年以下有期徒刑","verified":"已逐字核對 2026-10-23：處一年以上七年以下有期徒刑，得併科一百萬元以下罰金","source":LAW}]+DASH_MONTH[:3]+[DASH_TYPE["假投資"],DASH_TYPE["假交友投資"],
  calc_avg("假投資詐騙每件平均損失（自行換算）",109995.9,913,"115年9月全月"),
  calc_avg("假交友（投資詐財）詐騙每件平均損失（自行換算）",93129.1,814,"115年9月全月")],
 "stats_sources":[{"name":"韭點開始整理165資料（2026-10-23 WebFetch核對）","url":FN},
  DASH_SRC,
  {"name":"政府資料開放平台 dataset 172159（打擊詐欺犯罪執行成效）","url":DG,"supports_stats":False,"verified":"已擷取（連結有效）：此資料集僅含查緝團數/人數/查扣金額/攔阻金額，不含受理件數或財損，無法用來核對 176,242 件、893.3 億、135萬"}],
 "player_init":{"stats":{"存款":{"min":0,"init_range":[50000,800000]},"警覺":{"min":0,"max":100,"init_range":[20,50]},
   "人際":{"min":0,"max":100,"init_range":[30,70]},"心理":{"min":0,"max":100,"init_range":[40,80]}},
  "county_pool":["臺北市","新北市","桃園市","臺中市","臺南市","高雄市","新竹市","新竹縣","基隆市","苗栗縣","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"],
  "family_pool":[{"name":"小康","存款_mod":0},{"name":"單親","存款_mod":-0.3,"心理":-5},{"name":"務農","人際":5},{"name":"經商","存款_mod":0.5}],
  "start_event":"birth","flags":[]},
 "events":E,"endings":EN}
# ---- v3 ----
for e in EN:
    if e["id"]=="END_DEBT":
        e["conditions"]={"flags_all":["borrowed"],"any_of":[{"flags_all":["missed_bank_warning"]},{"flags_all":["mental_collapse"]},{"flags_all":["isolated"]}]}
        e["reason_texts"]=[{"flag":"missed_bank_warning","text":"你沒有理會行員的關心，最後一道防線也失守了。"},
          {"flag":"mental_collapse","text":"借錢加上一再被催款，你的心理撐不住了（心理≤20），再也沒有力氣止損。"},
          {"flag":"isolated","text":"你向親友借錢，也一再隱瞞，關係破裂（人際≤15），沒有人能拉你一把。"}]
    if e["id"]=="END_ALL_LOST":
        e["conditions"]={"flags_all":["borrowed"]}
        e["reason_texts"]=[{"flag":"borrowed","text":"你借了錢投進去。"}]
    if e["id"]=="END_EARLY": e["conditions"]={"flags_any":["spotted"],"flags_none":["savings_depleted"]}
    if e["id"]=="END_SMALL_LOSS": e["conditions"]={"flags_any":["stopped_loss"],"flags_none":["borrowed","savings_depleted"]}
EN.insert(3,{"id":"END_BROKE","priority":2.5,"conditions":{"flags_all":["savings_depleted"],"flags_none":["borrowed"]},
 "text":"你沒有借錢，但多年的存款全部歸零。你得從頭開始存第一桶金，買房的計畫也延後了十年。",
 "reason_texts":[{"flag":"savings_depleted","text":"你一次次加碼和繳費，把存款全部用光了（存款≤0）。"}],
 "case_card":card(7,"投資人入金3.2萬、順利出金3.6萬建立信任後，再入金約50萬，被以「交易流水不足」為由拒絕出金。"),
 "missed_red_flags":["小額出金成功是誘餌","出金前要先付錢或要求交易量","把大半存款押在陌生平台"],"sources":src(7,1)+st()+HL})
data["red_flag_texts"]={
 "missed_no_video":"對方總是不能視訊，你沒有起疑。",
 "missed_unknown_platform":"你把錢放進一個查不到合法登記的平台。",
 "missed_shills":"群組裡整齊劃一的「老師好準」其實是暗樁。",
 "missed_urgency":"「名額有限、今天截止」是在逼你沒時間想。",
 "missed_bait_withdraw":"小額能出金，是為了讓你放心加碼。",
 "missed_prepay_fee":"出金前要先繳稅金、保證金，就是詐騙。",
 "missed_legal_threat":"「法務」恐嚇說要告你，是施壓手段，不是真的法律程序。",
 "missed_bank_warning":"行員的關心提問是最後一道防線，你卻照對方教的說法敷衍過去。"}
finalize(data,data["red_flag_texts"])

# ================= v4：沉浸呈現 =================
def M(id,frm,text,delay=1200,type="text"): return {"id":id,"from":frm,"text":text,"delay_ms":delay,"type":type}
DATING={"app":"dating_like","app_display_name":"心動 Spark（虛構）","theme":"fictional_warm","contact":{"name":"Kevin","avatar":"placeholder_silhouette","status":"在線上"}}
GROUP={"app":"line_like","app_display_name":"聊聊 Chatto（虛構）","theme":"fictional_green_free","contact":{"name":"飆股學院 VIP 群（487人）","avatar":"placeholder_group","status":"群組"}}
ASSIST={"app":"line_like","app_display_name":"聊聊 Chatto（虛構）","theme":"fictional_green_free","contact":{"name":"助教 Vivian","avatar":"placeholder_silhouette","status":"在線上"}}
V4={
 "date_match":{"presentation":"chat","chat":{**DATING,"messages":[
   M("m1","scammer","早安～今天也要好好吃早餐喔"),M("m2","scammer","跟你聊天是我在國外最開心的時間"),
   M("m3","player","要不要視訊一下？"),M("m4","scammer","我手機鏡頭壞了😢 工地這邊也不方便，下次一定！",1800)]}},
 "date_refuse_video":{"presentation":"chat","chat":{**DATING,"messages":[
   M("m1","scammer","視訊真的不方便，你不相信我嗎？",1500),M("m2","scammer","對了，我學長在帶我做投資"),
   M("m3","scammer","我想讓你也一起過好日子，我們的未來")]}},
 "date_invest":{"presentation":"chat","chat":{**DATING,"messages":[
   M("m1","scammer","學長是內部人，名額很少，我幫你問到了"),M("m2","scammer","（傳來一個你沒聽過的投資 App 連結）",1000,"link"),
   M("m3","scammer","先放一點點試試就好，賺了再說"),M("m4","player","這個平台我查不到耶……")]}},
 "ad_group":{"presentation":"chat","chat":{**GROUP,"messages":[
   M("m1","scammer","【老師】今日盤前觀察：明天這檔有機會"),M("m2","shill","感謝老師！昨天又賺了",400),
   M("m3","shill","老師好準🙏",400),M("m4","shill","感謝老師帶領",400),M("m5","player","（大家的回覆好像都差不多……）")]}},
 "group_assistant":{"presentation":"chat","pressure":{"timer_s":30,"can_disable":True,"label":"名額倒數"},"chat":{**ASSIST,"messages":[
   M("m1","scammer","您好～老師看您很認真，想邀您進專屬跟單平台"),M("m2","scammer","VIP 名額只剩 3 位，今天截止喔",900),
   M("m3","scammer","（傳來一個陌生平台連結）",900,"link")]}},
 "small_win":{"presentation":"chat","chat":{**ASSIST,"messages":[
   M("m1","scammer","恭喜！一週報酬 30%",1000,"image"),M("m2","player","我試著提領一點……真的入帳了！"),
   M("m3","scammer","您看，平台很穩的。大戶都是加碼才翻身的")]}},
 "temptation":{"presentation":"chat","interrupts":[{"at":"m2","from":"好友","text":"欸你最近怎麼一直盯著手機？"}],"chat":{**ASSIST,"messages":[
   M("m1","scammer","（傳來其他會員翻倍的截圖）",1000,"image"),M("m2","scammer","您只放這樣太可惜了")]}},
 "withdraw_block":{"presentation":"chat","pressure":{"timer_s":30,"can_disable":True,"label":"帳戶凍結倒數"},"chat":{**ASSIST,"messages":[
   M("m1","system","提領失敗：帳戶需先完成驗證",800),M("m2","scammer","依規定要先繳稅金／保證金，帳戶才能解凍"),
   M("m3","scammer","不處理的話，帳上的獲利會被沒收喔",700),M("m4","player","不是說隨時可以領嗎？")]}},
 "pressure":{"presentation":"chat","pressure":{"timer_s":25,"can_disable":True,"label":"對方要求的期限"},
   "interrupts":[{"at":"m2","from":"媽媽","text":"最近都沒回家吃飯，還好嗎？"}],"chat":{**ASSIST,"contact":{"name":"平台法務部","avatar":"placeholder_silhouette","status":"在線上"},"messages":[
   M("m1","scammer","您的帳戶涉及違約，請於期限內補足款項",900),M("m2","scammer","否則我們將依法提告",600),
   M("m3","player","（心跳好快，存款已經見底了……）")]}},
 "bank_counter":{"presentation":"chat","chat":{"app":"in_person","app_display_name":"銀行臨櫃","theme":"neutral","contact":{"name":"行員","avatar":"placeholder_silhouette","status":"面對面"},"messages":[
   M("m1","teller","請問這筆錢要做什麼用途呢？"),M("m2","teller","最近很多人被假投資騙，可以跟我說說看嗎？"),
   M("m3","player","（想起對方交代「不要跟銀行說」……）")]}},
}
ANCH={
 "missed_no_video":[{"event":"date_match","message":"m4"},{"event":"date_refuse_video","message":"m1"}],
 "missed_unknown_platform":[{"event":"date_invest","message":"m2"},{"event":"group_assistant","message":"m3"}],
 "missed_shills":[{"event":"ad_group","message":"m3"}],
 "missed_urgency":[{"event":"group_assistant","message":"m2"}],
 "missed_bait_withdraw":[{"event":"small_win","message":"m3"}],
 "missed_prepay_fee":[{"event":"withdraw_block","message":"m2"}],
 "missed_legal_threat":[{"event":"pressure","message":"m2"}],
 "missed_bank_warning":[{"event":"bank_counter","message":"m2"}]}
# 真實統計（不是稀有度）：165 儀表板 115-09 自行換算
from common import share_of_cases,stat_null,SHARE_CARD
_inv=DASH_TYPE["假投資"]["value"]; _rom=DASH_TYPE["假交友投資"]["value"]; _all=DASH_MONTH[0]["value"]
_pct=round((_inv+_rom)/_all*100,1)
VICTIM_STAT={"kind":"share_of_reported_cases","value_pct":_pct,"formula":f"({_inv}+{_rom})/{_all}×100 = {_pct}%",
  "meaning":"115年9月全國受理的詐騙案件中，假投資＋假交友（投資詐財）所占比例；與玩家拿到哪個結局無關",
  "period":"115年9月（2026-09）全月","source":DB165,"verified":True,
  "verify_note":"165 儀表板截圖 04_fraud_type_top5_115-09.webp、05_monthly_115-09_summary.webp；自行換算；類型層級，不對應個別結局",
  "display":f"115 年 9 月全國受理的詐騙案中，約 {round(_pct)}% 是投資類"}
EV4={
 "END_EARLY":{"title":"理性懷疑者","title_emoji":"🛡","grid_color":"green","rarity_key":"inv_END_EARLY",
   "real_world_stat":stat_null("識破而未報案的人不會出現在受理統計中，沒有對應的官方數字"),
   "share_text":"我在投資詐騙前全身而退。你會嗎？"},
 "END_SMALL_LOSS":{"title":"及時煞車的人","title_emoji":"🚦","grid_color":"yellow","rarity_key":"inv_END_SMALL_LOSS",
   "real_world_stat":VICTIM_STAT,"share_text":"我差一點就陷進去，還好及時停下來。"},
 "END_BROKE":{"title":"被溫柔收割的人","title_emoji":"🌫","grid_color":"red","rarity_key":"inv_END_BROKE",
   "real_world_stat":VICTIM_STAT,"share_text":"我的存款歸零了。這一生只有一次。"},
 "END_ALL_LOST":{"title":"借來的希望","title_emoji":"🕳","grid_color":"red","rarity_key":"inv_END_ALL_LOST",
   "real_world_stat":VICTIM_STAT,"share_text":"我借錢想翻身，結果全沒了。"},
 "END_DEBT":{"title":"最後一道防線失守","title_emoji":"🧱","grid_color":"red","rarity_key":"inv_END_DEBT",
   "real_world_stat":VICTIM_STAT,"share_text":"連行員的提醒我都沒聽。你會比我更好嗎？"}}
for k,v in EV4.items():
    v["share_card"]=SHARE_CARD
META4={"presentation_notes":("event.presentation='chat' 時以全螢幕仿聊天室呈現 chat.messages（逐條、依 delay_ms）；"
   "chat.app 只寫類型，畫面一律使用虛構 app 名稱與外觀（app_display_name、theme），不得使用任何真實 App 的商標、圖示、配色。"
   "結局『你錯過的破綻』：對玩家擁有的 missed_* flag，依 red_flag_anchors 回到該事件訊息畫紅框。"),
 "no_pressure_mode":{"available":True,"default":False,"effect":"關閉所有 pressure 倒數、打字動畫改為一般速度；不影響劇情與結局","min_timer_s":20},
 "life_grid":{"bucket_years":5,"colors":{"green":"安全","yellow":"有疑點","red":"受騙損失"},
   "rule":"每 5 歲一格；該區間內玩家選過的 choice.grid 取最嚴重者（red>yellow>green），沒有事件的區間為 green；最後一格用 ending.grid_color"},
 "real_world_stat_notes":"real_world_stat（kind=share_of_reported_cases）是該詐騙類型占 115-09 全國受理件數的比例，事先用官方統計算好寫死；不是結局稀有度，不得顯示成『多少玩家拿到這個結局』。算不出時 value_pct=null 並附 null_reason。結局稀有度留給第二階段，以 rarity_key 對應玩家統計。",
 "phase2_todo":["daily_seed","npc_parallel","badges"]}
apply_v4(data,V4,ANCH,EV4,META4)
from common import apply_cross
def CC(t,e,n,sf=None,rq=None): return {"text":t,"effects":e,"next":n,"flags":{"set":sf or [],"require":rq or []},"grid":"green","cross_line":True}
apply_cross(data,[
 {"id":"inv_wary_ad","if_flags":{"all":["wary_of_easy_money"]},"target":{"event":"ad_group"},"effect":{"type":"stats_delta","stats":{"警覺":8}},
  "note":"人生中對「快錢」有戒心，看到報明牌群組更容易起疑"},
 {"id":"inv_wary_unlock","if_flags":{"all":["wary_of_easy_money"]},"target":{"event":"small_win"},
  "effect":{"type":"unlock_choice","choice":CC("想起以前學到的：獲利太漂亮反而可疑，把錢全部領回、不再投入",{"警覺":10},"END_ROUTER",["stopped_loss"])},
  "note":"多一個及早止損的選項"},
 {"id":"inv_mlm_group","if_flags":{"all":["mlm_joined"]},"target":{"event":"ad_group"},
  "effect":{"type":"rewrite_text","field":"text","text":"以前直銷認識的「朋友」把你拉進一個通訊軟體上的股票群組。「老師」每天報明牌，幾百人整齊地回「感謝老師」「老師好準」。"},
  "note":"人脈被當名單：入口改成熟人拉進群"},
 {"id":"inv_mlm_trust","if_flags":{"all":["mlm_joined"]},"target":{"event":"ad_group"},"effect":{"type":"stats_delta","stats":{"警覺":-5}},
  "note":"熟人介紹，戒心較低"},
 {"id":"inv_lent_mental","if_flags":{"all":["lent_money_lost"]},"target":{"event":"temptation"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"內心","text":"上次借出去的錢也沒拿回來……要是這次能賺回來就好了"}},
  "note":"之前借錢被倒，更想翻本"},
 {"id":"inv_pressure_signer","if_flags":{"all":["pressure_signer"]},"target":{"event":"withdraw_block"},"effect":{"type":"stats_delta","stats":{"警覺":-5}},
  "note":"容易在壓力下當場決定"},
 {"id":"inv_evidence","if_flags":{"all":["evidence_habit"]},"target":{"event":"report"},
  "effect":{"type":"rewrite_text","field":"text","text":"你報了案。因為你一直有保留對話和轉帳紀錄的習慣，警方很快就掌握了資料，及時報案也避免你再被「假檢警／協助追回」二次詐騙。"},
  "note":"保留證據的習慣讓報案更順利（不保證追回）"}])
data["cross_line_modifiers"]+=[
 {"id":"inv_trusts_adults","if_flags":{"all":["trusts_adults"]},"target":{"event":"pressure"},"effect":{"type":"stats_delta","stats":{"警覺":-5}},
  "note":"容易相信大人；面對「平台法務部」這類權威型威脅時較難識破（人生線 README 建議）"}]
# ================= v4.2：結局前提（文字必須與實際路徑一致） =================
from common import finalize_v42
ENX={x["id"]:x for x in data["endings"]}
# 修正矛盾：原 END_DEBT 也收「聽了行員提醒（bank_saved）但心理崩潰／孤立」的玩家，文字卻寫「連行員的提醒也沒聽」
ENX["END_DEBT"].update({"conditions":{"flags_all":["borrowed","missed_bank_warning"]},
  "text":"你借貸加碼，連行員的提醒也沒聽。存款歸零、負債累累。這一生無法重來。",
  "requires_flags":["borrowed","missed_bank_warning"],"forbids_flags":["bank_saved"]})
# 修正矛盾：原 END_ALL_LOST 寫「你最後報了案」，但走到這裡的一定是行員協助報警（bank_saved）
ENX["END_ALL_LOST"].update({"conditions":{"flags_all":["borrowed"],"flags_none":["missed_bank_warning"]},
  "text":"你借錢湊款，最後在銀行行員的協助下報了案，擋下了最後一筆提領。但先前投入的存款都沒了，還背著借來的債，和親友的關係需要很久修補。",
  "requires_flags":["borrowed","bank_saved"],"forbids_flags":["missed_bank_warning"]})
ENX["END_BROKE"].update({"requires_flags":["savings_depleted"],"forbids_flags":["borrowed"]})
ENX["END_SMALL_LOSS"].update({"requires_flags":["stopped_loss"],"forbids_flags":["borrowed","savings_depleted"]})
ENX["END_EARLY"].update({"requires_flags":["spotted"],"forbids_flags":["missed_unknown_platform","missed_bait_withdraw","borrowed","savings_depleted"]})
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
_RW=dict(VICTIM_STAT,consequence_note=NO_CONSEQ)
data["endings"]+=[
 {"id":"END_COLLAPSE","priority":0.5,
  "conditions":{"flags_all":["borrowed","missed_bank_warning","mental_collapse"]},
  "text":"你借貸加碼，連行員的提醒也沒聽。錢沒了、債還在，你開始整夜睡不著、吃不下，一直想「為什麼是我」。後來你被診斷為憂鬱症，需要吃藥、做心理治療，很長一段時間才慢慢好起來。"+HELP_LINE,
  "text_variants":[
   {"when":{"label":"supported","flags_all":["has_support"]},"requires_flags":["has_support"],
    "text":"你借貸加碼，連行員的提醒也沒聽。錢沒了、債還在，你開始整夜睡不著、吃不下，一直責怪自己。是家人發現你不對勁，陪你去看身心科。你被診斷為憂鬱症，吃藥加上心理治療，花了好幾個月才慢慢走出來。"+HELP_LINE},
   {"when":{"label":"alone","flags_none":["has_support"]},"forbids_flags":["has_support"],
    "text":"你借貸加碼，連行員的提醒也沒聽。錢沒了、債還在，你不敢跟任何人說，整夜睡不著、吃不下，一直覺得是自己太笨。你一個人撐了很久，最後才鼓起勇氣打了求助專線、去看身心科，被診斷為憂鬱症，需要長期治療。"+HELP_LINE}],
  "reason_texts":[{"flag":"borrowed","text":"你借了錢投進去，壓力從存款延燒到債務。"},
   {"flag":"missed_bank_warning","text":"你沒有理會行員的關心，最後一道防線也失守了。"},
   {"flag":"mental_collapse","text":"長期的壓力與自責讓你的心理狀態跌到谷底（心理≤20）。"},
   {"flag":"isolated","text":"你不敢讓人知道，身邊沒有人能拉你一把（人際≤15）。"}],
  "case_card":dcard((68,DK["cna_dep"]["url"]),"一名38歲女性在交友軟體認識外國男性，3個月內陸續借出近300萬元，對方失聯後才發現被騙。她不願向家人訴苦，一度狀態很危急，家人發現後立刻幫她求助、陪她就醫，也協助處理債務；她被診斷為憂鬱症，經過一段時間的心理治療和藥物，狀況慢慢改善。"),
  "missed_red_flags":["網友主動帶你投資","出金前要先繳各種費用","借錢投資是最危險的訊號","行員的關心提問是最後一道防線","被騙後把痛苦悶在心裡，只會越來越重"],
  "sources":[DK["cna_dep"],DK["shutien"],DK["pts_dep"],DK["ly_report"]]+src(5,2)+HELP3,
  "requires_flags":["borrowed","missed_bank_warning","mental_collapse"],"forbids_flags":["bank_saved"],
  "title":"錢之後，連自己也差點失去的人","title_emoji":"🌑","grid_color":"red","rarity_key":"inv_END_COLLAPSE",
  "real_world_stat":_RW,"share_text":"被騙之後，最難的不是錢，是怎麼原諒自己。","share_card":SHARE_CARD,"help_resources":HELP3},
 {"id":"END_FAMILY_RIFT","priority":0.7,
  "conditions":{"flags_all":["borrowed","isolated"],"flags_none":["mental_collapse"]},
  "text":"你向親友借的錢還不出來。家人勸過你好幾次，每次都吵到不歡而散；事情爆開後，親戚不再接你電話，家族聚會也不再找你。錢可以慢慢還，信任卻很難再借回來。"+HELP_LINE,
  "text_variants":[
   {"when":{"label":"bank","flags_all":["bank_saved"]},"requires_flags":["bank_saved"],
    "text":"行員協助你報了案，擋下了最後一筆提領。但你先前向親友借的錢早就投進去了。家人勸過你好幾次，每次都吵到不歡而散；事情爆開後，親戚不再接你電話，家族聚會也不再找你。錢可以慢慢還，信任卻很難再借回來。"+HELP_LINE},
   {"when":{"label":"ignored_bank","flags_all":["missed_bank_warning"]},"requires_flags":["missed_bank_warning"],
    "text":"你連行員的提醒也沒聽，把向親友借來的錢全部投了進去。家人勸過你好幾次，每次都吵到不歡而散；事情爆開後，親戚不再接你電話，家族聚會也不再找你。錢可以慢慢還，信任卻很難再借回來。"+HELP_LINE}],
  "reason_texts":[{"flag":"borrowed","text":"你刷卡、信貸，還向親友借錢湊款。"},
   {"flag":"isolated","text":"一再隱瞞和爭吵，讓你和身邊的人關係破裂（人際≤15）。"},
   {"flag":"missed_legal_threat","text":"「法務」的恐嚇讓你急著湊錢，沒有停下來跟家人商量。"}],
  "case_card":dcard((67,DK["shutien"]["url"]),"一名62歲女性加入投資群組，1個月內向親友集資近1,500萬元投入；家人擔心被騙、多次勸阻，雙方一再起衝突。家人堅持陪她到警局才確認是詐騙，之後她因自責對不起家人，出現焦慮、失眠，被診斷為適應障礙合併焦慮憂鬱。"),
  "missed_red_flags":["家人勸阻時，你選擇了爭吵而不是查證","向親友借錢投資，會把損失擴大到整個家族","「法務」恐嚇是施壓手段","出金前要先付錢就是詐騙"],
  "sources":[DK["shutien"],DK["pts_dep"],DK["ly_report"]]+src(2,3,5)+HELP3,
  "requires_flags":["borrowed","isolated"],"forbids_flags":["mental_collapse","has_support"],
  "title":"借走了家人信任的人","title_emoji":"🏚","grid_color":"red","rarity_key":"inv_END_FAMILY_RIFT",
  "real_world_stat":_RW,"share_text":"錢可以慢慢還，家人的信任卻借不回來。","share_card":SHARE_CARD,"help_resources":HELP3}]
data["ending_rules"]["evaluation"]+="（v4.4：COLLAPSE 0.5 → FAMILY_RIFT 0.7 → DEBT 1 …）"
# ================= v4.5：童年 flag（learned_odds） =================
data["cross_line_modifiers"]+=[
 {"id":"inv_learned_odds","if_flags":{"all":["learned_odds"]},"target":{"event":"small_win"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"回憶","text":"你想起文具店的抽抽樂：「永遠差一個字」。中不中，是賣的人決定的。"}},
  "note":"童年看過抽抽樂真相；「先讓你小賺」的情境多一個提醒"},
 {"id":"inv_learned_odds_stat","if_flags":{"all":["learned_odds"]},"target":{"event":"small_win"},"effect":{"type":"stats_delta","stats":{"警覺":5}},"note":"同上，警覺 +5（人生線 README 原建議）"}]
# ================= v4.6：合併模擬平衡（每個結局 2%–40%） =================
# 均勻抽樣下 EARLY 原本 >60%，深層（向銀行/親友借錢）結局 <2%。調整：
# 1) date_invest / group_assistant 的「查證」選項改成「查了但被說服、只放最低金額」→ 仍進 small_win（看見疑點≠停手，真實案例常見）
# 2) pressure 新增第三個選項：瞞著家人動用家裡的錢 → took_family_money，FAMILY_RIFT 改為 isolated 或 took_family_money
# 3) 深層心理扣分減輕（-20→-10），讓 DEBT（背債但沒崩潰）與 COLLAPSE 都有機會出現
EV={e["id"]:e for e in data["events"]}
for eid,txt in [("date_invest","查了金管會名單，查無此平台；他說「新平台還在申請」，你只放最低的1,000元"),
                ("group_assistant","覺得被催有點怪，但名額有限——只放最低的1,000元看看")]:
    c=EV[eid]["choices"][0]; r=EV[eid]["choices"][1]
    c.update({"text":txt,"effects":dict(r["effects"],**{"警覺":5}),"next":r["next"],
              "flags":{"set":["missed_unknown_platform","doubted_platform"],"require":[]},"grid":"yellow"})
P=EV["pressure"]
P["choices"][1]["effects"]["心理"]=-10
P["choices"].append({"text":"不敢讓家人知道，偷偷動用家裡的存款補上","effects":{"存款":-500000,"人際":-30,"心理":-5},
  "next":"bank_counter","flags":{"set":["borrowed","took_family_money","missed_legal_threat"],"require":[]},"grid":"red"})
EV["bank_counter"]["choices"][1]["effects"]["心理"]=-5
RF=next(x for x in data["endings"] if x["id"]=="END_FAMILY_RIFT")
RF["conditions"]={"flags_all":["borrowed"],"flags_none":["mental_collapse"],
  "any_of":[{"flags_all":["isolated"]},{"flags_all":["took_family_money"]}]}
RF["requires_flags"]=["borrowed"]; RF["forbids_flags"]=["mental_collapse"]
for v in RF["text_variants"]: v["forbids_flags"]=["took_family_money"]; v["requires_flags"]=v["requires_flags"]+["isolated"]
RF["text_variants"].insert(0,{"when":{"label":"family_money","flags_all":["took_family_money"]},"requires_flags":["took_family_money"],
  "text":"你瞞著家人，把家裡的存款拿去補「保證金」。錢沒了，事情也瞞不住；家人最在意的不只是錢，而是你一直沒說。之後好一段時間，家裡的對話只剩必要的幾句。錢可以慢慢還，信任卻很難再借回來。如果你或身邊的人也有類似的感受：1925 安心專線（24小時免付費）、1995 生命線、165 反詐騙專線。被騙不是你的錯。"})
RF["reason_texts"].append({"flag":"took_family_money","text":"你沒跟家人商量，就動用了家裡的錢。"})
data["ending_rules"]["evaluation"]+="（v4.6：FAMILY_RIFT 條件改為 borrowed 且（isolated 或 took_family_money））"
# 4) withdraw_block 新增「刷卡／信貸借錢繳費」→ 直接到 bank_counter（真實案例常見：為了解凍費去借款）
EV["withdraw_block"]["choices"].append({"text":"存款不夠，去辦信貸、刷卡湊解凍費","effects":{"存款":-200000,"人際":-10,"心理":-5},
  "next":"bank_counter","flags":{"set":["borrowed","missed_prepay_fee"],"require":[]},"grid":"red"})
# v4.7：偷動家裡存款的路徑一律判 FAMILY_RIFT（家庭裂痕是這條路的核心後果），COLLAPSE 改為排除 took_family_money
_C=next(x for x in data["endings"] if x["id"]=="END_COLLAPSE")
_C["conditions"].setdefault("flags_none",[]).append("took_family_money"); _C["forbids_flags"]=_C.get("forbids_flags",[])+["took_family_money"]
RF["conditions"]={"flags_all":["borrowed"],"any_of":[{"flags_all":["isolated"],"flags_none":["mental_collapse"]},{"flags_all":["took_family_money"]}]}
RF["forbids_flags"]=[]
for v in RF["text_variants"][1:]: v["forbids_flags"]=["took_family_money","mental_collapse"]
data["ending_rules"]["evaluation"]+="（v4.7：took_family_money 優先判 FAMILY_RIFT；COLLAPSE 排除 took_family_money）"
import outcomes; outcomes.apply(data,'investment')
finalize_v42(data)
from common import ensure_help; ensure_help(data,mental={"END_ALL_LOST","END_BROKE","END_DEBT","END_COLLAPSE","END_FAMILY_RIFT"},legal=())
data["cross_line_modifiers"].append({"id":"inv_lent_friend_group","if_flags":{"all":["lent_money_lost"]},"target":{"event":"ad_group"},
 "effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（把你拉進這個群組的，是 24 歲跟你借三萬、後來已讀不回的那位老朋友。他說：「這次真的能還你了。」）"}},
 "note":"v1.0 回頭同學連結：lend（24）借錢沒還的朋友，之後把你拉進投資群組"})
data["cross_line_modifiers"].append({"id":"inv_romance_memory","if_flags":{"all":["rm_deep_loss_seen"]},"target":{"event":"ad_group"},
 "effect":{"type":"stats_delta","stats":{"心理":-12}},"note":"v1.0：感情詐騙借錢的債還沒還完，看到「快速回本」特別心動也特別累（設計假設）"})
data["cross_line_modifiers"].append({"id":"inv_lent_friend_pressure","if_flags":{"all":["lent_money_lost"]},"target":{"event":"ad_group"},
 "effect":{"type":"stats_delta","stats":{"心理":-6}},"note":"v1.1：被當年沒還錢的朋友拉進群，又想討回又不好意思拒絕，心理壓力（設計假設）"})
data["cross_line_modifiers"].append({"id":"inv_gacha_memory","if_flags":{'all': ['chased_lottery']},"target":{"event":"temptation"},"effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（你想起以前抽抽樂花了不少錢的事。）"}},"note":"t43u gacha_try v1.2（寫手提供，待查證）"})
from common import mark_standalone; mark_standalone(data,{})
from common import apply_mental_wear; apply_mental_wear(data)
# v1.2 調分布：人生線心理回復 1.8→2.6 後 COLLAPSE 掉到 2% 以下，照銀行話術說的那一步bank_counter[1] 心理 -7→-14、withdraw_block[2] -7→-10（設計假設）
next(e for e in data["events"] if e["id"]=="bank_counter")["choices"][1]["effects"]["心理"]=-14
next(e for e in data["events"] if e["id"]=="withdraw_block")["choices"][2]["effects"]["心理"]=-10
next(e for e in data["events"] if e["id"]=="pressure")["choices"][1]["effects"]["心理"]=-18  # -15→-18（設計假設）
from common import set_title; set_title(data)  # v6
json.dump(data,open("script-investment.json","w"),ensure_ascii=False,indent=2)
