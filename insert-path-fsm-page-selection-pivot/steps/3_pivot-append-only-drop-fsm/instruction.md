# Pivot to append-only insert path — drop FSM

Your FSM-based page selection and per-batch updated state from last step now fail in production.

Fresh evidence:
- `/app/WORKLOAD.log` shows the workload switched to bulk `APPEND_ONLY` inserts — keys are monotonic, no deletes leaving interior slack, every batch is large sequential writes. A fragmentation audit says FSM search scatters tuples and causes random I/O, degrading tail latency.
- `/app/ENGINE_FLAGS` contains `USE_APPEND_ONLY=1` and says free-space map quantization and persisted `<new_state_file>` accounting are now deprecated — centralized space management owns extension, and second-arg state file must not be produced anymore.

Switch dialect: your heap loader must now byte-match new reference binary `/app/refheapload_append` (present for probing) which keeps the same state file input format (`USABLE`, `SLOT`, `CURSOR`, page count, `<pid> <true_free>`) and same stdout contract (landing page id per line) but changes selection to append-only: try the last page (`npages-1`) if its `true_free >= tuple size`, otherwise extend a new page id equal to current page count, place there, set its free to `USABLE - size`. No FSM category computation, no search from `CURSOR`, no wraparound, no overstatement false-positive handling. Probe `/app/refheapload_append` on crafted states and batches to discover the exact rule.

Remove the old logic:
- The previous path that computed category `ceil(f / SLOT)` and `needcat = ceil(s / SLOT)`, forward search from `max(CURSOR,0)` with wraparound, and false-positive correction to floor value and CONTINUE from next position must go — it is wrong for append-only and must not be present in final `/app/heapload`.
- The per-batch updated state write path — second argv handling that wrote `<new_state_file>` — must go. Final usage reverts to single arg `/app/heapload <state_file>` only. If invoked with two args, it should not create the file at the second path.

Keep `/app/heapload` at the same path, same state file reader for input, but drop FSM code and new-state accounting. Read samples and motivation logs for exact paths and flag names. You must still produce byte-identical output versus `/app/refheapload_append` on held-out cases, and static checks will assert your source no longer contains FSM quantization or extended search logic.
