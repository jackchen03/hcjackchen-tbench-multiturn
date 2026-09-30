# escape-rle-tape-codec

Three cumulative turns recover a bespoke tape encoding from an execute-only reference and then implement an independent encoder.

## Context and transitions

- Step 1 records token chunks, checksum-trailer bytes, total sizes, and the inferred split cap for three operated tapes.
- Step 2 carries `/app/report_S1.md`; its checksum evidence must reuse the recorded split cap when predicting long-tape trailer positions. It adds `/app/report_S2.md` and does not mutate the Step-1 report.
- Step 3 carries both reports as read-only reference material and adds `/app/encoder.py`. The encoder is exercised on byte-disjoint held-out tapes after the reference directory is quarantined.
- Both boundaries are compatible-additive. Earlier contracts do not forbid later work, so over-execution negatives are not contract-authorized.

## Grading and isolation

Steps 1 and 2 parse solver-authored reports against independently computed truth for the operated public tapes. Step 3 invokes the submitted CLI on held-out inputs and compares its bytes against an independent verifier implementation. The runtime reference is stripped, setuid-root, execute-only to the solver, and quarantined before candidate execution. Dedicated controls reject exact copies, renamed copies, wrappers, and lightly modified copies.

## Local evidence

The fresh Docker chain demonstrates red-before-work and green-after-oracle for all three steps with two executed and zero skipped tests per step. Both transition boundaries are contract-justified `NOT_REQUIRED` for over-execution.

## Calibration

| Agent | Step 1 | Step 2 | Step 3 | Whole task |
| --- | --- | --- | --- | --- |
| Nop | unmeasured | unmeasured | unmeasured | unmeasured |
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local oracle behavior is correctness evidence only; no model difficulty or cloud-validation claim is made.
