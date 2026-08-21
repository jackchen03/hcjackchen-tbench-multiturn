#!/usr/bin/env python3
import json
import struct
import zlib
from pathlib import Path


def varint(value):
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(out)


def encode_container(values, forced=None):
    values = sorted(values)
    runs = []
    for value in values:
        if not runs or value != runs[-1][0] + runs[-1][1]:
            runs.append([value, 1])
        else:
            runs[-1][1] += 1
    previous = 0
    array = bytearray()
    for value in values:
        array += varint(value - previous)
        previous = value
    if forced == "run" or (forced is None and len(runs) * 4 < len(array) and any(length >= 3 for _, length in runs)):
        return True, b"".join(struct.pack("<HH", start, length) for start, length in runs)
    if forced == "bitmap" or (forced is None and len(array) >= 8192):
        words = [0] * 1024
        for value in values:
            words[value // 64] |= 1 << (value % 64)
        return False, b"".join(struct.pack(">Q", word) for word in words)
    return False, bytes(array)


def write_file(path, item_ids, forced=None):
    by_key = {}
    for item in sorted(set(item_ids)):
        by_key.setdefault(item >> 16, []).append(item & 0xFFFF)
    directory, bodies, flags = [], [], bytearray((len(by_key) + 7) // 8)
    for index, (key, lows) in enumerate(sorted(by_key.items())):
        kind = forced.get(key) if isinstance(forced, dict) else forced
        is_run, body = encode_container(lows, kind)
        if is_run:
            flags[index // 8] |= 1 << (index % 8)
        directory.append(struct.pack("<HHI", key, len(lows) - 1, len(body)))
        bodies.append(body)
    payload = b"RBX1" + struct.pack("<I", len(directory)) + b"".join(directory) + bytes(flags) + b"".join(bodies)
    path.write_bytes(payload + struct.pack("<I", zlib.crc32(payload) & 0xFFFFFFFF))


def main():
    output = Path("/generated/samples")
    output.mkdir(parents=True, exist_ok=True)
    samples = {
        "dense_array.bin": ([2 * index for index in range(5000)], "array"),
        "sparse_bitmap.bin": ([3, 511, 4097, 16384, 32769, 65000], "bitmap"),
        "runs.bin": ([100000 + index for index in range(40)], "run"),
        "mixed.bin": (
            [7, 9, 11, 13, 15] + [(1 << 16) + index for index in range(200, 230)] + [(2 << 16) + value for value in (1, 70, 900, 5000)],
            {0: "array", 1: "run", 2: "bitmap"},
        ),
    }
    rows = []
    for name, (values, forced) in samples.items():
        write_file(output / name, values, forced)
        rows.append({"file": name, "item_ids": sorted(values)})
    (output / "decoded.jsonl").write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


if __name__ == "__main__":
    main()
