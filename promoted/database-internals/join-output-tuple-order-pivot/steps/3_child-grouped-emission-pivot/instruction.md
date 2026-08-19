# Pivot to child-grouped emission for recursed partitions

Your current operator handles single-level recursion but still drifts on deeper traces. Look closely at a partition that recursed: its output is NOT in parent probe-scan order. Instead its rows come out regrouped by child sub-partition — all rows whose keys map to child 0, then child 1, etc., where child order is spill-completion order within that parent, not ascending id. For a child sub-partition that itself recurses (two-level recursion), the same rule applies recursively: it is regrouped into its own children. Inputs where fit and recursed partitions coexist and where a key has multiple build matches (exercising build-insertion order) expose this.

Previous code emitted a recursed partition in flat probe-scan times build-insertion order, which is only correct for fit partitions. That flat path is wrong here and must be removed. Switch to child-grouped emission: a fit partition emits probe-scan times build-insertion; a recursed partition emits its child sub-partitions in spill-completion order, each child emitting by the fit rule or recursing again. Remove the flat emission branch for recursed partitions and the tuple-count based recursion check if you have one — they cause order divergence.

After this pivot, /app/hashjoin must byte-match /app/refjoin on all inputs: fit-only, single-level recursion, two-level recursion, mixed fit/recursed coexistence, multi-build-match keys, and skewed distributions that force non-ascending spill-completion processing order. During grading /app/refjoin will be absent, so your binary must be self-contained.

Output contract: /app/hashjoin at same path, same JSON stdin -> argv[1] file per /app/FORMAT.md, byte-matches on full held-out set spanning fit, single-level, two-level, mixed, multi-match, skewed spill-completion.
This step must handle flat emission branch must be removed correctly.
This step must handle second level recursion correctly.
Additionally, write a short JSON report of what you fixed to /app/3_child-grouped-emission-pivot_report.json.
