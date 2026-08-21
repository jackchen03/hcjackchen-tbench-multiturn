#!/usr/bin/env python3
import json
import random
import struct
from pathlib import Path

from refscan import EXTENT, NONE, PAGE_SIZE, trace

ROOT = 2
KEYS_PER_LEAF = 4


def fixture(path, chain, base):
    count = max(chain + [ROOT]) + 1
    image = bytearray(count * PAGE_SIZE)
    struct.pack_into("<4sIII", image, 0, b"BTFX", PAGE_SIZE, ROOT, count)
    root = ROOT * PAGE_SIZE
    image[root] = 1
    struct.pack_into("<H", image, root + 2, len(chain))
    for index, pid in enumerate(chain):
        minimum = base + index * 10
        struct.pack_into("<QI", image, root + 8 + index * 12, minimum, pid)
        offset = pid * PAGE_SIZE
        image[offset] = 2
        struct.pack_into("<HII", image, offset + 2, KEYS_PER_LEAF, chain[index + 1] if index + 1 < len(chain) else NONE, chain[index - 1] if index else NONE)
        for key_index in range(KEYS_PER_LEAF):
            struct.pack_into("<Q", image, offset + 16 + key_index * 8, minimum + key_index)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(image)


def write_case(directory, name, fixture_path, base, chain, start, finish, warm):
    case = directory / name
    case.mkdir(parents=True, exist_ok=True)
    lo = base + start * 10 + 1
    hi = base + finish * 10 + 3
    warm_path = case / "warm.txt"
    warm_path.write_text("".join(f"{pid}\n" for pid in sorted(set(warm))))
    def runtime_path(path):
        value = str(path)
        return value.replace("/generated/app", "/app").replace("/generated/grader", "/opt/grader")
    meta = {"fixture": runtime_path(fixture_path), "lo": lo, "hi": hi, "warm": runtime_path(warm_path)}
    (case / "case.json").write_text(json.dumps(meta, sort_keys=True))
    warm_set = set(warm)
    for mode in ("demand", "naive", "final"):
        values = trace(str(fixture_path), lo, hi, warm_set, mode)
        (case / f"{mode}.txt").write_text("".join(f"{value}\n" for value in values))


def main():
    generated = Path("/generated")
    app = generated / "app"
    grader = generated / "grader"
    main_chain = [4,5,6,7,8,9,10,15,16,17,18,19,20,21,22,31,32,33,34,35,36,37,38,12,13,14,23,24,25,26,27,28,29,30,39,40,41,42,43,44]
    alt_chain = [50,51,52,53,54,55,56,63,64,65,66,67,68,69,70,71,14,15,16,17,18,19,20,21,31,30,29,28,27,26,25,24]
    main_fixture = app / "fixture"
    alt_fixture = grader / "fixture_alt"
    fixture(main_fixture, main_chain, 1000)
    fixture(alt_fixture, alt_chain, 50000)
    (grader / "fixture_main").write_bytes(main_fixture.read_bytes())

    samples = app / "samples"
    write_case(samples / "demand", "cold", main_fixture, 1000, main_chain, 1, 5, [])
    write_case(samples / "demand", "warm", main_fixture, 1000, main_chain, 8, 13, [ROOT, main_chain[10]])
    write_case(samples / "prefetch", "cold", main_fixture, 1000, main_chain, 10, 14, [])
    write_case(samples / "prefetch", "reset", main_fixture, 1000, main_chain, 20, 25, [])
    write_case(samples / "full", "warm_extent", main_fixture, 1000, main_chain, 2, 12, [main_chain[4], main_chain[7]])

    cases = grader / "cases"
    rng = random.Random(0x13A04723)
    definitions = []
    for index in range(32):
        use_alt = index % 4 == 3
        chain = alt_chain if use_alt else main_chain
        base = 50000 if use_alt else 1000
        fpath = grader / ("fixture_alt" if use_alt else "fixture_main")
        start = rng.randrange(0, len(chain) - 8)
        finish = min(len(chain) - 1, start + rng.randrange(4, 12))
        warm = []
        if index % 3 == 1:
            warm.append(chain[min(finish + 2, start + 3)])
        if index % 5 == 2:
            warm.append(chain[start])
        if index % 7 == 4:
            warm.append(ROOT)
        name = f"case_{index:02d}"
        write_case(cases, name, fpath, base, chain, start, finish, warm)
        definitions.append(name)
    (grader / "manifest.json").write_text(json.dumps(definitions))

    # Build-time guard: the suite must contain real dialect separation.
    different = 0
    for name in definitions:
        case = cases / name
        if (case / "naive.txt").read_bytes() != (case / "final.txt").read_bytes():
            different += 1
    assert different >= 8
    assert any(pid // EXTENT != (pid - 1) // EXTENT for pid in main_chain)


if __name__ == "__main__":
    main()
