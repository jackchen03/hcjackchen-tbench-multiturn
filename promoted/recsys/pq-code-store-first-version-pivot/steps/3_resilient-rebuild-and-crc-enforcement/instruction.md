# Resilient rebuild when block offsets are zeroed and enforce CRC

Your codec now decodes and encodes the sample files, but field triage showed a new failure mode. Some production pqs files have their block_offset table zeroed — older writer version left it all zeros — so the old logic that seeks each block via block offsets fails and returns garbage. Worse, a few files with bit flips slipped through because decode never checked the trailing CRC.

The block_offset table can no longer be trusted. If its entries are all zero or point outside the file, your decode_store must rebuild offsets by scanning the file sequentially using the true record length, not the nominal record_len field. The file is still well-formed — the true advance is variable length gated by the changed mask, not the fixed record_len decoy. You already handled that decoy on write, now use it for rebuilding. The old approach that blindly trusts block offsets and advances by record_len must go.

On top of that, decode_store must now verify the trailing CRC32 which is computed over bytes [0 : len-4] and stored as u32 LE at file end. If CRC mismatches, raise ValueError. And add a new helper decode_vector(path, idx) that returns the single vector at global index idx as uint8 array shape (M,) without decoding the whole file — it should also work on zeroed-offset stores by using rebuilt offsets plus scanning inside the target block.

Keep encode_store writing correct offsets and correct CRC. Keep pq_codec.py as the only deliverable. Your decoder now covers first version pivot, writer version, and resilient rebuild.
Write report to /app/3_resilient-rebuild-and-crc-enforcement_report.json.
