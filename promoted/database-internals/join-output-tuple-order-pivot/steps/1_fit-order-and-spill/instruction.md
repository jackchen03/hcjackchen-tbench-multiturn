# Recover exact join tuple order for fit partitions

We have a stripped reference operator at /app/refjoin. It reads from stdin a JSON document with fields build, probe, build_key, probe_key — two relations and the join key column index for each side. It writes the equi inner join result to the file path given as argv[1]. The container format for input and the exact serialization for each output row (how build columns then probe columns are joined, delimiter, line terminator) is documented in /app/FORMAT.md — follow it exactly. The row multiset is ordinary inner-join semantics, never in doubt.

The problem is order. Your downstream does a byte-wise diff of output streams and expects the reference order. A textbook grace hash join produces the right multiset but its row order drifts from /app/refjoin on some inputs.

Start with the small inputs under /app/samples/. Those are modest enough that the reference never needs to recursively repartition. For this step, build an executable at /app/hashjoin that reads the same JSON from stdin and writes to argv[1]. Requirement: /app/hashjoin output must be byte-for-byte identical to /app/refjoin on all inputs of the same size class as the samples — i.e., where every build partition fits without recursion.

To get there you will need to probe /app/refjoin: figure out its partition function and fixed partition count P, how it orders partitions (hint: not ascending id), and how it emits rows inside a fit partition (probe-input order vs build-insertion order). The title keywords join, output, tuple, order, and spill must appear in your reasoning but the task is to produce /app/hashjoin that matches on fit cases.

Output contract for hidden tests: /app/hashjoin exists, executable, usage /app/hashjoin <output_file> reads JSON from stdin, writes joined rows per FORMAT.md, byte-matches /app/refjoin on all fit-only held-out inputs.