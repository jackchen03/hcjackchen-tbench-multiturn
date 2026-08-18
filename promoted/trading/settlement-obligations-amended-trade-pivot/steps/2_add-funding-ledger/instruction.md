That fixed the per-bucket settlement splits. Finance now needs a funding view building on the settlement book you just fixed.

Implement /app/funding_report.py that consumes the settlement CSV you produce and emits a funding aggregation.

CLI: `python3 /app/funding_report.py <settlement_csv> <funding_csv>` where <settlement_csv> is a file produced by `python3 /app/settle.py <messages> <settlement_csv>` with header `counterparty,currency,value_date,net_amount`, and <funding_csv> is the output to create.

Output contract: CSV with first row header `currency,value_date,total_net_amount`, then one row per (currency, value_date) aggregated across counterparties (sum of net_amount from settlement per currency per value_date). total_net_amount as integer micros, may be negative/zero? Only output rows where total_net_amount != 0, sorted by currency, value_date ascending.

Do not re-implement settlement netting inside funding_report.py — read the settlement CSV. More steps may follow; conserve resources.
