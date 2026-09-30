The lease service loses elections it already won: after a mid-run kill, `python3 /app/interleave_check.py --workers 8 --ops 500 --kill-at 250` shows losers committing, operations replaying, and the high-water mark regressing.

Fix /app/lease_impl.py so the fence token lives in fence.dat as an 8-byte big-endian u64 starting at 0 and increasing by exactly 1 on every grant, the high-water mark lives in hwm.dat as an 8-byte big-endian u64 holding the highest committed op, and every successful commit appends exactly one line shaped {"op","tok","val"} to log.jsonl. Every grant and every high-water-mark update must be durable before return (fsync), so the fence always equals the total grants issued; commit must return True only when tok equals the current fence and op is greater than the stored mark.

Only the lease behavior is checked in this step, via the interleave command above; contention profiling and any parallelism belong to step 2 — do not build them here.
