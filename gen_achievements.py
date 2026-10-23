"""gen_achievements.py：產生 achievements.json（成就系統 v1）。
來源一律從現有 script-*.json 的事件/結局 sources 自動帶入，不另寫數據；不含任何達成率。"""
import json
LINES=["life","mule","shopping","investment","romance","marriage","parent"]
S={l:json.load(open(f"script-{l}.json")) for l in LINES}
EV={l:{e["id"]:e for e in S[l]["events"]} for l in LINES}
EN={l:{e["id"]:e for e in S[l]["endings"]} for l in LINES}
LN={"life":"人生","mule":"車手線","shopping":"網購線","investment":"投資線","romance":"交往線","marriage":"婚姻線","parent":"家長篇"}
def src_list(ss):
    out=[{"name":s.get("name",""),"url":s.get("url")} for s in ss if s.get("name")]
    return out[:2]
def src_end(l,eid): return [{"ref":f"{l}:{eid}","from":"ending.sources",**s} for s in src_list(EN[l][eid].get("sources",[]))]
def src_ev(l,evid,fallback_end=None):
    s=src_list(EV[l][evid].get("sources",[]))
    if s: return [{"ref":f"{l}:{evid}","from":"event.sources",**x} for x in s]
    return src_end(l,fallback_end)
def ch(l,evid,i): return {"line":l,"event":evid,"choice_index":i,"text":EV[l][evid]["choices"][i]["text"]}
A=[]
def add(id,cat,name,desc,unlock,source,hidden=False,tone="positive"):
    assert len(name)<=10,name
    A.append(dict(id=id,category=cat,name=name,description=desc,unlock=unlock,hidden=hidden,tone=tone,source=source))
def U(endings=(),flags=(),choices=(),scope="run",any_endings=(),forbids_flags=(),forbids_endings=()):
    return {"scope":scope,"requires_endings":list(endings),"requires_any_endings":list(any_endings),"requires_flags":list(flags),"requires_choices":list(choices),"forbids_flags":list(forbids_flags),"forbids_endings":list(forbids_endings)}

# 1) 結局圖鑑：每個結局一個 + 收集全線
NEG={"mule":{"END_CONVICTED","END_RECORD","END_CUT_OFF","END_ACCOUNT"},"shopping":{"END_CS_DRAINED","END_TICKET_LOST","END_SMALL_FEE","END_SILENT_COLLAPSE"},
     "investment":{"END_ALL_LOST","END_BROKE","END_DEBT","END_COLLAPSE","END_FAMILY_RIFT"},"life":{"END_LIFE_STRETCHED","END_LIFE_HONGBAO_GONE","END_LIFE_RECORD","END_LIFE_HALTED"},
     "romance":{"END_RM_COLLAPSE","END_RM_DEEP"},"marriage":{"END_MR_COLLAPSE","END_MR_SILENT","END_MR_PAID"},"parent":{"END_PA_COLLAPSE","END_PA_HUSH","END_PA_SILENT"}}
SERIOUS={"END_CONVICTED","END_RECORD","END_CUT_OFF","END_COLLAPSE","END_SILENT_COLLAPSE","END_FAMILY_RIFT","END_LIFE_RECORD","END_LIFE_HALTED","END_RM_COLLAPSE","END_MR_COLLAPSE","END_PA_COLLAPSE"}
SHORT={"life":"人生","mule":"車手","shopping":"網購","investment":"投資","romance":"交往","marriage":"婚姻","parent":"家長"}
for l in LINES:
    for n_,(eid,e) in enumerate(EN[l].items(),1):
        t=e.get("title") or eid
        neg=eid in NEG[l]
        if eid in SERIOUS: d=f"圖鑑記錄：{LN[l]}結局「{t}」。這是真實案例裡會發生的後果，請看完案件卡與求助資源。"
        elif neg: d=f"圖鑑記錄：{LN[l]}結局「{t}」。回顧裡有你錯過的破綻。"
        else: d=f"走到{LN[l]}結局「{t}」。"
        add(f"ACH_END_{l.upper()}_{eid.replace('END_','')}","ending_codex",f"{SHORT[l]}圖鑑 No.{n_}",d,
            U(endings=[f"{l}:{eid}"],scope="collection"),src_end(l,eid),hidden=True,tone="serious" if eid in SERIOUS else ("record" if neg else "positive"))
    add(f"ACH_CODEX_{l.upper()}_ALL","ending_codex",f"{LN[l]}全收錄",f"在不同輪裡看過{LN[l]}全部 {len(EN[l])} 個結局（圖鑑收集，不代表鼓勵走壞結局）。",
        U(endings=[f"{l}:{k}" for k in EN[l]],scope="collection"),src_end(l,next(iter(EN[l]))),tone="record")
add("ACH_CODEX_ALL","ending_codex","全圖鑑完成","所有線、所有結局都已記錄在圖鑑裡。",
    U(endings=[f"{l}:{k}" for l in ["life","mule","shopping","investment"] for k in EN[l]],scope="collection"),[{"ref":"all","from":"ending.sources","name":"各結局案件卡來源（見各線結局）","url":None}],tone="record")
add("ACH_CODEX_ALL_V10","ending_codex","七線全圖鑑","人生與六條詐騙線（含交往、婚姻、家長篇）的所有結局都已記錄。",
    U(endings=[f"{l}:{k}" for l in LINES for k in EN[l]],scope="collection"),[{"ref":"all","from":"ending.sources","name":"各結局案件卡來源（見各線結局）","url":None}],tone="record")

# 2) 破綻辨識：關鍵事件的正確選擇
R=[("ACH_SPOT_SHOT","第一次發問","打針前先問「真的不痛嗎？」——習慣先確認。","life","shot",1,None),
   ("ACH_SPOT_SISTER","當面數清楚","姐姐還錢時，你當場算了一下。","life","sister_repay",1,None),
   ("ACH_SPOT_OTP","驗證碼不給","有人說要送遊戲禮物，要你傳驗證碼——你沒傳。","life","free_gift",1,None),
   ("ACH_SPOT_GAMETRADE","只走平台","遊戲交易只在平台內進行。","life","game_trade",0,None),
   ("ACH_SPOT_WAGE","留下證據","打工被欠薪，你留紀錄、申請調解。","life","part_time",0,None),
   ("ACH_SPOT_RENT","點交拍照","入住前拍照錄影、簽點交單。","life","rent",0,None),
   ("ACH_SPOT_MLM","先問清楚","朋友找你「聊個機會」，你先問清楚是什麼公司。","life","mlm",0,None),
   ("ACH_SPOT_LEND","白紙黑字","借錢給朋友時，用訊息寫清楚。","life","lend",0,None),
   ("ACH_SPOT_CONTRACT","帶回家比","業務催你當場簽，你把條款帶回家比較。","life","insurance",0,None),
   ("ACH_SPOT_JOB","查統編","看到條件太好的工作，先查公司統編。","mule","job_ad",0,"END_REFUSE"),
   ("ACH_SPOT_ACCOUNT","帳戶不外借","對方要你的帳戶，你拒絕了。","mule","job_offer",0,"END_REFUSE"),
   ("ACH_SPOT_FRIENDWARN","聽進勸告","朋友提醒後，你決定不做了。","mule","friend_warn",0,"END_REFUSE"),
   ("ACH_SPOT_SELFREPORT","主動說明","發現帳戶被拿去用，你停下來到派出所說明。","mule","account_used",0,"END_ACCOUNT"),
   ("ACH_SPOT_FAMILYTALK","說出實情","家人察覺不對勁時，你說了實話。","mule","family_notice",0,"END_STOPPED_ALONE"),
   ("ACH_SPOT_TICKET","放大看截圖","讓票前先仔細看截圖。","shopping","ticket",1,"END_SAFE"),
   ("ACH_SPOT_OFFICIAL","官方管道","票券只走官方轉售。","shopping","ticket",0,"END_SAFE"),
   ("ACH_SPOT_LINK","不點連結","便宜商品要你點連結付運費，你改從官方 App 下單。","shopping","cheap_item",0,"END_SAFE"),
   ("ACH_SPOT_CS","自己查號","「客服」來電說設錯分期，你掛斷後自己查號回撥。","shopping","fake_cs",0,"END_SAFE"),
   ("ACH_SPOT_VIDEO","先視訊","網友不肯視訊，你封鎖並打 165 查詢。","investment","date_refuse_video",0,"END_EARLY"),
   ("ACH_SPOT_GROUP","退群檢舉","投資群組老師報明牌，你退群並檢舉。","investment","ad_group",0,"END_EARLY"),
   ("ACH_SPOT_WITHDRAW","停止匯款","出金前被要求先繳費，你停下來去報案。","investment","withdraw_block",0,"END_SMALL_LOSS"),
   ("ACH_SPOT_GUESSWHO","打給本人","「猜猜我是誰」來借錢，你直接打給本人確認。","life","guess_who",0,None),
   ("ACH_SPOT_FAKEPOLICE","警察不要你保密","自稱警察要你配合保密，你掛斷打 165。","life","fake_police",0,None),
   ("ACH_SPOT_RM_SISTER","說給姐姐聽","網友一直不見面，你跟姐姐聊了這件事。","romance","rm_excuse",0,"END_RM_SISTER"),
   ("ACH_SPOT_RM_PHOTO","搜一下照片","對方開口要錢，你先搜尋他的照片。","romance","rm_ask_invest",0,"END_RM_CHECKED"),
   ("ACH_SPOT_RM_PHOTO_L","借錢前先查","對方說要周轉，你先搜尋他的照片。","romance","rm_ask_loan",0,"END_RM_CHECKED"),
   ("ACH_SPOT_RM_PHOTO_S","醫藥費先查","對方說家人生病，你先搜尋他的照片。","romance","rm_ask_sick",0,"END_RM_CHECKED"),
   ("ACH_SPOT_RM_165","被說不信任也查","被說「不信任我」，你還是打了 165。","romance","rm_push",0,"END_RM_HOTLINE"),
   ("ACH_SPOT_MR_CREDIT","查自己的信用","收到沒見過的催繳信，你申請自己的信用報告。","marriage","mr_letter",0,"END_MR_DIVORCE"),
   ("ACH_SPOT_MR_RECORD","查婚姻紀錄","另一半要錢又要借證件，你先查戶籍與婚姻紀錄。","marriage","mr_asks",0,"END_MR_ANNUL"),
   ("ACH_SPOT_PA_GAME","陪他去報案","孩子交出驗證碼，你陪他一起去報案。","parent","pa_game",1,"END_PA_OPEN"),
   ("ACH_SPOT_PA_THREAT","不付錢，報警","孩子被威脅要錢，你陪他報警，沒有付錢。","parent","pa_threat",1,"END_PA_OPEN"),
   ("ACH_SPOT_COUNTER","對行員說實話","臨櫃時，你跟行員說了實情。","investment","bank_counter",0,"END_ALL_LOST")]
# v1.2 additive：童年事件池修正與成人新事件的破綻成就（事件可能未抽到，屬收集型）
R+=[("ACH_SPOT_STICKER","先給人看看","交換貼紙前先拿給哥哥看。","life","sticker_trade",1,None),
   ("ACH_SPOT_TOY","回家再決定","陌生人賣玩具，你先回家問。","life","toy_seller",1,None),
   ("ACH_SPOT_PERMISSION","親自問老師","有人說「老師說可以」，你直接去問老師。","life","teacher_permission",1,None),
   ("ACH_SPOT_POINTS","點數不代收","有人要你幫忙收點數——你拒絕了。","life","points_help",1,None),
   ("ACH_SPOT_RENT_DEPOSIT","先看房再付","租屋要先付訂金，你堅持先看房。","life","rent_deposit",1,None),
   ("ACH_SPOT_CUSTOMS","掛斷自己查","包裹被扣要付費？你掛斷後自己查。","life","customs_fee",1,None),
   ("ACH_SPOT_INSURANCE","打回原公司","保單通知可疑，你打給原本的保險公司確認。","life","fake_insurance",0,None),
   ("ACH_SPOT_GOLD","先查證再說","對方要你把金條交給專人，你先查證。","life","gold_delivery",1,None),
   ("ACH_SPOT_LOANUSE","自己規劃","借來的錢，你自己規劃用途。","life","loan_use",0,None),
   ("ACH_SPOT_SLEEP","說出來","睡不著時，你找人聊聊或打專線。","life","sleep_issue",0,None)]
for id,n,d,l,ev,i,fb in R:
    add(id,"red_flag",n,d,U(choices=[ch(l,ev,i)],scope="run"),src_ev(l,ev,fb))

# 3) 人生成就（同一輪內判定；用既有 flags / 結局）
add("ACH_LIFE_CLEAN40","life","四十不受騙","活到 40 歲，遇到的每條詐騙線都安全離開，也沒有因詐騙損失金錢。",
    U(any_endings=[f"life:{k}" for k in EN["life"]],forbids_flags=["life:scam_money_lost","life:criminal_record"],
      forbids_endings=[f"{l}:{k}" for l in ("mule","shopping","investment") for k in NEG[l]]),
    src_end("life","END_LIFE_STEADY"))
add("ACH_LIFE_ALL3_SAFE","life","三關全過","同一輪人生遇到三條詐騙線，三條都安全離開。",
    U(endings=["mule:END_REFUSE","shopping:END_SAFE","investment:END_EARLY"]),src_end("mule","END_REFUSE")+src_end("shopping","END_SAFE"),hidden=True)
add("ACH_LIFE_PASSPHRASE","life","通關密語","爸媽靠家庭通關密語擋下假親友訊息。",
    U(flags=["life:family_passphrase"]),src_ev("life","elder"))
add("ACH_LIFE_TOLD","life","說出口了","被騙時向家人坦白，讓損失停下來。",
    U(choices=[ch("investment","pressure",0)]),src_ev("investment","pressure","END_SMALL_LOSS"))
add("ACH_LIFE_RESCUED","life","有人拉一把","帳戶出事後，身邊有人陪你處理。",U(endings=["mule:END_RESCUED"]),src_end("mule","END_RESCUED"))
add("ACH_LIFE_BANKSAVED","life","行員攔下","臨櫃時被行員攔下，沒再把錢交出去。",U(flags=["investment:bank_saved"]),src_ev("investment","bank_counter","END_ALL_LOST"))
add("ACH_LIFE_REPORTED","life","報案存證","受害後選擇報案、凍結帳戶，沒有一個人撐著。",U(flags=["shopping:reported"]),src_ev("shopping","aftermath","END_CS_DRAINED"))
add("ACH_LIFE_EVIDENCE","life","證據習慣","人生中養成保留紀錄的習慣。",U(flags=["life:evidence_habit"]),src_ev("life","rent"))
add("ACH_LIFE_HONGBAO","life","拿回存摺","長大後，紅包真的存在你的存摺裡。",U(endings=["life:END_LIFE_HONGBAO_SAVED"]),src_end("life","END_LIFE_HONGBAO_SAVED"),hidden=True)
add("ACH_LIFE_BROKE_CYCLE","life","不再重複","當年被責怪的你，這次先抱住了孩子。",U(endings=["parent:END_PA_BROKE_CYCLE"]),src_end("parent","END_PA_BROKE_CYCLE"),hidden=True)
add("ACH_LIFE_CLEAN50","life","五十不受騙","活到 50 歲，交往、婚姻、家長篇與其他詐騙線都安全度過，也沒有因詐騙損失金錢。",
    U(any_endings=[f"life:{k}" for k in EN["life"]],forbids_flags=["life:scam_money_lost","life:criminal_record","life:life_halted"],
      forbids_endings=[f"{l}:{k}" for l in LINES if l!="life" for k in NEG[l]]),src_end("life","END_LIFE_STEADY"),hidden=True)
add("ACH_LIFE_HALTED_SEEN","life","停下來也沒關係","你看過「停下來」這個結局。心累的時候，可以打 1925、1995，或找身邊的人說。",
    U(endings=["life:END_LIFE_HALTED"],scope="collection"),src_end("life","END_LIFE_HALTED"),hidden=True,tone="serious")
add("ACH_LIFE_OWNACCOUNT","life","自己的戶頭","小時候請爸媽陪你開了自己的帳戶。",U(choices=[ch("life","hongbao",1)]),src_ev("life","hongbao"))
# v6：CLEAN40 需實際活到 40 歲（HALTED 提早結束者不算）
for _a in A:
    if _a["id"]=="ACH_LIFE_CLEAN40": _a["unlock"]["min_age_lived"]=40
json.dump({"version":"1.0","note":"source 皆自動引用 script-*.json 既有事件/結局來源；不含達成率等統計數字。","achievements":A},open("achievements.json","w"),ensure_ascii=False,indent=1)
from collections import Counter;print("achievements",len(A),Counter(a["category"] for a in A))
