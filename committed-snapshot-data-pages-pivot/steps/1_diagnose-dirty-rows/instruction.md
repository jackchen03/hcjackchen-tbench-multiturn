A batch of updates crashed mid-rollback in our InnoDB-flavored accounts table. The table still reads, but finance reports see wrong balances.

Some rows on the latest page show a balance from a transaction that the log says was rolled back. The page-inspection tool at `/app/inspect.py` renders every row as clean, with info bit 0x02 "committed", so hexdump/cat look fine.

The crash site is archived under `/app/data/` as three binary files: `pages.bin` (clustered leaf rows), `undo.bin` (undo segment), `rseg.bin` (rollback segment header with authoritative per-trx state). Their byte layouts are documented in `/app/FORMATS.md`. You can also look at `/app/report_buggy.py` which is the current buggy reporter using page values + hint bit.

Write an executable program at `/app/diagnose`, usage `/app/diagnose <data_dir> <output_file>`. It must read `pages.bin`, `undo.bin`, `rseg.bin` from `<data_dir>`, decode each record's `trx_id` and `roll_ptr` according to `FORMATS.md`, reconcile against `rseg.bin` (the only authoritative trx state), and output every `account_id` whose current on-page balance is NOT from a committed transaction — i.e., whose top version's trx is not COMMITTED. One `account_id` per line, decimal integer, sorted ascending ascending, no extra content. Do not trust the on-record info/header committed hint.

We will test with a different data directory with disjoint account_ids and different balances/trx assignments, so parse the formats generically, not hardcode answers.
