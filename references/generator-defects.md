# Generator defects — what went wrong at scale, and which gate now catches it

Two mechanical scans of a 100-task multi-turn catalog (2026-08-03 and 2026-08-04) found that
almost every defect was a **generator** bug, not a per-task bug: the same broken shape emitted a
hundred times. This file is the record, kept so the same defect classes cannot come back
unnoticed. The right column is the gate code that now rejects it mechanically — run
`scripts/validate_task.py` (per task) or `scripts/check_catalog_uniqueness.py` (per catalog).

Headline numbers from the second scan: 29/100 were single-turn masquerading as multi-turn, 10
Dockerfiles would not parse, 69% of test functions (1138/1651) were boilerplate, 0/71 genuine
tasks had a passing oracle, and 13/71 degraded to a hollow pass when the reference was hidden.

## The fatal one: clones and fiction names

One run produced **100 renamed copies of a single task**: one distinct Dockerfile, one distinct
`solve.sh` set, one test suite byte-identical across all 100 dirs, every task containing the
`inventory` body regardless of slug, 50 titled `*-with-email-alias-migration` with zero matches
for `email`/`alias`. A dossier admitted "Auto-generated from template …". A suite like that
measures one problem 100 times.

| Rule | Gate |
|---|---|
| Two slugs must not share a byte-identical Dockerfile + `solve.sh` set + test suite | `X1` |
| Every substantive slug word must appear in that task's own steps | `X2` |
| A dossier must describe the specific schemas / regexes / tables that make *that* task unique, and must never say "auto-generated from template" | review |

## Fix 1–13 (2026-08-04 scan)

| # | Defect | Gate |
|---|---|---|
| 1 | Docker heredoc followed by a line starting `&&` → `unknown instruction: &&`, build fails (10 tasks). The terminator must be alone on its line and the next line must start a new `RUN` | `E2` |
| 2 | Service images as a base: `mysql:8` (Oracle Linux, no apt-get), `postgres:15`/`redis:7` (externally-managed pip). Use `python:3.11-slim` + the client package, or a sidecar | `E3` |
| 3 | 29 tasks had no `steps/`, `version = "1.0"`, root `[verifier]`/`[agent]`, a dangling content-free `[[steps]]`, yet were tagged `multi-turn`. Either reclassify as single-turn or split properly | `L1 L2 L3 L7` |
| 4 | A boilerplate test family repeated verbatim per step, off-topic (`test_solve_fails_without_git` in a fibonacci task), tautological, or with unbound template variables. Every remaining test must trace to a line in that step's own `instruction.md` | `V5 V6 V10 V11` |
| 5 | 123 test files read the reference `solve.sh` (60 executed it) — that grades the oracle, not the agent, and degrades to a hollow pass once the solution is masked. 60 also hardcoded the authoring host path | `V9` |
| 6 | 56 tasks' tests invoked a `/app/validate_*.py` that only the reference `solve.sh` creates, so a correct agent fails unconditionally. Ship it in `environment/` and state the contract, or assert on the artifact directly. (Also: `echo "{"errors": $n}"` produces invalid JSON — use `printf` or `jq -n`) | `V8a` |
| 7 | 29 tasks shelled out to git from tests in images without git | `E5` |
| 8 | 7 genuine oracle bugs: missing `SameSite`; an absolute wall-clock bar (`2.184 < 0.5`) instead of a relative one; a sum mismatch; `3 >= 5` on a fixture that only yields 3; a report file never written; a tag never recovered; and a step-1 oracle that emitted step-2/3 artifacts and tripped its own negatives | `ORACLE` / `GREEN` / `OVER-EXEC` |
| 9 | 183/212 `solve.sh` and 71/71 Dockerfiles missing the canary GUID | `O1 E1` |
| 10 | 61 tasks had `[steps.agent] timeout_sec = 600` — multi-turn needs ~1800 or Avocado times out; 29 carried root `[verifier]`/`[agent]` | `L10 L3` |
| 11 | Instructions unlike a real user's: 81 ended with `Keywords for this task: …`, 46 were under 50 words, some leaked the answer (an exact regex, "with a valid copy for reference"), pivots had no in-world motivation, and tests enforced numeric bars the spec never stated | `I1 I2 I3` (blocking; a 3P model reports the fix, the human author applies it) |
| 12 | 83/183 `test.sh` used a bare relative path and only worked if cwd was the step dir | `V4` |
| 13 | 30/71 chains were decorative — step N's `solve.sh` used nothing step N-1 produced. Plus 102 missing-regression flags, and no per-step pass-rate signal. Warning: textbook pairs (`fibonacci→memoized`, `linear-search→hashmap`, `lru-cache`) solve flat@1.0 — the lever is cross-round difficulty, not per-step optimality | `D1` + cascade calibration |

## The seven emit-time guards (2026-08-03 re-check, 70 rejects)

Ten tasks were re-graded Revise → **Reject** because their steps 1–2 had only negative tests that
`pytest.skip`ped when the artifact was absent (a skip exits 0 → pass) and their step 3's single
positive test compared a keyword against the task's own slug. A do-nothing agent collected
reward 1.0 on every step for zero work.

| Guard | Rule | Gate |
|---|---|---|
| a | Every asserted path must be named in some `instruction.md` (or created by `environment/`). Over-execution negatives may only name artifacts a **later** instruction asks for | `V8a` |
| b | `test_outputs.py` with zero `def test_` collects 0 tests, pytest exits 5, and the step fails unconditionally | `V2` |
| c | No always-true tails: `or True`, `or 3 == 3`, `N == N` | `V5` |
| d | No `pytest.skip` for a missing artifact — use `pytest.fail` or a plain assert | `V3` |
| e | No step whose tests are all negative — each step needs ≥1 positive covering its own core | `V7` |
| f | No assertion whose fallback operand is the task slug (always true) | `V11` |
| g | No unresolved template placeholders (`{tok}`, `{neg_esc}`, `# adapt to original task`) — a NameError on failure is not an AssertionError | `V10` |

**The do-nothing gate catches 60 of those 70 rejects on its own.** It is now the DO-NOTHING phase
of `scripts/run_oracle_chain.py`: run each step's tests against the container before that step's
`solve.sh`. Any step that passes is rejected.

## Worth preserving

The naive → profile → optimize shape produced the strongest tasks in the catalog:
`linear-search-then-hashmap-optimization`, `lru-cache-then-arc-optimization`,
`bubble-sort-then-quicksort-pivot`, `regex-backtracking-then-dfa-pivot`,
`sql-n-plus-1-then-join-optimization`, `json-parse-then-streaming-optimization`,
`image-resize-naive-then-libvips-pivot`, `log-grep-then-indexed-search-pivot`,
`csv-join-nested-then-hash-join-pivot`, `fibonacci-recursive-then-memoized-pivot` — real specs,
behavioural tests, AST-enforced pivots, disclosed numeric thresholds.

Their residual problems are the ones to design against next time: no regression checks on the
earlier step (4D), hardware-dependent absolute timing (always prefer a relative bar), and high
recall risk — every one of them needs a novelty check before it ships.

## Suggested repair order for an existing broken catalog

1. Fix 1 + 2 — make every image build.
2. Fix 4 + 5 + 6 — strip the template test family.
3. Fix 7 + 12 + 9 + 10 — git, `test.sh` robustness, canary, timeouts.
4. Fix 8 — the genuine oracle bugs.
5. Fix 3 — convert or reclassify the masquerading tasks.
6. Fix 11 + 13 — instructions and cross-step design.

Gate at every stage: the reference must pass every step end-to-end in a real harness. Nothing
ships while that number is non-zero.
