# Codec greedy decode ok byte mismatch

Our columnar store has an integer column encoder that has been in production for years. It compresses a column of non-negative integers into a compact page mixing run-length and bit-pack. A colleague rewrote it using the standard RLE plus bitpacking pattern they remembered from Parquet/ORC.

Now pages decode correctly — every integer comes back exactly — but our reader rejects them as corrupt on many inputs: the bytes differ from what the legacy encoder produced. The legacy binary still lives at /verifier/legacy_encoder: it reads stdin JSON {"values": [ ... ]} where values is a column of non-negative ints, and writes the encoded page as raw bytes to stdout. Under /app/samples/ you have a handful of example inputs and their expected outputs for orientation. You can run the legacy encoder freely to observe behavior.

Build an executable at /app/encoder that accepts the same stdin JSON ("values" key) and writes a page as raw bytes to stdout. The page must be structurally valid: 4-byte header with bytes 'C','0' then n as uint16 little-endian where n=len(values), followed by segments where you can read all values back exactly. At this stage we only check decode correctness and header validity, not yet byte identity against the legacy encoder — so a greedy "emit a run whenever a value repeats >=k else pack literals" implementation that produces decodable pages will pass this step, even though it byte-mismatches the reference on incompressible tails and run-boundary columns.

The title keywords byte match non greedy rle bitpack must appear in your notes. Keep the artifact at /app/encoder.

You will be tested with columns where values decode correctly despite byte mismatch. Focus on making encoding decodable and header C0 correct.
