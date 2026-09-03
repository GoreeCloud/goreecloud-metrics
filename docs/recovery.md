# GoreeCloud Metrics — Recovery Status

GoreeCloud Metrics does not yet have an accepted production recovery model or Everkeep integration.

## Material Development state now present

Source version `0.1.0-dev.2` can persist:

- monitored-system records;
- Metrics-local agent identities;
- one-time enrollment history;
- agent credential hashes and lifecycle timestamps;
- telemetry snapshots;
- runtime configuration outside source;
- local Development agent state containing the reusable per-agent credential.

Telemetry snapshots use a bounded Development retention window, but retention is not backup.

## Current recoverability

- Source code is reconstructible from GitHub.
- Database migrations are source-controlled and CI-applied.
- Expired telemetry can be removed by ingestion pruning or `prune_telemetry`.
- Agent revocation preserves server-side identity/credential history.

No database backup/restore procedure is implemented or validated. No isolated restore test exists. No Everkeep contract is implemented. No accepted recovery exists for a lost local agent credential/state file, and the current source has no credential-rotation/re-enrollment workflow for that case.

The local agent state file must not be copied into ordinary source control, logs, documentation, or unprotected backups merely to make recovery convenient.

## Production recovery requirements still open

Before production qualification, Metrics requires an approved and tested model for:

- server configuration;
- monitored-system and agent records;
- credential lifecycle and secret recovery/replacement;
- retention settings;
- required historical telemetry classes;
- database backup and restore;
- deployment configuration;
- integration configuration;
- application and agent version identity;
- production Metrics Agent configuration/state;
- rollback after schema/application/agent changes;
- privacy-preserving deletion and backup-retention behavior;
- Everkeep integration and acceptance.

Source CI is not recovery evidence.
