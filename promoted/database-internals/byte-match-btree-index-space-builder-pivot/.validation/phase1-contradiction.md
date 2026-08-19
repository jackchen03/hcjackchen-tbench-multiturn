# Phase-1 future-artifact contradiction

Phase 2 stopped before bundle implementation because Step 2 requires a deletion artifact before deletion exists in the task contract.

Step 2's final line says: `The output for this step must include /app/deletes.txt.` However:

- Step 2 is only the space-accounting extension; its specified solver outputs are `/app/btbuild` and `/app/btbuild.meta`.
- The environment does not define `/app/deletes.txt` as a planted file or a Step-2 output.
- Step 3 is the first instruction that introduces deletion input, and it defines an arbitrary `<deletes_file>` command-line argument rather than the fixed path `/app/deletes.txt`.
- The handoff's Step-2 artifact list excludes `/app/deletes.txt`, while the intended Step-2-to-Step-3 boundary guards later deletion work with a separate Step-3 report.

Requiring the agent to invent `/app/deletes.txt` in Step 2 pre-executes and pre-reveals the next workload, but there is no specified content for it. Omitting it violates the literal Step-2 instruction. Even if created empty, Step 3 grading passes held-out deletion files by argument, so the fixed artifact has no defined role.

Phase 1 must remove this line from Step 2 or define the file's exact contents, ownership, and role while redesigning the future boundary.
