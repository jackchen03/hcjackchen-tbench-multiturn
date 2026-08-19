#!/usr/bin/env python3
import struct
from pathlib import Path

FORMATS='''# Binary formats\n\nAll integers are little-endian with no padding. seqcat.bin: u32 count, then u32 seq_id, u8 name_len, ASCII name, i64 increment, u32 cache_size, i64 min_value, i64 max_value, u8 cycle. ckpt.bin: u32 count then u32 seq_id and i64 ckpt_ceiling. wal.bin: u32 record count, then u8 type; REFILL(0) has u32 seq_id; INSERT(1) has u32 xid,u32 seq_id,i64 value; COMMIT(2) and ABORT(3) have u32 xid.\n'''
def step(value,seq):
 candidate=value+seq['inc']
 if seq['inc']>0 and candidate>seq['max']: return seq['min'] if seq['cycle'] else seq['max']
 if seq['inc']<0 and candidate<seq['min']: return seq['max'] if seq['cycle'] else seq['min']
 return candidate
def committed(events):
 status={event[1]:event[0] for event in events if event[0] in (2,3)}; result={}
 for event in events:
  if event[0]==1 and status.get(event[1])==2: result.setdefault(event[2],[]).append(event[3])
 return {key:sorted(set(values)) for key,values in result.items()}
def expected(seqs,ckpt,events,mode):
 used=committed(events); refills={seq['id']:0 for seq in seqs}
 for event in events:
  if event[0]==0: refills[event[1]]+=1
 lines=[]
 for seq in sorted(seqs,key=lambda item:item['name'].encode()):
  values=used.get(seq['id'],[])
  if mode=='v2':
   nxt=step(max(values),seq) if values else (seq['min'] if seq['inc']>0 else seq['max'])
  else:
   ceiling=ckpt[seq['id']]
   for _ in range(refills[seq['id']]*seq['cache']): ceiling=step(ceiling,seq)
   nxt=step(ceiling,seq)
  if mode=='next': lines.append(f"{seq['name']}|{nxt}")
  else: lines.append(f"{seq['name']}|{nxt}|{','.join(map(str,values))}")
 return '\n'.join(lines)+'\n'
def write_fixture(root,seqs,ckpt,events):
 root=Path(root); root.mkdir(parents=True,exist_ok=True)
 with open(root/'seqcat.bin','wb') as f:
  f.write(struct.pack('<I',len(seqs)))
  for s in seqs:
   name=s['name'].encode(); f.write(struct.pack('<IB',s['id'],len(name))+name+struct.pack('<qIqqB',s['inc'],s['cache'],s['min'],s['max'],s['cycle']))
 with open(root/'ckpt.bin','wb') as f:
  f.write(struct.pack('<I',len(seqs)))
  for s in seqs:f.write(struct.pack('<Iq',s['id'],ckpt[s['id']]))
 with open(root/'wal.bin','wb') as f:
  f.write(struct.pack('<I',len(events)))
  for e in events:
   f.write(struct.pack('<B',e[0]))
   if e[0]==0:f.write(struct.pack('<I',e[1]))
   elif e[0]==1:f.write(struct.pack('<IIq',e[1],e[2],e[3]))
   else:f.write(struct.pack('<I',e[1]))
seqs=[{'id':1,'name':'order_id','inc':1,'cache':5,'min':1,'max':100,'cycle':0},{'id':2,'name':'invoice_no','inc':5,'cache':3,'min':0,'max':60,'cycle':1},{'id':3,'name':'descending','inc':-3,'cache':4,'min':-20,'max':10,'cycle':1},{'id':4,'name':'empty_seq','inc':2,'cache':4,'min':0,'max':40,'cycle':0}]
ckpt={1:10,2:50,3:-14,4:4}; events=[(0,1),(1,101,1,11),(2,101),(1,102,1,12),(3,102),(0,1),(1,103,1,17),(2,103),(1,104,1,19),(0,2),(1,201,2,55),(2,201),(1,202,2,60),(2,202),(0,3),(1,301,3,-17),(2,301),(1,302,3,-20),(2,302),(1,303,3,10),(3,303)]
write_fixture('/app',seqs,ckpt,events); Path('/app/FORMATS.md').write_text(FORMATS)
sample=Path('/app/data/sample'); write_fixture(sample,seqs[:3],{1:10,2:50,3:-14},events); (sample/'expected_next.txt').write_text(expected(seqs[:3],ckpt,events,'next')); (sample/'expected_full.txt').write_text(expected(seqs[:3],ckpt,events,'full')); (sample/'expected_v2.txt').write_text(expected(seqs[:3],ckpt,events,'v2'))
Path('/app/report_naive').write_text("#!/usr/bin/env python3\nprint('naive report resumes from observed values and includes every INSERT')\n")
