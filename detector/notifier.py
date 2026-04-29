import requests
import time


class Notifier:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def _send(self, message):
        try:
            requests.post(self.webhook_url, json={"text": message}, timeout=5)
        except Exception as e:
            print(f"[SLACK ERROR] {e}")

    def send_ban_alert(self, ip, duration, rate=0, baseline=0):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f":rotating_light: *IP BANNED*\n"
            f"IP: `{ip}`\n"
            f"Condition: anomaly detected\n"
            f"Rate: {rate:.2f} req/s\n"
            f"Baseline: {baseline:.2f} req/s\n"
            f"Duration: {duration}\n"
            f"Time: {ts}"
        )
        self._send(msg)

    def send_unban_alert(self, ip):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f":white_check_mark: *IP UNBANNED*\n"
            f"IP: `{ip}`\n"
            f"Time: {ts}"
        )
        self._send(msg)

    def send_global_alert(self, rate, baseline):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        msg = (
            f":warning: *GLOBAL TRAFFIC ANOMALY*\n"
            f"Condition: global rate spike\n"
            f"Rate: {rate:.2f} req/s\n"
            f"Baseline: {baseline:.2f} req/s\n"
            f"Time: {ts}"
        )
        self._send(msg)
