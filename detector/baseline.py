import time
import math
from collections import deque


class BaselineTracker:
    def __init__(self, window_minutes=30, recalc_interval=60):
        self.window_seconds = window_minutes * 60
        self.recalc_interval = recalc_interval
        self.counts = deque()
        self.hourly_slots = {}
        self.effective_mean = 1.0
        self.effective_stddev = 1.0
        self.last_recalc = time.time()
        self.last_second = int(time.time())
        self.current_second_count = 0

    def record_request(self):
        now = int(time.time())
        if now == self.last_second:
            self.current_second_count += 1
        else:
            self._store_count(self.last_second, self.current_second_count)
            self.current_second_count = 1
            self.last_second = now
        if time.time() - self.last_recalc >= self.recalc_interval:
            self._recalculate()

    def _store_count(self, timestamp, count):
        self.counts.append((timestamp, count))
        cutoff = timestamp - self.window_seconds
        while self.counts and self.counts[0][0] < cutoff:
            self.counts.popleft()
        hour = timestamp // 3600
        if hour not in self.hourly_slots:
            self.hourly_slots[hour] = []
        self.hourly_slots[hour].append(count)
        old_hours = [h for h in self.hourly_slots if h < hour - 2]
        for h in old_hours:
            del self.hourly_slots[h]

    def _recalculate(self):
        self.last_recalc = time.time()
        current_hour = int(time.time()) // 3600
        if current_hour in self.hourly_slots and len(self.hourly_slots[current_hour]) >= 60:
            samples = self.hourly_slots[current_hour]
        else:
            samples = [c for _, c in self.counts]
        if len(samples) < 10:
            return
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        stddev = math.sqrt(variance)
        self.effective_mean = max(mean, 0.1)
        self.effective_stddev = max(stddev, 0.1)
        from audit import write_audit
        write_audit(
            "BASELINE_RECALC", ip="global",
            condition=f"samples={len(samples)}",
            rate=0, baseline=self.effective_mean, duration=0
        )

    def get_zscore(self, rate):
        return (rate - self.effective_mean) / self.effective_stddev
