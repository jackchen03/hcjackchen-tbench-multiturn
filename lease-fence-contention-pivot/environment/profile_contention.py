#!/usr/bin/env python3
import argparse, json, tempfile
from lease_impl import LeaseStore

p=argparse.ArgumentParser(); p.add_argument('--workers',type=int,required=True); p.add_argument('--ops',type=int,required=True); a=p.parse_args()
with tempfile.TemporaryDirectory(dir='/app') as d:
    s=LeaseStore(d); ok=True
    for i in range(a.workers*a.ops):
        stripe=i%16
        try: t=s.acquire_stripe(stripe); ok &= bool(s.commit_striped(stripe,t,i,str(i)))
        except NotImplementedError: ok=False; break
    print(json.dumps({'striped':ok,'stripes':16}))
    raise SystemExit(0 if ok else 1)
