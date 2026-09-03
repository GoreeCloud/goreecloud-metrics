# Security Status

## Current controls in source

The current development foundation keeps a deliberately small network attack surface while adding fail-closed local agent-enrollment primitives:

- no monitoring administration UI;
- no network agent enrollment endpoint;
- no telemetry ingestion endpoint;
- no remote command execution;
- no Docker socket access;
- no hardware collector privileges;
- explicit runtime environment selection;
- explicit secret-key requirement;
- explicit production host allowlist requirement;
- production-only HTTPS redirect, secure cookies, and HSTS configuration;
- `nosniff`, same-origin referrer policy, and frame denial;
- liveness/readiness responses that do not expose dependency details;
- a bounded status endpoint containing only source identity/version/lifecycle/API-version fields;
- one-time enrollment and agent credential secrets generated with Python's cryptographically secure `secrets` module;
- plaintext enrollment/agent secrets are never persisted by the enrollment service;
- Django password hashing is used for stored enrollment and agent credential verification material;
- enrollment lifetime is bounded to a maximum of 24 hours;
- previous unused enrollment records are revoked when a replacement is issued;
- enrollment fails closed for missing, malformed, expired, revoked, already-used, or secret-invalid records;
- agent revocation preserves history while revoking all active credential records.

The local `issue_agent_enrollment` management command deliberately displays the one-time enrollment secret once to the invoking operator. That value is sensitive and must only be transferred through an approved secure channel. Shell capture, terminal logging, and automation around this command must be treated accordingly.

## Important limitation

These project-local controls are **not** a Wardveil Security adoption or conformance claim and are **not** GoreeCloud Identity integration. Network enrollment transport, authenticated administration, authorization, service/agent identity federation, certificate handling, audit controls, abuse resistance, credential rotation protocol, dependency-security evidence, and production hardening remain required work before production qualification.

No current HTTP endpoint accepts an agent credential, which is intentional until the transport and authorization contract is designed and validated.

Reusable secrets must not be committed to this repository. `.env` and `.env.*` are ignored except safe example/template files.
