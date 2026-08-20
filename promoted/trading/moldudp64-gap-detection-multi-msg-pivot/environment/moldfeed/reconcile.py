import sys
from .parser import parse_capture

def main(capture, stream_out, gaps_out):
    store = {}
    for _session, seq, _count, messages in parse_capture(capture):
        if messages:
            store[seq] = messages[0]
        else:
            store[seq] = b""
    with open(stream_out, "w") as handle:
        for key in sorted(store):
            handle.write(store[key].hex() + "\n")
    open(gaps_out, "w").close()

if __name__ == "__main__":
    main(*sys.argv[1:4])

