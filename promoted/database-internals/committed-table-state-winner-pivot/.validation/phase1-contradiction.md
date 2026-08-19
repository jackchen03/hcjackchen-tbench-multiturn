# Phase-1 future-reference contradiction

Phase 2 stopped before bundle implementation because Step 2 requires the Step-3 oracle as a Step-2 output, contradicting the declared reference lifecycle and semantic boundary.

The final line of Step 2 says: `The output for this step must include /app/gold_replay_v2.` However:

- `environment.spec.md` says `gold_replay_v2` implements the new retention/abort-on-miss semantics and is "not exposed to agent in Step1/2."
- The same environment says the v2 oracle and samples become visible only at Step 3.
- The task's core transition requires Step 2 to remain on v1 consumption/no-op semantics so that Step 3 can override them.
- The handoff's Step-2 artifact list does not include `gold_replay_v2`; it treats v2 materials as Step-3 artifacts.

Making the reference present or requiring the agent to produce it during Step 2 exposes the future answer and collapses the Step-2-to-Step-3 boundary. Keeping it hidden makes the literal Step-2 output contract impossible. An agent also cannot legitimately recreate an opaque grading oracle that the task says is environment-owned.

Phase 1 must remove `/app/gold_replay_v2` from Step 2 and stage it only after Step 2 verification, or explicitly redesign the transition.
