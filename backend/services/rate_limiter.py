import time
import os
import json
import fcntl

RATE_LIMIT_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "rate_limits.json"
)
os.makedirs(os.path.dirname(RATE_LIMIT_FILE), exist_ok=True)


class RateLimiter:
    def __init__(self, max_requests=10, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(RATE_LIMIT_FILE):
            with open(RATE_LIMIT_FILE, "w") as f:
                json.dump({}, f)

    def _read(self):
        with open(RATE_LIMIT_FILE, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def _write(self, data):
        with open(RATE_LIMIT_FILE, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                json.dump(data, f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def is_allowed(self, client_id):
        now = time.time()
        cutoff = now - self.window_seconds

        data = self._read()
        if client_id not in data:
            data[client_id] = []

        data[client_id] = [t for t in data[client_id] if t > cutoff]

        if len(data[client_id]) >= self.max_requests:
            self._write(data)
            return False

        data[client_id].append(now)
        self._write(data)
        return True

    def remaining(self, client_id):
        now = time.time()
        cutoff = now - self.window_seconds
        data = self._read()
        active = len([t for t in data.get(client_id, []) if t > cutoff])
        return max(0, self.max_requests - active)

    def reset_time(self, client_id):
        now = time.time()
        cutoff = now - self.window_seconds
        data = self._read()
        active = [t for t in data.get(client_id, []) if t > cutoff]
        if active:
            return max(0, active[0] + self.window_seconds - now)
        return 0
