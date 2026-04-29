import time
from collections import deque, defaultdict


class AnomalyDetector:
    def __init__(self, window_seconds=60):
        self.window_seconds = window_seconds
        self.global_window = deque()
        self.ip_windows = defaultdict(deque)
        self.ip_errors = defaultdict(deque)

    def record(self, ip, is_error=False):
        now = time.time()
        cutoff = now - self.window_seconds
        self.global_window.append(now)
        while self.global_window and self.global_window[0] < cutoff:
            self.global_window.popleft()
        self.ip_windows[ip].append(now)
        while self.ip_windows[ip] and self.ip_windows[ip][0] < cutoff:
            self.ip_windows[ip].popleft()
        self.ip_errors[ip].append((now, is_error))
        while self.ip_errors[ip] and self.ip_errors[ip][0][0] < cutoff:
            self.ip_errors[ip].popleft()
        global_rate = len(self.global_window) / self.window_seconds
        ip_rate = len(self.ip_windows[ip]) / self.window_seconds
        return global_rate, ip_rate

    def get_ip_error_rate(self, ip):
        if ip not in self.ip_errors:
            return 0.0
        errors = sum(1 for _, e in self.ip_errors[ip] if e)
        return errors / self.window_seconds

    def get_top_ips(self, n=10):
        now = time.time()
        cutoff = now - self.window_seconds
        counts = {}
        for ip, window in self.ip_windows.items():
            count = sum(1 for t in window if t >= cutoff)
            if count > 0:
                counts[ip] = count
        return sorted(counts.items(), key=lambda x: x[1], reverse=True)[:n]

    def is_anomalous_ip(self, ip, ip_rate, baseline, config):
        zscore = baseline.get_zscore(ip_rate)
        multiplier = ip_rate / max(baseline.effective_mean, 0.1)
        error_rate = self.get_ip_error_rate(ip)
        baseline_error = max(baseline.effective_mean * 0.1, 0.01)
        threshold_z = config['anomaly_zscore_threshold']
        threshold_m = config['anomaly_multiplier_threshold']
        if error_rate >= baseline_error * config['error_rate_multiplier']:
            threshold_z *= 0.7
            threshold_m *= 0.7
        return zscore > threshold_z or multiplier > threshold_m

    def is_anomalous_global(self, global_rate, baseline, config):
        zscore = baseline.get_zscore(global_rate)
        multiplier = global_rate / max(baseline.effective_mean, 0.1)
        return (zscore > config['anomaly_zscore_threshold'] or
                multiplier > config['anomaly_multiplier_threshold'])
