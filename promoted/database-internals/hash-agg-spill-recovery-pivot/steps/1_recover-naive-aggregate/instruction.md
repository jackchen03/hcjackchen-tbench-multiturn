We have a streaming GROUP BY operator running `SELECT g, SUM(x), COUNT(DISTINCT y) FROM t GROUP BY g`. Under memory pressure it hash-partitions groups and spills per-partition partial aggregate states as batch files to a spill directory.

Your task: recover the true final aggregates directly from the spilled batches on disk. The batch file format and combine semantics are documented in `/app/FORMAT.md`. A small untorn sample is in `/app/spill_sample/` with a buggy reference `/app/recover_naive` that reproduces the failure we saw - some groups come out too high, some too low, not a simple rescale fix. The sample's data barely hides the problem.

Write an executable at `/app/recover` that takes two arguments: first is the spill directory path, second is the output file path. It must read all batch files in that directory, reconstruct per-group `SUM(x)` and `COUNT(DISTINCT y)`, and write one line per group sorted ascending by `group_key`, each line three fields separated by `\t` (tab), in order `group_key`, `SUM(x)` integer, `COUNT(DISTINCT y)` integer, terminated by `\n` newline, with final file also ending in `\n`. We will test it on other spill directories you haven't seen, so don't hardcode this one.

More steps will follow; conserve resources.
