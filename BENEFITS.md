# GoreeCloud Metrics — Current Benefits

Benefits listed here are limited to behavior implemented by the current Development source.

## Current development benefits

- **First native end-to-end telemetry path:** a GoreeCloud-owned agent can enroll and submit a strictly bounded core Linux resource sample to the GoreeCloud-owned server.
- **No monitored-host listener requirement:** the Development agent initiates outbound communication rather than opening a general remote-administration or telemetry port.
- **Minimized first payload:** the core sample excludes hostnames, IP addresses, serial identifiers, process lists, environment variables, commands, logs, and file contents.
- **Fail-closed credential handling:** one-time enrollment, per-agent hashed server credentials, revocation enforcement, and owner-only local state reduce accidental credential exposure.
- **Bounded transport and input:** request-size limits, strict JSON shapes, timestamp bounds, numeric bounds, relationship checks, duplicate sample rejection, and HTTPS enforcement for non-loopback agent connections reduce malformed-input and transport risks.
- **Bounded Development retention:** snapshots default to seven days and cannot be configured beyond 90 days in the current source; expired data is pruned during ingestion and can be pruned explicitly.
- **Clear acceptance boundaries:** source documentation and platform status explicitly separate application-local controls from unimplemented GoreeCloud Identity, Wardveil Security, Privacy Shield, Everkeep, Mesh, Manager, and Glaze UI acceptance.

## Not yet available

User-facing resource visibility, historical charts, hardware-health insight, alerts, capacity planning, integrated GoreeCloud administration, accepted platform security/privacy identity, and validated recovery remain unavailable until their corresponding implementations and evidence exist.
