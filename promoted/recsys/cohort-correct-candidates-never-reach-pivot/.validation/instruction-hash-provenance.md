# Instruction hash provenance

The hashes in `instruction-sha256-before.txt` were captured by the pre-mutation `sha256sum steps/*/instruction.md` command at `2026-08-19T17:51:54Z`. The values were accidentally not persisted under `.validation/` until after the Docker chain. They exactly match the post-build snapshot and the instruction files have no Git diff. This note records the persistence-timing caveat rather than treating the later file timestamp as the capture time.
