import time
import os

AUDIT_LOG = "/var/log/detector/audit.log"


def write_audit(action, ip, condition, rate, baseline, duration):
    os.makedirs(os.path.dirname(AUDIT_LOG), exist_ok=True)
    ts = time.strftime("%Y-%m-%dT%H:%M:%S")
    line = f"[{ts}] {action} ip={ip} | condition={condition} | rate={rate:.2f} | baseline={baseline:.2f} | duration={duration}\n"
    with open(AUDIT_LOG, "a") as f:
        f.write(line)
    print(line.strip())
