Your byte-exact builder plus accounting from steps 1-2 assumed append-only bulk load — always filling the rightmost leaf and only splitting. Production trace replay shows that path is too slow for incremental maintenance and now fails because we do deletes.

New requirement: support deletion with merge and redistribution under the same space dialect.

The builder invocation changes: /app/btbuild <deletes_file> <output file> still reads base keys from stdin one per line, but now also reads a second file at <deletes_file> containing keys to delete, one per line. You must build base index from stdin keys as before, then delete each key listed in deletes_file (ignore if not present), and if a leaf underflows you must merge with a sibling or redistribute entries, using the same coupled rules for encoded size, high-fence-anchored prefix, and separator truncation + 4-byte padding. If a merge causes its parent to underflow, cascade upward. Internal nodes follow the same byte-balanced and prefix/separator rules during merge/redistribution. Final file must still be byte-exact versus new reference /verifier/btbuild-delete which implements the full delete dialect, on held-out cases that force leaf and internal merges and redistributions.

Your old append-only, rightmost-only split path that never checked underflow must be removed. We will assert absence: your /app/btbuild source no longer contains logic that only splits rightmost page and never handles merge/redistribution, and it must open <deletes_file> and contain merge/redistribution handling. Profile reason: sorted array bulk path and FSM page selection that only ever moved right is now wrong — must pivot to underflow handling.

Keep your previous /app/btbuild.meta accounting from last step — after delete, its fields must reflect final post-delete index. Keep byte-exact invariant for final file.

Paths to know from carried context: /app/btbuild is your binary, /app/btbuild.meta accounting, /verifier/btbuild-delete is the new oracle at /verifier/btbuild-delete <deletes_file> <output file> reading base keys on stdin, /verifier/dump-tree still works on final files.
