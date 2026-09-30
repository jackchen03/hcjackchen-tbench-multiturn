import json, os, struct, threading


class LeaseStore:
    def __init__(self,root='.'):
        self.root=root; os.makedirs(root,exist_ok=True); self._lock=threading.Lock(); self._stripe_locks={}; self._guard=threading.Lock()
        self.fence=os.path.join(root,'fence.dat'); self.hwm=os.path.join(root,'hwm.dat'); self.log=os.path.join(root,'log.jsonl')
        if not os.path.exists(self.fence): self._write(self.fence,0)
    @staticmethod
    def _read(path,default):
        try:
            raw=open(path,'rb').read(); return struct.unpack('>Q',raw)[0] if len(raw)==8 else default
        except FileNotFoundError:return default
    @staticmethod
    def _write(path,value):
        with open(path,'wb') as f:f.write(struct.pack('>Q',value));f.flush();os.fsync(f.fileno())
    @staticmethod
    def _commit(lock,fence,hwm,log,tok,op,val):
        with lock:
            if tok!=LeaseStore._read(fence,0) or op<=LeaseStore._read(hwm,-1):return False
            with open(log,'a') as f:f.write(json.dumps({'op':op,'tok':tok,'val':val},separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
            LeaseStore._write(hwm,op);return True
    def grant(self):
        with self._lock:v=self._read(self.fence,0)+1;self._write(self.fence,v);return v
    def commit(self,tok,op,val):return self._commit(self._lock,self.fence,self.hwm,self.log,tok,op,val)
    def _parts(self,stripe):
        if not isinstance(stripe,int) or stripe<0 or stripe>=16:raise ValueError('stripe must be 0..15')
        d=os.path.join(self.root,'stripe%02d'%stripe);os.makedirs(d,exist_ok=True)
        with self._guard:lock=self._stripe_locks.setdefault(stripe,threading.Lock())
        return lock,os.path.join(d,'fence.dat'),os.path.join(d,'hwm.dat'),os.path.join(d,'log.jsonl')
    def acquire_stripe(self,stripe):
        lock,fence,_,_=self._parts(stripe)
        with lock:v=self._read(fence,0)+1;self._write(fence,v);return v
    def commit_striped(self,stripe,tok,op,val):
        lock,fence,hwm,log=self._parts(stripe);return self._commit(lock,fence,hwm,log,tok,op,val)
