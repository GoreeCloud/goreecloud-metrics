# Security Status

## Current controls in source

The initial foundation implements a deliberately small attack surface:

- no monitoring administration UI;
- no agent enrollment endpoint;
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
- a bounded status endpoint containing only source identity/version/lifecycle/API-version fields.

## Important limitation

These project-local controls are not a Wardveil Security adoption or conformance claim. Wardveil integration, authenticated administration, authorization, service/agent identity, audit controls, abuse resistance, dependency-security evidence, and production hardening remain required work before production qualification.

Reusable secrets must not be committed to this repository. `.env` and `.env.*` are ignored except safe example/template files.
