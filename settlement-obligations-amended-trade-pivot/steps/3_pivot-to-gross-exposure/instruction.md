We profiled intraday liquidity — 2M messages, 10K amended chains, lookups dominate settlement aggregation. Risk says net settlement obligations masks liquidity risk: trades that net to zero still require gross cash movement. The net settlement obligations view you built in /app/settle.py is no longer sufficient, and the intermediate funding report at /app/funding_report.py that summed net per currency is deprecated.

Switch to gross exposure reporting and drop the net-only approaches. This is the pivot away from netting to gross — the final settlement obligations pivot.

Implement /app/gross_exposure.py:

CLI: `python3 /app/gross_exposure.py <messages_file> <exposure_csv>` where <messages_file> is same JSONL format as before (NEW/AMEND/CANCEL, trade_id, counterparty, trade_date, bought_ccy, bought_amount, sold_ccy, sold_amount, with calendars in /app/calendars/).

Output contract: CSV with first row header `counterparty,currency,value_date,gross_pay,gross_receive,net_amount`, then one row per (counterparty, currency, value_date) bucket. For each surviving terminal trade (after collapsing AMEND to last state and dropping CANCEL), its value_date is computed same spot rule as before (T+2 with calendars). For that trade, increment gross_pay by sold_amount in sold_ccy bucket and gross_receive by bought_amount in bought_ccy bucket (both stored as positive integers micros). Aggregate across trades per bucket. net_amount = gross_receive - gross_pay (same semantics as before, receive positive). Only output rows where net_amount != 0 or gross_pay !=0 or gross_receive !=0? But keep contract simple: only output rows where gross_pay !=0 or gross_receive !=0, sorted by counterparty, currency, value_date ascending. value_date as YYYY-MM-DD.

Absence assertions:
- The old net-only settlement file previously written at /app/output/settlement.csv must no longer be produced by this step — remove or do not invoke code that writes it; risk pipeline now runs only /app/gross_exposure.py.
- Implementation of /app/gross_exposure.py must NOT rely solely on net aggregation collapsing buys and sells into one sum before reporting gross — gross_pay and gross_receive must be tracked separately; tests will assert gross_pay and gross_receive columns correct, not just net.

You must still compute value_date correctly with the USD holiday gate from before; that logic carries over. Do not re-state settlement netting details beyond what is needed for gross.
