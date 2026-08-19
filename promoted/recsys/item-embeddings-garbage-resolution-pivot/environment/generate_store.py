from pathlib import Path
import json,struct,zlib
import numpy as np
root=Path('/app/embstore'); root.mkdir(parents=True,exist_ok=True); rng=np.random.default_rng(20260720); N,D=120,8; pr=30
true=rng.normal(0,1,(N,D)).astype(np.float32); means=rng.normal(0,3,(7,D)).astype(np.float32); np.save(root/'means.npy',means); np.save('/opt/grade/truth.npy',true)
(root/'meta.json').write_text(json.dumps({'num_items':N,'dim':D,'num_primary_shards':4,'num_replica_shards':3,'primary_rows':[pr]*4},sort_keys=True)+'\n')
idmap=bytearray()
for i in range(N): idmap+=struct.pack('<HI',i//pr,i%pr)
(root/'idmap.bin').write_bytes(idmap)
def primary(s):
 rows=(true[s*pr:(s+1)*pr]-means[s]).astype('<f2').tobytes(); ptr=b''.join(struct.pack('<HI',0xffff,0xffffffff) for _ in range(pr)); head=struct.pack('<4sIII',b'EMBS',1,pr,D); body=head+rows+ptr; return body+struct.pack('<I',zlib.crc32(body)&0xffffffff)
for s in range(4):
 data=primary(s)
 if s==2: data=data[:16+20*D*2]
 (root/f'primary_{s:03d}.bin').write_bytes(data)
for s in range(3):
 rows=(true-means[4+s]).astype('<f2').tobytes(); back=b''.join(struct.pack('<I',i) for i in range(N)); head=struct.pack('<4sII',b'EMBR',N,D); body=head+back+rows; (root/f'replica_{s:03d}.bin').write_bytes(body+struct.pack('<I',zlib.crc32(body)&0xffffffff))
np.save('/opt/grade/affected.npy',np.arange(80,90,dtype=np.int64))
