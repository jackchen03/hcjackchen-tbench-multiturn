That fixed the big splits, but some books still diverge.

Look at events where a tiny resting order exists — the reference shows `filled_qty` 0 for that order and its lot appears on larger orders, while your current matcher gives it 1. It's not a rounding error — a minimum fill rule is involved.

The blotter indicates any allocation that would be in the open interval `(0, MIN_FILL)` with `MIN_FILL=2` gets dropped to 0 and its quantity is re-pooled to survivors, iteratively. Extend your matcher from the previous step to handle this.

Don't re-explain allocation — build on the same `/app/matcher.py` you already fixed.

There are more steps after, keep the change minimal.
