# GoreeCloud Metrics — Security Status

## Acceptance state

Development source controls only. **No Wardveil Security conformance, security acceptance, target-runtime validation, or production approval is claimed.**

## Current source controls

- Explicit runtime environment and secret-key configuration.
- Production host allowlist requirement and HTTPS-oriented Django hardening.
- `X-Content-Type-Options`, same-origin referrer policy, and deny framing.
- Global 64 KiB request-memory bound plus narrower agent-protocol payload limits.
- One-time enrollment credentials with a maximum 24-hour lifetime.
- Cryptographically secure enrollment and agent secrets.
- Password-hash persistence instead of plaintext server-side enrollment/credential storage.
- Strict enrollment input and telemetry schema validation.
- Per-agent credential authentication for telemetry.
- Agent/credential revocation enforcement.
- Paused/retired monitored-system enforcement.
- Duplicate sample rejection.
- Server-side production checks rejecting insecure machine enrollment/telemetry requests.
- Development agent refusal of non-loopback HTTP URLs.
- Local Development agent state written atomically with mode `0600` and rejected when group/other access is present.
- No command-line parameter for the one-time enrollment secret.
- No telemetry read/admin API while human authorization is absent.
- No inbound listener or remote shell in the Development agent.
- Bounded continuous-agent retry/backoff.
- Minimized first telemetry payload.

These are application-local controls and do not substitute for GoreeCloud Identity or Wardveil.

## Current credential model

The initial source uses:

1. a short-lived one-time enrollment secret;
2. a Metrics-local agent UUID;
3. a per-agent bearer credential whose server representation is a password hash.

This establishes a narrow Development authentication boundary. It is not the final production service/device identity design.

Known open credential work includes rotation, lost-state recovery, approved production secret storage, service/device identity lifecycle, and integration with the current GoreeCloud Identity and Wardveil contracts.

## Transport status

The agent requires HTTPS for non-loopback destinations and the server source rejects insecure machine requests in production configuration.

No production reverse proxy, TLS certificate, service publication, firewall rule, private-network path, certificate pinning/mTLS decision, or target-environment transport has been validated. Source checks must not be reported as encrypted-production evidence.

## Privacy-sensitive security handling

Agent protocol code does not log request bodies, authorization headers, enrollment secrets, or agent credential secrets. The first telemetry schema excludes private workload/content data and unnecessary stable host identifiers.

No public/read telemetry API is provided yet, so source version `0.1.0-dev.2` does not expose stored snapshots to unauthenticated human consumers.

## Known production blockers

- GoreeCloud Identity integration and authorization.
- Wardveil Security contract implementation and acceptance.
- Privacy Shield contract implementation and acceptance.
- Security-relevant structured audit events.
- Abuse prevention/rate limiting.
- Credential rotation and recovery.
- Agent binary/package provenance, service sandbox, least privilege, resource bounds, update/rollback, and target-host evidence.
- Accepted production TLS/network publication.
- Production database/storage security.
- Backup/restore and secret-recovery controls.
- Dependency/vulnerability/release evidence required for promotion.
- Complete deployment and target-runtime negative-path testing.

## CSRF boundary

The two machine-agent POST endpoints are CSRF-exempt because they do not use browser session authentication; they use explicit one-time or per-agent credentials. Human/admin endpoints must not inherit this exception without their own justified authentication and CSRF model.
