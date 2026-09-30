# Transition evidence

Bundle fingerprint: `bundle-sha256-v1:cf8cc00ca1864ebccfb89785f318c5fc89fb37ce426d3d9fb24ade1fa6beeb92`

## 1 → 2

- Entry state: damaged read-only `disk.img`.
- Carried outputs: `fat_decision.txt`, `repair.sh`, and the mutable `repaired.img`.
- Mutation: Step 2 restores the two directory entries and damaged high word in `repaired.img`; FAT bytes remain unchanged and identical.
- Regression: Step-2 grading rechecks the decision, executable repair CLI, and FAT equality.
- Under-execution: without Step 1 there is no repaired primary FAT to walk; Step-2 do-nothing is red.
- Future isolation: no manifest or carve script is pre-staged.
- Over-execution: `NOT_REQUIRED`; Step 1 does not forbid compatible recovery artifacts.

## 2 → 3

- Entry state: repaired and undeleted image plus exact manifest.
- Carried outputs: `repaired.img`, `files_manifest.json`, `repair.sh`, and `carve.sh`.
- Mutation: Step 3 is read-only over image/manifest and adds `verify.sh` plus `outcome.txt`.
- Regression: Step-3 grading independently rechecks manifest schema, chain hashes, and carried scripts.
- Under-execution: without restored entries/manifest, row and hash closure cannot be computed; Step-3 do-nothing is red.
- Future isolation: no outcome or verify script is pre-staged.
- Over-execution: `NOT_REQUIRED`; Step 2 says the choice is settled but does not forbid re-derivation or compatible verification. A compatible early outcome file is explicitly accepted by the shipped Step-2 grader.
