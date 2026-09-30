# lease-fence-contention-pivot

Two-turn debugging task: first make fencing and high-water state durable across reopen, then retain that contract while introducing at least sixteen independently progressing stripes and explicitly retiring global order.

The verifier checks exact binary state, log shape, stale/replay rejection, the Step-1 over-execution boundary, signed carry binding, per-stripe durability, behavioral lock independence, and the carried global API. `difficultyProof` remains `pending_phase2` until trajectory evidence exists.
