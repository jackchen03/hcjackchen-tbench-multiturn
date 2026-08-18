# Team mode: discovering many MULTI-TURN T-Bench tasks at once

When the user wants a *catalog* of multi-turn terminal tasks from a seed (not one), fan out a
team. The bundled workflow `scripts/bulk-discovery.workflow.js` implements this; this file
explains the design so you can adapt or tune it. **Merged with single-turn `tbench-task-authoring` complexity bar.**

## Shape

Survey (parallel, barrier) → dedup surface + **mechanism** (load-bearing chain, not story) → **pipeline**:
Verify+Author (with complexity floor, 5-gate kill, difficulty signature, sharp screens) → Gate (per task) → return catalog.

1. **Survey** — one scout agent per *lens* (a scenario family framed around a natural step
   boundary; or per subsystem for a repo seed). Each proposes candidate multi-turn tasks: title,
   family, overall symptom, suspected cause/design, the **dynamic** (context-following /
   context-overriding / both), a **step_sketch** of 2–3 steps (each with its goal and what it
   *carries from* or *pivots against* the prior step), why the step boundary is real
   (`why_multiturn`), intrinsic difficulty, **complexity_floor** per step (how it clears ALL THREE: multi-step non-linear intra-step + behavioral discriminator + obvious approach fails ≥2), **coupling** (specific coupling/second-order/decoy/opaque quirk making recall fail per step + cross-step), **candidate_partial_failure** per step + cross-step, single-outcome-per-step, confidence. Scouts are blind
   to each other, so different lenses surface different carries/pivots.

   **HUNT HARD SHAPES FROM START** (from old single-turn skill): scouts ONLY propose candidates that ALREADY clear complexity floor and actively seek coupling/emergence. Don't cast wide easy net then prune — quality over volume. Lens that yields nothing hard returns little/nothing — correct not failure.

   **ANTI-CHEAT + DIFFICULTY CONTRACT**: each candidate must be truly distinct by mechanism chain, not just renamed copy. Two candidates different titles must have DIFFERENT area, symptom, CSV schemas, regexes, mapping file names, DB tables, AND different load-bearing mechanism chain. Title keywords must describe work that will be there (fiction names rejected). Every candidate must hit HARD difficulty signature PER STEP (non-obvious diagnosis invisible to cat/less, obvious-fix-incomplete, recall-proof, overfit-proof held-out with disjoint values) + genuine cross-step dependency (3-signal test) + over-execution guardable + single outcome per step. See `tbench-task-rubric.md` difficulty signature.

   Workflow injects HARD contract into both survey and verify prompts so whole team works to one bar. Default hard targets recall-resistant tasks hitting all four signature properties per step + coupling, rejects anything 5/5 per step.

2. **Barrier + dedup — surface AND mechanism** — collect all candidates and dedup by family+title+area+symptom (expanded from just family+title) to catch near-duplicates, PLUS **mechanism dedup** (from old skill): real duplicate check is by LOAD-BEARING MECHANISM CHAIN, not story. Two candidates with different narratives but same core insight/carry/pivot mechanism are SAME task, solver cracking one cracks other by recall. Example: PostgreSQL default window frame `RANGE` lumps peer rows surfaced as running-balance bug and cumulative-revenue bug — one mechanism, collapsed to one task. Keep only strictly-dominant member of shared-mechanism pair (richer trap, cleaner grader, load-bearing second assertion). Verify prompt instructs agents to do this; for high precision add post-pass re-cluster by mechanism. Shared story distinct mechanisms fine; shared mechanism distinct stories is duplicate. Legitimate barrier: dedup genuinely needs every scout's full list.

3. **Verify+Author — forcing function for hard bar** — one agent per *unique* candidate. It confirms (a) a single shared `environment/` can be built covering every step and the oracle **chain** scores 1.0 end-to-end (no starved later step), (b) the dependency is **not decorative** (the 3-signal test: S1 oracle coupling uses artifacts step N-1 PRODUCED, S2 instruction does NOT restate prior context, S3 tests verify adaptation to specific prior output — if <2, decorative), (c) each step clears complexity floor + 5-gate kill test + sharp screens + difficulty signature + recall-proof, (d) per-step **recall_resistance** (why recall can't win: coupling/second-order/decoy/opaque quirk + probing needed) and **partial_failure_mode** (concrete ≥1/5 way frontier fails per step + cross-step losing context/pivot) are articulable — if verifier can't name real partial_failure_mode per step, REJECT as too easy (cheapest proxy for Level-4 calibration). Also enforces **catalog-level anti-cheat**: tags BEFORE [[steps]] root-level via tomllib, Dockerfile must `pip install pytest`, no gaming verifier (regex defined must be USED with sys.exit), step3 git behavior-graded. If survives, writes each step's symptom-only `instruction.md` plus privileged `dossier.md` (must NOT say "Auto-generated from template" - must describe specific schemas/regexes/tables per step making THAT task unique, plus litmus, recall_resistance, partial_failure_mode, predicted cascade pass-rates, one-line litmus defended).

4. **Gate** — second pipeline stage, one agent per authored task. Runs `python3 <skill-dir>/scripts/validate_task.py <task-dir>`, fixes cause of each blocking finding, re-runs up to 4 rounds. Prompt carries forbidden-fix list explicitly (no deleting tests, no skips, no unfalsifiable assertions, no unconditional reward, no echo-only `solve.sh` written just to stop looking like stub) and tells it returning `clean=false` with remaining codes is good outcome — dishonest pass is not. Because gate is pipeline stage, task B still authored while task A gated.

5. **Return** — counts, gate-clean tasks, gate-blocked tasks with remaining codes, and candidates rejected at authoring (including those failing complexity floor, 5-gate, sharp screens, mechanism duplicate, missing partial_failure). `proven: false` returned unconditionally: static gate necessary not sufficient. Returned tasks include `recall_resistance` and `partial_failure_mode` per step for spot-checking.

Verification runs as its own stage rather than trusting scouts, but division is **hard-recall, not wide-recall** (from old skill): scouts recall *hard candidates* (find every genuinely complex, coupled, emergent problem lens supports — not every plausible task), verify optimizes for precision (kill weak slipped through). Pushing difficulty bar into survey deliberate — indexing on complex problems up front yields better catalog than generating pile easy candidates and pruning down, stops verify becoming mass-rejection bottleneck. Scouts optimize recall, verify precision, gate mechanical rather than persuadable.

## After the workflow returns — two things it cannot do for you

```bash
python3 <skill-dir>/scripts/check_catalog_uniqueness.py <outDir> --verbose
python3 <skill-dir>/scripts/run_oracle_chain.py <outDir>/<slug>       # per task
```

The catalog gate adds the two checks that only exist **across** tasks: byte-identical clones
(one problem measured N times) and fiction names (a slug promising work the task does not
contain). Both were real fatal findings — the full record is in `generator-defects.md`.

The chain runner is the only thing that proves a task works, because it actually builds the
image and runs each step's tests before and after its oracle. Until it has run, every task in the
catalog is a **draft**; `build_catalog.py` prints `unproven` in the INDEX proof column to keep
that visible rather than letting a confident-looking table imply validation that never happened.

## Lenses

The workflow ships with lenses framed around a natural carry or pivot (build→extend→pivot,
broken-service-then-reworked-assumption, staged data pipeline, correct-then-under-new-constraint,
implement-then-profile-then-optimize, refactor-then-feature, recover-then-operate,
forensics-then-new-evidence-pivot). **Adapt the lens list to the seed.** For a *repo* seed, lens
by subsystem and ask each scout what multi-turn task that slice supports (where does work carry
forward or get overturned?). Aim for 6–10 lenses.

## Difficulty contract (from single-turn skill)

Injected into BOTH survey and verify so whole team works to one bar:

- `difficulty: 'hard'` (**default**) — targets recall-resistant multi-turn tasks hitting all four difficulty-signature properties PER STEP + cross-step coupling: non-obvious diagnosis invisible to casual inspection (must probe bytes/plan/state/interleaving + carried context), obvious-fix-incomplete (coupled/second-order/decoy per step + carry/pivot loss), recall-proof, overfit-proof held-out grading. Verify rejects anything 5/5 per step.
- `difficulty: 'span'` — mixed medium→hard still rejects one-command answers, pure-recall bugs, decorative chains, but doesn't demand full hard signature per step.

Verify is forcing function: every authored task must return substantive `recall_resistance` per step and `partial_failure_mode` per step+transition. If verifier can't name real failure mode per step, REJECT too easy — cheapest pre-build proxy for cascade calibration. Both fields come back in catalog; skim when spot-checking.

You can sharpen bar further per-run by tuning lenses toward invisible/coupled defects (as log-pipeline-v2 and sql-v2 did) — contract and lenses compose.

## Tuning

- `maxCandidates` (default **16** — lower than single-turn 24, because multi-turn tasks heavier to author/calibrate) caps how many candidates get verify+author pass. Keeps highest-confidence and **logs what dropped** — never cap silently. Raise for coverage.
- **Adversarial recall-refutation (next lever for max precision, from old skill).** For hard multi-turn catalog, add cheap per-candidate refuter between survey and author: per step "try to solve this in one step by recalling named bug + textbook fix — can you?" plus per transition "try to solve step N from its instruction alone without prior context / ignoring pivot motivation". Reject any candidate refuter one-shots or solves N without carry. Catches recall-solvable and decorative tasks verify rationalizes as usable. Not wired by default (keeps cost predictable); add when precision > throughput.
- For higher precision, add adversarial verifier per surviving candidate prompted to *refute* that dependency is non-decorative AND that each step clears complexity floor (multi-step non-linear, behavioral discriminator, obvious approach fails ≥2) and keep only survivors.
- For thorough sweep, add second survey round with "what carry/pivot did first pass miss?" prompt and merge — discovery recall-bound, completeness pass catches tail.
- Token budget: if user gave "+Nk" directive, scale lens count / maxCandidates to `budget.total`; otherwise static defaults.
- Dedup by mechanism, not story: after barrier, re-cluster final catalog by mechanism chain (differential quirks, coupled defects, carry/pivot type) and drop dominated members, keep strictly-dominant (richer trap, cleaner grader, load-bearing second assertion per step).

## Lenses — adapted to seed + complexity floor

Old skill lenses (broken-service, build/deps, data-recovery, data-processing, concurrency, performance, multi-service, security-forensics) plus new multi-turn framing (build→extend→pivot, broken-service-then-reworked-assumption, staged pipeline, correct-then-under-new-constraint, implement-then-profile-then-optimize, refactor-then-feature, recover-then-operate, forensics-then-new-evidence-pivot). **Adapt to seed.** For repo seed, lens by subsystem (api/persistence/jobs/cli/build) and ask each scout what multi-turn task that slice supports where work carries forward or gets overturned. Aim 6–10 lenses; too few scout drowns, too many overlap. Each lens must hunt hard shapes from start seeking coupling/emergence, not padding.

## After survey — hard bar enforcement

Each scout returns: title, family, area, symptom, suspected_cause, dynamic, step_sketch (goal+carries_or_pivots), why_multiturn, intrinsic_difficulty, **complexity_floor** (concrete how clears ALL THREE per step), **coupling** (specific coupling/second-order/decoy/opaque quirk), **candidate_partial_failure** per step+cross-step, single_outcome, confidence. Quality over volume: handful genuinely clearing floor beats long list padded with easy. If lens yields nothing hard, return few/none rather than padding.

## Running it reliably (hard-won ops)

A first real run lost ~4h to these; the bundled workflow now defaults around them, but know why:

- **No-tools on ideation, tools on authoring.** A survey/brainstorm agent with the full toolset + a
  schema spams `Read` on repo/skill/memory files and mostly never calls `StructuredOutput`
  (measured: 410 `Read`, ~5 of 130 agents emitted). `surveyPrompt` now carries a no-tools protocol —
  keep it. Do NOT add it to `verifyPrompt`: verify+author legitimately needs tools to check
  buildability and write files.
- **Route pure-ideation to a light model; the heavy model's endpoint stalls at fan-out.** Even with
  no-tools, a single serial run, and a stable model, ~35–55% of ideation agents on the heavy
  inherited model (Opus/Fable) fail with `agent stalled (no progress for 180000ms) ×6`, each burning
  ~18 min of retries (~2 h/run). The workflow defaults `surveyModel:'sonnet'` (a sonnet fan-out
  completed 16/16 and 6/6 cleanly in minutes here); if verify+author also stalls, pass
  `authorModel:'sonnet'`.
- **Over-provision ~2×.** Expect ~50% loss on the heavy model, near-0 on sonnet. Size lens count /
  `maxCandidates` to about twice the yield you need, and top up any shortfall in a *second* run that
  passes the already-produced titles as an avoid-list — don't assume one run lands the target.
- **Launch once, then leave it alone.** Never self-poll with a backgrounded `sleep`+check: a
  completing background task fires a notification that starts a turn and interrupts the workflow's
  in-flight subagents (`[Request interrupted by user]`). Watch read-only via `/workflows`; wait for
  the workflow's own completion notification. Don't overlap two big runs, and don't `/model`-switch
  mid-run — both cause mass stalls.
- **Harvest from `<transcriptDir>/journal.jsonl`, not the returned count.** A stalled screen/curate
  stage silently defaults every idea to kept/unscored — an inflated "all top-tier, 0 weak" that
  hides the missing screen. The journal has one `{"type":"result",...}` line per completed agent with
  its full return value.
- **Validate structured outputs; redraft the degenerates.** Even sonnet returns a few
  `StructuredOutput retry cap exceeded` and the occasional schema-valid junk (`"Test"`/`"测试"`) at
  scale. Guard for too-short/placeholder fields and re-run only the offenders (cheap).
- **For a big idea set fed to a later pass (re-curate, scaffold, source-gen), embed it in the SCRIPT
  (≤512 KB), not args**, have those agents RETURN files/scores as structured data, and write to disk
  **inline**. A fleet that each Read+design+write-many+verify on disk stalls on the 180s watchdog and
  can land 0 files; returning-then-writing-inline never loses work.

## After it returns — spot-check with hard bar

The workflow runs in background and notifies on completion. Then:

1. Spot-check 2–3 authored tasks against FULL bar (old+new):
   - Each step's `instruction.md` (symptom-only? one outcome per step? inference thought-experiment per sentence? nothing inferable *or carried* leaked? later step doesn't re-pin earlier context? pivots legible+motivated+absence assertion? no pre-reveal of later steps? output contract hidden test needs stated? literal tokens verbatim? English natural prose? Would this be just as good as N single-turn? If yes, decorative)
   - `dossier.md` cross-step design (3-signal evidence S1/S2/S3 per transition, over-execution negatives from later identifiers only, oracle-chain feasibility no starved resource, cascade plan, **load-bearing mechanism chain** not story, **recall_resistance** per step (why recall can't win: coupling/second-order/decoy/opaque quirk + probing), **partial_failure_mode** per step+transition concrete ≥1/5 frontier failure, **one-line litmus** defended, **predicted per-model pass-rates** per step cascade with inverted-difficulty sweet spot weak mostly fails ≥1 strong passes ≥1/5 fails ≥1/5, Avocado reaches last step).
   - Mechanism: diff against other tasks in outDir by load-bearing chain — if shares core insight/carry/pivot with existing, keep only strictly-dominant (richer trap, cleaner grader, second assertion).
   - Hidden test outline: overfit-proof held-out disjoint values per step, runs agent actual artifact, fixtures off `/app`, asserts exact values/invariants/edge cases, positive case naive shortcut breaks.
   - Also check sharp screens: name-the-bug per step fails? layer-counts second layer independently discoverable + defeats recalled one-liner and fix-first-only stays RED? scale/unit anchored to byte/state discriminator + second assertion? differential bounded reachable quirks non-guessable and reliably solvable? fittability leak (named public algo + shipped pairs → least-squares) killed? difficulty-locus concept not grader? wrong-not-unparameterized? If any fail, REJECT.

   Fix or re-run any slipped.

2. Write `INDEX.md` in `outDir` with single `## Usable tasks` table — columns `# | family | dynamic | steps | title | conf | dir | mechanism`, where `dir` is REAL folder derived from written instruction.md path not model-reported slug, `mechanism` is load-bearing chain (e.g. coupled token reuse+HWM not durable + pivot to hashmap). Keep INDEX.md clean: no provenance line, no counts, no rejected section. Put rejected candidates + reasons (including complexity floor miss, 5-gate fail, sharp screen fail, mechanism duplicate, missing partial_failure) in separate `REJECTED.md`. Use bundled `scripts/build_catalog.py <workflow-output-file> [outDir]` — reads Workflow `.output` file and writes both in exactly this format (deriving dir from written path so links resolve).

3. Present catalog grouped by family/dynamic/mechanism, highlighting recall_resistance and partial_failure_mode per task, and offer to build gradeable **multi-step bundle** (task.toml schema 1.1 + steps/ + shared environment/ FROM ECR pip install pytest + pinned deps + deterministic fixtures + git history if needed, proven oracle-chain = 1.0 end-to-end + each step red→green + over-execution tripped, then calibrated per-step cascade with Avocado reaching last step) for any they pick.

4. Remember: no task "passing" until `run_oracle_chain.py` proves DO-NOTHING 0, ORACLE 1.0 chain, GREEN >0 executed 0 skipped, OVER-EXEC negatives trip. `build_catalog.py` prints `unproven` until that runs — honest not bug.
