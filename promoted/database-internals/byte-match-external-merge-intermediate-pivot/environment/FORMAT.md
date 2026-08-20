# PolySort binary formats

- Input records are exactly 24 bytes: `key` as unsigned 64-bit big-endian followed by a 16-byte payload.
- Spill files begin with big-endian `magic u32` (`0x52554E46`), `record_count u32`, `pass_depth u16`, and reserved `u16` zero. Records are `key u64`, payload 16 bytes, and `stamp u64`, all integers big-endian.
- Spill names are `run_%04u.bin` in global creation order.
- Final output contains only the 24-byte key+payload records, ordered by ascending key with the recovered dialect tie-break.
