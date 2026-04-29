import subprocess
from audit import write_audit


def ban_ip(ip, duration, notifier):
    try:
        subprocess.run(
            ["iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )
        duration_str = f"{duration}s" if duration > 0 else "permanent"
        write_audit("BAN", ip=ip, condition="anomaly",
                    rate=0, baseline=0, duration=duration)
        notifier.send_ban_alert(ip, duration_str)
        print(f"[BLOCKED] {ip} for {duration_str}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to ban {ip}: {e}")
        return False


def unban_ip(ip, notifier):
    try:
        subprocess.run(
            ["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"],
            check=True
        )
        write_audit("UNBAN", ip=ip, condition="backoff_expired",
                    rate=0, baseline=0, duration=0)
        notifier.send_unban_alert(ip)
        print(f"[UNBLOCKED] {ip}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to unban {ip}: {e}")
        return False
