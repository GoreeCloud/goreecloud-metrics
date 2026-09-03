# GoreeCloud Metrics — Development Agent Protocol

## Status

Protocol version: `1`  
Source version introduced: `0.1.0-dev.2`  
Acceptance: Development source only

This is not a production GoreeCloud Identity, Wardveil Security, Privacy Shield, or Mesh contract.

## Enrollment

`POST /api/v1/agents/enroll/`

Request body, exact fields:

```json
{
  "enrollment_id": "<uuid>",
  "enrollment_secret": "<one-time-secret>",
  "agent_version": "0.1.0-dev.2"
}
```

Successful response (`201`), exact fields:

```json
{
  "agent_id": "<uuid>",
  "credential_id": "<uuid>",
  "credential_secret": "<per-agent-secret>"
}
```

The response is `Cache-Control: no-store`. The plaintext credential secret is returned only at this boundary. Server persistence stores a password hash.

Enrollment fails closed when the identifier, secret, version, record state, expiry, or expected payload shape is invalid.

## Telemetry authentication

`POST /api/v1/agents/telemetry/`

Required headers:

```text
Authorization: Bearer <per-agent-secret>
X-GoreeCloud-Metrics-Credential-ID: <credential-uuid>
Content-Type: application/json
```

The agent credential authorizes only the current Metrics-local telemetry operation. It is not a reusable administrative credential.

## Telemetry payload version 1

Exact top-level fields:

```json
{
  "schema_version": 1,
  "sample_id": "<uuid>",
  "sampled_at": "<RFC3339 timestamp>",
  "agent_version": "0.1.0-dev.2",
  "cpu": {},
  "memory": {},
  "filesystem": {},
  "network": {}
}
```

### CPU

Exact fields:

- `logical_processors`
- `load_1`
- `load_5`
- `load_15`
- `user_ticks`
- `nice_ticks`
- `system_ticks`
- `idle_ticks`
- `iowait_ticks`
- `irq_ticks`
- `softirq_ticks`
- `steal_ticks`

### Memory

Exact fields:

- `total_bytes`
- `available_bytes`
- `swap_total_bytes`
- `swap_free_bytes`

Available/free values may not exceed corresponding totals.

### Filesystem

Exact fields:

- `mount` — currently must equal `/`
- `total_bytes`
- `available_bytes`

### Network

Exact fields:

- `rx_bytes`
- `tx_bytes`

The Development collector totals non-loopback interfaces.

## Validation bounds

- Enrollment body: maximum 8 KiB.
- Telemetry body: maximum 32 KiB.
- Global Django request-memory bound: 64 KiB.
- `Content-Length` is required for these JSON machine requests.
- Telemetry schema version must be exactly `1`.
- Sample timestamps may be at most 24 hours old and at most five minutes in the future.
- Counter values are non-negative integers bounded below `2^63`.
- Logical processor count is 1–65535.
- Load values must be finite and between 0 and 1,000,000.
- Agent version is non-empty and at most 64 characters.
- Unknown fields are rejected.
- Duplicate `sample_id` values are rejected.
- Revoked credentials/agents and paused/retired systems are rejected.

## Transport

The Development agent permits HTTP only to `localhost`, `127.0.0.1`, or `::1`. Other destinations require HTTPS.

When the Django server is configured as production, its agent enrollment and telemetry views also reject insecure requests. This source behavior is not a substitute for target-environment reverse-proxy, TLS, certificate, firewall, Identity, or Wardveil acceptance evidence.

## Data minimization

The protocol intentionally does not include:

- hostname;
- IP addresses;
- hardware serial numbers;
- usernames;
- process lists;
- environment variables;
- command lines;
- file contents;
- logs;
- packet contents;
- container metadata.

Any future schema expansion requires a documented monitoring purpose plus security/privacy review.

## Retention

Snapshots use the server's bounded `METRICS_TELEMETRY_RETENTION_HOURS` value. The Development default is 168 hours and the current source permits 1–2160 hours.

Expired records are pruned during successful ingestion and by `python manage.py prune_telemetry`.

This does not establish production deletion, backup, restore, historical aggregation, or portability behavior.

## Retry behavior

The Development agent's continuous mode uses a 10–3600 second collection interval and bounded exponential backoff up to five minutes after collection or communication failure.

A sample has a client-generated UUID. Because duplicate sample IDs are rejected, the current client does not automatically retry a sample after an ambiguous post-send failure; a later collection iteration creates a new sample. A durable offline/replay protocol is not yet implemented.

## Security and acceptance boundary

Open production gates include:

- production device/service identity and authorization;
- credential rotation/recovery and accepted secret storage;
- abuse/rate-limit controls;
- security-relevant audit integration;
- accepted encrypted transport and network publication;
- Wardveil integration/acceptance;
- Privacy Shield adapter/acceptance;
- Metrics Agent package/service hardening and least-privilege evidence;
- deployment and target-runtime validation.
