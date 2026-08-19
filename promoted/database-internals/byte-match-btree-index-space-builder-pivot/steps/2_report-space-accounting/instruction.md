Your builder from step 1 now produces byte-exact indexes.

Operations now needs visibility into space accounting. Keep your /app/btbuild exactly as before — same /verifier/btbuild <output file> stdin contract, same byte-exact index output.

Add a side-car: whenever /app/btbuild <output file> runs, it must also write a JSON file to /app/btbuild.meta with fields page_count, nlevels, root_pageid, total_bytes, page_size.

page_count must equal the actual number of pages in the file you just wrote, nlevels and root_pageid must match the header you wrote, total_bytes must equal page_count * page_size and also equal the file size, page_size is the fixed page size you discovered.

We will run your builder on new key sets and check that /app/btbuild.meta exists, valid JSON, keys present, values integer, and consistency: total_bytes == file size on disk, total_bytes == page_count * page_size, and page_count derived from file header matches your JSON. Byte-exact index requirement still holds.

Use your carried conventions and file from previous step; don't re-derive format docs.
The output for this step must include /app/deletes.txt.