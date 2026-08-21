The garbage-symbol issue is still happening, but only for messages that carry a different data field than the one you fixed. The previous fix handled `RawData` but the feed also contains `SecureData` and other length-prefixed fields whose payload can include embedded SOH bytes like `55=FAKE` that overwrite the real symbol — so we get a bogus quote under a garbage symbol and the real symbol disappears.

The container ships a small FIX data dictionary at `/app/data/fix_data_fields.txt` listing the Length→Data tag pairs the exchange uses (e.g., `90 91`, `95 96`, `212 213`, `354 355`). Make the parser handle the whole family from that dictionary, not just the one field visible in the first sample. A fix that special-cases only `96` will still fail the evaluation capture.

The output is still `/app/out/quotes.csv` as before — keep the same entry point — but now it must include those messages too, with correct symbols and no rows under garbage symbols.
