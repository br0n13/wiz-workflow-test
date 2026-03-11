# Webhook Listener Contract (Centralized Dispatch)

This repository expects the webhook listener service to dispatch a `repository_dispatch` event:

- **Target repo**: this centralized scan repository
- **Event type**: `wiz-cli-scan`
- **Payload fields**:
  - `target_owner`
  - `target_repo`
  - `target_ref` (prefer PR head SHA)
  - `pull_request_number` (optional)
  - `installation_id`

Example dispatch payload:

```json
{
  "event_type": "wiz-cli-scan",
  "client_payload": {
    "target_owner": "acme",
    "target_repo": "payments-service",
    "target_ref": "3f2c...",
    "pull_request_number": "42",
    "installation_id": "123456"
  }
}
```
