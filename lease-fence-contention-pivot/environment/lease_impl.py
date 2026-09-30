"""Intentionally unsafe starter lease used by both public diagnostics."""
import json
import threading


class LeaseStore:
    def __init__(self, root="."):
        self.root = root
        self._lock = threading.Lock()
        self._fence = 0
        self._hwm = -1
        self._log = []

    def grant(self):
        with self._lock:
            self._fence += 1
            return self._fence

    def commit(self, tok, op, val):
        with self._lock:
            if tok != self._fence or op <= self._hwm:
                return False
            self._hwm = op
            self._log.append(json.dumps({"op": op, "tok": tok, "val": val}))
            return True

    def acquire_stripe(self, stripe):
        raise NotImplementedError("striping belongs to step 2")

    def commit_striped(self, stripe, tok, op, val):
        raise NotImplementedError("striping belongs to step 2")
