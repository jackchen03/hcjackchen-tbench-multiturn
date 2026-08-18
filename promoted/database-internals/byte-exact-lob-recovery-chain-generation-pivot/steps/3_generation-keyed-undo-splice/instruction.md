# Generation-keyed undo splice

Your owner-based fix from last step clears flipped-owner reuses but still fails some values. Fresh evidence: header owner still reads as original value_id in some slots despite the data inside being foreign — that's a copy-forward decoy, owner check can't catch it. Also some slots were reused multiple times, so undo.log holds several before-images per slot; picking the newest image gives the wrong generation.

Switch to generation-keyed undo selection. For any slot where expected_gen != current_gen, don't trust owner — look in undo.log for the record whose gen_before == expected_gen and splice bytes_before at len_before, not at the current chunk_len from the slot. Current length belongs to the later writer.

Remove the old owner-only logic. The previous path that consulted the overflow slot header owner field to decide reuse must go — it is wrong and must not be present in the final /app/recover. Keep the same command /app/recover <inputDir> <outputDir> and same output files <value_id>.bin. Read FORMAT.md for undo.log, alloc.map, overflow.store, lob.dir layout and use value_id to name outputs. You need expected_gen, current_gen, gen_before, len_before all together.

This step is about generation-keyed undo splice — body includes generation, undo, splice, undo.log, gen_before, len_before, expected_gen, current_gen.
