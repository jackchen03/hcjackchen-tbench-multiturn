#!/usr/bin/env python3
import pathlib
import random
import sys

TOP = [("HH_00",800),("HH_01",770),("HH_02",740),("HH_03",710),("HH_04",680),("HH_05",560),("HH_06",560),("HH_07",530),("HH_08",515),("HH_09",500)]
TIER = [("HH_10",420),("HH_11",415),("HH_12",410),("HH_13",405),("HH_14",400),("HH_15",395),("HH_16",390),("HH_17",385),("HH_18",380),("HH_19",375)]

def stream(seed=7):
    counts = dict(TOP) | {"NH_%02d"%i:340+((i*13+seed*7)%61) for i in range(30)} | dict(TIER)
    lines=[]
    for key,n in counts.items(): lines.extend([key]*n)
    rng=random.Random(seed)
    cold=["COLD_%04d"%i for i in range(800)]
    lines.extend(rng.choice(cold) for _ in range(5000))
    rng.shuffle(lines)
    a,b="HH_05","HH_06"
    ia,ib=lines.index(a),lines.index(b)
    if ia < ib: lines[ia],lines[ib]=lines[ib],lines[ia]
    return lines

out=pathlib.Path(sys.argv[1]); out.mkdir(parents=True,exist_ok=True)
lines=stream()
(out/"stream_sample.txt").write_text("\n".join(lines)+"\n")
(out/"topk.py").write_text("""def exact_topk(lines, k=10):\n    return [[key, 1] for key in list(dict.fromkeys(lines))[:k]]\n""")
(out/"check_exact.py").write_text("""#!/usr/bin/env python3\nimport argparse\nfrom collections import Counter\nfrom topk import exact_topk\np=argparse.ArgumentParser();p.add_argument('--sample',required=True);p.add_argument('--k',type=int,default=10);a=p.parse_args()\nlines=[x.rstrip('\\n') for x in open(a.sample) if x.strip()]\nwant=[[k,v] for k,v in sorted(Counter(lines).items(),key=lambda x:(-x[1],x[0]))[:a.k]]\nraise SystemExit(0 if exact_topk(lines,a.k)==want else 1)\n""")
(out/"profile_driver.py").write_text("""#!/usr/bin/env python3\nimport argparse,time,statistics\nfrom collections import Counter\np=argparse.ArgumentParser();p.add_argument('--sample',required=True);p.add_argument('--k',type=int,default=10);a=p.parse_args();lines=[x.rstrip('\\n') for x in open(a.sample) if x.strip()]\ntc=[];ts=[]\nfor _ in range(5):\n t=time.perf_counter(); c=Counter(lines); tc.append((time.perf_counter()-t)*1000)\n t=time.perf_counter(); sorted(c.items(),key=lambda x:(-x[1],x[0]))[:a.k]; ts.append((time.perf_counter()-t)*1000)\nc=statistics.median(tc);s=statistics.median(ts);h='counting' if c>=s else 'selection';share=max(c,s)/(c+s)\nprint(f'counting: {c:.2f} ms');print(f'selection: {s:.2f} ms');print(f'hotspot: {h}');print(f'share: {share:.4f}')\n""")
(out/"benchmark.py").write_text("""#!/usr/bin/env python3\nimport argparse,importlib.util,statistics,time\np=argparse.ArgumentParser();p.add_argument('--func',required=True);p.add_argument('--stream',required=True);p.add_argument('--k',type=int,default=10);p.add_argument('--repeat',type=int,default=5);a=p.parse_args();lines=[x.rstrip('\\n') for x in open(a.stream) if x.strip()]\ns=importlib.util.spec_from_file_location('candidate','/app/topk.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);fn=getattr(m,a.func);vals=[]\nfor _ in range(a.repeat):\n t=time.perf_counter();fn(lines,a.k);vals.append((time.perf_counter()-t)*1000)\nprint(f'{statistics.median(vals):.2f}')\n""")
for p in out.iterdir(): p.chmod(0o755 if p.suffix==".py" else 0o644)
