# hcjackchen-tbench-multiturn catalog

`proof` is what oracle chain actually did in Docker. `unproven` = `run_oracle_chain.py` not yet run — draft, not validated.

## Usable tasks

| # | family | dynamic | steps | title | conf | proof | dir |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Workflow

```js
Workflow({
  scriptPath: "~/.opencode/skills/tbench-task-authoring-multiturn-ideation/scripts/bulk-discovery.workflow.js",
  args: { seed: "your_repo_or_domain", outDir: "/home/hcjackchen/hcjackchen-tbench-multiturn", maxCandidates: 16, skillDir: "~/.opencode/skills/tbench-task-authoring-multiturn-ideation", difficulty: "hard" }
})
```

Or promotion from single-turn:

```js
Workflow({
  scriptPath: "~/.opencode/skills/tbench-single-to-multiturn/scripts/single-to-multiturn-promotion.workflow.js",
  args: { inputDir: "/home/hcjackchen/hcjackchen-tbench-1/Ideas/tbench-database-internals-tasks", outDir: "/home/hcjackchen/hcjackchen-tbench-multiturn/promoted", maxPromotions: 5, skillDir: "~/.opencode/skills/tbench-single-to-multiturn", difficulty: "hard" }
})
```
