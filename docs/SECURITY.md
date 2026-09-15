# Security and privacy

## Implemented controls

| Risk | Control |
| --- | --- |
| Personal data in logs/database | Email, phone and payment-pattern redaction before storage |
| Direct customer identifiers | SHA-256 hashing before persistence |
| Prompt-injection attempts | Pattern-based pre-screening, safe refusal, escalation and audit event |
| Hallucinated policy | Retrieval confidence gate and deterministic approved-content fallback |
| Unauthorized administration | Constant-time `X-Admin-Key` comparison |
| Endpoint abuse | Per-client rate limit on chat and handoff |
| Browser abuse | Explicit CORS allowlist and restrictive security headers |
| Duplicate external tickets | Handoff ticket ID used as an idempotency key |
| Untraceable changes | Audit events for governed content and security decisions |
| Oversized imports | 2 MB upload limit and Pydantic validation |

## Data handling

- Raw customer messages are used only during the active request.
- The persisted message is the redacted form.
- The optional LLM receives the redacted form.
- Handoff transcripts are redacted before persistence or webhook delivery.
- Audit metadata deliberately excludes prompts and raw personal data.
- Voice capture is initiated only by the user and handled by the browser's Web
  Speech implementation; organizations must review their browser/provider data
  processing terms before production use.

## Prompt policy

The optional LLM is instructed to use only verified context, refuse to invent
customer/account facts, ignore instructions embedded in user content and
request human assistance when context is insufficient.

## Production recommendations

Before real customer use:

1. Replace the shared administrator key with OIDC/SSO and role-based access.
2. Store secrets in a managed secret store and rotate them.
3. Replace the in-process rate limiter with Redis or an API gateway policy.
4. Use PostgreSQL with encryption, backups and retention controls.
5. Add a DLP provider for locale-specific identifiers.
6. Add model and retrieval evaluation with an approved multilingual dataset.
7. Sign outbound webhook requests and verify downstream TLS policy.
8. Send audit events to a central SIEM.

## Responsible disclosure

This is a portfolio project. Please report security issues privately to the
repository owner rather than opening a public issue containing exploit details.
