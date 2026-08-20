#!/usr/bin/env python3
import struct
import sys

PAGE_SIZE = 512
NONE = 0xFFFFFFFF
W_MAX = 4
EXTENT = 8


def load_fixture(path):
    data = open(path, "rb").read()
    if data[:4] != b"BTFX":
        raise ValueError("bad fixture magic")
    page_size, root, page_count = struct.unpack_from("<III", data, 4)
    if page_size != PAGE_SIZE or len(data) != page_size * page_count:
        raise ValueError("bad fixture size")
    pages = {}
    for pid in range(1, page_count):
        page = data[pid * page_size:(pid + 1) * page_size]
        if page[0] == 1:
            count = struct.unpack_from("<H", page, 2)[0]
            pages[pid] = {"type": "internal", "entries": [struct.unpack_from("<QI", page, 8 + i * 12) for i in range(count)]}
        elif page[0] == 2:
            count = struct.unpack_from("<H", page, 2)[0]
            nxt, prev = struct.unpack_from("<II", page, 4)
            keys = [struct.unpack_from("<Q", page, 16 + i * 8)[0] for i in range(count)]
            pages[pid] = {"type": "leaf", "next": None if nxt == NONE else nxt, "prev": None if prev == NONE else prev, "keys": keys}
    return root, pages


def descend(root, pages, key):
    path = []
    pid = root
    while pages[pid]["type"] == "internal":
        path.append(pid)
        entries = pages[pid]["entries"]
        child = entries[0][1]
        for minimum, candidate in entries:
            if minimum <= key:
                child = candidate
            else:
                break
        pid = child
    return path, pid


def trace(fixture, lo, hi, warm, mode):
    root, pages = load_fixture(fixture)
    internal, cur = descend(root, pages, lo)
    out = []
    seen = set()

    def emit(pid):
        if pid in warm or pid in seen:
            return False
        seen.add(pid)
        out.append(pid)
        return True

    for pid in internal:
        emit(pid)
    window = 1
    previous = None
    while cur is not None and pages[cur]["keys"][0] <= hi:
        if previous is not None:
            if mode == "final" and cur // EXTENT != previous // EXTENT:
                window = 1
            elif cur == previous + 1:
                window = min(window * 2, W_MAX)
            else:
                window = 1
        emit(cur)
        if mode != "demand":
            candidate = pages[cur]["next"]
            if mode == "naive":
                issued = 0
                while candidate is not None and issued < window:
                    if emit(candidate):
                        issued += 1
                    candidate = pages[candidate]["next"]
            else:
                budget = window
                while candidate is not None and budget:
                    if candidate // EXTENT != cur // EXTENT:
                        break
                    budget -= 1
                    emit(candidate)
                    candidate = pages[candidate]["next"]
        previous = cur
        cur = pages[cur]["next"]
    return out


def main():
    fixture, lo, hi, warm_path, output = sys.argv[1:6]
    mode = sys.argv[6] if len(sys.argv) > 6 else "final"
    warm = {int(line) for line in open(warm_path) if line.strip()}
    values = trace(fixture, int(lo), int(hi), warm, mode)
    open(output, "w").write("".join(f"{value}\n" for value in values))


if __name__ == "__main__":
    main()
