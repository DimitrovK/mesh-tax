# bench.py <label> [repeats] -- loadgen inside the namespace, outside it, and split over 4 pods
import json, subprocess, sys, concurrent.futures as cf, pathlib, time
label = sys.argv[1]; reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
out = pathlib.Path("out2") / label; out.mkdir(parents=True, exist_ok=True)
def pods(ns, app):
    r = subprocess.run(["kubectl","-n",ns,"get","pod","-l",f"app={app}","--field-selector=status.phase=Running",
                        "-o","jsonpath={.items[*].metadata.name}"],capture_output=True,text=True)
    return r.stdout.split()
def fortio(ns, pod, c, url, t=25):
    r = subprocess.run(["kubectl","-n",ns,"exec",pod,"-c","fortio","--","fortio","load","-c",str(c),"-qps","0",
                        "-t",f"{t}s","-a","-json","-",url],capture_output=True,text=True)
    d = json.loads(r.stdout[r.stdout.index("{"):])
    codes = d["RetCodes"]; assert set(codes) == {"200"}, codes      # every request must have succeeded
    p = {x["Percentile"]: x["Value"]*1000 for x in d["DurationHistogram"]["Percentiles"]}
    return dict(qps=d["ActualQPS"], p50=p[50], p99=p[99], n=d["DurationHistogram"]["Count"])
B = "http://backend.default.svc.cluster.local:8080/"; F = "http://frontend.default.svc.cluster.local:8080/"
inside = pods("default","loadgen")[0]; outside = pods("outside","loadgen-out")[0]; four = pods("default","loadgen4")
assert len(four) == 4, four
cases = [("inside_1hop_c1", lambda: fortio("default",inside,1,B)),
         ("inside_1hop_c32", lambda: fortio("default",inside,32,B)),
         ("inside_2hop_c32", lambda: fortio("default",inside,32,F)),
         ("outside_1hop_c1", lambda: fortio("outside",outside,1,B)),
         ("outside_1hop_c32", lambda: fortio("outside",outside,32,B)),
         ("outside_2hop_c32", lambda: fortio("outside",outside,32,F))]
def split():
    with cf.ThreadPoolExecutor(4) as ex: rs = list(ex.map(lambda p: fortio("default",p,8,B), four))
    return dict(qps=sum(r["qps"] for r in rs), p50=sum(r["p50"] for r in rs)/4, p99=max(r["p99"] for r in rs),
                n=sum(r["n"] for r in rs), per_pod=[round(r["qps"]) for r in rs])
cases.append(("split4x8_1hop", split))
res = {}
for rep in range(reps):
    for name, fn in cases:
        r = fn(); res.setdefault(name, []).append(r)
        print(f"{label} rep{rep+1} {name:<18} {r['qps']:>9.0f} rps  p50 {r['p50']:.3f} ms  p99 {r['p99']:.2f} ms", flush=True)
        json.dump(res, open(out/"results.json","w"), indent=1)
        time.sleep(3)
