# Argus

Argus is a network intrusion detection and prevention platform built for defensive use on networks you are authorized to monitor. It captures live traffic or replays saved PCAP files, decodes packets, and applies behavioral detectors and rules to identify scans, brute force attempts, floods, DNS abuse, and other suspicious activity. Each alert includes evidence and an explained risk score so that findings can be reviewed without guessing. It is a college project built for demonstration and learning.

## Features

Argus provides live capture and PCAP replay, behavioral detectors for port scans, sweeps, brute force, floods, DNS tunneling, denylist matches, and TCP flag anomalies. It includes a rule engine with a safe YAML rule language, statistical anomaly baselines with optional machine learning models, risk scoring with stored contributions, incident correlation, and a response engine with detect only, manual approval, or automatic modes behind a safety guard. The platform includes role based access control, audit logging, REST and WebSocket APIs, a web dashboard, a CLI, and Prometheus metrics. Prevention is off by default and dry run is enforced until explicitly enabled.

## How it works

Argus is split into a backend API, a detection and processing pipeline, and a web dashboard. The Python package lives in packages/argus and contains capture, decoding, features, detection, correlation, risk, response, storage, and API components. The dashboard is a Next.js application in apps/dashboard. Storage uses SQLAlchemy with SQLite by default and supports PostgreSQL. Redis is used for shared rate limits and state when available.

A packet is captured or replayed, then decoded and turned into features. Detection engines compare those features against built-in behavioral rules, YAML rules, and local threat intelligence lists. Every detection produces an evidence string and a risk score with the contribution of each factor. Related detections are grouped into incidents. The response engine can block or rate limit an attacking address in the host firewall, but only after a safety guard checks that the target is not loopback, allowlisted, a management address, or the operator's own address. Dry run mode simulates every action without touching the firewall.

## Requirements

Python 3.12 or higher is required. Node.js 20.9 or higher is required for the dashboard. On Linux, live capture uses AF_PACKET; libpcap is used elsewhere. On Windows, live capture requires Npcap (docs/packet-capture.md:126). Firewall control requires appropriate privileges and is only used when prevention is enabled. Firewall changes on Windows require an Administrator terminal.

## First run

The dashboard opens at http://127.0.0.1:3000 (apps/dashboard/package.json:7, next.config.ts:8). The API runs at http://127.0.0.1:8000 (.env.example:39).

On first start, if no users exist, Argus creates the first administrator account. The username comes from `API__BOOTSTRAP_ADMIN_USERNAME` (default `admin`, settings.py:561) and the password comes from `API__BOOTSTRAP_ADMIN_PASSWORD` (.env.example:48). If you leave the password empty, Argus generates one and writes it to a private file (`initial-admin-password`, services/bootstrap.py:35) that only the server account can read; the console shows the path, never the password. You must change it at first sign-in, which deletes the file.

After logging in, the dashboard shows detections at the Detections page (packages/argus/api/routes/detections.py:21), the firewall status at the Firewall page (packages/argus/api/routes/firewall.py:28), and system health including version at the health endpoint (packages/argus/api/routes/system.py:22).

## Installation

On Linux or macOS:

```
python3 -m venv .venv
.venv/bin/pip install -e ".[dev,ml]"
```

On Windows (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev,ml]"
```

For the dashboard on any platform:

```
cd apps/dashboard
npm ci
```

Copy the example environment file and review it before running:

On Linux or macOS:

```
cp .env.example .env
```

On Windows (PowerShell):

```
copy .env.example .env
```

## Running the backend and the dashboard

On Linux or macOS, start the API server:

```
.venv/bin/argus start --reload
```

On Windows (PowerShell):

```
.\.venv\Scripts\argus start
```

Start only the dashboard:

On Linux or macOS:

```
cd apps/dashboard
ARGUS_API_URL=http://127.0.0.1:8000 npm run dev
```

On Windows (PowerShell):

```
cd apps/dashboard
$env:ARGUS_API_URL="http://127.0.0.1:8000"
npm run dev
```

The dashboard reads `ARGUS_API_URL` (apps/dashboard/next.config.ts:8).

Run both together on Linux or macOS:

```
make dev
```

The plain command behind `make dev` is:

```
.venv/bin/argus start --reload &
(cd apps/dashboard && ARGUS_API_URL=http://127.0.0.1:8000 npm run dev) &
wait
```

On Windows, run the API and the dashboard in separate PowerShell terminals:

Terminal 1:

```
.\.venv\Scripts\argus start --reload
```

Terminal 2:

```
cd apps/dashboard
$env:ARGUS_API_URL="http://127.0.0.1:8000"
npm run dev
```

By default prevention is disabled and the system runs in detection mode.

## Configuration

Argus is configured through environment variables. The environment beats .env; the nested form beats the short form. Confirmed short names (settings.py FLAT_ALIASES):

- DATABASE_URL: database connection string, SQLite by default
- REDIS_URL: Redis connection for rate limits and WebSocket tickets
- RETENTION_DAYS: how long stored events are kept
- API_HOST: host the API binds to
- API_PORT: port the API listens on
- CORS_ORIGINS: origins allowed to call the API
- JWT_SECRET: secret used to sign JWT tokens, required in production
- API__BOOTSTRAP_ADMIN_PASSWORD: password for the first admin account (nested form)
- API__METRICS_TOKEN: bearer token for Prometheus metrics scraped from another host (nested form)
- CAPTURE_INTERFACE: interface name or any for live capture
- CAPTURE__BACKEND: auto, af_packet, or libpcap (nested form)
- BPF_FILTER: optional kernel level packet filter
- PCAP_DIRECTORY: directory of PCAP files to replay
- DETECTION_MODE: disabled, signature_only, balanced, or aggressive
- RESPONSE_MODE: detect_only, manual_approval, or automatic
- DRY_RUN: when true, firewall actions are simulated only
- FIREWALL_BACKEND: null, auto, nftables, iptables, pf, or windows_firewall
- RESPONSE__WEBHOOK_URL: HTTPS endpoint that receives high risk detection posts (nested form)
- ANOMALY__ML_ENABLED: whether the Isolation Forest detector is active (nested form)
- ANOMALY__ML_MODEL_PATH: path to the trained machine learning model (nested form)
- SENSOR_NAME: identifier for this sensor
- LOG_LEVEL: DEBUG, INFO, WARNING, ERROR, or CRITICAL
- LOG_FORMAT: console or json

Additional docker-compose-only variables include POSTGRES_USER, POSTGRES_DB, POSTGRES_PASSWORD, REDIS_PASSWORD, DASHBOARD_PORT, and ARGUS_API_UPSTREAM.

## Running the tests

Backend tests assume the virtual environment is active or use the .venv path:

```
python -m pytest
```

On Windows (PowerShell):

```
.\.venv\Scripts\python -m pytest
```

Tests against real PostgreSQL and Redis (from Makefile test-integration):

On Linux or macOS:

```
ARGUS_TEST_POSTGRES_URL=postgresql://argus:argus-test@127.0.0.1:55432/argus_test
ARGUS_TEST_REDIS_URL=redis://127.0.0.1:56379/0
python -m pytest
```

On Windows (PowerShell):

```
$env:ARGUS_TEST_POSTGRES_URL="postgresql://argus:argus-test@127.0.0.1:55432/argus_test"
$env:ARGUS_TEST_REDIS_URL="redis://127.0.0.1:56379/0"
.\.venv\Scripts\python -m pytest
```

Start PostgreSQL and Redis containers first (from Makefile test-integration):

```
docker run -d --rm --name sx-it-pg -e POSTGRES_USER=argus -e POSTGRES_PASSWORD=argus-test -e POSTGRES_DB=argus_test -p 127.0.0.1:55432:5432 postgres:17-alpine
docker run -d --rm --name sx-it-redis -p 127.0.0.1:56379:6379 redis:7-alpine
```

Real capture and firewall tests require Linux:

```
unshare -rn sh -c 'ip link set lo up && ip link add sx0 type dummy && ip addr add 203.0.113.5/32 dev sx0 && ip addr add 203.0.113.6/32 dev sx0 && ip link set sx0 up && .venv/bin/python -m pytest tests/kernel -p no:cacheprovider'
```

These tests use Linux-only networking primitives (`unshare`, `ip link`, `iptables`) and do not run on Windows.

The frontend can be linted, type checked, and built from apps/dashboard:

```
npm run lint
npm run typecheck
npm run build
```

## Project layout

packages/argus contains the core library and API. apps/dashboard contains the web interface. tests contains test suites. docs contains documentation. scripts contains utilities for benchmarking, seeding, and demonstrations. rules contains detection rules. docker contains container images. pcaps contains capture fixtures.

## Safety notes about the response and firewall features

Prevention is off by default. Dry run is enforced until explicitly enabled. When dry run is turned off or automatic enforcement is enabled, the operator must type the confirmation phrase `ENABLE PREVENTION`. The safety guard refuses to block loopback, link-local, multicast, unspecified, or reserved addresses, and never blocks allowlisted networks or management addresses. Blocks larger than a /24 are refused. On Windows, administrator rights are required for firewall changes and the Windows Firewall adapter is not yet verified on real hosts. Argus is meant for defensive use on networks you are authorised to monitor. Do not run prevention on networks you do not own or have permission to protect.

## Project status and limitations

Argus is version V3. It is a college project built for learning and demonstration. Known gaps include unverified pf and Windows Firewall adapters on real hosts, lack of multi factor authentication, and per process rate limiting while Redis is unavailable. Detection can miss activity that stays below configured thresholds. This software is not a substitute for a dedicated enterprise security tool.

## License

Argus is licensed under the MIT License. Copyright (c) 2026 Dhruv Vijan.

## Acknowledgements

Argus depends on FastAPI, Uvicorn, SQLAlchemy, Pydantic, Scapy, Typer, Next.js, React, Tailwind CSS, and other open source libraries listed in pyproject.toml and package.json. The dashboard bundles fonts under the SIL Open Font License 1.1 as noted in NOTICE.
