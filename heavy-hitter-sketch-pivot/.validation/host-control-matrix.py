#!/usr/bin/env python3
import base64, json, pathlib, subprocess, sys

IMAGE="tbench-mt-heavy-hitter-sketch-pivot:validate"
TASK=pathlib.Path("/home/hcjackchen/worktrees/phase2-mt-reaudit-20260930/heavy-hitter-sketch-pivot")
NAME="heavy-control"

def sh(args, check=True):
    return subprocess.run(args,text=True,capture_output=True,check=check)

def dx(*args, check=True):
    return sh(["docker","exec",NAME,*args],check=check)

def fresh():
    sh(["docker","rm","-f",NAME],check=False)
    sh(["docker","run","-d","--name",NAME,IMAGE,"sleep","infinity"])

def put(path,text):
    payload=base64.b64encode(text.encode()).decode()
    code="import base64,pathlib;pathlib.Path(%r).write_bytes(base64.b64decode(%r))"%(path,payload)
    dx("python3","-c",code)

def oracle(step):
    sh(["docker","cp",str(TASK/"steps"/step/"solution"/"solve.sh"),NAME+":/tmp/solve.sh"])
    dx("bash","/tmp/solve.sh")

def grade(step,want,label):
    sh(["docker","cp",str(TASK/"steps"/step/"tests")+"/.",NAME+":/tests"])
    dx("bash","/tests/test.sh",check=False)
    got=dx("cat","/logs/verifier/reward.txt").stdout.strip()
    if got != str(want):
        print("CONTROL",label,"FAIL expected",want,"got",got)
        print(dx("cat","/logs/verifier/test-stdout.txt",check=False).stdout)
        raise SystemExit(1)
    print("CONTROL",label,"OK reward="+got)

EXACT="""from collections import Counter
def exact_topk(lines,k=10):
 return [[a,b] for a,b in sorted(Counter(lines).items(),key=lambda x:(-x[1],x[0]))[:k]]
"""
ALT_SORT="""from collections import Counter
def exact_topk(lines,k=10):
 pairs=sorted(Counter(lines).items())
 pairs.sort(key=lambda x:-x[1])
 return [[a,b] for a,b in pairs[:k]]
"""
MOST="""from collections import Counter
def exact_topk(lines,k=10): return [[a,b] for a,b in Counter(lines).most_common(k)]
"""
HARD="""def exact_topk(lines,k=10):
 return [['HH_00',800],['HH_01',770],['HH_02',740],['HH_03',710],['HH_04',680],['HH_05',560],['HH_06',560],['HH_07',530],['HH_08',515],['HH_09',500]][:k]
"""
SPACE=EXACT+"""
class S:
 def __init__(self): self.c={}
 def add(self,x):
  if x in self.c:self.c[x]+=1
  elif len(self.c)<128:self.c[x]=1
  else:
   v=min(self.c,key=self.c.get);self.c[x]=self.c.pop(v)+1
def approx_topk(lines,k=10):
 s=S()
 for x in lines:s.add(x)
 return [x for x,_ in sorted(s.c.items(),key=lambda z:(-z[1],z[0]))[:k]]
"""
CMS=EXACT+"""
from array import array
import hashlib,heapq
def approx_topk(lines,k=10):
 w=1024;tabs=[array('I',[0])*w for _ in range(4)];heap=[];seen=set()
 def est(x):return min(tabs[r][int.from_bytes(hashlib.md5((str(r)+':'+x).encode()).digest()[:4],'little')%w] for r in range(4))
 for x in lines:
  for r in range(4):tabs[r][int.from_bytes(hashlib.md5((str(r)+':'+x).encode()).digest()[:4],'little')%w]+=1
  e=est(x)
  if x in seen:
   for i,(_,y) in enumerate(heap):
    if y==x:heap[i]=(e,x);heapq.heapify(heap);break
  elif len(heap)<k:heapq.heappush(heap,(e,x));seen.add(x)
  elif e>heap[0][0]:
   _,y=heapq.heapreplace(heap,(e,x));seen.remove(y);seen.add(x)
 return [x for _,x in sorted(heap,key=lambda z:(-z[0],z[1]))]
"""
def finish():
    oracle("3_approx")

try:
    fresh();put("/app/topk.py",ALT_SORT);grade("1_exact",1,"alt_sorted_key")
    fresh();put("/app/topk.py",MOST);grade("1_exact",0,"mutant_most_common")
    fresh();put("/app/topk.py",HARD);grade("1_exact",0,"mutant_public_hardcode")

    fresh();put("/app/topk.py",EXACT);put("/app/diagnosis.json",json.dumps({"hotspot":"counting","share":0.75,"evidence":"counting: 1.00 ms\nselection: 0.30 ms\nindependent annotation"})+"\n");grade("2_diagnose",1,"alt_independent_measure")
    fresh();put("/app/topk.py",EXACT);put("/app/diagnosis.json",json.dumps({"hotspot":"counting","share_ms":1.0,"evidence":"counting: 1.00 ms\nselection: 0.30 ms"})+"\n");grade("2_diagnose",0,"mutant_abs_time")
    fresh();put("/app/topk.py",EXACT);put("/app/diagnosis.json",json.dumps({"hotspot":"counting","share":0.75,"evidence":"profiled manually"})+"\n");grade("2_diagnose",0,"mutant_no_quote")

    fresh();oracle("1_exact");oracle("2_diagnose");put("/app/topk.py",CMS);put("/app/diagnosis.json",json.dumps({"hotspot":"counting","share":0.75,"evidence":"counting: 1.00 ms\nselection: 0.30 ms"})+"\n");finish();grade("3_approx",1,"alt_array_cms")
    variants={
      "mutant_sampled_dict": EXACT+"\ndef approx_topk(lines,k=10): return [x for x,_ in __import__('collections').Counter(lines[::10]).most_common(k)]\n",
      "mutant_narrow_cms": EXACT+"\ndef approx_topk(lines,k=10): return ['COLD_%04d'%i for i in range(k)]\n",
      "mutant_exact_as_approx": EXACT+"\ndef approx_topk(lines,k=10): return [x for x,_ in exact_topk(lines,k)]\n",
      "mutant_int_cms_memory": EXACT+"\ndef approx_topk(lines,k=10):\n junk=[0]*200000; return [x for x,_ in exact_topk(lines,k)]\n",
      "mutant_hardcoded_approx": EXACT+"\ndef approx_topk(lines,k=10): return ['HH_%02d'%i for i in range(k)]\n"
    }
    for label,src in variants.items():
      fresh();oracle("1_exact");oracle("2_diagnose");put("/app/topk.py",src);put("/app/RETIREMENT.signed","EXACT_COUNTS_RETIRED\n1.00\ncounting\n");grade("3_approx",0,label)
    for label,line2,line3 in [("mutant_fabricated_time","999.99","counting"),("mutant_wrong_citation","1.00","selection")]:
      fresh();oracle("1_exact");oracle("2_diagnose");put("/app/topk.py",SPACE);put("/app/RETIREMENT.signed",f"EXACT_COUNTS_RETIRED\n{line2}\n{line3}\n");grade("3_approx",0,label)
finally:
    sh(["docker","rm","-f",NAME],check=False)
print("host-control-matrix PASS alternatives=3 mutants=11")
