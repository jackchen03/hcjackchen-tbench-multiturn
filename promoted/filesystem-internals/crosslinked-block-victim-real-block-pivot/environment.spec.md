# Environment spec

FROM public.ecr.aws/docker/library/python:3.11-slim
- base: pinned Debian bookworm variant as of 2024-12, python 3.11.10
- apt-get: e2fsprogs=1.47.0-2+deb12u1 (provides mke2fs, fsck.ext4, debugfs, dumpe2fs), coreutils, util-linux, file, faketime optional for deterministic mtimes
  ```
  apt-get update && apt-get install -y --no-install-recommends \
    e2fsprogs=1.47.0-2+deb12u1 \
    coreutils \
    util-linux \
    file \
  && rm -rf /var/lib/apt/lists/*
  ```
- pip: pytest==8.3.4 only (stdlib struct, os, json, sys used)
  ```
  pip install --no-cache-dir pytest==8.3.4
  ```
- deterministic: build-time image synthesis uses `faketime "2020-01-01 00:00:00"` for mke2fs and fixed UUIDs `-U <fixed-uuid>` per instance, seeded PRNG (python random.Random(seed) pinned per instance) for file contents, pinned interior offset k in (0, L-1)
- planted state:
  - /work/disk.img — target broken image for step1, 64 MiB ext4, `-b 4096 -O extent,^metadata_csum,^64bit -E root_owner=0:0`, contains aggressor file >=4 blocks contiguous single extent, victim single-block file whose ee_start overwritten to D=S+k interior of aggressor, other ordinary files. fsck -n reports multiply-claimed + leaked, `debugfs cat victim` returns aggressor block-k bytes.
  - /work/example/broken.img + /work/example/original.img — different instance same class, disjoint block numbers/content/layout, for understanding only.
  - /opt/holdout/ root:root 700 — heldout_broken_0.img, heldout_broken_1.img (single-leak inline), heldout_deep_0.img (depth>0 index leaf), heldout_multi_leak_0.img (2-3 leaks, one victim real, others orphan), each with manifest json holding per-inode path->sha256 original, A path, B path, P_B, D, orphan list. Also .canary file containing canary GUID.
- allow_internet: false — offline, no network needed, pip pinned
- no prior-run artifacts: /solution not pre-created, /app empty except task files, /work writable for disk.img in-place fix
- canary GUID: TBENCH-MT-FSINT-XLINK-24-ac3c809e-ad1b-475d-a562-0488d8299043 to be copied into final Dockerfile + each solve.sh + test.sh/test_outputs.py by Codex

What Codex must NOT invent: different base image, different e2fsprogs version unpinned, extra python deps, network fetches, mount/loop/fuse usage (container unprivileged without CAP_SYS_ADMIN). Must keep Dockerfile FROM ECR python:3.11-slim and pip pytest.
