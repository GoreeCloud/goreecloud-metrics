# Platform Integration Status

This record is intentionally fail-closed. A required GoreeCloud platform integration is listed as implemented only after application-specific source and validation evidence exists.

| Platform system | Requirement | Current Metrics state |
| --- | --- | --- |
| GoreeCloud Manager | Limited read-only high-level consumer | Not implemented |
| Privacy Shield | Telemetry collection, retention, visibility, and sharing governance | Not implemented |
| Wardveil Security | Security contract and application protections | Not implemented; only project-local baseline HTTP/configuration hardening and local enrollment-secret lifecycle controls exist |
| Everkeep | Backup, restoration, continuity, and recovery | Not implemented |
| Glaze UI | Current Stable 2.2.0 for user-facing UI | Target recorded; user-facing Metrics UI not implemented yet |
| GoreeCloud Mesh | Discovery, relationships, events, dependency context | Not implemented |
| GoreeCloud Identity | User/service/agent identity and authorization integration where applicable | Not implemented; Metrics-local agent identity records are not Identity integration |

Additional planned product integrations such as GoreeCloud Notify, Inventory, and Monitor remain unimplemented.

## Local agent identity boundary

Metrics now has development-level monitored-system records, a Metrics-local one-agent-per-system identity model, hashed one-time enrollment records, hashed agent credential metadata, and revocation primitives. These are application-owned fail-closed foundations only. They do not prove GoreeCloud Identity federation, Wardveil protection, Mesh registration, secure network transport, or deployed-agent authentication.

## Platform manifest

No `goreecloud.platform.yaml` is present. The shared GoreeCloud machine-readable platform declaration/schema is still a platform-level planned capability and is not treated here as an approved contract.

## Release boundary

This repository is development-only. The states above block any claim of Stable, production-ready, platform-conforming, or fully integrated Metrics behavior.
