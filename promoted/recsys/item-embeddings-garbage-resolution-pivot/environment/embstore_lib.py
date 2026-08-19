import json,struct
from pathlib import Path
import numpy as np
def load_store(root):
 root=Path(root); meta=json.loads((root/'meta.json').read_text()); n,d=meta['num_items'],meta['dim']; means=np.load(root/'means.npy'); ids=(root/'idmap.bin').read_bytes(); out=np.empty((n,d),dtype=np.float32)
 for i in range(n):
  shard,row=struct.unpack_from('<HI',ids,i*6); data=(root/f'primary_{shard:03d}.bin').read_bytes(); off=16+row*d*2
  vec=np.frombuffer(data[off:off+d*2],dtype='<f2').astype(np.float32) if off+d*2<=len(data) else np.zeros(d,dtype=np.float32); out[i]=vec+means[shard]
 return out
def topk(query,k,root='/app/embstore'):
 m=load_store(root); dist=((m-np.asarray(query,dtype=np.float32))**2).sum(1); return np.argsort(dist)[:k].tolist()
