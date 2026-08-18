# What makes a good T-Bench task

This is the bar. Everything in the workflow serves it.

A task is a piece of real command-line work, posed the way it actually arrives: as a vague
report, a symptom, or a desired end goal — **not** a worked specification. Diagnosing what is
really being asked — the root cause of a failure, or the design behind a deliverable — is
itself part of the task and is not handed over. The under-specification is in the
**presentation only**; there is still exactly one correct, testable outcome, pinned by a hidden
test the solver never sees and proven by an oracle that scores 1.0.

## The three rules

1. **Difficulty must be intrinsic, not informational.** The challenge has to live in the
   *work* — stateful, multi-step, cross-component terminal work — where no amount of prompt
   wording can remove it. If writing the prompt out in full also writes out the solution ("run
   `systemctl restart nginx`"), the task has no signal: a capable model can never fail it.
   Choose a scenario where *understanding the system* is the hard part, not transcribing the
   prompt.

2. **Present it the way real work arrives.** Hand over the symptom or the end goal, and stop.
   Do **not** name the cause, the file to change, or the fix — discovering those *is* the task.
   State only what an actual incident report or feature request would contain.

3. **Under-specify the presentation, not the outcome.** Vague framing, single answer. Exactly
   one correct result, pinned by the hidden test. Because T-Bench tests are **hidden at solve
   time**, any concrete contract the test asserts that the solver could *not* infer from the
   container (exact output path/filename, required format/columns, error wording) must be
   stated in the prompt — leaving it out makes the task unfair, not harder. Omit everything a
   proficient engineer could infer from the environment.

## The recall trap

Rule 1 has a sharp edge that's easy to miss: difficulty can be *informational* even when the
**prompt** gives nothing away. A task can be flawlessly symptom-posed, diagnosis-required,
single-outcome, oracle=1.0 and red→green clean — and still be trivial, because the planted root
cause is a **named, canonical bug with a textbook fix**: O(n²) membership → use a set; missing
`try/finally` → connection leak; cache stampede → single-flight; AB-BA → order the locks;
condition-variable hang → wait in a `while`. Capable models hold these as named patterns — they
read the file, match "classic X", and emit the standard fix with no reasoning. The task then
discriminates broken-vs-fixed but **not capable-model-vs-capable-model**, which is the entire
point of an eval.

So the real test is sharper than "is the prompt under-specified?" — it is **"can the diagnosis
be reached by recall instead of reasoning?"** If yes, the task is too easy no matter how vague
the prompt. And the fix is rarely a different prompt; it's engineering the reasoning gap into
the **construction**:

- **Make the obvious fix wrong or incomplete** — the textbook patch should introduce or expose
  a second-order failure the hidden test catches, so a recalled fix fails.
- **Couple multiple factors** so no single named fix clears the bar (e.g. a hot-loop rebuild is
  *why* a memoization key's identity changes → *why* the cache misses; fixing one alone stays
  slow).
- **Plant a decoy** that pre-empts the recalled move: the famous primitive is already present
  and correct (a lock that isn't the bug; locks already ordered), so "add a lock / order them"
  inspects it, finds nothing, and fails.
- **Make recall *actively wrong*, not just absent** — anti-canonical behavior (a dialect that
  contradicts the famous tool it resembles) turns the model's strongest prior into an error it
  must correct by probing; far better than mere unfamiliarity.
- **Require localization** — bury the cause in a realistic, multi-file codebase with plausible
  distractors, not a 15-line file where the bug is the only thing present. Diagnosis must not be
  free.
- **Reject shortcut escapes in the test** (pool size 1, one global lock, swallow the error,
  timeout/poll masking) so a symptom-suppressing non-fix can't pass.

The **differential reimplementation** form (discovery reference, §2) is the cleanest guarantee
that recall can't win: the correct behavior is one specific opaque artifact's quirks, so there
is nothing to recall — the solver must probe and localize. Whatever the form, **screen every
candidate with the `team-aai:novelty-checker` agent before investing in a build.**

## The Level-4 bar (the nine axes)

A task worth shipping clears **Level 4** on every axis. (Levels 1–3 are stepping stones, not
the target.)

1. **Realistic** — genuine command-line work someone would actually do, posed as a vague goal
   or symptom you must first pin down to one testable outcome (e.g. "the importer silently
   drops some rows — make it stop", not "add a NOT NULL check on line 42").
2. **Requires domain expertise** — deep and/or cross-subfield expertise a generalist could not
   supply even handed the approach (fixing a race a naive lock leaves in place; tuning a query
   planner; recovering a corrupted write-ahead log).
3. **Original** — genuinely novel; forces first-principles reasoning, no tutorial covers it. A
   task that *looks* like simple validation but is really a state-machine problem.
4. **The model can't already solve it (but it's solvable)** — calibrated so a frontier model
   (Avocado or Opus) passes **≥1 of 5 and fails ≥1 of 5**. Room to learn, provably solvable.
5. **Targets a missing capability** — an underrepresented language, domain, or task type
   (within your expertise), not the 200th of a saturated category.
6. **Hard to solve, easy to verify** — solving needs sustained multi-step reasoning; the
   verifier is fast, deterministic, and scales to thousands of runs (pass/fail in minutes — no
   human, no GPU, no LLM judge).
7. **Spec leaves room for reasoning** — symptoms only; multiple valid approaches; the agent
   must diagnose, weigh tradeoffs, and choose a strategy.
8. **Tests pass exactly the right solutions and fail the wrong ones** — behavior-based,
   multi-input, edge-case-rich, ungameable; all correct approaches pass, all incorrect fail,
   ground truth hidden on a verifier-only path.
9. **Reproducible** — hermetic and deterministic: pinned deps, ECR base image, no network
   reliance at test time, no prior-run artifacts, hardware-independent; clean across repeated
   runs.

## The inference thought experiment

For every piece of information you're tempted to add to the prompt, ask: *can a proficient
engineer, dropped into this container, infer this without being told?* If yes, leave it out —
stating it over-specifies and leaks the diagnosis. If no, and the hidden test requires it, keep
it. This single test decides what goes in the prompt. (T-Bench twist: the test is hidden, so
the bar for "required" includes every output contract the test asserts.)

## Voice & format (write it like a real ticket)

Plain, everyday words and short sentences, in flowing prose — one to three short paragraphs,
not a structured document. Open with what's going wrong, add a little on the problem, then what
is needed, weaving the few concrete must-haves (output path, format, error text) into the
sentences. Avoid bullet lists and keep blank lines to a minimum. A developer should skim it in
~20 seconds.

## Guardrails (T-Bench specifics)

- The oracle `solution/solve.sh` must score **1.0**, and an empty/no-op solution must score
  **0** — prove red→green before shipping.
- The hidden test must **run the agent's actual artifact** (script/binary/output) on real
  inputs, not just check a file exists or read a pre-staged file. Assert exact values and
  invariants across multiple inputs and edge cases so a shortcut (hardcoding, zeroing,
  swallowing an error) fails.
- **Ground truth and test fixtures live off agent-writable paths** (`/tests/`, `/verifier/`, a
  verify-only mount), never in `/app`. Nothing in the shipped container reveals the answer.
- The environment must **build** (pinned deps, ECR base image) and the symptom must reproduce
  deterministically (seed randomness, control time) so red/green is stable.
- Prefer **one unambiguous** correct outcome; avoid framings where the "intended behavior" is
  itself debatable (those produce multiple defensible fixes and can't be graded cleanly).
- Remove **accidental** difficulty (a broken build unrelated to the task, missing tools). Keep
  difficulty intrinsic.

## Examples (symptom / end-goal only — diagnosis left to the solver)

- A service that "works on the first request but hangs on the third" — a connection-pool
  exhaustion the solver must find and fix.
- "Make these 4 GB of mixed logs searchable by request id under 200 ms" — format, index, and
  query interface left to the solver.
- A database that "won't start after the box ran out of disk" — a corrupted WAL to recover.
- An importer that "sometimes drops records" on real, messy input — find out why and fix it.

## Anti-patterns (do not ship)

- A prompt whose body *is* the solution (the exact command or full procedure). No residual
  difficulty.
- A symptom-posed task whose root cause is a **named, canonical bug with a textbook fix**
  (O(n²)→set, missing try/finally→leak, deadlock→order the locks). Recognition closes the gap
  with no reasoning, so frontier models ace it 5/5 — it discriminates broken-vs-fixed, not
  capable model vs capable model. See "The recall trap".
- Naming the file, service, or root cause a real report wouldn't. Hands over the diagnosis and
  collapses the task back to transcription.
- A test that checks only file existence or reads a pre-staged file without running the agent's
  code — an `echo done > out.txt` passes it.
- A symptom with more than one defensible "correct" fix, or no test that distinguishes the real
  fix from a shortcut.
- Ground truth (oracle output, reference fixtures) COPY'd to an agent-readable path.

## The one-line litmus (from single-turn skill, per step)

Write this at top of every per-step dossier section and defend it before you build:

> "A senior engineer who knows this domain cold still can't produce the correct output in one pass for this step — because the recalled approach is **wrong**, not just **unparameterized**, and in multi-turn loses carried context or fails to pivot."

If you can't defend that sentence for each step, stop and redesign. "Unparameterized" is the trap — expert has right method and only needs to fit constant or flip flag → too easy, however exotic domain. For multi-turn, also: expert who remembers prior steps still fails if they don't carry/pivot correctly.

## Difficulty signature — the positive test PER STEP (from single-turn)

Hardest tasks share four properties — checklist, prefer candidates hitting all four PER STEP. Candidate missing any one probably too easy:

1. **Non-obvious diagnosis — invisible to casual inspection.** Plain `cat`/`less`/`ls`/`SELECT *` makes broken state look *correct*. Finding cause requires running system and probing beneath surface — bytes (`od -c`, `hexdump`, `cat -A`), query plan (`EXPLAIN`), traced multi-process interleaving, reconciling aggregates vs ground truth. Eyeballing fails, recall fails: no name to match until probed. For multi-turn: carried context (file, area, conventions) also invisible to later prompt — must be remembered, not re-pinned.

2. **Obvious fix incomplete or WRONG.** First patch capable model reaches for must still grade RED — because two causes COUPLED across components (fixing one alone fails), textbook patch exposes SECOND-ORDER failure, or DECOY pre-empts recalled move. For multi-turn: fixing current step alone without using carried output, or recreating prior context from scratch, or adding new feature on top without removing old approach (pivot) still RED.

3. **Overfit-proof grading — held-out disjoint values.** Hidden test runs agent's ACTUAL artifact on HELD-OUT input values disjoint from any shipped sample, so fabrication/hardcoding/dropping/suppressing grades RED. If static answer could pass, too easy. For multi-turn: per step held-out, plus over-execution negatives trip if does next step early, regression checks ensure prior steps still pass.

4. **Nameable partial-failure mode per step + cross-step.** Concrete how capable model gets it wrong — specific ≥1/5 failure path per step. If cannot name path, too easy: frontier aces 5/5. Write down BEFORE building, then check against real calibration. For multi-turn also name cross-step: loses carried context, over-pins, misses pivot motivation, does next step early, breaks prior (regression). This cheapest pre-build proxy for Level-4 calibration.

Exemplars (adapted multi-turn):

- **Logstash grok `_grokparsefailure` (TAB-vs-space) → step2 add metric relying on unrepeated grok pattern area.** Fields TAB-separated but grok uses spaces; `cat` renders TABs as whitespace so log looks space-separated (prop1 — must byte-probe). Tag-removal hack strips marker but loses required fields, held-out values defeat fabrication (prop3). Failure: eyeballs file assumes spaces fixes nothing; step2 fails because forgets area/file and re-pins.

- **Lease-lock manager grants two writers (coupled token reuse + HWM not durable) → step2 profile says lock path too slow must pivot.** Two coupled defects two files so fixing either alone stays RED (prop2), inert decoy (worker-local clock check + missing mutex) burns recalled add-a-lock. Failure: fixes token OR HWM not both, chases decoy; step2 misses pivot motivation or keeps ordering.

## The 5-gate kill test PER STEP (~2 min, ideation)

Five sequential kill-gates plus complexity floor and multi-turn gates. Run IN ORDER at ideation — fail any → dead/redesign not build. Each gate points at deeper screen.

1. **Name-the-bug (per step).** Write bug+fix one sentence per step. If YOU can, LLM can → kill. ("ONNX export bakes batch dim → add dynamic_axes" dead). Remedy: empirically-discoverable layer + cross-step carry symptom doesn't imply.

2. **Public-algorithm + shipped-pairs fittability (per step).** Is step core NAMED PUBLIC ALGORITHM (DSP/image/tokenizer/ML idiom mu-law, Malvar demosaic, NFKC, stereo downmix…) AND will you ship golden input→output samples? If BOTH, bespoke constant fittable by least-squares/grid-search from pairs — solver regresses without understanding → kill. Fixes: don't ship enough pairs, make divergence STRUCTURAL (branch/edge-case not scalar), or use oracle whose behavior can't be captured by fitting one constant. (discovery §4 differential tasks)

3. **Wrong-answer test (per step, concrete litmus).** Does recalled/default approach produce WRONG answer — not slightly-off one tweak/constant repairs? If tweak fixes → kill. Expert's method must be WRONG not merely UNPARAMETERIZED. Scale/magnitude, illusory-coupling framings fail here most often.

4. **Difficulty locus (per step).** Where hardness lives — CONCEPT or GRADER (exact counts, tight tolerances, anti-cheat substrings, all-N conjunctions)? If grader makes hard → kill: false pass or over-gate waiting. Concept carries difficulty, grader only pins outcome. Task you had to make hard by tightening tolerances isn't hard, brittle.

5. **Provenance (per step + chain).** Scenario, data, framing your own clean-room authorship? If any 3p-generated or lifted from public bug/issue → kill/rewrite now — can't fix later, contaminates (discovery §6 no public-bug sourcing; AAI scope note).

PLUS multi-turn kill-gates:

6. **3-signal non-decorative per N-1→N** — if ≥2 no, decorative → ship single-turn.

7. **Over-execution guardable?** Can you name negatives per boundary from identifiers later instruction explicitly names? If not, boundary not guardable → redesign.

**Complexity floor — "complex enough" PER STEP means all three together:**

- **Multi-step, non-linear intra-step.** Solution chain where sub-step N depends on DISCOVERING N-1 (detect corruption → identify tensor → rebuild offsets → resolve bf16/fp16 differential). Single transform however fancy not enough. For multi-turn stacks with inter-step carry/pivot chain.

- **Behavioral / empirical discriminator.** Correctness hinges on something ONLY observable by running/probing (bf16-vs-fp16 forward-pass differential; byte layout; query plan), NOT derivable from prompt.

- **Obvious expert approach FAILS.** You can name ≥2 plausible strong-model attempts per step and explain why EACH produces WRONG output. If only one or none — no gap. For multi-turn also need cross-step failure: e.g. fixes current step but loses carried context, or implements both old+new approaches instead of pivoting.

**Calibration target to state in dossier per step cascade.** Aim for inverted-difficulty sweet spot: weak tester mostly fails per step, ≥1 strong model passes ≥1/5 and fails ≥1/5 among trials reaching it. Write predicted per-model pass-rates down BEFORE building per step (e.g. Avocado .6/.66/1.0 cascade, not 5/5 per step). If expect weak 5/5 per step, too easy; all strong 0/5 means over-gated/flaky. Prediction checked against real runs Level-4 calibration step (axis 4). Avocado must reach last step — if dies at step2, earlier step filters too hard, fix earlier first.

## Sharp screening tests — cheap gates per step (from single-turn)

Fastest ways to catch too-easy task, learned from catalogs shipping recall-solvable despite looking clean. Run all four + multi-turn screens on every step candidate:

1. **Name-the-bug test per step.** Read one-line symptom aloud and ask strong model (or yourself honestly): can it name bug family and recite fix from symptom alone? If yes, too easy — difficulty informational not intrinsic. Remedy empirically-discoverable layer something solver only finds by probing data/bytes/state/plan that symptom doesn't imply.

2. **Layer-counts test per step.** "Coupled" or "second" layer adds difficulty ONLY if BOTH (a) independently discoverable in data/bytes/state AND (b) defeats recalled one-liner for first layer. If single idiom/fix already covers both, not two layers — one dressed twice. This is how illusory coupling sneaks in: first defect alone reproduces whole symptom so second neither necessary nor tested. Trace fix-first-layer-only case confirm it STAYS RED before counting second layer. For multi-turn also check cross-step layer: earlier step's output discovery required for later step's second layer.

3. **Scale/unit framings weak by default.** "Off by few percent", "wrong magnitude", "wrong units" soft symptom model usually fixes by recalling scaling gotcha (integer division, float truncation, unit conversion). Keep ONLY if anchored to byte-level/state-level discriminator you must probe AND carries load-bearing SECOND assertion naive rescale fails — e.g. row/doc COUNT must also match not just sum. Lone magnitude check reward-hackable and usually recall-solvable.

4. **Differentials non-guessable AND reliably solvable + bounded surface.** Opaque-oracle form strongest anti-recall shape, but fails two ways. If quirk guessable from symptom, too easy. If independent-discovery surface too large (too many independent quirks/edge cases to reverse-engineer), even strong cannot reach it and task busts ≥1/5-pass half calibration bar. Cap discovery surface to bounded reachable set of quirks, confirm strong would actually reach it in couple probes — solvable not lottery. For multi-turn, quirk may span steps (e.g. step1 implements LRU, step2 says low memory poor hit rate switch to LFU and double capacity — old approach must be removed, test absence).

Additional from old, adapted:

- **Fittability test — differential leak.** If core is NAMED PUBLIC ALGORITHM and divergence is single bespoke scalar/coefficient, any golden pairs shipped or probeable let solver least-squares/grid-search constant without understanding at all. Defend by making divergence STRUCTURAL (added branch, edge-case reordering, changed boundary), keeping reference-probe budget small so fit under-determined, or choosing oracle whose behavior no single fitted constant reproduces. If whole step reduces to "recover one number from pairs", too easy.

- **Difficulty-locus + wrong-not-unparameterized** as in 5-gate — concept must be wrong not unparameterized.

- **Mechanism dedup (from old):** two tasks sharing same load-bearing MECHANISM CHAIN (not just theme) are duplicates — catalog keeps only strictly-dominant member (richer trap, cleaner grader, load-bearing second assertion per step). Shared story distinct mechanisms fine; shared mechanism distinct stories is not. Diff by mechanism not story.

- **Multi-turn specific screens:** over-pinned context (later step restates area/purpose/conventions) kills following signal; bare pivot (no motivation, unreadable as override, no absence assertion) kills overriding; pre-revealed future (earlier instruction names later objectives/filenames) destroys over-execution signal; decorative chain (≥2 coupling signals no); fiction name; byte-identical clones.

## Worked before/after (single-turn exemplar still applies per step)

Same underlying task (log-shipping script silently drops lines when downstream buffer full):

- **Too much handed over:** "In `ship_logs.py`, the `flush()` call drops lines because it doesn't check return value of `sock.send()`; handle short writes in loop." — names file, cause, fix. Pure transcription; capable model can't fail.

- **Calibrated (symptom only):** "Our log shipper is losing lines under load. Everything looks fine at low volume, but when traffic spikes downstream index missing entries — more so busier we get, dropped lines never come back. Find out why and make it stop losing data; every line must arrive complete and in order." — diagnosis (short writes on non-blocking socket, missing retry loop, preserving order) is work. Output contract (complete, in order) stated because hidden test asserts it and solver could not otherwise know it's checked.

## Multi-turn: the additional bar (merged)

Everything above is bar EACH individual step must still clear. Multi-turn earns structure ONLY if on top clears these — full how-to in `references/multiturn.md`:

- **It tests real cross-turn dynamic.** Either **context-following** (step relies on context from prior step — area of code, purpose, conventions, algorithm choice — NOT repeated) or **context-overriding** (step pivots away from prior approach: bad assumption corrected and old approach must be abandoned), ideally both. If neither point, should be single-turn task.

- **Dependency not decorative.** For each N-1→N transition, ≥2 of three must be "yes": step N oracle uses step N-1's *output*; step N instruction does NOT re-state step N-1's context; step N tests verify adaptation to step N-1's *specific* output. Steps each solvable from own instruction alone add zero multi-turn value. Ask blunt: would this be just as good as ≥2 independent single-turn tasks? If yes, decorative — forge genuine carry/pivot or ship single-turn.

- **Complexity floor per step + cross-step coupling:** per step hits all three floor properties (non-linear, empirical discriminator, obvious expert fails ≥2) AND cross-step needs probing carried output, not just re-pinning. Obvious approach fails includes losing context/pivot failures.

- **Over-execution guarded.** Every step with successor has negative tests asserting next step's artifacts don't exist yet, drawn ONLY from identifiers later instruction explicitly names (contamination trap). So agent racing ahead caught — and no earlier instruction pre-reveals later objective. Pick negatives ONLY from later instruction verbatim names.

- **Carried context unrepeated; pivots legible + motivated + absence-tested.** Following step reads like terse real-user follow-up, not recall drill or fresh full spec; overriding step states contradiction+motivation and tests old approach actually removed. See multiturn.md do/don't.

- **Oracle is CHAIN completing end-to-end** (each solve.sh runs on prior end state; no later step starved of carried resource, self-contained given declared outputs not solution internals) and **calibration per step**: every step must among trials reaching it both pass ≥1 and fail ≥1 (min_reward=1.0 cascade). Step flat at 1.0 or 0.0 doesn't discriminate. Avocado must reach last step. Only coupling failures (lost context, regression, wrong data flow from prior output) validate multi-turn design — standalone failures don't.

- **Mechanism dedup across catalog:** tasks sharing same load-bearing mechanism chain are duplicates even if story different. Keep strictly-dominant.

- **Overfit-proof per step + held-out disjoint + no fittable constant:** per step asserts exact values/invariants across multiple inputs/edge cases including positive case naive shortcut breaks, runs agent actual artifact, fixtures/ground truth off agent-writable paths, balance labels (no class ≥60%), don't leak bug in test names.
