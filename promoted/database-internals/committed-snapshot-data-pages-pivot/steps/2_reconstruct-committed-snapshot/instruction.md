Diagnosis identified dirty rows, but finance still needs the correct report.

Now build `/app/reconstruct` with usage `/app/reconstruct <data_dir> <output_file>`.

It must compute the last truly committed state for every account, using the same decoding you built for the prior step. For each account's latest on-page record, if its transaction is not committed according to `rseg.bin`, follow its `roll_ptr` into `undo.bin`, reading prior versions, and keep walking until you find a version whose `trx_id` is COMMITTED — this may need more than one hop when the immediate predecessor is also from an aborted/active transaction. If the chain ends with no committed version (for example the account was created only by an aborted INSERT), omit that account entirely.

Output: each line `<account_id> <balance>`, both decimal integers, balance in cents as stored, one space separator, all lines sorted by `account_id` ascending ascending, no extra content. If an account does not exist in the committed snapshot, do not emit it.

Do not trust the info hint bit rendered by `/app/inspect.py`. Handle held-out data with disjoint ids and values.
