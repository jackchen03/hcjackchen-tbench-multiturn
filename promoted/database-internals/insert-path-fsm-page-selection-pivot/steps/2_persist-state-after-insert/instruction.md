# Persist updated state after insert path

Your previous `/app/heapload` now byte-matches `/verifier/heapload` for arbitrary batches — it reproduces the FSM dialect exactly.

The insertion service now needs per-batch persisted relation state for the next batch. You already have the area and conventions from your previous binary and state format — don't re-derive container layout from scratch.

Usage changes to `/app/heapload <state_file> <new_state_file>`: first arg is the input state file (same format as before with `USABLE`, `SLOT`, `CURSOR`, page count and `<pid> <true_free>` lines), second arg is a path where you must write updated state after applying the batch. The second arg path `<new_state_file>` is provided by the caller; you must create it.

The updated state format is identical to input: `USABLE` unchanged, `SLOT` unchanged, `CURSOR` set to last landing page id after batch, number of pages updated for any extends, then each page id with its new `true_free` after subtracting placed tuple sizes (new pages have `true_free = USABLE - size`). The batch still comes from stdin, and stdout must still be the landing page ids one per line, byte-exact versus `/verifier/heapload` on the same input state.

Keep `/app/heapload` at the same path and keep the exact same FSM selection logic you already discovered. The new state file must be computed from the actual selection you produced, not just from input counts — if your selection differs, free-space decrements and extension count will differ and the persisted file will be wrong.

Samples for this step are under `/app/samples/` with golden `<new_state_file>` examples for some state/batch pairs. Use them to validate your second-arg writing before probing unseen cases.
