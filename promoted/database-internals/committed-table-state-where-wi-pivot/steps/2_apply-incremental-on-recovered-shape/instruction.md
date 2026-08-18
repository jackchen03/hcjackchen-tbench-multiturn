We now need to handle incremental replay on top of what you just recovered.

You are given a base table file that is the exact output of your `/app/replay` from the previous step — same `<key> <value>` sorted format, possibly empty — plus an incremental binary log that uses the same adjudication you already decoded. Apply the incremental log's surviving mutations on top of that base table and produce the final state.

Deliver an executable at `/app/apply`, usage `/app/apply <base_file> <inc_log> <output_file>`. Read `<base_file>` as the starting map, parse `<inc_log>` per `/app/FORMATS.md` and the semantics you learned from `/app/gold_replay`, filter to committed and not undone records, then replay those survivors in global log order atop the base map (`PUT` sets, `DEL` removes). Write result to `<output_file>` in the same format as before: `<key> <value>` per line sorted ascending, `\n` terminated, no header, empty file if empty.

Samples for this mode are in `/app/inc_samples/`, each case has `base.txt`, `inc.log`, and `final.out`. Do not re-implement from scratch ignoring the carried table shape — grading will feed your own previous step's output as base for some cases, so an incorrect base from step 1 will cause step 2 to fail even if incremental logic is right.

Keep `/app/replay` working — regression checks will still run it on v1 logs.
