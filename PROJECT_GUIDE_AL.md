# AutomatizoCX — Udhëzues për prezantim

## Çfarë demonstron?

Ky projekt lidh mbi 3 vite përvojë reale në customer support me solution
engineering: Python, JavaScript, APIs, prompt engineering, voice/chatbot,
Knowledge Management, process automation, security dhe dokumentim.

Të gjitha rastet dhe të dhënat janë sintetike. Projekti nuk është ndërtuar për
Sky ose TP dhe nuk përdor informacione konfidenciale.

## Demo 7-minutëshe

1. **Overview:** shpjego automation rate, latency, handoffs dhe intent metrics.
2. **Assistant EN:** pyet `Where can I view my invoice?` dhe trego source/confidence.
3. **Assistant DE:** pyet `Mein Internet funktioniert nicht.`
4. **Human control:** kërko cancellation dhe trego handoff ticket.
5. **Security:** provo një prompt-injection dhe trego audit event.
6. **Knowledge:** importo JSON/CSV dhe shpjego content governance.
7. **Automation:** krahaso një proces rule-based me një proces sensitive.

## Pikat teknike

- FastAPI routers janë të ndara nga services dhe repositories.
- SQLite ruan articles, redacted conversation turns, handoffs dhe audit events.
- Retrieval përdor BM25-style ranking, metadata weighting dhe confidence gate.
- Përgjigjja ka source attribution; pa knowledge të mjaftueshme bëhet escalation.
- OpenAI është opsional; platforma punon edhe me deterministic fallback.
- Voice përdor Web Speech API me locale `en-GB` dhe `de-DE`.
- PII maskohet para database, LLM dhe webhook-ut.
- n8n workflow dërgon ticket me idempotency key.
- CI ekzekuton 21 teste, Ruff, ESLint dhe production build.
- Docker përdor non-root API, Nginx reverse proxy dhe health checks.

## Përshkrimi për CV

**AutomatizoCX — Secure Multilingual Customer-Support Orchestration Platform**

Designed and developed a full-stack customer-experience automation platform
using Python, FastAPI, JavaScript, React and SQLite. Implemented English/German
voice and chat assistance, governed Knowledge Base CRUD/import, BM25-style
retrieval with source attribution, prompt-injection and PII controls, process
automation scoring, persistent human handoffs, REST/webhook integrations, an
importable n8n ticket workflow, operational analytics, Docker and CI quality
gates. Applied 3+ years of customer-support experience to synthetic telecom
workflows without using proprietary data.

## Nëse pyetesh për kufizimet

Trego maturi teknike: SQLite, shared admin key dhe browser voice janë zgjedhje që
e bëjnë portfolio-n të ekzekutueshëm lokalisht. Për production do të përdorje
PostgreSQL, OIDC/RBAC, Redis rate limiting, managed contact-center voice dhe një
multilingual evaluation dataset.
