import json,struct
from pathlib import Path
out=Path("/app/sample"); out.mkdir(parents=True,exist_ok=True)
def add(ver,seq,ts,oid,side,sym,price,size):
    prefix=b"A"+bytes([ver])+struct.pack("<IQQB",seq,ts,oid,side); sb=sym.encode()
    if ver==1: return prefix+bytes([len(sb)])+sb+struct.pack(">I",price)+struct.pack("<I",size)
    return prefix+struct.pack(">I",price)+struct.pack("<I",size)+bytes([len(sb)])+sb
def exe(seq,ts,oid,size): return b"E\x01"+struct.pack("<IQQI",seq,ts,oid,size)
feed=add(1,1,10,1001,0,"XYZ",65792,65792)+add(1,2,11,1002,1,"XYZ",131584,65792)+exe(3,12,1001,256)
(out/"feed.bin").write_bytes(feed)
(out/"expected.json").write_text(json.dumps({"XYZ":{"bids":[[65792,65536]],"asks":[[131584,65792]],"vwap":65792}},sort_keys=True,separators=(",",":")))
