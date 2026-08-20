import json,sys
from pathlib import Path
root=Path(sys.argv[1])
for name,tag in (("cameras.bin",b"CAM1"),("images.bin",b"IMG1"),("points3D.bin",b"PTS1")):
    data=(root/name).read_bytes()
    if not data.startswith(tag): raise SystemExit(2)
    print(name,json.loads(data[4:]))
