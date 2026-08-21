#!/usr/bin/env python3
from pathlib import Path
import subprocess


SAMPLES = {
    "basic.feed": """A 101 B 10000 9
A 102 B 10000 5
A 201 S 10005 7
E 101 3
U 102 112 10000 3
""",
    "levels.feed": """A 301 B 9998 4
A 302 B 10002 8
A 401 S 10008 6
A 402 S 10004 11
X 401 2
""",
}


def main():
    output = Path("/generated/sample")
    output.mkdir(parents=True, exist_ok=True)
    for name, body in SAMPLES.items():
        feed = output / name
        feed.write_text(body, encoding="utf-8")
        expected = output / name.replace(".feed", ".expected")
        result = subprocess.run(["/build/refbook", str(feed)], check=True, capture_output=True)
        expected.write_bytes(result.stdout)


if __name__ == "__main__":
    main()
