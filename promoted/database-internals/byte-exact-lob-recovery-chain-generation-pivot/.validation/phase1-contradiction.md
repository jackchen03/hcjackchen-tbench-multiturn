# Phase-1 blocker

Phase 2 stopped before bundle implementation because the human-owned dossier explicitly marks Step 2 as not gradeable and requires a contract decision.

The dossier's `Phase-2 blocker addendum` states:

- Step 2 requires replacing a reused slot's foreign window with the original bytes.
- `alloc.map` supplies generation/ownership metadata but not original bytes.
- The only declared original-byte source is `undo.log`, whose before-images and selection semantics are introduced as the Step-3 mechanism.
- The stated Step-2 over-execution plan forbids using that later source/mechanism.

Therefore a Step-2 oracle cannot simultaneously require restored bytes and preserve the intended boundary. Allowing `undo.log`/before-image recovery in Step 2 collapses the Step-3 discovery boundary; forbidding it leaves Step 2 without the bytes it is required to emit. The dossier directs a human to choose either a Step-2 byte source or a detection-only Step-2 contract.

No builder-side interpretation can resolve that choice without changing the human-owned task design, so no solutions, tests, or environment bundle were written.
