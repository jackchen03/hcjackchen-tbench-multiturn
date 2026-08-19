# Rebuild FSM from live set

Your previous /app/reconcile reconstructs the live set using canonical xmin/xmax vs commit.log and passes checksum and layout checks, but its FSM rebuild (if you did one) will still be wrong vs sample ground truth on some pages, and even on clean pages the free bytes must match exactly.

You now have fsm.bin in /app as well, plus the FORMAT.md description of FSM leaves (header fsmLSN u64 LE, first_page u16 LE, n_entries u16 LE, then records {page_id u16 LE, free_bytes u16 LE}). Don't re-derive heap slot layout, commit.log rec_type, or live.txt sorting from scratch — you already have the area and conventions from step1.

Keep your previous parsing for heap.bin and commit.log and the live.txt rule (drop aborted xmin, keep aborted xmax). Now also rebuild the free-space map from that live set:

For each heap page, compute free_after = USABLE - sum(tuple_len over surviving slots in R) where USABLE is the fixed per-page constant from FORMAT.md. Write a fresh consistent fsm.bin into <outputDir>/fsm.bin using the layout in FORMAT.md, with canonical fsmLSN = max LSN across inputs (heap pages + FSM leaves + commit.log), covering all pages.

Keep /app/reconcile at same path and keep writing live.txt exactly like before (same sorting, same abort handling). This step's oracle still expects the same naive live set as step1 (so case-3 unstamped deletes still appear as live), and expects fsm.bin to be the naive rebuild from that live set, not yet the final golden on case-3 pages — that's intentional. Your previous implementation of heap and log parsing should be reused.

Ensure you read overflow? No, just heap.bin, fsm.bin, commit.log, FORMAT.md, and write live.txt + fsm.bin. Both outputs must be byte-valid per FORMAT.md, but live.txt will still be RED vs final golden on case-3.

This step talks about rebuilding FSM from live set — body must mention fsm.bin, free_bytes, USABLE, live.txt, first_page, n_entries.
The output for this step must include /app/fsm.bin.