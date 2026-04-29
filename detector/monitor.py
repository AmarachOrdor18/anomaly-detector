import time
import os


def tail_log(log_path):
    while not os.path.exists(log_path):
        print(f"Waiting for log file: {log_path}")
        time.sleep(2)

    with open(log_path, "r") as f:
        f.seek(0, 2)
        while True:
            line = f.readline()
            if line:
                yield line.strip()
            else:
                time.sleep(0.05)
