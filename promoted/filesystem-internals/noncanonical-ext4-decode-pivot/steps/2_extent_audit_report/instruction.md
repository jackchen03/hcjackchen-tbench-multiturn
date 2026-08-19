Now that extraction works, we need an audit artifact for forensics that proves you understood the on-disk layout.

Using the working decoder you built at `/app/myextract`, generate an extent audit report for the files listed in `/app/samples/files.txt`.

Executable/output contract for this step:
- Build or extend an executable at `/app/decode_extents` (or extend `/app/myextract` to support audit mode) with usage: `/app/decode_extents <samples_files_list> <report_output>` or `/app/myextract --audit <image> <inode> <report>`. Canonical report output path is `/app/extent_report.json`.
- For this step, reading `/app/samples/files.txt` (each line "<image filename> <inode number>") and using your non-canonical decode logic, write a JSON array to `/app/extent_report.json` at that exact path.
- The report must be at `/app/extent_report.json` — this path must appear literally in your generation code invocation, e.g., `/app/decode_extents /app/samples/files.txt /app/extent_report.json` or `python3 /app/generate_report.py /app/samples/files.txt /app/extent_report.json`.
- Keep `/app/myextract` working with its original CLI `myextract <image> <inode>` to stdout.

Report schema (`/app/extent_report.json`):
[
  {
    "image": "<filename as in files.txt, e.g. sample1.img>",
    "inode": <int>,
    "i_size": <int>,
    "extents": [
      {"logical_block": <int>, "length": <int>, "physical_block": <int>, "is_unwritten": <bool>},
      ...
    ],
    "holes": [{"logical_block": <int>, "length": <int>}, ...]
  },
  ...
]

Requirements:
- logical_block and length are absolute logical block numbers after fully resolving the dialect (not the raw stored ee_block deltas).
- physical_block is the true data block number after masking the dialect's flag bits (0 if is_unwritten).
- is_unwritten true iff the extent must read as zeros per the reference extractor's behavior (disk may hold nonzero stale).
- holes are gaps implied by positive deltas between extents, staying zero at read time.
- Order extents by ascending logical_block as decoded.
- i_size from the inode's i_size_lo | i_size_high<<32.

After this step, `/app/extent_report.json` must exist and be valid JSON matching the schema, and `/app/myextract` must still be byte-exact.
This report path `/app/extent_report.json` will be removed in the next pivot, so keep generation isolated.
