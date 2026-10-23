import json
from common import finalize,apply_v4,apply_cross,M,SHARE_CARD,stat_null,COUNTY_SRC,DASH_SRC,DASH_MONTH,DASH_TYPE,calc_avg,COUNTY_DASH,NO_OFFICIAL,DB as DB165
S={8:"https://www.dcard.tw/f/job/p/260035407",9:"https://www.dcard.tw/f/anti_fraud/p/257882793",
10:"https://www.ptt.cc/bbs/Bunco/M.1762823791.A.A96.html",11:"https://www.ptt.cc/bbs/Bunco/M.1723002516.A.604.html",
12:"https://www.dcard.tw/f/mood/p/257343629",13:"https://www.dcard.tw/f/anti_fraud/p/255776339"}
W={"ltn_18yo":{"name":"自由時報：18歲兼職變車手，法官認定新聞常報屬常識，判4月","url":"https://news.ltn.com.tw/news/society/breakingnews/3969039","verified":True,"verify_note":"依搜尋摘錄核對（直接連線回 403）"},
"ltn_student":{"name":"自由時報：大學生當車手交保再犯，宣告刑合計逾7年、民事判賠200萬","url":"https://news.ltn.com.tw/news/Taichung/breakingnews/4677183","verified":True,"verify_note":"依搜尋摘錄核對（直接連線回 403）"},
"ltn_civil":{"name":"自由時報：車手常須負民事連帶賠償，判賠數百萬至上千萬","url":"https://news.ltn.com.tw/news/society/paper/1686908","verified":True,"verify_note":"依搜尋摘錄核對（直接連線回 403）"},
"judgment":{"name":"臺灣士林地方法院112年度金訴緝字第17號刑事判決（司法院裁判書系統，去識別化引用）","url":"https://judgment.judicial.gov.tw/FJUD/data.aspx?ty=JD&id=SLDM%2c112%2c%e9%87%91%e8%a8%b4%e7%b7%9d%2c17%2c20230619%2c1","verified":True,"verify_note":"2026-10-23 WebFetch 官方頁核對：裁判日期112-06-19、應執行有期徒刑2年10月；curl 會被 bot-defense 擋"},
"moj_manual":{"name":"法務部詐欺防制法治教育手冊（第四章 收簿手、車手的刑事與民事責任）","url":"https://www.freemoo.com.tw/webebook/2025Tang_moj/files/basic-html/page35.html"}}
LAW={"339-4":("刑法§339-4 加重詐欺","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=339-4"),
"aml19":("洗錢防制法§19 一般洗錢","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380131&flno=19"),
"aml22":("洗錢防制法§22 無正當理由提供帳戶","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380131&flno=22"),
"org3":("組織犯罪防制條例§3","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000013&flno=3"),
"civ185":("民法§185 共同侵權連帶賠償","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=185"),
"rec6":("警察刑事紀錄證明核發條例§6","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=D0080088&flno=6"),
"civil28":("公務人員任用法§28","https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=S0020001&flno=28")}
HL=[{"name":"165全民防騙網（撥打165）","url":"https://165.npa.gov.tw/"},{"name":"1925安心專線","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html"}]
def src(*k):
    o=[]
    for x in k:
        if isinstance(x,int): o.append({"story_id":x,"url":S[x]})
        elif x in W: o.append(W[x])
        else: o.append({"name":LAW[x][0],"url":LAW[x][1]})
    return o
def C(text,effects,nxt,require=None,set_flags=None): return {"text":text,"effects":effects,"next":nxt,"flags":{"set":set_flags or [],"require":require or []}}
E=[]
def ev(id,age,text,choices,sources,**kw): E.append({"id":id,"age":age,"text":text,"choices":choices,"sources":sources,**kw})
R="END_ROUTER"
ev("birth",0,"你出生在{county}的{family}家庭。這一生只有一次，選擇無法重來。",[C("長大",{},"teen")],[COUNTY_SRC,COUNTY_DASH])
ev("teen",16,"高一時，學校來宣導「不要出借帳戶」。台下同學在滑手機。",
 [C("認真聽，記下165",{"警覺":8},"broke"),C("趴著睡覺",{},"broke")],src("moj_manual"))
ev("broke",20,"你剛上大學（或剛出社會），房租、學貸、手機分期壓得喘不過氣，存款快見底。",
 [C("找家人或學校談經濟困難、申請補助",{"人際":5,"心理":5,"存款":10000},"job_ad",set_flags=["asked_help"]),
  C("自己扛，上網找快錢",{"心理":-5},"job_ad")],src("moj_manual"))
ev("job_ad",20,"社群上一則徵才：「居家輕鬆、日領三千、免經驗，私訊加好友」。對方很親切，說是正派公司。",
 [C("搜尋公司統編、上正規求職網站看是否有正式職缺",{"警覺":10},"job_check"),
  C("直接加好友私聊",{"警覺":-5},"job_offer",set_flags=["missed_too_good"])],src(10,"ltn_18yo"))
ev("job_check",20,"查不到公司登記，對方改口說是「新創、還沒登記」。",
 [C("不合理，封鎖並向165通報",{"警覺":15},R,set_flags=["refused"]),
  C("新創也很正常吧",{},"job_offer",set_flags=["missed_too_good"])],src(11,"moj_manual"))
ev("job_offer",20,"對方說第一份任務很簡單：把你的金融卡和密碼寄過去「申請補助」，或提供帳戶給公司「代收貨款、節稅」，每本有酬勞。",
 [C("正常工作不會要員工的金融卡、密碼或個人帳戶收公司款；拒絕",{"警覺":15},R,set_flags=["refused"]),
  C("問朋友意見",{"人際":3},"friend_warn"),
  C("照做，拿到第一筆酬勞",{"存款":5000,"警覺":-10},"account_used",set_flags=["gave_account","paid_for_account","missed_card_request"])],src(8,9,11,"aml22"))
ev("friend_warn",20,"朋友傳了一篇新聞給你：「求職提供帳戶，變警示戶還被告」。",
 [C("謝謝提醒，拒絕這份工作",{"警覺":10,"人際":5},R,set_flags=["refused"]),
  C("覺得朋友太緊張，還是照做",{"存款":5000,"人際":-10},"account_used",set_flags=["gave_account","paid_for_account","missed_card_request","ignored_friend"])],src(11,13))
ev("account_used",21,"幾天後，你的帳戶突然有好幾筆陌生人的匯款進出。對方說：「接下來升級任務，外出幫公司收款，每趟另有獎金。」",
 [C("覺得不對，立刻停止並主動到派出所說明",{"警覺":15,"心理":-10},"police_call",set_flags=["self_reported"]),
  C("先不做升級任務，但也不聲張",{"心理":-10},"police_call"),
  C("接受升級任務",{"存款":20000,"警覺":-10},"family_notice",set_flags=["became_mule","missed_salary_from_cash"])],src(10,11,"ltn_18yo"))
ev("family_notice",21,"家人發現你最近常常臨時出門、手頭突然變寬，問你在做什麼工作。",
 [C("說出實情，家人陪你去報警、停止",{"人際":5,"心理":-5},"police_call",set_flags=["family_stopped"]),
  C("敷衍帶過，繼續做",{"人際":-15,"心理":-10},"arrest",set_flags=["missed_family_warning"])],src(10))
ev("arrest",21,"某天你在外面時被警察攔下。原來被害人早已報案，你是整條線上最容易被找到的人。",
 [C("配合偵查、坦承",{"心理":-20},"trial",set_flags=["arrested","confessed"]),
  C("堅稱只是打工，什麼都不知道",{"心理":-25},"trial",set_flags=["arrested"])],src("ltn_student","judgment","ltn_18yo"))
ev("trial",22,"你被以加重詐欺、洗錢、參與犯罪組織起訴。法官說：反詐宣導這麼多年，『只是求職』很難當藉口。被害人也提起民事求償。",
 [C("盡力與被害人和解、分期賠償",{"存款":-200000,"心理":-10},R,set_flags=["convicted","settled"]),
  C("不出庭、不理民事",{"存款":-500000,"人際":-10,"心理":-15},R,set_flags=["convicted","civil_judgment"])],
 src("339-4","aml19","org3","civ185","ltn_student","ltn_civil"))
ev("police_call",21,"警察來電：你的帳戶涉及詐欺案，被列為警示帳戶，請你到案說明。",
 [C("帶著求職對話紀錄、廣告截圖到案說明",{"警覺":10,"心理":-10},"aftermath",set_flags=["kept_evidence"]),
  C("慌了，刪掉所有聊天紀錄",{"心理":-20,"警覺":-5},"aftermath",set_flags=["deleted_evidence"])],src(9,12,13,"aml22"))
ev("aftermath",22,"調查結果出來了，帳戶凍結期間你無法領薪、轉帳，銀行也對你另眼相看。",
 [C("繼續生活",{"心理":-5},R)],src(12,13))
ev(R,23,"多年後回頭看這段經歷……（引擎依 ending_rules 自動判定結局，不顯示選項）",[C("回顧",{},"__EVAL__")],HL,router=True)

def card(sid,summary,url): return {"story_id":sid,"summary":summary,"url":url,"note":"去識別化改寫，細節以原文為準"}
EN=[
 {"id":"END_CONVICTED","priority":1,"conditions":{"flags_all":["convicted"],"flags_none":["settled"],"any_of":[{"flags_all":["civil_judgment"]},{"stats":{"存款":{"lte":0}}},{"stats":{"心理":{"lte":20}}}]},
  "text":"你被判有罪，留下前科，還背著民事賠償。真正的上游沒被抓到，被害人的損失落在你身上。有罪判決確定的紀錄可能會出現在「良民證」（警察刑事紀錄證明）上，碰到要繳交良民證的工作，求職可能會受影響。",
  "case_card":card("ltn_student","一名大學生當車手，交保後又再犯，各案宣告刑合計逾7年；不出庭也沒有和解，民事被判賠被害人200萬元。",W["ltn_student"]["url"]),
  "missed_red_flags":["日領三千、免經驗的高薪輕鬆工作","薪水從經手的款項裡抽成","家人關心時選擇隱瞞","有被害人就有民事連帶賠償"],
  "sources":src("ltn_student","ltn_civil","339-4","aml19","org3","civ185","rec6","civil28")+HL},
 {"id":"END_RECORD","priority":2,"conditions":{"flags_all":["convicted"]},
  "text":"你坦承犯行、努力分期賠償，法院也有考量。但你已經有了犯罪紀錄。如果獲判緩刑，依法良民證上不會記載這筆紀錄；即使如此，往後的人生仍可能受到影響。",
  "case_card":card("ltn_18yo","18歲學生在社群網站的兼職社團應徵，提供帳戶並轉交款項；法院認為反詐宣導已是一般常識，依洗錢防制法判4月，並須賠償被害人。",W["ltn_18yo"]["url"]),
  "missed_red_flags":["對方要你的帳戶","你自己都問過『這合法嗎？』，表示已經起疑","收入跟付出完全不成比例"],
  "sources":src("ltn_18yo","judgment","339-4","aml19","civ185","rec6")+HL},
 {"id":"END_ACCOUNT","priority":3,"conditions":{"flags_all":["gave_account"],"flags_none":["became_mule"]},
  "text":"你沒有去收款，但帳戶已經被拿去當收贓款的工具。帳戶被警示凍結，你被調查、做筆錄。就算最後沒有被起訴，好幾年裡辦帳戶、借貸都處處受限。",
  "case_card":card(11,"一名女性應徵行政助理，用自己的薪轉戶替「老闆」收大筆款項再匯出，一個月經手約3000萬；所有帳戶被凍結，本人失業並接受調查。",S[11]),
  "missed_red_flags":["正職工作不會用員工的個人帳戶收公司款","要金融卡、密碼＝紅燈","面試地點是日租會議室","提供帳戶收取對價可能觸犯洗錢防制法§22"],
  "sources":src(11,9,12,13,"aml22")+HL},
 {"id":"END_RESCUED","priority":4,"conditions":{"flags_any":["family_stopped","self_reported"],"stats":{"人際":{"gte":20}}},
  "text":"你在越陷越深之前停下來了，靠的是家人，或是自己的那一點不安。你還是得面對調查，但你沒有走到最壞的那一步。",
  "case_card":card(10,"一名28歲女性在社群網站應徵「外務收款」，母親察覺不對而報警，警方埋伏逮到詐團成員，本人沒有受損。",S[10]),
  "missed_red_flags":["薪水從收來的錢裡扣","外出收「公司款項」卻沒有正式公司"],
  "sources":src(10,"aml22")+HL},
 {"id":"END_REFUSE","priority":5,"conditions":{"flags_all":["refused"],"flags_none":["gave_account"]},
  "text":"你拒絕了那份「輕鬆高薪」的工作。錢還是很緊，但你的名字、帳戶和未來都還乾乾淨淨。",
  "case_card":card(8,"一位母親做社群網站上的居家打字工作，被要求用自己的帳戶代收款「節稅」，結果被被害人提告，必須請律師處理。對照之下，你在第一步就拒絕了。",S[8]),
  "missed_red_flags":["你抓到了：查不到公司登記、要帳戶或金融卡、報酬高得不合理"],
  "sources":src(8,"moj_manual")+HL},
]
data={"meta":{"title":"80億分之1：求職變車手線","version":"0.1","language":"zh-TW","one_life":True,
 "content_policy":"只呈現受騙過程與法律、人生後果；不含提領、取款、規避查緝、轉帳等任何可照做的操作細節",
 "engine_notes":"同投資線：next=='__EVAL__' 時依 ending_rules 判定；數值夾在 min/max 之間"},
 "ending_rules":{"evaluation":"依 priority 由小到大檢查 endings[].conditions，第一個成立者為結局；都不成立用 fallback","fallback":"END_ACCOUNT",
  "condition_grammar":{"flags_all":"全部都要有","flags_any":"至少一個","flags_none":"都不能有","stats":"{數值:{gt|gte|lt|lte:數字}}","any_of":"子條件任一成立；與同層其他鍵為 AND"}},
 "stats":[
  {"label":"刑法§339-4 加重詐欺","value":"處一年以上七年以下有期徒刑，得併科一百萬元以下罰金","verified":"2026-10-23 逐字核對","source":LAW["339-4"][1]},
  {"label":"洗錢防制法§19 一般洗錢","value":"處三年以上十年以下有期徒刑，併科新臺幣一億元以下罰金；洗錢財物未達一億元者，處六月以上五年以下有期徒刑，併科新臺幣五千萬元以下罰金","verified":"2026-10-23 逐字核對","source":LAW["aml19"][1]},
  {"label":"洗錢防制法§22 無正當理由提供帳戶","value":"原則由警察機關裁處告誡；期約或收受對價、提供三個以上帳戶、或告誡後五年內再犯者，處三年以下有期徒刑、拘役或科或併科新臺幣一百萬元以下罰金；金融機構得暫停、限制或關閉帳戶","verified":"2026-10-23 逐字核對","source":LAW["aml22"][1]},
  {"label":"組織犯罪防制條例§3 參與犯罪組織","value":"參與者，處六月以上五年以下有期徒刑，得併科新臺幣一千萬元以下罰金。但參與情節輕微者，得減輕或免除其刑","verified":"2026-10-23 逐字核對","source":LAW["org3"][1]},
  {"label":"民法§185 共同侵權","value":"數人共同不法侵害他人之權利者，連帶負損害賠償責任","verified":"2026-10-23 逐字核對","source":LAW["civ185"][1]},
  {"label":"警察刑事紀錄證明核發條例§6（良民證記載範圍）","value":"明確記載有無刑事案件紀錄；但受緩刑之宣告未經撤銷者、受拘役罰金之宣告者、經易科罰金或易服社會勞動執行完畢五年內未再受有期徒刑以上刑之宣告者等，不予記載","verified":"2026-10-23 逐字核對","source":LAW["rec6"][1]},
  {"label":"公務人員任用法§28 第1項第5款","value":"犯（內亂外患、貪污以外之）罪，判處有期徒刑以上之刑確定，尚未執行或執行未畢者，不得任用為公務人員。但受緩刑宣告者，不在此限","verified":"2026-10-23 逐字核對","source":LAW["civil28"][1]},
  *DASH_MONTH[:2],
  {"label":"前科對民間求職的實際影響","value":"劇本只用「可能」描述；沒有統計數據","verified":"待核實：查無可引用的統計數據"}],
 "stats_sources":[DASH_SRC]+[{"name":v[0],"url":v[1]} for v in LAW.values()]+list(W.values()),
 "player_init":{"stats":{"存款":{"min":0,"init_range":[5000,80000]},"警覺":{"min":0,"max":100,"init_range":[15,45]},
   "人際":{"min":0,"max":100,"init_range":[20,70]},"心理":{"min":0,"max":100,"init_range":[40,80]}},
  "county_pool":["臺北市","新北市","桃園市","臺中市","臺南市","高雄市","新竹市","新竹縣","基隆市","苗栗縣","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"],
  "family_pool":[{"name":"小康","存款_mod":0},{"name":"單親","存款_mod":-0.3,"心理":-5},{"name":"務農","人際":5},{"name":"經商","存款_mod":0.5}],
  "start_event":"birth","flags":[]},
 "events":E,"endings":EN}
# ---- v3 ----
for e in EN:
    if e["id"]=="END_CONVICTED":
        e["conditions"]={"flags_all":["convicted"],"flags_none":["settled"],"any_of":[{"flags_all":["civil_judgment"]},{"flags_all":["savings_depleted"]},{"flags_all":["mental_collapse"]}]}
        e["reason_texts"]=[{"flag":"civil_judgment","text":"你沒出庭、也不處理民事，法院判你賠償全額。"},
          {"flag":"savings_depleted","text":"賠償和律師費讓你的存款歸零（存款≤0）。"},
          {"flag":"mental_collapse","text":"官司拖了好幾年，你的心理狀態跌到谷底（心理≤20）。"}]
    if e["id"]=="END_RESCUED":
        e["conditions"]={"flags_any":["family_stopped","self_reported"],"flags_all":["has_support"]}
        e["reason_texts"]=[{"flag":"family_stopped","text":"家人察覺不對，陪你一起停下來。"},{"flag":"self_reported","text":"你相信自己的不安，主動去說明。"}]
    if e["id"]=="END_ACCOUNT":
        e["reason_texts"]=[{"flag":"gave_account","text":"你的帳戶被拿去收被害人的錢。"},
          {"flag":"self_reported","text":"你雖然主動說明了，但身邊沒有人陪你撐過調查（人際<20），帳戶的後遺症只能自己扛。"},
          {"flag":"deleted_evidence","text":"你刪掉了聊天紀錄，很難證明自己是被騙去求職的。"}]
RF={"missed_too_good":"「日領三千、免經驗、居家輕鬆」高得不合理。",
 "missed_card_request":"正職工作不會要你的金融卡、密碼或個人帳戶。",
 "missed_salary_from_cash":"薪水從你經手的錢裡抽成，這不是正常的工作。",
 "missed_family_warning":"家人問起時，你選擇了隱瞞。"}
finalize(data,RF)
# ================= v4：沉浸呈現 =================
# 內容原則：訊息只呈現詐團話術與受害者反應；不描述任何提領、交付、規避查緝的做法。
APP="聊聊 Chatto（虛構）"
REC={"app":"line_like","app_display_name":APP,"theme":"fictional_green_free","contact":{"name":"人資 Amy（自稱）","avatar":"placeholder_silhouette","status":"在線上"}}
V4={
 "job_ad":{"presentation":"chat","chat":{"app":"sms_like","app_display_name":"社群動態（虛構）","theme":"neutral","contact":{"name":"兼職好康分享團","avatar":"placeholder_group","status":"社團貼文"},"messages":[
   M("m1","scammer","【急徵】居家輕鬆、日領三千、免經驗"),M("m2","scammer","正派公司，名額有限，有興趣私訊我",900),
   M("m3","player","（日領三千……房租好像有救了）")]}},
 "job_check":{"presentation":"chat","chat":{**REC,"messages":[
   M("m1","player","我查不到貴公司的登記耶"),M("m2","scammer","我們是新創，還在跑登記流程啦",1500),
   M("m3","scammer","很多大公司一開始也這樣，別想太多～")]}},
 "job_offer":{"presentation":"chat","pressure":{"timer_s":30,"can_disable":True,"label":"對方催你回覆"},"chat":{**REC,"messages":[
   M("m1","scammer","恭喜錄取！第一份任務很簡單"),M("m2","scammer","把金融卡和密碼寄來，我們幫你「申請補助」",1400),
   M("m3","scammer","或提供帳戶幫公司代收貨款、節稅，每本都有酬勞"),M("m4","scammer","今天要回覆喔，後面還很多人排隊",800),
   M("m5","player","要給卡和密碼……這樣正常嗎？")]}},
 "friend_warn":{"presentation":"chat","chat":{"app":"line_like","app_display_name":APP,"theme":"fictional_green_free","contact":{"name":"大學同學 阿哲","avatar":"placeholder_silhouette","status":"在線上"},"messages":[
   M("m1","friend","欸你說的那個工作，是不是要你給帳戶？"),M("m2","friend","（傳來新聞：求職提供帳戶，變警示戶還被告）",1000,"link"),
   M("m3","friend","正常公司不會跟你要卡跟密碼啦")]}},
 "account_used":{"presentation":"chat","interrupts":[{"at":"m2","from":"系統通知","text":"您的帳戶有多筆不明入帳"}],"chat":{**REC,"messages":[
   M("m1","scammer","你表現很好，主管很欣賞你"),M("m2","scammer","接下來有升級任務，每趟另有獎金",1200),
   M("m3","scammer","薪水直接從經手的款項裡抽成，很方便"),M("m4","player","（帳戶裡怎麼一直有陌生人的錢……）")]}},
 "family_notice":{"presentation":"chat","chat":{"app":"in_person","app_display_name":"家裡客廳","theme":"neutral","contact":{"name":"媽媽","avatar":"placeholder_silhouette","status":"面對面"},"messages":[
   M("m1","family","你最近怎麼常常臨時出門？"),M("m2","family","手頭好像突然變寬了，是在做什麼工作？",1400),
   M("m3","player","（要說實話嗎……）")]}},
 "police_call":{"presentation":"chat","chat":{"app":"phone_call","app_display_name":"來電","theme":"neutral","contact":{"name":"轄區派出所（已自行查證號碼）","avatar":"placeholder_silhouette","status":"通話中"},"messages":[
   M("m1","police","你的帳戶涉及詐欺案，已列為警示帳戶"),M("m2","police","請你到案說明，有相關紀錄可以一起帶來",1400),
   M("m3","player","（腦袋一片空白……）")]}},
}
ANCH={"missed_too_good":[{"event":"job_ad","message":"m1"},{"event":"job_check","message":"m2"}],
 "missed_card_request":[{"event":"job_offer","message":"m2"},{"event":"friend_warn","message":"m3"}],
 "missed_salary_from_cash":[{"event":"account_used","message":"m3"}],
 "missed_family_warning":[{"event":"family_notice","message":"m2"}]}
_NR="165 儀表板的受理統計以被害人遭遇的詐騙手法分類，沒有「求職被吸收成車手／提供帳戶」這個類別（車手與人頭帳戶在法律上是共犯或被告，而不是被害類型），因此算不出對應比例，不硬套其他類別"
EV4={
 "END_CONVICTED":{"title":"替上游扛下一切的人","title_emoji":"⛓","grid_color":"red","share_text":"我以為只是打工，結果被判有罪、還要賠錢。"},
 "END_RECORD":{"title":"留下紀錄的人","title_emoji":"📄","grid_color":"red","share_text":"我坦承、我賠償，但紀錄還是留下了。"},
 "END_ACCOUNT":{"title":"帳戶被借走的人","title_emoji":"🧊","grid_color":"yellow","share_text":"我只是給了帳戶，人生就被凍結了好幾年。"},
 "END_RESCUED":{"title":"被拉回來的人","title_emoji":"🤝","grid_color":"yellow","share_text":"還好有人拉了我一把。"},
 "END_REFUSE":{"title":"第一步就說不的人","title_emoji":"🛡","grid_color":"green","share_text":"日領三千的工作，我第一步就拒絕了。你呢？"}}
for k,v in EV4.items(): v.update({"rarity_key":"mule_"+k,"real_world_stat":stat_null(_NR),"share_card":SHARE_CARD})
META4={"presentation_notes":("同投資線：presentation='chat' 以全螢幕仿聊天室呈現；畫面一律使用虛構 app 名稱與外觀。"
   "本線聊天內容只呈現詐團話術與受害者反應，不含提領、交付、規避查緝的任何做法。"),
 "no_pressure_mode":{"available":True,"default":False,"effect":"關閉所有 pressure 倒數；不影響劇情與結局","min_timer_s":20},
 "life_grid":{"bucket_years":5,"colors":{"green":"安全","yellow":"有疑點","red":"受騙損失"},"rule":"同投資線"},
 "real_world_stat_notes":"real_world_stat 是詐騙類型占 115-09 全國受理件數的比例，不是結局稀有度。本線沒有對應類別，全部為 null 並附 null_reason。"}
apply_v4(data,V4,ANCH,EV4,META4)
def CC(t,e,n,sf=None,rq=None): return {"text":t,"effects":e,"next":n,"flags":{"set":sf or [],"require":rq or []},"grid":"green","cross_line":True}
apply_cross(data,[
 {"id":"mule_cash_broke","if_flags":{"all":["cash_strapped"]},"target":{"event":"broke"},
  "effect":{"type":"rewrite_text","field":"text","text":"你剛上大學（或剛出社會）。從小就常為錢煩惱的你，這次房租、學貸、手機分期一起到期，存款只剩幾百塊。"},
  "note":"急需用錢：開場壓力更大"},
 {"id":"mule_cash_lure","if_flags":{"all":["cash_strapped"]},"target":{"event":"job_ad"},"effect":{"type":"stats_delta","stats":{"警覺":-8,"心理":-5}},
  "note":"急需用錢讓高薪誘惑更強"},
 {"id":"mule_cash_lure_msg","if_flags":{"all":["cash_strapped"]},"target":{"event":"job_ad"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"系統通知","text":"本期房租已逾期 3 天"}},"note":"催繳通知加深壓力"},
 {"id":"mule_wary","if_flags":{"all":["wary_of_easy_money"]},"target":{"event":"job_ad"},"effect":{"type":"stats_delta","stats":{"警覺":10}},
  "note":"對快錢有戒心，較容易識破"},
 {"id":"mule_wary_unlock","if_flags":{"all":["wary_of_easy_money"],"none":["cash_strapped"]},"target":{"event":"job_ad"},
  "effect":{"type":"unlock_choice","choice":CC("想起以前學到的：「輕鬆高薪」通常有問題。不回覆，向165通報這則貼文",{"警覺":15},"END_ROUTER",["refused"])},
  "note":"多一個第一步就拒絕的選項"},
 {"id":"mule_pressure_signer","if_flags":{"all":["pressure_signer"]},"target":{"event":"job_offer"},"effect":{"type":"stats_delta","stats":{"警覺":-5}},
  "note":"容易在催促下當場答應"},
 {"id":"mule_lent","if_flags":{"all":["lent_money_lost"]},"target":{"event":"friend_warn"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"內心","text":"上次借錢給朋友被倒，現在聽朋友的話好像也……"}},"note":"借錢被倒後對朋友的信任較低"},
 {"id":"mule_lent_stat","if_flags":{"all":["lent_money_lost"]},"target":{"event":"friend_warn"},"effect":{"type":"stats_delta","stats":{"人際":-5}},"note":"人際-"},
 {"id":"mule_evidence","if_flags":{"all":["evidence_habit"]},"target":{"event":"police_call"},
  "effect":{"type":"rewrite_text","field":"choice_text","text":"你本來就有截圖存證的習慣：帶著完整的求職對話、廣告截圖到案說明"},"target_note":"choice 0",
  "note":"保留紀錄的習慣讓說明更有依據"},
 {"id":"mule_family_pass","if_flags":{"all":["family_passphrase"]},"target":{"event":"family_notice"},"effect":{"type":"stats_delta","stats":{"人際":5}},
  "note":"家裡有事先約好的通關密語、習慣互相確認，家人更容易開口、你也更願意說實話"}])
for m in data["cross_line_modifiers"]:
    if m["id"]=="mule_evidence": m["target"]["choice"]=0; m.pop("target_note")
# ================= v4.2：結局規則重整（文字必須與實際路徑一致） =================
from common import finalize_v42
ENX={x["id"]:x for x in data["endings"]}
# 1) 自己報警且身邊有人支持 → RESCUED（priority 移到 ACCOUNT 之前）
ENX["END_RESCUED"].update({"priority":3,
  "conditions":{"flags_any":["family_stopped","self_reported"],"flags_all":["gave_account","has_support"],"flags_none":["convicted"]},
  "text":"你在越陷越深之前停下來了。你還是得面對調查，但你沒有走到最壞的那一步。",
  "text_variants":[
   {"when":{"label":"family","flags_all":["family_stopped"]},"requires_flags":["became_mule","family_stopped"],
    "text":"你已經接下了「升級任務」，是家人察覺不對、陪你一起停下來去說明。你還是得面對調查，但你沒有走到最壞的那一步。"},
   {"when":{"label":"self","flags_all":["self_reported"]},"requires_flags":["self_reported"],"forbids_flags":["became_mule"],
    "text":"帳戶被拿去收陌生人的錢之後，你相信了自己的不安，主動到派出所說明，沒有接下「升級任務」。你還是得面對調查，但身邊有人陪你撐過去。"}],
  "requires_flags":["gave_account","has_support"],"forbids_flags":["convicted","arrested"]})
# 2) 當了車手、被家人阻止、但身邊沒人支持（人際<20）→ 新結局 END_STOPPED_ALONE
ENX["END_ACCOUNT"].update({"priority":4,"requires_flags":["gave_account"],"forbids_flags":["became_mule","convicted","arrested"]})
NEW={"id":"END_STOPPED_ALONE","priority":3.5,
 "conditions":{"flags_all":["became_mule","family_stopped"],"flags_none":["convicted","has_support"]},
 "text":"家人察覺不對之後，你停了下來，也去說明了。但你已經接過「升級任務」，帳戶和經手的款項都要接受調查。這段時間你和身邊的人越來越疏遠，很多事只能自己扛。",
 "reason_texts":[{"flag":"became_mule","text":"你接下了「升級任務」，不只是提供帳戶而已。"},
   {"flag":"family_stopped","text":"是家人讓你停下來的。"},
   {"flag":"isolated","text":"你和身邊的人很疏遠（人際≤15），調查期間沒有人能陪你。"},
   {"flag":"deleted_evidence","text":"你刪掉了聊天紀錄，很難證明自己是被騙去求職的。"}],
 "case_card":ENX["END_RESCUED"]["case_card"],
 "missed_red_flags":["薪水從經手的款項裡抽成","外出替「公司」收款卻沒有正式公司","帳戶出現陌生人的匯款"],
 "sources":ENX["END_RESCUED"]["sources"],
 "requires_flags":["became_mule","family_stopped"],"forbids_flags":["convicted","arrested","has_support"],
 "title":"停下來，卻只能自己扛的人","title_emoji":"🌧","grid_color":"red","rarity_key":"mule_END_STOPPED_ALONE",
 "real_world_stat":stat_null(_NR),"share_text":"我停下來了，但後果只能一個人扛。","share_card":SHARE_CARD}
data["endings"].append(NEW)
# 3) 其他結局的前提
ENX["END_CONVICTED"].update({"requires_flags":["convicted","arrested","civil_judgment"],"forbids_flags":["settled"]})
ENX["END_RECORD"].update({"requires_flags":["convicted","arrested","settled"],"forbids_flags":["civil_judgment"],
  "text":"你努力分期賠償，法院也有考量。但你已經有了犯罪紀錄。如果獲判緩刑，依法良民證上不會記載這筆紀錄；即使如此，往後的人生仍可能受到影響。",
  "text_variants":[
   {"when":{"label":"confessed","flags_all":["confessed"]},"requires_flags":["confessed"],
    "text":"你坦承犯行、努力分期賠償，法院也有考量。但你已經有了犯罪紀錄。如果獲判緩刑，依法良民證上不會記載這筆紀錄；即使如此，往後的人生仍可能受到影響。"},
   {"when":{"label":"denied","flags_none":["confessed"]},"forbids_flags":["confessed"],
    "text":"你一開始堅稱「只是打工」，後來仍努力和被害人和解、分期賠償，法院也有考量。但你已經有了犯罪紀錄。如果獲判緩刑，依法良民證上不會記載這筆紀錄；即使如此，往後的人生仍可能受到影響。"}]})
ENX["END_REFUSE"].update({"requires_flags":["refused"],"forbids_flags":["gave_account","became_mule","convicted"]})
data["ending_rules"]["evaluation"]+="（v4.2：RESCUED 3 → STOPPED_ALONE 3.5 → ACCOUNT 4）"
# ================= v4.4：更重的負面結局（家人失和／心理崩潰／被親友切割） =================
# 原則：只寫後果，不寫任何犯罪操作；提到輕生只用非畫面化描述，並附求助資源。
HELP3=[{"name":"1925安心專線（衛福部，24小時免付費）","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html","verified":True,"verify_note":"2026-10-23 curl HTTP 200"},
 {"name":"1995生命線協談專線","url":"https://www.life1995.org.tw/","verified":True,"verify_note":"2026-10-23 curl HTTP 200"},
 {"name":"165反詐騙諮詢專線（警政署）","url":"https://165.npa.gov.tw/","verified":True}]
#
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
_CUT_BASE="你被判有罪。家人在親戚群組裡說「這是他自己選的，我們不會幫他」，之後就不再回你訊息；朋友也陸續封鎖你。開庭、找工作、面對被害人，全都只能一個人去。"

LAF={"name":"法律扶助基金會 全國專線 412-8518（市話直撥，手機加02；免費法律諮詢，犯罪被害人也可諮詢）","url":"https://www.laf.org.tw/tel-ext","verified":True,"verify_note":"2026-10-23 curl HTTP 200，官網頁面載明 412-8518"}
_LAF_LINE="需要法律協助（刑事、民事求償、分期和解）：法律扶助基金會 412-8518（手機加02）。"
NEW={"id":"END_CUT_OFF","priority":0.5,
 "conditions":{"flags_all":["convicted","isolated"]},
 "text":_CUT_BASE+HELP_LINE+_LAF_LINE,
 "text_variants":[
  {"when":{"label":"civil","flags_all":["civil_judgment"],"flags_none":["mental_collapse"]},"requires_flags":["civil_judgment"],"forbids_flags":["settled","mental_collapse"],
   "text":"你被判有罪，也沒去處理民事，法院判你賠償全額。家人在親戚群組裡說「這是他自己選的，我們不會幫他還」，之後就不再回你訊息；朋友也陸續封鎖你。前科加上一大筆債，只能一個人背。"+HELP_LINE+_LAF_LINE},
  {"when":{"label":"settled","flags_all":["settled"],"flags_none":["mental_collapse"]},"requires_flags":["settled"],"forbids_flags":["civil_judgment","mental_collapse"],
   "text":"你被判有罪，也努力和被害人和解、分期賠償，但家人說「這是他自己選的，我們不會幫他」，之後就不再回你訊息；朋友也陸續封鎖你。每個月的賠償款，只能一個人慢慢還。"+HELP_LINE+_LAF_LINE},
  {"when":{"label":"collapse","flags_all":["mental_collapse"]},"requires_flags":["mental_collapse"],
   "text":_CUT_BASE+"你開始失眠、什麼都不想做，覺得自己毀了所有人的生活。後來你去看了身心科，才知道這種狀態需要治療，不是撐一撐就會過去。"+HELP_LINE+_LAF_LINE}],
 "reason_texts":[{"flag":"convicted","text":"你經手了被害人的錢，被依詐欺、洗錢判刑。"},
   {"flag":"missed_family_warning","text":"家人提醒過你，你沒有理會。"},
   {"flag":"isolated","text":"你和家人、朋友的關係已經斷了（人際≤15）。"},
   {"flag":"civil_judgment","text":"你不處理民事，法院判你賠償全額。"},
   {"flag":"mental_collapse","text":"判決、債務和孤立讓你的心理狀態跌到谷底（心理≤20）。"}],
 "case_card":dcard((70,DK["nown_cutoff"]["url"]),"一名成年男子涉嫌擔任詐騙車手被捕（報導當時為涉嫌、尚未判決）。他的家人公開表示和他切割、不會出面幫忙，並把孩子接回照顧。另有一件案例：一名16歲少年當車手只拿到2千元，因為未成年，父母被法院判連帶賠償157萬元。"),
 "missed_red_flags":["家人提醒時選擇不理，最後連能陪你的人都沒了","「領錢、轉交」就是車手，報酬再少也要負刑事與民事責任","刑事判決之外還有民事求償，債不會因為服刑就消失"],
 "sources":[DK["nown_cutoff"],DK["cna_parents"],DK["civ187"],DK["ly_report"]]+ENX["END_CONVICTED"]["sources"]+HELP3+[LAF],
 "requires_flags":["convicted","arrested","isolated"],"forbids_flags":["has_support"],
 "title":"被所有人切割的人","title_emoji":"✂️","grid_color":"red","rarity_key":"mule_END_CUT_OFF",
 "real_world_stat":stat_null(_NR+"；官方統計也沒有『被親友切割』的分類或人數"),"share_text":"判決之後，家人在群組說：這是他自己選的。","share_card":SHARE_CARD,"help_resources":HELP3+[LAF]}
data["endings"].append(NEW)
data["ending_rules"]["evaluation"]+="（v4.4：CUT_OFF 0.5 最先檢查）"
# ================= v4.5：STOPPED_ALONE 重調機率、童年 flag told_truth =================
# 舊條件只靠「人際<20」，人際初始 20–70，均勻抽樣下約 0.04%（審稿估約 1/3000）。
# 新條件：當了車手＋被家人攔下，且（之前無視朋友的提醒 ignored_friend，或身邊沒人支持）。
# 「無視朋友提醒」本身就是人際裂痕，劇情上也說得通；priority 2.9 排在 RESCUED 之前。
SA=next(x for x in data["endings"] if x["id"]=="END_STOPPED_ALONE")
SA.update({"priority":2.9,
 "conditions":{"flags_all":["became_mule","family_stopped"],"flags_none":["convicted"],
   "any_of":[{"flags_all":["ignored_friend"]},{"flags_none":["has_support"]}]},
 "requires_flags":["became_mule","family_stopped"],"forbids_flags":["convicted","arrested"],
 "text_variants":[
  {"when":{"label":"ignored_friend","flags_all":["ignored_friend"]},"requires_flags":["ignored_friend"],
   "text":"家人察覺不對之後，你停了下來，也去說明了。但你已經接過「升級任務」，帳戶和經手的款項都要接受調查。當初提醒你的朋友，你沒聽；事後你一直開不了口找他，很多事只能自己扛。"},
  {"when":{"label":"alone","flags_none":["has_support"]},"forbids_flags":["has_support"],
   "text":SA["text"]}]})
SA["reason_texts"].append({"flag":"ignored_friend","text":"朋友提醒過你，你沒聽，之後也不好意思再找他。"})
data["ending_rules"]["evaluation"]+="（v4.5：STOPPED_ALONE 改為 2.9，條件加入 ignored_friend）"
data["cross_line_modifiers"].append(
 {"id":"mule_told_truth","if_flags":{"all":["told_truth"]},"target":{"event":"family_notice"},
  "effect":{"type":"add_interrupt","interrupt":{"at":"m3","from":"回憶","text":"你想起小學那次窗戶破掉，你舉手承認了。很難，但你做到過一次。"}},
  "note":"童年 honesty 事件選了舉手承認；家人追問時多一個「說實話」的提醒（不改數值，選擇仍由玩家決定）"})
# ================= v4.6：合併模擬平衡（每個結局 2%–40%） =================
# 均勻抽樣下 REFUSE 約 2/3。調整：
# 1) job_check「查不到登記」不再直接結束，而是記下疑點（checked_company）繼續聽工作內容
# 2) job_offer 的直接拒絕只在「查過公司」時出現（兩個疑點疊起來才拒絕）；沒查的人要靠朋友提醒
# 3) arrest「堅稱只是打工」家人也被牽連而疏遠：人際 -15（CUT_OFF 需 人際≤15）
EV={e["id"]:e for e in data["events"]}
c=EV["job_check"]["choices"][0]
c.update({"text":"把「查不到登記」記下來，先聽聽工作內容再決定","effects":{"警覺":15},"next":"job_offer",
          "flags":{"set":["checked_company"],"require":[]},"grid":"green"})
c=EV["job_offer"]["choices"][0]
c["text"]="公司查不到登記，現在又要金融卡和密碼——正常工作不會這樣；拒絕"
c["flags"]["require"]=["checked_company"]
EV["arrest"]["choices"][1]["effects"]["人際"]=-15
data["ending_rules"]["evaluation"]+="（v4.6：job_check 不再直接拒絕；job_offer 拒絕需 checked_company）"
# 4) friend_warn 新增「半信半疑，只給帳號不給密碼」：真實案例常見的自我說服，結果帳戶一樣被拿去收贓款
EV["friend_warn"]["choices"].append({"text":"半信半疑：只給帳號、不給密碼應該沒關係吧","effects":{"存款":3000,"人際":-5},
  "next":"account_used","flags":{"set":["gave_account","paid_for_account","missed_card_request","ignored_friend"],"require":[]},"grid":"yellow"})
# v4.9：v0.9b 隨機初始人際＋提早結束後重調，「堅稱只是打工」人際 -15 → -20（設計假設）
EV["arrest"]["choices"][1]["effects"]["人際"]=-20
import outcomes; outcomes.apply(data,'mule')
finalize_v42(data)
from common import ensure_help; ensure_help(data,mental={"END_CONVICTED","END_RECORD","END_CUT_OFF","END_ACCOUNT"},legal={"END_CONVICTED","END_RECORD","END_CUT_OFF","END_ACCOUNT"})
data["cross_line_modifiers"].append({"id":"mule_v_salary_card","if_flags":{'all': ['mv_salary_card']},"target":{"event":"job_offer"},"effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"system","text":"（對方補充：先把薪資卡用超商寄件寄過來「開通」，下週就能領薪。）"}},"note":"t29u job_card_delivery → 入口變體 v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"mule_v_delivery_code","if_flags":{'all': ['mv_delivery_code']},"target":{"event":"job_offer"},"effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"system","text":"（對方傳來一組寄件代碼：「到超商印單，把金融卡寄過來就能完成認證、申請補助。」）"}},"note":"t29u delivery_code → 入口變體 v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"mule_v_kiosk","if_flags":{'all': ['mv_kiosk']},"target":{"event":"job_offer"},"effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"system","text":"（對方給你一組代碼，要你到超商機台列印，再把存摺和密碼一起寄過去領補助。）"}},"note":"t29u 超商機台代碼 → 入口變體 v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"mule_v_loan","if_flags":{'all': ['mv_loan_beautify']},"target":{"event":"job_offer"},"effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"system","text":"（對方改口說也能幫你辦貸款，只要先寄金融卡和存摺「美化帳戶」。）"}},"note":"t29u loan_beautify → 入口變體 v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"mule_v_sim","if_flags":{'all': ['mv_sim']},"target":{"event":"job_offer"},"effect":{"type":"add_interrupt","interrupt":{"at":"m2","from":"system","text":"（對方又說，把手機SIM卡寄過來就能開通優惠方案。）"}},"note":"t29u sim_card → 入口變體 v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"mule_fake_permission","if_flags":{'all': ['fake_permission']},"target":{"event":"account_used"},"effect":{"type":"add_interrupt","interrupt":{"at":"m1","from":"system","text":"（你想起以前同學說「老師說可以帶小抄」的事。）"}},"note":"t43u teacher_permission → 主管說可以 v1.2（寫手提供，待查證）"})
data["cross_line_modifiers"].append({"id":"mule_core_flag","if_flags":{'all': ['mv_delivery_code']},"target":{"event":"friend_warn"},"effect":{"type":"add_interrupt","interrupt":{"at":"m3","from":"system","text":"（給代碼叫你寄卡的，幾乎都是陷阱。）"}},"note":"t29u 核心破綻：給代碼叫你寄 v1.2（寫手提供，待查證）"})
from common import mark_standalone; mark_standalone(data,{'mule_lent': '合併模式（人生線中途插入）下，這個 flag 在本線進場年齡範圍內還不可能拿到（lent_money_lost 24歲才設定，車手線 18–22歲進場），所以只在單獨遊玩本線（standalone，人生線 flag 由前一局整段人生帶入）時生效；保留給單線模式。combined.py 會檢查：確實觸發不了才可標 standalone_only。', 'mule_lent_stat': '合併模式（人生線中途插入）下，這個 flag 在本線進場年齡範圍內還不可能拿到（lent_money_lost 24歲才設定，車手線 18–22歲進場），所以只在單獨遊玩本線（standalone，人生線 flag 由前一局整段人生帶入）時生效；保留給單線模式。combined.py 會檢查：確實觸發不了才可標 standalone_only。', 'mule_pressure_signer': '合併模式（人生線中途插入）下，這個 flag 在本線進場年齡範圍內還不可能拿到（pressure_signer 26歲才設定，車手線 18–22歲進場），所以只在單獨遊玩本線（standalone，人生線 flag 由前一局整段人生帶入）時生效；保留給單線模式。combined.py 會檢查：確實觸發不了才可標 standalone_only。', 'mule_family_pass': '合併模式（人生線中途插入）下，這個 flag 在本線進場年齡範圍內還不可能拿到（family_passphrase 35歲才設定，車手線 18–22歲進場），所以只在單獨遊玩本線（standalone，人生線 flag 由前一局整段人生帶入）時生效；保留給單線模式。combined.py 會檢查：確實觸發不了才可標 standalone_only。'})
from common import apply_mental_wear; apply_mental_wear(data)
from common import set_title; set_title(data)  # v6
json.dump(data,open("script-mule.json","w"),ensure_ascii=False,indent=2)
