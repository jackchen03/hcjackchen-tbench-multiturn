# Multi-turn template structure (from `codimango task init --type tbench-multi`)

Generated via:
```
codimango --site vanilla task init test-org/example-mt --type tbench-multi
```

```
example-mt/
├── task.toml  # schema_version = "1.1"
├── environment/Dockerfile
├── steps/
│   ├── 1_step_one/
│   │   ├── instruction.md
│   │   ├── solution/solve.sh
│   │   └── tests/{test.sh,test_outputs.py}
│   └── 2_step_two/ (same)
└── README.md
```

## task.toml skeleton (schema 1.1)

```toml
schema_version = "1.1"

[task]
name = "org/slug"
description = "..."
authors = []

[metadata]
difficulty = "hard"
category = "iterate_on_feature"
tags = ["iterate_on_feature"]  # BEFORE [[steps]], includes "multi-turn" + dynamic

[agent]
timeout_sec = 600.0  # should be 1800 for multi-turn

[environment]
build_timeout_sec = 600.0

[[steps]]
name = "1_step_one"
dependencies = []
min_reward = 1.0

[steps.verifier]
timeout_sec = 600.0

[steps.agent]
timeout_sec = 600.0

[[steps]]
name = "2_step_two"
dependencies = ["1_step_one"]
min_reward = 1.0
inherit_prior_session = true  # required on 2+

[steps.verifier]
timeout_sec = 600.0

[steps.agent]
timeout_sec = 600.0
```

## Phase1 handoff (MetaCode → Codex) vs Phase2

Phase1 (this repo before Codex) must NOT have solution/tests/Dockerfile yet:

```
<slug>/
├── task.toml              # skeleton 1.1
├── dossier.md             # privileged: litmus per step + S1/S2/S3 + mechanism + recall_resistance + partial_failure + predicted cascade + hidden-test + over-exec negatives ONLY from later identifiers + regression + env spec + canary GUID
├── environment.spec.md    # Dockerfile recipe FROM ECR, pip install pytest, pinned deps covering ALL steps
├── steps/
│   ├── 1_<name>/instruction.md   # FINAL English symptom-only
│   ├── 2_<name>/instruction.md
│   └── 3_<name>/instruction.md
└── .meta/handoff.json     # { taskSlug, canaryGuid uuid4, dynamics, stepArtifacts, overExecMap, mechanism }
```

Codex Phase2 then builds:

- environment/Dockerfile FROM public.ecr.aws/docker/library/python:3.11-slim, pip install pytest, deterministic mtimes, canary
- steps/<N>/solution/solve.sh (chmod +x, real oracle, not TODO)
- steps/<N>/tests/test.sh (copy templates/test.sh, derives reward from junit)
- steps/<N>/tests/test_outputs.py (NEVER pytest.skip, >=1 positive + over-exec negatives + regression, fixtures off /app)

## Anti-patterns

- tags after [[steps]] → scopes into last step (root tags 0)
- missing inherit_prior_session on 2+
- top-level instruction.md/solution/ leftovers → L8
- over-pinned context (step2 restates area/purpose/conventions) → kills following
- bare pivot (no motivation, no absence) → kills overriding
- pre-revealed future (step1 names later objectives/filenames) → destroys over-execution signal
- decorative chain (>=2 of 3 coupling signals no)
