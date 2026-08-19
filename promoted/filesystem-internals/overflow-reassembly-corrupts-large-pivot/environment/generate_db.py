#!/usr/bin/env python3
import hashlib
import json
import random
import struct
import sys
from pathlib import Path


def varint(value):
    if value <= 0x7F:
        return bytes([value])
    chunks = []
    while value:
        chunks.append(value & 0x7F)
        value >>= 7
    chunks.reverse()
    return bytes((chunk | 0x80) if index < len(chunks) - 1 else chunk for index, chunk in enumerate(chunks))


def local_size(payload, usable):
    maximum = usable - 35
    if payload <= maximum:
        return payload
    minimum = ((usable - 12) * 32 // 255) - 23
    candidate = minimum + ((payload - minimum) % (usable - 4))
    return candidate if candidate <= maximum else minimum


def record(blob):
    serial = 12 + len(blob) * 2
    serial_bytes = varint(serial)
    header_size = 2 + len(serial_bytes)
    header = varint(header_size) + b"\x00" + serial_bytes
    return header + blob


def create(path, page_size, reserved, rows, seed, truth_path):
    usable = page_size - reserved
    payloads = {rowid: record(blob) for rowid, blob in rows.items()}
    leaf_pages = {rowid: index + 2 for index, rowid in enumerate(rows)}
    next_page = 2 + len(rows)
    chains = {}
    for rowid, payload in payloads.items():
        local = local_size(len(payload), usable)
        remaining = payload[local:]
        chain = []
        while remaining:
            chain.append(next_page)
            next_page += 1
            remaining = remaining[usable - 4:]
        chains[rowid] = chain
    pages = [bytearray(page_size) for _ in range(next_page - 1)]
    header = pages[0]
    header[:16] = b"SQLite format 3\x00"
    struct.pack_into(">H", header, 16, 1 if page_size == 65536 else page_size)
    header[18] = header[19] = 1
    header[20] = reserved
    struct.pack_into(">I", header, 28, len(pages))
    struct.pack_into(">I", header, 44, 4)
    for rowid, payload in payloads.items():
        page = pages[leaf_pages[rowid] - 1]
        local = local_size(len(payload), usable)
        prefix = varint(len(payload)) + varint(rowid)
        cell = prefix + payload[:local]
        if chains[rowid]:
            cell += struct.pack(">I", chains[rowid][0])
        offset = usable - len(cell)
        page[0] = 0x0D
        struct.pack_into(">H", page, 3, 1)
        struct.pack_into(">H", page, 5, offset)
        struct.pack_into(">H", page, 8, offset)
        page[offset:offset + len(cell)] = cell
        if reserved:
            page[usable:] = bytes([0xA5]) * reserved
        remaining = payload[local:]
        for index, page_number in enumerate(chains[rowid]):
            overflow = pages[page_number - 1]
            following = chains[rowid][index + 1] if index + 1 < len(chains[rowid]) else 0
            struct.pack_into(">I", overflow, 0, following)
            chunk = remaining[:usable - 4]
            overflow[4:4 + len(chunk)] = chunk
            remaining = remaining[len(chunk):]
            if reserved:
                overflow[usable:] = bytes([0x5A]) * reserved
    header[20] = 0
    header[100:] = bytes(page_size - 100)
    path.write_bytes(b"".join(pages))
    truth = {str(rowid): hashlib.sha256(blob).hexdigest() for rowid, blob in rows.items()}
    truth_path.write_text(json.dumps(truth, sort_keys=True) + "\n", encoding="utf-8")


def main(output_dir):
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    rng = random.Random(0xC58C0432)
    rows = {
        1: rng.randbytes(900),
        2: rng.randbytes(1500),
        3: rng.randbytes(20000),
        4: rng.randbytes(45000),
        5: rng.randbytes(1200),
    }
    rows[6] = rows[3]
    create(root / "broken.sqlite", 4096, 32, rows, 0xC58C0432, root / "truth.json")
    held_rng = random.Random(0x6FD1774B)
    held = {
        7: held_rng.randbytes(700),
        19: held_rng.randbytes(2400),
        20: held_rng.randbytes(26000),
        103: held_rng.randbytes(61000),
        250: held_rng.randbytes(1300),
    }
    held[88] = held[20]
    create(root / "held.sqlite", 8192, 20, held, 0x6FD1774B, root / "held_truth.json")


if __name__ == "__main__":
    main(sys.argv[1])
