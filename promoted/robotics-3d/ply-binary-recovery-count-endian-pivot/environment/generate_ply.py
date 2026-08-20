#!/usr/bin/env python3
import hashlib
import json
import struct
from pathlib import Path

import numpy as np


def geometry(seed, n, low, high):
    rng = np.random.default_rng(seed)
    vertices = rng.uniform(low, high, size=(n, 3)).astype(np.float32)
    colors = rng.integers(0, 256, size=(n, 3), dtype=np.uint8)
    faces = []
    for i in range(n * 2):
        if i % 101 == 0:
            a = int(rng.integers(0, n)); b = int(rng.integers(0, n)); face = [a, a, b]
        else:
            face = rng.choice(n, size=3, replace=False).astype(int).tolist()
        faces.append(face)
    return vertices, colors, faces


def header(n, face_count, format_name="binary_little_endian"):
    return (
        "ply\n"
        f"format {format_name} 1.0\n"
        "comment scanner export\n"
        f"element vertex {n}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property uchar red\nproperty uchar green\nproperty uchar blue\n"
        f"element face {face_count}\n"
        "property list uchar int vertex_indices\n"
        "end_header\n"
    ).encode("ascii")


def write_corrupted(path, vertices, colors, faces):
    body = bytearray(header(len(vertices), len(faces)))
    for xyz, rgb in zip(vertices, colors):
        body.extend(struct.pack("<ff", float(xyz[0]), float(xyz[1])))
        body.extend(struct.pack(">f", float(xyz[2])))
        body.extend(bytes(int(value) for value in rgb))
        body.append(0)
    for face in faces:
        body.extend(struct.pack("<B", len(face)))
        body.extend(struct.pack(f"<{len(face)}i", *face))
    body.extend(b"\x00" * 3_200_000)
    path.write_bytes(body)


def write_clean(path, vertices, colors, faces):
    body = bytearray(header(len(vertices), len(faces)))
    for xyz, rgb in zip(vertices, colors):
        body.extend(struct.pack("<fffBBB", *map(float, xyz), *map(int, rgb)))
    for face in faces:
        body.extend(struct.pack("<B", len(face)))
        body.extend(struct.pack(f"<{len(face)}i", *face))
    path.write_bytes(body)


def normals(vertices, faces):
    points = vertices.astype(np.float64)
    accum = np.zeros_like(points)
    for face in faces:
        if len(face) < 3:
            continue
        origin = points[face[0]]
        for index in range(1, len(face) - 1):
            cross = np.cross(points[face[index]] - origin, points[face[index + 1]] - origin)
            if np.linalg.norm(cross) <= 1e-12:
                continue
            for vertex_index in (face[0], face[index], face[index + 1]):
                accum[vertex_index] += cross
    lengths = np.linalg.norm(accum, axis=1)
    result = np.zeros_like(accum)
    nonzero = lengths > 1e-12
    result[nonzero] = accum[nonzero] / lengths[nonzero, None]
    return result


def write_case(root, name, seed, n, low, high, visible=False):
    vertices, colors, faces = geometry(seed, n, low, high)
    corrupted = root / f"{name}_corrupted.ply"
    write_corrupted(corrupted, vertices, colors, faces)
    np.save(root / f"{name}_vertices.npy", vertices, allow_pickle=False)
    np.save(root / f"{name}_colors.npy", colors, allow_pickle=False)
    np.save(root / f"{name}_normals.npy", normals(vertices, faces), allow_pickle=False)
    (root / f"{name}_faces.json").write_text(json.dumps(faces), encoding="utf-8")
    write_clean(root / f"{name}_expected_recovered.ply", vertices, colors, faces)
    return corrupted


def main():
    data = Path("/app/data"); data.mkdir(parents=True, exist_ok=True)
    grader = Path("/opt/grader"); grader.mkdir(parents=True, exist_ok=True)
    sample_root = grader / "sample"; hidden = grader / "hidden"
    sample_root.mkdir(); hidden.mkdir()
    sample_corrupted = write_case(sample_root, "sample", 42, 960, -2.0, 3.0)
    (data / "scan_corrupted.ply").write_bytes(sample_corrupted.read_bytes())
    (grader / "sample_input.sha256").write_text(hashlib.sha256(sample_corrupted.read_bytes()).hexdigest() + "\n")
    write_case(hidden, "hidden_a", 1337, 1103, 10.0, 31.0)
    write_case(hidden, "hidden_b", 4242, 1257, -17.0, 8.0)


if __name__ == "__main__":
    main()
