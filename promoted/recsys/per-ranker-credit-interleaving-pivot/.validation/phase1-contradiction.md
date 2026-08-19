# Phase-1 Step-2 contradiction

Phase 2 stopped before bundle implementation because Step 2 simultaneously requires and forbids the future audit artifact.

The Step-2 human instruction says:

- `Don't emit corrected log files yet; that comes next.`
- `The output for this step must include /app/output/audit.jsonl.`

The surrounding Phase-1 design confirms that `audit.jsonl` belongs to the Step-3 corrected-log pivot, not credit-only Step 2:

- The dossier's Step-2 over-execution negative explicitly asserts that both `/app/output/corrected_log.jsonl` **and** `/app/output/audit.jsonl` must not exist after Step 2.
- The Step-3 oracle sketch says corrected-log generation may optionally write `/app/output/audit.jsonl` with the contested-position audit.
- `environment.spec.md` likewise lists `audit.jsonl` only as an optional Step-3 output.
- The handoff's Step-2 artifact list contains only `/app/credit.py` and `/app/output/credit.csv`; Step 3 owns the corrected-log artifacts.

Therefore the literal Step-2 instruction cannot pass the intended boundary verifier: creating `audit.jsonl` satisfies its mandatory line but fails the documented over-execution negative; omitting it preserves the boundary but violates the instruction. No content/schema for a Step-2 audit is defined either.

Phase 1 must remove the mandatory `audit.jsonl` line from Step 2 or move and fully define the audit contract there while redesigning the Step-2-to-Step-3 boundary.
