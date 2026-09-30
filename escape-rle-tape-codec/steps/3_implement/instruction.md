Implement /app/encoder.py as python3 /app/encoder.py <in.bin> <out.tape> so its output is byte-identical to /opt/ref/bin/tape_encode on any input, computed directly without shelling out to tape_encode. It must exit 0 and write the output file.

Grading runs your encoder on held-out tapes and checks byte identity with cmp, in an image where /opt/ref is absent, so any delegation to the reference binaries fails. Your /app/report_S1.md and /app/report_S2.md stay on disk as reference but only encoder.py output counts.
