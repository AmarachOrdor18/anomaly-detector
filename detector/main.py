import json
import threading
import time
import yaml
import os

from monitor import tail_log
from baseline import BaselineTracker
from detector import AnomalyDetector
from blocker import ban_ip
from unbanner import Unbanner
from notifier import Notifier
from dashboard import run_dashboard, state
from audit import write_audit


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path) as f:
        config = yaml.safe_load(f)
    # override webhook from environment variable if set
    webhook = os.environ.get("SLACK_WEBHOOK", "")
    if webhook:
        config["slack_webhook"] = webhook
    return config


def parse_line(line):
    try:
        return json.loads(line)
    except Exception:
        return None


def main():
    config = load_config()
    notifier = Notifier(config["slack_webhook"])
    baseline = BaselineTracker(
        window_minutes=config["baseline_window_minutes"],
        recalc_interval=config["baseline_recalc_interval"]
    )
    detector = AnomalyDetector(window_seconds=config["window_seconds"])
    unbanner = Unbanner(notifier)

    unban_thread = threading.Thread(target=unbanner.run, daemon=True)
    unban_thread.start()

    dash_thread = threading.Thread(
        target=run_dashboard,
        args=(config["dashboard_port"],),
        daemon=True
    )
    dash_thread.start()

    print(f"[STARTED] Tailing {config['log_path']}")

    last_global_alert = 0

    for line in tail_log(config["log_path"]):
        entry = parse_line(line)
        if not entry:
            continue

        ip = entry.get("source_ip", "")
        status = int(entry.get("status", 200))
        is_error = status >= 400

        if not ip or ip == "-":
            continue

        if unbanner.is_banned(ip):
            continue

        baseline.record_request()
        global_rate, ip_rate = detector.record(ip, is_error)

        state["global_rps"] = round(global_rate, 2)
        state["top_ips"] = detector.get_top_ips(10)
        state["banned_ips"] = list(unbanner.banned.keys())
        state["effective_mean"] = round(baseline.effective_mean, 3)
        state["effective_stddev"] = round(baseline.effective_stddev, 3)

        if detector.is_anomalous_ip(ip, ip_rate, baseline, config):
            duration = unbanner.add_ban(ip)
            ban_ip(ip, duration, notifier)
            write_audit(
                "BAN", ip=ip,
                condition=f"ip_rate={ip_rate:.2f}",
                rate=ip_rate,
                baseline=baseline.effective_mean,
                duration=duration
            )
        elif detector.is_anomalous_global(global_rate, baseline, config):
            now = time.time()
            if now - last_global_alert > 60:
                notifier.send_global_alert(global_rate, baseline.effective_mean)
                write_audit(
                    "GLOBAL_ALERT", ip="global",
                    condition=f"global_rate={global_rate:.2f}",
                    rate=global_rate,
                    baseline=baseline.effective_mean,
                    duration=0
                )
                last_global_alert = now


if __name__ == "__main__":
    main()
