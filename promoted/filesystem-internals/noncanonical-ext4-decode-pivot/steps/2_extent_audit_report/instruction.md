Now that extraction works, we need an audit artifact for forensics that proves you understood the on-disk layout.

Using the working decoder you built, generate an extent audit report for the files listed in /app/samples/files.txt.

Write /app/extent_report.json with exact format:

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

Do not re-explain the extractor path /app/myextract — reuse it. Keep /app/myextract working; add this report alongside. The hidden tests will check /app/extent_report.json fields against ground truth built from the same dialect rules.

Keep output path exactly /app/extent_report.json and field names logical_block, physical_block, is_unwritten, length, holes, i_size, inode, image, extents verbatim.
