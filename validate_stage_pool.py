"""validate_stage_pool.py（v7）：檢查 stage-pool.json 是否符合內容規範。"""
import json, re, sys
from common import BRAND_BAN_TEXT
d = json.load(open("stage-pool.json")); E = []
HELP = re.compile(r"165|1925|1995|專線|安心專線")
DEATH = re.compile(r"自殺|輕生|跳樓|死掉|去死|尋死|燒炭")
CRIME = re.compile(r"人頭帳戶怎麼|如何洗錢|車手.*(領|提)款步驟")
def chk(where, t):
    if HELP.search(t): E.append(f"{where}: 遊戲中出現求助專線（只能放結局）")
    if DEATH.search(t): E.append(f"{where}: 死亡／自殺描述")
    if CRIME.search(t): E.append(f"{where}: 犯罪操作細節")
    for b in BRAND_BAN_TEXT:
        if b in t: E.append(f"{where}: 品牌 {b}")
for l in d["lies"]: chk(l["id"], l["text"])
for p in d["positive"]:
    chk(p["id"], p["text"] + "".join(c["text"] + c["outcome_text"] for c in p["choices"]))
    for c in p["choices"]:
        if len(c["text"]) > 15: E.append(f"{p['id']}: 選項超過 15 字「{c['text']}」")
for c in d["lie_endings"]:
    c = {**c, "case": c["case"] or c.get("case_v7", ""), "source_note": c.get("source_note") or c.get("source_note_v7", "")}   # v8 公開版：未查證案件移到 *_v7 不上畫面
    for k in ("text", "case", "review"):
        if not c[k]: E.append(f"{c['id']}: 缺 {k}")
    if "待查證" not in c.get("source_note", "") and not (c.get("sources") and all(s.get("verified") is True and s.get("url") for s in c["sources"])): E.append(f"{c['id']}: 來源未標待查證")   # v8：附已查證網址者可免標
    if DEATH.search(c["text"] + c["case"]): E.append(f"{c['id']}: 死亡描述")
for s in d["stages"]:
    L = [l for l in d["lies"] if l["stage"] == s["id"]]; P = [p for p in d["positive"] if p["stage"] == s["id"]]
    if len(P) < s["draws"] - s["max_lies"]: E.append(f"{s['id']}: 正面事件不足")
    if not 2 <= s["max_lies"] <= 3: E.append(f"{s['id']}: max_lies 應為 2–3")
for f in d["core_flags"]:
    if not any(f in l["core_flags"] for l in d["lies"]): E.append(f"core flag {f} 沒有任何謊言觸發")
if sum(1 for c in d["lie_endings"] if c["requires"]) < 4: E.append("有前置 flag 的結局少於 4 張")
print("stage-pool", "ERRORS " + str(E) if E else "OK"); sys.exit(1 if E else 0)
