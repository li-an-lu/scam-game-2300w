"""v8 新增／改寫的內容（資料）。數值皆為 0–100 內部值、10 的倍數。
不刪 Leo 原文：改寫的欄位都把舊值留在 *_v7 欄位。"""
G, Y, R = "green", "yellow", "red"
def C(text, outcome, eff, flags, grid, mood, nxt=None, **kw):
    d = {"text": text, "outcome_text": outcome, "effects": eff, "flags": {"set": flags, "require": kw.pop("require", [])},
         "grid": grid, "mood_line": mood, "log_text": kw.pop("log", text)}
    if nxt: d["next"] = nxt
    if grid == G: d["rethink"] = False
    d.update(kw); return d

# ── 需求 4＋6：關鍵詐騙事件 4 選項＋mood_line。"keep" 代表保留 Leo 原選項（依原文字比對），只補 mood_line／改標籤
KEY = {
 "c_stranger_pickup": [
   ("keep", "問她通關密語", {"mood_line": "你握緊書包帶，心還在跳，但你知道自己做對了。"}),
   ("keep", "跟她走到路口", {"mood_line": "那天晚上你一直想起那個路口，睡不太著。"}),
   C("問她媽媽叫什麼", "她馬上說出媽媽的名字。你愣了一下，正要跟她走，導師從後面叫住你。後來才知道，名字很容易從別人那裡聽來。",
     {"警覺": 10, "心理": -10}, ["kid_trusts_adult"], Y, "原來知道名字，不代表認識你。", "pool_c_lost_kid"),
   C("回校門口找老師", "你跑回校門口抓住導師的手。導師打電話給媽媽，媽媽說她沒有叫任何人來。",
     {"警覺": 10}, ["kid_family_code"], G, "老師的手很暖，你覺得安全了。", "pool_c_lost_kid"),
 ],
 "c_online_friend": [
   ("keep", "先跟爸媽說", {"mood_line": "說出來以後，胸口那顆石頭放下了。"}),
   ("keep", "傳學校名字就好", {"mood_line": "你有點後悔，但也有點慶幸自己說了。"}),
   C("先要他的照片", "他很快傳來一張笑得很開心的照片。過幾天你在別的網站看到同一張照片，名字不一樣。",
     {"警覺": 10, "心理": -10}, ["kid_trusts_adult"], Y, "你盯著那張照片，第一次懷疑螢幕另一頭是誰。", "lend_reveal"),
   C("約他語音聊天", "電話接通，對方的聲音比你想的低很多。他要你別跟家人說。你嚇得掛掉，跑去找媽媽。",
     {"警覺": 10, "心理": -10}, ["kid_trusts_adult", "kid_online_voice"], R, "你把平板反蓋在桌上，好久不想打開。", "lend_reveal"),
 ],
 "free_gift": [
   ("keep", "傳驗證碼", {"mood_line": "那個笑臉讓你心裡毛毛的。"}),
   ("keep", "不傳", {"mood_line": "你有點可惜那個造型，但不後悔。"}),
   C("先問他是誰", "他說自己是社團管理員，還傳了後台截圖。你覺得看起來很真，就把驗證碼傳過去了。隔天你的帳號登不進去。",
     {"心理": -10}, ["gave_otp", "missed_otp_share"], R, "你一直刷新登入畫面，手心冒汗。", "pool_c_link_drink"),
   C("截圖問其他社員", "你把訊息截圖貼到社團問。好幾個人回：「他也私訊我了，是假的。」",
     {"警覺": 10, "人際": 10}, ["checks_first"], G, "原來不只你遇到，你鬆了一口氣。", "pool_c_link_drink"),
 ],
 "part_time_ad": [
   ("keep", "先問家人", {"mood_line": "被提醒的感覺有點糗，但很踏實。"}),
   ("keep", "直接轉帳", {"mood_line": "你一直盯著手機，等那份教材。"}),
   C("先付一半試試", "對方說：「一半也可以，先幫你保留名額。」你轉了150元，之後他說要補齊才能開始。",
     {"存款": -150, "心理": -10}, ["paid_job_fee"], Y, "你告訴自己才150元，可是心裡不太舒服。", "ad_result"),
   C("要求見面簽約", "你說想先看合約、到公司簽。對方說「都線上作業」，再問就不回了。",
     {"警覺": 10}, ["checks_first"], G, "你把貼文滑掉，覺得自己長大了一點。", "ad_result"),
 ],
 "loan_use": [
   ("keep", "自己規劃用途", {"mood_line": "錢放在該放的地方，你睡得很安穩。"}),
   ("keep", "聽對方建議", {"mood_line": "你每天打開帳戶，數字一天比一天陌生。"}),
   C("先投一小筆看看", "第一週真的多了幾百元。你又加了一些。第二個月，對方說要先繳「解鎖費」才能領出來。",
     {"存款": -15000, "心理": -10}, ["loan_invest", "lost_money"], R, "那幾百元的獲利，現在想起來像誘餌。", "rent"),
   C("查他的證照和公司", "你照他給的名字去主管機關網站查，查不到這個人。你封鎖了帳號。",
     {"警覺": 10}, ["checks_first"], G, "多花十分鐘查，你覺得很值得。", "rent"),
 ],
 "rent_deposit": [
   ("keep", "先匯訂金", {"mood_line": "你一邊等房東回覆，一邊開始想像新房間。"}),
   ("keep", "堅持先看房", {"mood_line": "你知道好房子會被搶，但你更不想被騙。"}),
   C("先匯一半保留", "房東說一半也行。匯完後他說還有別人要看，要你補齊。你再傳訊息，已經讀不到了。",
     {"存款": -5000, "心理": -10}, ["rent_scammed", "lost_money"], Y, "你看著已讀不回的對話框，手有點冷。", "rent_result"),
   C("請朋友代看房", "住附近的朋友幫你去敲門，開門的住戶說：「這間沒有要出租啊。」",
     {"警覺": 10, "人際": 10}, ["checks_first", "helped_by_friend"], G, "有朋友在，找房子沒那麼孤單。", "mlm"),
 ],
 "mlm": [
   ("keep", "先問清楚公司", {"mood_line": "朋友少了一個，但你不後悔問。"}),
   ("keep", "直接去現場聊", {"mood_line": "那袋產品堆在牆角，你每天經過都不太敢看。"}),
   C("帶朋友一起去", "現場很熱鬧，大家都在分享成功故事。你們兩個都買了入門組，回家後才覺得哪裡不對。",
     {"存款": -8000, "人際": 10, "心理": -10}, ["mlm_small_buy", "missed_vague_job_offer"], Y, "有人陪著，反而更不好意思拒絕。", "a_first_salary"),
   C("先查公司登記", "你查了公司登記，營業項目跟他說的完全不一樣。你回他：「我先不去了。」",
     {"警覺": 10}, ["wary_of_easy_money"], G, "你關掉網頁，覺得自己有底氣。", "a_first_salary"),
 ],
 "customs_fee": [
   ("keep", "到超商寄出", {"mood_line": "寄出那一刻你鬆了口氣，後來才知道那是錯覺。"}),
   ("keep", "掛斷，自己查", {"mood_line": "電話安靜了，你的心也慢慢安靜下來。"}),
   C("問對方員工編號", "對方很流利地報了一串編號，還說可以查。你沒有查，照著寄了。",
     {"存款": -20000, "心理": -10}, ["customs_scammed", "lost_money"], R, "那串編號聽起來好正式，正式到你沒有懷疑。", "customs_result"),
   C("回撥來電號碼", "你回撥，接電話的人說他是「主管」，口氣很急。你越聽越不對，先掛了。",
     {"警覺": 10, "心理": -10}, ["called_back_scammer"], Y, "你發現回撥找到的，還是同一群人。", "insurance"),
 ],
 "second_scam": [
   ("keep", "打165確認", {"text": "找官方管道確認", "mood_line": "原來想把錢找回來的心，也會被利用。"}),
   ("keep", "滑掉訊息", {"mood_line": "莫名其妙的訊息，滑掉就好。"}),
   ("keep", "先付一筆試試", {"mood_line": "又一次。你坐在床邊，很久沒有動。"}),
   C("加入受害者群組", "群組裡很多人說自己拿回了錢，管理員要大家先繳「律師費」。你繳了，之後群組被解散。",
     {"存款": -20000, "心理": -10}, ["second_victim"], R, "你以為找到同伴，結果是另一個陷阱。", "pool_fake_insurance", require=["lost_money"]),
   C("請他先追回再付", "對方傳來一張「追回進度」截圖，說只差最後一筆保證金。你付了。",
     {"存款": -10000, "心理": -10}, ["second_victim"], Y, "那張截圖做得很像真的，你不知道該怪誰。", "pool_fake_insurance", require=["lost_money"]),
 ],
 "fake_insurance": [
   ("keep", "打給原保險公司", {"mood_line": "一通電話，就把那個數字變回了泡沫。"}),
   ("keep", "先付手續費", {"mood_line": "那筆解約金一直沒來，帳單倒是來了。"}),
   C("請他寄文件來看", "他寄來的文件有章有編號，看起來很正式。你付了手續費。",
     {"存款": -20000, "心理": -10}, ["insurance_fee", "lost_money"], R, "你把文件收進抽屜，再也不想打開。", "route_sleep"),
   C("問懂保險的家人", "姊姊看了一眼說：「解約金不會要你先付錢。」你把電話設成封鎖。",
     {"警覺": 10, "人際": 10}, ["checks_first"], G, "家人一句話，比對方十句話都可靠。", "route_sleep"),
 ],
 "gold_delivery": [
   ("keep", "寄出黃金", {"mood_line": "首飾盒空了，你不敢讓家人知道。"}),
   ("keep", "先見面或查證", {"mood_line": "對方一推託，你反而清醒了。"}),
   C("先寄一小部分", "你只寄了一條手鍊。對方說「已經入金」，要你把剩下的也寄來。你再也聯絡不上他。",
     {"存款": -30000, "心理": -10}, ["gold_sent", "lost_money", "scam_money_lost"], R, "你摸著空了一半的盒子，覺得好丟臉。", "guess_who"),
   C("問銀行理專", "你拿著對話紀錄去銀行問。理專說：「投資不會要你用寄件寄黃金。」",
     {"警覺": 10}, ["checks_first"], G, "專業的人一句話，你就放下了。", "guess_who"),
 ],
 "guess_who": [
   ("keep", "打電話問本人", {"mood_line": "聽到本人的聲音，你笑了出來。"}),
   ("keep", "去銀行準備轉帳", {"mood_line": "被行員攔下來，你又羞又慶幸。"}),
   C("先回訊息問細節", "你問他是哪一班的，他答得出學校名字。你差點就轉了，想了想還是先打給本人。",
     {"警覺": 10, "心理": -10}, ["chatted_impostor"], Y, "他知道得太多了，你背脊發涼。", "fake_police"),
   C("在同學群組問", "你在同學群組問：「有人換號碼嗎？」好幾個人說也收到一樣的訊息。",
     {"警覺": 10, "人際": 10}, ["checks_first"], G, "大家一起笑那則訊息，你一點也不孤單。", "fake_police"),
 ],
 "fake_police": [
   ("keep", "掛斷，打165", {"text": "掛斷，自己打給警局", "outcome_text": "你自己查了警局電話打過去。值班員警說：警察不會用電話做筆錄，也不會監管你的帳戶。",
                           "mood_line": "掛掉電話，你的手還在抖，但你沒有被帶走。"}),
   ("keep", "配合並保密", {"mood_line": "保密兩個字，讓你一個人扛了好久。"}),
   C("要求看他的證件", "對方傳來一張有照片、有警徽的證件圖，還有一份「公文」。你照著指示轉了錢。",
     {"存款": -60000, "心理": -10}, ["lost_money", "scam_money_lost"], R, "那張證件圖做得太像了，你到現在還會夢到。", "LIFE_ROUTER"),
   C("先跟家人商量", "對方說「不能告訴任何人」。你還是傳訊息給家人。家人回：「先掛掉，我們一起打給警局。」",
     {"警覺": 10, "人際": 10}, ["told_family_police"], G, "說出來的那一刻，你不再是一個人。", "LIFE_ROUTER"),
 ],
}
# Leo 原文裡出現在結果文字的專線號碼 → 改成一般說法（原文保留在 outcome_text_v7）
OUTCOME_FIX = {
 ("second_scam", "打165確認"): "你找到官方的反詐騙網站核對。上面寫得很清楚：說能幫你追回被騙的錢、還要先收費的，本身就是詐騙。你封鎖了對方。",
}

# ── 需求 2：固定劇情 3 版本（v1＝Leo 原文，不寫 text 就沿用）
VERSIONS = {
 "part_time": [
   {"id": "v1"},
   {"id": "v2", "text": "高二暑假，你在市場旁的早餐店打工，清晨五點半就要開始煎蛋餅。兩個月過去，老闆說「生意不好」，最後一個月的薪水一拖再拖。同時，社群上有個「資料登打」打工，說要先給帳戶當薪轉戶。"},
   {"id": "v3", "text": "高二暑假，你在補習班當櫃檯工讀，每天幫忙點名、印考卷。暑假結束，主任說最後一個月的工讀金「要等下一期學費收齊」。同時，有人私訊你一個「影片審核」打工，說要先給帳戶當薪轉戶。"},
 ],
 "student_loan": [
   {"id": "v1"},
   {"id": "v2", "text": "上大學了。你留在家裡附近的學校，每天騎車通勤四十分鐘。註冊單上的學費數字很大，你把單子摺起來塞進書包，不太想讓爸媽看到。"},
   {"id": "v3", "text": "上大學了。你和高中好友考上同一所學校，兩個人一起搬進宿舍。註冊那天，你們排在長長的隊伍裡，互相看了對方的學費單，都沉默了。"},
 ],
 "rent": [
   {"id": "v1"},
   {"id": "v2", "text": "大三搬出宿舍，你和同學分租一層老公寓，客廳的沙發是前房客留下的。房東說：「押金兩個月，退租看狀況。」一年後退租時，房東說地板刮傷，押金要扣一大半。"},
   {"id": "v3", "text": "大三搬出宿舍，你租了學校附近頂樓加蓋的雅房，夏天熱得睡不著。房東說：「押金兩個月，退租看狀況。」一年後退租時，房東說門鎖壞了要換，押金要扣一大半。"},
 ],
 "a_move_out": [
   {"id": "v1"},
   {"id": "v2", "text": "畢業前搬家。你把書和衣服分成八個箱子，有一半是捨不得丟的筆記。新住處離捷運站有點遠，但樓下有一間很晚才關的麵店。"},
   {"id": "v3", "text": "畢業前搬家。你只有一個行李箱和兩袋棉被，第一次發現自己的東西這麼少。新房間沒有窗戶，但房東說可以養植物。"},
 ],
 "a_first_salary": [
   {"id": "v1"},
   {"id": "v2", "text": "第一份正職的薪水入帳了。你在午休時偷偷打開帳戶看了三次，扣掉勞健保比你想的少，但那是你自己賺的。"},
   {"id": "v3", "text": "第一份正職的薪水入帳了。下班後你站在便利商店門口，傳了一張帳戶截圖給家裡的群組，又馬上收回。"},
 ],
}

# ── 需求 5：加害者線（被拉進來的人）。只放已查證的法條／判決；沒有操作細節
SRC = {
 "law22": {"name": "洗錢防制法§22 無正當理由提供帳戶", "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=G0380131&flno=22", "verified": True},
 "law3394": {"name": "刑法§339-4 加重詐欺", "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=C0000001&flno=339-4", "verified": True},
 "civil185": {"name": "民法§185 共同侵權", "url": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=185", "verified": True},
 "ltn18": {"name": "自由時報：18歲兼職變車手，法官認定新聞常報屬常識，判4月", "url": "https://news.ltn.com.tw/news/society/breakingnews/3969039", "verified": True},
 "sldm": {"name": "臺灣士林地方法院112年度金訴緝字第17號刑事判決（去識別化引用）", "url": "https://judgment.judicial.gov.tw/FJUD/data.aspx?ty=JD&id=SLDM%2c112%2c%e9%87%91%e8%a8%b4%e7%b7%9d%2c17%2c20230619%2c1", "verified": True},
 "ltnuni": {"name": "自由時報：大學生當車手交保再犯，宣告刑合計逾7年、民事判賠200萬", "url": "https://news.ltn.com.tw/news/Taichung/breakingnews/4677183", "verified": True},
}
PERP_EVENTS = [
 {"id": "perp_account_ask", "age": 21, "category": "加害者線", "line": "perpetrator", "presentation": "card",
  "text": "系上學長在群組私訊你：「我朋友公司在做點數代收，缺帳戶周轉。借一個月就好，給你五千，什麼都不用做。」\n你最近房租快繳不出來。",
  "sources": [SRC["law22"]],
  "choices": [
   C("直接拒絕", "你回：「帳戶不外借。」學長說你想太多，之後在群組不太理你。", {"警覺": 10, "人際": -10}, ["refused_account"], G,
     "被冷落有點難受，但你的名字還是你自己的。", "pool_rent_deposit"),
   C("問清楚是哪家公司", "你問公司名字和合約。學長說「朋友的公司，不方便講」，又說「大家都這樣借」。你沒有答應。",
     {"警覺": 10}, ["checks_first", "refused_account"], G, "問不到答案，本身就是答案。", "pool_rent_deposit"),
   C("借一個月就好", "你想：只是借，又不是我去騙人。你把提款卡交給學長，收到了五千元。",
     {"存款": 5000, "心理": -10}, ["perp_account_lent", "account_lost"], R, "五千元在帳上，你卻一直覺得哪裡不對。", "perp_consequence"),
   C("先問會不會有事", "學長說：「放心啦，出事我負責。」你相信了，把提款卡交出去，收了錢。",
     {"存款": 5000, "心理": -10}, ["perp_account_lent", "account_lost", "perp_trusted_promise"], R, "「我負責」三個字，後來誰也負責不了。", "perp_consequence"),
  ]},
 {"id": "perp_consequence", "age": 21, "category": "加害者線", "line": "perpetrator", "presentation": "card",
  "text": "兩週後，你的帳戶被銀行凍結，接著收到警察局的到案通知。你的帳戶被拿去收被害人的錢。\n你心裡一直重複：「我也是被騙的。」可是被害人的錢，是從你的帳戶經過的。\n（法律說明：無正當理由把帳戶交給別人，依洗錢防制法第22條會被警察告誡；收了報酬、交出三個以上帳戶，或告誡後五年內再犯，可處三年以下有期徒刑、拘役或罰金。若被認定參與詐騙，刑法第339條之4加重詐欺可處一年以上七年以下有期徒刑。被害人也可能依民法要求連帶賠償。實際結果由法院依個案判斷。）",
  "sources": [SRC["law22"], SRC["law3394"], SRC["civil185"], SRC["ltn18"], SRC["sldm"]],
  "case_note": "真實判決（去識別化）：曾有 18 歲兼職者把工作做成車手，法官認為詐騙新聞常見、應有認知，判刑 4 月（自由時報）；士林地院 112 年度金訴緝字第17號判決，車手數罪合併應執行有期徒刑 2 年 10 月。",
  "choices": [
   C("主動到案說實話", "你帶著和學長的對話紀錄去警局，把經過一五一十說出來。員警說之後會依程序處理，結果要看司法判斷。",
     {"警覺": 10, "心理": -10}, ["perp_cooperated"], G, "說完以後很累，但你不用再假裝了。", "pool_rent_deposit"),
   C("先跟家人說", "你在電話裡哭著說完。爸媽沉默了很久，然後說：「我們陪你去，先找法律協助。」",
     {"人際": 10, "心理": -10}, ["perp_cooperated", "told_family_perp"], G, "家人沒有放開你的手。", "pool_rent_deposit"),
   C("去找學長問清楚", "學長的帳號已經刪了，群組裡沒人說得出他去哪了。你一個人坐在宿舍，到案通知還在桌上。",
     {"心理": -10}, ["perp_alone"], Y, "你發現，「我負責」的人消失得最快。", "pool_rent_deposit"),
   C("刪掉對話紀錄", "你把對話全刪了，想當作沒發生。到了警局，你拿不出任何能說明經過的東西。",
     {"心理": -20}, ["perp_hid_evidence"], R, "刪掉的是證據，留下來的是你一個人。", "pool_rent_deposit"),
  ]},
]
PERP_INSERT_AFTER = "a_move_out"   # a_move_out 的選項 next 改指向 perp_account_ask（原本 → pool_rent_deposit）

PERP_ENDING = {
 "id": "END_ACCOUNT_LENT", "force": True, "name": "我只是借了帳戶",
 "text": "很多人以為，只要自己沒有打電話騙人，就跟詐騙無關。\n你把帳戶交出去的那天，只想著房租。後來的到案通知、凍結的帳戶、被害人的名字，都是你沒想過的事。",
 "case": "案例對照（已查證、去識別化）：18 歲兼職者把工作做成車手，法官認定詐騙新聞常見，判刑 4 月（自由時報）。法條：洗錢防制法§22（無正當理由提供帳戶，原則告誡；收受對價或三個以上帳戶可處三年以下有期徒刑）。",
 "missed": ["「借帳戶就有錢拿」本身就不合理", "對方不肯說公司名稱", "「出事我負責」沒有任何保障"],
 "review": "有人說「只是借一下」的時候", "help": "165 反詐騙專線", "source_note": "已查證：law.moj.gov.tw 洗錢防制法§22；自由時報 3969039",
 "base": 6, "boost": {"perp_account_lent": 30}, "requires": ["perp_account_lent"], "pool": "heavy", "review_flags": ["perp_account_lent"],
 "sources": [SRC["law22"], SRC["ltn18"]],
}

# ── 需求 8：結局卡的固定句改成通用句（原文留在 text_v7）
ENDING_FIRSTLINE = {
 "END_TRUST_LONG": "那些提醒你都聽過，只是那時候，它聽起來跟你無關。",
 "END_GROUP_PROFIT": "當身邊每個人都在做同一件事，停下來會讓人很不安。",
 "END_AUTHORITY_CALL": "聽到「警察」兩個字，很多人的第一個反應是照做。",
 "END_JOB_FEE": "想快點證明自己的時候，很容易接受不合理的條件。",
 "END_ROMANCE_BORROW": "越是珍惜的人開口，越難說「等一下」。",
 "END_INVEST_SMALL": "怕錯過的感覺，常常比怕損失更大聲。",
}
# ── 需求 7：讓固定事件的旗標影響結局（只加 boost，不改 requires）
ENDING_BOOST = {
 "END_TRUST_LONG": {"kid_trusts_adult": 10, "kid_online_voice": 8},
 "END_ALMOST": {"kid_family_code": 10, "kid_told_parent": 8, "told_truth": 8, "told_family_police": 10},
 "END_HELPED_OTHERS": {"counted_change": 8, "checks_first": 6, "refused_account": 8},
 "END_JOB_FEE": {"wage_unpaid": 10, "paid_job_fee": 12, "missed_payroll_account_ask": 10},
 "END_CUSTOMER_SERVICE": {"gave_otp": 12},
 "END_INVEST_SMALL": {"mlm_joined": 10, "loan_invest": 10},
 "END_GROUP_PROFIT": {"mlm_small_buy": 10},
 "END_LOAN_FIRST": {"cash_strapped": 8},
 "END_AUTHORITY_CALL": {"called_back_scammer": 8},
 "END_FAMILY_IMPERSONATE": {"chatted_impostor": 10},
 "END_QUIET": {"first_salary_saved": 6},
}

# ── 需求 3：再想一下（引擎讀 meta.rethink）
RETHINK = {"stats": {"警覺": 60, "人際": 70}, "probability": 0.6,
           "text": "要不要再想一下？", "back": "再想一下", "go": "就這樣決定",
           "friend": {"stat": "人際", "gte": 70, "text": "朋友剛好傳訊息來：「欸，這個聽起來怪怪的，要不要先問一下？」", "back": "先問問看", "go": "沒事啦"},
           "note": "警覺≥6（內部60）或人際≥7（內部70）時，對沒標 rethink:false 的選項有 60% 機率跳出。friend 為人際高時的朋友版本（需引擎支援，見 HANDOFF-v8.md）。"}
MOOD_LINES = [
 {"stat": "心理", "max": 20, "text": ["你覺得好累，只想先躺下來。", "你很久沒有好好睡一覺了。"]},
 {"stat": "心理", "max": 50, "text": ["你深呼吸了一下，繼續往前走。", "心裡有點重，但日子還在過。"]},
 {"max": 100, "text": ["你覺得自己撐得住。", "今天的你，還算平穩。"]},
]

# ── 需求 1：年份填空（ui.js 會依年齡篩選）
YEAR_FILLER = [
 {"text": "學會自己走路，跌倒很多次。", "min_age": 1, "max_age": 2},
 {"text": "每天在家裡跑來跑去。", "min_age": 1, "max_age": 4},
 {"text": "第一次上幼兒園，哭了一整個早上。", "min_age": 3, "max_age": 4},
 {"text": "平凡地過了一年。", "min_age": 1, "max_age": 99},
 {"text": "家裡養了一隻貓。", "min_age": 1, "max_age": 99},
 {"text": "颱風假在家看卡通。", "min_age": 3, "max_age": 12},
 {"text": "學會騎腳踏車。", "min_age": 5, "max_age": 10},
 {"text": "每天寫作業寫到很晚。", "min_age": 7, "max_age": 17},
 {"text": "颱風假在家追劇。", "min_age": 13, "max_age": 99},
 {"text": "換了一支新手機。", "min_age": 13, "max_age": 99},
 {"text": "讀書、打工、和朋友吃宵夜。", "min_age": 16, "max_age": 24},
 {"text": "第一次自己出國旅行。", "min_age": 18, "max_age": 99},
 {"text": "被長輩催著找穩定工作。", "min_age": 22, "max_age": 35},
 {"text": "過年回家被問薪水。", "min_age": 23, "max_age": 45},
 {"text": "手機裡的群組越來越多。", "min_age": 13, "max_age": 99},
]

# 文字提到「別人」的事、不是主角本人在做（年齡關鍵字豁免，需寫理由）
AGE_KEYWORD_OK = {"c_uncle_story": "舅舅講自己年輕時打工的故事，主角 9 歲只是聽"}

# ── v8.1（Leo 決定）：非結局文字不出現專線號碼；選項只寫動作
SIS = ("把對話給姐姐看", {"outcome_text": "姐姐看完，握著你的手說：「我們一起打電話去問清楚。」查證的人聽完說，這是很典型的手法。"})
HOTLINE_FIX = {
 ("investment", "date_refuse_video"): [("封鎖，撥165查詢", {"text": "封鎖，打電話查證", "outcome_text": "你封鎖了對方，打電話去反詐騙單位問了一下，對方說這是很常見的手法。"})],
 ("investment", "bank_counter"): [("跟行員說實情", {"outcome_text": "你把情況告訴行員。行員請你坐下，幫你打電話找警方查證，這筆錢沒有交出去。但前面已經投入的錢，大多拿不回來了。"})],
 ("mule", "teen"): [("認真聽，記下165", {"text": "認真聽，抄下重點", "outcome_text": "你在筆記本角落寫下：「接到怪電話，先掛斷，自己打電話查證。」"})],
 ("mule", "job_offer"): [("拒絕", {"outcome_text": "你拒絕了，封鎖對方並把對話截圖向警方通報。錢還是很緊，但帳戶是乾淨的。"})],
 ("shopping", "ticket_blocked"): [("留紀錄，打165報案", {"text": "留紀錄，去報案", "outcome_text": "你把對話和匯款紀錄整理好去報案，員警幫你做了筆錄。"})],
 ("shopping", "cs_call"): [("掛斷，打165", {"text": "掛斷，自己打去查證", "outcome_text": "你掛斷電話，自己打給反詐騙單位查證。對方說這是常見的假客服手法：「你剛剛差一點。」你沒有損失。"})],
 ("romance", "rm_ask_invest"): [SIS], ("romance", "rm_ask_loan"): [SIS], ("romance", "rm_ask_sick"): [SIS],
 ("romance", "rm_push"): [("打 165 問問看", {"text": "打電話查證", "outcome_text": "查證的人聽完說：不見面、只談錢，這是交友詐騙最常見的樣子。你掛上電話，哭了一下。"})],
}
# hongbao 補第 4 選項（似是而非：聽起來在「理財」）＋全部選項 mood_line
HONGBAO_MOOD = {"交給媽媽": "有點捨不得，但覺得安心。", "請爸媽陪我去開戶": "存摺上有自己的名字，好驕傲。",
                "留一點買遊戲點數": "開心是真的，錢也真的花掉了。"}
HONGBAO_4TH = {"text": "交給說會讓錢變多的表哥", "effects": {"人際": 10, "存款": -3000}, "next": "pool_c_temple_fair",
  "flags": {"set": ["hongbao_cousin"], "require": []}, "grid": "red",
  "outcome_text": "表哥說他「懂理財」，過完年就還你兩倍。後來每次問，他都說「再等一下」。那疊紅包再也沒回來。",
  "log_text": "紅包交給說會翻倍的表哥", "mood_line": "他是家人，應該不會騙我吧……"}
