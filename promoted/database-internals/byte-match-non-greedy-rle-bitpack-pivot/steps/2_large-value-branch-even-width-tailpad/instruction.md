# Large value branch even width tailpad

Your previous /app/encoder decodes fine but its pages still fail the byte-exact check against /verifier/legacy_encoder on many held-out columns. The divergence concentrates on columns where run and literal segments interleave near the decision boundary, on segments whose max needs an odd bit-length, on segments whose length is not a multiple of 8 with a nonzero last value, and on tie cases where two segmentations cost the same.

Tighten the existing binary at the same path /app/encoder with same invocation: stdin JSON {"values":[...]} on stdin, raw page bytes on stdout, header C0 plus u16 n. Do not re-derive the container or create a new binary elsewhere; you already have the area and conventions from last step. Now the output must be byte-for-byte identical to /verifier/legacy_encoder for every input.

Probe the legacy oracle: vary a distant value that changes a neighbor's width and watch segment boundaries move to discover non-greedy global min-cost segmentation; try max values that need odd bit-lengths to see width branch; craft tails with L%8 in 1..7 and last value nonzero vs zero to see padding difference; craft cost-tie inputs to isolate tie-break rule. You need to recover cost formulas and handle large values that need the even-round width branch and cap at 32.

The title keywords large value branch even width tailpad must appear. Keep /app/encoder self-contained and do not call legacy encoder at runtime. Keep same output contract. Preserve run-length encoding path for now.
