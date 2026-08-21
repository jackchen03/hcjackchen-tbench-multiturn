Your previous `/app/run.sh` that matched kernel `SEEK_HOLE`/`SEEK_DATA` on plain sparse interior holes still fails on the next image set — same paths, different extent types.

Two new behaviors are now probed:

- Files created with `fallocate` produce extents that read as all-zeros on disk yet the kernel reports them as `DATA`, never a hole. In the raw extent tree leaf, this is an unwritten / preallocated extent: the high bit of `ee_len` flags it. When `ee_len > 0x8000`, true length is `ee_len - 0x8000` and it must still be treated as mapped data. Content-based zero scanning that reports those zeros as holes is wrong for `seek hole data kernel match`.

- `EOF` cutoff dominates the map. There are two places this bites: a query with offset `off >= i_size` must return `ENXIO` for both `SEEK_HOLE` and `SEEK_DATA`, even if that logical block is mapped (fallocate past EOF). Second, for `SEEK_DATA` in the trailing hole before `EOF`, result must be `ENXIO` (not `i_size`), while `SEEK_HOLE` when file is mapped up to `i_size` with no interior hole must return `i_size` itself. Same `i_size` value has two different conventions — `SEEK_HOLE` returns `S = i_size`, `SEEK_DATA` returns `ENXIO`.

Update the same `/app/run.sh` you already have to handle both: parse leaf `ee_len` with `0x8000` unwritten mask, treat unwritten as mapped, apply `off >= i_size` -> `ENXIO` check first before map lookup, and implement the trailing-hole `ENXIO` vs `S` split. For this step you may still use `debugfs -R stat` and `debugfs -R dump_extents` and `dumpe2fs -h` subprocess calls to resolve extent maps — raw parsing is deferred to next step, so `debugfs` usage is allowed here.

Keep the existing `/app/run.sh <image_path> <queries_file> <output_file>` contract and output format (`ENXIO` literal or decimal offset). Do not re-create the tool from scratch — fix the extent-map logic you already ship, keeping `debugfs` if you use it.

You can still validate against `/app/samples/` with `expected_*.txt`, but grading now includes held-out images with unwritten extents wholly below `i_size` and queries with `off >= S`.
