import json,matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fm.fontManager.addfont("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
plt.rcParams["font.family"]="Noto Sans CJK TC"
LINES=[("人生日常線","script-life.json","#2e7d32"),("投資詐騙線","script-investment.json","#c62828"),("求職車手線","script-mule.json","#6a1b9a"),("假網拍線","script-shopping.json","#1565c0")]
data=[]
for name,fn,col in LINES:
    evs=[e for e in json.load(open(fn))["events"] if e["id"] not in("birth",) and not e.get("router") and e["id"]!="END_ROUTER"]
    g={}
    for e in evs: g.setdefault(e["age"],[]).append(e)
    data.append((name,col,g))
ages=sorted({a for _,_,g in data for a in g}); X={a:i for i,a in enumerate(ages)}
H=[max(len(v) for v in g.values()) for _,_,g in data]
fig,ax=plt.subplots(figsize=(1.6*len(ages)+2.5,0.8*sum(H)+2.2),dpi=120)
y0=0
for (name,col,g),h in reversed(list(zip(data,H))):
    ax.axhspan(y0-.5,y0+h-.5,color=col,alpha=.07)
    ax.text(-0.7,y0+(h-1)/2,name,ha="right",va="center",fontsize=14,color=col,weight="bold")
    for a,evs in g.items():
        for k,e in enumerate(evs):
            t=e["text"].replace("{county}","").replace("{family}","")[:9]
            ax.text(X[a],y0+h-1-k,f"{e['id']}\n{t}",ha="center",va="center",fontsize=10,
                bbox=dict(boxstyle="round,pad=.3",fc="#fff8e1" if e.get("category")=="揭曉" or e["id"]=="hongbao_result" else "white",ec=col,lw=1.3,ls="--" if e.get("category")=="揭曉" or e["id"]=="hongbao_result" else "-"))
    y0+=h
ax.set_xticks(range(len(ages)));ax.set_xticklabels([f"{a}歲" for a in ages],fontsize=11)
ax.set_xlim(-0.6,len(ages)-0.4);ax.set_ylim(-.6,y0-.4);ax.set_yticks([])
ax.grid(axis="x",ls=":",alpha=.5)
ax.set_title("《80億分之1》事件總覽：橫軸＝年齡（只列出有事件的年齡），顏色＝路線；黃底虛線框＝延後揭曉",fontsize=16)
plt.tight_layout();plt.savefig("overview.png")
