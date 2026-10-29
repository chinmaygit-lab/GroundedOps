# Production integration incident response (synthetic example)

An integration outage is declared severity 1 when production synchronization fails for all clients or a critical client. The on-call engineer opens an incident record, notes the start time, identifies the failing connector, and alerts the incident lead within 10 minutes. Do not silently retry destructive operations.

The incident lead should identify the last successful synchronization cursor, check recent deployment changes, and review API rate limit and authentication errors. Pausing writes is preferred when duplicate mutations are possible. All recovery actions require operator confirmation.

During an ongoing severity 1 incident, publish an internal status update every 30 minutes. The team records the timeline, affected tenants, root cause, impact and resolution after recovery. A follow-up review should be completed within two business days.
