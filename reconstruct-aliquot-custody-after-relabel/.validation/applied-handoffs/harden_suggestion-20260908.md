# MetaCode instruction handoff

Status: **PENDING — MetaCode must edit the instruction; Codex must not.**

## Scope

- Edit only `steps/1_reconstruct-custody/instruction.md`.
- Current SHA-256: `0a478f2d6d4c9b4f70ac59aafa561b7abafc41db7f1d86c87ea0aea6c3e8d54b`.
- Do not change the task's semantics, add implementation guidance, or touch any other file.

## Requested wording-only change

Replace this sentence:

> Return the single custody graph supported by those rules, including cases with equal quantities and interchangeable positions; do not choose among multiple graphs by ordering or labels.

With this semantically equivalent wording:

> Return the single graph supported by those rules, including cases with equal quantities and interchangeable positions; ordering and labels are not tie-breakers.

## Why this is needed

The canonical multi-turn boundary classifier treats any sentence containing `do not` as a possible
successor prohibition, then uses token overlap with the next instruction. The old sentence contains
`custody`, which also appears in Step 2, so the classifier incorrectly requires Step 2 to make the
Step-1 grader fail. Step 2 is additive and explicitly preserves physical custody and taint conclusions;
all substantive Step-1 behavior should continue to pass after Step 2.

Evidence: `.validation/build-blocker.json` and `.validation/chain-20260908T154833Z.json`.

## Required follow-up after MetaCode edits

1. Verify the returned diff changes only the one sentence above.
2. Preserve this handoff and its checksum under `.validation/applied-handoffs/`, then remove the live task-root copy.
3. Record the authorized instruction transition and new instruction hash.
4. Regenerate static, full Docker-chain, valid-alternative, mutant, Oracle-x3, projection, hygiene, and build-closure evidence on one unchanged final fingerprint.
5. Do not commit or push the task unless the regenerated build closure passes.
