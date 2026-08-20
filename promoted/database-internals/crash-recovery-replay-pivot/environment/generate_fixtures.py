#!/usr/bin/env python3
import struct
from pathlib import Path
PAGE=256
FORMATS='''# Replay formats\nheap.bin is 256-byte pages: pageLSN u64 LE at 0, slot_count u16 LE at 8, reserved through 15, then slot entries `<HH` tuple_off,flags. wal.bin records are `<QIBBHHH` lsn,page_no,rec_type,pad,arg,length,payload_len followed by payload. Types: OVERWRITE=0, DELTA=1, SET_SLOT=2, PRUNE=3.\n'''
def wal_bytes(records):
 out=bytearray()
 for lsn,page,kind,arg,length,payload in records: out+=struct.pack('<QIBBHHH',lsn,page,kind,0,arg,length,len(payload))+payload
 return bytes(out)
def parse_wal(data):
 records=[];off=0;index=0
 while off<len(data):
  lsn,page,kind,_,arg,length,payload_len=struct.unpack_from('<QIBBHHH',data,off);off+=20;payload=data[off:off+payload_len];off+=payload_len;records.append((lsn,page,kind,arg,length,payload,index));index+=1
 return records
def apply(heap,wal,version):
 pages=[bytearray(heap[i:i+PAGE]) for i in range(0,len(heap),PAGE)];records=parse_wal(wal)
 for page_no,page in enumerate(pages):
  original=struct.unpack_from('<Q',page,0)[0];selected=[r for r in records if r[1]==page_no and r[0]>original]
  if version==1:selected.sort(key=lambda r:(r[0],0 if r[2]==2 else 2 if r[2]==3 else 1,r[6]))
  else:selected.sort(key=lambda r:(r[0],r[6]))
  for lsn,_,kind,arg,length,payload,_ in selected:
   if kind==0 or (kind==1 and version==2):page[arg:arg+len(payload)]=payload
   elif kind==1:
    for i,value in enumerate(payload):page[arg+i]^=value
   elif kind==2:page[16+arg*4:20+arg*4]=payload
   else:
    tuple_off,flags=struct.unpack_from('<HH',page,16+arg*4)
    if version==2 or flags&1==0:page[tuple_off:tuple_off+length]=bytes(length)
   struct.pack_into('<Q',page,0,lsn)
 return b''.join(pages)
def base_page(lsn,flags=1,offset=100):
 page=bytearray(PAGE);struct.pack_into('<QH',page,0,lsn,1);struct.pack_into('<HH',page,16,offset,flags);page[offset:offset+20]=bytes(range(16,36));return bytes(page)
def create(root,version,cases):
 root=Path(root);root.mkdir(parents=True,exist_ok=True)
 for name,heap,records in cases:
  case=root/name;case.mkdir();wal=wal_bytes(records);(case/'heap.bin').write_bytes(heap);(case/'wal.bin').write_bytes(wal);(case/'recovered.bin').write_bytes(apply(heap,wal,version))
v1=[('case00',base_page(5),[(4,0,0,110,2,b'zz'),(6,0,1,100,2,b'\xff\x0f')]),('case01',base_page(5,1),[(6,0,3,0,4,b'')]),('case02',base_page(5,1),[(7,0,3,0,3,b''),(7,0,2,0,4,struct.pack('<HH',100,0))]),('case03',base_page(5),[(6,0,0,105,3,b'ABC')]),('case04',base_page(5,0,120),[(8,0,2,0,4,struct.pack('<HH',120,0)),(8,0,3,0,5,b''),(8,0,1,125,2,b'\x55\xaa')])]
v2=[('case00',base_page(5),[(6,0,1,100,2,b'\x01\x02')]),('case01',base_page(5,1),[(6,0,3,0,4,b'')]),('case02',base_page(5,1,100),[(7,0,3,0,3,b''),(7,0,2,0,4,struct.pack('<HH',120,0))]),('case03',base_page(5,0),[(6,0,1,104,3,b'XYZ')]),('case04',base_page(5,1),[(9,0,0,110,2,b'qq'),(9,0,3,0,2,b'')])]
Path('/app/FORMATS.md').write_text(FORMATS);create('/app/samples',1,v1);create('/app/samples_v2',2,v2)
