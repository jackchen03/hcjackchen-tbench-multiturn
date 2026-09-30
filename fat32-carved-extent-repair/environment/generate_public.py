#!/usr/bin/env python3
"""Build the public damaged FAT32 image; this file stays in the builder stage."""

import hashlib
import os
import random
import sqlite3
import struct
import subprocess
import sys
import tempfile

SEED = 2001
MTIME = "2024-01-02 03:04:05"
EOC = 0x0FFFFFF8


def run(argv):
    subprocess.run(argv, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def mkdb(path, name, rows):
    con = sqlite3.connect(path)
    con.execute("CREATE TABLE filemeta(name TEXT)")
    con.execute("INSERT INTO filemeta VALUES(?)", (name,))
    con.execute("CREATE TABLE records(id INTEGER PRIMARY KEY, payload TEXT)")
    con.executemany(
        "INSERT INTO records(payload) VALUES(?)",
        [(f"payload-{SEED}-{i:04d}-data",) for i in range(rows)],
    )
    con.commit()
    con.close()


def geometry(image):
    bps = struct.unpack_from("<H", image, 11)[0]
    spc = image[13]
    reserved = struct.unpack_from("<H", image, 14)[0]
    fats = image[16]
    fat_sectors = struct.unpack_from("<I", image, 36)[0]
    root = struct.unpack_from("<I", image, 44)[0]
    fat1 = reserved * bps
    fat_bytes = fat_sectors * bps
    return {
        "fat1": fat1,
        "fat2": fat1 + fat_bytes,
        "fat_bytes": fat_bytes,
        "data": (reserved + fats * fat_sectors) * bps,
        "cluster_size": bps * spc,
        "root": root,
    }


def fat_value(image, offset, cluster):
    return struct.unpack_from("<I", image, offset + cluster * 4)[0] & 0x0FFFFFFF


def walk(image, offset, start):
    chain = []
    cluster = start
    while True:
        chain.append(cluster)
        nxt = fat_value(image, offset, cluster)
        if nxt >= EOC:
            return chain
        cluster = nxt
        if len(chain) > 100000:
            raise RuntimeError("FAT chain loop")


def short_name(name):
    base, ext = name.split(".")
    return (base.ljust(8) + ext.ljust(3)).encode("ascii")


def main():
    output = os.path.abspath(sys.argv[1])
    with tempfile.TemporaryDirectory() as tmp:
        image_path = os.path.join(tmp, "disk.img")
        with open(image_path, "wb") as handle:
            handle.truncate(36 * 1024 * 1024)
        run(["mkfs.vfat", "-F", "32", "-n", "TESTDISK", "-s", "1", "-i", f"{SEED:08X}", image_path])
        names = ("NOTES.DB", "CACHE.DB")
        rows = (11, 7)
        sources = []
        for index, (name, count) in enumerate(zip(names, rows)):
            path = os.path.join(tmp, f"db{index}.sqlite")
            mkdb(path, name, count)
            run(["touch", "-d", MTIME, path])
            sources.append(path)
        filler = os.path.join(tmp, "fill.bin")
        with open(filler, "wb") as handle:
            handle.write(random.Random(SEED).randbytes(8192))
        run(["touch", "-d", MTIME, filler])
        run(["mcopy", "-i", image_path, filler, "::FILLER.BIN"])
        for name, path in zip(names, sources):
            run(["mcopy", "-i", image_path, path, "::" + name])

        image = bytearray(open(image_path, "rb").read())
        geo = geometry(image)
        root_offset = geo["data"] + (geo["root"] - 2) * geo["cluster_size"]
        entries = {}
        index = 0
        while True:
            entry = image[root_offset + index * 32:root_offset + (index + 1) * 32]
            if entry[0] == 0:
                break
            if entry[11] not in (0x08, 0x0F):
                low = struct.unpack_from("<H", entry, 26)[0]
                high = struct.unpack_from("<H", entry, 20)[0]
                size = struct.unpack_from("<I", entry, 28)[0]
                entries[bytes(entry[:11])] = (index, (high << 16) | low, size)
            index += 1

        first = entries[short_name(names[0])]
        second = entries[short_name(names[1])]
        chain_b = walk(image, geo["fat2"], second[1])
        tail_count = len(chain_b) // 2
        predecessor = chain_b[-tail_count - 1]
        old_tail = chain_b[-tail_count:]
        clusters = (len(image) - geo["data"]) // geo["cluster_size"]
        new_start = 2000
        while not all(fat_value(image, geo["fat2"], c) == 0 for c in range(new_start, new_start + tail_count)):
            new_start += 1
        new_tail = list(range(new_start, new_start + tail_count))
        for old, new in zip(old_tail, new_tail):
            old_offset = geo["data"] + (old - 2) * geo["cluster_size"]
            new_offset = geo["data"] + (new - 2) * geo["cluster_size"]
            image[new_offset:new_offset + geo["cluster_size"]] = image[old_offset:old_offset + geo["cluster_size"]]
            image[old_offset:old_offset + geo["cluster_size"]] = b"\0" * geo["cluster_size"]
            for fat in (geo["fat1"], geo["fat2"]):
                struct.pack_into("<I", image, fat + old * 4, 0)
        for fat in (geo["fat1"], geo["fat2"]):
            struct.pack_into("<I", image, fat + predecessor * 4, new_start)
            for pos, cluster in enumerate(new_tail):
                nxt = new_tail[pos + 1] if pos + 1 < len(new_tail) else 0x0FFFFFFF
                struct.pack_into("<I", image, fat + cluster * 4, nxt)

        heads = (first[1], second[1])
        low = max(2, min(heads) - 2 - (SEED % 3))
        high = max(heads) + 8 + (SEED % 5)
        for cluster in range(low, high + 1):
            struct.pack_into("<I", image, geo["fat1"] + cluster * 4, 0)
        for item, is_first in ((first, True), (second, False)):
            index, _, _ = item
            image[root_offset + index * 32] = 0xE5
            if not is_first:
                struct.pack_into("<H", image, root_offset + index * 32 + 20, 0x0BAD + SEED % 7)
        with open(output, "wb") as handle:
            handle.write(image)
        run(["touch", "-d", MTIME, output])
        assert hashlib.sha256(image).hexdigest()


if __name__ == "__main__":
    main()
