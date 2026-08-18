# Single-turn → Multi-turn Promotion

Promoting tasks from `hcjackchen-tbench-1/Ideas/` (74 ideas) to multi-turn handoff.

## Input

Single-turn catalog (old skill `tbench-task-authoring`):
```
<inputDir>/   e.g. /home/hcjackchen/hcjackchen-tbench-1/Ideas/tbench-database-internals-tasks/
├── INDEX.md
├── REJECTED.md
└── <slug>/
    ├── instruction.md   (Chinese symptom-only, literal tokens verbatim untranslated)
    └── dossier.md       (litmus, diagnosis, why discriminates >=2 fails, recall_resistance, partial_failure_mode, predicted rates, hidden test outline held-out, env recipe ECR pinned, oracle sketch, mechanism chain)
```

## Output — Phase1 handoff (for Codex)

```
<outDir>/<new-slug>/
├── task.toml              # schema 1.1, tags BEFORE [[steps]], 2-3 steps, inherit_prior_session true on 2+, min_reward 1.0, timeout 1800
├── dossier.md             # per-step litmus + diagnosis + S1/S2/S3 + mechanism + recall_resistance per step + partial_failure per step+cross + predicted cascade + hidden-test held-out + over-exec negatives from later identifiers ONLY + regression + env spec ECR + canary GUID
├── environment.spec.md    # Dockerfile recipe FROM ECR pytest pinned covering ALL steps, deterministic mtimes, git history if needed, planted state, allow_internet rationale
├── steps/
│   ├── 1_<name>/instruction.md   # FINAL English symptom-only, literal tokens verbatim
│   ├── 2_<name>/instruction.md   # terse follow-up relying on carried context
│   └── 3_<name>/instruction.md   # overriding legible motivated with absence assertion
└── .meta/handoff.json
```

## Promotion patterns

- split-internal-chain (following): old internal chain detect→localize→rebuild→resolve split into carried steps
- extend-then-pivot (overriding, PREFERRED, 3 steps): step1 original core, step2 extends relying on unrepeated carry, step3 profile says slow → switch data structure + drop old + absence

Example: LOB recovery across 3 artifacts:
- step1 recover using chain dir alone (will be WRONG, foreign chunk passes checksum — must probe generation mismatch via alloc.map)
- step2 now add allocation-map generation check to detect reuse (following, area/file not re-pinned, relies on step1's recovered shape but adds detection)
- step3 new evidence: undo log holds multiple before-images per slot — need generation-keyed splice at len_before, old owner-only splice must be removed (overriding + absence, motivation: header owner unreliable because copy-forward decoy)

This chain is non-decorative because S1: step2 oracle uses step1 output + new artifact, S2: step2 doesn't restate chain dir area, S3: test verifies adaptation to specific prior output's generation.

## Workflow

```js
Workflow({
  scriptPath: "scripts/single-to-multiturn-promotion.workflow.js", // from tbench-single-to-multiturn skill
  args: { inputDir: "/home/hcjackchen/hcjackchen-tbench-1/Ideas/tbench-database-internals-tasks", outDir: "/home/hcjackchen/hcjackchen-tbench-multiturn/promoted/database-internals", maxPromotions: 5, skillDir: "~/.opencode/skills/tbench-single-to-multiturn", difficulty: "hard" }
})
```

Then gate:

```
python3 scripts/check_catalog_uniqueness.py promoted/database-internals --verbose
python3 scripts/build_catalog.py <workflow-output.json> promoted/database-internals
```

Per task later (Codex Phase2):

```
python3 scripts/run_oracle_chain.py promoted/database-internals/<slug>  # DO-NOTHING FAIL, ORACLE 1.0, GREEN >0 executed 0 skipped, OVER-EXEC trip
```

## The 5 current Idea families not yet in Codimango

- tbench-database-internals-tasks: 25
- tbench-filesystem-internals-tasks: 15
- tbench-recsys-tasks: 15
- tbench-robotics-3d-recon-tasks: 9
- tbench-trading-catalog: 10

Pick 5 representative slugs for initial multi-turn batch, one per family, favor richest coupling.

Suggested picks for hard multi-turn:
1. byte-exact-lob-recovery-across-three-artifacts-o-14 (3 artifacts coupling + decoy header owner copy-forward + generation-keyed undo)
2. byte-exact-file-reconstruction-from-a-carved-ext-10 (depth-2 extent tree + eh_entries vs eh_max decoy + unwritten extent zeros + shuffled manifest)
3. hnsw-index-returns-deleted-items-and-misses-live-2 (half-applied per-node gen-gated remap + free-list stale + entry_point)
4. ba-converges-but-recovered-structure-fails-a-whi-2 (BA converges but structure fails white-box test — likely reprojection + scale trap)
5. l3-l2-rebuild-replace-reprice-vs-double-counted--24 (order book rebuild complexity)

These all have natural split→extend→pivot boundaries.
