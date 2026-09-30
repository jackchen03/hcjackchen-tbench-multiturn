#!/usr/bin/env python3
import argparse, json, os, tempfile
from lease_impl import LeaseStore

p=argparse.ArgumentParser(); p.add_argument('--workers',type=int,required=True); p.add_argument('--ops',type=int,required=True); p.add_argument('--kill-at',type=int,required=True); a=p.parse_args()
with tempfile.TemporaryDirectory(dir='/app') as d:
    s=LeaseStore(d)
    for i in range(a.kill_at):
        t=s.grant(); s.commit(t,i,str(i))
    s=LeaseStore(d)
    for i in range(a.kill_at,a.workers*a.ops):
        t=s.grant(); s.commit(t,i,str(i))
    fp=os.path.join(d,'fence.dat')
    ok=os.path.exists(fp) and int.from_bytes(open(fp,'rb').read(),'big')==a.workers*a.ops
    print(json.dumps({'durable':ok,'events':a.workers*a.ops}))
    raise SystemExit(0 if ok else 1)
