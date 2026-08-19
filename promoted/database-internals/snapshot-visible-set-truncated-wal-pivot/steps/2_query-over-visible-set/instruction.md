# Query over the recovered visible set

Now that we can get the correct visible set, the reporting team needs to answer range count queries against it.

There is a workload file at /app/data/queries.bin containing range queries. Its format is documented under queries.bin in /app/FORMATS.md.

Build an executable at /app/query with usage `/app/query <data_dir> <query_file> <output_file>`. For each query in <query_file> (in order), count how many rows from the truly visible set you recovered in the previous step have row_id in [low, high] inclusive, and write one count per line into <output_file> in query order.

Use your visibility logic from the previous step; don't trust the old buggy reporter and don't re-derive heap layout from scratch. The visible set is what you already built in /app/reconstruct – the outputs from that step are declared and will be used by the oracle.

We will test with different queries.bin and different data directories with disjoint row_ids, so your counting must be based on the actual live set, not hardcoded. The title keywords query and visible set must be reflected in this step.

More steps follow.
The output for this step must include /app/output/query_results.txt written via <output_file> argument (one count per line).