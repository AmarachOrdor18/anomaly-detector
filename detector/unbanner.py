import time
import threading
from blocker import unban_ip


class Unbanner:
    def __init__(self, notifier):
        self.notifier = notifier
        self.banned = {}
        self.lock = threading.Lock()
        self.schedule = [600, 1800, 7200, -1]

    def add_ban(self, ip):
        with self.lock:
            if ip not in self.banned:
                self.banned[ip] = {"ban_count": 0, "unban_time": None}
            count = self.banned[ip]["ban_count"]
            duration = self.schedule[min(count, len(self.schedule) - 1)]
            if duration == -1:
                self.banned[ip]["unban_time"] = None
            else:
                self.banned[ip]["unban_time"] = time.time() + duration
            self.banned[ip]["ban_count"] += 1
            return duration

    def is_banned(self, ip):
        with self.lock:
            return ip in self.banned

    def run(self):
        while True:
            now = time.time()
            to_unban = []
            with self.lock:
                for ip, info in self.banned.items():
                    if info["unban_time"] and now >= info["unban_time"]:
                        to_unban.append(ip)
            for ip in to_unban:
                unban_ip(ip, self.notifier)
                with self.lock:
                    if ip in self.banned:
                        del self.banned[ip]
            time.sleep(10)
