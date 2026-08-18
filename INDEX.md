# hcjackchen-tbench-multiturn catalog

`proof` is what the oracle chain actually did in Docker, not an opinion. `unproven` means `run_oracle_chain.py` has not been run on that task yet — those tasks are drafts, not validated tasks.

## Usable tasks

| # | family | dynamic | steps | title | conf | proof | dir |
|---|---|---|---|---|---|---|---|
| 1 | database-internals | both | 3 | Byte-exact LOB recovery: chain to generation-pivot to undo splice | 0.92 | unproven | `promoted/database-internals/byte-exact-lob-recovery-chain-generation-pivot/` |
| 2 | filesystem-internals | both | 3 | Carved ext4 extent tree unwritten pivot | 0.90 | unproven | `promoted/filesystem-internals/carved-ext4-extent-tree-unwritten-pivot/` |
| 3 | recsys | both | 3 | HNSW interrupted compaction gen-gated pivot | 0.88 | unproven | `promoted/recsys/hnsw-interrupted-compaction-gen-gated-pivot/` |
| 4 | robotics-3d | both | 3 | Bundle adjustment converges structure drift pivot | 0.87 | unproven | `promoted/robotics-3d/bundle-adjustment-converges-structure-drift-pivot/` |
| 5 | trading | both | 3 | L3 L2 orderbook replace reprice dedup pivot | 0.89 | unproven | `promoted/trading/l3-l2-orderbook-replace-reprice-dedup-pivot/` |

## Family breakdown

- database-internals: 25 single-turn ideas available, 1 promoted (overriding+following 3-step: chain-only → generation detection → generation-keyed undo splice with owner decoy)
- filesystem-internals: 15 ideas, 1 promoted (shuffled block_map → unwritten zeros + eh_entries vs eh_max decoy → EOF truncation)
- recsys: 15 ideas, 1 promoted (uniform remap double-remap → gen-gated remap → free-list trim)
- robotics-3d: 9 ideas, 1 promoted (whiten Jacobian weighting → fix LM gain ratio → unify weighted path removing raw helpers)
- trading: 10 ideas, 1 promoted (L2 rebuild double-count → REPLACE dedup → REPRICE in-place preserving time priority with fencing)

Total single-turn Ideas available: 74 (5 families)

## Promotion method

```js
Workflow({
  scriptPath: "~/.opencode/skills/tbench-single-to-multiturn/scripts/single-to-multiturn-promotion.workflow.js",
  args: {
    inputDir: "/home/hcjackchen/hcjackchen-tbench-1/Ideas/tbench-database-internals-tasks",
    outDir: "/home/hcjackchen/hcjackchen-tbench-multiturn/promoted/database-internals",
    maxPromotions: 5,
    skillDir: "~/.opencode/skills/tbench-single-to-multiturn",
    difficulty: "hard"
  }
})
```

Then per family:

```
python3 scripts/check_catalog_uniqueness.py promoted/<family> --verbose   # OK 1/1
python3 scripts/check_catalog_uniqueness.py /tmp/flat-catalog --verbose   # OK 5/5, 0 clones
```

Per task later (Codex Phase2):

```
python3 <skill-dir>/scripts/run_oracle_chain.py promoted/<family>/<slug>  # DO-NOTHING FAIL, ORACLE 1.0 chain, GREEN >0 executed 0 skipped, OVER-EXEC trip
```

## Multi-turn bar enforced

- Per-step complexity floor: multi-step non-linear + empirical discriminator (bytes od -c, hexdump, EXPLAIN, traced interleaving, forward-pass diff, aggregate vs ground truth) + obvious fails >=2
- 5-gate kill per step: name-the-bug, public-algorithm+fittability, wrong-answer WRONG not unparameterized, difficulty-locus concept not grader, provenance
- Sharp screens: layer-counts (fix-first-only stays RED), scale/unit weak needs byte/state + second assertion, differential bounded reachable, fittability leak structural vs scalar
- 3-signal non-decorative: S1 oracle coupling uses prior output, S2 instruction avoids restating prior context, S3 tests verify adaptation to specific prior output
- Over-execution guardable: negatives from later identifiers ONLY (contamination trap)
- Mechanism dedup by load-bearing chain not story
- Bias overriding + 3 steps (pool skewed following+2, only 2/31 alpha used overriding)
