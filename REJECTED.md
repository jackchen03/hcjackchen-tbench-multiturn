# Rejected candidates

None — 75 promoted tasks all passed Phase1 static gates + Phase2 conflict fixes:
- Fixed invalid Docker digests (61/65/69 hex -> 64 hex valid)
- Fixed overExecMap non-path tokens -> file-path discipline /app/... appearing literally in later steps
- Fixed prerevealed (future file mentioned early) and nonliteral (token not in later)
- Fixed cross-step resource starvation: undo.log reserved for step3 made step2 detection-only, gold_replay_v2 reserved for step3 removed from step2, data_v2 snapshot.bin removed from step2, deletes.txt removed from step2, report.json self-conflict removed, etc.
- Fixed missing executable/output contracts: legacy-page-writer /app/writer, carved-ext4 /workdir/reconstruct.sh, etc.
- Fixed contradictory pivots: hash-agg drop hash partitioning removed from step2, sparsepack eh_depth>0 removed from step2, seek-hole debugfs guard changed to raw-parser, greedy-reranker pin diversity contradiction removed, lsm tombstone rule made single exact rule (retain all unconditionally), heap-tuple-writer counter->hash pivot, etc.
- Added deterministic identification: crosslinked-block checksum/journal ownership, fat16 payload stripping, rowid padding, jbd2 replay artifact guard, noncanonical report path, etc.

All 74 Ideas from hcjackchen-tbench-1/Ideas have been promoted to 75 tasks (including 1 alt). 33 Phase2 conflicts listed by agents have been resolved.
