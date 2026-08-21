# Historical VaR report interface

Run `python3 /app/var_report.py <price_history_csv> <positions_csv> <output_path>`.

The prices file is a wide CSV whose first column is `date`; remaining columns are assets and blank cells mean that asset had no observation that day. The positions file has `asset,position` columns. The output is JSON containing one positive numeric field named `var_99`.
