#!/usr/bin/env python3
import os
import struct
import sys
from pathlib import Path

PAGE = 4096


def specification(seed):
    geometry_seed = 11 if seed in (21, 22) else seed
    base = (geometry_seed * 7 + geometry_seed // 5) % 5
    sizes = [64 + ((base + i * 13) % 5) * 32 for i in range(6)]
    kills_by_seed = {
        11: [1, 3],
        12: [5, 3, 2],
        21: [4, 1],
        22: [2, 3],
    }
    return sizes, kills_by_seed[seed]


def payload(seed, index, size):
    return bytes(65 + ((seed + index * 3 + j) % 26) for j in range(size))


def make_page(seed):
    sizes, kills = specification(seed)
    death = {record: order + 1 for order, record in enumerate(kills)}
    page = bytearray(PAGE)
    page[:4] = b"SLBP"
    offset = 16
    offsets = []
    for index, size in enumerate(sizes):
        page[offset : offset + size] = payload(seed, index, size)
        offsets.append(offset)
        offset += size
    slot_start = PAGE - 8 * len(sizes)
    page[offset:slot_start] = bytes([0xCC]) * (slot_start - offset)
    for index, size in enumerate(sizes):
        struct.pack_into(
            "<HHHH",
            page,
            slot_start + 8 * index,
            offsets[index],
            size,
            0 if index in death else 1,
            death.get(index, 0),
        )
    struct.pack_into("<HHHH", page, 4, len(sizes), offset, len(kills), len(sizes))
    return bytes(page)


def main():
    root = Path(sys.argv[1])
    root.mkdir(parents=True, exist_ok=True)
    names = {
        11: "frag_11.bin",
        12: "frag_12.bin",
        21: "mutant_order.bin",
        22: "mutant_coalesce.bin",
    }
    for seed, name in names.items():
        path = root / name
        path.write_bytes(make_page(seed))
        os.utime(path, (1577836800, 1577836800))


if __name__ == "__main__":
    main()
