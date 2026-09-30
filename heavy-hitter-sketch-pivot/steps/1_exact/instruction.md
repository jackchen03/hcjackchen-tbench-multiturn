The sample stream in /app/stream_sample.txt is too large for eyeballing: naive top-k helpers disagree on order and counts.

Implement exact_topk(lines, k=10) in /app/topk.py taking an iterable of stripped lines and returning the top k keys as a list of [key, count] pairs with exact counts, tie-broken by count descending then key ascending. Your implementation must satisfy `python3 /app/check_exact.py --sample /app/stream_sample.txt --k 10`.

Only /app/topk.py behavior on held-out streams is checked.
