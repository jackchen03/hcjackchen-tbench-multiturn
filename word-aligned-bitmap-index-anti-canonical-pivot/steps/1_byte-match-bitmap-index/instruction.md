# Byte match bitmap index

Our storage engine has a secondary bitmap index writer that was recently rewritten. The rewritten version writes index files that are no longer byte-for-byte identical to what the old tool produced. Downstream checksum and cache logic is hard-coded to the old tool's byte layout, so we need the new tool to write exactly the same bytes as the old tool – not just semantically equivalent or decodes back to same bits.

The old tool still lives at /app/reference/bitmap_index and you can run it freely to observe its behavior on various inputs. It will be removed in production soon, so you cannot depend on calling it in your final solution – you must figure out its on-disk format and replicate it. Under /app/samples you have a few paired inputs and their outputs for orientation.

Input convention: program reads from stdin JSON like {"nbits": N, "positions": [...]} where nbits is total number of bits and positions is a sorted, deduped list of set-bit indices that are set to 1 and less than N. Program must write the encoded index file verbatim to stdout as raw binary.

Put an executable program at /app/indexer that for the same input produces byte-identical output as /app/reference/bitmap_index. We will test it with bitmaps you have not seen before that are disjoint from samples, doing byte-for-byte compare, so make sure it matches for any legal input not just the handful of samples.

The title keywords word aligned bitmap index anti canonical pivot must appear in your notes. Keep artifact at /app/indexer and keep invocation as stdin JSON to stdout bytes.
