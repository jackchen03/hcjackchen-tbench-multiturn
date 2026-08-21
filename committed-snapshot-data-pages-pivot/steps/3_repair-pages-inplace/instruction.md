The text report path is too slow. Downstream now runs the unmodified engine that reads `pages.bin` directly — it cannot join your text file.

The sorted text output we added for reporting is fast enough for audit but profiling shows the live path re-reading `pages.bin` still sees aborted balances and phantom accounts, because we never fixed the file itself. We need to abandon that approach.

Build `/app/repair_pages` with usage `/app/repair_pages <data_dir> <output_pages_file>`. It must produce a repaired `pages.bin` file at `<output_pages_file>` that contains ONLY the committed snapshot you reconstructed earlier:

- Parse `pages.bin`, `undo.bin`, `rseg.bin` from `<data_dir>` using the decoding from previous steps.
- Compute committed version per account as before (multi-hop walk gated on `rseg.bin`, omit aborted-INSERT origins).
- Write new binary page file at `<output_pages_file>` using the same record layout documented in `/app/FORMATS.md`: each record `account_id` u32 LE, `balance` i64 LE, `trx_id` 6-byte BE of the committed trx that produced it, `roll_ptr` all zeroes (null), `info` byte with committed hint bit 0x02 correctly set. Records sorted by `account_id` ascending.
- The repaired file must NOT contain any balance that was only produced by an aborted/active transaction, must NOT contain phantom accounts created only by aborted INSERTs, must have all `roll_ptr` zeroed, and must pass `/app/inspect.py` showing committed balances.

Do not produce the previous text report format as primary output; the artifact is the binary repaired pages file. Ensure the old aborted balances and phantom accounts are absent — we will check absence.
