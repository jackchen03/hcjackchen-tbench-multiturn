# Phase-1 contradictions

Phase 2 stopped before bundle implementation because the future-artifact boundary and Step-2 input contract are internally inconsistent.

## Future artifacts are required in the initial image

The handoff declares `/app/CHECKPOINT_FORMAT.md` and `/app/LOGICAL_FORMAT.md` as Step-1 over-execution artifacts, and `/app/LOGICAL_FORMAT.md` plus `/app/MIGRATION.md` as Step-2 over-execution artifacts. However, `environment.spec.md` explicitly requires all of those files, along with `/app/logical2stream`, checkpoint samples, and logical samples, to exist in the final shared image from the start. A predecessor verifier cannot use existence of those paths to detect early work because a do-nothing container already has them. Removing or delaying them would contradict the planted-state requirement; keeping them makes the declared over-execution map permanently contaminated.

## Step 2 names two checkpoint sources

Step 2 defines `/app/verify <wal_segment_path> <checkpoint_path> <report_path>`, which requires consuming the second argument. The same instruction then says to compute state and compare against the fixed `/app/checkpoint.json`. Those are different contracts whenever the caller passes a held-out checkpoint at another path. Ignoring the argument violates the usage contract; honoring it violates the fixed-path sentence.

Phase 1 must define a verifier-staged lifecycle for later documents/references (and use guardable solver outputs for over-execution), and choose whether Step 2 reads the checkpoint argument or a fixed file before a fail-closed bundle can be built.
