import json, glob, os, statistics, sys
rows=[]
for f in sorted(glob.glob("out/*/*.json")):
    lab=f.split("/")[1]; name=os.path.basename(f).replace(".json","")
    try: d=json.load(open(f))
    except Exception: continue
    h=d.get("DurationHistogram",{})
    pct={p["Percentile"]:p["Value"]*1000 for p in h.get("Percentiles",[])}
    rows.append(dict(label=lab, case=name, qps=d.get("ActualQPS"),
                     p50=pct.get(50), p90=pct.get(90), p99=pct.get(99), p999=pct.get(99.9),
                     avg=h.get("Avg",0)*1000, count=h.get("Count")))
print(f"{'variant':<12}{'case':<14}{'qps':>9}{'p50 ms':>9}{'p90 ms':>9}{'p99 ms':>9}{'n':>9}")
for r in sorted(rows,key=lambda r:(r["case"],r["label"])):
    print(f"{r['label']:<12}{r['case']:<14}{r['qps'] or 0:>9.0f}{(r['p50'] or 0):>9.3f}"
          f"{(r['p90'] or 0):>9.3f}{(r['p99'] or 0):>9.3f}{r['count'] or 0:>9}")
json.dump(rows, open("summary.json","w"), indent=1)
