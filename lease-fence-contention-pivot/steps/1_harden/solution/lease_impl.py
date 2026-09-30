import json, os, struct, threading


class LeaseStore:
    def __init__(self, root="."):
        self.root=root; os.makedirs(root,exist_ok=True); self._lock=threading.Lock()
        self.fence=os.path.join(root,'fence.dat'); self.hwm=os.path.join(root,'hwm.dat'); self.log=os.path.join(root,'log.jsonl')
        if not os.path.exists(self.fence): self._write(self.fence,0)

    @staticmethod
    def _read(path, default):
        try:
            raw=open(path,'rb').read()
            return struct.unpack('>Q',raw)[0] if len(raw)==8 else default
        except FileNotFoundError: return default

    @staticmethod
    def _write(path,value):
        with open(path,'wb') as f:
            f.write(struct.pack('>Q',value)); f.flush(); os.fsync(f.fileno())

    def grant(self):
        with self._lock:
            value=self._read(self.fence,0)+1; self._write(self.fence,value); return value

    def commit(self,tok,op,val):
        with self._lock:
            if tok!=self._read(self.fence,0) or op<=self._read(self.hwm,-1): return False
            with open(self.log,'a') as f:
                f.write(json.dumps({'op':op,'tok':tok,'val':val},separators=(',',':'))+'\n'); f.flush(); os.fsync(f.fileno())
            self._write(self.hwm,op); return True

    def acquire_stripe(self,stripe): raise NotImplementedError('step 2')
    def commit_striped(self,stripe,tok,op,val): raise NotImplementedError('step 2')
