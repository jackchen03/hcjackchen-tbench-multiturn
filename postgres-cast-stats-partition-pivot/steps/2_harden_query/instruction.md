That helped, but the same query still falls over on a few customer ids: a handful of
ids own a large share of the rows, and on those skewed ids the plan reads most of
the table even without a sequential scan. Harden it so the bad ids stay fast too,
keeping the same results and the same rules from /app/bounds.txt on every tested id:
no sequential scan on orders, buffer sums under the staged budget number, exact rows.
Settings-only changes that leave buffer use unchanged are not a fix.
