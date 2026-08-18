export const meta = {
  name: 'bulk-tbench-multiturn-task-discovery',
  description: 'Survey a seed (repo/tool/domain) with a team of agents, then verify and author as many good MULTI-TURN terminal-bench tasks as possible (each: 2-3 coupled steps, per-step symptom-only instruction.md + a cross-step author dossier), then GATE each one with the fail-closed static validator so no scaffold oracle or skip-as-pass verifier ships.',
  phases: [
    { title: 'Survey' },
    { title: 'Verify+Author' },
    { title: 'Gate' },
  ],
}

// ---- inputs ----------------------------------------------------------------
const seed = (args && (args.seed || args.repoPath)) || '/tmp/seed'
const outDir = (args && args.outDir) || '/tmp/tbench-multiturn-tasks'
const MAX = (args && args.maxCandidates) || 16
const SKILL_DIR = (args && args.skillDir) || '~/.claude/skills/tbench-task-authoring-multiturn'
const DIFFICULTY = (args && args.difficulty) || 'hard'

const SURVEY_MODEL = (args && args.surveyModel) || 'sonnet'
const AUTHOR_MODEL = (args && args.authorModel) || undefined

// Difficulty contract — from single-turn tbench-task-authoring skill, adapted for multi-turn HARD bar
const HARD_CONTRACT = [
  'DIFFICULTY BAR — HARD multi-turn, recall-resistant, non-decorative. Default target.',
  'Per-step must satisfy ALL FOUR difficulty-signature properties:',
  '1. Non-obvious diagnosis invisible to casual inspection (plain cat/less/ls/SELECT looks correct); diagnosing REQUIRES running system + probing beneath surface — bytes (od -c, hexdump, cat -A), query plan (EXPLAIN), traced multi-process interleaving, reconciling aggregates vs ground truth, plus carried context not re-pinned.',
  '2. Obvious fix incomplete or WRONG per step: first patch capable model reaches for still grades RED — two causes COUPLED across components (fixing one alone fails), textbook patch exposes second-order failure, or decoy pre-empts recalled move. Cross-step: losing carried context, over-pinning, missing pivot, or doing next step early still RED.',
  '3. Recall-proof per step: NOT solvable by recognizing named canonical bug + emitting textbook fix (O(n^2)->set, add-a-lock, order-the-locks, bump-isolation, add-an-index, try/finally). If competent model could one-shot from name, REJECT.',
  '4. Overfit-proof per step: hidden test runs agent ACTUAL artifact on HELD-OUT input values disjoint from any shipped sample, so fabricated/hardcoded/drop/suppress shortcuts grade RED per step, plus over-execution negatives and regression.',
  'Cross-step: >=2 of 3 coupling signals yes (S1 oracle uses prior output, S2 instruction avoids restating prior context, S3 tests verify adaptation to specific prior output). Over-execution negatives drawn ONLY from later identifiers. Generic "more steps follow" only, never pre-reveal.',
  'Calibration: frontier per step among trials reaching it pass >=1/5 and FAIL >=1/5, Avocado must reach last step. Task flat at 1.0 per step REJECT however clean.',
  'Every step MUST have substantive recall_resistance (coupling/second-order/decoy/opaque quirk + probing) and partial_failure_mode (concrete >=1/5 frontier failure). If verifier cannot name real failure per step, REJECT too easy.',
  'Quality over volume: smaller catalog genuinely hard beats large easy one. If lens yields nothing hard, return few/none not padding.',
].join('\n')
const DIFFICULTY_CONTRACT = DIFFICULTY === 'hard' ? HARD_CONTRACT : ('DIFFICULTY BAR — span medium->hard. Every step still needs intrinsic, stateful, multi-step difficulty (prompt cannot encode fix) and exactly one testable outcome per step, plus non-decorative carry/pivot. Reject one-command answers, pure-recall bugs, decorative chains.')

const LENSES = (args && args.lenses) || [
  { key: 'build-extend-pivot', area: 'Build a component, then EXTEND it, then hit a requirements change that OVERRIDES the earlier approach (e.g. schema -> add constraints -> pivot to views; parser -> add a token type -> the grammar assumption breaks and must be reworked).' },
  { key: 'broken-service', area: 'A long-running service/daemon: first make it start/behave, then a later step changes the operating assumption (a config that seemed right is wrong under load) so the earlier fix must be reworked.' },
  { key: 'data-processing', area: 'A data pipeline built in stages: parse/normalize, then transform/index relying on the earlier stage\'s output and conventions, then a spec change (new field / different key) that overrides the earlier shape.' },
  { key: 'concurrency', area: 'Make an operation correct, then make it correct UNDER a new constraint introduced later (concurrency / idempotency / ordering) that invalidates the first single-threaded assumption.' },
  { key: 'performance', area: 'Implement a correct version, then PROFILE and optimize relying on the earlier implementation/tests, where the naive data structure chosen first must be abandoned (relative threshold measured in the test, never wall-clock constants).' },
  { key: 'refactor-then-feature', area: 'Refactor/modernize code under stated conventions, then add a feature that must follow those same (unrepeated) conventions and the area established in the refactor.' },
  { key: 'data-recovery', area: 'Recover/repair corrupted data to a verifiable state, then operate on the recovered artifact in a later step relying on its exact recovered shape.' },
  { key: 'security-forensics', area: 'Reconstruct events / fix a vulnerability, then a later step pivots on new evidence that contradicts the initial hypothesis and forces a different remediation.' },
]

const SURVEY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          title: { type: 'string' },
          family: { type: 'string' },
          area: { type: 'string' },
          symptom: { type: 'string' },
          suspected_cause: { type: 'string' },
          dynamic: { type: 'string', enum: ['context-following', 'context-overriding', 'both'] },
          step_sketch: {
            type: 'array',
            items: {
              type: 'object',
              additionalProperties: false,
              properties: {
                goal: { type: 'string' },
                carries_or_pivots: { type: 'string' },
              },
              required: ['goal', 'carries_or_pivots'],
            },
          },
          why_multiturn: { type: 'string' },
          intrinsic_difficulty: { type: 'string' },
          complexity_floor: { type: 'string', description: 'How clears ALL THREE per step: multi-step non-linear, behavioral discriminator, obvious expert fails >=2' },
          coupling: { type: 'string', description: 'Specific coupling/second-order/decoy/opaque quirk per step + cross-step making recall fail' },
          candidate_partial_failure: { type: 'string', description: 'Concrete >=1/5 frontier failure per step + cross-step losing context/pivot/over-exec' },
          mechanism: { type: 'string', description: 'Load-bearing mechanism chain, not story — e.g. coupled token reuse+HWM not durable + pivot to hashmap' },
          single_outcome: { type: 'boolean' },
          confidence: { type: 'number' },
        },
        required: ['title', 'family', 'area', 'symptom', 'suspected_cause', 'dynamic', 'step_sketch', 'why_multiturn', 'intrinsic_difficulty', 'complexity_floor', 'coupling', 'candidate_partial_failure', 'mechanism', 'single_outcome', 'confidence'],
      },
    },
  },
  required: ['candidates'],
}

const VERIFY_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    usable: { type: 'boolean' },
    reason: { type: 'string' },
    title: { type: 'string' },
    slug: { type: 'string' },
    family: { type: 'string' },
    dynamic: { type: 'string' },
    confidence: { type: 'number' },
    n_steps: { type: 'number' },
    mechanism: { type: 'string' },
    recall_resistance: { type: 'string', description: 'Per step why recall cannot win — coupling/second-order/decoy/opaque quirk + probing, and cross-step' },
    partial_failure_mode: { type: 'string', description: 'Concrete >=1/5 frontier failure per step + cross-step losing context/pivot/over-exec/regression' },
    predicted_rates: { type: 'string', description: 'Predicted per-model per-step pass-rates before building (weak mostly fails, strong >=1/5 pass and >=1/5 fail among reaching, Avocado reaches last)' },
    steps: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          name: { type: 'string' },
          goal_en: { type: 'string' },
          instruction_md: { type: 'string' },
          instruction_path: { type: 'string' },
          complexity_floor: { type: 'string' },
          recall_resistance: { type: 'string' },
          partial_failure: { type: 'string' },
        },
        required: ['name', 'goal_en', 'instruction_md', 'instruction_path', 'complexity_floor', 'recall_resistance', 'partial_failure'],
      },
    },
    instruction_path: { type: 'string' },
    dossier_path: { type: 'string' },
    test_outline: { type: 'string' },
  },
  required: ['usable', 'reason', 'title', 'slug', 'family', 'dynamic', 'confidence', 'n_steps', 'mechanism', 'recall_resistance', 'partial_failure_mode', 'predicted_rates', 'steps', 'test_outline'],
}

const NO_TOOLS = 'OUTPUT PROTOCOL — READ FIRST. Answer entirely from your own expert knowledge. Use NO tools: do not read files, do not search the web, do not call ToolSearch or any MCP/search/code tool, do not explore. Do not narrate. Your ONLY action is to call the StructuredOutput tool immediately. Any other tool call will stall and fail the task.'

function surveyPrompt(lens) {
  return [
    NO_TOOLS,
    'You are scouting to DISCOVER candidate MULTI-TURN terminal-bench TASKS — a chain of 2-3 sequential prompts an agent works through in ONE carried-over Docker session,graded by hidden tests per step.',
    'Seed: ' + seed,
    'Focus: ' + lens.area,
    '',
    DIFFICULTY_CONTRACT,
    '',
    'A candidate only counts as MULTI-TURN if it tests context-following (later step relies on prior context NOT repeated) or context-overriding (later step pivots away, bad assumption corrected) — ideally both across 3 steps. Bias overriding +3 steps.',
    '',
    'HUNT HARD SHAPES FROM START — from single-turn tbench-task-authoring skill:',
    'Do NOT cast wide net plausible tasks and prune easy later — index on COMPLEX COUPLED EMERGENT problems up front. Only propose if ALREADY clears 3-part complexity floor per step: (a) multi-step non-linear chain where sub-step N depends on discovering N-1, (b) behavioral/empirical discriminator observable ONLY by running/probing (byte layout od -c/hexdump, query plan EXPLAIN, traced interleaving, forward-pass differential, aggregate vs ground truth), (c) obvious expert approach FAILS with >=2 named strong attempts why each wrong. Quality over volume. Lens yielding nothing hard returns few/none — not failure.',
    '',
    'CRITICAL ANTI-CHEAT + MECHANISM DEDUP (from 2026-08-03 fatal + single-turn mechanism dedup):',
    '- Each candidate MUST be TRULY DISTINCT by LOAD-BEARING MECHANISM CHAIN not story. Two candidates different titles must have DIFFERENT area, symptom, CSV schemas, regexes, mapping file names, DB tables, file paths, AND different mechanism chain (e.g. coupled token reuse+HWM not durable + pivot vs TAB-vs-space grok). Byte-identical solve.sh sets across tasks is fatal cheat (X1). Same mechanism chain different stories is duplicate — keep strictly-dominant.',
    '- Title/slug must describe work THERE. If title says email-alias-migration, candidate must involve email/alias handling not inventory SKU. Grepping title keywords in final task body must succeed (excluding banner and task@example.com). Fiction names rejected X2.',
    '- Candidates must carry INTRINSIC difficulty per step hitting ALL FOUR signature props (non-obvious diagnosis invisible to cat/less, obvious-fix-incomplete, recall-proof, overfit-proof held-out disjoint), GENUINE cross-step dependency 3-signal test, guardable over-execution, single testable outcome per step, red→green, oracle chain 1.0 per step + end-to-end.',
    '',
    'Return per candidate: title; family; area; symptom one-line real incident style NO cause/fix; suspected cause design privileged; dynamic; step_sketch 2-3 steps goal+carries_or_pivots; why_multiturn; intrinsic_difficulty multi-step diagnosis; complexity_floor concrete how clears ALL THREE per step — be concrete or drop; coupling specific coupling/second-order/decoy/opaque quirk per step+cross-step making recall fail — if cannot name drop; candidate_partial_failure concrete >=1/5 frontier failure per step+cross-step losing context/pivot/over-exec — if cannot name drop; mechanism load-bearing chain not story; single_outcome; confidence.',
    'Be thorough, favor real cross-step signal, coupling/emergence, ensure diversity across lenses. Fewer genuinely hard beats long padded easy.',
  ].join('\n')
}

function verifyPrompt(c, slug) {
  const stepSketch = (c.step_sketch || []).map(function (s, i) { return '     ' + (i+1) + '. ' + s.goal + '  (carries/pivots: ' + s.carries_or_pivots + ')' }).join('\n')
  return [
    'You are verifying and authoring ONE candidate MULTI-TURN T-Bench task — applying HARD bar from single-turn tbench-task-authoring skill adapted for multi-turn.',
    'Seed: ' + seed,
    'Output dir: ' + outDir + '/' + slug,
    '',
    'Candidate (draft from scout — treat claims as STARTING POINT not proof, verify each holds, reject if complexity floor or coupling does not survive):',
    '- title: ' + c.title,
    '- family: ' + c.family,
    '- area: ' + c.area,
    '- symptom (draft): ' + c.symptom,
    '- suspected cause (draft): ' + c.suspected_cause,
    '- dynamic: ' + c.dynamic,
    '- step sketch:',
    stepSketch,
    '- complexity_floor claim: ' + (c.complexity_floor || '(none given)'),
    '- coupling / recall-defeater: ' + (c.coupling || '(none)'),
    '- partial_failure draft: ' + (c.candidate_partial_failure || '(none)'),
    '- mechanism chain: ' + (c.mechanism || '(none)'),
    '',
    DIFFICULTY_CONTRACT,
    '',
    'Steps — MUST ALL PASS or usable=false with clear reason, no files:',
    '1. Confirm REAL and gradeable as chain per step: believable Docker env reproduces symptom/deterministic, planted state, ECR base, pinned deps, single hidden test per step can pin single outcome red on base/no-op at step1 FAIL and green after fix, held-out disjoint values per step, no ambiguity >1 outcome. Trace concretely what installed, planted, test asserts. Shared environment/ covers every step, oracle chain 1.0 end-to-end no starved resource (cross-round feasibility). One unambiguous outcome per step singled.',
    '2. Complexity floor per step (from old skill): MUST clear ALL THREE per step — (a) multi-step non-linear intra-step chain where sub-step N depends on discovering N-1, (b) behavioral/empirical discriminator observable ONLY by running/probing (bytes od -c/hexdump/cat -A, query plan EXPLAIN, traced interleaving, forward-pass diff, aggregate vs ground truth) — cat/less/ls/SELECT looks correct, (c) obvious expert approach FAILS per step with >=2 named strong attempts why EACH wrong. If any step misses, usable=false too easy — don\'t build. Also cross-step: obvious approach losing context/pivot/over-exec fails.',
    '3. 5-gate kill test per step (~2 min) IN ORDER — fail any → dead/redesign (from old skill):',
    '   3a Name-the-bug per step: write bug+fix one sentence per step — if YOU can, LLM can → kill. Need empirically-discoverable layer + cross-step carry not implied by symptom.',
    '   3b Public-algorithm+fittability per step: core NAMED PUBLIC ALGO (mu-law, Malvar demosaic, NFKC, stereo downmix) AND shipped/probeable golden pairs → bespoke scalar fittable least-squares/grid-search without understanding → kill unless divergence STRUCTURAL (branch/edge-case/boundary not scalar) or probe budget under-determined.',
    '   3c Wrong-answer test per step — concrete litmus: recalled/default approach must produce WRONG answer not slightly-off tweak/constant repairs — if tweak fixes → kill. Litmus: expert method WRONG not UNPARAMETERIZED. Scale/magnitude/wrong units fails here unless anchored to byte/state discriminator + second assertion.',
    '   3d Difficulty-locus per step: hardness in CONCEPT not GRADER (tight tolerances, exact counts, anti-cheat substrings, all-N). If grader makes hard → kill false-pass/over-gate.',
    '   3e Provenance per step+chain: clean-room own authorship not 3p-generated/lifted from public bug/issue → kill/rewrite now.',
    '4. Sharp screening tests per step (from old): name-the-bug, layer-counts (second layer counts ONLY if BOTH independently discoverable in data/bytes/state AND defeats recalled one-liner for first — trace fix-first-only STAYS RED, else illusory coupling reject), scale/unit weak (off by few percent) keep ONLY if anchored byte/state discriminator + load-bearing second assertion, differential non-guessable AND reliably solvable + bounded reachable quirk set (guessable→too easy, too-large→busts >=1/5 calibration → reject both), fittability leak, difficulty-locus, wrong-not-unparameterized. Fail any → usable=false STOP no files.',
    '5. Genuinely multi-turn not decorative: for each N-1→N at least 2 of 3 coupling signals must hold S1 oracle coupling uses artifacts step N-1 PRODUCED not just env, S2 instruction does NOT restate prior context, S3 tests verify adaptation to specific prior output. If <2 usable=false decorative. Also mechanism dedup: list tasks already written under ' + outDir + ' and diff THIS candidate by LOAD-BEARING MECHANISM CHAIN not story. If shares core insight/carry/pivot mechanism with existing (solver cracking that one cracks this by recall), keep only strictly-dominant member — if existing dominates, usable=false name mechanism overlap in reason; if this dominates proceed (dominated pruned later). Shared story distinct mechanisms fine; shared mechanism distinct stories is duplicate.',
    '6. Difficulty signature per step (4 props) — MUST articulate per step recall_resistance and partial_failure_mode (concrete >=1/5 frontier failure per step + cross-step losing context/pivot/over-exec/regression). If cannot name real failure per step, too easy → usable=false STOP. Per step: non-obvious diagnosis invisible to cat/less requiring bytes/plan/state/interleaving probing, obvious-fix-incomplete (coupled causes/second-order/decoy), recall-proof, overfit-proof held-out disjoint. Cross-step: over-execution negatives from later identifiers only, regression checks.',
    '7. If usable, create output dir and WRITE Phase-1 handoff ONLY (no solve.sh/tests/Dockerfile yet — those Codex Phase 2). Hunt hard shapes not padding, quality over volume:',
    '   - For each step dir steps/<N>_<name>/instruction.md — FINAL symptom-only ENGLISH (multi-turn track canonical English, not Chinese single-turn) — solver-facing. Symptom/end-goal ONLY never cause/file/fix. Because tests HIDDEN, MUST state any output contract hidden test asserts that solver could not infer (exact paths/formats/error wording/col headers) — omit inferable, keep non-inferable. Inference thought-experiment per sentence. Write like real person ticket: plain everyday words short sentences flowing prose 1-3 short paragraphs, concrete must-haves woven in, avoid bullet lists/blank lines, never dense numbered spec. MULTI-TURN RULES: later step must RELY on carried context NOT restate it — over-pinning kills following; pivot must state contradiction+motivation and tell what to abandon not just add, plus absence assertion; NEVER pre-reveal later steps objective/filenames (only generic "more steps follow; conserve resources") else over-execution signal gone. CRITICAL: title/slug keywords must appear in instruction body (excluding banner) and describe work there — fiction name reject. Example good following: "Now extend it to accept hex literals too." not "Recall from step1 we edit parser/tokenizer.py using 4-space..." Example good overriding: "Sorted-array approach too slow on traces we just profiled — lookups dominate. Switch index to hash map and drop ordering work." not "Now use hash map."',
    '   - dossier.md — privileged author notes opening with ONE-LINE LITMUS defended (from old skill, per step adapted): "A senior engineer who knows this domain cold still cannot produce correct output in one pass for this step — because recalled approach is WRONG not UNPARAMETERIZED, and in multi-turn loses carried context or fails to pivot." Then real root cause/design per step; cross-step design S1/S2/S3 per transition and why not decorative; load-bearing MECHANISM CHAIN not story; per step recall_resistance (coupling/second-order/decoy/opaque quirk + probing needed) + partial_failure_mode concrete >=1/5 frontier failure per step + cross-step; predicted per-model per-step PASS-RATES (weak tester + Avocado/Opus/GPT out of 5) written now — calibration expectation frontier passes >=1/5 and fails >=1/5 among reaching, Avocado reaches last, weak mostly fails; hidden-test plan with overfit-proof held-out disjoint values/asserts exact invariants across realistic inputs+runs agent actual artifact+keeps fixtures off /app+positive case naive shortcut breaks+balance labels no class >=60%; over-execution negatives drawn ONLY from identifiers later steps name (contamination trap never invent) + regression checks for steps modifying prior artifact; cascade plan how each step will hit >=1 pass >=1 fail denominators shrink coupling vs standalone failures; environment recipe ECR base pinned deps covering all steps planted state deterministic mtimes git history mapping file tracked then removed so working tree absent but log shows it + canary GUID fresh uuid4; task.toml skeleton schema 1.1 tags BEFORE steps [[steps]] names sync numeric prefix dirs only clean kebab task slug no numeric suffix dependencies inherit_prior_session true on 2+ min_reward 1.0 timeout 1800 no root verifier/agent; oracle-chain sketch per step runs on prior end state self-contained given declared outputs not solution internals. MUST NOT say "Auto-generated from template..." — describe specific CSV schemas/regexes/mapping file names/DB tables per step making THAT task unique. No fiction.',
    '   - environment.spec.md — Dockerfile recipe FROM ECR python:3.11-slim apt-get sqlite3 git bash MUST pip install pytest with deterministic mtimes for dedup tests git repo history containing mapping file etc ensure no DB/CLI at start, what every step needs, what planted, canary placeholder, allow_internet rationale.',
    '   - task.toml skeleton — schema 1.1 slug==dir name title family dynamic tags BEFORE steps at root or under [metadata] NOT after [[steps]] (old bug 0/100), include [environment] build_timeout, then [[steps]] blocks name dependencies inherit_prior_session min_reward timeouts, no root verifier/agent.',
    '   - .meta/handoff.json — { taskSlug, canaryGuid fresh uuid4, difficulty:"hard", category, dynamics, stepArtifacts: { "1": ["/app/..."] }, overExecMap: { "1": ["/app/report.json"] }, recall_resistance: { "1": "..."}, partial_failure_mode, mechanism }',
    '',
    '8. Do NOT WRITE per step solution/solve.sh and tests/ here — this skill stops before them (Phase1). Those are Codex Phase2 deliverables. Writing them here collapses split and reintroduces scaffold-oracle/skip-as-pass failure. If you were to write them, NEVER-CHEAT CONTRACT would apply: solve.sh real working oracle not stub TODO/FIXME/exit 1, prepend canary BENCHMARK DATA... + t-bench-canary GUID <fresh uuid4> chmod +x, tests/test.sh copy templates/test.sh verbatim (derives reward from junit so 0 collected/any skipped/error force 0), tests/test_outputs.py NEVER pytest.skip/mark.skip — must FAIL if artifact missing, >=1 positive per step + over-exec negatives from later identifiers + no always-true tails or assertion-free or slug compare or unresolved placeholders, never read/execute reference solve.sh, assert only paths instruction.md names or env creates, anti-gaming regex defined must be USED leading to sys.exit(1). But you do NOT write them now — spec them in dossier so Codex can build without guessing.',
    '9. Return structured object: usable, reason, title, slug, family, dynamic, confidence, n_steps, mechanism, recall_resistance, partial_failure_mode, predicted_rates, steps[] with name, goal_en, instruction_md, instruction_path, complexity_floor, recall_resistance, partial_failure per step, instruction_path dossier_path test_outline. Keep title/goal_en/dynamic/mechanism in English — feeds catalog. Per-step instruction_md English symptom-only. Be strict — better reject than ship weak, decorative, fiction-named, cloned, stub-oracle, or too-easy task that fails any of name-the-bug, fittability, layer-counts, scale/unit, differential bounded, difficulty-locus, wrong-not-unparameterized, mechanism duplicate, missing partial_failure.',
  ].join('\n')
}

const GATE_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    slug: { type: 'string' },
    clean: { type: 'boolean' },
    rounds: { type: 'number' },
    remaining_codes: { type: 'array', items: { type: 'string' } },
    fixed_summary: { type: 'string' },
  },
  required: ['slug', 'clean', 'rounds', 'remaining_codes', 'fixed_summary'],
}

function gatePrompt(slug) {
  const dir = outDir + '/' + slug
  return [
    'You are the GATE for one authored multi-turn T-Bench task. Your job is to make the fail-closed validator pass HONESTLY, or report that it does not.',
    'Task dir: ' + dir,
    '',
    'Loop, at most 4 rounds:',
    '  1. Run: python3 ' + SKILL_DIR + '/scripts/validate_task.py ' + dir,
    '  2. If it exits 0, stop - you are done.',
    '  3. Otherwise fix the CAUSE each blocking finding names, then go back to step 1.',
    '',
    'You may edit: steps/*/solution/, steps/*/tests/, environment/, task.toml, README.md, dossier.md.',
    'You may NOT edit any steps/*/instruction.md - record needed instruction changes in the dossier as recommendations instead.',
    '',
    'FORBIDDEN ways to make the validator pass - these are the cheat, not the fix:',
    '  - deleting a test, or the assertion inside it; adding pytest.skip/xfail; wrapping a failing check in try/except',
    '  - loosening an assertion to something unfalsifiable (>= 0, or True, "is not None" where the value matters)',
    '  - making reward.txt unconditional, or masking an exit code with || true',
    '  - writing a solve.sh that only echoes and exits so it stops looking like a stub - it must do the real work',
    '  - renaming or deleting a file purely to dodge a check',
    'If a finding cannot be fixed honestly in 4 rounds, return clean=false with the remaining codes. That is a good outcome; a dishonest pass is not.',
    '',
    'Return: slug, clean (validator exited 0), rounds used, remaining_codes (the blocking codes still open), fixed_summary (one line per real fix you made).',
  ].join('\n')
}

// Two candidates whose titles normalise to the same slug would be handed the SAME output dir,
// silently overwriting each other. Disambiguate with a word from the candidate rather than a
// numeric suffix (task dir slugs carry no numbers - only step dirs do).
const usedSlugs = {}
function slugify(s, c) {
  const base = String(s || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60).replace(/-+$/g, '')
  let slug = base || 'task'
  if (usedSlugs[slug]) {
    const extras = [c && c.lens, c && c.family, c && c.dynamic]
    for (let k = 0; k < extras.length; k++) {
      const suffix = String(extras[k] || '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
      if (suffix && !usedSlugs[slug + '-' + suffix]) { slug = slug + '-' + suffix; break }
    }
    while (usedSlugs[slug]) slug = slug + '-alt'
  }
  usedSlugs[slug] = true
  return slug
}

phase('Survey')
const surveyResults = await parallel(LENSES.map(function (l) {
  return function () {
    return agent(surveyPrompt(l), { label: 'survey:' + l.key, phase: 'Survey', schema: SURVEY_SCHEMA, model: SURVEY_MODEL })
      .then(function (r) {
        if (!r || !r.candidates) return []
        return r.candidates.map(function (c) { c.lens = l.key; return c })
      })
  }
}))

const allCands = surveyResults.filter(Boolean).reduce(function (a, b) { return a.concat(b) }, [])
const seen = {}
const unique = []
for (let i = 0; i < allCands.length; i++) {
  const c = allCands[i]
  const key = (c.family + '|' + c.title + '|' + c.area + '|' + c.symptom).toLowerCase().replace(/\s+/g, ' ')
  if (!seen[key]) { seen[key] = true; unique.push(c) }
}
log('Survey: ' + allCands.length + ' raw candidates, ' + unique.length + ' unique across ' + LENSES.length + ' lenses (dedup by family|title|area|symptom surface)')
log('Mechanism dedup (load-bearing chain not story) happens in Verify stage per tbench-task-authoring — shared mechanism different stories = duplicate, keep strictly-dominant')

let toVerify = unique
if (unique.length > MAX) {
  toVerify = unique.slice().sort(function (a, b) { return b.confidence - a.confidence }).slice(0, MAX)
  log('Capping to top ' + MAX + ' by confidence; dropping ' + (unique.length - MAX) + ' lower-confidence (raise maxCandidates for full coverage)')
}

phase('Verify+Author')
const piped = await pipeline(
  toVerify,
  function (c) {
    const slug = slugify(c.title, c)
    return agent(verifyPrompt(c, slug), { label: 'verify:' + slug, phase: 'Verify+Author', schema: VERIFY_SCHEMA, model: AUTHOR_MODEL })
      .then(function (v) { if (v) { v.lens = c.lens; v.slug = slug; v.dir = slug } return v })
  },
  function (v) {
    if (!v || !v.usable) return v
    return agent(gatePrompt(v.slug), { label: 'gate:' + v.slug, phase: 'Gate', schema: GATE_SCHEMA, model: AUTHOR_MODEL })
      .then(function (g) {
        v.gate = g || { slug: v.slug, clean: false, rounds: 0, remaining_codes: ['GATE_AGENT_DIED'], fixed_summary: '' }
        return v
      })
  }
)

const results = piped.filter(Boolean)
const authored = results.filter(function (r) { return r.usable })
const rejected = results.filter(function (r) { return !r.usable })
const gated = authored.filter(function (r) { return r.gate && r.gate.clean })
const blocked = authored.filter(function (r) { return !(r.gate && r.gate.clean) })
log('Authored ' + authored.length + '; gate clean ' + gated.length + ', gate blocked ' + blocked.length + '; rejected at authoring ' + rejected.length)
log('NEXT, before shipping: python3 <skill-dir>/scripts/check_catalog_uniqueness.py ' + outDir + ' --verbose   (clones + fiction names + per-task gates)')
log('And per task, the only proof that counts: python3 <skill-dir>/scripts/run_oracle_chain.py ' + outDir + '/<slug>   (docker: red before, green after, over-execution tripped)')
log('The static gate is necessary, not sufficient. No task in this catalog is "passing" until its oracle chain has actually run.')

return {
  seed: seed,
  outDir: outDir,
  counts: {
    raw: allCands.length, unique: unique.length, verified: results.length,
    authored: authored.length, gateClean: gated.length, gateBlocked: blocked.length, rejected: rejected.length,
  },
  proven: false,
  nextSteps: [
    'python3 <skill-dir>/scripts/check_catalog_uniqueness.py ' + outDir + ' --verbose',
    'python3 <skill-dir>/scripts/run_oracle_chain.py ' + outDir + '/<slug>   # per task, required',
  ],
  tasks: gated.map(function (r) {
    return {
      slug: r.slug, dir: r.dir || r.slug, title: r.title, family: r.family, confidence: r.confidence, lens: r.lens,
      dynamic: r.dynamic, n_steps: r.n_steps || (r.steps ? r.steps.length : 0),
      mechanism: r.mechanism,
      recall_resistance: r.recall_resistance,
      partial_failure_mode: r.partial_failure_mode,
      predicted_rates: r.predicted_rates,
      steps: (r.steps || []).map(function (s) { return { name: s.name, goal_en: s.goal_en, instruction_path: s.instruction_path, instruction_md: s.instruction_md, complexity_floor: s.complexity_floor, recall_resistance: s.recall_resistance, partial_failure: s.partial_failure } }),
      instruction_path: r.instruction_path, dossier_path: r.dossier_path, test_outline: r.test_outline,
      gate: r.gate,
    }
  }),
  gateBlocked: blocked.map(function (r) {
    return { slug: r.slug, title: r.title, remaining_codes: (r.gate && r.gate.remaining_codes) || ['UNKNOWN'], fixed_summary: (r.gate && r.gate.fixed_summary) || '', mechanism: r.mechanism, reason: r.reason }
  }),
  rejected: rejected.map(function (r) { return { title: r.title, family: r.family, reason: r.reason, mechanism: r.mechanism } }),
}
