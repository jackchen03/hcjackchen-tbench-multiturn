# Cursor-stable segmented-store recovery

This two-step task starts with recovery of acknowledged transactions from a
segmented store containing manifest-lineage distractors, bounded corruption,
authenticated resynchronization points, split control envelopes, and reused
transaction IDs. The second turn carries the exact implementation, decisions,
and source-interval provenance forward, then overrides any physical rewrite
strategy with an immutable view that retains old replica-cursor meaning.

The dependency is substantive on all three signals. The Step-2 oracle consumes
Step-1's exact decision bytes and provenance; its instruction intentionally
does not repeat the recovery rules; and its verifier rechecks the carried
recovery semantics before grading cursor mapping. The 1→2 over-execution probe
is contract-justified `NOT_REQUIRED`: Step 1 does not forbid a compatible
non-destructive or cursor-capable superset.

## Local correctness and calibration

Local proof records correctness only. Difficulty and model discrimination stay
unmeasured until separately authorized exact-revision trials exist.

| Agent | Step 1 | Step 2 | Whole task |
| --- | --- | --- | --- |
| Nop | locally rejected | not reached | locally rejected |
| Oracle | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured |

The hidden verifier uses independently serialized stores and independently
derived semantic truth. Public and hidden stores differ in identifiers,
payloads, layouts, corruption offsets, and cursor probes. No model completion,
novelty, cloud-validation, or balance claim is made here.
