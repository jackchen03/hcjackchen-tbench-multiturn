# Authoring multi-turn (multi-step) T-Bench tasks — deep reference

This is the multi-turn-specific reference. Everything in the single-turn method still holds —
read `tbench-task-rubric.md` (the bar) and `tbench-discovery.md` (families + build/calibrate)
first. This file adds only what changes when a task becomes a **sequence of steps** the agent
works through in one carried-over session.

**Contents:** the two dynamics (why build one) · structure on disk · `task.toml` schema (v1.1) ·
non-decorative dependency (the 3-signal test) · context-following · context-overriding ·
over-execution + negative tests (the contamination trap) · per-step tests / regression / Harbor
limits · the oracle chain · multi-turn cheat vectors (MC1–MC8) · per-step cascade calibration ·
build & prove loop · the per-step `instruction.md` policy · anti-patterns.

## What a multi-turn task IS — and the only two reasons to build one

A multi-turn task is a chain of N user-authored prompts (`steps/<N_step>/instruction.md`) the
agent works through **in order, keeping its session/context across steps**
(`inherit_prior_session = true`). The agent sees only the *current* step's instruction at each
turn; it must carry everything else in its head from the turns before.

That carry-over is the whole point. A multi-turn task earns its structure only if it tests one
(ideally both) of these:

- **Context-following** — step N relies on context established in a prior step **that is not
  repeated** in step N: the area of code being modified, the purpose of the change, the
  coding-style conventions, the algorithm choice, the problem framing. The agent must *remember*
  and *reuse* it. If step N restates that context, the signal is gone.
- **Context-overriding** — step N **pivots away** from a prior step's direction: a bad
  assumption is corrected, the requirements change, the agent must abandon the approach it just
  built and take a different one. The agent must *notice the contradiction* and change course
  rather than plough ahead on the old plan.

Tag the task accordingly in `task.toml` (`context-following`, `context-overriding`, or both —
they're not mutually exclusive; a 3-step task can follow across 1→2 and override across 2→3).

**Bias toward context-overriding and toward 3 steps.** Following is the default shape and most
real follow-ups look like it, so submissions cluster there: of 31 alpha submissions only **2**
used overriding, and the pool is heavily skewed to exactly 2 steps. Research has asked for more
of both. When two candidates are otherwise equal, build the one that pivots, and build it in 3
steps.

**If neither dynamic is the point, use single-turn.** Multi-turn has more failure modes, more
validator gaps, and more calibration burden. "It feels multi-stage" (setup, then do the thing,
then clean up) is *not* a reason — that's one single-turn task with three paragraphs. Reach for
multi-turn only when the *carrying* or the *pivot* is the hard part.

**Step count: aim for 2–3.** More than 3 multiplies the cascade-tuning burden without much added
signal. One `[[steps]]` block means you mis-scoped a single-turn task as multi-turn.

## Structure on disk

```
<task>/
├── environment/                 # SHARED across all steps — one Dockerfile + source/fixtures
│   └── Dockerfile               # Claude-authored config; source under it is user-authored
├── steps/
│   ├── 1_<stepName>/            # order fixed by the [[steps]] blocks in task.toml
│   │   ├── instruction.md       # agent-visible spec for THIS step ONLY (user-authored)
│   │   ├── solution/solve.sh    # reference oracle for THIS step (runs on the prior step's end state)
│   │   └── tests/{test.sh, test_outputs.py}   # hidden per-step verifier
│   ├── 2_<stepName>/  (same shape)
│   └── 3_<stepName>/  (same shape)
├── task.toml                    # schema_version = "1.1", one [[steps]] block per step
├── README.md                    # author notes / completion-rate grid (NOT agent-facing)
└── (no top-level instruction.md / solution/ / tests/ — see below)
```

Scaffolding **removes the top-level `instruction.md` and `solution/`** and they must stay absent —
the per-step copies replace them, and `validate_task.py` flags either as a single-turn leftover
(`L8`). A **task-level `tests/` is allowed, for utilities only** (helper modules several steps
import); `L8` fires on it only when it contains real `def test_` assertions, which is a
single-turn leftover that breaks grading.

## task.toml — the multi-turn schema (v1.1)

See full schema in earlier fetch — schema_version 1.1, inherit_prior_session true on step 2+, dependencies, min_reward 1.0, per-step verifier/agent timeouts 1800, tags BEFORE [[steps]].

## The cross-step dependency must be REAL, not decorative

3-signal test: S1 oracle coupling, S2 instruction non-duplication, S3 test adaptation. If >=2 no, decorative.

## Context-following, done well

Write terse follow-up assuming shared history, not recall drill. Do: "Add a constraint..." Don't: repeat context.

## Context-overriding, done well

Pivot must be legible + motivated, with absence assertion that old approach removed.

## Over-execution: the primary multi-turn failure mode

Every step with successor MUST include negative tests asserting next step's artifacts don't exist yet. Boundaries live in tests, not prose. Pick negatives ONLY from identifiers later instruction.md explicitly names.

## Per-step tests, regression, and Harbor limits

- Each test lives in step that introduces functionality
- Regression: step N must re-check step N-1 core
- Harbor does NOT expose /tests/ across steps
- Later steps test.sh must not re-run whole pipeline

## The oracle is a CHAIN — prove it end-to-end

Each solve.sh runs sequentially on prior end state, self-contained given declared outputs. Cross-round feasibility must hold.

## Multi-turn cheat vectors

MC1 future artifact exposed early, MC2 later test re-runs pipeline, MC3 reads prior /tests/, MC4 over-execution unguarded, MC5 env-bypassed dep, MC6-8 answers in tests, MC9 skip-as-pass, MC10 stub oracle.

## Calibration is per-step (the cascade)

Bar: task level >=1 pass and >=1 fail across models, Avocado not 5/5. Step level every step needs >=1 pass and >=1 fail among trials reaching it. Avocado must reach last step. Calibrate incrementally 1, then 1+2, then 1+2+3.

## Build & prove loop

1. Scaffold codimango task init --type tbench-multi
2. Build shared environment/ covering all steps
3. Per step: solution/solve.sh + tests/test_outputs.py + copy templates/test.sh
4. Prove chain: validate_task.py + run_oracle_chain.py
5. Skip codimango bench validate for multi-step
6. Calibrate cascade

## Known platform issues

Avocado slow 600s default, need 1800. Cannot run step in isolation. bench validate reports missing files. API key permission error.

## What the README must contain

Explain context handling across steps + completion-rate gradient per step.

## instruction.md policy

Personal practice: skill drafts symptom-only instruction.md. Official AAI: human-only, 3P model may NOT author.

## Complexity floor PER STEP + cross-step (merged from single-turn tbench-task-authoring)

From single-turn skill, now required per step AND cross-step:

A step ONLY worth proposing if it ALREADY clears ALL THREE:

(a) Multi-step non-linear intra-step + inter-step carry/pivot chain where discovery N depends on discovering N-1, not single transform.
(b) Behavioral/empirical discriminator observable ONLY by running/probing (bytes od -c/hexdump/cat -A, EXPLAIN, traced interleaving, forward-pass diff, aggregate vs ground truth, carried file/conventions not re-pinned).
(c) Obvious expert approach FAILS per step with >=2 named strong attempts why each wrong, plus cross-step failure losing context/pivot/over-exec.

Hunt hard shapes from start, quality over volume. Lens yielding nothing hard returns few/none — correct not failure. If cannot name >=2 failing attempts per step, no gap — REJECT.

## Difficulty signature per step (from single-turn)

Per step must hit ALL FOUR:

1. Non-obvious diagnosis invisible to casual inspection (cat/less/ls/SELECT looks correct, need probing beneath surface + carried context not re-pinned)
2. Obvious fix incomplete/WRONG (coupled causes/second-order/decoy per step + cross-step losing context/pivot still RED)
3. Overfit-proof held-out disjoint values per step + over-execution negatives trip
4. Nameable partial_failure_mode per step + cross-step (concrete >=1/5 frontier failure)

Also required per task: recall_resistance per step, partial_failure_mode, mechanism chain, predicted per-model cascade rates, one-line litmus defended.

## 5-gate kill + sharp screens per step (from single-turn)

Run in order at ideation per step: name-the-bug, public-algorithm+fittability, wrong-answer (WRONG not unparameterized), difficulty-locus (concept not grader), provenance, plus multi-turn 3-signal and over-execution guard. Fail any → dead/redesign.

Sharp screens: name-the-bug, layer-counts (second layer independently discoverable AND defeats recalled one-liner, fix-first-only stays RED else illusory coupling), scale/unit weak (off by few percent needs byte/state discriminator + second assertion), differential non-guessable AND reliably solvable + bounded surface, fittability leak (named public algo + shipped pairs least-squares), difficulty-locus, wrong-not-unparameterized, plus multi-turn over-pinned, bare pivot, pre-revealed future.

## Mechanism dedup (from single-turn)

Real duplicate check is by LOAD-BEARING MECHANISM CHAIN not story title. Two candidates different narratives same core insight/carry/pivot mechanism = SAME task, solver cracking one cracks other by recall. Keep only strictly-dominant (richer trap, cleaner grader, load-bearing second assertion per step). Shared story distinct mechanisms fine; shared mechanism distinct stories duplicate. Surface dedup family|title|area|symptom catches near-duplicates, but mechanism dedup happens in Verify stage — agents must diff against already-written tasks under outDir by mechanism chain.

## Litmus + predicted rates (from single-turn)

Top of every dossier: "A senior engineer who knows this domain cold still can't produce correct output in one pass for this step — because recalled approach is WRONG, not just UNPARAMETERIZED, and in multi-turn loses carried context or fails to pivot." Defend per step.

Predicted per-model per-step pass-rates before building (weak mostly fails, frontier >=1/5 pass and >=1/5 fail among reaching, Avocado reaches last). Inverted-difficulty sweet spot. If expect weak 5/5, too easy; all strong 0/5 over-gated/flaky.

## Multi-turn anti-patterns — merged single + multi

- Too easy / recall-solvable: fails any of name-the-bug, fittability, layer-counts, scale/unit, differential bounded, difficulty-locus, wrong-not-unparameterized, missing partial_failure
- Illusory coupling, shared mechanism duplicate
- Decorative chain (≥2 signals no) — ship single-turn
- Over-pinned context (restates area/purpose/conventions) or bare pivot (no motivation, no absence assertion)
- Pre-revealed future or instruction is solution / recalled canonical fix
- Scale/unit magnitude-only, fittable constant, difficulty in grader
- Tags after [[steps]], missing inherit_prior_session, top-level instruction.md/solution leftovers
- Dossier auto-generated from template — describe specific schemas/regexes/tables per step + recall_resistance + partial_failure + litmus
- Fiction name, byte-identical clones
- Unguarded over-execution, broken chain, single-turn leftovers, stub oracle MC10, skip-as-pass MC9, vacuous grading, ungraded core

See generator-defects.md for catalog-scale anti-patterns.
Full originals:
- https://www.internalfb.com/code/notes/users/brendonn/.metacode/skills/tbench-task-authoring-multiturn-ideation/references/multiturn.md (new multi-turn)
- https://www.internalfb.com/code/notes/users/hcjackchen/.claude/skills/tbench-task-authoring/references/tbench-task-rubric.md (old single-turn complexity bar)
