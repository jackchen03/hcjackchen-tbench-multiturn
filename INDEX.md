# hcjackchen-tbench-multiturn catalog — full 74 tasks from 5 Idea families

`proof` is what oracle chain actually did in Docker. `unproven` = `run_oracle_chain.py` not yet run — drafts, not validated tasks yet.

## Usable tasks (Phase1 handoff, ready for Codex Phase2 builder)

| # | family | dynamic | steps | title | conf | proof | dir |
|---|---|---|---|---|---|---|---|
| 1 | database-internals | both | 3 | Byte-exact LOB recovery: chain to generation-pivot to undo splice | 0.88 | unproven | `promoted/database-internals/byte-exact-lob-recovery-chain-generation-pivot/` |
| 2 | database-internals | both | 3 | Byte-exact pages after mixed insert/delete pivot | 0.88 | unproven | `promoted/database-internals/byte-exact-pages-mixed-insert-delete-pivot/` |
| 3 | database-internals | both | 3 | Byte-match B-tree index builder under space constraint — reporting to deletion | 0.88 | unproven | `promoted/database-internals/byte-match-btree-index-space-builder-pivot/` |
| 4 | database-internals | both | 3 | Byte-match external merge intermediate spill pivot to heap and no-cleanup | 0.88 | unproven | `promoted/database-internals/byte-match-external-merge-intermediate-pivot/` |
| 5 | database-internals | both | 3 | Byte-match non-greedy RLE bit-pack hybrid integer encoder then pivot to dictiona | 0.88 | unproven | `promoted/database-internals/byte-match-non-greedy-rle-bitpack-pivot/` |
| 6 | database-internals | both | 3 | Chained LOBs recovery: de-masked on-disk pivot | 0.88 | unproven | `promoted/database-internals/chained-lobs-demasked-pivot/` |
| 7 | database-internals | both | 3 | Reconstruct committed snapshot from data pages with abort-interrupted rollback p | 0.88 | unproven | `promoted/database-internals/committed-snapshot-data-pages-pivot/` |
| 8 | database-internals | both | 3 |  | 0.88 | unproven | `promoted/database-internals/committed-table-state-where-wi-pivot/` |
| 9 | database-internals | both | 3 |  | 0.88 | unproven | `promoted/database-internals/committed-table-state-winner-pivot/` |
| 10 | database-internals | both | 3 | Reconcile consistent heap live set and rebuild FSM — signed residual pivot | 0.88 | unproven | `promoted/database-internals/consistent-heap-live-set-rebuild-pivot/` |
| 11 | database-internals | both | 3 | Crash recovery replay: quirky XOR-prune recovery then pivot to canonical v2 | 0.88 | unproven | `promoted/database-internals/crash-recovery-replay-pivot/` |
| 12 | database-internals | both | 3 | Crash-safe next value recovery, audit operate, then pivot to simple counter sche | 0.88 | unproven | `promoted/database-internals/crash-safe-next-value-pivot/` |
| 13 | database-internals | both | 3 | Hash aggregation spill recovery — merge frontier then sort pivot | 0.88 | unproven | `promoted/database-internals/hash-agg-spill-recovery-pivot/` |
| 14 | database-internals | both | 3 | Heap tuple writer byte-for-byte: core layout then overflow largest-first then co | 0.88 | unproven | `promoted/database-internals/heap-tuple-writer-byte-exact-pivot/` |
| 15 | database-internals | both | 3 | Reproduce index-scan physical read trace with adaptive prefetch pivot to residen | 0.88 | unproven | `promoted/database-internals/index-scan-physical-read-pivot/` |
| 16 | database-internals | both | 3 | Byte-match the insert path's FSM page-selection dialect with persisted state and | 0.88 | unproven | `promoted/database-internals/insert-path-fsm-page-selection-pivot/` |
| 17 | database-internals | both | 3 | Reproduce exact join output tuple order of opaque hash-join with spill-completio | 0.88 | unproven | `promoted/database-internals/join-output-tuple-order-pivot/` |
| 18 | database-internals | both | 3 | Legacy page writer byte image across delete-reinsert churn and compaction cascad | 0.88 | unproven | `promoted/database-internals/legacy-page-writer-byte-image-pivot/` |
| 19 | database-internals | both | 3 | Reimplement opaque linear-hash index on-disk dialect byte-exact with split-trigg | 0.88 | unproven | `promoted/database-internals/linear-hash-index-on-disk-pivot/` |
| 20 | database-internals | both | 3 | Byte-match opaque LSM compactor anti-canonical dialect with level accounting piv | 0.88 | unproven | `promoted/database-internals/lsm-compactor-anti-canonical-pivot/` |
| 21 | database-internals | both | 3 | Physical WAL reimpl anti-canonical pivot to logical WAL dropping physical path | 0.88 | unproven | `promoted/database-internals/physical-wal-reimpl-anti-canonical-pivot/` |
| 22 | database-internals | both | 3 | Recycled WAL committed set reconstruction — index build to hash pivot | 0.88 | unproven | `promoted/database-internals/recycled-wal-committed-set-pivot/` |
| 23 | database-internals | both | 3 | Reconcile snapshot visible set from truncated WAL and pivot visibility model | 0.88 | unproven | `promoted/database-internals/snapshot-visible-set-truncated-wal-pivot/` |
| 24 | database-internals | both | 3 | Stale page with valid checksum double-write recovery to PITR manifest pivot | 0.88 | unproven | `promoted/database-internals/stale-page-valid-checksum-double-write-pivot/` |
| 25 | database-internals | both | 3 | Stateful escape segment framer with mandatory tail pivot | 0.88 | unproven | `promoted/database-internals/stateful-escape-segment-framer-pivot/` |
| 26 | database-internals | both | 3 | Byte-match opaque word-aligned bitmap index anti-canonical dialect with query pi | 0.88 | unproven | `promoted/database-internals/word-aligned-bitmap-index-anti-canonical-pivot/` |
| 27 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/carved-ext4-extent-tree-unwritten-pivot/` |
| 28 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/carve-live-rows-corrupted-int-pivot/` |
| 29 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/clobbered-dirent-link-count-pivot/` |
| 30 | filesystem-internals | both | 3 | Cross-linked block where victim real block is leaked - generic repair to deep ex | 0.88 | unproven | `promoted/filesystem-internals/crosslinked-block-victim-real-block-pivot/` |
| 31 | filesystem-internals | both | 3 | FAT16 cluster chain recovery pivot: size-correct FAT walk to content reassembly  | 0.88 | unproven | `promoted/filesystem-internals/fat16-cluster-chain-recovery-pivot/` |
| 32 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/formatter-clusters-metadata-pivot/` |
| 33 | filesystem-internals | both | 3 | Reverse nonstandard ext4 htree dirhash to placement pivot | 0.88 | unproven | `promoted/filesystem-internals/htree-dirhash-reverse-pivot/` |
| 34 | filesystem-internals | both | 3 | Replay a detached jbd2 journal to committed consistent state and pivot on revoke | 0.88 | unproven | `promoted/filesystem-internals/jbd2-journal-replay-consistent-pivot/` |
| 35 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/noncanonical-ext4-decode-pivot/` |
| 36 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/nonstandard-journal-reimpl-pivot/` |
| 37 | filesystem-internals | both | 3 | Overflow reassembly that silently corrupts large blobs — inventory, then recov | 0.88 | unproven | `promoted/filesystem-internals/overflow-reassembly-corrupts-large-pivot/` |
| 38 | filesystem-internals | both | 3 | Rowid substitution at non-first PK column with zero-body types and genuine NULL  | 0.88 | unproven | `promoted/filesystem-internals/rowid-substitution-nonfirst-pk-pivot/` |
| 39 | filesystem-internals | both | 3 | Userspace SEEK_HOLE/SEEK_DATA matching kernel on raw ext4 images — offline par | 0.88 | unproven | `promoted/filesystem-internals/seek-hole-data-kernel-match-pivot/` |
| 40 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/sparsepack-three-state-archive-pivot/` |
| 41 | filesystem-internals | both | 3 |  | 0.88 | unproven | `promoted/filesystem-internals/vfat-anti-canonical-reimpl-pivot/` |
| 42 | recsys | both | 3 | Recover exact already-served item set from non-canonical roaring-style bitmap th | 0.88 | unproven | `promoted/recsys/already-served-item-set-recovery-pivot/` |
| 43 | recsys | both | 3 | calibrated-ranking-monotone-pivot | 0.88 | unproven | `promoted/recsys/calibrated-ranking-monotone-pivot/` |
| 44 | recsys | both | 3 | Cohort of correct candidates never reach top — ranking pivot to two-phase with | 0.88 | unproven | `promoted/recsys/cohort-correct-candidates-never-reach-pivot/` |
| 45 | recsys | both | 3 | Reproduce the greedy re-ranker whose diversity penalty and pinned slots co-evolv | 0.88 | unproven | `promoted/recsys/greedy-reranker-diversity-pivot/` |
| 46 | recsys | both | 3 | HNSW interrupted compaction: gen-gated remap plus free-list eviction pivot | 0.88 | unproven | `promoted/recsys/hnsw-interrupted-compaction-gen-gated-pivot/` |
| 47 | recsys | both | 3 | Reproduce house ANN greedy search dialect: integer distance to per-push counter  | 0.88 | unproven | `promoted/recsys/house-ann-greedy-dialect-pivot/` |
| 48 | recsys | both | 3 | Subset of item embeddings garbage due to truncated shard and cross-shard centeri | 0.88 | unproven | `promoted/recsys/item-embeddings-garbage-resolution-pivot/` |
| 49 | recsys | both | 3 | Reconstruct the item factor matrix from quantized checkpoint including head-gate | 0.88 | unproven | `promoted/recsys/item-factor-matrix-quantized-recovery-pivot/` |
| 50 | recsys | both | 3 | Per-ranker credit from interleaving log drifts after first duplicate — pivot t | 0.88 | unproven | `promoted/recsys/per-ranker-credit-interleaving-pivot/` |
| 51 | recsys | both | 3 | Byte-exact codec for product quantization store with index build and scalar pivo | 0.88 | unproven | `promoted/recsys/pq-codec-product-quantization-pivot/` |
| 52 | recsys | both | 3 | PQ code store decodes first vector per block correctly then drifts — keyframe  | 0.88 | unproven | `promoted/recsys/pq-code-store-first-version-pivot/` |
| 53 | recsys | both | 3 | Repeat shoppers see already-bought items and duplicate listings — from dtype d | 0.88 | unproven | `promoted/recsys/repeat-shoppers-already-bought-dedup-pivot/` |
| 54 | recsys | both | 3 | Restored MF checkpoint scores held-out pairs wrong after writer upgrade, with dr | 0.88 | unproven | `promoted/recsys/restored-mf-checkpoint-heldout-pivot/` |
| 55 | recsys | both | 3 | Session feature byte-exact reader writer and streaming scan pivot | 0.88 | unproven | `promoted/recsys/session-feature-reader-writer-pivot/` |
| 56 | recsys | both | 3 | Tag posting lists decode short and phantom repeats then lookup and unified absol | 0.88 | unproven | `promoted/recsys/tag-posting-lists-decode-pivot/` |
| 57 | robotics-3d | both | 3 | Bundle adjustment converges but recovered structure fails whitening — weightin | 0.88 | unproven | `promoted/robotics-3d/bundle-adjustment-converges-structure-drift-pivot/` |
| 58 | robotics-3d | both | 3 | COLMAP binary model recovery with coupled record-boundary and field-typing lies, | 0.88 | unproven | `promoted/robotics-3d/colmap-binary-model-recovery-typing-pivot/` |
| 59 | robotics-3d | both | 3 | ICP registrar adaptive rejection pivot: match opaque then pivot to unbiased | 0.88 | unproven | `promoted/robotics-3d/icp-registrar-adaptive-rejection-pivot/` |
| 60 | robotics-3d | both | 3 | Match opaque ICP registration binary whose correspondence-rejection schedule set | 0.88 | unproven | `promoted/robotics-3d/icp-registration-binary-coherence-pivot/` |
| 61 | robotics-3d | both | 3 | Incremental SfM cloud looks clean but chamfer-drifts — track uniqueness scope  | 0.88 | unproven | `promoted/robotics-3d/incremental-sfm-chamfer-drift-pivot/` |
| 62 | robotics-3d | both | 3 | Marching cubes extractor ambiguity with per-cell rescale and raster ownership pi | 0.88 | unproven | `promoted/robotics-3d/marching-cubes-extractor-ambiguity-pivot/` |
| 63 | robotics-3d | both | 3 | PLY binary recovery: coupled count-stride endian lie then normals then ASCII piv | 0.88 | unproven | `promoted/robotics-3d/ply-binary-recovery-count-endian-pivot/` |
| 64 | robotics-3d | both | 3 | Pose-graph optimizer open-loop pivot: fix direction shear then full covariance t | 0.88 | unproven | `promoted/robotics-3d/pose-graph-optimizer-open-loop-pivot/` |
| 65 | robotics-3d | both | 3 | Two-regime undistortion with asymmetric radius branch coupled to tangential doma | 0.88 | unproven | `promoted/robotics-3d/two-regime-undistortion-asymmetric-radius-pivot/` |
| 66 | trading | both | 3 | Cumulative vs incremental fill reconciliation pivot to gross exposure hash index | 0.88 | unproven | `promoted/trading/cumulative-vs-incremental-fill-recon-pivot/` |
| 67 | trading | both | 3 | Exchange pro-rata allocation dialect: carve-out to min-fill repool pivot to repo | 0.88 | unproven | `promoted/trading/exchange-pro-rata-allocation-dialect-pivot/` |
| 68 | trading | both | 3 | Historical-simulation VaR under-reports on staggered calendars and pre-open job  | 0.88 | unproven | `promoted/trading/historical-var-underreports-pivot/` |
| 69 | trading | both | 3 | L3 to L2 rebuild: REPLACE vs REPRICE double-counted vs time-priority pivot | 0.88 | unproven | `promoted/trading/l3-l2-orderbook-replace-reprice-dedup-pivot/` |
| 70 | trading | both | 3 | MoldUDP64 gap detection: multi-message count drift to heartbeat/EOS sentinel to  | 0.88 | unproven | `promoted/trading/moldudp64-gap-detection-multi-msg-pivot/` |
| 71 | trading | both | 3 | Differential reimplementation of order-by-order book with zero-retention and piv | 0.88 | unproven | `promoted/trading/order-by-order-reimpl-pivot/` |
| 72 | trading | both | 3 | Packed binary feed replay rebuilds corrupt book — pivot version branch | 0.88 | unproven | `promoted/trading/packed-feed-corrupt-book-rebuild-pivot/` |
| 73 | trading | both | 3 | Price-time priority silently violated by worker-pool reordering with sequential  | 0.88 | unproven | `promoted/trading/price-time-priority-worker-violation-pivot/` |
| 74 | trading | both | 3 | Settlement obligations net wrong for amended trades pivot to gross exposure | 0.88 | unproven | `promoted/trading/settlement-obligations-amended-trade-pivot/` |
| 75 | trading | both | 3 | FIX stream desync from embedded SOH inside raw data — family dictionary and ch | 0.88 | unproven | `promoted/trading/stream-desync-embedded-soh-pivot/` |
