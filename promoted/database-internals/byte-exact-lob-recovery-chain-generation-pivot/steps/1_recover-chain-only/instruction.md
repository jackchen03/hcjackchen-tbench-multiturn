# Recover LOBs from chain

Your storage engine splits big values into blocks and scatters them across overflow slots. Each row keeps a chain that says which slots belong to its value. After a round of updates and cleanup some rows read back wrong — length matches, per-block checksums pass, no error or missing bytes, but if you compare to the known-good original a clean middle window is wrong. It looks like someone else's bytes slipped into the chain.

The crash files live in /app. The layout of overflow.store and lob.dir is in /app/FORMAT.md. A sample set with correct originals is under /app/samples you can use to see the symptom. /app/report_naive shows the naive chain walk.

Build an executable at /app/recover with usage /app/recover <inputDir> <outputDir>. The input directory has the same files as the sample layout. For every value that appears in lob.dir recover the original full bytes and write one file per value into the output dir named after its decimal value_id like <value_id>.bin — file content is exactly the recovered original bytes, no header or wrapper. At this point just walk the chain in order and take slot data verbatim; you only have overflow.store and lob.dir to reason about.

The title keywords recover and chain must appear but the fix is just walking the chain — output must be /app/recover that writes <value_id>.bin files, reads overflow.store and lob.dir, and follows FORMAT.md.
