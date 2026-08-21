That fixed net positions and matches the sample and holdout.

Compliance now needs a detailed audit trail of every true incremental fill that contributed to those positions — same dedup rules and same carry/reset handling you just implemented, no re-explanation.

Create a new tool at `/app/ledger.py` that runs as `python3 /app/ledger.py <dropcopy_file> <ledger_output_path>`.

It must read the same drop-copy format and emit a JSON array at the output path, ordered by appearance in the drop-copy after dedup, each element containing exactly the keys `symbol`, `venue`, `side`, `qty`, `exec_id`, `clordid`, `root_id`:

- `symbol` is tag 55
- `venue` is SenderCompID tag 49
- `side` is tag 54 value "1" or "2"
- `qty` is the true incremental fill quantity (int, >0) after your per-order baseline and LastQty-else-delta logic
- `exec_id` is tag 17
- `clordid` is tag 11
- `root_id` is the transitive root ClOrdID of the chain traced via OrigClOrdID (tag 41)

Sums per symbol from this ledger must tie to the net positions from step1. Continue to handle PossDup (tag 43=Y) and LastQty omitted cases correctly. More steps may follow.