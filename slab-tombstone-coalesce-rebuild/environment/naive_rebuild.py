#!/usr/bin/env python3
import struct
import sys

PAGE = 4096


def rebuild(raw):
    if len(raw) != PAGE or raw[:4] != b"SLBP":
        raise ValueError("not a 4096-byte SLBP page")
    count = struct.unpack_from("<H", raw, 10)[0]
    slot_start = PAGE - 8 * count
    slots = [struct.unpack_from("<HHHH", raw, slot_start + 8 * i) for i in range(count)]
    out = bytearray(PAGE)
    out[:4] = b"SLBP"
    cursor = 16
    live = []
    for offset, length, is_live, _ in slots:
        if is_live:
            out[cursor : cursor + length] = raw[offset : offset + length]
            live.append((cursor, length, 1, 0))
            cursor += length
    new_slot_start = PAGE - 8 * len(live)
    for i, slot in enumerate(sorted(live)):
        struct.pack_into("<HHHH", out, new_slot_start + 8 * i, *slot)
    struct.pack_into("<HHHH", out, 4, len(live), cursor, 0, len(live))
    return bytes(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: naive_rebuild.py IN OUT")
    with open(sys.argv[1], "rb") as source:
        raw = source.read()
    with open(sys.argv[2], "wb") as target:
        target.write(rebuild(raw))
