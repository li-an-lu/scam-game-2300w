"""v8 共用規則：年齡關鍵字、10 倍數換算。apply_v8.py 與 validate_v8.py 共用。"""
# 文字出現這些詞時，事件／項目的 min_age 至少要多少（含選項與結果文字）
AGE_KEYWORDS = [
    (["正職", "找穩定工作", "面試", "履歷", "主管", "上班", "第一份工作", "下班", "同事"], 18),
    (["打工", "時薪", "兼職", "薪水", "薪轉"], 15),
    (["租屋", "房租", "押金", "套房", "房東", "退租", "搬出"], 18),
    (["學貸", "大三", "註冊單"], 18),
    (["結婚", "婚禮", "房貸", "育嬰", "孩子的學費", "你兒子", "你女兒"], 22),
    (["自己出國", "出國旅行"], 16),
    (["信用卡", "刷卡", "保單", "解約金", "網銀", "貸款"], 18),
    (["帳戶", "提款卡"], 13),
]
# 文字提到「別人」的工作等不算（例：舅舅的故事），在事件上寫 age_keyword_ok 並附理由即可豁免
def kw_min(text):
    m, hit = 0, []
    for words, a in AGE_KEYWORDS:
        for w in words:
            if w in text and a > m: m, hit = a, [w]
    return m, hit

STAGES = [("child", 0, 12), ("student", 13, 22), ("adult", 23, 99)]
def stage_of(a):
    for s, lo, hi in STAGES:
        if lo <= a <= hi: return s, lo, hi
    return "adult", 23, 99

MENTAL = ("警覺", "人際", "心理")
STRICT_MIN = False   # True：非零至少 ±10；False：|v|≤5 歸零（v8 採用，避免小加分膨脹）
def r10(v, stat=None):
    """0–100 制變化量 → 10 的倍數。警覺／人際：5 進位（+5→+10，學到東西要看得到）；
    心理：5 捨去（±5→0、±15→±10），保持 v7 的心理歸零比例（合併模擬 HALTED v7 12.2% → v8 約 13%）。"""
    if not v: return 0
    a = abs(v)
    m = (int((a + 4.999) / 10) if stat == "心理" else int(a / 10 + 0.5)) * 10 or (10 if STRICT_MIN else 0)
    return m if v > 0 else -m
def leo10(v):
    """stage-pool：v7 以 Leo 1 單位 = 3 分存放 → v8 改為 1 單位 = 10 分"""
    if not v: return 0
    u = int(abs(v) / 3 + 0.5) or 1
    return u * 10 if v > 0 else -u * 10

HELPLINE_WORDS = ["165", "1925", "1995", "113 專線", "反詐騙專線"]

def texts(o, own_only=False):
    """收集事件裡所有給玩家看的字（text／outcome_text／text_variants／versions），不含 sources、說明欄位"""
    out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("text", "outcome_text") and isinstance(v, str): out.append(v)
            elif k in ("text_variants", "versions", "choices") or isinstance(v, (dict, list)) and k in ("variants",): out += texts(v)
    elif isinstance(o, list):
        for x in o: out += texts(x) if not isinstance(x, str) else [x]
    return out
