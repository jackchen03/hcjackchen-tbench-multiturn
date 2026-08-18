# Promotion reference — single-turn → multi-turn

This file explains how to take a task authored by `tbench-task-authoring` (single-turn, Chinese instruction.md + dossier.md with litmus, complexity_floor, coupling, recall_resistance, partial_failure_mode, mechanism, predicted rates) and promote it into a multi-turn Phase-1 handoff expected by `tbench-task-authoring-multiturn-ideation`.

## Why promotion is non-trivial

A single-turn task that already hits the hard bar (complexity floor, difficulty signature, 5-gate kill, sharp screens) is NOT automatically a good multi-turn task when its steps are just revealed sequentially — that would be decorative (≥2 of 3 coupling signals no). Promotion must forge genuine carry/pivot where step N's diagnosis depends on discovering step N-1 and tests verify adaptation to specific prior output.

## Input shape — what you read

For each slug under `<inputDir>/`:

- `instruction.md` — Chinese symptom-only prose, literal tokens verbatim (paths, filenames, flags, code, column headers, error wording, output contract). Extract output contracts that must be preserved verbatim in English translation.
- `dossier.md` — parse:
  - one-line litmus
  - diagnosis/design (real root cause, not just story)
  - why discriminates (≥2 plausible strong-model attempts why each wrong)
  - recall_resistance (coupling/second-order/decoy/opaque quirk + probing needed)
  - partial_failure_mode (concrete ≥1/5 frontier failure)
  - predicted rates (weak vs strong out of 5)
  - hidden test outline (held-out disjoint values, runs agent artifact)
  - env recipe (ECR base, pinned deps, planted state, canary)
  - oracle sketch (solve.sh steps)
  - mechanism chain (load-bearing not story)
- Optionally: `task.toml` single-turn, `environment/Dockerfile`, `solution/solve.sh`, `tests/` — to judge cross-round feasibility and what Codex will need to cover.

Also `INDEX.md`/`REJECTED.md` for catalog-level mechanism inventory.

## Output shape — handoff package (Phase1 only)

Per promoted task under `<outDir>/<new-slug>/`:

```
task.toml (schema 1.1, tags BEFORE steps, 1800 timeout, inherit_prior_session, min_reward 1.0)
dossier.md (litmus per step + diagnosis + S1/S2/S3 + mechanism chain + recall_resistance per step + partial_failure per step+cross + predicted cascade + hidden-test held-out + over-exec negatives from later identifiers ONLY + regression + env spec + canary + oracle-chain sketch)
environment.spec.md (Dockerfile recipe FROM ECR python:3.11-slim pip install pytest pinned deps covering ALL steps deterministic mtimes git history if needed)
steps/1_<name>/instruction.md (English symptom-only FINAL)
steps/2_<name>/instruction.md (terse follow-up relying on carried context)
steps/3_<name>/instruction.md (if 3 steps, overriding legible motivated + absence)
.meta/handoff.json (machine manifest with stepArtifacts, overExecMap, recall_resistance, mechanism, originalSingleTurnSlug)
```

No solution/, tests/, environment/Dockerfile, README yet.

## Promotion patterns — where boundaries live

Look where state accumulates and interacts across old task's internal chain:

- **Split internal chain (following):** old task's solution internally is chain detect→localize→rebuild→resolve. Split into carried steps. Example: log shipper losing lines: step1 stop losing (complete), step2 ensure order (relies on area/file/conventions not re-pinned).

- **Extend then pivot (overriding, preferred — pool skewed to following+2steps, research wants more overriding):**
  - build→extend→pivot: schema → add constraints → pivot to views
  - correct→under-new-constraint: make correct single-threaded, then make correct under concurrency/idempotency/ordering that invalidates first assumption
  - implement→profile→optimize: correct naive → PROFILE shows slow on production traces → abandon data structure, relative threshold not wall-clock
  - refactor→feature: refactor under conventions → add feature must follow same unrepeated conventions+area
  - recover→operate: recover corrupted to verifiable state → operate on recovered exact shape
  - forensics→new-evidence-pivot: reconstruct/fix → new evidence contradicts hypothesis → different remediation

Bias overriding + 3 steps.

## Verification — hard bar per new step + cross-step

Apply in order per promoted candidate:

1. Recall-risk screen per new step (novelty-checker) — HIGH → redesign
2. Complexity floor per new step (3-part): non-linear intra-step, empirical discriminator (bytes/plan/state/interleaving + carried context), obvious fails ≥2. If any misses → REJECT too easy.
3. 5-gate kill per new step: name-the-bug, public-algorithm+fittability (named public algo + shipped pairs → least-squares fit), wrong-answer (WRONG not unparameterized), difficulty-locus (concept not grader), provenance. Fail any → dead.
4. Sharp screens per new step: layer-counts (fix-first-only stays RED), scale/unit (needs byte/state discriminator + second assertion), differential bounded reachable quirks, fittability leak structural vs scalar, wrong-not-unparameterized.
5. 3-signal non-decorative per transition: S1 oracle coupling uses prior output, S2 instruction non-duplication, S3 test adaptation to specific prior output. ≥2 no → decorative → ship single-turn not promote.
6. Difficulty signature per new step (4 props): non-obvious invisible to cat/less+carried, obvious-fix-incomplete per step+cross-step, recall-proof, overfit-proof held-out disjoint + nameable partial_failure per step+cross-step (losing context/pivot/over-exec/regression). If can't name failure → REJECT.
7. Over-execution guardable: negatives from later identifiers only — if can't name → boundary not guardable.
8. Mechanism dedup by chain: diff against outDir existing + inputDir by load-bearing chain not story. Shared chain different stories duplicate → keep strictly-dominant (richer trap, cleaner grader, second assertion). Shared story distinct mechanisms fine.
9. Cross-round feasibility: single shared environment/ covers every step, oracle CHAIN 1.0 end-to-end no starved resource. Trace carried resource across chain.
10. Single outcome per new step, title keywords fidelity (X2), byte-identical clones (X1).

## Writing per-step instruction.md — translation + splitting

- Translate Chinese old symptom to English natural prose (not word-for-word) but preserve literal tokens verbatim untranslated: paths, filenames, flags, env vars, code, column headers, error wording, output contracts. Those are output contract — translating breaks test/unfair.
- Per new step symptom/end-goal only, never cause/file/fix. Don't let step become spec restating rules/algorithm or naming fix mechanism. Give observable failure. State output contract hidden tests need that solver can't infer (exact paths/formats/error wording). Omit inferable.
- Later steps terse follow-up assuming shared history, not recall drill ("remember X from step1") nor fresh full spec. Over-pinning kills following signal.
- Pivots legible+motivated: contradiction explicit, motivated (e.g. "sorted array too slow on traces we just profiled — lookups dominate. Switch index to hash map and drop ordering work we added."), what to abandon not just add. Reader of step N alone can tell it overrides N-1. Test absence old approach removed.
- Never pre-reveal later steps objectives/filenames — over-execution signal depends on not knowing. Only generic "more steps follow; conserve resources" allowed.
- Title keywords must appear in instruction body describing work there.

## Writing dossier — merged goods

Per promoted task dossier must include (from old+new):

- Litmus per task+per step defended (senior engineer still can't one-pass because WRONG not UNPARAMETERIZED + loses context/fails pivot)
- Diagnosis per step + cross-step S1/S2/S3 why not decorative, mechanism chain load-bearing
- recall_resistance per step + cross-step, partial_failure_mode per step+cross-step concrete ≥1/5, why discriminates ≥2 attempts per step why each wrong
- Predicted per-model per-step cascade rates before building (weak mostly fails, frontier ≥1/5 pass ≥1/5 fail among reaching, Avocado reaches last) — target inverted sweet spot
- Hidden-test plan per step held-out disjoint values, runs agent artifact, fixtures off /app, exact values/invariants/asserts, edge cases, positive case naive shortcut breaks, balance labels no class ≥60%
- Over-execution negatives from later identifiers ONLY + regression checks for steps modifying prior artifact
- Cascade plan coupling vs standalone failures, how each step hits ≥1 pass ≥1 fail
- Env spec ECR python:3.11-slim pip install pytest pinned deps covering all steps deterministic mtimes git history mapping file tracked then removed if needed, canary GUID fresh uuid4
- task.toml skeleton schema 1.1 tags BEFORE steps 1800 timeout inherit_prior_session min_reward 1.0 no root verifier/agent
- Oracle-chain sketch per step self-contained given declared outputs not solution internals
- What omitted/inferable vs kept/non-inferable contract per step

## Environment.spec.md

FROM ECR, pip install pytest, apt-get sqlite3 git bash pinned, creates fixtures for ALL steps deterministic mtimes git repo history mapping file tracked then removed so working tree absent but log shows it, ensure no DB/CLI at start if old task had none, what every step needs, what NOT to invent, canary placeholder, allow_internet rationale.

## task.toml skeleton

schema_version=1.1, slug==dir name clean kebab no numeric suffix, title family dynamic tags BEFORE steps root or under [metadata] NOT after, include [environment] build_timeout, then [[steps]] blocks name dependencies inherit_prior_session min_reward timeouts, no root verifier/agent.

## .meta/handoff.json

{ taskSlug, canaryGuid fresh uuid4, difficulty:"hard", category:"iterate_on_feature", dynamics:["context-following","context-overriding"], stepArtifacts:{"1":["/app/..."]}, overExecMap:{"1":["/app/report.json"]}, recall_resistance, partial_failure_mode, mechanism, predicted_rates, originalSingleTurnSlug, originalSingleTurnFamily }

## Catalog emission

After promotion workflow returns:

```
python3 <skill-dir>/scripts/check_catalog_uniqueness.py <outDir> --verbose
python3 <skill-dir>/scripts/build_catalog.py <workflow-output-file>
```

build_catalog prints unproven until Codex runs run_oracle_chain.py — honest.

Per task later (Codex Phase2):

```
python3 <skill-dir>/scripts/run_oracle_chain.py <outDir>/<slug>  # DO-NOTHING FAIL before, ORACLE 1.0 chain, GREEN >0 executed 0 skipped, OVER-EXEC trip
```

## Examples promotion

- Single: log shipper losing lines under load, every line complete and in order → Multi: step1 stop losing complete, step2 ensure order too (following), step3 sorted approach too slow on production traces → switch hashmap drop ordering (overriding+absence)
- Single: rate limiter token bucket 100 Redis rl: → Multi: step1 add rate limiter token bucket, step2 add metrics for throttled (following), step3 low memory poor hit rate → switch LFU double capacity remove LRU (overriding)
- Single: make 4GB mixed logs searchable by request id <200ms → Multi: step1 parse/normalize to precise output, step2 build index relying on earlier exact output+conventions (following), step3 spec change new field/different key overrides earlier shape (overriding)

## Anti-patterns promotion

- Too easy per new step (fails any gate/sharp, no real partial_failure) → REJECT, keep single-turn
- Illusory coupling per new step (first defect alone reproduces whole symptom)
- Shared mechanism duplicate chain → keep dominant
- Decorative chain ≥2 signals no
- Over-pinned context / bare pivot / pre-revealed future
- Scale/unit magnitude-only, fittable constant, difficulty in grader
- Tags after steps, missing inherit_prior_session, top-level leftovers
- Dossier auto-generated from template, fiction name, byte-identical clones
- Unguarded over-execution, broken chain starved, stub oracle MC10, skip-as-pass MC9, vacuous grading

Full originals:
- single-turn: https://www.internalfb.com/code/notes/users/hcjackchen/.claude/skills/tbench-task-authoring (complexity floor, 5-gate, difficulty signature, litmus, sharp screens, mechanism dedup)
- multi-turn: https://www.internalfb.com/code/notes/users/brendonn/.metacode/skills/tbench-task-authoring-multiturn-ideation (3-signal, over-exec, carry/pivot, cascade, chain)
