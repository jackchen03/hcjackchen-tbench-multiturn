# historical-var-underreports-pivot

This three-step chain keeps one `/app/var_report.py` artifact throughout. Step 1 corrects the sample's discrete tail selection while retaining the shared-calendar-only positional assembly. Step 2 carries that quantile behavior forward and aligns per-asset returns by date. Step 3 overrides the slow row-wise repricing path with one vectorized matrix multiplication while rechecking both prior result families.

The chain is load-bearing: step 2 first runs the step-1 artifact and preserves its discrete quantile; step 3 first runs the step-2 artifact and preserves both shared and staggered results. Boundary probes are behavioral: step 1 must still disagree on the later staggered fixture, and step 2 must still exceed the short production probe until the vectorized pivot is applied.

| Agent | Step 1 | Step 2 | Step 3 | Result |
|---|---|---|---|---|
| Nop | unmeasured | unmeasured | unmeasured | unmeasured |
| Oracle | unmeasured | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured | unmeasured |
| Opus | unmeasured | unmeasured | unmeasured | unmeasured |
| GPT | unmeasured | unmeasured | unmeasured | unmeasured |

Local chain evidence, oracle stability, model completion, and cloud validation remain unmeasured until their corresponding artifacts exist.
