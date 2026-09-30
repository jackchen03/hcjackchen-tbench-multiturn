#!/usr/bin/env python3
import os,pathlib,resource,signal,subprocess,sys,time
ROOT=pathlib.Path('/app'); stop=False
def term(*_):
 global stop;stop=True
signal.signal(signal.SIGTERM,term)
def config():
 text=(ROOT/'svc/configd.service').read_text()
 d=ROOT/'svc/configd.service.d'
 if d.exists():
  for p in sorted(d.glob('*.conf')):text+='\n'+p.read_text()
 vals={}
 for line in text.splitlines():
  if '=' in line: k,v=line.split('=',1);vals[k.strip()]=v.strip()
 return vals
while not stop:
 c=config();lim=int(c.get('LimitNOFILE','1024'))
 def child():
  resource.setrlimit(resource.RLIMIT_NOFILE,(lim,lim));os.setgid(65534);os.setuid(65534);os.chdir('/app')
 p=subprocess.Popen(['/app/build/configd','--daemon'],preexec_fn=child)
 (ROOT/'svc/configd.pid').write_text(str(p.pid)+'\n')
 while p.poll() is None and not stop:time.sleep(.05)
 if stop:
  if p.poll() is None:p.terminate()
  break
 if c.get('Restart')!='on-failure':break
 delay=float(c.get('AcceptRetrySec','0.05'));time.sleep(min(max(delay,0.01),1.0))
