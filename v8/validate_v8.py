"""v8 檢查：年齡（擋下 3 歲找工作這類錯誤）、選項數與字數、mood_line、rethink、版本、10 倍數、專線只在結局。
錯誤 → exit 1；Leo 原文的既有問題列為 WARN 不擋。"""
import json, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import texts, kw_min, MENTAL, HELPLINE_WORDS
import content as K
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ld = lambda f: json.load(open(os.path.join(ROOT, f)))
ERR, WARN = [], []
LINES = ["life", "investment", "mule", "shopping", "romance", "marriage", "parent"]
NEW_IDS = {e["id"] for e in K.PERP_EVENTS}

def chk_eff(where, eff):
    for s in MENTAL:
        v = (eff or {}).get(s)
        if isinstance(v, (int, float)) and v % 10: ERR.append(f"{where}: {s} 變化 {v} 不是 10 的倍數")

L = ld("script-life.json")
r = L["meta"].get("rethink") or {}
if not 0.5 <= r.get("probability", 0) <= 0.7: ERR.append("meta.rethink.probability 必須明確寫 0.5–0.7")
if r.get("stats", {}).get("警覺") != 60: ERR.append("meta.rethink.stats.警覺 應為 60（=畫面 6）")
if not L["meta"].get("early_halt", {}).get("immediate_in_scam", False): ERR.append("early_halt.immediate_in_scam 應為 true（心理歸零無條件結束）")
for g in LINES:
    d = L if g == "life" else ld(f"script-{g}.json")
    for s in MENTAL:
        if d["player_init"]["stats"][s].get("display_max") != 10: ERR.append(f"{g}: {s} 缺 display_max=10")
    for e in d["events"]:
        w = f"{g}:{e['id']}"
        if "min_age" not in e or "max_age" not in e:
            if e["id"] != "birth" or g == "life": ERR.append(f"{w}: 缺 min_age/max_age")
            continue
        if g == "life" and not e["min_age"] <= e["age"] <= e["max_age"]:
            ERR.append(f"{w}: 事件年齡 {e['age']} 不在 {e['min_age']}–{e['max_age']}（引擎會跳過）")
        k, hit = kw_min("".join(texts(e)))
        if g == "life" and k > e["age"] and not e.get("age_keyword_ok"):
            ERR.append(f"{w}: {e['age']} 歲出現「{hit[0]}」（需 ≥{k} 歲）")
        if k > e["min_age"] and not e.get("age_keyword_ok"):
            ERR.append(f"{w}: min_age {e['min_age']} 低於關鍵字「{hit[0]}」要求的 {k}")
        chk_eff(w, e.get("on_enter_effects"))
        for c in e.get("choices", []):
            chk_eff(w, c.get("effects"))
            if len(c["text"]) > 15: (ERR if e.get("v8_key") or e["id"] in NEW_IDS else WARN).append(f"{w}: 選項「{c['text']}」超過 15 字")
        if e.get("v8_key") or e["id"] in NEW_IDS:
            vis = [c for c in e["choices"] if not any(f.startswith("!") for f in c["flags"]["require"])] 
            if len({c["text"] for c in e["choices"]}) < 4: ERR.append(f"{w}: 關鍵選擇應有 4 個選項")
            for c in e["choices"]:
                if not c.get("mood_line"): ERR.append(f"{w}: 「{c['text']}」缺 mood_line")
                for h in HELPLINE_WORDS:
                    if h in c["text"] + c.get("outcome_text", "") + c.get("mood_line", ""): ERR.append(f"{w}: 專線只能出現在結局（{h}）")
        elif g == "life" and not e.get("router") and len(e.get("choices", [])) > 2 and e.get("category") != "揭曉":
            n = len({c["text"] for c in e["choices"]})
            if n > 2: WARN.append(f"{w}: 日常事件有 {n} 個不同選項（Leo 原稿，未改）")
        for c in e.get("choices", []):
            for h in HELPLINE_WORDS:
                if h in c["text"] + c.get("outcome_text", "") and not (e.get("v8_key") or e["id"] in NEW_IDS):
                    WARN.append(f"{w}: 非結局文字出現專線「{h}」（Leo 原稿）")
for eid, vs in K.VERSIONS.items():
    e = next(x for x in L["events"] if x["id"] == eid)
    if len(e.get("versions", [])) != 3: ERR.append(f"{eid}: 需要 3 個版本")
for f in L.get("year_filler", []):
    k, hit = kw_min(f["text"])
    if f["min_age"] < k: ERR.append(f"year_filler「{f['text']}」min_age {f['min_age']} < {k}")
m = ld("web/manifest.json")
for f in m.get("year_filler", []):
    if isinstance(f, str): ERR.append(f"manifest year_filler「{f}」沒有年齡範圍")

S = ld("stage-pool.json")
for x in S["lies"] + S["positive"]:
    w = f"pool:{x['id']}"
    if not x.get("min_age", 0) <= x["age"] <= x.get("max_age", 99) or "min_age" not in x: ERR.append(f"{w}: 年齡欄位錯誤")
    t = x.get("text", "") + "".join(c.get("text", "") + c.get("outcome_text", "") for c in x.get("choices", []))
    k, hit = kw_min(t)
    if k > x["age"] and not x.get("age_keyword_ok"): ERR.append(f"{w}: {x['age']} 歲出現「{hit[0]}」（需 ≥{k}）")
    chk_eff(w, x.get("effects"))
    for c in x.get("choices", []): chk_eff(w, c.get("effects"))
for e in S["lie_endings"]:
    if re.match(r"^(你記得|你小時候)", e["text"]): ERR.append(f"{e['id']}: 結局卡仍以固定回憶句開頭")
print("\n".join("WARN " + w for w in WARN)); print("\n".join("ERROR " + e for e in ERR))
print(f"validate_v8: {len(ERR)} errors, {len(WARN)} warnings")
sys.exit(1 if ERR else 0)
