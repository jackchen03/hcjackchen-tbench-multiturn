import struct
from pathlib import Path

SESSION=b"ALPHA00001"
def packet(seq, messages, count=None):
    if count is None:
        count=len(messages)
    body=SESSION+struct.pack(">QH",seq,count)
    for msg in messages:
        body += struct.pack(">H",len(msg))+msg
    return struct.pack(">H",len(body))+body

def expected(packets):
    store={}
    for seq,msgs,count in packets:
        if count in (0,65535):
            continue
        for i,msg in enumerate(msgs):
            store.setdefault(seq+i,msg)
    keys=sorted(store)
    stream="".join(store[k].hex()+"\n" for k in keys)
    gaps=[]; start=None
    if keys:
        for k in range(keys[0],keys[-1]+1):
            if k not in store and start is None:
                start=k
            elif k in store and start is not None:
                gaps.append((start,k-1)); start=None
        if start is not None:
            gaps.append((start,keys[-1]))
    gaptext="".join((str(a) if a==b else f"{a} {b}")+"\n" for a,b in gaps)
    return stream,gaptext

out=Path("/generated/samples")
sets={
 "sample_single":[(1,[b"A"],1),(2,[b"B"],1),(3,[b"C"],1)],
 "prod_multi":[(1,[b"A",b"B",b"C"],3),(4,[b"D",b"E"],2),(7,[b"G"],1)],
 "with_heartbeat":[(1,[b"A",b"B"],2),(3,[],0),(3,[b"C"],1),(4,[],65535)],
 "collision":[(1,[b"A",b"B",b"C"],3),(4,[b"D",b"E",b"F"],3),(4,[b"D",b"E",b"F",b"G"],4),(8,[],65535)],
}
for name,packets in sets.items():
    (out/f"{name}.mold").write_bytes(b"".join(packet(seq,msgs,count) for seq,msgs,count in packets))
    stream,gaps=expected(packets)
    (out/f"{name}.stream").write_text(stream)
    (out/f"{name}.gaps").write_text(gaps)

