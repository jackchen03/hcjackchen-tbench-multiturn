# Packed Bytecode Origin Ledger

This two-step task carries one compiler/runtime checkout forward. Step 1 repairs
semantic ownership after variable-width layout. Step 2 extends that repaired
state through mandatory opcode fusion while retaining ordered duplicate phases,
phase-local handlers and roots, and complete size accounting.

| Evaluation | Step 1 | Step 2 | Whole chain |
| --- | --- | --- | --- |
| Oracle | unmeasured | unmeasured | unmeasured |
| Avocado | unmeasured | unmeasured | unmeasured |
| Other models | unmeasured | unmeasured | unmeasured |

Local build evidence demonstrates only the reference chain and grader controls;
it does not measure model completion or difficulty.
