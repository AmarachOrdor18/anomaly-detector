import time
import psutil
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

state = {
    "banned_ips": [],
    "global_rps": 0.0,
    "top_ips": [],
    "cpu": 0.0,
    "memory": 0.0,
    "effective_mean": 0.0,
    "effective_stddev": 0.0,
    "uptime": time.time()
}

HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Anomaly Detector Dashboard</title>
  <meta http-equiv="refresh" content="3">
  <style>
    body { font-family: monospace; background: #0d1117; color: #c9d1d9; padding: 20px; }
    h1 { color: #58a6ff; }
    h2 { color: #f0883e; margin-top: 30px; }
    table { border-collapse: collapse; width: 100%; margin-top: 10px; }
    th, td { border: 1px solid #30363d; padding: 8px 12px; text-align: left; }
    th { background: #161b22; color: #58a6ff; }
    .banned { color: #f85149; font-weight: bold; }
    .metric { display: inline-block; background: #161b22; border: 1px solid #30363d;
              padding: 15px 25px; margin: 10px; border-radius: 6px; min-width: 150px; }
    .metric-label { font-size: 12px; color: #8b949e; }
    .metric-value { font-size: 24px; color: #58a6ff; margin-top: 5px; }
  </style>
</head>
<body>
  <h1>Anomaly Detection Dashboard</h1>
  <p>Uptime: {{ uptime }} | Auto-refreshes every 3 seconds</p>
  <div class="metric">
    <div class="metric-label">Global Req/s</div>
    <div class="metric-value">{{ state.global_rps }}</div>
  </div>
  <div class="metric">
    <div class="metric-label">CPU Usage</div>
    <div class="metric-value">{{ state.cpu }}%</div>
  </div>
  <div class="metric">
    <div class="metric-label">Memory Usage</div>
    <div class="metric-value">{{ state.memory }}%</div>
  </div>
  <div class="metric">
    <div class="metric-label">Baseline Mean</div>
    <div class="metric-value">{{ state.effective_mean }}</div>
  </div>
  <div class="metric">
    <div class="metric-label">Baseline Stddev</div>
    <div class="metric-value">{{ state.effective_stddev }}</div>
  </div>
  <div class="metric">
    <div class="metric-label">Banned IPs</div>
    <div class="metric-value banned">{{ state.banned_ips | length }}</div>
  </div>
  <h2>Banned IPs</h2>
  <table>
    <tr><th>IP Address</th></tr>
    {% for ip in state.banned_ips %}
    <tr><td class="banned">{{ ip }}</td></tr>
    {% else %}
    <tr><td>No IPs currently banned</td></tr>
    {% endfor %}
  </table>
  <h2>Top 10 Source IPs</h2>
  <table>
    <tr><th>IP Address</th><th>Requests (last 60s)</th></tr>
    {% for ip, count in state.top_ips %}
    <tr><td>{{ ip }}</td><td>{{ count }}</td></tr>
    {% else %}
    <tr><td colspan="2">No traffic yet</td></tr>
    {% endfor %}
  </table>
</body>
</html>
"""


@app.route("/")
def dashboard():
    uptime_seconds = int(time.time() - state["uptime"])
    uptime_str = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
    state["cpu"] = round(psutil.cpu_percent(), 1)
    state["memory"] = round(psutil.virtual_memory().percent, 1)
    return render_template_string(HTML, state=state, uptime=uptime_str)


@app.route("/metrics")
def metrics():
    return jsonify(state)


def run_dashboard(port=8080):
    app.run(host="0.0.0.0", port=port, debug=False)
