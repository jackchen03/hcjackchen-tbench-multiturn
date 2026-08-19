from pathlib import Path
import struct,zlib
B=8192; MAGIC=0x57414C01
def rec(xid,prev,typ,body=b''):
 total=32+len(body); prefix=struct.pack('>IQQB3s',total,xid,prev,typ,b'\0'*3); zero=prefix+b'\0'*4+b'\0'*4+body; crc=zlib.crc32(zero)&0xffffffff; return prefix+struct.pack('>I',crc)+b'\0'*4+body
buf=bytearray(B*2); struct.pack_into('>IIQQ',buf,0,MAGIC,1,0,0); struct.pack_into('>IIQQ',buf,B,MAGIC,1,0,999999)
off=24; prev=0
for xid,typ in [(10,0),(10,2),(20,0),(20,3),(30,0),(30,2)]:
 raw=rec(xid,prev,typ); buf[off:off+len(raw)]=raw; prev=off; off+=len(raw)
raw=rec(99,123456,0); buf[off:off+len(raw)]=raw; stale=off; off+=len(raw)
raw=rec(99,stale,2); buf[off:off+len(raw)]=raw
Path('/app/data').mkdir(parents=True,exist_ok=True); Path('/app/data/0001.wal').write_bytes(buf)
