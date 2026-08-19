# Phase-1 boundary contradiction

Phase 2 stopped before bundle implementation because the declared Step-2 implementation and Step-2 over-execution guard directly conflict.

- Step 3 describes the prior Step-2 `/app/run.sh` as using `debugfs -R stat`, `debugfs -R dump_extents`, and `dumpe2fs -h`, and requires those calls to be removed only in the final pivot.
- The dossier's oracle sketch likewise specifies a `debugfs`/`dumpe2fs` implementation for both Steps 1 and 2, with Step 2 extending that same implementation for unwritten extents and EOF handling.
- The handoff's `overExecMap[2]` nevertheless includes the token `debugfs`, classifying it as forbidden early Step-3 work.

Thus the intended correct Step-2 source necessarily contains a token that the Step-2 boundary guard says must be absent. If the verifier enforces the map, the oracle Step-2 solution cannot pass; if it ignores the map, the required boundary is unguarded. `debugfs` is not evidence of early raw-parser work here—it is explicitly the approach that Step 3 later overrides.

Phase 1 must remove `debugfs` from the Step-2 over-execution map and guard Step 3 with identifiers unique to the raw parser (for example `s_log_block_size`, `eh_magic`, or direct superblock parsing).
