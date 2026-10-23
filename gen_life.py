"""人生日常線：不是詐騙線，而是讓玩家在詐騙線前累積數值與 flag。每個事件都取材自真實分享或新聞。"""
import json
from common import finalize,HL,COUNTY_SRC,COUNTY_DASH
def s(name,url,how,ok=True): return {"name":name,"url":url,"verified":ok,"verify_note":how}
CU="2026-10-23 curl 開啟原文比對"; SR="原站擋自動連線，依 WebSearch 搜尋摘錄核對"
# 紅包（正面）
HB_POS=[s("PTT Gossiping〈媽媽幫你存起來是真的〉：媽媽過世後整理遺產，才知道每月交給她的錢都真的存著","https://www.pttweb.cc/bbs/Gossiping/M.1582284292.A.8D1",CU),
 s("PTT C_Chat 2026-03-01 討論串：推文「成年就拿到存摺印章提款卡」「跟老媽對分，我那一半存進戶頭」","https://www.ptt.cc/bbs/C_Chat/M.1772379094.A.2BA.html",CU),
 s("TVBS（Dcard 心情板轉述）：一直以為紅包被拿去家用，長大後媽媽交給她近20萬的存摺","https://news.tvbs.com.tw/life/2390629",CU),
 s("三立（Dcard 心情板轉述）：〈我媽把從小到大保管的紅包都給我了〉","https://www.setn.com/News.aspx?NewsID=1246155",CU),
 s("ETtoday：媽媽幫你存起來！他突收「從小到大所有紅包」","https://www.ettoday.net/news/20230201/2431672.htm",CU)]
# 紅包（反面）
HB_NEG=[s("三立（PTT 轉述，2018）：媽媽說幫忙存，長大後「始終音訊全無」；推文「養你不用錢嗎」","https://www.setn.com/News.aspx?NewsID=351665",CU),
 s("三立（PTT 轉述，2020）：紅包被收走，「搞不好拿去買股票賠光」，可以告父母侵占嗎？","https://www.setn.com/News.aspx?NewsID=782179",CU),
 s("PTT C_Chat 2026-03-01 討論串：推文「我們家領走不敢跟我講」「紅包是互包的」","https://www.ptt.cc/bbs/C_Chat/M.1772379094.A.2BA.html",CU),
 s("喆律法律事務所：「爸媽幫你存起來」的法律問題（民法1087、1088條）","https://zhelu.tw/post/legal-issue-of-red-envelope",CU)]
PHONE=[s("ETtoday：10歲兒子用媽媽手機玩手遊，偷刷近30萬；點數已使用就難退款","https://www.ettoday.net/news/20210108/1894368.htm",CU)]
GAME=[s("巴哈姆特新楓之谷板：8591 買到與描述不符的裝備，賣家要付費才取消（stories #32）","https://forum.gamer.com.tw/C.php?bsn=7650&snA=1029867",CU),
 s("數位發展部：網友說家裡斷生活費，請他代買1萬點數，店員攔下（stories #60）","https://ipfs.moda.gov.tw/ADI/antifraud/af-third-case/19422.html",CU)]
WAGE=[s("Dcard 工作板：勞資調解心路歷程（文長）","https://www.dcard.tw/f/job/p/225265409",SR),
 s("Dcard 工作板：勞資調解經歷分享","https://www.dcard.tw/f/job/p/259725066",SR)]
JOB=[s("TVBS：17歲高中生IG應徵「字幕專員」，交出帳戶並轉匯款項，被送辦（stories #61）","https://news.tvbs.com.tw/local/2169821",CU)]
LOAN=[s("TVBS：畢業時學貸43萬，兩年還掉近20萬的心得","https://news.tvbs.com.tw/life/1708074",CU),
 s("Dcard 理財板：就學貸款討論","https://www.dcard.tw/f/money/p/229189985",SR)]
RENT=[s("TVBS：退租驗收已過，房東仍以重新粉刷為由，19,200元押金只退8,700元","https://news.tvbs.com.tw/life/2646011",CU),
 s("Dcard 租屋板：租屋請慎選，否則押金拿不回來","https://www.dcard.tw/f/rent/p/256130275",SR),
 s("中央社：臉書租屋廣告要先付約2萬才能看屋（stories #35）","https://www.cna.com.tw/news/asoc/202406290176.aspx","2026-10-23 WebFetch 開啟原文比對")]
MLM=[s("Dcard 閒聊板：好朋友拉我直銷","https://www.dcard.tw/f/talk/p/258656458",SR),
 s("Dcard 心情板：十年好友開始做直銷","https://www.dcard.tw/f/mood/p/254119573",SR)]
LEND=[s("Dcard 閒聊板：本來以為是兄弟，結果借錢不還","https://www.dcard.tw/f/talk/p/258243311",SR),
 s("Dcard 心情板：借錢一直拖著不還的朋友","https://www.dcard.tw/f/mood/p/258579026",SR)]
INS=[s("Dcard 理財板：為何我不買儲蓄險","https://www.dcard.tw/f/money/p/245663877",SR),
 s("金管會金融智慧網：保險宣導（契約撤銷期）","https://moneywise.fsc.gov.tw/home.jsp?dataserno=33&id=4&mcustomize=publicizeinfo_view.jsp&parentpath=0","WebSearch 摘錄；10天撤銷期細節待核實",False)]
ROSCA=[s("PTT WomenTalk：請問現在還有人在跟會、標會嗎？","https://www.ptt.cc/bbs/WomenTalk/M.1607100523.A.029.html",CU),
 s("自由時報：被倒會可成立自救會求償","https://news.ltn.com.tw/news/society/paper/1318152",SR)]
ELDER=[s("內政部：LINE名稱與兒子相同的新帳號借39萬（stories #40）","https://www.moi.gov.tw/News_Content.aspx?n=4&s=330123",CU),
 s("TVBS：AI仿聲「女兒」語音要20萬，老翁打給女兒才識破（stories #39）","https://news.tvbs.com.tw/local/2999037",CU),
 s("Dcard 反詐騙板：媽媽疑似遇到詐騙","https://www.dcard.tw/f/anti_fraud/p/256911121",SR)]
def C(t,e,n,set_flags=None,req=None): return {"text":t,"effects":e,"next":n,"flags":{"set":set_flags or [],"require":req or []}}
E=[]
def ev(i,a,cat,t,c,src,**k): E.append({"id":i,"age":a,"category":cat,"text":t,"choices":c,"sources":src,**k})
R="LIFE_ROUTER"
# ===== 童年 0–18 歲（v0.4）：「當下不知道」的事件，之後由 reveal 事件揭曉 =====
CE="共同經驗：找不到單一來源，附上討論串"
def ce(name,url,how=CU): return s(name+"（"+CE+"）",url,how)
SHOT=[s("妞新聞：黃瑽寧醫師「別告訴孩子不會痛」","https://www.niusnews.com/=P1rbval1",CU),
 s("PChome 個人新聞台：診所裡的小男孩大吼「妳騙人啦！打針明明就很痛！」","https://mypaper.pchome.com.tw/littlesuntaipei/post/1324600677",CU)]
PROMISE=[s("華視：父母承諾「考上公立就去迪士尼」後食言，原PO說「大人人前說的跟事後做的不一樣」","https://news.cts.com.tw/cts/life/202307/202307202205175.html",CU),
 s("Dcard 閒聊板：考全校前5就買電腦，結局超心寒","https://www.dcard.tw/f/talk/p/235130284",SR)]
GATE=[ce("PTT Childhood〈學校旁文具店老闆的煉金術，你被坑多少〉：小雞、染色小雞、蠶寶寶","https://www.pttweb.cc/bbs/Childhood/M.1703615356.A.A75"),
 s("PTT NHU_Talk：國小有人來擺攤賣套書，「買一套送小鳥」，小鳥後來死了","https://www.pttapp.cc/bbs/NHU_Talk/M.1301074112.A.61A.html",CU)]
CARD=[s("ETtoday：小一兒拿7張七龍珠卡換「限量寶可夢卡」，結果是一張商品吊牌","https://www.ettoday.net/news/20221025/2365423.htm",CU),
 s("未來親子：國小老師談「校園地下交易」","https://futureparenting.cwgv.com.tw/family/content/index/18810",CU)]
LOTTO=[ce("PTT Childhood〈以前文具店有種抽籤集字換玩具〉：推文「永遠缺一個字」「大概是很多小朋友第一次被詐騙的東東」","https://www.pttweb.cc/bbs/Childhood/M.1693736306.A.FC8"),
 ce("PTT C_Chat 2026-04-26〈小時候玩過抽抽樂嗎〉：「黑暗大法，就是沒有師」","https://www.pttweb.cc/bbs/C_Chat/M.1777180881.A.664","依 WebSearch 摘錄核對"),
 s("民視：YouTuber 實測柑仔店抽抽樂，花800元只換回250元，「童年充滿了謊言」","https://www.ftvnews.com.tw/news/detail/2021A07W0350",CU)]
LEND5=[s("PTT StupidClown〈[童年] 所以是欠多少錢〉：借100元只還50元，理由是「只花了50」","https://www.pttweb.cc/bbs/StupidClown/M.1418036788.A.1DF",CU),
 s("Disp BBS ott 板〈[眼殘] 學弟，可以借我5塊錢嗎?〉（內文待核實）","https://disp.cc/b/ott/87Yu","2026-10-23 curl 只確認標題，內文待核實")]
PE=[ce("PTT Gossiping：體育課走到操場集合，又被班長叫回教室拿數學課本，老師說「走那麼遠，有運動到了」","https://www.pttweb.cc/bbs/Gossiping/M.1627768020.A.7B7"),
 s("民視：國中音樂、體育課被借去上考科，監委申請自動調查（民間調查逾8成學生有被借課經驗）","https://www.ftvnews.com.tw/news/detail/2020A12W0053",CU)]
HONEST=[s("Disp BBS（PTT StupidClown 轉）〈[童年] 誠信的重要〉：誠實說「沒辦法保證」，被罰半蹲兩次","https://disp.cc/b/Stupid/9Bjz",CU),
 s("未來親子：乖孩子受的傷最重","https://futureparenting.cwgv.com.tw/family/content/index/5947","2026-10-23 curl 確認標題")]
SLURPEE=[s("ETtoday（Dcard 轉述）：國小「100分換思樂冰」，98分當場哭，下次考到100分如願換到","https://www.ettoday.net/news/20230526/2507013.htm",CU)]
GIFT=[s("TVBS：手遊FB社團說要「贈禮」，孩子傳了驗證碼，媽媽遭小額盜刷","https://news.tvbs.com.tw/life/1950036",CU),
 s("防詐雷達：遊戲點數詐騙","https://fraud.tw/guide/gaming-points","2026-10-23 curl 確認標題")]
QUIZ=[ce("PTT PT-97〈驚天動地普化小考〉","https://www.ptt.cc/bbs/PT-97/M.1222946647.A.310.html","依 WebSearch 摘錄核對"),
 ce("Dcard 輔大板〈教授的嘴騙人的鬼〉：說「一定考」結果沒考","https://www.dcard.tw/f/fju/p/239107778/b/7",SR)]
ev("shot",4,"長輩的善意謊言","打預防針。媽媽說：「不痛，像蚊子叮一下。」護理師阿姨已經拿起針了。",
 [C("相信媽媽，勇敢伸出手（然後哭得整條走廊都聽到）",{"心理":-3,"人際":3},"promise_park",["trusts_adults"]),
  C("問護理師阿姨：「真的不痛嗎？」",{"警覺":3},"promise_park",["checks_first"])],SHOT)
ev("promise_park",5,"長輩的善意謊言","爸爸說：「把青菜吃完，週末就帶你去公園玩。」",
 [C("三口吞完青菜，開始倒數週末",{"心理":3},"school_gate",["park_promise"]),
  C("伸出小指：「打勾勾，蓋印章，星期六早上喔！」",{"警覺":2},"school_gate",["park_pinky"])],PROMISE)
ev("school_gate",6,"校門口","放學時，校門口有人在賣毛茸茸的染色小雞。一隻二十塊，旁邊圍了一圈小朋友。",
 [C("拿早餐錢買一隻粉紅色的",{"存款":-20,"心理":5},"park_reveal",[]),
  C("先回家問媽媽",{"警覺":3},"park_reveal",["checks_first"])],GATE)
ev("park_reveal",7,"揭曉","（兩年前的那個週末）",
 [C("「下次啦，爸爸今天好累。」下次、下下次……公園一直在「下次」",{"心理":-5,"警覺":3},"card_trade",[],["park_promise"]),
  C("星期六早上，爸爸真的拿著球在門口等你。原來打勾勾有用",{"心理":5,"人際":5},"card_trade",[],["park_pinky"])],PROMISE)
ev("card_trade",7,"同學","同學拿出一張亮晶晶的「超限量卡」，說只要用你7張卡來換。",
 [C("換！7張換1張超限量，賺翻了",{"人際":3},"hongbao",["traded_card"]),
  C("說「我先拿給哥哥看一下」",{"警覺":3,"人際":-2},"hongbao",["checks_first"])],CARD)
ev("lottery",9,"校門口","文具店的抽抽樂，5塊一抽，集滿「黑暗大法師」就能換怪獸對打機。你已經有「黑暗大法」了。",
 [C("再抽一次就好……再一次……",{"存款":-300,"心理":-3},"lend5",["chased_lottery","missed_rigged_odds"]),
  C("站在旁邊看同學抽，自己的錢留著買雞蛋糕",{"心理":2},"lend5",[])],LOTTO)
ev("lend5",9,"同學","隔壁同學說：「借我5塊買棒棒冰，明天一定還你！」",
 [C("借他",{"存款":-5,"人際":3},"card_reveal",["lent_5"]),
  C("說「我也只剩5塊」",{},"card_reveal",[])],LEND5)
ev("card_reveal",10,"揭曉","你拿出那張「超限量卡」想給新同學看……",
 [C("他看了三秒：「這是便當袋上的吊牌吧？」你的7張卡再也回不來了",{"心理":-5,"警覺":5},"pe_class",["card_scammed"],["traded_card"]),
  C("你的7張卡都還在，哥哥說那張「限量卡」其實是吊牌",{"警覺":3},"pe_class",[],["!traded_card"])],CARD)
ev("pe_class",10,"老師的文字遊戲","體育課！全班衝到操場集合。班長跑來：「老師叫大家回教室，帶數學課本。」",
 [C("舉手問：「那體育課什麼時候還？」",{"警覺":3,"人際":-2},"honesty",["checks_first"]),
  C("默默拿出數學課本。老師說：「走那麼遠，有運動到了。」",{"心理":-3},"honesty",[])],PE)
ev("honesty",11,"老師的文字遊戲","教室的窗戶破了。老師說：「是誰？說實話就不罰你。」其實是你踢的球。",
 [C("舉手承認",{"心理":-3,"人際":5},"slurpee",["told_truth"]),
  C("低頭不說話，看別人會不會被冤枉",{"心理":-5,"人際":-3},"slurpee",[])],HONEST)
ev("slurpee",11,"兌現的約定","附近便利商店說：段考考100分，可以拿考卷換一杯冰沙。",
 [C("拚了！第一次考98分，當場哭出來；下一次終於100，換到了",{"心理":8},"lend_reveal",[]),
  C("覺得一定是騙人的，沒去換",{"警覺":2,"心理":-2},"lend_reveal",[])],SLURPEE)
ev("lend_reveal",12,"揭曉","（三年前那5塊錢）",
 [C("畢業典禮那天，他塞給你5塊錢和一包乖乖：「欠很久了。」",{"人際":8,"心理":5},"first_phone",["trust_repaid"],["lent_5"]),
  C("你有點羨慕：有人畢業時還記得還同學5塊錢",{},"first_phone",[],["!lent_5"])],LEND5)
ev("free_gift",13,"網友","遊戲社團有人說「免費送限定造型」，只要把手機收到的驗證碼傳給他。",
 [C("傳了，等了一天，造型沒來，好像也沒怎樣",{"人際":2},"game_trade",["gave_otp","missed_otp_share"]),
  C("驗證碼是給自己用的，不傳",{"警覺":5},"game_trade",["checks_first"])],GIFT)
ev("quiz",15,"老師的文字遊戲","老師說：「明天只是小考，不用緊張。」",
 [C("信了，只看了一點點。隔天發下來三張滿滿的A4",{"心理":-5,"警覺":3},"otp_reveal",[]),
  C("問：「小考是考哪幾課？幾張？」老師笑了：「一到三課，三張。」",{"警覺":3},"otp_reveal",["checks_first"])],QUIZ)
ev("otp_reveal",15,"揭曉","（兩年前那串驗證碼）",
 [C("媽媽拿著電話帳單問：「這幾筆小額付款是什麼？」你這才知道那串數字不是送禮用的",{"人際":-5,"心理":-5,"警覺":8},"lottery_reveal",["otp_scammed"],["gave_otp"]),
  C("新聞說有孩子傳驗證碼，媽媽被小額盜刷。你想起那天沒傳",{"警覺":2},"lottery_reveal",[],["!gave_otp"])],GIFT)
ev("lottery_reveal",16,"揭曉","你看到網紅把一整盒抽抽樂抽完：花了800塊，換回250。",
 [C("原來那個「師」根本沒有要給你。你算了一下：當年那些錢可以買好多雞蛋糕",{"警覺":8},"part_time",["learned_odds"],["chased_lottery"]),
  C("還好當年在旁邊看就好",{"心理":2},"part_time",[],["!chased_lottery"])],LOTTO)
ev("birth",0,"人生","你出生在{county}的{family}家庭。",[C("長大",{},"shot")],[COUNTY_SRC,COUNTY_DASH])
ev("hongbao",8,"家庭與金錢","過年了，你收到一疊紅包。媽媽笑著說：「媽媽幫你存起來。」",
 [C("交給媽媽",{"人際":5},"lottery",["gave_hongbao"]),
  C("請爸媽陪你去郵局，用自己的名字開戶存進去",{"警覺":5},"lottery",["own_account"]),
  C("留一點自己花，買了遊戲點數",{"心理":5,"存款":-2000},"lottery",["spent_hongbao"])],HB_POS+HB_NEG)
ev("first_phone",12,"家庭與金錢","你有了第一支手機。手遊裡的限定角色只要「綁一下爸媽的卡」就能抽。",
 [C("跟爸媽約好使用規則，不綁卡",{"警覺":5,"人際":5},"free_gift",["phone_contract"]),
  C("偷偷用爸媽的卡抽卡，月底帳單嚇壞一家人",{"人際":-10,"心理":-5},"free_gift",["game_spender"])],PHONE)
ev("game_trade",14,"網路交易","有人在遊戲裡私訊你：「交易平台手續費好貴，我們私下交易比較便宜。」另一個網友則說家裡斷了生活費，請你幫忙買點數。",
 [C("只在平台內交易，也不幫人買點數",{"警覺":8},"quiz",["platform_only"]),
  C("私下交易，對方傳來一張匯款截圖，你就把寶物交出去了",{"存款":-3000,"心理":-5},"quiz",["game_scammed","missed_fake_receipt"])],GAME)
ev("part_time",17,"工作","暑假打工做了兩個月，老闆一直拖著不發最後一個月的薪水。同時，社群上有個「字幕專員」的打工說要先給帳戶當薪轉戶。",
 [C("保留打卡和聊天紀錄，到勞工局申請調解；社群上那份工作不碰",{"警覺":8,"心理":-5,"存款":15000},"hongbao_result",["evidence_habit","wary_of_easy_money"]),
  C("算了不想吵；看到社群上那份工作很輕鬆，有點心動但沒去",{"心理":-10},"hongbao_result",["wage_unpaid","missed_payroll_account_ask"])],WAGE+JOB)
ev("hongbao_result",18,"家庭與金錢","你滿18歲了。你想起小時候的紅包……",
 [C("（結果A）媽媽拿出一本存摺，裡面是從小到大的紅包錢，一筆都沒少",{"存款":80000,"人際":10,"心理":10},"student_loan",["hongbao_returned"],["gave_hongbao"]),
  C("（結果B）你問起紅包，爸媽說「早就拿去包回別人家、繳學費了，養你不用錢嗎？」",{"心理":-10,"人際":-10},"student_loan",["hongbao_lost"],["gave_hongbao"]),
  C("你打開自己名字的存摺，或想起早就花掉的那些點數",{},"student_loan",[],["!gave_hongbao"])],HB_POS+HB_NEG,
 random=True,random_weights={"hongbao_returned":0.5,"hongbao_lost":0.5},design_assumption=True,
 random_note="設計設定，非統計，前台不顯示為統計。結果A／B由引擎各以50%隨機抽選。")
ev("student_loan",19,"家庭與金錢","上大學了，學費很貴。",
 [C("申請學貸，列好畢業後的還款計畫",{"存款":-20000,"警覺":5},"rent",["student_loan"]),
  C("不貸款，每天打工撐學費，睡眠不足",{"心理":-10,"存款":10000},"rent",["cash_strapped"])],LOAN)
ev("rent",20,"租屋","找到一間便宜套房。退租時，房東說牆要重新粉刷，押金要扣一大半。",
 [C("入住和退租時都拍照錄影、簽點交單，拿回押金",{"警覺":8},"mlm",["evidence_habit"]),
  C("沒留紀錄，只能吞下去",{"存款":-10500,"心理":-5},"mlm",["deposit_lost","missed_no_checkin_photos"])],RENT)
ev("mlm",22,"人際邀約","很久沒聯絡的朋友說要「介紹一份很好的工作」，但不肯說公司名稱，只約你去現場聊。",
 [C("先問清楚公司、職務、要不要買產品，對方支吾其詞就拒絕",{"警覺":10,"人際":-5},"lend",["wary_of_easy_money"]),
  C("去了才知道是直銷，被勸買了一套入門產品",{"存款":-30000,"人際":5},"lend",["mlm_joined","missed_vague_job_offer"])],MLM)
ev("lend",24,"借錢","好朋友說急用，跟你借三萬，「下個月一定還」。",
 [C("借了，但用訊息寫清楚金額和還款日",{"存款":-30000,"人際":5},"insurance",["lent_with_record"]),
  C("借了，沒留任何紀錄。半年後對方已讀不回",{"存款":-30000,"人際":-10,"心理":-10},"insurance",["lent_money_lost"]),
  ],LEND)
ev("insurance",26,"人際邀約","親戚當上保險業務，拿來一份「穩賺的」儲蓄險，要你當場簽。",
 [C("拿條款回家比較，確認需求再說",{"警覺":8,"人際":-5},"rosca",["compares_before_sign"]),
  C("礙於人情當場簽了，後來繳不起想解約，賠了一筆",{"存款":-20000,"人際":5},"rosca",["pressure_signer","missed_sign_on_spot"])],INS)
ev("rosca",30,"家庭與金錢","媽媽邀你一起跟會，會頭是認識多年的鄰居。",
 [C("不跟會，錢放在自己能掌握的地方",{"警覺":5,"人際":-5},"elder",[]),
  C("跟了。兩年後會頭失聯，倒會",{"存款":-60000,"心理":-10},"elder",["rosca_lost"])],ROSCA)
ev("elder",35,"長輩","爸媽收到「兒子換新號碼」的訊息，說急需周轉。",
 [C("你早就跟爸媽約好家庭通關密語，他們打給你確認後識破",{"人際":10,"警覺":5},R,["family_passphrase"]),
  C("爸媽差點匯款，是行員攔下來的。你們一家人都嚇壞了",{"心理":-10},R,["elder_near_miss"])],ELDER)
ev(R,40,"人生","回頭看這五十年……（引擎依 ending_rules 自動判定，不顯示選項）",[C("回顧",{},"__EVAL__")],HL,router=True)
def card(t,src): return {"summary":t,"url":src["url"],"note":"去識別化改寫，細節以原文為準"}
EN=[
 {"id":"END_LIFE_STRETCHED","priority":1,"conditions":{"any_of":[{"flags_all":["savings_depleted"]},{"flags_all":["lent_money_lost","rosca_lost"],"flags_none":["has_support"]}]},
  "text":"借出去的錢沒回來，跟會又倒了。你的生活一直很緊，遇到「快速賺錢」的機會時，很難不心動。",
  "reason_texts":[{"flag":"savings_depleted","text":"存款歸零了。"},{"flag":"lent_money_lost","text":"借給朋友的錢沒有紀錄，要不回來。"},{"flag":"rosca_lost","text":"會頭失聯，倒會了。"},{"flag":"isolated","text":"兩筆錢都沒了，身邊也沒人能拉你一把。"}],
  "case_card":card("一位網友說，借錢給很要好的朋友，對方之後一再拖延，最後連訊息都不回。",LEND[0]),
  "missed_red_flags":["借錢沒有留下任何紀錄","把錢交給自己無法掌握的跟會"],"sources":LEND+ROSCA+HL},
 {"id":"END_LIFE_HONGBAO_GONE","priority":2,"conditions":{"flags_all":["hongbao_lost"]},
  "text":"那些紅包終究沒有回來。你不怪爸媽，但從那時起，你學會把錢放在自己名下。",
  "reason_texts":[{"flag":"evidence_habit","text":"你養成了留紀錄的習慣。"}],
  "case_card":card("一位網友說，小時候紅包都交給媽媽「幫忙存」，長大後卻音訊全無，問起時得到的是「養你不用錢嗎？」",HB_NEG[0]),
  "missed_red_flags":["沒有用自己名字開的帳戶","沒有約定什麼時候還給你"],"sources":HB_NEG+HL},
 {"id":"END_LIFE_HONGBAO_SAVED","priority":3,"conditions":{"flags_all":["hongbao_returned"]},
  "text":"18歲那天的存摺，讓你第一次知道爸媽為你守了多少。你也開始幫自己存錢。",
  "reason_texts":[{"flag":"family_passphrase","text":"你和家人有通關密語，詐騙更難得逞。"}],
  "case_card":card("一位網友一直以為紅包被拿去貼補家用，長大後媽媽交給她一本近20萬的存摺，讓她百感交集。",HB_POS[2]),
  "missed_red_flags":["你沒有錯過：家人把錢存在你名下"],"sources":HB_POS+HL},
 {"id":"END_LIFE_STEADY","priority":4,"conditions":{"flags_none":["hongbao_lost","hongbao_returned"]},
  "text":"你很早就有自己的帳戶，跌跌撞撞，但每次都多學到一點。",
  "reason_texts":[{"flag":"evidence_habit","text":"你習慣留證據，遇到糾紛時保護了自己。"},{"flag":"wary_of_easy_money","text":"你對「輕鬆賺錢」特別警覺。"}],
  "case_card":card("討論串中有網友說，紅包跟媽媽對分，自己那一半存進自己的戶頭。",HB_POS[1]),
  "missed_red_flags":["你抓到了：要你帳戶的打工、不肯說公司名稱的工作邀約"],"sources":HB_POS[1:2]+HL}]
data={"meta":{"title":"80億分之1：人生日常線","version":"0.4","language":"zh-TW","one_life":True,
 "content_policy":"只描述生活中看到、經歷到的事，不寫任何詐騙或犯罪操作手法",
 "cross_line_flags":{
  "wary_of_easy_money":"建議：投資線、車手線中「高報酬／輕鬆打工」選項的警覺門檻降低（較容易識破）",
  "evidence_habit":"建議：被騙後的「報案」選項更容易成功（有保留紀錄）",
  "family_passphrase":"建議：假親友、AI 仿聲事件可直接識破",
  "lent_money_lost":"建議：心理-、人際-；之後「朋友借錢」事件更容易觸發",
  "cash_strapped":"建議：求職車手線「急需用錢」事件更容易觸發",
  "game_scammed":"建議：假網拍線的警覺初始值+5（學過一次教訓）",
  "mlm_joined":"建議：投資群組事件更容易觸發（人脈被當名單）",
  "checks_first":"從小習慣確認（童年任一「先問／先確認」選項）。建議：各線第一個可疑訊息自動顯示查證提示",
  "trusts_adults":"容易相信大人。建議：假檢警、假客服等權威型話術的警覺判定較難",
  "learned_odds":"看過抽抽樂真相。投資線 small_win（先讓你小賺）多一則回憶提醒＋警覺+5（inv_learned_odds）",
  "card_scammed":"小時候換卡換到吊牌。假網拍線 ticket（只看截圖的私下交易）多一則回憶提醒＋警覺+3（shop_card_scammed）",
  "told_truth":"小學打破窗戶時舉手承認。車手線 family_notice（家人追問）多一則「說實話」回憶提醒，不改數值（mule_told_truth）",
  "otp_scammed":"小時候傳過驗證碼。建議：假網拍線的驗證碼／連結題警覺+5",
  "trust_repaid":"信任被回報過。假網拍線 aftermath（被騙之後）人際+5，比較願意開口找朋友（shop_trust_repaid）",
  "pressure_signer":"建議：「當場決定」類的假客服、假檢警事件更容易得逞",
  "_note":"這裡列的每個 flag 都至少被一條詐騙線的 cross_line_modifiers 讀取（validate.py 會檢查被引用的 flag 都定義在這裡）。各 flag 的說明以實際套用的 modifier 為準。童年 flag 的處理（接線、刪除、只在人生線內部使用）見 meta.childhood_flag_decisions。"}},
 "ending_rules":{"evaluation":"依 priority 由小到大檢查，第一個成立者為結局","fallback":"END_LIFE_STEADY",
  "condition_grammar":{"flags_all":"全部都要有","flags_any":"至少一個","flags_none":"都不能有","any_of":"子條件任一成立"}},
 "stats":[],"stats_sources":[],
 "player_init":{"stats":{"存款":{"min":0,"init_range":[80000,200000]},"警覺":{"min":0,"max":100,"init_range":[15,45]},
   "人際":{"min":0,"max":100,"init_range":[30,70]},"心理":{"min":0,"max":100,"init_range":[40,80]}},
  "county_pool":["臺北市","新北市","桃園市","臺中市","臺南市","高雄市","新竹市","新竹縣","基隆市","苗栗縣","彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣","金門縣","連江縣"],
  "family_pool":[{"name":"小康","存款_mod":0},{"name":"單親","存款_mod":-0.3,"心理":-5},{"name":"務農","人際":5},{"name":"經商","存款_mod":0.5}],
  "start_event":"birth","flags":[]},
 "events":E,"endings":EN}
RF={"missed_fake_receipt":"看到匯款截圖不等於錢真的入帳，要自己查帳戶。",
 "missed_payroll_account_ask":"正常打工不會一開始就要你的帳戶來「轉帳」。",
 "missed_no_checkin_photos":"入住和退租都沒拍照、沒簽點交單，押金爭議時就沒有證據。",
 "missed_vague_job_offer":"不肯說公司名稱、只約現場談的「好工作」。",
 "missed_sign_on_spot":"被要求「當場簽」，沒有時間比較條款。",
 "missed_rigged_odds":"「永遠缺一個字」：大獎的機率由賣的人決定。",
 "missed_otp_share":"驗證碼是給自己用的，任何「送禮」都不需要它。"}
finalize(data,RF)
# ================= v0.4：照詐騙線 v4 規範補欄位（只加欄位，不改判定邏輯） =================
from common import apply_v4,finalize_v42,M,SHARE_CARD,stat_null
CHAT={"app":"line_like","app_display_name":"聊聊 Chatto（虛構）","theme":"fictional_green_free"}
def P(app,disp,name,status,msgs): return {"presentation":"chat","chat":{"app":app,"app_display_name":disp,"theme":"neutral" if app=="in_person" else "fictional_green_free","contact":{"name":name,"avatar":"placeholder_silhouette","status":status},"messages":msgs}}
V4={
 "lottery":P("in_person","文具店門口","文具店老闆","面對面",[M("m1","contact","5塊一抽，集滿「黑暗大法師」換對打機喔！"),M("m2","contact","差一個字而已啦，再抽一次一定有！"),M("m3","player","（我已經有「黑暗大法」了……）")]),
 "free_gift":P("line_like","遊戲社團（虛構）","送禮的大大","在線上",[M("m1","contact","限定造型免費送，名額有限～"),M("m2","contact","你手機等一下會收到一串數字，傳給我我就幫你領"),M("m3","player","真的免費嗎？")]),
 "game_trade":P("line_like","遊戲私訊（虛構）","買家","在線上",[M("m1","contact","平台手續費好貴，我們私下交易比較便宜"),M("m2","contact","[圖片] 匯款完成截圖，你看，錢轉過去了"),M("m3","contact","快把寶物給我，我在趕時間")]),
 "part_time":{**P("line_like","聊聊 Chatto（虛構）","徵才小幫手","在線上",[M("m1","contact","在家打字幕，日領現金，很輕鬆"),M("m2","contact","先把你的帳戶給我們登記成薪轉戶就好"),M("m3","player","最後一個月的薪水，老闆還沒發……")])},
 "rent":P("in_person","套房門口","房東","面對面",[M("m1","contact","牆要重新粉刷，押金要扣一大半"),M("m2","contact","你說本來就有的痕跡？證據呢？"),M("m3","player","（我入住時好像沒拍照……）")]),
 "mlm":P("line_like","聊聊 Chatto（虛構）","很久沒聯絡的朋友","在線上",[M("m1","contact","好久不見！有一份很好的工作想介紹給你"),M("m2","contact","公司名稱見面再說啦，電話講不清楚"),M("m3","contact","週六下午來聽聽看就好")]),
 "insurance":P("in_person","親戚家客廳","當上保險業務的親戚","面對面",[M("m1","contact","這個儲蓄險穩賺的，我自己也買了"),M("m2","contact","今天簽最划算，下個月就沒這個條件了"),M("m3","contact","自己人，我還會騙你嗎？")]),
}
for e in E:
    if e.get("category")=="揭曉" or e["id"]=="hongbao_result": V4.setdefault(e["id"],{"presentation":"timeskip"})
ANCH={"missed_rigged_odds":[{"event":"lottery","message":"m2"}],"missed_otp_share":[{"event":"free_gift","message":"m2"}],
 "missed_fake_receipt":[{"event":"game_trade","message":"m2"}],"missed_payroll_account_ask":[{"event":"part_time","message":"m2"}],
 "missed_no_checkin_photos":[{"event":"rent","message":"m2"}],"missed_vague_job_offer":[{"event":"mlm","message":"m2"}],
 "missed_sign_on_spot":[{"event":"insurance","message":"m2"}]}
NULL=stat_null("165 儀表板的詐騙類型統計沒有這一類（家人保管紅包、借錢不還、倒會、日常生活壓力都不是受理分類），沒有對應的官方數字")
EV4={
 "END_LIFE_STRETCHED":{"title":"一直很緊的人","title_emoji":"🧾","grid_color":"red","real_world_stat":NULL,"share_text":"我的人生日常線：錢一直很緊。你呢？"},
 "END_LIFE_HONGBAO_GONE":{"title":"紅包沒回來的人","title_emoji":"🧧","grid_color":"yellow","real_world_stat":NULL,"share_text":"小時候的紅包，長大後沒有回來。"},
 "END_LIFE_HONGBAO_SAVED":{"title":"拿到存摺的人","title_emoji":"📒","grid_color":"green","real_world_stat":NULL,"share_text":"18歲那天，我拿到一本存摺。"},
 "END_LIFE_STEADY":{"title":"跌跌撞撞長大的人","title_emoji":"🌱","grid_color":"green","real_world_stat":NULL,"share_text":"跌跌撞撞，但每次都多學到一點。"}}
for k,v in EV4.items(): v.update({"rarity_key":"life_"+k,"share_card":SHARE_CARD})
META4={"presentation_notes":"同詐騙線：presentation='chat' 以全螢幕仿聊天室／面對面對話呈現，畫面一律使用虛構 app 名稱；'timeskip' 用於延後揭曉的事件（時間跳轉畫面）；其餘為 'card'。只呈現受騙過程與後果，不寫可照做的操作細節。",
 "no_pressure_mode":{"available":True,"default":False,"effect":"人生線沒有倒數；此設定與其他線一致，不影響劇情與結局","min_timer_s":20},
 "real_world_stat_notes":"人生線結局對應的都不是 165 受理的詐騙類型，real_world_stat.value_pct 一律為 null，display 為 null，前台不顯示統計列（v4.5 起不再顯示「官方無此分類」佔位字）；null_reason 只留在資料裡給製作者看。"}
apply_v4(data,V4,ANCH,EV4,META4)
ENX={x["id"]:x for x in data["endings"]}
ENX["END_LIFE_STRETCHED"].update({"text":"存款一路見底。你的生活一直很緊，遇到「快速賺錢」的機會時，很難不心動。","requires_flags":[],"forbids_flags":[],
 "text_variants":[{"when":{"label":"lent_and_rosca","flags_all":["lent_money_lost","rosca_lost"]},"requires_flags":["lent_money_lost","rosca_lost"],
   "text":"借出去的錢沒回來，跟會又倒了。你的生活一直很緊，遇到「快速賺錢」的機會時，很難不心動。"}]})
ENX["END_LIFE_HONGBAO_GONE"].update({"requires_flags":["hongbao_lost","gave_hongbao"],"forbids_flags":["hongbao_returned"]})
ENX["END_LIFE_HONGBAO_SAVED"].update({"requires_flags":["hongbao_returned","gave_hongbao"],"forbids_flags":["hongbao_lost"]})
ENX["END_LIFE_STEADY"].update({"requires_flags":[],"forbids_flags":["hongbao_lost","hongbao_returned","savings_depleted"]})
# ================= v0.5：詐騙線插入人生線（中途進入、結束後回到人生線） =================
MOI36={"name":"內政部統計處：115年第36週內政統計通報（115年1-6月詐欺案件；表2 嫌疑犯及被害人按年齡別）","url":"https://www.moi.gov.tw/News_Content.aspx?n=2905&s=340735&sms=10305","verified":True,
 "verify_note":"2026-10-23 依 WebSearch 摘錄核對全文與 PDF 表2：被害人 8萬2,004人，18-23歲 11,174人（13.6%）、24-29歲 11,413人（13.9%）、30-39歲 17,906人（21.8%）、40-49歲 17,566人（21.4%）；59歲以下被害人以假網路拍賣（購物）占比最高，60歲以上以投資詐欺最高"}
NPA10={"name":"警政署統計室：警政統計通報 114年第10週（113年9-12月青少年嫌疑犯前3大涉案類型）","url":"https://www.npa.gov.tw/ch/app/data/doc?detailNo=1363679580417691648&module=wg063&type=s","verified":True,
 "verify_note":"2026-10-23 依 WebSearch 摘錄核對：18-23歲嫌疑犯 15,936人，涉詐欺 6,945人（43.58%），其中擔任車手 3,866人；12-23歲擔任車手共 5,145人"}
FN_AGE={"name":"fromnineon 整理：各年齡層詐欺被害人主要被詐騙手法（警政統計通報 115年第38週表4，115年1-7月）","url":"https://fromnineon.com/data/taiwan-fraud-statistics/","verified":True,
 "verify_note":"2026-10-23 curl 開啟核對：假網拍占 18-23歲 37.27%、24-29歲 31.44%、30-39歲 27.16%；投資詐欺占 24-29歲 20.55%、30-39歲 23.42%、40-49歲 25.00%、65歲以上 32.14%。二手整理，原表為警政署 115年第38週通報（未直接開啟原 PDF）"}
DA="design_assumption"
SCAM_INTEGRATION={
 "version":"1.0",
 "summary":"一局＝一個人生。人生線照年齡往前走，走到指定事件之後，若符合觸發條件就插入一條詐騙線；詐騙線結束（走到它的 __EVAL__ 並判定結局）後，帶著數值與對應 flag 回到人生線原本的下一個事件。同一局可以經歷 0–3 條詐騙線。",
 "principles":[
  "不重新投胎：插入的詐騙線不使用自己的 player_init（init_range、family_pool、county_pool 全部忽略），直接沿用人生線當下的 4 項數值、年齡、縣市與家庭。",
  "跳過詐騙線自己的童年：從 entry_event 開始（birth／teen 等童年事件不播），人生線已經演過童年。",
  "flag 單向流入：進入時把人生線目前所有 flag 交給詐騙線，cross_line_modifiers 依這些 flag 套用（含 __INIT__ 的 stats_delta，在進入當下套用）。",
  "詐騙線內部 flag 不外流：結束後只把 return_map 列出的 flag 加回人生線；其餘內部 flag 只寫進 scam_history。",
  "stat_flags（savings_depleted／mental_collapse／isolated／has_support）是即時算的：每次判定結局前依當下數值重算，不跨線保存。",
  "數值原樣帶回：詐騙線內所有 effects 已經改動數值，回到人生線不再重複扣；return_map 的 stats_delta 預設為空，保留欄位供日後調整。"],
 "hook_semantics":"在 after_event 做完選擇、套用 effects 之後、前往該選擇的 next 之前檢查 trigger；成立就進入詐騙線，詐騙線結束後前往原本的 next（validator 檢查 after_event 的每個選擇都指向 return_to）。不成立就照常前往 next。",
 "age_rules":{"entry_age":"等於 after_event 的 age 加 entry_offset_years（只能 ≥0）",
  "exit_age":"entry_age 加 duration（預設 default_years；rules 依詐騙線內部 flag 由上而下取第一個成立者）",
  "monotonic":"整局的年齡序列（人生事件 age、各詐騙線 entry_age／exit_age）必須不遞減；exit_age 不可超過 return_to 事件的 age",
  "age_lived":"最終結局顯示的年齡＝max(最後一個人生事件的 age, 最後一條詐騙線的 exit_age)。目前人生線停在 LIFE_ROUTER（40歲），所有 exit_age 都 ≤40，所以 age_lived 恆為 40"},
 "age_sources":[MOI36,NPA10,FN_AGE],
 "lines":[
  {"line":"mule","name":"求職車手線","script":"script-mule.json","after_event":"student_loan","entry_offset_years":0,"entry_age":19,
   "trigger":{"flags_all":["cash_strapped"]},"entry_event":"broke","return_to":"rent",
   "duration":{"default_years":0,"rules":[{"if_flags_any":["arrested"],"years":1,"note":"有被捕／審判的路徑，回到人生線時算過了一年"}]},
   "age_basis":{"status":"sourced_bracket+design_assumption",
     "sourced":"警政署 114年第10週：113年9-12月 18-23歲嫌疑犯涉詐欺 6,945人，其中擔任車手 3,866人，是這個年齡層最大宗的涉案類型。19歲落在 18-23歲區間。",
     "assumption":"具體選 19歲、接在 student_loan 之後，是設計決定：車手線開場 broke 事件的前提是「手頭很緊」，人生線裡 cash_strapped 只在 student_loan（19歲）設定。duration 1 年也是設計假設（實際偵審時間因案而異，劇情不寫具體時程）。",
     "source_names":[NPA10["name"]]},
   "trigger_rationale":"只有 cash_strapped（不貸款、靠打工撐學費）才進入：車手線的開場就是「急需用錢」，沒缺錢卻演這段會跟前提矛盾。"},
  {"line":"shopping","name":"假網拍線","script":"script-shopping.json","after_event":"insurance","entry_offset_years":1,"entry_age":27,
   "trigger":{},"entry_event":"ticket","return_to":"rosca",
   "duration":{"default_years":0,"rules":[]},
   "age_basis":{"status":"sourced_bracket+design_assumption",
     "sourced":"內政部 115年第36週：59歲以下各年齡層被害人都以假網路拍賣（購物）占比最高；fromnineon 整理的 115年1-7月表：24-29歲被害人中假網拍占 31.44%。27歲落在 24-29歲區間。",
     "assumption":"選 27歲（insurance 之後）而不是 18-23歲：放在 lend（24）、insurance（26）之後，lent_money_lost、pressure_signer 這兩個假網拍線會讀的 flag 才可能已經出現。這是設計決定。",
     "source_names":[MOI36["name"],FN_AGE["name"]]},
   "trigger_rationale":"每一局都會進入：假網拍是 59歲以下最常見的被騙手法，人人都可能遇到。"},
  {"line":"investment","name":"假投資線","script":"script-investment.json","after_event":"elder","entry_offset_years":2,"entry_age":37,
   "trigger":{},"entry_event":"work","return_to":"LIFE_ROUTER",
   "duration":{"default_years":0,"rules":[{"if_flags_any":["borrowed"],"years":1,"note":"借錢湊款、跟銀行周旋的路徑，算過了一年"}]},
   "age_basis":{"status":"sourced_bracket+design_assumption",
     "sourced":"內政部 115年第36週表2：30-39歲是被害人最多的年齡層（17,906人，21.8%）；fromnineon 整理：30-39歲被害人中投資詐欺占 23.42%，比 18-29歲高。37歲落在 30-39歲區間。",
     "assumption":"官方資料顯示投資詐欺占比最高的是 60歲以上，但人生線只演到 40歲，所以放在 37歲。這是設計決定，不代表投資詐欺最常發生在 37歲。",
     "source_names":[MOI36["name"],FN_AGE["name"]]},
   "trigger_rationale":"每一局都會進入（人生線最後一段）。"}],
 "return_map":{
  "_always":{"flags":["scam_seen_{line}"],"stats_delta":{},"note":"每條詐騙線結束都加 scam_seen_<line>，並把 {line, ending_id, title, grid_color, entry_age, exit_age, internal_flags} 推進 scam_history"},
  "_carry_internal":{"kept_evidence":"evidence_habit","reported":"evidence_habit","told_someone":"has_told_someone",
     "_note":"詐騙線內部 flag → 人生線 flag 的固定對照：有保留證據／報案過的人，之後的詐騙線也讀得到 evidence_habit"},
  "mule":{
   "END_CUT_OFF":{"flags":["criminal_record","wary_of_easy_money"]},
   "END_CONVICTED":{"flags":["criminal_record","wary_of_easy_money"]},
   "END_RECORD":{"flags":["criminal_record","wary_of_easy_money"]},
   "END_RESCUED":{"flags":["wary_of_easy_money"]},
   "END_STOPPED_ALONE":{"flags":["wary_of_easy_money"]},
   "END_ACCOUNT":{"flags":["wary_of_easy_money"]},
   "END_REFUSE":{"flags":["wary_of_easy_money"]}},
  "shopping":{
   "END_SILENT_COLLAPSE":{"flags":["scam_money_lost"]},
   "END_CS_DRAINED":{"flags":["scam_money_lost"]},
   "END_TICKET_LOST":{"flags":["scam_money_lost"]},
   "END_SMALL_FEE":{"flags":[]},
   "END_SAFE":{"flags":["checks_first"]}},
  "investment":{
   "END_COLLAPSE":{"flags":["scam_money_lost","scam_debt"]},
   "END_FAMILY_RIFT":{"flags":["scam_money_lost","scam_debt"]},
   "END_DEBT":{"flags":["scam_money_lost","scam_debt"]},
   "END_ALL_LOST":{"flags":["scam_money_lost","scam_debt"]},
   "END_BROKE":{"flags":["scam_money_lost"]},
   "END_SMALL_LOSS":{"flags":["wary_of_easy_money"]},
   "END_EARLY":{"flags":["wary_of_easy_money"]}}},
 "return_flag_notes":{"criminal_record":"車手線被判刑（CUT_OFF／CONVICTED／RECORD）。人生線結局 END_LIFE_RECORD 讀取",
  "scam_money_lost":"被騙走實質金額（假網拍大額、假投資）。END_LIFE_STRETCHED／END_LIFE_STEADY 的 scammed 變體讀取",
  "scam_debt":"為了被騙而借錢（假投資 borrowed）。只記錄，給分享卡與日後擴充",
  "has_told_someone":"被騙後有跟人說。只記錄",
  "scam_seen_{line}":"經歷過這條詐騙線"},
 "final_ending":{
  "evaluation":"回到 LIFE_ROUTER 後照人生線 ending_rules 判定（數值是經過所有詐騙線之後的數值；stat_flags 重算；return_map 加的 flag 都算在內）",
  "recap":{"show_if":"scam_history 非空","template":"{entry_age}歲｜{name}：{title_emoji} {title}","position":"結局本文之後、case_card 之前，依 entry_age 排序"},
  "life_grid":"每 5 歲一格；人生事件 choice.grid 與詐騙線結局 grid_color 都放進 entry_age 所在的格子，取最嚴重者（red>yellow>green）；最後一格用人生線結局 grid_color",
  "share_card":"人生線結局 share_card.fields 加 age_lived、scam_history（只顯示 title_emoji＋title，不顯示詐騙線細節，維持 spoiler_free）"}}
data["meta"]["scam_integration"]=SCAM_INTEGRATION
for k,v in SCAM_INTEGRATION["return_flag_notes"].items(): pass
data["meta"]["childhood_flag_decisions"]={
 "learned_odds":{"decision":"wired","modifier":"inv_learned_odds(+_stat)","rationale":"看過抽抽樂「永遠差一個字」，對「先讓你小賺」的投資平台多一層懷疑"},
 "card_scammed":{"decision":"wired","modifier":"shop_card_scammed(+_stat)","rationale":"童年換卡被吊牌騙，正好對應只看截圖就私下交易的情境"},
 "trust_repaid":{"decision":"wired","modifier":"shop_trust_repaid","rationale":"借出的錢被好好還過，代表玩家有「信任會被回報」的經驗；被騙後比較願意開口找朋友（人際+5），避免遊戲只教玩家什麼都不信"},
 "told_truth":{"decision":"wired","modifier":"mule_told_truth","rationale":"家人追問時多一則說實話的回憶；只加提示、不改數值，選擇仍由玩家決定"},
 "promise_broken":{"decision":"deleted","rationale":"公園約定是家長的善意謊言，接到詐騙線只會變成「不要相信家人」，和車手線／投資線「家人是保護力」的設計相反。效果（心理／警覺）保留，只拿掉 flag"},
 "promise_kept":{"decision":"deleted","rationale":"同上；思樂冰兌現是正面回憶，沒有對應的詐騙情境。效果保留，只拿掉 flag"},
 "bought_chick":{"decision":"deleted","rationale":"染色小雞是童年小額衝動消費，和三條詐騙線的情境都沒有合理關聯；效果保留，只拿掉 flag"},
 "lent_5":{"decision":"internal_only","rationale":"lend_reveal 用它判斷要不要演「5塊錢有沒有還」；結果已由 trust_repaid 帶到詐騙線，不另外接"},
 "gave_otp":{"decision":"internal_only","rationale":"otp_reveal 用它判斷要不要演揭曉；結果已由 otp_scammed 帶到假網拍線（shop_otp_link），不另外接"}}
# 人生線結局：反映詐騙經歷
JOBSRC={"name":"自由時報：18歲兼職變車手，法官認定新聞常報屬常識，判4月","url":"https://news.ltn.com.tw/news/society/breakingnews/3969039","verified":True,"verify_note":"依搜尋摘錄核對（直接連線回 403）；與車手線 END_RECORD 同一來源"}
data["endings"].append({"id":"END_LIFE_RECORD","priority":0.5,"conditions":{"flags_all":["criminal_record"]},
 "text":"年輕時那份「打工」，讓你留下了犯罪紀錄。後來的每一步，你都走得比別人更小心，也更辛苦。",
 "reason_texts":[{"flag":"criminal_record","text":"你在求職車手線被判刑。"},{"flag":"has_support","text":"身邊還有願意陪你的人。"}],
 "case_card":{"summary":"一名18歲學生在社群網站的兼職社團應徵，提供帳戶並轉交款項；法院認為反詐宣導已是一般常識，依洗錢防制法判4月，並須賠償被害人。","url":JOBSRC["url"],"note":"去識別化改寫，細節以原文為準"},
 "missed_red_flags":["「日領三千、免經驗」的打工","工作要你交出帳戶或代收款項"],"sources":[JOBSRC]+HL,
 "requires_flags":["criminal_record"],"forbids_flags":[],
 "title":"帶著紀錄長大的人","title_emoji":"📄","grid_color":"red","rarity_key":"life_END_LIFE_RECORD","combined_only":True,"combined_only_note":"只有經過車手線（scam_integration）才會拿到 criminal_record；單獨跑人生線到不了，可達性由 combined.py 檢查",
 "real_world_stat":stat_null("165 儀表板以被害人遭遇的手法分類，沒有「當車手留下紀錄的人」這種統計"),
 "share_text":"那份「輕鬆打工」，我付了很久的代價。","share_card":SHARE_CARD})
ENX=({x["id"]:x for x in data["endings"]})
ENX["END_LIFE_STRETCHED"]["text_variants"].insert(0,{"when":{"label":"scammed","flags_all":["scam_money_lost","savings_depleted"]},"requires_flags":["scam_money_lost","savings_depleted"],
 "text":"存款一路見底，其中有一大筆是被騙走的。你的生活一直很緊，但你也比以前更知道，哪些「機會」不能碰。"})
ENX["END_LIFE_STRETCHED"]["reason_texts"].append({"flag":"scam_money_lost","text":"你在詐騙線被騙走了錢。"})
ENX["END_LIFE_STEADY"].setdefault("text_variants",[]).insert(0,{"when":{"label":"scammed","flags_all":["scam_money_lost"]},"requires_flags":["scam_money_lost"],
 "text":"你很早就有自己的帳戶。中間也被騙過，跌跌撞撞，但每次都多學到一點。"})
for x in data["endings"]:
    x["share_card"]=dict(x["share_card"],fields=x["share_card"]["fields"]+["age_lived","scam_history"])
data["ending_rules"]["evaluation"]+="（v0.5：END_LIFE_RECORD 0.5 最先檢查）"
data["meta"]["version"]="0.5"
for f in ["criminal_record","scam_money_lost","scam_debt","has_told_someone"]: pass
# ================= v0.6：彈性插入點、機率進入、投資金額比例化、進場前心理小幅回復 =================
for _s in (MOI36,NPA10,FN_AGE): pass
FN_AGE["verified"]=False
FN_AGE["display"]=False
FN_AGE["verify_note"]=("二手整理（fromnineon），聲稱引用警政署 115年第38週警政統計通報表4（115年1-7月）；2026-10-23 只用 curl 開啟 fromnineon 頁面讀到數字，"
 "沒有開啟警政署原始通報或 PDF 核對，所以標 verified:false。display:false：前台不可把這些百分比當官方數字顯示，只供製作者決定插入年齡參考。")
SI=SCAM_INTEGRATION; SI["version"]="2.0"
SI["summary"]=("一局＝一個人生。人生線照年齡往前走；每條詐騙線各自抽一個進入年齡（基準年齡±隨機偏移），在人生線走到該年齡時，若觸發條件成立、"
 "再通過進入機率，就插入這條詐騙線，演完回到人生線的下一個事件。同一局可以經歷 0–3 條詐騙線。")
SI.pop("hook_semantics",None)
SI["insertion_rules"]={
 "roll":"開局時對每條線各抽一次：entry_age = base_age + randint(offset_min, offset_max)（整數、均勻）；並抽一次 U(0,1) 與 probability 比較。兩者都在開局抽好，之後不重抽",
 "slot":"人生線每做完一個事件 E（年齡 a_E）、要前往下一個事件 N（年齡 a_N；N 為 __EVAL__ 時 a_N 視為 LIFE_ROUTER 年齡）之前，找出所有 a_E ≤ entry_age < a_N 且尚未處理的線，依 entry_age 由小到大（同齡依 lines 陣列順序）逐一處理",
 "check":"處理時才檢查 trigger（用當下的 flags 與數值）；trigger 成立且機率抽中才進入。不成立就跳過，這局不會再進這條線（scam_history 不記）",
 "return":"詐騙線結束後回到 N（彈性回歸點：不是寫死的事件，而是插入位置的下一個人生事件）",
 "age_guarantee":"年齡都是整數，entry_age < a_N 且 duration ≤ 1，所以 exit_age ≤ a_N，年齡序列一定不遞減（combined.py 仍逐局檢查）",
 "end_bound":"entry_age 必須 < LIFE_ROUTER 年齡（40）；offset 範圍已設計成不會超過"}
SI["pre_entry"]={"mental_recovery":{"stat":"心理","delta":10,"design_assumption":True,
  "note":"進入詐騙線前心理 +10（上限 100）。代表人生事件之間的時間讓人稍微喘口氣；數值是設計假設，不是統計。目的：避免人生線前段的心理消耗讓詐騙線只剩「崩潰」結局"}}
SI["age_rules"]={"entry_age":"見 insertion_rules.roll","exit_age":"entry_age + duration（rules 依詐騙線內部 flag 由上而下取第一個成立者）",
 "monotonic":"整局年齡序列不遞減；exit_age ≤ 回歸事件年齡",
 "age_lived":"max(最後一個人生事件的 age, 最後一條詐騙線的 exit_age)；人生線停在 LIFE_ROUTER（40），所以目前恆為 40；分享卡顯示這個值"}
L={l["line"]:l for l in SI["lines"]}
for l in SI["lines"]:
    for k in ("after_event","entry_offset_years","entry_age","return_to"): l.pop(k,None)
L["mule"].update({"entry_window":{"base_age":20,"offset_min":-2,"offset_max":2,"range":[18,22]},"probability":0.6,
  "trigger":{"flags_any":["cash_strapped","wage_unpaid"]},
  "probability_note":"design_assumption：符合條件（缺錢）的人約六成會在這段時間遇到這種「打工」",
  "trigger_rationale":"車手線開場的前提是「急需用錢」：17歲打工被欠薪（wage_unpaid）或19歲靠打工撐學費（cash_strapped）任一成立。18歲進場時只可能是 wage_unpaid"})
L["mule"]["age_basis"]["assumption"]=("18–22歲落在警政署 18-23歲區間；具體範圍、機率 0.6、duration 都是設計假設")
L["shopping"].update({"entry_window":{"base_age":25,"offset_min":-3,"offset_max":3,"range":[22,28]},"probability":0.7,"trigger":{},
  "probability_note":"design_assumption：假網拍是 59歲以下最常見的被騙手法（內政部 115年第36週），所以機率設最高",
  "trigger_rationale":"沒有前提條件"})
L["shopping"]["age_basis"]["assumption"]=("22–28歲跨 18-23、24-29 兩個年齡層；具體範圍與機率 0.7 是設計假設。年齡×手法百分比（fromnineon）verified:false、display:false，只當製作參考")
L["investment"].update({"entry_window":{"base_age":37,"offset_min":-3,"offset_max":2,"range":[34,39]},"probability":0.6,
  "trigger":{"stats":{"存款":{"gt":0}}},
  "probability_note":"design_assumption",
  "trigger_rationale":"手上要有存款才會被當成投資詐騙的目標；存款為 0 時不進場（否則「及早識破」的結局也會被存款歸零擋掉）",
  "amount_scaling":{"stat":"存款","apply_to":"詐騙線內所有負的 存款 effects（含 on_enter_effects）","factor":"max(進場時存款, floor) / ref","ref":425000,"floor":50000,"design_assumption":True,
   "note":"ref＝投資線單獨遊玩時初始存款範圍 50,000–800,000 的中點；floor＝該範圍下限。讓損失跟著玩家當下存款等比例變動（劇本寫 30 萬的那一步，存款 42.5 萬的人損失 30 萬、8.5 萬的人損失 6 萬）。正的 存款 effects 不縮放。前台顯示的金額文字不變（劇本沒有寫死金額給玩家看的部分以 JSON 為準）"}})
L["investment"]["age_basis"]["assumption"]=("34–39歲落在內政部 30-39歲（被害人最多）區間；投資詐欺占比最高其實是 60歲以上，但人生線只演到 40歲。範圍與機率是設計假設")
data["meta"]["scam_integration"]=SI
data["meta"]["version"]="0.6"
# ================= v0.7：童年事件「姐姐借100還50」（Leo 提供的個人經驗） =================
_LEO=[{"name":"Leo 提供的個人經驗：姐姐借100元，還錢時說「我只花了50，所以還你50」","kind":"personal_experience","verified":False,
       "verify_note":"個人經驗，無公開網址；同類情節另見 lend5 事件引用的 PTT StupidClown〈所以是欠多少錢〉"}]
_EV={e["id"]:e for e in data["events"]}
for c in _EV["hongbao"]["choices"]: c["next"]="sister_repay"
for c in _EV["lottery"]["choices"]: c["next"]="sister_reveal"
_i=[e["id"] for e in data["events"]].index("hongbao")+1
data["events"].insert(_i,{"id":"sister_repay","age":8,"category":"家人",
 "text":"上週姐姐跟你借了100元。今天她把錢還你，一臉認真：「我只花了50，所以還你50。」",
 "choices":[
  {"text":"好喔，收下","effects":{},"next":"lottery","flags":{"set":["sister_short","missed_reasonable_talk"],"require":[]},"grid":"yellow"},
  {"text":"等等，我算一下","effects":{"警覺":3,"人際":2},"next":"lottery","flags":{"set":["counted_change","checks_first"],"require":[]},"grid":"green"}],
 "sources":_LEO,"presentation":"chat",
 "chat":{"app":"in_person","app_display_name":"家裡客廳","theme":"neutral","contact":{"name":"姐姐","avatar":"placeholder_silhouette","status":"面對面"},
  "messages":[{"id":"m1","from":"contact","text":"欸，上次跟你借的100，現在還你。","delay_ms":1200,"type":"text"},
   {"id":"m2","from":"contact","text":"我只花了50，所以還你50。","delay_ms":1400,"type":"text"},
   {"id":"m3","from":"player","text":"（嗯……好像很合理？）","delay_ms":1200,"type":"text"}]}})
_j=[e["id"] for e in data["events"]].index("lottery")+1
data["events"].insert(_j,{"id":"sister_reveal","age":9,"category":"揭曉","text":"（姐姐還的那筆錢）",
 "choices":[
  {"text":"倒出存錢筒數錢","effects":{"警覺":3,"人際":2,"心理":-1},"next":"lend5","flags":{"set":["learned_count"],"require":["sister_short"]},"grid":"green"},
  {"text":"倒出存錢筒數錢","effects":{"心理":2},"next":"lend5","flags":{"set":[],"require":["!sister_short"]},"grid":"green"}],
 "sources":_LEO,"presentation":"timeskip"})
data.setdefault("red_flag_texts",{})["missed_reasonable_talk"]="話術聽起來合理，不代表數字是對的。用輕鬆的語氣，認真算一次。"
data.setdefault("red_flag_anchors",{})["missed_reasonable_talk"]=[{"event":"sister_repay","message":"m2"}]
data["meta"]["cross_line_flags"]["counted_change"]="小時候當場算出姐姐少還50。假網拍線 fee_more（付款後要你處理「凍結」）多一則回憶提醒，不改數值（shop_sister_math）"
data["meta"]["childhood_flag_decisions"].update({
 "counted_change":{"decision":"wired","rationale":"接到假網拍線 shop_sister_math：聽起來合理的說法也要自己算／查一次"},
 "sister_short":{"decision":"internal_only","rationale":"sister_reveal 用它決定揭曉內容"},
 "learned_count":{"decision":"internal_only","rationale":"事後才發現少50；保留給日後擴充，目前不接詐騙線，避免同一教訓重複加成"}})
# v0.6：age_basis 內引用的 fromnineon 百分比標註 verified:false / display:false
for _h in data["meta"]["scam_integration"]["lines"]:
    _ab=_h.get("age_basis",{})
    if "fromnineon" in _ab.get("sourced",""):
        _ab["sourced"]+="（fromnineon 的百分比為第三方整理，verified:false、display:false：前端不得當官方數字顯示）"
        _ab["unverified_figures"]=[{"source":"fromnineon","verified":False,"display":False,
           "verify_note":"第三方整理的年齡×手法百分比，尚未對到內政部／警政署原始表；只當製作參考"}]
import outcomes; outcomes.apply(data,'life')
finalize_v42(data)
# ================= v0.8：elder 兩個一模一樣的「接爸媽的電話」→ 單一 random:true 選項 =================
from common import ensure_help
_el=next(e for e in data["events"] if e["id"]=="elder"); _a,_b=_el["choices"]
_el["choices"]=[{"text":_a["text"],"random":True,"effects":{},"next":_a["next"],"flags":{"set":[],"require":[]},"grid":"green",
 "outcomes":[{"probability":0.5,"effects":_a["effects"],"flags_set":_a["flags"]["set"],"outcome_text":_a["outcome_text"],"log_text":_a["log_text"],"grid":_a.get("grid","green")},
             {"probability":0.5,"effects":_b["effects"],"flags_set":_b["flags"]["set"],"outcome_text":_b["outcome_text"],"log_text":_b["log_text"],"grid":_b.get("grid","green")}],
 "random_note":{"design_assumption":True,"note":"50/50 是設計假設，不是統計：同原本兩個一模一樣的按鈕（均勻抽選＝各 50%），結局分布不變。爸媽有沒有先約好通關密語不由玩家當下決定，所以做成隨機。"}}]
data["meta"]["random_choice_spec"]=("v0.8：choice.random=true 時只顯示一個按鈕；按下後抽一次 U(0,1)，依 outcomes 陣列順序累加 probability 決定分支。"
 "分支 effects／flags_set 加在 choice 本身 effects／flags.set 之後，next 預設沿用 choice.next；顯示分支的 outcome_text／log_text、grid。參考實作 common.branches／resolve")
ensure_help(data,mental={"END_LIFE_STRETCHED","END_LIFE_HONGBAO_GONE","END_LIFE_RECORD"},legal={"END_LIFE_RECORD"})
data["meta"]["version"]="0.8"

# ================= v0.9：寫手擴充第二／三輪（expansion-r2.md、expansion-r3.md）整合 =================
def _W(desc): return {"name":"寫手提供："+desc+"（寫手提供，待查證）","kind":"writer_provided","verified":False,
  "verify_note":"2026-10-23 Leo 轉貼的寫手擴充文件，只有文字描述、沒有網址或數字出處；待查證。不得當統計或真實案件顯示"}
def _ch(t,e,n,fs,req,ot,lt,g): return {"text":t,"effects":e,"next":n,"flags":{"set":fs,"require":req},"outcome_text":ot,"log_text":lt,"grid":g}
def _ins_after(prev,evs):
    ids=[e["id"] for e in data["events"]]; i=ids.index(prev)+1
    for k,e in enumerate(evs): data["events"].insert(i+k,e)
_EV={e["id"]:e for e in data["events"]}
# 1) 染色小雞揭曉（r3 chick_result；chick_seller 與既有 school_gate 重複，不另加）
_EV["school_gate"]["choices"][0]["flags"]["set"].append("bought_chick")
for c in _EV["school_gate"]["choices"]: c["next"]="chick_result"
_ins_after("school_gate",[{"id":"chick_result","age":6,"category":"揭曉","text":"（幾天後）那天校門口的小雞……",
 "choices":[_ch("看看紙盒",{"心理":-3,"警覺":3},"park_reveal",[],["bought_chick"],"小雞很快就不動了。媽媽說那種是染色的，不太能活。","小雞沒養活","yellow"),
            _ch("看看紙盒",{},"park_reveal",[],["!bought_chick"],"隔壁同學說他買的小雞沒幾天就不見了。你想起媽媽說的話。","想起媽媽說的話","green")],
 "sources":GATE+[_W("童年染色小雞相關回憶（r3 chick_result）")],"presentation":"timeskip"}])
data["meta"]["childhood_flag_decisions"]["bought_chick"]={"decision":"internal_only","rationale":"v0.9 恢復：只給 chick_result 決定揭曉內容，不接詐騙線"}
# 2) 校園團購（r3 group_buy／group_result）
for c in _EV["lend_reveal"]["choices"]: c["next"]="group_buy"
_GB=[_W("校園團購先收錢、之後沒交貨的相關討論（r3 group_buy）")]
_ins_after("lend_reveal",[
 {"id":"group_buy","age":12,"category":"同學","text":"班上有人說要團購限定公仔，先收錢，下週交貨。",
  "choices":[_ch("先付錢",{"存款":-300},"group_result",["paid_group_buy"],[],"你把300元交給負責的同學，他在名單上打了一個勾。","團購先付了300元","yellow"),
             _ch("等看到東西再給錢",{"警覺":5},"group_result",["checks_first"],[],"負責的同學說「隨便你啊」，把名單收了起來。","等看到東西再付錢","green")],"sources":_GB},
 {"id":"group_result","age":12,"category":"揭曉","text":"（一週後）團購的公仔……",
  "choices":[_ch("問負責人",{"警覺":4,"心理":-3},"first_phone",[],["paid_group_buy"],"負責人說貨還沒到，要再等。後來有人說他收了錢就沒再出現。","團購公仔沒拿到","red"),
             _ch("問負責人",{"警覺":2},"first_phone",[],["!paid_group_buy"],"負責人說貨還沒到。付了錢的同學開始著急，你的300元還在。","沒付錢，錢還在","green")],
  "sources":_GB,"presentation":"timeskip"}])
# 3) 先付教材費的打工（r3 part_time_ad／ad_result；年齡 17→16，避開既有 part_time 17歲）
for c in _EV["lottery_reveal"]["choices"]: c["next"]="part_time_ad"
_PT=[_W("「居家打字、先付教材費」的打工徵才（r3 part_time_ad）")]
_ins_after("lottery_reveal",[
 {"id":"part_time_ad","age":16,"category":"工作","text":"社群上有人徵「居家打字，日領五百，先付三百元教材費就能開始」。",
  "choices":[_ch("先問家人",{"警覺":5},"ad_result",["checks_first"],[],"家人皺眉說：「工作還沒做，怎麼先要你付錢？」你把貼文滑掉了。","先問了家人","green"),
             _ch("直接轉帳",{"存款":-300,"心理":-3},"ad_result",["paid_job_fee"],[],"你轉了300元，對方回：「收到，教材這幾天寄出。」","付了300元教材費","yellow")],"sources":_PT},
 {"id":"ad_result","age":16,"category":"揭曉","text":"（幾天後）那份居家打字的工作……",
  "choices":[_ch("傳訊息問",{"警覺":4,"心理":-2},"part_time",["wary_of_easy_money"],["paid_job_fee"],"對方已讀，沒有回。教材一直沒寄來，你的300元也沒了。","教材費要不回來","red"),
             _ch("傳訊息問",{},"part_time",[],["!paid_job_fee"],"你沒付錢，也就沒什麼好問的。那則貼文過幾天就不見了。","貼文不見了","green")],
  "sources":_PT,"presentation":"timeskip"}])
data["meta"]["childhood_flag_decisions"].update({"paid_group_buy":{"decision":"internal_only","rationale":"group_result 揭曉用"},
 "paid_job_fee":{"decision":"internal_only","rationale":"ad_result 揭曉用；付過教材費的人在揭曉時加 wary_of_easy_money（已接車手線／投資線）"}})
# 4) 二次受害「幫你追回被騙的錢」（r2 second_scam；32歲，只在有 scam_money_lost 時演）
for c in _EV["rosca"]["choices"]: c["next"]="second_scam"
_ins_after("rosca",[{"id":"second_scam","age":32,"category":"網友","text":"有人私訊你，說可以幫被騙的人「追回損失」，只要先付一筆手續費。",
 "choices":[_ch("打165確認",{"警覺":10},"elder",["checks_first"],["lost_money"],"165的人說：說能幫你追回被騙的錢、還要先收費的，本身就是詐騙。你封鎖了對方。","打165確認追回服務","green"),
            _ch("先付一筆試試",{"存款":-30000,"心理":-10},"elder",["second_victim"],["lost_money"],"你付了手續費。對方又要更多錢，最後也消失了。","又被騙了一次","red"),
            _ch("滑掉訊息",{},"elder",[],["!lost_money"],"你沒有被倒過、騙過錢，覺得這訊息莫名其妙，就滑掉了。","滑掉陌生私訊","green")],
 "sources":[_W("二次受害：財損受害者中有人受騙不止一次（文件未附統計數字與出處）")],
 "amount_note":{"design_assumption":True,"note":"寫手原稿 -50,000；人生線初始存款 80,000–200,000，改為 -30,000（設計假設，非統計）"}}])
data["meta"]["cross_line_flags"].setdefault("_v09_note","v0.9 新 flag second_victim 只記錄（給成就／分享卡），不接詐騙線")
for _e,_i in (("rosca",1),("lend",1),("rent",1),("game_trade",1)): _EV[_e]["choices"][_i]["flags"]["set"].append("lost_money")
for _ln,_m in data["meta"]["scam_integration"]["return_map"].items():
    if _ln.startswith("_"): continue
    for _k,_v in _m.items():
        if "scam_money_lost" in _v["flags"]: _v["flags"].append("lost_money")
data["meta"]["scam_integration"]["return_flag_notes"]["lost_money"]="v0.9：人生線或詐騙線有實質財損（倒會、借錢不還、押金、遊戲交易、詐騙線 scam_money_lost）。second_scam（追回詐騙）讀取"
for _e in data["events"]:
    if _e["id"] in ("group_buy","part_time_ad","second_scam"): _e["presentation"]="card"

# ================= v0.9b：開局數值隨機骰＋心理歸零提早結束（END_LIFE_HALTED） =================
data["meta"]["initial_stats_roll"]={"design_assumption":True,
 "rule":"開局各數值獨立抽整數，均勻分布於 range（含兩端）；再抽一次 temperament，套用其 心理 加減（最後依 min/max 截斷）。不套 family_pool（與 rates.py 一致）",
 "stats":{"存款":{"range":[80000,200000]},"警覺":{"range":[15,45]},"人際":{"range":[30,70]},"心理":{"range":[35,80]}},
 "temperament":[{"id":"steady","p":0.8,"心理":0,"note":"一般"},{"id":"sensitive","p":0.2,"心理":-10,"note":"天生比較容易累、比較敏感（不顯示給玩家，也不是診斷）"}],
 "note":"範圍與 20% 較敏感的比例都是設計假設，不是統計；目的只是讓每一局起點不同，有人天生比較脆弱"}
for _k,_v in data["meta"]["initial_stats_roll"]["stats"].items(): data["player_init"]["stats"][_k]["init_range"]=_v["range"]
data["meta"]["early_halt"]={"stat":"心理","when":"lte 0","ending":"END_LIFE_HALTED",
 "rule":"人生線：每做完一個選擇、套用 effects 之後，若 心理 ≤ 0 立刻停止，不再前往下一個事件，直接顯示 END_LIFE_HALTED。詐騙線：照常演到該線結局並記入 scam_history（詐騙線自己的崩潰結局仍會出現），結束時若 心理 ≤ 0，不回人生線，直接顯示 END_LIFE_HALTED。age_lived＝停止時的年齡",
 "reference":"combined.py play()／play_scam()","design_assumption":True}
data["endings"].append({"id":"END_LIFE_HALTED","priority":0.1,"conditions":{"flags_all":["life_halted"]},
 "text":"一件一件的事壓下來，你的身心撐不下去了。這一局的人生，停在這裡。\n但在真實世界裡，撐不下去的時候，可以先停下來、找人說。很多人走過最低的地方，後來慢慢好起來。",
 "reason_texts":[{"flag":"life_halted","text":"心理一點一點被磨到見底。"},{"flag":"scam_money_lost","text":"被騙走的錢，壓得你喘不過氣。"},{"flag":"lost_money","text":"一次又一次的金錢損失。"},{"flag":"criminal_record","text":"那段「打工」留下的紀錄。"}],
 "case_card":{"summary":"這個結局沒有對應單一真實案件。遊戲把每一次被騙、被倒、被為難都算成一點點心理消耗，累積到撐不住為止，提醒你：壓力是會累積的，不必等到最低點才求助。","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html","note":"設計說明，非真實案件；連結為 1925 安心專線"},
 "missed_red_flags":["累了很久，卻一直沒有跟人說","把每一次損失都自己扛下來"],
 "sources":HL,"requires_flags":["life_halted"],"forbids_flags":[],
 "title":"停在這裡的人","title_emoji":"🕯️","grid_color":"red","rarity_key":"life_END_LIFE_HALTED","combined_only":True,
 "combined_only_note":"心理歸零由 combined.py 的 early_halt 規則觸發；單獨跑人生線不判定",
 "real_world_stat":stat_null("這是遊戲機制結局，沒有對應的官方統計"),"share_text":"這一局，我停在這裡。撐不住的時候，記得找人說。",
 "share_card":dict(SHARE_CARD,fields=SHARE_CARD["fields"]+["age_lived","scam_history"]),"tone":"serious_hopeful",
 "safety_note":"不描寫自殺或死亡、不提任何方式；必附 1925、1995、165"})
data["meta"]["mental_time_recovery"]={"stat":"心理","per_year":2.6,"design_assumption":True,"rule":"人生線前進到下一個事件時，心理 + per_year ×（年齡差），上限 100；詐騙線內不回復（另有 pre_entry +10）","tuning_note":"v1.2：新增成人事件後 1.8→2.6，使 HALTED 回到 5–15%（設計假設）","note":"時間會讓人慢慢喘口氣；數值是設計假設，用來讓心理歸零靠長期累積而不是單一事件"}
data["meta"]["scam_integration"]["return_flag_notes"]["life_halted"]="v0.9：心理歸零（early_halt）。END_LIFE_HALTED 讀取"

# ================= v1.0：人生線延長到 50 歲；交往（25–29）、婚姻（30–34）、家長篇（41–45）三條新線（Leo 核准） =================
_EV={e["id"]:e for e in data["events"]}
_EV["LIFE_ROUTER"]["age"]=50; _EV["LIFE_ROUTER"]["text"]="回頭看這五十年……（引擎依 ending_rules 自動判定，不顯示選項）"
for c in _EV["elder"]["choices"]:
    c["next"]="child"
    for o in c.get("outcomes",[]): o["next"]="child"
_c=_EV["otp_reveal"]["choices"][0]; _c["flags"]["set"].append("family_blame")
_c["outcome_text"]+="媽媽很生氣：「你怎麼會這麼笨？」你低著頭，什麼也說不出來。"
_new=[
 {"id":"child","age":38,"category":"家庭","text":"你有了一個孩子。抱著他的那一刻，你想起自己小時候的很多事。","presentation":"card",
  "sources":[_W("人生線延長到 50 歲的過場事件（Leo 核准的家長篇前提）")],
  "choices":[_ch("答應自己要好好聽他說",{"心理":5,"人際":5,"存款":60000},"guess_who",["has_child"],[],"你在心裡答應：以後他遇到事情，你要先聽他說完。（這些年工作慢慢存下一筆積蓄——金額為設計假設）","有了孩子","green")]},
 {"id":"guess_who","age":47,"category":"長輩","text":"你收到一則訊息，頭像是早安圖，對方說是「老同學」，說下錯單急需周轉。",
  "presentation":"card","sources":[_W("guess_who：假同學下錯單案（原稿 45 歲，配合家長篇改為 47 歲）")]+ELDER[:1],
  "choices":[_ch("打電話問本人",{"警覺":10},"fake_police",["checks_first"],[],"本人接了電話，一頭霧水：「我沒有傳訊息給你啊。」","打給本人","green"),
   _ch("去銀行準備轉帳",{"警覺":-5},"fake_police",["bank_stopped"],[],"你到了銀行。行員覺得不對勁，通報了警方。錢沒有匯出去。","去銀行轉帳","yellow")]},
 {"id":"fake_police","age":49,"category":"權威","text":"有人打電話說你的證件被冒用，接著自稱警察要做「電話筆錄」，要你保密、配合監管帳戶。",
  "presentation":"card","sources":[_W("fake_police：假檢警監管帳戶（原稿 55 歲，人生線只到 50 歲，改為 49 歲）")],
  "choices":[_ch("掛斷，打165",{"警覺":15},"LIFE_ROUTER",["checks_first"],[],"165 說：警察不會用電話做筆錄，也不會監管你的帳戶。","掛斷打165","green"),
   _ch("配合並保密",{"存款":-60000,"心理":-12},"LIFE_ROUTER",["lost_money","scam_money_lost"],[],"你照著指示把錢轉出去，也沒告訴家人。後來才知道那些「警察」都是假的。","配合假警察","red")],
  "amount_note":{"design_assumption":True,"note":"寫手原稿 -2,000,000；依人生線存款量級縮為 -60,000（設計假設）"}}]
_ins_after("elder",_new)
SI=data["meta"]["scam_integration"]; CF=data["meta"]["cross_line_flags"]
CF["family_blame"]="曾被家人責怪（otp_reveal 媽媽生氣、交往線借錢匯款、婚姻線替配偶還債）。家長篇多一則回憶句＋「不重複」選項（pa_blame_*）"
CF["paid_job_fee"]="16 歲付過求職費用。交往線 rm_ask_invest 多一則回憶（rm_fee_memory）"
CF["rm_deep_loss_seen"]="交往線借錢匯款（DEEP／COLLAPSE）。婚姻線 mr_asks 多一則回憶（mr_romance_memory）"
def _line(line,name,base,lo,hi,entry,src,note):
    return {"line":line,"name":name,"script":f"script-{line}.json","trigger":{},"entry_event":entry,
      "duration":{"default_years":0,"rules":[]},"entry_window":{"base_age":base,"offset_min":lo,"offset_max":hi,"range":[base+lo,base+hi]},
      "probability":1.0,"probability_note":"每局必出（Leo 核准）","amount_scaling":{"stat":"存款","apply_to":"詐騙線內負的 存款 effects","factor":"max(進場時存款, floor) / ref","ref":150000,"floor":20000,"design_assumption":True},"mandatory":True,
      "age_basis":{"status":"design_assumption","assumption":note,"source_names":src},"trigger_rationale":"沒有前提條件；每局必出"}
SI["lines"]+=[_line("romance","交往詐騙線",27,-2,2,"rm_meet",["刑事局 115-02-21 交友投資案"],"25–29 歲：Leo 指定；具體範圍為設計假設"),
 _line("marriage","婚姻詐騙線",32,-2,2,"mr_wedding",["高院 112上訴2406","桃園 114桃簡1372","苗栗 95婚75"],"30–34 歲：Leo 指定 30–35，entry 須早於下一個事件，取 30–34"),
 _line("parent","家長篇",43,-2,2,"pa_start",["教育部、內政部致家長信","臺北市少年警察隊"],"41–45 歲：孩子國中階段；設計假設")]
SI["lines"][-3]["probability"]=1.0
RMAP=SI["return_map"]
RMAP["romance"]={"END_RM_COLLAPSE":{"flags":["scam_money_lost","scam_debt","lost_money","family_blame","rm_deep_loss_seen"]},
 "END_RM_DEEP":{"flags":["scam_money_lost","scam_debt","lost_money","family_blame","rm_deep_loss_seen"]},
 "END_RM_STOPPED":{"flags":["lost_money","evidence_habit"]},"END_RM_SISTER":{"flags":["checks_first"]},
 "END_RM_HOTLINE":{"flags":["checks_first"]},"END_RM_CHECKED":{"flags":["checks_first"]}}
RMAP["marriage"]={"END_MR_COLLAPSE":{"flags":["scam_money_lost","lost_money"]},"END_MR_SILENT":{"flags":["scam_money_lost","lost_money"]},
 "END_MR_PAID":{"flags":["scam_money_lost","lost_money","family_blame"]},"END_MR_DIVORCE":{"flags":["evidence_habit"]},
 "END_MR_LEGAL":{"flags":["evidence_habit"]},"END_MR_ANNUL":{"flags":["evidence_habit"]}}
RMAP["parent"]={k:{"flags":f} for k,f in {"END_PA_COLLAPSE":["lost_money"],"END_PA_HUSH":["lost_money"],"END_PA_SILENT":[],"END_PA_BROKE_CYCLE":["broke_blame_cycle"],"END_PA_OPEN":[]}.items()}
SI["return_flag_notes"]["broke_blame_cycle"]="v1.0：家長篇選擇不重複當年的責怪。只記錄（成就讀取）"
SI["return_flag_notes"]["family_blame"]=CF["family_blame"]
SI["age_rules"]["age_lived"]="max(最後一個人生事件的 age, 最後一條詐騙線的 exit_age)；v1.0 人生線延長到 LIFE_ROUTER 50 歲；心理歸零提前結束時是當下年齡"
data["meta"]["event_pool"]={"concept":"同一年齡窗內的事件隨機排序、部分事件只依機率出現（詐騙線以 entry_window＋probability 實作：開局抽好進場年齡，同齡依 lines 順序）",
 "mandatory_lines":["romance","parent"],"note":"人生線本體仍為固定順序的童年→成年事件；隨機性來自詐騙線插入時機與 random:true 分支（設計假設）"}
data["meta"]["recurring_characters"]={"姐姐":"sister_repay（8）→ rm_excuse／rm_ask_*（交往線，給姐姐看對話）",
 "爸媽":"hongbao（8）、otp_reveal（15，媽媽生氣→family_blame）、elder（35）、交往線/婚姻線的責怪→家長篇回憶",
 "借錢的朋友":"lend（24）→ 交往線 rm_ask_loan 回憶（rm_lent_memory）→ 投資線 ad_group（inv_lent_friend_group：拉你進群組的就是他）",
 "孩子":"child（38）→ 家長篇（41–45）"}
from common import apply_mental_wear; apply_mental_wear(data)
ensure_help(data,mental={"END_LIFE_HALTED"})
# 5) 既有事件只補結果文字（寫手 r2 文字；與既有分支語意一致者才採用）
_EV={e["id"]:e for e in data["events"]}
_c=_EV["otp_reveal"]["choices"][0]; _c["outcome_text"]="媽媽拿著電話帳單問：「這幾筆小額付款是什麼？」帳單上多了幾筆你沒印象的遊戲點數。你這才知道那串數字不是送禮用的。"
data["meta"]["writer_r2_r3_integration"]={"date":"2026-10-23","files":["expansion-r2.md","expansion-r3.md"],"note":"採用／合併／待決清單見 script-life-README.md v0.9"}
data["meta"]["version"]="0.9"
# ===== v1.2：expansion-childhood-fix.md（t43u）、expansion-r4.md（t29u/t30u）、expansion-flagtext.md（t42u）整合 =====
_EV={e["id"]:e for e in data["events"]}
def _del(i): data["events"][:]=[e for e in data["events"] if e["id"]!=i]
def _card(i,a,cat,t,chs,src,**k): return {"id":i,"age":a,"category":cat,"text":t,"presentation":"card","choices":chs,"sources":src,**k}
def _nextof(i): s={c["next"] for c in _EV[i]["choices"]}; assert len(s)==1,(i,s); return s.pop()
def _rewire(i,new): 
    for c in _EV[i]["choices"]:
        c["next"]=new
        for o in c.get("outcomes",[]):
            if "next" in o: o["next"]=new  # 隨機分支自己的 next 也要改
def _croute(rid,age,cond,yes,no):  # 條件 router：有 cond flag 才進 yes，否則跳 no
    return {"id":rid,"age":age,"category":"系統","router":True,"text":"（條件分流，不顯示）","presentation":"timeskip",
      "choices":[{"text":"條件成立","effects":{},"next":yes,"flags":{"set":[],"require":[cond]},"grid":"green","outcome_text":"（系統分流）","log_text":"（分流）"},
                 {"text":"條件不成立","effects":{},"next":no,"flags":{"set":[],"require":["!"+cond]},"grid":"green","outcome_text":"（系統分流）","log_text":"（分流）"}],
      "sources":[{"name":"設計假設：條件分流（遊戲機制）","url":"https://165.npa.gov.tw/"}]}
CF=[_W("童年受騙事件擴充（修正版）expansion-childhood-fix.md")]
R4=[_W("《2300萬分之一》交貨便與相關擴充＋第四輪 expansion-r4.md；依據描述：刑事局揭露超商寄件被用於洗錢")]
FT=[_W("有標記／沒標記結果文字差異 expansion-flagtext.md")]
# --- t43u：移除染色小雞（school_gate、chick_result）
_rewire("promise_park","park_reveal"); _del("school_gate"); _del("chick_result")
# --- t43u card_swap 併入既有 card_trade／card_reveal（5張，本版為準；flag 沿用 traded_card／card_scammed）
_EV={e["id"]:e for e in data["events"]}
for i in ("card_trade","card_reveal"):
    e=_EV[i]; e["text"]=e["text"].replace("7張","5張")
    for c in e["choices"]:
        for k in ("text","outcome_text","log_text"):
            if c.get(k): c[k]=c[k].replace("7張","5張")
    e["sources"]=e["sources"]+CF
# --- t43u group_buy 改 11 歲、200 元，移到 lend_reveal（12）之前
_rewire("lend_reveal","first_phone")
for i in ("slurpee",): _rewire(i,"group_buy")
_rewire("group_result","lend_reveal")
for i in ("group_buy","group_result"):
    e=_EV[i]; e["age"]=11; e["sources"]=e["sources"]+CF
    for c in e["choices"]:
        for k in ("outcome_text","log_text"):
            if c.get(k): c[k]=c[k].replace("300","200")
        if c["effects"].get("存款")==-300: c["effects"]["存款"]=-200
_gb=[e for e in data["events"] if e["id"] in("group_buy","group_result")]
data["events"][:]=[e for e in data["events"] if e["id"] not in("group_buy","group_result")]
_ins_after("slurpee",_gb)
# --- t43u 新事件（成對：受騙選項→當天/幾天後揭曉；安全選項直接往下）
def _pair(prev,sid,rid,age,cat,text,bad,good,rtext,rlabel,flag,blog):
    nx=_nextof(prev); _rewire(prev,sid)
    _ins_after(prev,[
     _card(sid,age,cat,text,[_ch(bad[0],bad[1],rid,[],[],bad[2],bad[3],"yellow"),
                             _ch(good[0],good[1],nx,["checks_first"],[],good[2],good[3],"green")],CF),
     _card(rid,age,"揭曉",rlabel[0],[_ch(rlabel[1],rlabel[2],nx,[flag,"lost_money"] if blog else [flag],[],rtext,rlabel[3],"red" if blog else "yellow")],CF)])
    _EV.update({e["id"]:e for e in data["events"]})
_EV={e["id"]:e for e in data["events"]}
_pair("card_trade","sticker_trade","sticker_result",7,"同學","同學拿出一疊亮晶晶的貼紙，說用你三張稀有卡換他一整疊。",
  ("換！",{"人際":3},"你把三張稀有卡交出去，抱著一整疊貼紙回家。","用三張卡換了一疊貼紙"),
  ("先拿給哥哥看",{"警覺":4},"哥哥翻了翻那疊貼紙，叫你先別換。","先拿給哥哥看"),
  "別人說這些貼紙很多都是重複的，而且有些是假的。你換出去的卡沒了。",("（當天）你把換到的貼紙拿出來看。","拿給別人看",{"心理":-4,"警覺":5},"換到的貼紙多是重複的"),"fake_sticker",False)
_pair("sister_repay","toy_seller","toy_result",8,"校門口","雜貨店外面有人說「最後幾隻限量玩具，原價的一半」，還拿出包裝給你看。",
  ("買一隻",{"存款":-150,"心理":3},"你掏出零用錢，抱著包裝盒回家。","買了限量玩具"),
  ("先回家問",{"警覺":4},"你先回家問。隔天那個攤子已經不在了。","先回家問"),
  "裡面的玩具跟外面說的不一樣，而且做工很粗糙。媽媽說這種是假的。",("（當天）你打開包裝。","看看裡面",{"心理":-5,"警覺":5},"買到假玩具"),"fake_toy",False)
_pair("card_reveal","teacher_permission","exam_result",10,"老師的文字遊戲","同學說：「老師說這次小考可以帶小抄，我已經準備好了。」",
  ("信了，也準備小抄",{"心理":-5,"警覺":3},"你也寫了一張小抄，夾在鉛筆盒裡。","準備了小抄"),
  ("先問老師",{"警覺":5},"老師說：「誰說可以帶小抄？」你鬆了一口氣。","先問老師"),
  "老師說根本沒有允許帶小抄。你被罰站，同學也沒被抓到。",("（考試當天）考試時你拿出小抄。","被老師看到",{"心理":-8,"人際":-3,"警覺":5},"小抄被老師看到"),"fake_permission",False)
_pair("first_phone","points_help","points_result",12,"網友","有人在遊戲裡私訊你：「家裡斷了生活費，可以幫我買一點遊戲點數嗎？我之後還你。」",
  ("幫他買",{"存款":-300,"人際":3},"你用零用錢買了點數，把序號傳給他。","幫網友買點數"),
  ("拒絕",{"警覺":4},"你回他：「不好意思，我沒辦法。」對方就沒再傳了。","拒絕代買點數"),
  "他已讀不回。你後來發現那個帳號也不見了。",("（幾天後）你問他要還錢。","問他",{"警覺":5,"人際":-2},"幫買的點數沒拿回"),"points_not_returned",False)
# ice_lend 併入既有 lend5（以情境變體呈現；flag 沿用 lent_5）；gacha_try 併入既有 lottery（flag 沿用 chased_lottery）
_EV["lend5"]["sources"]=_EV["lend5"]["sources"]+CF; _EV["lottery"]["sources"]=_EV["lottery"]["sources"]+CF
# --- t29u/t30u 成年事件
_EV={e["id"]:e for e in data["events"]}
# 學貸拿去投資（loan_use，20 歲；只有申請學貸者會遇到）
_rewire("student_loan","route_loan_use")
_ins_after("student_loan",[_croute("route_loan_use",20,"student_loan","loan_use","rent"),
 _card("loan_use",20,"家庭與金錢","學貸撥下來了。有人私訊你：「學貸利率很低，先借來投資，我幫你操作，很快回本。」",
  [_ch("自己規劃用途",{"警覺":5},"rent",["checks_first"],[],"你把學貸留給學費和生活費，封鎖了那個帳號。","自己規劃學貸用途","green"),
   _ch("聽對方建議",{"存款":-30000,"心理":-5},"rent",["loan_invest","lost_money"],[],"你照對方的建議把錢轉出去。幾個月後，那筆錢只剩帳面上的數字，對方也不回了。","學貸被拿去「投資」","red")],R4)])
# 租屋先匯訂金（rent_deposit，22 歲；變體 rent_key：鑰匙在超商寄貨櫃）
_EV={e["id"]:e for e in data["events"]}
_rewire("rent","rent_deposit")
_ins_after("rent",[
 _card("rent_deposit",22,"租屋","網路上看到一間便宜套房。房東說人在外地，要先匯一萬元訂金才能幫你保留看房。",
  [_ch("先匯訂金",{"存款":-10000,"心理":-5},"rent_result",["rent_scammed","lost_money"],[],"你匯了訂金，房東說會再約你看房時間。","先匯了訂金","yellow"),
   _ch("堅持先看房",{"警覺":8},"mlm",["checks_first"],[],"你沒有先匯訂金。你約了看房再決定。","堅持先看房再給錢","green")],R4),
 _card("rent_result",22,"揭曉","（幾天後）你再傳訊息問看房時間。",
  [_ch("再傳訊息",{"警覺":5,"心理":-3},"mlm",[],["!v_rent_deposit_1"],"對方已讀不回。那個地址根本沒有在出租。","租屋訂金被騙","red"),
   _ch("去取鑰匙",{"心理":-5,"警覺":4},"mlm",[],["v_rent_deposit_1"],"取件碼是假的。房東消失了。","超商寄貨櫃取件碼是假的","red")],R4)])
# 海外包裹扣關（customs_fee，25 歲）
_EV={e["id"]:e for e in data["events"]}
_rewire("lend","customs_fee")
_ins_after("lend",[
 _card("customs_fee",25,"網路交易","有人打來說你的海外包裹被扣關，要你到超商寄件，寄現金或金融卡代墊通關費。",
  [_ch("到超商寄出",{"存款":-20000,"心理":-8},"customs_result",["customs_scammed","lost_money"],[],"你照指示到超商寄出。對方說包裹很快就會放行。","寄出通關費","yellow"),
   _ch("掛斷，自己查",{"警覺":10},"insurance",["checks_first"],[],"你掛斷電話，自己查了物流紀錄，根本沒有被扣的包裹。","掛斷自己查","green")],R4),
 _card("customs_result",25,"揭曉","（幾天後）包裹一直沒到。",
  [_ch("再傳訊息問",{"心理":-5,"警覺":5},"insurance",[],[],"對方已讀不回。你沒有收到任何包裹。","假通關費被騙","red")],R4)])
# 假保單解約（fake_insurance，32 歲）
_EV={e["id"]:e for e in data["events"]}
_rewire("second_scam","fake_insurance")
_ins_after("second_scam",[
 _card("fake_insurance",32,"權威","有人自稱保險專員，說你的保單可以提前解約領一筆高額解約金，但要先付手續費。",
  [_ch("打給原保險公司",{"警覺":12},"route_sleep",["checks_first"],[],"你打給原保險公司確認。對方說沒有這回事。","打給原保險公司確認","green"),
   _ch("先付手續費",{"存款":-20000,"心理":-8},"route_sleep",["insurance_fee","lost_money"],[],"你付了手續費。對方又要更多文件費，最後消失。","付了假解約手續費","red")],R4),
 _croute("route_sleep",34,"lost_money","sleep_issue","elder"),
 _card("sleep_issue",34,"心理","被騙之後，你常常半夜醒來，腦中一直重播那些對話。",
  [_ch("找人聊聊或打專線",{"心理":8,"人際":5},"elder",["sought_help"],[],"你打了專線。對方說很多人都有類似的感覺，被騙不是你的錯。","打專線找人聊","green"),
   _ch("自己撐",{"心理":-10},"elder",[],[],"你一個人撐著，白天照常上班。你告訴自己：被騙不是你的錯。","一個人撐著","yellow")],
  R4+[{"name":"1925安心專線（衛福部心理健康司，24小時免付費）","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html"}])])
# 家人說「你怎麼這麼笨」（family_talk，36 歲；只有被騙過者）
_EV={e["id"]:e for e in data["events"]}
_rewire("elder","route_family_talk")
_ins_after("elder",[_croute("route_family_talk",36,"lost_money","family_talk","child"),
 _card("family_talk",36,"家人","家族聚會時，有人提起你被騙的事：「你怎麼這麼笨？」",
  [_ch("跟他們說明過程",{"人際":3,"心理":5},"child",["told_family"],[],"你把過程一步一步說出來。有人沉默，有人說自己也差點被騙過。","跟家人說明過程","green"),
   _ch("不再提",{"人際":-5,"心理":-8},"child",["family_blame"],[],"你選擇不再解釋。之後家裡談到錢的時候，氣氛變得很奇怪。","不再提被騙的事","yellow")],R4)])
# 寄黃金（gold_delivery，40 歲；金額 -500000 依 v1.0 比例縮為 -80000（v1.2 調整分布再縮），設計假設）
_EV={e["id"]:e for e in data["events"]}
_rewire("child","gold_delivery")
_ins_after("child",[_card("gold_delivery",40,"網友","社群上認識的「投資老師」說黃金期貨很賺，叫你把家裡的黃金用超商寄件寄過去，還叮嚀店員問就說是生活用品。",
  [_ch("寄出黃金",{"存款":-80000,"心理":-15},"guess_who",["gold_sent","lost_money","scam_money_lost"],[],"你把黃金寄出去了。對方之後就消失。錢和黃金都拿不回來。","寄出黃金","red"),
   _ch("先見面或查證",{"警覺":12},"guess_who",["checks_first"],[],"你說要先見面。對方開始找理由推託，你沒有寄。","先見面查證","green")],R4,amount_note="原稿 -500000，依 v1.0 縮放後再調為 -80000（約 0.16 倍，v1.2 為穩定結局分布，設計假設）")])
# 車手線入口變體（t29u 寄卡／寄件代碼／超商機台／貸款美化帳戶／寄 SIM 卡 → mule 入口變體；17 歲系統抽選，進 mule 後以插話呈現）
_EV={e["id"]:e for e in data["events"]}
_rewire("ad_result","pool_mule_variant"); _rewire("part_time_ad","pool_mule_variant") if False else None
for e,c in [(e,c) for e in data["events"] for c in e["choices"] if c["next"]=="part_time" and e["id"]!="pool_mule_variant"]: c["next"]="pool_mule_variant"
_ins_after("ad_result",[{"id":"pool_mule_variant","age":17,"category":"系統","router":True,"random":True,"text":"（事件池抽選：車手線入口情境，不顯示）","presentation":"timeskip",
 "choices":[{"text":f"抽選{k+1}","effects":{},"next":"part_time","flags":{"set":[f] if f else [],"require":[]},"grid":"green","outcome_text":"（系統抽選）","log_text":"（事件池）"}
            for k,f in enumerate([None,"mv_salary_card","mv_delivery_code","mv_kiosk","mv_loan_beautify","mv_sim"])],"sources":R4}])
# --- t42u：有標記結果文字（只掛在「選對」的選項；沒標記時沿用既有結果文字——既有架構優先）
_EV={e["id"]:e for e in data["events"]}
def _ov(eid,ci,flags_all,text,flags_none=()):
    c=_EV[eid]["choices"][ci]; c.setdefault("outcome_variants",[]).append({"when":{"flags_all":list(flags_all),"flags_none":list(flags_none)},"text":text,"source":"expansion-flagtext.md（寫手提供，待查證）"})
_ov("game_trade",0,["points_not_returned"],"你想起以前幫買遊戲點數後對方已讀不回的事。這次你沒有再幫，只在平台內交易。")  # 27＋19
_ov("mlm",0,["paid_job_fee"],"你想起上次付了費用後對方就消失的事。這次你沒有再付，先查公司再決定。")  # 11
_ov("rent_deposit",1,["deposit_lost"],"你想起上次押金拿不回來的事。這次你堅持先看房再給錢。")  # 12（早期 flag 沿用 deposit_lost）
_ov("second_scam",0,["lost_money"],"你想起上次已經被騙過一次。這次你直接打165確認，沒有再付任何費用。")  # 9＋24
_ov("fake_insurance",0,["pressure_signer"],"你想起上次當場簽約後後悔的事。這次你直接打給原保險公司確認。")  # 14（早期 flag 沿用 pressure_signer）
_ov("gold_delivery",1,["scam_money_lost"],"你想起上次被騙走一大筆錢的事。這次你沒有寄，選擇先見面確認。")  # 23
_ov("customs_fee",1,["lost_money"],"你想起以前付了錢卻什麼都沒拿到的事。這次你沒有寄，自己查了物流紀錄。")  # 8 近似
# --- t43u：後期「你想起以前…」（人生線事件文字變體）
_EV["lend"].setdefault("text_variants",[])
_EV["lend"]["text_variants"]+= [
 {"when":{"flags_all":["points_not_returned"]},"text":_EV["lend"]["text"]+"（你想起以前幫買遊戲點數後對方消失的事。）"},
 {"when":{"flags_all":["lent_5"],"flags_none":["trust_repaid"]},"text":_EV["lend"]["text"]+"（你想起以前借同學錢買冰、說好隔天還卻沒還的事。）"}]
_EV["insurance"].setdefault("text_variants",[]).append({"when":{"flags_all":["fake_permission"]},"text":_EV["insurance"]["text"]+"（業務說「主管說可以先簽」。你想起以前同學說老師允許帶小抄的事。）"})
data["meta"]["flag_text_spec"]=("v1.2：choice.outcome_variants=[{when:{flags_all,flags_none},text}]，選後依『選之前』已有的 flags 取第一個成立者取代 outcome_text；"
  "只掛在安全選項（t42u：沒標記文字只適用選對時；沒標記時沿用既有 outcome_text，既有架構優先）。事件 text_variants 同理取代 text。")
data["meta"]["v12_flag_map"]={"flag_fake_card":"card_scammed（既有）","flag_ice_not_returned":"lent_5 且無 trust_repaid（既有）","flag_gacha_loss":"chased_lottery（既有）",
 "flag_group_buy_fail":"paid_group_buy（既有）","flag_fake_sticker":"fake_sticker（新）","flag_fake_toy":"fake_toy（新）","flag_points_not_returned":"points_not_returned（新）",
 "flag_fake_permission":"fake_permission（新）","flag_rent_scammed":"rent_scammed（新）","flag_loan_invest":"loan_invest（新）","flag_insurance_fee":"insurance_fee（新）",
 "flag_gold_sent":"gold_sent（新）","flag_big_loss":"lost_money（既有）","flag_job_fee":"paid_job_fee（既有）","flag_game_trade":"game_scammed（既有）","flag_red_packet_self":"own_account（既有）","flag_red_packet_mom":"gave_hongbao（既有）","flag_salary_delayed":"wage_unpaid（既有）","flag_otp_sent":"gave_otp（既有）"}

# ===== v2.0（v6）：童年日常事件池擴充、生活里程碑具象化、「純真與真誠」線（Leo 9:35 PM 指示） =====
def _O(basis,url,ok=True,note=None): return {"name":f"原創情境（依{basis}）","kind":"original","verified":ok,"url":url,**({"note":note} if note else {})}
_GEN="泛用官方頁：查無對應此情境的具體官方文章，連結為 165 全民防騙網首頁"
S165=_O("165全民防騙網常見手法宣導","https://165.npa.gov.tw/",note=_GEN)
SPHISH=_O("刑事警察局：釣魚簡訊與假連結竊取個資宣導","https://www.cib.npa.gov.tw/ch/app/news/view?id=1887&module=news&serno=f0a71d25-073b-48c8-959a-02117a240e25")
SGUESS=_O("刑事警察局《常見詐騙手法話術解析與因應之道》第五章 猜猜我是誰：以舊電話向本人確認、約定密語","https://www.cib.npa.gov.tw/ch/app/data/view?id=1909&module=wg116&serno=4f04dab6-3ca5-4139-a94e-66be03b62ba3")
SKID=_O("警政署兒童網站〈自我保護〉：不接受陌生人物品、走散時找服務台","https://www.npa.gov.tw/kids/app/artwebsite/view?id=1306&module=artwebsite&serno=e3cc7c20-ac54-4140-9552-41e41dfe2052")
SKIDCODE=_O("金門縣警察局〈預防教育篇〉：約定暗語；陌生人來校接學生應與家長查證","https://kpb.kinmen.gov.tw/cp.aspx?n=1E376F200F2FB2C4")
SDON=_O("衛福部社會救助及社工司〈捐款獻愛心注意事項〉：認明勸募許可文號","https://dep.mohw.gov.tw/dosaasw/fp-609-85395-103.html")
SLAB=_O("勞動部〈部分工時／工讀生，我該瞭解的權益有哪些?〉","https://www.mol.gov.tw/1607/28690/87756/")
SRENT=_O("租賃住宅市場發展及管理條例第7條：押金不得逾二個月租金，租約消滅應返還","https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=D0060125")
SPSY=_O("聯合新聞網〈諮商心理師：羞愧、自責壓垮被害人〉（被騙後常見羞愧與自責）","https://udn.com/news/story/124490/9055907")
SDES=lambda: _O("設計假設：一般兒童／同儕日常經驗，無外部統計","https://165.npa.gov.tw/",note="無對應外部來源；連結為 165 全民防騙網首頁（泛用）")
_EV={e["id"]:e for e in data["events"]}
def _chain(prev,evs):  # 依序插在 prev 之後；每個新事件所有選項都接下一個
    nx=_nextof(prev); ids=[e["id"] for e in evs]
    for e,n in zip(evs,ids[1:]+[nx]):
        for c in e["choices"]: c["next"]=n
    _rewire(prev,ids[0]); _ins_after(prev,evs); _EV.update({e["id"]:e for e in data["events"]})
def _k(i,a,cat,t,chs,src,**kw): return _card(i,a,cat,t,[_ch(*c[:2],"?",c[2],[],c[3],c[4],c[5]) for c in chs],src,**kw)
V6_NEW=[]
def _addchain(prev,evs): _chain(prev,evs); V6_NEW.extend(e["id"] for e in evs)
# --- (1) 童年／國小／國中日常（13 則；伏筆 flag 於成年事件以 text_variants／outcome_variants 回收）
_addchain("promise_park",[
 _k("c_lost_wallet",6,"純真","夜市人好多。你在烤香腸攤旁邊撿到一個皮夾，裡面有幾張鈔票和一張小朋友的照片。",
  [("交給攤位阿姨",{"人際":4,"心理":3},["kid_honest"],"阿姨用麥克風廣播。一個叔叔跑過來，一直跟你說謝謝。","撿到皮夾交出去","green"),
   ("偷偷收進口袋",{"心理":-3},[],"你把皮夾帶回家。晚上媽媽發現了，牽著你去派出所。警察伯伯沒有罵你。","皮夾被媽媽送去派出所","yellow")],[SKID]),
 _k("c_share_lunch",6,"純真","午餐時間，隔壁的小胖忘了帶便當，一直盯著你的滷蛋。",
  [("分他一半",{"人際":5},["kid_shares"],"他吃得好開心，說明天要帶他阿嬤做的粽子給你。","把滷蛋分給同學","green"),
   ("自己吃完",{"心理":1},[],"你把便當吃完。小胖去福利社買了麵包。","自己吃完便當","green")],[SDES()])])
_addchain("park_reveal",[
 _k("c_pinky_promise",7,"純真","好朋友把他最寶貝的彈珠借你帶回家玩，勾勾手指：「星期一一定要還我喔。」",
  [("星期一準時還",{"人際":5,"心理":2},["kid_kept_promise"],"你一早就把彈珠放進書包。他接過去的時候笑得好大聲。從那天起，你覺得說好的事就要做到。","說到做到還了彈珠","green"),
   ("先玩幾天再說",{"人際":-3},[],"你多玩了三天才還。他沒說什麼，但下課不太找你玩了。","彈珠晚了三天才還","yellow")],[SDES()])])
_addchain("hongbao",[
 _k("c_temple_fair",8,"誘惑","廟口的套圈圈攤，老闆說：「差一點點！再買十個圈，大獎一定是你的。」",
  [("再買十個圈",{"存款":-100,"心理":-2},["kid_near_miss"],"十個圈全都差一點點。大獎那台遊戲機一直穩穩站在最後面。","套圈圈再加碼","yellow"),
   ("夠了，去吃糖葫蘆",{"警覺":3,"心理":2},["checks_first"],"你拿剩下的錢買了糖葫蘆，邊走邊吃，一點也不覺得虧。","不再加碼","green")],[_O("設計假設：「差一點就中」的加碼心理","https://165.npa.gov.tw/",note=_GEN)])])
_addchain("sister_reveal",[
 _k("c_stranger_pickup",9,"陌生人","放學時，一個沒看過的阿姨站在校門口：「你媽媽在忙，叫我來接你喔。」",
  [("問她通關密語",{"警覺":6},["checks_first","kid_family_code"],"阿姨說不出你家的密語，轉身就走了。你跑去找導師，導師打給媽媽，媽媽說她根本沒叫人來。","問了通關密語","green"),
   ("跟她走到路口",{"警覺":4,"心理":-4},["kid_trusts_adult"],"走到路口，剛好遇到導護爸爸叫住你。阿姨一下就不見了。你心臟跳得好快。","差點跟陌生人走","red")],[SKIDCODE]),
 _k("c_lost_kid",9,"純真","菜市場裡，一個比你小的小朋友一直哭，說找不到媽媽。",
  [("陪他去找攤販阿姨",{"人際":5,"心理":3},["kid_helps"],"你牽著他去找賣菜的阿姨。阿姨用大嗓門一喊，他媽媽就跑過來了。","陪迷路小孩找大人","green"),
   ("自己帶他去找",{"人際":3,"警覺":-1},["kid_helps"],"你們繞了兩圈都沒找到，最後還是請攤販幫忙廣播。媽媽說：「下次先找大人。」","自己帶他到處找","yellow")],[SKID])])
_addchain("card_reveal",[
 _k("c_survey_gift",10,"個資","書展門口有人發問卷：「填爸媽手機和住址，就送你一支自動鉛筆。」",
  [("填了拿鉛筆",{"心理":2},["kid_gave_info"],"你拿到一支自動鉛筆。那個月家裡電話多了好幾通推銷。","填了個資換贈品","yellow"),
   ("說要先問媽媽",{"警覺":4},["checks_first"],"那個人笑著說好。媽媽說：「家裡的電話和地址，不要隨便寫給別人。」","先問媽媽","green")],[SPHISH])])
_addchain("group_result",[
 _k("c_chain_msg",11,"謠言","班群傳來一則訊息：「轉傳給十個人，不然會倒楣一整年！」好幾個同學都轉了。",
  [("也轉十個人",{"人際":2,"心理":-1},["kid_forwarded"],"你轉了。隔天老師在班上說，這種訊息常常夾著奇怪的連結。","轉傳了倒楣信","yellow"),
   ("不轉，問老師",{"警覺":4},["checks_first"],"老師說：「不會倒楣的。會轉的人，常常也會轉到壞連結。」","沒有轉傳","green")],[SPHISH]),
 _k("c_online_friend",11,"網友","遊戲裡認識一個網友，說他也 11 歲，想要你的照片和學校名字，「這樣我們才是真的好朋友」。",
  [("先跟爸媽說",{"警覺":6,"人際":2},["checks_first","kid_told_parent"],"爸爸陪你看了對話，說真正的朋友不會要你保密。你們一起把他封鎖了。","把網友的事跟爸媽說","green"),
   ("傳學校名字就好",{"警覺":3,"心理":-4},["kid_trusts_adult"],"你傳了學校名字。他又要照片。你覺得怪怪的，跟媽媽說了。媽媽沒有罵你，抱了你一下。","給了網友學校名字","red")],[SKID])])
_addchain("lend_reveal",[
 _k("c_donation_box",12,"真誠","捷運站出口有人拿著流浪狗照片的募款箱：「一點點就能救一條命。」你口袋裡有午餐錢。",
  [("投五十元",{"存款":-50,"心理":2},["kid_donated"],"你投了五十元，心裡暖暖的。後來老師說，正式募款會有政府的許可字號，下次可以先看。","投了募款箱","yellow"),
   ("找許可字號",{"警覺":5},["checks_first"],"箱子上什麼字號都沒有。你把錢留著，回家上網找了正式的動物收容單位。","先找許可字號","green")],[SDON])])
_addchain("free_gift",[
 _k("c_link_drink",13,"連結","班群有人貼連結：「填手機號碼就送一杯免費飲料！」已經有三個人說領到了。",
  [("填號碼試試",{"心理":-2},["kid_gave_info"],"飲料沒有出現。之後你的手機一直收到奇怪的簡訊。","填了號碼","yellow"),
   ("問誰真的領到",{"警覺":5},["checks_first"],"那三個人都說「好像還沒」。你沒有填。","先問清楚","green")],[SPHISH])])
_addchain("game_trade",[
 _k("c_friend_repay",14,"真誠","畢業旅行前，好朋友跟你借三百塊買紀念品：「月底拿到零用錢就還。」",
  [("借他",{"存款":-300,"人際":3},["kid_lent_friend"],"月底他真的把三百塊放在你桌上，還多了一包乖乖。你覺得朋友之間，就是這樣。","借朋友300元","green"),
   ("說自己也不夠",{"心理":-1},[],"他說沒關係，去跟別人借了。","沒有借","green")],[SDES()]),
 _k("c_grandma_call",14,"家人","阿嬤打給你，聲音在抖：「剛剛有人說你表哥出事了，要我匯錢……」",
  [("先打給表哥",{"警覺":8,"人際":4},["checks_first","kid_verified_for_grandma"],"表哥接了電話，說他正在打球。阿嬤在電話那頭鬆了一口氣，說：「還好有問你。」","幫阿嬤打給表哥","green"),
   ("叫阿嬤先別急",{"警覺":4,"人際":2},["kid_verified_for_grandma"],"你叫阿嬤先別急，自己也慌了。後來舅舅打電話確認，表哥沒事。","陪阿嬤等消息","yellow")],[SGUESS])])
V6OPT=[([i],1,1) for i in ("c_lost_wallet","c_share_lunch","c_temple_fair","c_lost_kid","c_survey_gift","c_chain_msg","c_online_friend","c_donation_box","c_link_drink","c_friend_repay")]
V6OPT[0]=(["c_lost_wallet"],2,1); V6OPT[6]=(["c_online_friend"],2,1)
# c_pinky_promise、c_stranger_pickup、c_grandma_call 為必出（伏筆核心）
# --- (2) 生活里程碑具象化（加場景文字，不改判定）
_EV["part_time"]["text"]="高二暑假，你在巷口的飲料店打工，一小時的時薪寫在員工守則第一頁。手搖杯搖到手腕痠，兩個月過去，"+_EV["part_time"]["text"].replace("暑假打工做了兩個月，","")
_EV["part_time"]["sources"]=_EV["part_time"]["sources"]+[SLAB]
_EV["student_loan"]["text"]="上大學了。你拖著行李箱第一次離家，坐了三個小時的車到外地。註冊單上的學費數字很大，你盯著看了很久。"
_EV["rent"]["text"]="大三搬出宿舍，你在學校後面租了一間六坪套房：一張床、一張書桌、一台會滴水的冷氣。房東太太說：「押金兩個月，退租看狀況。」一年後退租時，房東說牆要重新粉刷，押金要扣一大半。"
_EV["rent"]["sources"]=_EV["rent"]["sources"]+[SRENT]
_addchain("rent",[
 _k("a_move_out",21,"生活","畢業前搬家。你把所有家當塞進六個紙箱，請朋友開車載。新房間比舊的小，但窗外看得到一棵樹。",
  [("自己搬，請朋友吃飯",{"存款":-1500,"人際":4},["helped_by_friend"],"朋友搬到滿身汗，你請他吃了一頓熱炒。他說：「以後你搬家都叫我。」","朋友幫忙搬家","green"),
   ("找搬家公司估價",{"存款":-3000,"警覺":3},["checks_first"],"你找了兩家估價、看了合約才請人搬。多花了一點，但東西一件沒少。","比價後請人搬家","green")],[SRENT])])
_addchain("mlm",[
 _k("a_first_salary",23,"生活","第一份正職的薪水入帳了。你在提款機前看著那串數字，想起高中搖飲料的暑假。",
  [("請爸媽吃飯",{"存款":-3000,"人際":5,"心理":5},["first_salary_shared"],"媽媽一直說太破費，但吃完偷偷把菜單拍下來傳給阿姨。","第一份薪水請爸媽","green"),
   ("先存一半",{"存款":5000,"心理":3,"警覺":2},["first_salary_saved"],"你開了一個新帳戶，把一半的薪水轉進去，取名叫「不准動」。","第一份薪水存一半","green")],[SLAB])])
# --- (3) 純真與真誠：成年後的善意、因真誠而被騙的情感重量
_addchain("insurance",[
 _k("a_help_stranger",27,"真誠","下班的捷運站，一位看起來很狼狽的大哥攔住你：「我錢包被偷了，可以借我兩百塊坐車回家嗎？我會還你。」他把手機號碼寫給你。",
  [("借他兩百",{"存款":-200,"心理":1},["adult_helped_stranger"],"他一直鞠躬。那支號碼後來打不通。一個月後，你在另一站又看見他，攔著另一個人說同一段話。你不是氣那兩百塊，是氣自己當時那麼相信。","借了兩百塊","yellow"),
   ("陪他去服務台",{"警覺":5,"人際":2},["checks_first"],"你陪他走到服務台，說站務人員可以協助。他說不用了，轉身走掉。你不確定自己是不是太多心。","陪他去服務台","green")],[S165])])
_EV["a_help_stranger"]["text_variants"]=[{"when":{"flags_all":["kid_helps"]},"text":"下班的捷運站，一位看起來很狼狽的大哥攔住你：「我錢包被偷了，可以借我兩百塊坐車回家嗎？」你想起小時候在菜市場牽著迷路小孩找媽媽的那天。","source":"原創情境（伏筆回收：c_lost_kid）"}]
# 因真誠而上當：在既有借錢／投資邀約事件加伏筆變體（不改數值）
def _tv(eid,flag,text): _EV[eid].setdefault("text_variants",[]).insert(0,{"when":{"flags_all":[flag],"flags_none":[]},"text":text,"source":"原創情境（伏筆回收，v6）"})
_tv("lend","kid_kept_promise","好朋友說急用，跟你借三萬，「下個月一定還」。你從小就是說好就做到的人，所以你也相信，他說的「一定」是真的。")
_tv("lend5","kid_shares",_EV["lend5"]["text"]+"你想起自己以前也把滷蛋分給別人。")
for c in _EV["lend"]["choices"]:
    if "lent_money_lost" in c["flags"]["set"] or c["effects"].get("存款",0)<0:
        c.setdefault("outcome_variants",[]).append({"when":{"flags_all":["kid_lent_friend"],"flags_none":[]},"text":(c.get("outcome_text") or "")+"國中那年借出去的三百塊，朋友月底就還了。你一直以為，朋友之間就是這樣。","source":"原創情境（伏筆回收：c_friend_repay）"})
if "elder" in _EV:
    _tv("elder","kid_verified_for_grandma","爸媽打電話來，聲音很急。你想起十四歲那年，阿嬤在電話裡發抖的聲音。")
if "fake_police" in _EV:
    _tv("fake_police","kid_trusts_adult",_EV["fake_police"]["text"]+"對方的語氣，像極了小時候那些「大人說的就是對的」。")
# 被騙後：還要不要相信人（只有 lost_money 者經 family_talk 才會到）
_addchain("family_talk",[
 _k("a_still_kind",37,"真誠","那件事過了很久。有一天，同事說他媽媽住院，問能不能先借你五千。你的手停在手機上。",
  [("先去醫院看看",{"心理":6,"人際":5,"警覺":4},["still_trusts_checks"],"你帶著水果去醫院，真的看到他媽媽。你借了錢，他兩週後就還了。你發現，相信人和先確認，可以同時存在。","先確認再幫忙","green"),
   ("從此不借任何人",{"心理":-3,"人際":-4},["closed_heart"],"你說了抱歉。他說沒關係。你知道自己不是小氣，只是很怕再痛一次。被騙不是你的錯。","不敢再借錢給人","yellow")],[SPSY])])
_EV["a_still_kind"]["text_variants"]=[{"when":{"flags_all":["kid_kept_promise"],"flags_none":[]},"text":"那件事過了很久。你一直是守約的人，被騙那次最痛的不是錢，是你發現別人不一定跟你一樣。有一天，同事說他媽媽住院，問能不能先借你五千。","source":"原創情境（伏筆回收：c_pinky_promise）"}]
# 數值微調（v6 最小修正）：新事件不設 checks_first、警覺增幅上限 2，避免拉低各線 COLLAPSE／CUT_OFF
for _i in V6_NEW:
    for _c in _EV[_i]["choices"]:
        _c["flags"]["set"]=[f for f in _c["flags"]["set"] if f!="checks_first"]
        if _c["effects"].get("警覺",0)>2: _c["effects"]["警覺"]=2
        for _s in ("心理","人際"):
            if _c["effects"].get(_s,0)>0: _c["effects"][_s]=min(_c["effects"][_s],1)
data["meta"]["v6_additions"]={"date":"2026-10-23","new_events":V6_NEW,"note":"童年 13 則（10 則隨機池、3 則必出伏筆）＋成年里程碑 a_move_out/a_first_salary＋真誠線 a_help_stranger/a_still_kind；伏筆以 text_variants/outcome_variants 回收"}
# ===== v1.1 童年事件池（steer 9）：每年齡區間只抽部分事件、同齡順序隨機、情境/結果變體；核心教學事件必出 =====

def _evs(): return {e["id"]:e for e in data["events"]}
def _idx(i): return [e["id"] for e in data["events"]].index(i)
def _preds(i): return [(e,c) for e in data["events"] for c in e["choices"] if c["next"]==i]
def _router(rid,age,choices):
    return {"id":rid,"age":age,"category":"系統","router":True,"random":True,"text":"（事件池抽選，不顯示）","presentation":"timeskip",
            "choices":[dict(c,text=f"抽選{k+1}") for k,c in enumerate(choices)],"sources":_POOL_SRC}
def _rc(nxt,fl=None): return {"text":"（抽選）","effects":{},"next":nxt,"flags":{"set":fl or [],"require":[]},"grid":"green","outcome_text":"（系統抽選，不顯示）","log_text":"（事件池）"}
_POOL_SRC=[{"name":"設計假設：事件池抽選（遊戲機制，非史實資料）","url":"https://165.npa.gov.tw/"}]
POOL={"optional":[],"swaps":[],"variants":{},"core":["hongbao","sister_repay","sister_reveal","lend5","lend_reveal","first_phone","free_gift","otp_reveal","part_time"]}
# --- 1) 情境變體：(事件id, [(變體文字, {choice_idx:(effects覆寫, outcome覆寫)})...]) 變體0=原文
VAR={
 "shot":[("健康檢查要抽血。爸爸說：「一下下就好，不會痛。」護士阿姨已經在綁止血帶了。",{}),
         ("阿嬤帶你去打流感疫苗，說：「不痛不痛，打完帶你去吃冰。」護理師阿姨已經拿起針了。",{})],
 "lend5":[("隔壁同學說：「借我10塊買冰淇淋，明天一定還你！」",{0:({"存款":-10,"人際":3},None)})],
 "rent_deposit":[("網路上看到一間便宜套房。房東說鑰匙放在超商寄貨櫃，先付一個月租金就把取件碼給你。",{0:({"存款":-12000,"心理":-5},None)})],
 "_drop_school_gate":[("放學時，公園門口有人在賣毛茸茸的染色小雞。一隻二十五塊，旁邊圍了一圈小朋友。",{0:({"存款":-25,"心理":5},None)}),
                ("廟口夜市有攤子在賣毛茸茸的染色小雞。一隻三十塊，表弟已經蹲在紙箱前不走了。",{0:({"存款":-30,"心理":5},"粉紅色的小雞在紙盒裡啾啾叫，表弟跟你一路捧著回家。三十塊零用錢沒了。")})],
 "card_trade":[("隔壁班的同學拿出一張亮晶晶的「超限量卡」，說只要用你5張卡來換，「今天不換就給別人」。",{}),
               ("表哥拿出一張亮晶晶的「超限量卡」，說只要用你5張卡來換，「我是看你是表弟才換」。",{})],
 "lottery":[("巷口雜貨店的抽抽樂，5塊一抽，集滿「黑暗大法師」就能換怪獸對打機。你已經有「黑暗大法」了。",{0:({"存款":-200,"心理":-5},None)}),
            ("文具店的抽抽樂漲到10塊一抽，集滿「黑暗大法師」就能換怪獸對打機。你已經有「黑暗大法」了。",{0:({"存款":-400,"心理":-6},"紙條一張張撕開，還是沒有那個「師」。十塊十塊地，存了兩個月的零用錢不見了。")})],
 "honesty":[("走廊的窗戶破了。老師說：「是誰？說實話就不罰你。」其實是你踢的球。",{}),
            ("音樂教室的窗戶破了。老師說：「是誰？說實話就不罰你。」其實是你踢的球。",{})],
 "group_buy":[("社團學長說要團購限定公仔，先收錢，下週交貨。",{}),("補習班同學說要團購限定公仔，先收錢，下週交貨。",{})],
 "quiz":[("補習班老師說：「明天只是小考，不用緊張。」",{}),("班導說：「明天只是隨堂考，不用緊張。」",{})],
 "game_trade":[("遊戲公會裡有人私訊你：「交易平台手續費好貴，我們私下交易比較便宜。」另一個網友則說家裡斷了生活費，請你幫忙買點數。",{1:({"存款":-2500,"心理":-7},None)}),
               ("同學轉介一個網友：「交易平台手續費好貴，我們私下交易比較便宜。」另一個網友則說家裡斷了生活費，請你幫忙買點數。",{1:({"存款":-3500,"心理":-8},"寶物送出去後，你去查帳戶，那筆錢始終沒有入帳。同學說他也不認識那個人。")})],
}
VAR.pop("_drop_school_gate",None)
_E=_evs()
for eid,vs in VAR.items():
    e=_E[eid]; fl=[f"v_{eid}_{k+1}" for k in range(len(vs))]
    e["text_variants"]=[{"when":{"flags_all":[fl[k]]},"text":t} for k,(t,_) in enumerate(vs)]
    nchoice=len(e["choices"]); add=[]
    for k,(t,ov) in enumerate(vs):
        for ci,(eff,out) in ov.items():
            o=e["choices"][ci]; o["flags"]["require"]=list(o["flags"]["require"])+[f"!{fl[k]}"]
            c=json.loads(json.dumps(o)); c["effects"]=eff; c["flags"]["require"]=[r for r in c["flags"]["require"] if not r.startswith("!v_")]+[fl[k]]
            if out: c["outcome_text"]=out
            c["variant_of"]=ci; add.append(c)
    e["choices"]+=add
    POOL["variants"][eid]={"scene":len(vs)+1,"amount_variants":sum(1 for _,ov in vs if ov)}
# --- 2) 可略過區塊：(區塊事件ids, 出現機率權重 go:skip)
VAR.pop("_drop_school_gate",None)
OPT=V6OPT+[(["shot"],3,1),(["sticker_trade","sticker_result"],1,1),(["toy_seller","toy_result"],1,1),(["teacher_permission","exam_result"],1,1),
     (["points_help","points_result"],1,1),(["customs_fee","customs_result"],1,1),(["rent_deposit","rent_result"],1,1),(["fake_insurance"],1,1),(["gold_delivery"],1,1),(["group_buy","group_result"],2,1),
     (["part_time_ad","ad_result"],2,1),(["quiz"],2,1),(["game_trade"],3,1),(["pe_class"],2,1)]
# --- 3) 同齡順序互換
SWAP=[("honesty","slurpee")]
for a,b in SWAP:
    E2=_evs(); A,B=E2[a],E2[b]; assert A["age"]==B["age"] and all(c["next"]==b for c in A["choices"])
    nxt=B["choices"][0]["next"]; assert all(c["next"]==nxt for c in B["choices"])
    B2=json.loads(json.dumps(B)); B2["id"]=b+"__swap"
    A2=json.loads(json.dumps(A)); A2["id"]=a+"__swap"
    for c in B2["choices"]: c["next"]=A2["id"]
    for c in A2["choices"]: c["next"]=nxt
    rid=f"pool_order_{a}"; R=_router(rid,A["age"],[_rc(a),_rc(B2["id"])])
    for e,c in _preds(a): c["next"]=rid
    i=_idx(a); data["events"][i:i]=[R]; j=_idx(b)+1; data["events"][j:j]=[B2,A2]
    POOL["swaps"].append({"router":rid,"orders":[[a,b],[b,a]],"note":"互換時使用 __swap 副本事件；以原 id 判定的成就僅在原順序觸發"})
_E=_evs()
for ids,wg,ws in OPT:
    first,last=_E[ids[0]],_E[ids[-1]]
    after={c["next"] for c in last["choices"]}; assert len(after)==1,(ids,after); after=after.pop()
    fl=[f"v_{first['id']}_{k+1}" for k in range(len(VAR.get(first["id"],[])))]
    gos=[_rc(first["id"])]+[_rc(first["id"],[f]) for f in fl]
    # 變體平均分配到 go 權重：每個變體各重複 wg 次以維持 go:skip 比例
    ch=[c for c in gos for _ in range(wg)]+[_rc(after,[f"skip_{first['id']}"]) for _ in range(ws*len(gos))]
    rid="pool_"+first["id"]; R=_router(rid,first["age"],ch)
    for e,c in _preds(first["id"]): c["next"]=rid
    i=_idx(first["id"]); data["events"][i:i]=[R]
    POOL["optional"].append({"block":ids,"p_appear":round(wg/(wg+ws),2),"router":rid})
# --- 4) 必出但有變體的事件：前面插 router 只抽變體
_E=_evs()
for eid in VAR:
    if any(eid==o[0][0] for o in OPT): continue
    fl=[f"v_{eid}_{k+1}" for k in range(len(VAR[eid]))]
    rid="pool_var_"+eid; R=_router(rid,_E[eid]["age"],[_rc(eid)]+[_rc(eid,[f]) for f in fl])
    for e,c in _preds(eid):
        if e["id"]!=rid: c["next"]=rid
    i=_idx(eid); data["events"][i:i]=[R]
data["meta"].setdefault("event_pool",{}).update({"childhood":POOL,
 "rule":"v1.1：童年每個年齡區間只抽部分事件（optional 區塊各有出現機率）、同齡事件順序隨機（swaps）、同一事件 2–3 種情境變體（場景、人物、金額微調）並附對應結果文字；核心教學事件（紅包、姐姐借錢、借同學錢、手機綁卡、送禮驗證碼、打工）必出，因為後續有結局與跨線依賴。router 事件為系統抽選、不顯示、不計入人生格子。抽選機率與變體金額為設計假設。"})

# v1.2：新跨線 flag 登記（只加插話「你想起以前…」，不改數值）
_CLF=data["meta"]["cross_line_flags"]
for _k,_v in {"fake_permission":"小時候信了「老師說可以」。車手線 account_used 多一則回憶插話",
  "fake_sticker":"小時候換到假貼紙。網購線 ticket 多一則「限量」回憶插話","fake_toy":"小時候買到假玩具。網購線 cheap_item 多一則回憶插話",
  "paid_group_buy":"小時候團購先付錢。網購線 cheap_item 多一則「先付款」回憶插話","chased_lottery":"小時候追抽獎。投資線 temptation 多一則回憶插話",
  **{f:"車手入口變體（pool_mule_variant 抽選）。車手線 job_offer 多一則對應插話" for f in ["mv_salary_card","mv_delivery_code","mv_kiosk","mv_loan_beautify","mv_sim"]}}.items():
    _CLF.setdefault(_k,_v)
from common import set_title; set_title(data)  # v6
json.dump(data,open("script-life.json","w"),ensure_ascii=False,indent=2)
print(len(E),"events",len(EN),"endings")
