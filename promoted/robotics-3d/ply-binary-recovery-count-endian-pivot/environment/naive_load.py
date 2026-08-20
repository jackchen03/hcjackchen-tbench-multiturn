#!/usr/bin/env python3
import sys
import numpy as np
from plyfile import PlyData

ply = PlyData.read(sys.argv[1])
v = ply["vertex"].data
xyz = np.column_stack([v["x"], v["y"], v["z"]])
print("vertices", len(v), "bbox", xyz.min(axis=0).tolist(), xyz.max(axis=0).tolist())
if "face" in ply:
    print("faces", len(ply["face"].data), "first", ply["face"].data[:3])
