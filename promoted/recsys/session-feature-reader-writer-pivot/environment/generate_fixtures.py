#!/usr/bin/env python3
import json
import struct
import sys
import zlib
from pathlib import Path


def zigzag(value):
    return value * 2 if value >= 0 else -value * 2 - 1


def varint(value):
    result = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        result.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(result)


def encode(sessions):
    records = bytearray(b"SFS1" + struct.pack("<I", len(sessions)))
    for session in sessions:
        events = session["events"]
        items = sorted(event["item_id"] for event in events)
        anchor = items[(len(items) - 1) // 2]
        records += struct.pack("<IBI", session["session_id"], len(events), anchor)
        for event in events:
            records += varint(zigzag(event["item_id"] - anchor))
        for event in events:
            encoded = zigzag(event["ts_delta"])
            rest = encoded >> 4
            records.append((event["recency_bucket"] << 5) | (0x10 if rest else 0) | (encoded & 0x0F))
            if rest:
                records += varint(rest)
    records += b"\xff\xff"
    checksum = zlib.crc32(records) & 0xFFFFFFFF
    pad_length = (-(len(records) + 4)) % 64
    return bytes(records) + bytes(pad_length) + struct.pack("<I", checksum)


SAMPLES = [
    [
        {"session_id": 1101, "events": [{"item_id": 905, "ts_delta": 0, "recency_bucket": 0}, {"item_id": 860, "ts_delta": 19, "recency_bucket": 4}, {"item_id": 940, "ts_delta": -37, "recency_bucket": 7}, {"item_id": 880, "ts_delta": 8, "recency_bucket": 2}]},
        {"session_id": 1102, "events": [{"item_id": 1500, "ts_delta": 127, "recency_bucket": 1}, {"item_id": 1320, "ts_delta": -2, "recency_bucket": 6}, {"item_id": 1410, "ts_delta": 3, "recency_bucket": 3}]},
    ],
    [
        {"session_id": 2201, "events": [{"item_id": 42000, "ts_delta": 4097, "recency_bucket": 5}, {"item_id": 41700, "ts_delta": -4096, "recency_bucket": 0}]},
        {"session_id": 2202, "events": [{"item_id": 73, "ts_delta": 15, "recency_bucket": 7}, {"item_id": 91, "ts_delta": 16, "recency_bucket": 1}, {"item_id": 64, "ts_delta": 17, "recency_bucket": 2}, {"item_id": 108, "ts_delta": 18, "recency_bucket": 3}, {"item_id": 82, "ts_delta": 19, "recency_bucket": 4}]},
    ],
    [{"session_id": 3301, "events": [{"item_id": 800000, "ts_delta": -99999, "recency_bucket": 6}, {"item_id": 700001, "ts_delta": 99999, "recency_bucket": 2}, {"item_id": 750000, "ts_delta": -1, "recency_bucket": 5}, {"item_id": 760000, "ts_delta": 1, "recency_bucket": 0}]}],
    [
        {"session_id": 4401, "events": [{"item_id": 250, "ts_delta": 31, "recency_bucket": 3}]},
        {"session_id": 4402, "events": [{"item_id": 999, "ts_delta": 32, "recency_bucket": 4}, {"item_id": 1001, "ts_delta": 33, "recency_bucket": 5}, {"item_id": 998, "ts_delta": 34, "recency_bucket": 6}, {"item_id": 1005, "ts_delta": 35, "recency_bucket": 7}]},
    ],
    [{"session_id": 5501, "events": [{"item_id": 34567, "ts_delta": -1234567, "recency_bucket": 1}, {"item_id": 12345, "ts_delta": 7654321, "recency_bucket": 2}, {"item_id": 23456, "ts_delta": 0, "recency_bucket": 3}]}],
]


def main(output_directory):
    target = Path(output_directory)
    target.mkdir(parents=True, exist_ok=True)
    sidecar = []
    for index, sessions in enumerate(SAMPLES):
        name = f"shard_{index:03d}.bin"
        (target / name).write_bytes(encode(sessions))
        sidecar.append({"shard": name, "sessions": sessions})
    with (target / "sessions.jsonl").open("w") as handle:
        for entry in sidecar:
            handle.write(json.dumps(entry, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
