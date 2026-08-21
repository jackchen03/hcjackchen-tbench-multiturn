Your previous recovery to /app/recovered.bin worked for this card. Now we need it to work across the whole batch.

Keep /app/recovered.bin intact; your new binary should be able to reproduce it when run as /app/solution/recover /app/card.img /app/recovered.bin, and any output it produces must still pass /app/tools/rptverify.

Output format contract (consistent across all steps):
- Output file must be payload-only after stripping per-block SDR1 header (4-byte magic plus stream_id/seq/plen fields) and CRC trailer (4-byte or 2-byte per firmware) and verifying CRC per block.
- `rptverify` expects payload-only file: it checks that the payload concatenation is byte-exact and that underlying blocks had valid CRCs, not that headers/CRC bytes are inside the output.
- Do NOT output raw clusters with headers/CRC still included — that will fail rptverify even if size looks right.

Only intrinsic content of the report blocks, not the FAT chain, can be trusted for recovery. The tool must discover the valid payload blocks in the raw image by scanning for SDR1 magic and valid CRC, group by stream_id, sort by seq, and reassemble payload[:plen] in order.

A further firmware change is coming, so conserve resources and keep the binary modular.
Additionally, write a short JSON report of what you fixed to /workdir/2_generalize-recover-binary_report.json.
