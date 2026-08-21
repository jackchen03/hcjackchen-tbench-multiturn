# FSM residual override pivot — alternative heap layout witness

Your canonical-visibility + rebuild-FSM fix from last step clears stamped deletes but still fails some values. Fresh evidence from diffing your outputs vs sample ground truth:

- Some heap pages show a slot with xmax==0 that looks live, yet the FSM leaf for that page already reclaimed space exactly equal to that slot's tuple_len — FSM free is AHEAD of what your live set predicts.
- Other pages show a committed xmax stamp on the page, but the FSM leaf still shows old pre-reclaim free — FSM is BEHIND.
- Plus there is a trap: a page whose xmax is an aborted transaction (so slot should stay LIVE) happens to have a coincidentally low stale FSM free; if you trusted FSM free as authority you'd drop a live row as false negative.

The old path that trusted xmax==0 as live and that trusted raw FSM free as authority can't both be right. You must pivot to an alternative interpretation where the heap page can be stale and the FSM leaf is the only witness for a committed delete that was never stamped (xmax==0).

Switch to signed-residual localization:

For each heap page P, compute R after step1 rules (drop aborted xmin, keep aborted xmax, mark committed xmax dead), compute occ = sum(len over R), free_after = USABLE - occ, and read free_fsm from input fsm.bin leaf for that page.

If free_fsm > free_after: FSM AHEAD — a committed delete reclaimed space the page still shows as occupied (xmax==0). delta = free_fsm - free_after. Find the unique tuple in R whose tuple_len == delta (generator guarantees distinct lengths per page and at most one such per page, no subset-sum collision), mark it DEAD, remove from R. This localizes the unstamped delete that commit.log cannot name (no tuple map).

If free_fsm <= free_after: FSM behind or in-sync — it carries no extra delete; trust page+log result, keep R as-is.

This sign test disambiguates ahead vs behind. Do not drop tuples to make page match FSM free unconditionally.

Then emit final `<outputDir>/live.txt` (surviving row_ids ascending) and final `<outputDir>/fsm.bin` rebuilt byte-exact from final survivors: per page free_bytes = USABLE - sum(len over final R), written in documented FSM layout with canonical fsmLSN = max LSN across inputs. Both must now match golden exactly on all cases including aborted-delete false-negative trap and unstamped case.

Remove the old unconditional "xmax==0 ⇒ live" trust and the old "FSM free is authority" path — final /app/reconcile must not contain logic that keeps all xmax==0 rows unconditionally nor logic that drops rows just because free_fsm differs; it must have signed branch free_fsm > free_after and len==delta selection.

Keep same command `/app/reconcile <inputDir> <outputDir>` and same outputs. Read FORMAT.md for all layouts. Your program must stay self-contained, not depend on report_naive or samples at runtime.

This step is about signed residual override and alternative heap layout witness — body must include free_fsm, free_after, delta, tuple_len, xmax==0, signed residual, fsm.bin, heap.bin, commit.log, USABLE, live.txt.
Additionally, write a short JSON report of what you fixed to /app/3_fsm-residual-override-pivot_report.json.
