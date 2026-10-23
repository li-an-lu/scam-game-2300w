import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
fp='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
import os
if not os.path.exists(fp): fp='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'
fm.fontManager.addfont(fp); plt.rcParams['font.family']=fm.FontProperties(fname=fp).get_name()
ex=[("shot",4),("promise_park",5),("school_gate",6),("park_reveal",7),("card_trade",7),("hongbao",8),("lottery",9),("lend5",9),("card_reveal",10),("pe_class",10),("honesty",11),("slurpee",11),("first_phone",12),("lend_reveal",12),("free_gift",13),("game_trade",14),("quiz",15),("otp_reveal",15),("lottery_reveal",16),("part_time",17),("hongbao_result",18),("student_loan",19),("rent",20),("mlm",22),("lend",24),("insurance",26),("rosca",30),("elder",35)]
pr=[("NEW 才藝班退費",6),("NEW 考100分就買",8),("NEW 不說出去就不罰",9),("NEW 你不乖就不要你",5),("NEW 同學集資團購",13),("NEW 學長「輕鬆賺」",14),("NEW 借帳戶給朋友",16),("NEW 堂會/陣頭兄弟",15),("NEW 演唱會代購",17),("NEW 免審核小額借貸",20),("NEW 代辦貸款顧問費",23),("NEW 卡債最低應繳",25),("NEW 借錢給家人當保人",28)]
stages=[(0,12,"童年：家庭誘導","#ffe0b2"),(12,18,"國高中：同儕＋幫派吸收","#c8e6c9"),(18,24,"18+：借貸","#bbdefb"),(24,40,"求職/成人","#e1bee7")]
fig,ax=plt.subplots(figsize=(18,7))
for a,b,n,c in stages:
    ax.axvspan(a,b,color=c,alpha=.6); ax.text((a+b)/2,3.75,n,ha='center',fontsize=13,weight='bold')
for i,(n,a) in enumerate(ex):
    y=2.6+(i%4)*0.25; ax.plot(a,y,'o',color='#455a64'); ax.text(a+.1,y,n,fontsize=8)
for i,(n,a) in enumerate(pr):
    y=0.9+(i%4)*0.3; ax.plot(a,y,'*',color='#d32f2f',ms=12); ax.text(a+.15,y,n,fontsize=9,color='#b71c1c')
for n,a in [("車手線 ~19(±2–3)",19),("假網拍線 ~27(±2–3)",27),("假投資線 ~37(±2–3)",37)]:
    ax.axvline(a,color='k',ls='--'); ax.axvspan(a-2.5,a+2.5,ymin=0,ymax=.12,color='gray',alpha=.4); ax.text(a,0.15,n,ha='center',fontsize=10,weight='bold')
ax.text(0.2,3.2,"● 既有事件(script-life.json)",fontsize=10,color='#455a64'); ax.text(0.2,1.95,"★ 建議新增",fontsize=10,color='#b71c1c')
ax.set_xlim(0,40); ax.set_ylim(0,4); ax.set_yticks([]); ax.set_xticks(range(0,41,2)); ax.set_xlabel("年齡")
ax.set_title("人生各階段受騙事件總覽：既有 vs 建議新增 與詐騙線入口",fontsize=15)
plt.tight_layout(); plt.savefig('lifestage-overview.png',dpi=110)
