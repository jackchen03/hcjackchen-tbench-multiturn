# Phase-1 contract omissions

Phase 2 stopped before bundle implementation because the human instructions omit required executable and input contracts that the planned graders assume.

## Step 1 has no deliverable contract

Step 1 describes `/app/goldwriter`, its invocation, bulk `I ` operations, and sample files, but it never instructs the agent to create `/app/writer`, never states the required `/app/writer <ops_file> <out_page_file>` invocation, and never explicitly identifies any agent output. The handoff and dossier nevertheless declare `/app/writer` as the Step-1 artifact and the hidden-test plan invokes it. A do-nothing or prose-only response cannot fairly be failed for omitting a path the human instruction never requested.

## Delete syntax is never defined

Step 2 requires delete/re-insert churn and says to keep the same contract from Step 1. Step 1 only defines insert lines beginning with `I `; Step 2 never defines how a delete identifies a slot or record. The dossier assumes a `D` syntax, but the human instruction does not state it. Choosing `D <slot>`, `D <key>`, zero- vs one-based slots, or another form materially changes the parser and resulting page image.

Phase 1 must explicitly add the Step-1 `/app/writer` deliverable/usage and the exact delete-operation grammar before a fail-closed bundle can grade agent behavior without relying on hidden requirements.
