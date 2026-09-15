# n8n handoff workflow

## Import

1. Open n8n and select **Import from file**.
2. Choose `handoff-workflow.json`.
3. Configure these n8n environment variables:
   - `TICKETING_API_URL`
   - `TICKETING_API_TOKEN`
4. Activate the workflow.
5. Copy the production Webhook URL into the AutomatizoCX
   `HANDOFF_WEBHOOK_URL` environment variable.

## Workflow behavior

1. Receives the persisted handoff payload.
2. Validates and normalizes priority.
3. Maps the request to a generic external-ticket contract.
4. Calls the ticket API with bearer authorization and an idempotency key.
5. Returns HTTP 202 with downstream delivery status.

The HTTP Request node is intentionally vendor-neutral. Its mapped payload can be
adapted to Zendesk, Salesforce, ServiceNow, HubSpot or another ticketing API.

Do not store the downstream API token inside the exported workflow JSON.
