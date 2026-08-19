# Byte-exact escape block framer

Our log storage layer packs a batch of records into a continuous segment byte stream for disk, then the reader scans for frame boundaries to split records back. A new framer was written from memory of a standard byte-stuffing idea, and it passes single-record round-trip, but when the whole segment is handed to the reader its boundary scan drops the next record on certain inputs. We need byte-for-byte identical output to the old framer.

The old framer still lives in the environment at /verifier/legacy_framer — you can run it freely to observe behavior: it reads stdin JSON of shape {"records": [ ... ]} where each element is a record's raw bytes as base64 string, and it writes the packed whole segment as raw bytes to stdout. Under /app/samples/ there are a few example inputs and their corresponding segment outputs to warm up. Construct various records, feed them, and hexdiff the outputs to learn the framing rules.


Focus for this step: discover the magic delimiter, the blocking, and the per-block footer pattern plus the trailing length encoding by probing. The segment is built from a logical stream that starts with a magic marker per record plus an escaped payload. Your current target is to match outputs for inputs that avoid ambiguous escape patterns — the samples already exhibit the block footer structure if you xxd them. Build /app/framer so it reads {"records":[b64]} and writes raw segment, matching legacy_framer on inputs that avoid the edge cases described later.

The title keywords framer and block must appear but the fix is byte-exact framing — output must be /app/framer that reads JSON and writes raw bytes, using /verifier/legacy_framer and /app/samples/ for probing.