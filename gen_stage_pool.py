"""gen_stage_pool.py：把 Leo 的被動謊言／正面事件／14 張謊言連結結局卡整理成 stage-pool.json（v7）。
內容一字不刪：謊言與正面事件取自 web/playable/full.html 的 CONTENT（與 *-events-*.md 等 99 則敘事一一對應），
結局卡取自 ending-cards-lie-linked-complete.md。只做「連結」：補核心 flag、伏筆 flag、階段、權重。"""
import json, re
SRC = open("web/playable/full.html", encoding="utf-8").read()
def grab(name):
    i = SRC.index(f"const {name} =") + len(f"const {name} =")
    return json.JSONDecoder().raw_decode(SRC[i:].lstrip())[0]
C = grab("CONTENT")
stage = lambda a: "child" if a <= 12 else "student" if a <= 22 else "adult"
clean = lambda t: re.sub(r"\s*>\s*", "\n", t).strip()
UNIT = 3   # Leo 的 心±1 是 10 分制；本作數值 0–100，1 單位 = 3 分
KEY = {"心": "心理", "警": "警覺", "人": "人際"}
def eff(s):
    out = {}
    for k, v in re.findall(r"([心警人])([+-]\d+)", s): out[KEY[k]] = out.get(KEY[k], 0) + int(v) * UNIT
    return out
# 核心 flag 連結（只補，不改 Leo 已標的）
CORE = ["heard_stranger", "heard_police", "heard_everyone", "said_its_fine", "heard_miss_chance", "obey_authority"]
LINK = [  # (關鍵字, flag)；連結理由寫在 HANDOFF-v7.md
    ("虎姑婆", "heard_stranger"), ("那種人混", "heard_stranger"),
    ("警察會來", "heard_police"), ("少年隊", "heard_police"),
    ("別人都", "heard_everyone"), ("你看你同學", "heard_everyone"), ("你看隔壁", "heard_everyone"),
    ("沒機會", "heard_miss_chance"),
    ("「還好」", "said_its_fine"), ("「沒事」", "said_its_fine"),
    ("老師在門口說：「再遲到", "obey_authority"), ("主管說：「現在請假", "obey_authority"), ("主管說：「現在請會影響", "obey_authority"),
    ("主管說：「公司像家", "obey_authority"),
]
lies = []
for i, x in enumerate(C["lies"]):
    flags = [x["flag"]] if x.get("flag") else []
    for kw, f in LINK:
        if kw in x["text"] and f not in flags: flags.append(f)
    lies.append({"id": f"L{i:03d}", "age": x["age"], "stage": stage(x["age"]), "text": clean(x["text"]),
                 "effects": {"心理": -UNIT}, "core_flags": flags})
# 伏筆：正面事件裡的「查證／告訴家人／停一下」→ 之後詐騙線開場會回扣
FS = [(r"確認|查證|問清楚|打電話", "fs_verify", "你想起很久以前，有人教過你：先確認，再決定。"),
      (r"家人|爸|媽|阿嬤|阿公|奶奶|爺爺", "reminded_family", "你想起家裡那句話：有事可以說，不用一個人扛。"),
      (r"同事|朋友|同學", "talked_family_work", "你想起曾經有人在你猶豫時，陪你停下來想一想。")]
pos = []
for x in C["pos"]:
    ch = []
    for c in x["choices"]:
        assert len(c["t"]) <= 15, c["t"]
        e = eff(c["eff"]); fl = []
        if sum(e.values()) > 0:
            for pat, f, _ in FS:
                if re.search(pat, c["t"] + c["result"]) and f not in fl: fl.append(f); break
        ch.append({"text": c["t"], "outcome_text": clean(c["result"]), "effects": e, "flags": fl})
    pos.append({"id": x["id"], "age": x["age"], "stage": stage(x["age"]), "text": clean(x["text"]), "choices": ch})
# 14 張結局卡
md = open("ending-cards-lie-linked-complete.md", encoding="utf-8").read()
cards = []
for blk in re.split(r"\n### ", md)[1:]:
    head, body = blk.split("\n", 1)
    eid, name = [s.strip() for s in head.split("｜")]
    sec = lambda k: (re.search(rf"\*\*{k}：\*\*\s*(.*?)(?=\n\*\*|\n---|\Z)", body, re.S) or [None, ""])[1].strip()
    text = "\n".join(l.lstrip("> ").strip() for l in sec("結局文字").splitlines() if l.strip())
    case = sec("真實案件卡")
    missed = [l[2:].strip() for l in sec("你錯過的破綻").splitlines() if l.startswith("- ")]
    cards.append({"id": eid, "name": name, "text": text, "case": re.sub(r"\s+\n", "\n", case),
                  "missed": missed, "review": sec("回顧連結"), "help": sec("求助資訊"),
                  "source_note": "寫手提供，待查證"})
assert len(cards) == 14, len(cards)
W = {  # base, boost(flag→weight), requires(核心前置 flag), pool
 "END_TRUST_LONG": (8, {"heard_stranger": 18}, ["heard_stranger"], "heavy"),
 "END_AUTHORITY_CALL": (6, {"heard_police": 16}, ["heard_police"], "heavy"),
 "END_GROUP_PROFIT": (10, {"heard_everyone": 20, "heard_miss_chance": 20}, ["heard_everyone"], "heavy"),
 "END_DONT_WORRY": (8, {"said_its_fine": 18}, ["said_its_fine"], "heavy"),
 "END_INVEST_SMALL": (10, {"heard_miss_chance": 18}, ["heard_miss_chance"], "heavy"),
 "END_FAMILY_IMPERSONATE": (8, {"said_its_fine": 14}, ["said_its_fine"], "heavy"),
 "END_SHOPPING_LINK": (12, {"obey_authority": 16}, [], "heavy"),
 "END_CUSTOMER_SERVICE": (10, {"obey_authority": 16}, [], "heavy"),
 "END_JOB_FEE": (8, {"obey_authority": 14}, [], "heavy"),
 "END_ROMANCE_BORROW": (8, {}, [], "heavy"), "END_LOAN_FIRST": (8, {}, [], "heavy"),
 "END_ALMOST": (6, {"reminded_family": 22}, [], "light"),
 "END_QUIET": (15, {"_no_core": 25}, [], "light"),
 "END_HELPED_OTHERS": (4, {"talked_family_work": 12, "fs_verify": 10}, [], "light")}
REVIEW_FLAGS = {"END_TRUST_LONG": ["heard_stranger"], "END_AUTHORITY_CALL": ["heard_police"], "END_GROUP_PROFIT": ["heard_everyone", "heard_miss_chance"],
 "END_DONT_WORRY": ["said_its_fine"], "END_FAMILY_IMPERSONATE": ["said_its_fine"], "END_INVEST_SMALL": ["heard_miss_chance"],
 "END_SHOPPING_LINK": ["obey_authority"], "END_CUSTOMER_SERVICE": ["obey_authority"], "END_JOB_FEE": ["obey_authority"], "END_LOAN_FIRST": ["obey_authority"]}
for c in cards:
    b, bo, rq, pl = W[c["id"]]
    c.update(base=b, boost=bo, requires=rq, pool=pl, review_flags=REVIEW_FLAGS.get(c["id"], []))
out = {"version": "v7", "unit_note": "Leo 原稿 1 單位 = 本作 3 分（0–100 制）",
 "core_flags": CORE,
 "stages": [  # draws＝每階段固定抽數；max_lies＝被動謊言上限；不連續出現謊言（cooldown 1）
   {"id": "child", "label": "童年", "min_age": 4, "max_age": 12, "draws": 6, "max_lies": 3},
   {"id": "student", "label": "學生", "min_age": 13, "max_age": 22, "draws": 6, "max_lies": 3},
   {"id": "adult", "label": "出社會", "min_age": 23, "max_age": 42, "draws": 6, "max_lies": 3}],
 "lie_cooldown": 1, "core_lie_weight": 3,
 "foreshadow": {f: t for _, f, t in FS},
 "childhood_mindset": [   # 童年經驗 → 進入學生期時的數值與文字差異
   {"when": {"min_pos": 3}, "text": "那幾年，總有人在你跌倒時蹲下來。你慢慢相信，遇到怪事可以先問人。", "effects": {"警覺": 3, "心理": 3}},
   {"when": {"min_lies": 3}, "text": "小時候聽過很多「不這樣就會怎樣」。長大後，你很容易被一句嚇人的話推著走。", "effects": {"警覺": -3}},
   {"when": {}, "text": "童年過去了。有些話你記得，有些人你也記得。", "effects": {}}],
 "lies": lies, "positive": pos, "lie_endings": cards}
json.dump(out, open("stage-pool.json", "w"), ensure_ascii=False, indent=1)
from collections import Counter
print("stage-pool lies", len(lies), "pos", len(pos), "cards", len(cards),
      "core", Counter(f for l in lies for f in l["core_flags"]), "fs", Counter(f for p in pos for c in p["choices"] for f in c["flags"]))
