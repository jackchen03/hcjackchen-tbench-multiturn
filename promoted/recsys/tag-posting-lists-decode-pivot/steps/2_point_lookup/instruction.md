Decoding is fixed, now serving path is too heavy — it decodes full lists for every point check.

Add a fast point lookup that reuses the index format without full decoding. Write /app/postings_lookup.py invoked as `python3 /app/postings_lookup.py <index_dir> <tag> <doc_id>` and prints exactly `true` or `false` (lowercase, newline) for whether doc_id appears in that tag's posting list.

It must use the skip data to jump and handle the tail correctly, so it works for popular tags too. Keep using the conventions and layout you already discovered — don't re-derive from scratch in comments.

After this step, `python3 /app/decode_postings.py /app/index /app/decoded.json` still produces a correct file that matches /app/sample_tags.json (regression check).
