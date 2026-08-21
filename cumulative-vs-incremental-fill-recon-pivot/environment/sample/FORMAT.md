# Drop-copy format

Run `python3 /app/reconcile.py <dropcopy_file> <output_json>`.

Input is one pipe- or SOH-delimited FIX ExecutionReport per line. The output is a sorted JSON object mapping each symbol to an integer net share position; buys are positive and sells negative.
