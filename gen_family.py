"""gen_family.py（v1.0，Leo 核准的三段新劇情）：交往詐騙線（25–29）、婚姻詐騙線（30–34）、家長篇（41–45）。
產生 script-romance.json、script-marriage.json、script-parent.json。結構沿用 script-shopping.json 的 v4 格式。
金額為設計假設（等比例縮放）；案件卡為去識別化改寫；私密影像案只寫流程與後果，不描述任何影像內容。"""
import json,copy
from common import SHARE_CARD,stat_null,M,ensure_help,apply_mental_wear,HL,finalize_v42
BASE=json.load(open("script-shopping.json"))
def s(name,url,note="2026-10-23 WebSearch 搜尋摘錄核對；去識別化改寫",ok=True): return {"name":name,"url":url,"verified":ok,"verify_note":note}
def C(t,e,n,fl=(),out="",log="",grid="green",req=()):
    return {"text":t,"effects":dict(e),"next":n,"flags":{"set":list(fl),"require":list(req)},"grid":grid,"outcome_text":out,"log_text":log}
def RND(t,outs,note):
    return {"text":t,"random":True,"effects":{},"next":outs[0]["next"],"flags":{"set":[],"require":[]},"grid":"green",
            "outcomes":outs,"random_note":{"design_assumption":True,"note":note}}
def O(p,e,n,fl,out,log,grid="green"): return {"probability":p,"effects":dict(e),"next":n,"flags_set":list(fl),"outcome_text":out,"log_text":log,"grid":grid}
def chat(app,name,contact,msgs): return {"presentation":"chat","chat":{"app":app,"app_display_name":name,"theme":"fictional_warm","contact":{"name":contact,"avatar":"placeholder_silhouette","status":"在線上"},"messages":msgs}}
def END(id,pri,cond,title,emoji,grid,text,card,src,missed,share,req=(),forb=(),variants=None,reason=None):
    x={"id":id,"priority":pri,"conditions":cond,"text":text,"reason_texts":reason or [],"case_card":{"summary":card,"url":src[0]["url"],"note":"去識別化改寫，細節以原文為準"},
       "missed_red_flags":missed,"sources":src+HL,"title":title,"title_emoji":emoji,"grid_color":grid,
       "real_world_stat":stat_null("165 儀表板沒有對應這個結局的分類統計"),"share_text":share,"share_card":SHARE_CARD,
       "requires_flags":list(req),"forbids_flags":list(forb)}
    if variants: x["text_variants"]=variants
    return x
def build(line,title,events,endings,rft,anchors,mods,meta_extra,mental,stats_note):
    d={k:copy.deepcopy(BASE[k]) for k in ("meta","ending_rules","player_init")}
    d["meta"].update({"title":title,"line":line,"version":"1.0","cross_line_notes":BASE["meta"]["cross_line_notes"],**meta_extra})
    d["meta"]["amount_note"]="金額為設計假設：依真實案件量級等比例縮小，合併模式另依進場存款縮放（見 script-life.json scam_integration）"
    d["ending_rules"]["fallback"]=endings[-1]["id"]
    d["stats"]=[]; d["stats_sources"]=[]; d["meta"]["stats_note"]=stats_note
    d["player_init"]["start_event"]=events[0]["id"]
    for e in events: e.setdefault("presentation","card")
    for x in endings: x["rarity_key"]=f"{line}_{x['id']}"
    d["events"]=events; d["endings"]=endings; d["red_flag_texts"]=rft; d["red_flag_anchors"]=anchors
    for m in mods: m.setdefault("mode","all")
    d["cross_line_modifiers"]=mods
    apply_mental_wear(d); ensure_help(d,mental=mental); finalize_v42(d)
    from common import set_title; set_title(d)  # v6
    # v6：案件卡 story_id／url 對應 research-romance-marriage-parent.md 的列編號（R/M/K）；查不到標「待查」
    import re as _re
    _RM={}
    for _ln in open("research-romance-marriage-parent.md",encoding="utf-8"):
        _m=_re.match(r"\|\s*([RMK]\d+)\s*\|",_ln)
        if _m:
            for _u in _re.findall(r"https?://[^\s|）)；]+",_ln): _RM.setdefault(_u.rstrip("。，"),_m.group(1))
    # v6.1：人工核對後，摘要改成與研究列內容一致（不捏造；只取研究列文字）
    _FIX={"END_RM_DEEP":("https://www.cna.com.tw/news/asoc/202601040111.aspx","高雄一名男子在交友軟體認識網友，對方要他下載非官方 App 儲值；小額能提領後，他把積蓄全部存進去，結果領不出來，損失約 320 萬元。"),
          "END_MR_COLLAPSE":(None,"女子未經前夫同意，在借款本票與借據上偽造前夫簽名，讓他成為連帶保證人；前夫被追債後才知道。彰化地院依偽造私文書、偽造有價證券罪判刑。"),
          "END_MR_PAID":(None,"桃園一名女子婚後 3 個月，家裡開始有人上門討債，才知道丈夫婚前就背了鉅額債務；丈夫 5 個月後躲債失聯。"),
          "END_MR_DIVORCE":("https://udn.com/news/story/7321/9492558","前夫發現自己被前妻偽簽成借款連帶保證人、遭追債後提告，彰化地院判前妻偽造私文書與偽造有價證券罪。")}
    for _x in d["endings"]:
        if _x["id"] in _FIX:
            _u2,_sm=_FIX[_x["id"]]; _c=_x.setdefault("case_card",{}); _c["summary"]=_sm
            if _u2: _c["url"]=_u2
    for _x in d["endings"]:
        _c=_x.setdefault("case_card",{}); _u=_c.get("url")
        _c["story_id"]=("research_"+_RM[_u]) if _u in _RM else "待查"
        if not _u: _c["url"]="待查"
        if _u and _u not in _RM: _c["url_note"]="此 url 未列在 research-romance-marriage-parent.md，待查"
    json.dump(d,open(f"script-{line}.json","w"),ensure_ascii=False,indent=2); print(line,len(events),"events",len(endings),"endings")
    return d

# ======================= 1) 交往詐騙線 25–29（每局必出） =======================
RM_SRC=[s("刑事警察局 115-02-21：交友 App 認識網友後被帶往假投資平台，曾出金成功、再申請信貸加碼，第二次出金被要求繳訂金才發覺（桃園，累計 700 多萬元）","https://www.cib.npa.gov.tw/ch/app/news/view?id=1887&module=news&serno=b4316ff9-f1f8-4d45-b094-5490896ee976","2026-10-23 WebFetch 開啟核對；去識別化"),
 s("中央社 2025-02-07：陌生帳號每日問候，以母親開刀為由借錢，行員關懷後報警攔阻（台中，70 多歲，50 萬元未匯出）","https://www.cna.com.tw/news/asoc/202502070163.aspx","2026-10-23 WebFetch 開啟核對；去識別化"),
 s("中央社 2025-07-28：網戀數月，對方稱母親重病需醫藥費，臨櫃匯款前警方識破，對方隨即已讀不回（台中，60 多歲，20 萬元未匯出）","https://www.cna.com.tw/news/asoc/202507280044.aspx","2026-10-23 WebFetch 開啟核對；去識別化"),
 s("反詐騙討論板網友經驗分享：對方常說要來見面卻從沒出現，話題轉向虛擬貨幣，查證後停止聯絡並截圖留證","https://www.dcard.tw/f/anti_fraud/p/260128103","2026-10-23 WebFetch 開啟核對；去識別化；民間經驗分享，非官方")]
RM_PEND=s("工作認識、網聚認識的交往詐騙台灣案例：待查","","寫手提供，待查證",False)
RM_EY=RM_SRC[1]
ev=[]
ev.append({"id":"rm_meet","age":27,"text":"你最近開始想找個伴。認識新朋友的方式有很多種……","sources":RM_SRC[:1]+[RM_SRC[3]],"sources_pending":["工作認識、網聚認識的交往詐騙台灣案例：待查（寫手提供，待查證）"],
 "choices":[RND("認識新的人",[
   O(1/3,{"心理":5},"rm_weeks",["rm_via_app"],"你在交友軟體上配對到「阿澄」，聊天很合拍。","交友軟體認識阿澄"),
   O(1/3,{"心理":5},"rm_weeks",["rm_via_meetup"],"朋友揪的桌遊網聚上，你和「阿澄」很聊得來，散場前互加好友。","網聚認識阿澄"),
   O(1/3,{"心理":5},"rm_weeks",["rm_via_work"],"合作廠商的窗口「阿澄」很照顧你，案子結束後還常傳訊息關心。","工作認識阿澄")],
   "認識管道三選一、各 1/3 是設計假設，不是統計；三種管道在真實案件裡都有")]})
ev.append({"id":"rm_weeks","age":27,"text":"幾個星期下來，阿澄每天早安晚安，記得你說過的每件小事。你開始期待手機亮起來。","sources":RM_SRC[:3],
 **chat("dating_like","心動訊息（虛構）","阿澄",[M("m1","scammer","早安～昨天你說胃不舒服，今天有好一點嗎？"),M("m2","scammer","我覺得我們好像認識很久了"),
   M("m3","player","下週末要不要見個面？"),M("m4","scammer","下週我要出差耶😢 等我回來一定！",1800)]),
 "choices":[C("再約一次具體時間",{"警覺":5},"rm_excuse",["rm_asked_meet"],"你約了具體的日期。阿澄說好，但前一天又說臨時有事。","再約時間"),
   C("先這樣聊就好",{"心理":3,"警覺":-3},"rm_turn",["missed_rm_no_meet"],"你說沒關係，慢慢來。阿澄傳了一個愛心。","沒約見面","yellow")]})
ev.append({"id":"rm_excuse","age":27,"text":"見面一延再延，視訊也總是「網路不好」。週末回家吃飯時，姐姐問你最近怎麼一直在笑。","sources":RM_SRC[:2],
 "choices":[C("跟姐姐聊聊阿澄",{"人際":3},"rm_turn",["rm_told_sister"],"姐姐聽完說：「你開心我很高興，不過如果他開口跟你要錢，先給我看一下好不好？」","跟姐姐聊了"),
   C("相信阿澄很忙",{"警覺":-3},"rm_turn",["missed_rm_excuse"],"你告訴自己，他只是比較忙。","相信很忙","yellow")]})
ev.append({"id":"rm_turn","age":28,"text":"有一天，阿澄的語氣變了。","sources":RM_SRC+[RM_EY],
 "choices":[RND("看阿澄的訊息",[
   O(1/3,{},"rm_ask_invest",["rm_type_invest"],"阿澄說他「跟著一位老師投資」，想帶你一起賺，為你們的未來存錢。","阿澄提投資"),
   O(1/3,{},"rm_ask_loan",["rm_type_loan"],"阿澄說店裡周轉不過來，下個月就能還，只差三萬。","阿澄要借錢"),
   O(1/3,{},"rm_ask_sick",["rm_type_sick"],"阿澄說家人突然住院，醫藥費要先繳，一直在道歉。","阿澄家人生病")],
   "三種轉折各 1/3 是設計假設；真實案件常見投資、借款、家人急病三類說法（刑事局、行政院宣導）")]})
def ask(id,text,msgs,src):
    ev.append({"id":id,"age":28,"text":text,"sources":src,**chat("dating_like","心動訊息（虛構）","阿澄",msgs),
     "choices":[C("搜尋阿澄的照片",{"警覺":8,"心理":-8},"__EVAL__",["rm_checked"],"同一張照片出現在好幾個不同名字的帳號上。你盯著螢幕很久，心裡空了一塊。","查到照片"),
       C("先轉一小筆",{"存款":-10000,"心理":2},"rm_more",["rm_paid_once","missed_rm_money_ask"],"你轉了一萬。阿澄說「謝謝你，我真的好愛你」。","先轉一萬","red"),
       C("說要再想想",{"心理":-3},"rm_push",[],"阿澄沉默了一下，接著傳來一長串訊息。","說要想想"),
       C("把對話給姐姐看",{"人際":5,"心理":-6},"__EVAL__",["rm_sister_stop"],"姐姐看完，握著你的手說：「我們一起打 165 問問看。」電話那頭說，這是很典型的手法。","給姐姐看",req=["rm_told_sister"])]})
ask("rm_ask_invest","阿澄傳來一個投資平台的截圖，說「老師帶的都賺」，要你先入金試試。",
    [M("m1","scammer","寶貝你看，我上週又賺了 12%"),M("m2","scammer","我們一起存結婚基金好不好？"),M("m3","scammer","先放一萬試試，我教你操作",1600)],RM_SRC)
ask("rm_ask_loan","阿澄說店裡周轉不過來，想先跟你借三萬，下個月一定還。",
    [M("m1","scammer","我真的很不想開口……"),M("m2","scammer","只是周轉一下，下個月一定還你"),M("m3","scammer","你先轉一萬也好，拜託",1600)],RM_SRC[:2]+[RM_EY])
ask("rm_ask_sick","阿澄說家人住院，醫藥費要先繳，問你能不能先幫忙。",
    [M("m1","scammer","醫院說今天要先繳費"),M("m2","scammer","我在這邊誰都不認識，只有你了"),M("m3","scammer","先一萬就好，我回去馬上還你",1600)],[RM_EY]+RM_SRC[:2])
ev.append({"id":"rm_push","age":28,"text":"阿澄說：「你是不是不信任我？我們在一起這麼久了。」接著好幾個小時都沒有再傳訊息。","sources":RM_SRC[2:],
 "choices":[C("打 165 問問看",{"警覺":10,"心理":-10},"__EVAL__",["rm_hotline"],"165 的人聽完說：不見面、只談錢，這是交友詐騙最常見的樣子。你掛上電話，哭了一下。","打給165"),
   C("怕他難過，還是轉",{"存款":-10000},"rm_more",["rm_paid_once","missed_rm_guilt"],"你轉了錢。阿澄又變回原本溫柔的樣子。","還是轉了","red")]})
ev.append({"id":"rm_more","age":29,"text":"幾週後，阿澄說還差一點：保證金、手續費、或是「最後一次」的醫藥費。金額一次比一次大。","sources":RM_SRC,
 "choices":[C("停下來去報案",{"警覺":10,"心理":-12},"__EVAL__",["rm_reported","reported"],"你帶著轉帳紀錄去派出所。警察說能追的會盡量追，但你得有心理準備。","去報案"),
   C("借錢再匯過去",{"存款":-60000,"心理":-15,"人際":-5},"__EVAL__",["rm_deep_loss","rm_loan_taken","family_blame"],"你跟信貸借了錢匯過去，之後阿澄就消失了。爸媽知道後罵你：「怎麼會這麼笨？」","借錢再匯","red")]})
RM_RFT={"missed_rm_no_meet":"聊了好幾個星期，對方一直沒有真的見面","missed_rm_excuse":"見面、視訊一再推託","missed_rm_money_ask":"還沒見過面，對方就開口談錢","missed_rm_guilt":"用「你不信任我」讓你愧疚"}
RM_ANC={"missed_rm_no_meet":[{"event":"rm_weeks","message":"m4"}],"missed_rm_excuse":[{"event":"rm_weeks","message":"m4"}],
 "missed_rm_money_ask":[{"event":"rm_ask_invest","message":"m3"},{"event":"rm_ask_loan","message":"m3"},{"event":"rm_ask_sick","message":"m3"}],"missed_rm_guilt":[{"event":"rm_ask_loan","message":"m1"}]}
SAD="真心付出被利用的難過是真的，不是你太傻。這種失落可以找人說。"
rm_end=[
 END("END_RM_COLLAPSE",1,{"flags_all":["rm_deep_loss","mental_collapse"]},"空掉的人","🌧️","red",
  "錢沒了，信任也沒了。你好幾個月提不起勁，連手機亮起來都會發抖。\n"+SAD,"一名女子在交友後被帶進投資平台，陸續匯出超過百萬，平台要求再繳費才能出金，才發現被騙。",RM_SRC[:1],
  ["還沒見過面就談錢","借錢去匯款"],"我在交往詐騙線，撐得很辛苦。",req=["rm_deep_loss"]),
 END("END_RM_DEEP",2,{"flags_all":["rm_deep_loss"]},"借來的心動","💸","red",
  "你為了阿澄借了錢，人卻消失了。每個月的還款提醒你那段日子。\n"+SAD,"一名男子網路交友後，對方以投資、借款為由要錢，他陸續借貸匯款，對方失聯。",[RM_SRC[2]],
  ["見面一再推託","金額越來越大"],"我在交往詐騙線，學到很貴的一課。",req=["rm_deep_loss"]),
 END("END_RM_STOPPED",3,{"flags_all":["rm_reported"]},"停損的人","🛑","yellow",
  "你轉出去的錢不一定追得回來，但你在越陷越深前停下來了。\n"+SAD,"被害人在交友對象多次以各種名目要錢後，帶著轉帳紀錄報案，警方協助凍結部分款項。",RM_SRC[1:2],
  ["沒見面就先轉帳"],"我在交往詐騙線及時停下來了。",req=["rm_reported"]),
 END("END_RM_SISTER",4,{"flags_all":["rm_sister_stop"]},"有人陪著看","🤝","green",
  "姐姐陪你打了 165。那天晚上你很難過，但你沒有一個人扛。","家人察覺被害人和網友聊天後情緒起伏大，陪同查證，對方要錢前即被識破。",RM_SRC[3:4],
  ["一直沒有真的見面"],"我在交往詐騙線，有家人陪我一起看清楚。",req=["rm_sister_stop"]),
 END("END_RM_HOTLINE",5,{"flags_all":["rm_hotline"]},"打出那通電話","☎️","green",
  "被說「不信任」很難受，但你還是打了 165。心痛會過去，存款還在。","交友對象以情緒勒索催促匯款，被害人先撥 165 查證，確認為詐騙手法。",RM_SRC[1:2],
  ["用愧疚感催你匯款"],"我在交往詐騙線打了 165。",req=["rm_hotline"]),
 END("END_RM_CHECKED",6,{},"查過照片的人","🔍","green",
  "同一張臉、好幾個名字。你難過了好幾天，但你沒有把錢交出去。","民眾以圖片搜尋發現交友對象的照片被多個假帳號使用，及早停止往來。",RM_SRC[3:4],
  ["還沒見面就談錢"],"我在交往詐騙線，先查了再說。")]
RM_MODS=[
 {"id":"rm_lent_memory","if_flags":{"all":["lent_money_lost"]},"target":{"event":"rm_ask_loan"},"effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"system","text":"（你想起 24 歲借出去、到現在都沒回來的那三萬。）"}},"note":"借錢線連結：lend（24）→交往借款"},
 {"id":"rm_fee_memory","if_flags":{"all":["paid_job_fee"]},"target":{"event":"rm_ask_invest"},"effect":{"type":"add_interrupt","interrupt":{"at":"m3","from":"system","text":"（16 歲那次，也是說「先付一點」才能開始。）"}},"note":"先付費連結：part_time_ad（16）→交往投資"},
 {"id":"rm_otp_memory","if_flags":{"all":["otp_scammed"]},"target":{"event":"rm_weeks"},"effect":{"type":"stats_delta","stats":{"警覺":5}},"note":"驗證碼連結：小時候傳過驗證碼，對「只在線上」的人多一點戒心"},
 {"id":"rm_sister_memory","if_flags":{"all":["counted_change"]},"target":{"event":"rm_excuse"},"effect":{"type":"add_interrupt","interrupt":{"at":"__event__","from":"system","text":"姐姐笑說：「你從小就會當場算清楚，這次也算一下吧。」"}},"note":"姐姐（8 歲借100還50）連結","mode":"all"}]
RM_MODS=[m for m in RM_MODS if m["effect"]["type"]!="add_interrupt" or m["target"]["event"] in ("rm_ask_loan","rm_ask_invest")]
rm=build("romance","交往詐騙線",ev,rm_end,RM_RFT,RM_ANC,RM_MODS,{"mandatory":True,"mental_cost_rule":"每條路徑都有心理代價（即使及早查證也有失落）"},
 {"END_RM_COLLAPSE","END_RM_DEEP","END_RM_STOPPED","END_RM_SISTER","END_RM_HOTLINE","END_RM_CHECKED"},"165 儀表板只有假交友（投資詐財）類別，與本線借款、急病說法不完全對應，不放統計")

# ======================= 2) 婚姻詐騙線 30–34 =======================
MR_SRC=[s("三立新聞 2019-01-08：婚後 3 個月債主上門才知配偶婚前負債，配偶 5 個月後躲債失聯，法院判准離婚（桃園）","https://www.setn.com/News.aspx?NewsID=482098","2026-10-23 WebFetch 開啟核對；去識別化"),
 s("聯合新聞網 2026-05-09：前配偶冒簽姓名，讓對方成為借款連帶保證人，被追債才知道；判偽造私文書 6 月、偽造有價證券 3 年 2 月（彰化）","https://udn.com/news/story/7321/9492558","2026-10-23 WebFetch 開啟核對；去識別化"),
 s("自由時報 2025-04-22：已婚者隱瞞婚姻、變造證件照片配偶欄、誇大收入，以結婚為前提借款 360 萬元；刑事判 2 年 6 月，民事判還 358.4 萬元（台南）","https://news.ltn.com.tw/news/society/breakingnews/5020227","2026-10-23 WebFetch 開啟核對；去識別化"),
 s("全國法規資料庫 民法第 997 條：因被詐欺而結婚者，得於發見詐欺後六個月內向法院請求撤銷","https://law.moj.gov.tw/LawClass/LawSingleRela.aspx?FLNO=997&PCODE=B0000001&ty=J","2026-10-23 WebFetch 開啟核對；去識別化；法條原文")]
ev=[]
ev.append({"id":"mr_wedding","age":32,"text":"你結婚了。婚宴上大家都說你們很登對，媽媽偷偷擦了眼淚。","sources":MR_SRC[:2],
 "choices":[RND("開始婚後生活",[
   O(0.5,{"心理":5},"mr_letter",["mr_type_debt"],"婚後一切看起來都很平順。直到某天信箱多了一封信。","婚後收到信"),
   O(0.5,{"心理":5},"mr_asks",["mr_type_fraud"],"婚後沒多久，另一半開始常常提到錢。","另一半常提錢")],
   "兩種類型各 50% 是設計假設：配偶隱瞞債務／冒名借款、預謀詐婚，判決中都有")]})
ev.append({"id":"mr_letter","age":32,"text":"信封上寫著你的名字：一家你沒去過的融資公司，通知你「保證的借款」已經逾期。","sources":MR_SRC[:3],
 **chat("sms_like","簡訊（虛構）","某融資公司",[M("m1","other","您擔任保證人之借款已逾期，請儘速處理"),M("m2","player","我沒有當過任何人的保證人"),M("m3","other","契約上有您的簽名與證件影本",1600)]),
 "choices":[C("申請自己的信用報告",{"警覺":10,"心理":-5},"mr_talk",["mr_checked_credit"],"報告上有兩筆你從沒辦過的借款，用的是你的身分證影本。","查信用報告"),
   C("先放著不問",{"心理":-5},"mr_later",["missed_mr_letter"],"你把信收進抽屜，告訴自己應該是弄錯了。","先放著","yellow")]})
ev.append({"id":"mr_later","age":33,"presentation":"timeskip","text":"半年後，催收電話開始打到你公司。","sources":MR_SRC[:2],
 "choices":[C("回家問另一半",{"存款":-20000,"心理":-8},"mr_talk",["mr_debt_grew"],"利息又滾了一筆。另一半終於承認，是他拿你的證件去辦的。","回家問")]})
ev.append({"id":"mr_talk","age":33,"text":"另一半說：「我只是周轉一下，本來想自己還掉。」你看著那些契約，上面是你的名字。","sources":MR_SRC,
 "choices":[C("報警，也辦離婚",{"心理":-15,"人際":-5},"__EVAL__",["mr_reported","mr_divorced","reported"],"你帶著信用報告去報案。偽造文書的案子走了很久，婚也離了。","報警並離婚"),
   C("幫他把錢還掉",{"存款":-80000,"心理":-10},"__EVAL__",["mr_paid_debt","family_blame"],"你拿出存款還了債。爸媽知道後說：「早就叫你看清楚，現在怎麼辦？」","幫忙還錢","red"),
   C("先找法律諮詢",{"心理":-8,"警覺":5},"__EVAL__",["mr_legal"],"法律扶助的律師告訴你：冒名簽的保證契約可以爭執，先別自己認下來。","找法律諮詢")]})
ev.append({"id":"mr_asks","age":33,"text":"另一半說老家要整修、媽媽要開刀，要你先拿一筆錢；你的身分證和印章也「借去辦點事」。","sources":MR_SRC[3:],
 **chat("line_like","聊天（虛構）","另一半",[M("m1","scammer","我媽下週要開刀，還差二十萬"),M("m2","scammer","你的印章先借我，辦完就還你"),M("m3","scammer","我們是一家人，你不相信我嗎？",1600)]),
 "choices":[C("查戶籍和婚姻紀錄",{"警覺":10,"心理":-5},"mr_truth",["mr_checked_record"],"你請戶政調了資料，發現對方隱瞞了一段前婚。","查戶籍紀錄"),
   C("先把錢給他",{"存款":-50000,"心理":-5},"mr_truth",["mr_paid_partner","missed_mr_id_lent"],"你把錢和印章都交了出去。","交出錢和印章","red")]})
ev.append({"id":"mr_truth","age":34,"text":"沒多久，另一半帶著東西消失了，電話也打不通。","sources":MR_SRC[3:],
 "choices":[C("報警並請求撤銷婚姻",{"心理":-15,"人際":-3},"__EVAL__",["mr_reported","mr_annul","reported"],"你報了案，也向法院請求撤銷婚姻。程序很長，但你一步一步走。","報警並撤銷"),
   C("忍下來，不跟人說",{"心理":-20,"人際":-8},"__EVAL__",["mr_silent"],"你覺得丟臉，誰也沒說。夜裡常常睡不著。","忍下來","yellow")]})
MR_RFT={"missed_mr_letter":"你的名字出現在你沒簽過的契約上","missed_mr_id_lent":"身分證、印章被「借去辦事」"}
MR_ANC={"missed_mr_letter":[{"event":"mr_letter","message":"m3"}],"missed_mr_id_lent":[{"event":"mr_asks","message":"m2"}]}
HURT="被最親近的人冒用名字，受傷是正常的。你可以找人說，也可以找法律協助。"
mr_end=[
 END("END_MR_COLLAPSE",1,{"flags_all":["mental_collapse"],"flags_any":["mr_silent","mr_paid_debt","mr_paid_partner"]},"撐不住的婚姻","🌧️","red",
  "錢、婚姻、自信一起被拿走。你很久都不想見人。\n"+HURT,"配偶利用對方證件辦理分期借款，被害人長期承受催收壓力，法院認定構成經濟上的不法侵害。",[MR_SRC[1]],["沒簽過的契約","證件被借走"],"我在婚姻詐騙線撐得很辛苦。"),
 END("END_MR_SILENT",2,{"flags_all":["mr_silent"]},"一個人吞下","🤐","red",
  "你沒有報警，也沒有跟家人說。錢沒了，婚姻也只剩一張紙。\n"+HURT,"被害人遭配偶隱瞞前婚、以家人開刀等理由要錢後失聯，事後才提起訴訟撤銷婚姻。",[MR_SRC[3]],["身分證、印章被借去辦事"],"我在婚姻詐騙線選擇自己吞下。",req=["mr_silent"]),
 END("END_MR_PAID",3,{"flags_all":["mr_paid_debt"]},"替他還的人","🧾","red",
  "你替另一半還了債。名字回來了，存款沒了，信任也很難回來。\n"+HURT,"配偶冒用名義向他人借款，被害人先行代償；法院後續仍以偽造文書判處配偶有期徒刑。",[MR_SRC[0]],["沒簽過的契約"],"我在婚姻詐騙線替人還了債。",req=["mr_paid_debt"]),
 END("END_MR_DIVORCE",4,{"flags_all":["mr_divorced"]},"拿回名字","⚖️","yellow",
  "報警、離婚，都很痛。但那些契約上的名字，你一筆一筆拿回來了。\n"+HURT,"前配偶偽簽保證人，被害人報案提告，法院判決偽造文書有罪。",[MR_SRC[2]],["信箱裡的催繳信"],"我在婚姻詐騙線拿回自己的名字。",req=["mr_divorced"]),
 END("END_MR_LEGAL",5,{"flags_all":["mr_legal"]},"先問清楚","📚","yellow",
  "你沒有先認下債務，而是找律師問清楚每一步的代價。\n"+HURT,"配偶冒名借款案中，被害人尋求法律協助，主張保證契約非本人簽署。",[MR_SRC[0]],["沒簽過的契約"],"我在婚姻詐騙線先找了法律協助。",req=["mr_legal"]),
 END("END_MR_ANNUL",6,{},"撤銷那紙婚約","📄","yellow",
  "你報了案，也請法院撤銷婚姻。很累，但你沒有讓這件事定義你。\n"+HURT,"一方隱瞞前婚並謊稱懷孕締結婚姻，法院依民法第997條判准撤銷婚姻。",[MR_SRC[3]],["證件被借去辦事"],"我在婚姻詐騙線撤銷了婚約。")]
MR_MODS=[
 {"id":"mr_evidence","if_flags":{"all":["evidence_habit"]},"target":{"event":"mr_letter"},"effect":{"type":"stats_delta","stats":{"警覺":5}},"note":"證據習慣：比較會想到查信用報告"},
 {"id":"mr_romance_memory","if_flags":{"all":["rm_deep_loss_seen"]},"target":{"event":"mr_asks"},"effect":{"type":"add_interrupt","interrupt":{"at":"m3","from":"system","text":"（「你不相信我嗎？」——你好像在哪裡聽過這句話。）"}},"note":"交往線連結：交往詐騙中借錢匯款的人"}]
mr=build("marriage","婚姻詐騙線",ev,mr_end,MR_RFT,MR_ANC,MR_MODS,{"types":["配偶隱瞞債務／冒名借款、當保證人","預謀詐婚"]},
 {e["id"] for e in mr_end},"沒有官方統計對應婚姻內的冒名借款或詐婚，不放統計")

# ======================= 3) 家長篇 41–45（每局必出） =======================
PA_SRC={"game":[s("教育部、內政部致家長的一封信：網購或網路交友要你買遊戲點數就是詐騙","https://jsps.chc.edu.tw/posts/8986","2026-10-23 WebFetch 開啟核對；去識別化")],
 "mule":[s("中央社 2025-06-19：成年人招募 16 歲少年當取款車手，少年在交款現場被捕，招募者依組織犯罪條例加重判 1 年","https://www.cna.com.tw/news/asoc/202506190113.aspx","2026-10-23 WebFetch 開啟核對；去識別化")],
 "date":[s("臺北市少年警察隊：兒少網路交友與私密照外流應變（保留證據、求助報警、禁止散布）","https://young.police.gov.taipei/News_Content.aspx?n=2F706BAC97CD7533&s=D7592B5544C17752&sms=AA60320A15BFA2FF","2026-10-23 WebFetch 開啟核對；去識別化")],
 "threat":[s("自由時報 2025-08-11：男子以送免費遊戲點數為餌鎖定兒少，被害 20 餘名遭起訴；台中警方統計加害者為網友 40%、同學 35%、伴侶 14%，宣導「五不四要」","https://news.ltn.com.tw/news/society/breakingnews/5139175","2026-10-23 WebFetch 開啟核對；去識別化"),
   s("臺北市少年警察隊：私密照外流應變與求助管道（110、113、iWIN 02-2577-5118）","https://young.police.gov.taipei/News_Content.aspx?n=2F706BAC97CD7533&s=D7592B5544C17752&sms=AA60320A15BFA2FF","2026-10-23 WebFetch 開啟核對；去識別化")]}
PA_PEND=s("家長私下付錢壓下後遭再次勒索的台灣案例：待查","","寫手提供，待查證",False)
ALLSRC=PA_SRC["game"]+PA_SRC["mule"]+PA_SRC["date"]+PA_SRC["threat"]
ev=[]
ev.append({"id":"pa_start","age":43,"text":"孩子上國中了。這天晚上，他在房間門口站了很久，好像有話要說。","sources":ALLSRC[:3],
 "choices":[RND("等他開口",[
   O(0.3,{},"pa_game",["pa_case_game"],"孩子說，他在遊戲裡為了拿「免費點數」，把你手機收到的驗證碼傳給別人。","驗證碼給了人"),
   O(0.25,{},"pa_mule",["pa_case_mule"],"孩子說，同學找他「幫忙領包裹、領錢」，一次給兩千，他已經去了一次。","同學找他領錢"),
   O(0.25,{},"pa_date",["pa_case_date"],"孩子說，網路上認識的「學姐」要他買點數，說買了才能見面。","網友要他買點數"),
   O(0.2,{},"pa_threat",["pa_case_threat"],"孩子紅著眼說，有人威脅要把他的私密照片傳給同學，除非他付錢。","有人威脅他")],
   "四種情境比例是設計假設，不是統計")]})
REACT=lambda: [C("先罵他一頓",{"心理":-10,"人際":-8},"pa_after",["pa_scolded"],"你脫口而出：「你怎麼這麼笨！」孩子低下頭，回房間關上門。","先罵一頓","yellow"),
   C("陪他一起去報案",{"心理":-6,"警覺":8,"人際":5},"pa_after",["pa_accompanied","reported"],"你拍拍他的肩：「說出來很勇敢。我們一起處理。」你們帶著截圖去了派出所。","陪他報案"),
   C("自己出錢把事情壓下",{"存款":-15000,"心理":-14},"pa_after",["pa_paid_off"],"你照對方說的付了錢，叮嚀孩子別跟任何人說。","出錢壓下","red")]
def pcase(id,text,msgs,src,app="line_like",who="孩子"):
    ev.append({"id":id,"age":43,"text":text,"sources":src,**chat(app,"家人聊天（虛構）",who,msgs),"choices":REACT()})
pcase("pa_game","帳單上多了好幾筆你沒買過的小額付款，你的門號也被拿去綁了別人的帳號。",[M("m1","child","對方說傳驗證碼就送點數……"),M("m2","child","我以為那只是一串數字"),M("m3","child","對不起",1600)],PA_SRC["game"])
pcase("pa_mule","孩子說同學說「只是幫忙」，可是領的錢要交給一個從沒見過的人。",[M("m1","child","同學說很多人都在做，很好賺"),M("m2","child","他說不能跟大人講"),M("m3","child","我是不是做錯事了？",1600)],PA_SRC["mule"])
pcase("pa_date","孩子給你看對話：對方叫他買點數、拍下序號，才肯見面。",[M("m1","child","學姐說買了點數就跟我見面"),M("m2","child","可是買了之後她又說不夠"),M("m3","child","我零用錢都花光了",1600)],PA_SRC["date"])
pcase("pa_threat","孩子說，對方在網路上和他聊了好幾週，之後開始威脅，要他付錢。（遊戲不描述任何影像內容。）",[M("m1","child","他說不付錢就傳給我全班"),M("m2","child","我好怕"),M("m3","child","不要告訴別人好不好",1600)],PA_SRC["threat"])
ev.append({"id":"pa_after","age":44,"presentation":"timeskip","text":"幾個月過去了。","sources":ALLSRC[:2],
 "choices":[C("看看孩子最近",{},"__EVAL__",[],"日子慢慢回到原本的樣子，但有些事改變了。","幾個月後")]})
PA_RFT={}; PA_ANC={}
TH_NOTE="孩子遇到私密影像威脅時：不要付錢、保留對話與帳號、報警，並可透過 iWIN 申請下架、撥 113 求助。"
pa_end=[
 END("END_PA_COLLAPSE",1,{"flags_all":["mental_collapse"],"flags_any":["pa_paid_off","pa_scolded"]},"兩個人都撐著","🌧️","red",
  "這件事壓在你和孩子身上很久。你們都很累，卻都沒跟對方說。\n"+TH_NOTE,"未成年人遭網友以私密影像威脅付款，家長私下付款後對方持續勒索，最後仍需報警與申請下架。",PA_SRC["threat"],["孩子被要求「不要告訴大人」"],"我在家長篇撐得很辛苦。"),
 END("END_PA_HUSH",2,{"flags_all":["pa_paid_off"]},"錢壓不住","🤫","red",
  "你付了錢，對方過一陣子又來要。孩子學到的是：出事就花錢、不要說。\n"+TH_NOTE,"（待查）家長代未成年子女付款了事，對方再度聯繫要錢——此情節為推論，尚無台灣來源。",PA_SRC["threat"][1:],["對方要求付錢換取沉默"],"我在家長篇用錢壓了下來。",req=["pa_paid_off"],
  variants=[{"when":{"label":"mule","flags_all":["pa_case_mule"]},"requires_flags":["pa_case_mule"],"text":"你賠了錢，但孩子提領過的那筆錢還是被追查到。家長也可能要負連帶賠償。"}]),
 END("END_PA_SILENT",3,{"flags_all":["pa_scolded"]},"關上的門","🚪","yellow",
  "孩子之後再遇到怪事，都沒有再來找你。你是從別人那裡才知道的。","國中生遇到交友或打工陷阱，因怕被罵不敢跟家長說，事態擴大後才被發現。",PA_SRC["mule"][:1],["孩子被要求「不要告訴大人」"],"我在家長篇，孩子後來不跟我說了。",req=["pa_scolded"],
  variants=[{"when":{"label":"mule","flags_all":["pa_case_mule"]},"requires_flags":["pa_case_mule"],"text":"孩子之後還是被同學拉去領了幾次錢，被警方約談時你才知道。家長也可能要負連帶賠償。"}]),
 END("END_PA_BROKE_CYCLE",4,{"flags_all":["pa_hugged"]},"不再重複","🫂","green",
  "你想起自己當年被責怪的感覺，這次選擇先抱住他。孩子後來遇到事情，第一個找的是你。","（設計結局）家人間「先接住、再處理」的回應方式，對應衛福部兒少保護宣導。",PA_SRC["threat"][1:],["孩子被要求「不要告訴大人」"],"我在家長篇，沒有重複當年的事。",req=["pa_hugged"]),
 END("END_PA_OPEN",5,{},"願意開口的孩子","🗣️","green",
  "你們一起報了案。孩子之後遇到奇怪的訊息，會先拿來問你。","家長陪同未成年子女報案並保留證據，警方協助處理，孩子之後主動求助。",PA_SRC["game"]+PA_SRC["threat"][:1],["孩子被要求「不要告訴大人」"],"我在家長篇，孩子願意跟我說。",
  variants=[{"when":{"label":"threat","flags_all":["pa_case_threat"]},"requires_flags":["pa_case_threat"],"text":"你們一起報了案，也透過 iWIN 申請下架。孩子說：「謝謝你沒有罵我。」"}])]
for x in pa_end:
  if x["id"]=="END_PA_HUSH": x["sources_pending"]=["家長私下付錢壓下後遭再次勒索的台灣案例：待查（寫手提供，待查證）"]
  x["help_resources"]=[{"name":"iWIN 網路內容防護機構（02-2577-5118，協助下架）","url":"https://young.police.gov.taipei/News_Content.aspx?n=2F706BAC97CD7533&s=D7592B5544C17752&sms=AA60320A15BFA2FF","verified":True,"verify_note":"臺北市少年警察隊頁面列出，2026-10-23 WebFetch"},
   {"name":"113 保護專線（衛福部）","url":"https://www.mohw.gov.tw/fp-190-233-1.html","verified":True,"verify_note":"官方網站"}]
PA_MODS=[{"id":f"pa_blame_{k}","if_flags":{"all":["family_blame"]},"target":{"event":f"pa_{k}"},
   "effect":{"type":"unlock_choice","choice":C("想起當年，先抱抱他",{"心理":-4,"人際":10,"警覺":5},"pa_after",["pa_hugged","pa_accompanied","reported"],
     "你想起自己當年被罵「怎麼這麼笨」的那一刻。你沒有重複那句話，先抱住他，再一起去報案。","沒有重複當年")},
   "note":"family_blame（曾被家人責怪）：多一個不重複的選項"} for k in ("game","mule","date","threat")]
PA_MODS+=[{"id":f"pa_blame_memory_{k}","if_flags":{"all":["family_blame"]},"target":{"event":f"pa_{k}"},
   "effect":{"type":"add_interrupt","interrupt":{"at":"m3","from":"system","text":"（你想起很多年前，有人對你說：「怎麼會這麼笨？」）"}},"note":"family_blame 回憶句"} for k in ("game","mule","date","threat")]
for x in pa_end:
    if x["id"] in ("END_PA_COLLAPSE","END_PA_BROKE_CYCLE"):
        x["combined_only"]=True; x["combined_only_note"]="需要人生線帶入的心理低點或 family_blame，單獨遊玩家長篇不會出現"
pa=build("parent","家長篇",ev,pa_end,PA_RFT,PA_ANC,PA_MODS,{"mandatory":True,"content_policy_extra":"私密影像案只寫流程與後果，絕不描述影像內容"},
 {e["id"] for e in pa_end},"沒有官方統計對應家長篇情境，不放統計")
