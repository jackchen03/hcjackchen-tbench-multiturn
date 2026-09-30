#!/usr/bin/env python3
from pathlib import Path

FE = 0xFE
ROOT = Path("/data/tapes")
ROOT.mkdir(parents=True, exist_ok=True)

fixtures = {
    "long_200x41.bin": bytes([0x41]) * 200 + b"hello" + bytes([0x42]) * 5 + bytes([0x43]) * 130 + b"end",
    "short_5x42.bin": b"hi" + bytes([0x42]) * 5 + b"bye",
    "short_hello.bin": b"hello world",
    "edge_FE.bin": b"A" + bytes([FE]) + b"B",
    "edge_FEFE.bin": bytes([FE]) * 5,
    "edge_41FE41.bin": bytes([0x41]) * 5 + bytes([FE]) + b"A",
    "literal_hello.bin": b"hello",
}
for name, data in fixtures.items():
    path = ROOT / name
    path.write_bytes(data)
    path.chmod(0o444)
