Profiling the production traces after your fix shows the worker-pool plus reorder-buffer approach still adds tail latency on the critical path and leaves a risk window where someone could reintroduce worker-stamped timing. Latency budget requires simplifying this path.

Switch the gateway to single-threaded sequential ingestion that assigns a monotonic ingress sequence number directly in the reader loop before any dispatch and processes events strictly in that ingress order, filling resting orders in arrival order. This should preserve the same price-time priority and determinism guarantees from before, but without concurrency.

Final /app/gateway.py must NOT import or use threading, queue, concurrent.futures.ThreadPoolExecutor, and must NOT contain ts_ms stamping via time.time(), worker-stamped seq counter, or (ts_ms, oid) / (ts, oid) sort tie-break to oid. Remove the old worker-pool and timestamp-based ordering path entirely — relying on ingress gseq only. Keep the same CLI python3 /app/gateway.py <feed_file> <output_file> and same JSON array of {"taker","maker","price","qty"} output.

Also write /app/PERF_NOTE.md with one paragraph explaining why the pool was removed and how ingress sequencing replaces it.
