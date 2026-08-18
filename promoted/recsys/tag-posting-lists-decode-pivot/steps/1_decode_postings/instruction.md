Our retrieval chain's tag-to-product posting decoder is gone — only the on-disk index under /app/index remains (terms.dict, skips.bin, postings.bin). There's a small human-checked reference at /app/sample_tags.json for a few tags.

Popular tags are broken: decoded lists come up short versus the df in the dictionary, and some decode to an extra duplicate of the last product at the tail. Normal tags look okay. You can't tell by just listing files — you have to actually decode bytes and compare against the reference to see the pattern.

Write a script /app/decode_postings.py invoked as `python3 /app/decode_postings.py <index_dir> <output_json_path>`. It must read the given index directory and write a JSON object mapping tag string to integer product id array, in the exact storage order, with no missing tail and no phantom duplicates.

Running it as `python3 /app/decode_postings.py /app/index /tmp/out.json` must make every tag covered in /app/sample_tags.json match exactly. Don't hardcode sample results — grading will run it on a separate index built the same way.
