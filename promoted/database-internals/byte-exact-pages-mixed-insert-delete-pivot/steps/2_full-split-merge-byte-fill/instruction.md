Your single-page replica now passes small cases, but it fails on larger operation streams that cause the tree to grow beyond one page and later shrink again. The bytes diverge exactly when a page should split or when an underfull page should borrow or merge — merge timing is off, and the pages that get rewritten have different ghost counts afterwards.

Extend the same binary at `/app/btapply` (overwrite it, keep the same path and usage `/app/btapply <output file>` reading `I <key>` / `D <key>`) so it handles the full multi-page B+ tree: splits on insert overflow and borrow/merge on delete underflow. Keep all the single-page ghost and reuse conventions you already reverse engineered — do not reimplement the page header from scratch.

We will now validate on all streams, including those in `/app/samples/` that trigger splits and merges, plus larger held-out streams with delete-heavy patterns, variable-length keys crafted so byte-fill vs key-count underflow differs, and cascades of split then merge. You need to discover the split point rule, the underflow trigger quantity and threshold, when compaction of ghosts happens, and which sibling is preferred for borrow and merge.

Also write `/app/split_boundary.json` with the thresholds and sibling preference you discovered, containing exactly keys `split_pct`, `merge_pct`, `borrow_order`, `merge_order` — for example `{"split_pct":<int>,"merge_pct":<int>,"borrow_order":["right","left"],"merge_order":["right","left"]}`. The integer values must be the actual percentages you reverse engineered. This file is part of this step's contract.

Do not yet write `/app/migration_report.json`. The old tool remains at `/verifier/btapply` and `/verifier/dump-tree` for probing.
