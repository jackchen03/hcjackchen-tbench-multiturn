#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

SOH = b"\x01"


def field(tag, value):
    if isinstance(value, bytes):
        return str(tag).encode() + b"=" + value + SOH
    return f"{tag}={value}".encode() + SOH


def message(symbol, price, data_pair=None, payload=b""):
    parts = [field(8, "FIX.4.4"), field(9, 0), field(35, "W"), field(55, symbol)]
    if data_pair is not None:
        length_tag, data_tag = data_pair
        parts.extend([field(length_tag, len(payload)), field(data_tag, payload)])
    parts.append(field(270, price))
    prefix = b"".join(parts)
    checksum = sum(prefix) % 256
    return prefix + field(10, f"{checksum:03d}")


def main(feed_path, expected_path):
    rows = [("AAA", "101.25"), ("BBB", "202.50"), ("CCC", "303.75")]
    payload = b"raw-prefix\x0110=042\x01raw-suffix"
    feed = (
        message("AAA", "101.25")
        + message("BBB", "202.50", (95, 96), payload)
        + message("CCC", "303.75")
    )
    feed_file = Path(feed_path)
    feed_file.parent.mkdir(parents=True, exist_ok=True)
    feed_file.write_bytes(feed)
    expected = Path(expected_path)
    with expected.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["symbol", "price"])
        writer.writerows(rows)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

