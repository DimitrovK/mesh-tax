import json, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
rows={ (r["label"],r["case"]):r for r in json.load(open("summary.json")) }
plt.rcParams.update({"figure.facecolor":"#12141a","axes.facecolor":"#12141a","axes.edgecolor":"#3a4050",
 "text.color":"#e6e8ee","axes.labelcolor":"#e6e8ee","xtick.color":"#9aa3b5","ytick.color":"#9aa3b5",
 "font.size":11,"grid.color":"#232733"})
CONC=[1,8,32]
fig=plt.figure(figsize=(12.5,9)); gs=fig.add_gridspec(2,2,hspace=0.42,wspace=0.26)
for col,hop,hoplab in [(0,"one_hop","one hop: client to backend"),(1,"two_hop","two hops: client to frontend to backend")]:
    ax=fig.add_subplot(gs[0,col])
    b=[rows[("baseline_big",f"{hop}_c{c}")]["qps"] for c in CONC]
    m=[rows[("meshed_big", f"{hop}_c{c}")]["qps"] for c in CONC]
    x=np.arange(len(CONC)); w=0.36
    ax.bar(x-w/2,b,w,color="#3fb950",label="no mesh",edgecolor="#12141a",lw=1.2)
    ax.bar(x+w/2,m,w,color="#e5484d",label="Linkerd",edgecolor="#12141a",lw=1.2)
    for i,(bb,mm) in enumerate(zip(b,m)):
        ax.text(i-w/2,bb*1.03,f"{bb:,.0f}",ha="center",fontsize=9)
        ax.text(i+w/2,mm*1.03,f"{mm:,.0f}",ha="center",fontsize=9)
        ax.text(i,max(bb,mm)*1.19 if i else max(b)*0.30,f"-{100*(1-mm/bb):.0f}%",ha="center",fontsize=10.5,color="#ffb4b6")
    ax.set_xticks(x); ax.set_xticklabels([f"c={c}" for c in CONC])
    ax.set_ylim(0,max(b)*1.35); ax.set_ylabel("requests per second" if col==0 else "")
    ax.grid(axis="y",alpha=.3,lw=.6); ax.set_title(hoplab,loc="left",fontsize=11.5,pad=8)
    if col==0: ax.legend(facecolor="#1a1d26",edgecolor="#3a4050",fontsize=9.5)
    ax2=fig.add_subplot(gs[1,col])
    bp=[rows[("baseline_big",f"{hop}_c{c}")]["p50"] for c in CONC]
    mp=[rows[("meshed_big", f"{hop}_c{c}")]["p50"] for c in CONC]
    b9=[rows[("baseline_big",f"{hop}_c{c}")]["p99"] for c in CONC]
    m9=[rows[("meshed_big", f"{hop}_c{c}")]["p99"] for c in CONC]
    ax2.plot(CONC,bp,"o-",color="#3fb950",lw=2.2,label="no mesh p50")
    ax2.plot(CONC,mp,"o-",color="#e5484d",lw=2.2,label="Linkerd p50")
    ax2.plot(CONC,b9,"o--",color="#3fb950",lw=1.4,alpha=.6,label="no mesh p99")
    ax2.plot(CONC,m9,"o--",color="#e5484d",lw=1.4,alpha=.6,label="Linkerd p99")
    ax2.set_xscale("log"); ax2.set_xticks(CONC); ax2.set_xticklabels([f"c={c}" for c in CONC])
    ax2.set_ylabel("latency (ms)" if col==0 else ""); ax2.grid(alpha=.3,lw=.6)
    ax2.set_title("latency",loc="left",fontsize=11.5,pad=8)
    if col==0: ax2.legend(facecolor="#1a1d26",edgecolor="#3a4050",fontsize=8.5,ncol=2)
fig.suptitle("The service mesh latency number everyone quotes is the one that matters least",
             x=0.055,ha="left",fontsize=14.5,y=0.985)
fig.text(0.055,0.948,"Linkerd edge-26.9.3 on DOKS 1.36.3, 3x s-4vcpu-8gb. nginx on both tiers, fortio load. Nodes never exceeded 50% CPU.",
         ha="left",fontsize=9.5,color="#9aa3b5")
fig.subplots_adjust(left=0.085,right=0.975,top=0.895,bottom=0.07)
fig.savefig("results.png",dpi=145); print("wrote results.png")
