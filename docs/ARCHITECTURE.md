# Architecture

## Design goals

AutomatizoCX separates transport, business logic, persistence, integrations
and security so that each concern can be tested and replaced independently.

## Request lifecycle

```mermaid
sequenceDiagram
    participant C as Customer
    participant U as React UI
    participant A as FastAPI
    participant S as Guardrails
    participant K as Knowledge
    participant H as Handoff

    C->>U: Text or voice request
    U->>A: POST /api/chat
    A->>S: Redact PII and inspect prompt
    alt Unsafe request
        S-->>A: Security flags
        A->>H: Persist human handoff
        A-->>U: Safe refusal and escalation
    else Safe request
        A->>K: Rank approved articles
        alt Confidence is sufficient
            K-->>A: Answer and traceable sources
            A-->>U: Grounded response
        else Confidence is low
            A->>H: Persist human handoff
            A-->>U: Escalation with reason
        end
    end
```

## Backend boundaries

| Layer | Responsibility |
| --- | --- |
| Routers | HTTP contracts, access dependencies and response codes |
| Services | Use-case orchestration and business decisions |
| Repositories | SQLAlchemy reads and writes |
| Security | PII handling, injection detection, admin access and rate limiting |
| Integrations | External LLM and ticket-workflow communication |
| Schemas | Input validation and response serialization |
| Models | Persistent operational state |

## Persistent entities

| Entity | Important fields |
| --- | --- |
| KnowledgeArticle | bilingual content, intent, keywords, active state |
| ConversationTurn | redacted message, answer, confidence, latency, decision |
| HandoffTicket | reason, priority, transcript, queue and integration state |
| AuditEvent | action, entity, outcome and safe metadata |

## Reliability decisions

- The application operates without an external LLM.
- Handoff delivery sends an idempotency key and retries once.
- Failed delivery does not discard the locally persisted ticket.
- Health checks verify database connectivity.
- SQLite uses WAL mode and a busy timeout for safer concurrent portfolio use.
- Request IDs are returned to the caller and included in structured logs.
- Knowledge deletion is soft so operational history remains explainable.
