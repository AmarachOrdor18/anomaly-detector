# Anomaly Detection Engine

A real-time HTTP traffic anomaly detection and DDoS protection tool built alongside Nextcloud.

## Server Details
- **Server IP**: 13.60.167.245
- **Metrics Dashboard**: https://amarachi-detect.duckdns.org
- **Language**: Python

## Architecture
- Nginx reverse proxy with JSON access logs
- Python daemon monitoring logs in real time
- Redis-free sliding window anomaly detection
- iptables-based IP blocking
- Flask dashboard refreshing every 3 seconds

## How the Sliding Window Works
Two deque-based windows track request rates over the last 60 seconds:
- Per-IP window: timestamps of requests from each IP stored in a deque
- Global window: timestamps of all requests stored in a deque
- On each new request, timestamps older than 60 seconds are evicted from the left
- Rate = number of entries in deque / 60

## How the Baseline Works
- Rolling 30-minute window of per-second request counts
- Recalculated every 60 seconds
- Per-hour slots maintained — current hour preferred when it has 60+ samples
- Floor values: mean=0.1, stddev=0.1 to avoid division by zero

## Detection Logic
An IP or global rate is flagged as anomalous if:
- Z-score exceeds 3.0, OR
- Rate is more than 5x the baseline mean
- Error surge (4xx/5xx rate 3x baseline) tightens thresholds by 30%

## How iptables Blocking Works
When an IP is flagged:
1. `iptables -I INPUT -s <ip> -j DROP` drops all packets from that IP
2. Slack alert sent within 10 seconds
3. Auto-unban on backoff schedule: 10min → 30min → 2hrs → permanent

## Setup Instructions

### Prerequisites
- Ubuntu 22.04+ VPS (2 vCPU, 2GB RAM minimum)
- Docker and Docker Compose installed
- A domain pointing to your server

### Steps
```bash
git clone https://github.com/AmarachOrdor18/anomaly-detector.git
cd anomaly-detector
# Edit detector/config.yaml with your Slack webhook URL
docker compose up -d --build
```

## Repository
https://github.com/AmarachOrdor18/anomaly-detector
