Now that extraction works, we need an audit artifact for forensics that proves you understood the on-disk layout.

Using the working decoder you built, generate an extent audit report for the files listed in /app/samples/files.txt.


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
