Your demand-order walk is correct; now add the adaptive readahead that the stripped binary at `/app/scan` shows on cold-cache scans.

Probe `/app/scan` on cold-cache long scans: after each demand leaf, it issues a prefetch batch for future leaves along the sibling chain. The window size appears to start at 1 and grow, doubling on sequential leaves where the sibling's physical id == current leaf's physical id + 1, resetting to 1 on a non-adjacent physical jump, capped at a hidden `W_max`. You can read off `W_max` by running cold long adjacent-run scans.

Build an executable at `/app/scan_prefetch` with usage `/app/scan_prefetch <fixture> <lo> <hi> <warmpool_file> <out_file>`. It must do what `/app/scan_demand` did, plus after each demand leaf (after updating the window), issue a prefetch batch for the next `W` leaves along the sibling chain, in chain order. Demand and prefetch reads are interleaved: emit the demand leaf read (if not suppressed), then its prefetch batch reads, then next demand leaf, etc. For this step, use textbook residency handling: a leaf already in `<warmpool_file>` or already emitted (read or prefetched earlier) emits no line (suppress), and does not otherwise affect budget; on a resident demand leaf skip its read but still check adjacency for next ramp update. No extent handling yet.

Write to `<out_file>` one physical page id per line, decimal, in exact issue order, demand followed by prefetch per leaf. Samples for naive prefetch are under `/app/samples/prefetch/`, values disjoint from held-out. We will test on cold-cache and lightly warmed short scans that don't straddle extent boundaries.

More steps follow; conserve resources and do not anticipate the final dialect's exact path yet.
