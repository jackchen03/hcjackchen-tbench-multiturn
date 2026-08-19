# Add byte-identical writer

Your previous fix makes decode_store correct on the samples. Now the write side is missing.

Add encode_store(codes, out_path) to the same /app/pq_codec.py. It takes a uint8 array shaped (N, M) and must write a pqs file to out_path that is byte-identical to what the lost canonical writer would produce — the grader will compare bytes exactly. The file must also be accepted by /app/pq_store_validate (return 0) and when you read it back with your own decode_store it must match the input array exactly.

Don't hardcode sample bytes or special-case existing files. The format itself must be understood — read and write have to match on bytes. Keep the same API; you already know where the store samples and ground truth live from last step.
Write report to /app/2_encode-byte-identical-writer_report.json.
