"""三條線共用：v3 正規化（verified 布林、url 非 null、stat_flags、red_flag_texts）。"""
import json
HL=[{"name":"165全民防騙網（警政署，撥打165）","url":"https://165.npa.gov.tw/"},
    {"name":"1925安心專線（衛福部心理健康司，24小時免付費）","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html"}]
COUNTY_SRC={"name":"縣市池依據：年度縣市分布（韭點開始整理165資料）","url":"https://fromnineon.com/data/taiwan-fraud-statistics/","verified":True,"verify_note":"年度縣市分布：165 儀表板未提供此期間數字，尚無官方原始來源"}
STAT_FLAGS=[
 {"flag":"savings_depleted","stats":{"存款":{"lte":0}},"text":"你的存款歸零了。"},
 {"flag":"mental_collapse","stats":{"心理":{"lte":20}},"text":"長期的壓力讓你的心理狀態跌到谷底（心理≤20）。"},
 {"flag":"isolated","stats":{"人際":{"lte":15}},"text":"你和身邊的人越來越疏遠，沒有人能拉你一把（人際≤15）。"},
 {"flag":"has_support","stats":{"人際":{"gte":20}},"text":"身邊還有願意幫你的人（人際≥20）。"}]
def _norm(o):
    if isinstance(o,dict):
        if "url" in o and o["url"] is None: raise ValueError(f"url is null: {o}")
        v=o.get("verified")
        if isinstance(v,str):
            o["verify_note"]=v; o["verified"]=not v.startswith("待核實")
        for x in o.values(): _norm(x)
    elif isinstance(o,list):
        for x in o: _norm(x)
def finalize(data,red_flag_texts):
    data["meta"]["version"]="0.3"
    data["meta"]["engine_notes"]=("next=='__EVAL__' 時：先依 ending_rules.stat_flags 依數值設定 flag，再依 priority 判定結局。"
      "結局畫面：顯示 reason_texts 中玩家擁有之 flag 的說明；『你錯過的破綻』＝玩家擁有的 missed_* flag 依 red_flag_texts 逐條顯示，若無則顯示 missed_red_flags（通用版）。數值套用後夾在 min/max。"
      "初始存款＝init 值×(1+family.存款_mod)；family 其他數值為加減。")
    data["ending_rules"]["stat_flags"]=STAT_FLAGS
    data["red_flag_texts"]=red_flag_texts
    for e in data["events"]:
        if not e["sources"]: raise ValueError(e["id"])
    _norm(data)
    return data

# ---- 165 打詐儀表板（官方）截圖核對：儀表板更新日期 115-10-23；截圖在 165dashboard/*.webp ----
DB="https://165dashboard.tw/"
NO_OFFICIAL="165 儀表板未提供此期間數字，尚無官方原始來源"
def _d(label,value,unit,period,shot,note="2026-10-23 依儀表板截圖讀圖核對（官方來源）",**k):
    return {"label":label,"value":value,"unit":unit,"period":period,"verified":True,
            "verify_note":note+f"；截圖 165dashboard/{shot}","source":DB,**k}
DASH_SRC={"name":"165打詐儀表板（內政部警政署，官方；更新日期115-10-23，依瀏覽器截圖讀數）","url":DB,"verified":True,
          "verify_note":"前端渲染，數字依 2026-10-23 瀏覽器截圖讀圖；儀表板只提供單日與月資料（115-09、115-10），沒有年度總數、年齡分布或每件平均損失"}
DASH_MONTH=[
 _d("全國詐騙案件受理數",10775,"件","115年9月（2026-09）全月","05_monthly_115-09_summary.webp",prev="115年8月 10,652件，+1.2%（+123件）"),
 _d("全國詐騙財產損失",39.35723,"億元","115年9月（2026-09）全月","05_monthly_115-09_summary.webp",display="39億3,572.3萬",prev="115年8月 41億757.7萬，-4.2%"),
 _d("趨勢圖橫幅：較113年8月受理數減少43%、財損減少68%","敘述","","115年9月 對比 113年8月","03_trend_chart_113-08_to_115-09.webp"),
 _d("每十萬人受理數最多縣市：新竹市",55.3,"件/十萬人","115年9月全月","05_monthly_115-09_summary.webp"),
 _d("每十萬人財損最多縣市：臺北市",2614.6,"萬元/十萬人","115年9月全月","05_monthly_115-09_summary.webp"),
 _d("受理數增加最多縣市：臺中市",1458,"件","115年9月全月（較8月1,401件增加57件，+4.1%）","05_monthly_115-09_summary.webp",note="2026-10-23 依儀表板截圖讀圖核對；1,458 是 9 月總件數，增加 57 件"),
 _d("每十萬人受理數最高縣市：新竹市",39.28,"件/十萬人","115年10月月至今（儀表板未標明截止日；更新日期115-10-23）","07_county_monthly_115-10_per100k.webp",
    others="花蓮縣38.64、臺中市35.45、臺北市34.19、桃園市33.83、高雄市33.34…最低為連江縣0（連江縣不列入）")]
DASH_TYPE={
 "假網拍":_d("電信網路詐欺類型第1名：假網拍詐騙",3513,"件","115年9月全月","04_fraud_type_top5_115-09.webp",loss="3億2,066萬元"),
 "假投資":_d("電信網路詐欺類型第2名：假投資詐騙",913,"件","115年9月全月","04_fraud_type_top5_115-09.webp",loss="10億9,995.9萬元"),
 "色情應召":_d("電信網路詐欺類型第3名：色情應召詐財詐騙",830,"件","115年9月全月","04_fraud_type_top5_115-09.webp",loss="1億6,328.9萬元"),
 "假交友投資":_d("電信網路詐欺類型第4名：假交友（投資詐財）詐騙",814,"件","115年9月全月","04_fraud_type_top5_115-09.webp",loss="9億3,129.1萬元"),
 "釣魚":_d("電信網路詐欺類型第5名：釣魚連結詐騙",804,"件","115年9月全月","04_fraud_type_top5_115-09.webp",loss="5,978萬元")}
def calc_avg(label,loss_wan,n,period):
    return {"label":label,"value":round(loss_wan/n,1),"unit":"萬元/件","period":period,"verified":True,"self_calculated":True,
            "verify_note":f"自行換算：儀表板財損 {loss_wan:,} 萬 ÷ {n:,} 件；儀表板本身未提供每件平均損失","source":DB}
COUNTY_DASH={"name":"縣市池補充：165打詐儀表板各縣市數據統計（官方，115-09、115-10 月資料）","url":DB,"verified":True,
             "verify_note":"儀表板只有月資料；年度縣市分布仍取自 fromnineon（"+NO_OFFICIAL+"）"}

# ---- v4：沉浸呈現（presentation／chat／red_flag anchor／分享卡）----
CHAT_APP_TYPES={"line_like","dating_like","shop_like","sms_like","phone_call","in_person"}
BRAND_BAN=["LINE","Line","Tinder","Bumble","Pairs","Facebook","臉書","FB","蝦皮","Shopee","Instagram","IG","WhatsApp","Telegram","Messenger"]
MIN_TIMER_S=20
def apply_v4(data,spec,red_flag_anchors,endings_v4,meta_v4):
    """spec: {event_id: {presentation, chat?, pressure?, interrupts?}}；只加欄位，不改 v3 判定邏輯。"""
    ev={e["id"]:e for e in data["events"]}
    for eid,s in spec.items():
        ev[eid].update(s)
    for e in data["events"]:
        e.setdefault("presentation","card")
        for c in e["choices"]:
            miss=[f for f in c["flags"]["set"] if f.startswith("missed_")]
            loss=c["effects"].get("存款",0)<0
            c["grid"]="red" if (miss and loss) else ("yellow" if miss else "green")
    data["red_flag_anchors"]=red_flag_anchors
    for x in data["endings"]:
        x.update(endings_v4[x["id"]])
    data["meta"]["version"]="0.4"
    data["meta"].update(meta_v4)
    return data

# ---- v4.1：共用 helper ----
BRAND_BAN_TEXT=BRAND_BAN+["Threads","賣貨便","104人力","上104","Dcard","PTT","7-11","全家","思樂冰","YouTuber"]
def M(id,frm,text,delay=1200,type="text"): return {"id":id,"from":frm,"text":text,"delay_ms":delay,"type":type}
SHARE_CARD={"format":"1080x1920","fields":["title","title_emoji","life_grid","real_world_stat.display","share_text","url"],"spoiler_free":True}
def share_of_cases(type_key,label):
    """real_world_stat：某詐騙類型占 115-09 全國受理件數的比例（不是結局稀有度）。"""
    n=DASH_TYPE[type_key]["value"]; tot=DASH_MONTH[0]["value"]; pct=round(n/tot*100,1)
    return {"kind":"share_of_reported_cases","value_pct":pct,"formula":f"{n}/{tot}×100 = {pct}%",
            "meaning":f"115年9月全國受理的詐騙案件中，{label}所占比例；與玩家拿到哪個結局無關",
            "period":"115年9月（2026-09）全月","source":DB,"verified":True,
            "verify_note":"165 儀表板截圖 04_fraud_type_top5_115-09.webp、05_monthly_115-09_summary.webp；自行換算",
            "display":f"115 年 9 月全國受理的詐騙案中，約 {round(pct)}% 是{label}"}
def stat_null(reason): return {"kind":"share_of_reported_cases","value_pct":None,"null_reason":reason}
def brand_hits(data):
    """掃描玩家會看到的文字（不含 url / 來源名稱）是否出現真實品牌。"""
    hits=[]
    def scan(where,t):
        for b in BRAND_BAN_TEXT:
            if isinstance(t,str) and b in t: hits.append(f"{where}:{b}")
    for e in data["events"]:
        scan(e["id"],e["text"])
        for c in e["choices"]: scan(e["id"]+"/choice",c["text"])
        ch=e.get("chat")
        if ch:
            scan(e["id"]+"/chat",json.dumps({k:ch.get(k) for k in ("app_display_name","theme","contact","messages")},ensure_ascii=False))
        scan(e["id"]+"/interrupts",json.dumps(e.get("interrupts",[]),ensure_ascii=False))
    for x in data["endings"]:
        scan(x["id"],x["text"]); scan(x["id"]+"/card",x.get("case_card",{}).get("summary",""))
        for m in x.get("missed_red_flags",[]): scan(x["id"]+"/missed",m)
        scan(x["id"]+"/share",x.get("share_text",""))
    for k,v in data.get("red_flag_texts",{}).items(): scan(k,v)
    return hits

# ---- v4.1：跨線 flag（人生線 → 詐騙線），資料驅動 ----
# cross_line_modifiers[]: {id, if_flags:{all:[...], none:[...]}, target:{event, choice?}, effect:{...}, note}
#   effect.type:
#     stats_delta   {stats:{數值:±n}}             進入 target.event 時套用一次（event="__INIT__" 表示開局）
#     unlock_choice {choice:{...同 choices[] 格式}} 在 target.event 的 choices 末端多一個選項
#     add_interrupt {interrupt:{at,from,text}}     在 target.event 的 chat 中插入一則外部訊息
#     rewrite_text  {field:"text"|"choice_text", text}  改寫事件文字，或 target.choice（索引）的選項文字
CROSS_TYPES={"stats_delta","unlock_choice","add_interrupt","rewrite_text"}
def life_flags():
    import os
    p=os.path.join(os.path.dirname(os.path.abspath(__file__)),"script-life.json")
    d=json.load(open(p))
    return {k for k in d["meta"].get("cross_line_flags",{}) if not k.startswith("_")}
def apply_cross(data,mods):
    data["cross_line_modifiers"]=mods
    data["meta"]["cross_line_notes"]=("跨線 flag 來自人生線（script-life.json 結束時玩家持有的 flag，見其 meta.cross_line_flags）。"
      "進入詐騙線時，把人生線 flag 併入玩家 flags；之後對每筆 cross_line_modifiers，若 if_flags.all 全有且 if_flags.none 全無，"
      "就在 target 事件套用 effect（見 common.py 註解）。同一事件多筆規則依陣列順序套用。")
    return data
def apply_modifiers(data,flags):
    """回傳套用後的 events 深拷貝（引擎與 validator 共用的參考實作）。"""
    import copy
    evs={e["id"]:copy.deepcopy(e) for e in data["events"]}; init={}
    for m in data.get("cross_line_modifiers",[]):
        c=m["if_flags"]
        if not all(f in flags for f in c.get("all",[])) or any(f in flags for f in c.get("none",[])): continue
        t=m["target"]; ef=m["effect"]
        if t["event"]=="__INIT__":
            for k,v in ef.get("stats",{}).items(): init[k]=init.get(k,0)+v
            continue
        e=evs[t["event"]]
        if ef["type"]=="stats_delta": e.setdefault("on_enter_effects",{}); [e["on_enter_effects"].__setitem__(k,e["on_enter_effects"].get(k,0)+v) for k,v in ef["stats"].items()]
        elif ef["type"]=="unlock_choice": e["choices"].append(copy.deepcopy(ef["choice"]))
        elif ef["type"]=="add_interrupt": e.setdefault("interrupts",[]).append(ef["interrupt"])
        elif ef["type"]=="rewrite_text":
            if ef["field"]=="text": e["text"]=ef["text"]
            else: e["choices"][t["choice"]]["text"]=ef["text"]
    return list(evs.values()),init

# ---- v4.2：結局前提、統計標記（加法） ----
NO_CATEGORY="官方無此分類"
def finalize_v42(data):
    """stats[] 一律帶 self_calculated(bool)；real_world_stat 沒數字時 display=None（v4.5：前台完全不顯示統計列，不再顯示「官方無此分類」）。"""
    import copy
    out=[]
    for s in data.get("stats",[]):
        s=copy.deepcopy(s)
        if not isinstance(s.get("self_calculated"),bool):
            blob=s.get("label","")+str(s.get("verify_note",""))
            s["self_calculated"]=("自行換算" in blob) or ("自行計算" in blob)
        out.append(s)
    data["stats"]=out
    for x in data["endings"]:
        r=x.get("real_world_stat")
        if r is not None and r.get("value_pct") is None:
            x["real_world_stat"]=dict(r,display=None)
    data["meta"]["ending_premise_notes"]=("endings[].requires_flags／forbids_flags 宣告結局文字預設的前提（validate.py 窮舉路徑檢查）。"
      "text_variants[]：{when:{flags_all,flags_none}, text, requires_flags?, forbids_flags?}，引擎依序取第一個 when 成立的變體取代 text；都不成立用 text。")
    return data
def pick_text(ending,flags):
    for v in ending.get("text_variants",[]):
        w=v["when"]
        if all(f in flags for f in w.get("flags_all",[])) and not any(f in flags for f in w.get("flags_none",[])): return v
    return None

# ---- v4.7：random:true 選項（一個按鈕、結果隨機）----
# choice = {text, random:true, effects:{}, flags:{set:[],require:[...]}, next, grid, outcome_text(按鈕前提示可省略), log_text,
#           outcomes:[{probability, effects, flags_set, outcome_text, log_text, grid, next?}], random_note}
# 引擎：玩家按下按鈕後抽一次 U(0,1)，依 outcomes 陣列順序累加 probability，落在哪一段就用哪個分支。
# 分支的 effects／flags_set 加在 choice 本身的 effects／flags.set 之後；next 預設沿用 choice.next。
def branches(c):
    """回傳 [(probability, 合併後的等效選項)]；非 random 選項回傳 [(1.0, c)]。"""
    if not c.get("random"): return [(1.0,c)]
    out=[]
    for b in c["outcomes"]:
        eff=dict(c.get("effects",{}))
        for k,v in b.get("effects",{}).items(): eff[k]=eff.get(k,0)+v
        m=dict(c,effects=eff,flags={"set":list(c["flags"]["set"])+list(b.get("flags_set",[])),"require":c["flags"]["require"]},
               next=b.get("next",c["next"]),outcome_text=b.get("outcome_text"),log_text=b.get("log_text"),grid=b.get("grid",c.get("grid")))
        m.pop("outcomes",None); m.pop("random",None); out.append((b["probability"],m))
    return out
def resolve(c,rng):
    """依 rng.random() 選一個分支（random 選項才會消耗一次亂數）。"""
    bs=branches(c)
    if len(bs)==1 and not c.get("random"): return bs[0][1]
    r=rng.random(); acc=0.0
    for p,m in bs:
        acc+=p
        if r<acc: return m
    return bs[-1][1]
def set_flags_all(c):
    """選項所有可能設定的 flag（含 random 分支）。"""
    return [q for _,m in branches(c) for q in m["flags"]["set"]]

# ---- v4.7：每個結局都附 help_resources ----
HELP_165={"name":"165反詐騙諮詢專線（警政署）","url":"https://165.npa.gov.tw/","verified":True,"verify_note":"警政署 165 全民防騙網官方網址"}
HELP_1925={"name":"1925安心專線（衛福部，24小時免付費）","url":"https://dep.mohw.gov.tw/DOMHAOH/cp-4906-54077-107.html","verified":True,"verify_note":"2026-10-23 curl HTTP 200"}
HELP_1995={"name":"1995生命線協談專線","url":"https://www.life1995.org.tw/","verified":True,"verify_note":"2026-10-23 curl HTTP 200"}
HELP_LAF={"name":"法律扶助基金會 全國專線 412-8518（市話直撥，手機加02；免費法律諮詢，犯罪被害人也可諮詢）","url":"https://www.laf.org.tw/tel-ext","verified":True,"verify_note":"2026-10-23 curl HTTP 200，官網頁面載明 412-8518"}
def ensure_help(data,mental=(),legal=()):
    """每個結局至少有 165；mental 內的結局加 1925/1995；legal 內的結局加法律扶助基金會。依 url 去重，165 一律排第一。"""
    for x in data["endings"]:
        cur=list(x.get("help_resources",[]))
        want=[HELP_165]+([HELP_1925,HELP_1995] if x["id"] in mental else [])+([HELP_LAF] if x["id"] in legal else [])
        urls={h["url"] for h in cur}
        for h in want:
            if h["url"] not in urls: cur.append(dict(h)); urls.add(h["url"])
        cur.sort(key=lambda h:0 if "165" in h["url"] else 1)
        x["help_resources"]=cur
    data["meta"]["help_resources_rule"]="v4.7：每個結局都有 help_resources（至少 165）；有心理傷害的結局加 1925／1995；車手線刑事相關結局加法律扶助基金會 412-8518"

def mark_standalone(data,notes):
    """v4.7：合併模式觸發不了的跨線修正，標 mode:"standalone_only"（保留給單線模式）。"""
    for m in data.get("cross_line_modifiers",[]):
        if m["id"] in notes: m["mode"]="standalone_only"; m["mode_note"]=notes[m["id"]]
        else: m.setdefault("mode","all")
    data["meta"]["cross_line_mode_rule"]=("cross_line_modifiers[].mode：all＝單線與合併模式都會套用；standalone_only＝合併模式下進場年齡範圍內拿不到該 flag，"
      "實際上只會在單線模式觸發（引擎不需特別處理，條件本來就不成立）；validate／combined 只列為 info")

# ---- v4.9：心理磨損（犯錯／受騙選項各扣一點心理，靠累積，不靠單一大扣）----
import os as _os
MENTAL_WEAR=int(_os.environ.get("MENTAL_WEAR","-2"))
def apply_mental_wear(data,delta=None):
    """grid 為 yellow／red 的選項（含 random 分支、unlock 解鎖選項）在 effects 的 心理 再加 delta；標記 mental_wear。"""
    d=MENTAL_WEAR if delta is None else delta
    def hit(o):
        if o.get("grid") in ("yellow","red"):
            o.setdefault("effects",{}); o["effects"]["心理"]=o["effects"].get("心理",0)+d; o["mental_wear"]=d
    for e in data["events"]:
        for c in e["choices"]:
            if c.get("random"):
                for b in c.get("outcomes",[]): hit(b)
            else: hit(c)
    for m in data.get("cross_line_modifiers",[]):
        if m["effect"]["type"]=="unlock_choice": hit(m["effect"]["choice"])
    data["meta"]["mental_wear"]={"delta":d,"applies_to":"grid 為 yellow／red 的選項（含 random 分支、解鎖選項）","design_assumption":True,
      "note":"每個犯錯／受騙選項只多扣 2 點心理（已併入 effects，choice.mental_wear 標示）。單一選項不會造成大扣；心理歸零靠一生累積。數值是設計假設"}
    return data

GAME_TITLE="2300萬分之1"
def set_title(data):
    """v6：遊戲正式名稱「2300萬分之1」；原本的線名移到 meta.subtitle"""
    m=data["meta"]; old=m.get("title","")
    if old!=GAME_TITLE:
        sub=old.split("：",1)[1] if "：" in old else old
        if sub: m["subtitle"]=sub
    m["title"]=GAME_TITLE; return data
