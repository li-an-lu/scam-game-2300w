"""v8 資料層：在 gen_*.py 產生 v7 JSON 之後套用（build.py --all 會呼叫）。冪等：重跑不會重複加。
用法：python3 v8/apply_v8.py scripts   （改 script-*.json）
      python3 v8/apply_v8.py pool      （改 stage-pool.json）
      python3 v8/apply_v8.py manifest  （改 web/manifest.json 的 year_filler）"""
import json, sys, os, copy, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rules import texts, kw_min, stage_of, MENTAL, r10, leo10
import content as K
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda f: os.path.join(ROOT, f)
LINES = ["life", "investment", "mule", "shopping", "romance", "marriage", "parent"]
load = lambda f: json.load(open(P(f)))
def dump(o, f): json.dump(o, open(P(f), "w"), ensure_ascii=False, indent=2)

def round_effects(o):
    if isinstance(o, dict):
        if o.get("type") == "stats_delta" and isinstance(o.get("stats"), dict):
            for s in MENTAL:
                if isinstance(o["stats"].get(s), (int, float)): o["stats"][s] = r10(o["stats"][s], s)
        for k, v in o.items():
            if k in ("effects", "on_enter_effects", "enter_effects") and isinstance(v, dict):
                for s in MENTAL:
                    if isinstance(v.get(s), (int, float)): v[s] = r10(v[s], s)
            else: round_effects(v)
    elif isinstance(o, list):
        for x in o: round_effects(x)

def all_text(e):
    return "".join(texts(e))

def mule_thresholds(d):
    """10 倍數換算後人際普遍偏高，CUT_OFF（需 isolated）幾乎消失 → 門檻對齊畫面 0–10：isolated ≤20（=2）、has_support ≥30（=3）"""
    for f in d["ending_rules"]["stat_flags"]:
        if f["flag"] == "isolated": f["stats"]["人際"] = {"lte": 20}
        if f["flag"] == "has_support": f["stats"]["人際"] = {"gte": 30}
    s = json.dumps(d, ensure_ascii=False).replace("人際≤15", "人際≤2").replace("人際≥20", "人際≥3")
    d.clear(); d.update(json.loads(s))

def scripts():
    L = load("script-life.json"); E = {e["id"]: e for e in L["events"]}
    # 加害者線
    if "perp_account_ask" not in E:
        i = [e["id"] for e in L["events"]].index(K.PERP_INSERT_AFTER)
        for c in E[K.PERP_INSERT_AFTER]["choices"]:
            c["next_v7"] = c["next"]; c["next"] = "perp_account_ask"
        for j, pe in enumerate(copy.deepcopy(K.PERP_EVENTS)): L["events"].insert(i + 1 + j, pe)
        E = {e["id"]: e for e in L["events"]}
    # 關鍵詐騙事件 4 選項
    for eid, spec in ([] if os.environ.get("V8_SKIP_KEY") else K.KEY.items()):
        e = E[eid]
        if e.get("v8_key"): continue
        e["v8_key"] = True
        for s in spec:
            if isinstance(s, tuple):
                _, label, patch = s
                hit = [c for c in e["choices"] if c["text"] == label]
                assert hit, (eid, label)
                for c in hit:
                    if "text" in patch: c["text_v7"] = c["text"]
                    if "outcome_text" in patch: c["outcome_text_v7"] = c["outcome_text"]
                    c.update(patch)
                    fx = K.OUTCOME_FIX.get((eid, label))
                    if fx: c["outcome_text_v7"] = c["outcome_text"]; c["outcome_text"] = fx
            else:
                e["choices"].append(copy.deepcopy(s))
    # 固定劇情 3 版本
    for eid, vs in K.VERSIONS.items(): E[eid]["versions"] = copy.deepcopy(vs)
    L["meta"]["rethink"] = K.RETHINK
    L["meta"]["early_halt"]["immediate_in_scam"] = True
    L["year_filler"] = K.YEAR_FILLER
    for g in LINES:
        d = L if g == "life" else load(f"script-{g}.json")
        if not os.environ.get("V8_SKIP_ROUND"): round_effects(d)
        d["meta"].pop("mood_lines", None)   # 不放全域備援句：每個小選擇都多一次點擊太拖；只在關鍵選擇寫 mood_line
        d["meta"]["v8"] = {"stat_scale": "內部 0–100，畫面 0–10（display_max）；警覺／人際／心理 的變化量皆為 10 的倍數（v8 由 apply_v8.py 四捨五入，非零至少 ±10）"}
        for s, st in d["player_init"]["stats"].items():
            if s in MENTAL and isinstance(st, dict): st["display_max"] = 10
        win = None
        if g != "life":
            h = next(x for x in L["meta"]["scam_integration"]["lines"] if x["line"] == g)
            win = (h["entry_window"]["range"][0], h["entry_window"]["range"][1] + 1)
        for e in d["events"]:
            for c in e.get("choices", []):
                if c.get("grid") == "green": c.setdefault("rethink", False)
            if e["id"] == "birth":
                if g == "life": e["min_age"], e["max_age"] = 0, 0
                continue
            if win: lo, hi = win
            else: _, lo, hi = stage_of(e["age"])
            k, _ = kw_min(all_text(e))
            if e.get("age_keyword_ok"): k = 0
            e["min_age"], e["max_age"] = max(lo, k), hi
        for e in d["events"]:
            for label, patch in K.HOTLINE_FIX.get((g, e["id"]), []):
                for c in e["choices"]:
                    if c["text"] == label or c.get("text_v7") == label:
                        if "text" in patch and "text_v7" not in c: c["text_v7"] = c["text"]
                        if "outcome_text_v7" not in c: c["outcome_text_v7"] = c["outcome_text"]
                        c.update(patch)
            if g == "life" and e["id"] == "hongbao" and not e.get("v8_key"):
                e["v8_key"] = True
                for c in e["choices"]: c.setdefault("mood_line", K.HONGBAO_MOOD[c["text"]])
                e["choices"].append(copy.deepcopy(K.HONGBAO_4TH))
        public_clean(d)
        if g == "mule": mule_thresholds(d)
        dump(d, f"script-{g}.json")
    print("v8 scripts applied")

DEVNOTE = re.compile(r"設計說明|審查修正|非真實|待查證|寫手提供|^v\d")
def public_clean(d):
    """公開版：沒有官方原始來源的統計不顯示；給作者看的案件卡註記清空（原文留 *_v7）。"""
    for st in d.get("stats", []):
        if "尚無官方原始來源" in (st.get("verify_note") or "") and st.get("display") is not False:
            st["display_v7"] = st.get("display"); st["display"] = False
    for en in d.get("endings", []):
        cc = en.get("case_card") or {}
        if DEVNOTE.search(cc.get("note") or ""): cc["note_v7"] = cc["note"]; cc["note"] = ""

def pool():
    S = load("stage-pool.json")
    if S.get("version") == "v8": print("pool already v8"); return
    S["version"] = "v8"; S["unit_note_v7"] = S.get("unit_note"); S["unit_note"] = "v8：Leo 原稿 1 單位 = 10 分（0–100 制，畫面 0–10）"
    W = {s["id"]: (s["min_age"], s["max_age"]) for s in S["stages"]}
    def conv(eff):
        for k in list(eff):
            if k in MENTAL: eff[k] = leo10(eff[k])
    for x in S["lies"] + S["positive"]:
        conv(x.get("effects", {}))
        for c in x.get("choices", []):
            conv(c.get("effects", {})); c["rethink"] = False
        t = x.get("text", "") + "".join(c.get("text", "") + c.get("outcome_text", "") for c in x.get("choices", []))
        lo, hi = W[x["stage"]]; k, _ = kw_min(t)
        if x["id"] in K.AGE_KEYWORD_OK: x["age_keyword_ok"] = K.AGE_KEYWORD_OK[x["id"]]; k = 0
        x["min_age"], x["max_age"] = max(lo, k), hi
    for m in S["childhood_mindset"]: conv(m.get("effects", {}))
    for e in S["lie_endings"]:
        if e["id"] in K.ENDING_FIRSTLINE:
            e["text_v7"] = e["text"]; lines = e["text"].split("\n"); lines[0] = K.ENDING_FIRSTLINE[e["id"]]; e["text"] = "\n".join(lines)
        e["boost"].update(K.ENDING_BOOST.get(e["id"], {}))
    for e in S["lie_endings"]:   # 未查證的案件對照不上公開畫面（原文留 *_v7）
        if re.search(r"待查證|寫手提供", e.get("source_note", "")):
            e["case_v7"], e["source_note_v7"] = e.get("case", ""), e["source_note"]; e["case"] = ""; e["source_note"] = ""
    if not any(e["id"] == K.PERP_ENDING["id"] for e in S["lie_endings"]): S["lie_endings"].append(copy.deepcopy(K.PERP_ENDING))
    dump(S, "stage-pool.json"); print("v8 pool applied")

def manifest():
    m = load("web/manifest.json"); m["year_filler"] = K.YEAR_FILLER; dump(m, "web/manifest.json"); print("v8 manifest applied")

if __name__ == "__main__":
    {"scripts": scripts, "pool": pool, "manifest": manifest}[sys.argv[1]]()
