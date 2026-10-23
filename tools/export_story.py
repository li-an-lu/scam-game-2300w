"""把 script-*.json 劇情文本匯出成 STORY-TEXT-ALL.md（＋.docx）。用法：python3 tools/export_story.py"""
import json,os,re
os.chdir(os.path.join(os.path.dirname(__file__),".."))
LINES=[("life","人生日常線"),("romance","交往線"),("marriage","婚姻線"),("parent","家長篇"),("mule","求職變車手線"),("shopping","假網拍線"),("investment","投資詐騙線")]
AB={"存款":"存","警覺":"警","人際":"人","心理":"心"}
def eff(e):
    out=[]
    for k,v in (e or {}).items():
        if not v: continue
        if k=="存款" and abs(v)>=10000: s=f"{v/10000:+g}萬"
        else: s=f"{v:+g}"
        out.append(AB.get(k,k)+s)
    return " ".join(out) or "—"
def srcs(ss):
    out=[]
    for s in ss or []:
        n=s.get("name","")
        if "寫手" in n: tag="寫手提供，待查證"
        elif "設計假設" in n or "原創" in n: tag="原創／設計假設"
        elif re.search("判決|法院|判賠|判刑|刑事",n): tag="判決／司法"
        elif "165" in n or "警政署" in n or "刑事警察局" in n: tag="165／警政"
        else: tag="研究／新聞"
        v="" if s.get("verified",None) is None else ("（已核對）" if s.get("verified") else "（待查）")
        out.append(f"[{tag}] {n}{v}"+(f" <{s['url']}>" if s.get("url") else ""))
    return out
def when(w):
    w=w or {}; p=[]
    if w.get("flags_all"): p.append("有 "+"、".join(w["flags_all"]))
    if w.get("flags_none"): p.append("無 "+"、".join(w["flags_none"]))
    if w.get("label"): p.append(w["label"])
    return "；".join(p) or "（條件）"
def q(t): return "> "+(t or "").replace("\n","\n> ")
D={l:json.load(open(f"script-{l}.json")) for l,_ in LINES if os.path.exists(f"script-{l}.json")}
L=D["life"]; POOL=L["meta"].get("event_pool",{}).get("childhood",{})
opt={}; 
for b in POOL.get("optional",[]):
    for x in b["block"]: opt[x]=b["p_appear"]
md=[f"# 《{L['meta'].get('title','')}》全劇本文本\n","自動匯出（tools/export_story.py）。修改請改 gen_*.py 後重新 build；本檔僅供閱讀與標註。數值簡寫：存＝存款、警＝警覺、人＝人際、心＝心理。\n","## 目錄\n"]
for l,n in LINES:
    if l in D: md.append(f"- [{n}（{l}）](#{l})")
md.append("- [固定必出 vs 隨機池](#pool)\n")
md.append('<a id="pool"></a>\n## 固定必出 vs 隨機池（人生線）\n')
md.append("| 事件 | 年齡 | 類型 |\n|---|---|---|")
for e in L["events"]:
    if e.get("router"): continue
    base=e["id"].replace("__swap","")
    if base in opt: t=f"隨機池（出現 {opt[base]:.0%}）"
    elif e["id"].endswith("__swap"): t="順序互換副本"
    elif e["id"] in ("loan_use","sleep_issue","family_talk"): t="條件觸發"
    else: t="固定必出"+("（核心）" if e["id"] in POOL.get("core",[]) else "")
    if e["id"] in POOL.get("variants",{}): t+=f"；情境變體 {POOL['variants'][e['id']]['scene']} 種"
    md.append(f"| {e['id']} | {e.get('age','')} | {t} |")
md.append("\n詐騙線依 meta.scam_integration 於進場年齡窗插入；romance、parent 為必出線。車手入口變體由 pool_mule_variant 抽 1。\n")
for l,n in LINES:
    if l not in D: continue
    d=D[l]; md.append(f'<a id="{l}"></a>\n## {n}（{l}）\n')
    evs=[e for e in d["events"] if not e.get("router")]
    if l=="life": evs=sorted(evs,key=lambda e:e.get("age",0))  # 同齡保持原順序（sorted 穩定）
    for e in evs:
        md.append(f"### {e['id']}　｜　{e.get('age','')} 歲　｜　{e.get('category','')} {e.get('presentation','')}")
        if e["id"] in opt: md.append(f"*隨機池：出現機率 {opt[e['id']]:.0%}*")
        md.append("**情境：**\n\n"+q(e.get("text","")))
        ch=e.get("chat")
        if ch:
            md.append("\n**聊天訊息：**\n")
            for m in ch.get("messages",[]): md.append(f"- `{m.get('id')}` {m.get('from','')}：{m.get('text','')}")
        for it in e.get("interrupts",[]): md.append(f"- 插話（{it.get('at')}）{it.get('text','')}")
        for v in e.get("text_variants",[]): md.append(f"\n**情境變體**（{when(v.get('when'))}）：\n\n"+q(v.get("text","")))
        md.append("\n**選項：**\n")
        for i,c in enumerate(e["choices"]):
            md.append(f"{i+1}. 【{c.get('text','')}】（{c.get('grid','')}）數值：{eff(c.get('effects'))}　→ {c.get('next')}")
            if c.get("outcome_text"): md.append(f"   - 結果：{c['outcome_text']}")
            if c["flags"].get("require"): md.append(f"   - 需要：{'、'.join(c['flags']['require'])}")
            if c["flags"].get("set"): md.append(f"   - 旗標：{'、'.join(c['flags']['set'])}")
            for o in c.get("outcomes",[]): md.append(f"   - 隨機 {o.get('probability',0):.0%}：{o.get('outcome_text','')}（{eff(o.get('effects'))}）")
            for v in c.get("outcome_variants",[]): md.append(f"   - 旗標變體（{when(v.get('when'))}）：{v.get('outcome_text') or v.get('text','')}")
        if e.get("amount_note"): md.append(f"\n*金額說明：{e['amount_note'] if isinstance(e['amount_note'],str) else e['amount_note'].get('note','')}*")
        s=srcs(e.get("sources"))
        if s: md.append("\n**來源：**\n"+"\n".join("- "+x for x in s))
        md.append("")
    for m in d.get("cross_line_modifiers",[]):
        if m==d["cross_line_modifiers"][0]: md.append(f"### {n}：跨線修飾（人生線旗標 → 本線）\n")
        ef=m["effect"]; txt=ef.get("interrupt",{}).get("text") or ef.get("text") or eff(ef.get("delta") or ef.get("effects")) or ef.get("type")
        md.append(f"- `{m['id']}` 條件 {when({'flags_all':m['if_flags'].get('all'),'flags_none':m['if_flags'].get('none')})} → {m['target'].get('event')}：{ef['type']} {txt}")
    md.append(f"\n### {n}：結局與案件卡\n")
    for x in sorted(d["endings"],key=lambda x:x.get("priority",9)):
        md.append(f"#### {x.get('title_emoji','')} {x.get('title','')}（{x['id']}）")
        md.append(q(x.get("text","")))
        for v in x.get("text_variants",[]): md.append(f"\n- 變體（{when(v.get('when'))}）：{v.get('text','')}")
        cc=x.get("case_card") or {}
        if cc: md.append(f"\n**案件卡**（story_id：{cc.get('story_id','待查')}）：{cc.get('summary','')}　{('<'+cc['url']+'>') if cc.get('url') else '（url 待查）'}")
        if x.get("missed_red_flags"): md.append("**錯過的破綻：** "+"；".join(map(str,x["missed_red_flags"]))[:600])
        s=srcs(x.get("sources"))
        if s: md.append("**來源：**\n"+"\n".join("- "+y for y in s))
        md.append("")
open("STORY-TEXT-ALL.md","w").write("\n".join(md))
try:
    import pypandoc; pypandoc.convert_file("STORY-TEXT-ALL.md","docx",outputfile="STORY-TEXT-ALL.docx"); print("docx ok")
except Exception as ex: print("docx failed",ex)
print("events",sum(len([e for e in d['events'] if not e.get('router')]) for d in D.values()))
