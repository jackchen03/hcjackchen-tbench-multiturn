# Handoff to Codex — Phase2 Builder

Consume `<outDir>/<slug>/` — treat every `steps/*/instruction.md` as READ-ONLY (English symptom-only, literal tokens verbatim), derive hidden tests only from identifiers those files name + `dossier.md`'s plan (held-out disjoint values per step, positives+negatives+regression, over-exec negatives from later identifiers ONLY, behavior-based not substring grep), and follow `tbench-task-authoring-multiturn-builder` steps 7-8 to produce gradeable bundle + validation evidence. Must satisfy: DO-NOTHING OK per step (tests FAIL before solve), ORACLE OK 1.0 chain end-to-end, GREEN OK >0 executed 0 skipped per step, OVER-EXEC OK negatives trip when doing next step early. Copy canary GUID from handoff to final Dockerfile + each solve.sh + test.sh/test_outputs.py. FROM ECR `public.ecr.aws/docker/library/...`, pip install pytest pinned deps covering all steps. Per-step agent timeout 1800. No root [verifier]/[agent].

Builder skill: `tbench-task-authoring-multiturn-builder` with gate table.

Per task validation:

```
python3 scripts/run_oracle_chain.py promoted/<family>/<slug>  # DO-NOTHING FAIL before, ORACLE 1.0 chain, GREEN >0 executed 0 skipped, OVER-EXEC trip
python3 scripts/check_catalog_uniqueness.py promoted --verbose
python3 scripts/build_catalog.py <workflow-output.json>
```
