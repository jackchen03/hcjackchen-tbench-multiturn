We have a  GROUP BY operator running `SELECT g, SUM(x), COUNT(DISTINCT y) FROM t GROUP BY g`. Under memory pressure it hash-partitions groups and spills per-partition partial aggregate states as batch files to a spill directory.

Your task: recover the true final aggregates directly from the spilled batches on disk. The batch file format and combine semantics are documented in `/app/FORMAT.md`. A small un sample is in `/app/spill_sample/` with a buggy reference `/app/recover_naive` that reproduces the failure we saw - some groups come out too high, some too low, not a simple rescale fix. The sample's data barely hides the problem.


More steps will follow; conserve resources.