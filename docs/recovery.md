# Recovery Status

GoreeCloud Metrics does not yet have a production recovery model.

The current development database can now contain monitored-system definitions, agent identity records, one-time enrollment metadata, and hashed agent credential metadata. Those records are development state only; there is no production database or accepted restoration procedure. Source code is version controlled, but source control alone is not considered recovery.

Plaintext enrollment and agent credential secrets are intentionally not persisted, so a future recovery design must not assume they can or should be reconstructed from a database backup. Recovery and credential re-establishment/rotation are separate concerns that require an approved model.

Before production qualification, Metrics must define and validate Everkeep-governed backup and restoration for all required application state, including configuration, system definitions, identities/enrollment metadata, alert rules, integration configuration, required historical data, application version identity, and approved secret-recovery or credential-reissuance mechanisms.

Restoration evidence does not exist yet.
