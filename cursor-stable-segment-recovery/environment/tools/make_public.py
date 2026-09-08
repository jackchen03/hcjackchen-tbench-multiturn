#!/usr/bin/env python3
import hashlib
import json
import pathlib
import struct
import sys
import zlib

ZERO = "0" * 64


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def frame(header, payload):
    hb = canon(header)
    prefix = b"SGF1" + struct.pack(">III", len(hb), len(payload), zlib.crc32(hb))
    body = prefix + hb + payload + struct.pack(">I", zlib.crc32(payload))
    digest = hashlib.sha256(body).digest()
    return body + digest, digest.hex()


def add(parts, segment, prev, txid, incarnation, envelope, order, payload=b"", split=1):
    chunks = [payload[i * len(payload) // split:(i + 1) * len(payload) // split] for i in range(split)]
    for i, chunk in enumerate(chunks):
        kind = "solo" if split == 1 else ("start" if i == 0 else "seal" if i == split - 1 else "continuation")
        header = {"branch":"blue","envelope":envelope,"generation":2,"incarnation":incarnation,
                  "kind":kind,"order":order,"part":i,"parts":split,"prev":prev,
                  "segment":segment,"txid":txid}
        raw, prev = frame(header, chunk)
        parts.setdefault(segment, bytearray()).extend(raw)
    return prev


def slot_checksum(slot):
    return hashlib.sha256(canon({k:v for k,v in slot.items() if k != "checksum"})).hexdigest()


def main(out):
    out = pathlib.Path(out)
    (out / "segments").mkdir(parents=True, exist_ok=True)
    segs = {}
    prev = ZERO
    ops = lambda pairs: canon({"ops":[{"key":k,"op":"put","value":v} for k,v in pairs]})
    prev = add(segs, 1, prev, "same", 1, "data", 10, ops([("base","one")]))
    prev = add(segs, 1, prev, "same", 1, "commit", 11)
    prev = add(segs, 1, prev, "same", 1, "ack", 12)
    cross = ops([("cross","segment")])
    prev = add(segs, 1, prev, "cross", 1, "data", 20, cross[:len(cross)//2])
    # Replace the last frame's header to make this a two-part start.
    last = segs[1]
    # Rebuild the cross start at the correct shape after removing its single frame.
    # Find the preceding frame boundary by parsing the deterministic prefix.
    pos = 0
    starts = []
    while pos < len(last):
        starts.append(pos)
        hl, pl = struct.unpack(">II", last[pos+4:pos+12])
        pos += 16 + hl + pl + 4 + 32
    del last[starts[-1]:]
    prev_before_cross = hashlib.sha256(bytes(last[starts[-2]:])).hexdigest() if False else None
    # The digest before cross is the ack digest captured by walking the final frame.
    p = starts[-2]
    hl, pl = struct.unpack(">II", last[p+4:p+12])
    prev = bytes(last[p + 16 + hl + pl + 4:p + 16 + hl + pl + 36]).hex()
    h = {"branch":"blue","envelope":"data","generation":2,"incarnation":1,"kind":"start",
         "order":20,"part":0,"parts":2,"prev":prev,"segment":1,"txid":"cross"}
    raw, prev = frame(h, cross[:len(cross)//2]); last.extend(raw)
    h.update({"kind":"seal","part":1,"prev":prev,"segment":2})
    raw, prev = frame(h, cross[len(cross)//2:]); segs.setdefault(2,bytearray()).extend(raw)
    prev = add(segs, 2, prev, "cross", 1, "commit", 21)
    prev = add(segs, 2, prev, "cross", 1, "ack", 22)
    segs[2].extend(b"\x99broken-SGF1-pocket\x00")
    decoy_header = {"branch":"blue","envelope":"data","generation":2,"incarnation":9,"kind":"solo",
                    "order":30,"part":0,"parts":1,"prev":ZERO,"segment":2,"txid":"decoy"}
    raw, _ = frame(decoy_header, ops([("decoy","bad")]))
    segs[2].extend(raw)
    anchor_offset = len(segs[2])
    anchor_header = {"branch":"blue","envelope":"data","generation":2,"incarnation":1,"kind":"solo",
                     "order":40,"part":0,"parts":1,"prev":prev,"segment":2,"txid":"aborted"}
    raw, anchor_digest = frame(anchor_header, ops([("never","apply")]))
    segs[2].extend(raw); prev = anchor_digest
    prev = add(segs, 2, prev, "aborted", 1, "commit", 41)
    prev = add(segs, 2, prev, "aborted", 1, "abort", 42)
    prev = add(segs, 2, prev, "aborted", 1, "ack", 43)
    prev = add(segs, 2, prev, "same", 2, "data", 50, ops([("tail","kept")]))
    prev = add(segs, 2, prev, "same", 2, "commit", 51)
    prev = add(segs, 2, prev, "same", 2, "ack", 52)
    for n,b in segs.items(): (out / "segments" / f"seg-{n:04d}.dat").write_bytes(b)
    parent = {"anchors":[],"branch":"blue","bridges":[],"checksum":"","damage_bound":512,
              "generation":1,"parent":None,"sealed":True,"segments":[1],"sequence":1}
    parent["checksum"] = slot_checksum(parent)
    auth = {"anchors":[{"digest":anchor_digest,"offset":anchor_offset,"segment":2}],"branch":"blue",
            "bridges":[{"boundary":1,"from_branch":"legacy","from_end":4096,"from_generation":7,
                         "from_segment":9,"from_start":0}],"checksum":"","damage_bound":512,
            "generation":2,"parent":{"branch":"blue","generation":1,"sequence":1},"sealed":True,
            "segments":[1,2],"sequence":2}
    auth["checksum"] = slot_checksum(auth)
    unsealed = dict(auth); unsealed.update({"generation":5,"sequence":100,"sealed":False,"parent":None,"checksum":""}); unsealed["checksum"] = slot_checksum(unsealed)
    stale = dict(auth); stale.update({"branch":"red","generation":1,"sequence":80,"parent":None,"segments":[99],"anchors":[],"bridges":[],"checksum":""}); stale["checksum"] = slot_checksum(stale)
    (out / "manifest.json").write_bytes(canon({"slots":[unsealed,stale,parent,auth]}) + b"\n")
    (out / "README.txt").write_text("Diagnostic SegStore fixture. Run segstore recover against this directory.\n")


if __name__ == "__main__":
    main(sys.argv[1])
