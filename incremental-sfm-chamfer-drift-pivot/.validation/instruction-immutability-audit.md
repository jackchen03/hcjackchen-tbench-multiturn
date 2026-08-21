# Instruction immutability audit

The three instruction hashes were printed in a read-only command before bundle edits:

```
8c3fd182ac0b6ec0a391710360924bfebe09e4ec900ae9edc9b1f968d5be8300  steps/1_diagnose-and-fix-chamfer-drift/instruction.md
957a1afb31dc5486906d55a8999ceb0a9d2a82df4b834737e63e1995e6b3a869  steps/2_add-track-quality-report/instruction.md
e9efc547ed9c241f652527ca7d96f58ebd9389864a87e0c31de66c45d1ba8039  steps/3_pivot-to-ply-and-optimize-track-merge/instruction.md
```

The final hashes match these values and Git shows no instruction diff. However, the required
`.validation/instruction-sha256-before.txt` file was not written before bundle editing began.
Under the fail-closed builder contract, filesystem-snapshot immutability is therefore unproven.
