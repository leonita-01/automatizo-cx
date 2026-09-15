# API examples

Set the local API and administrator key:

```bash
export CX_API=http://localhost:8000
export CX_ADMIN_KEY=change-me-before-production
```

## Ask the assistant

```bash
curl -X POST "$CX_API/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Where can I view my invoice?",
    "language": "en"
  }'
```

Continue the same conversation by returning the received `conversation_id`:

```bash
curl -X POST "$CX_API/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "The charge still looks incorrect",
    "language": "en",
    "conversation_id": "REPLACE_WITH_CONVERSATION_ID"
  }'
```

## Assess an automation opportunity

```bash
curl -X POST "$CX_API/api/processes/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Billing address change",
    "monthly_volume": 1200,
    "average_handle_minutes": 8,
    "rule_based_percentage": 85,
    "systems_count": 2,
    "sensitive_data": false
  }'
```

## Create a governed article

```bash
curl -X POST "$CX_API/api/knowledge/articles" \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: $CX_ADMIN_KEY" \
  -d '{
    "title": "Password reset",
    "intent": "account_access",
    "keywords": ["password", "reset", "passwort"],
    "content_en": "Use Forgot password on the approved sign-in page.",
    "content_de": "Nutzen Sie Passwort vergessen auf der Anmeldeseite."
  }'
```

## Import governed content

```bash
curl -X POST "$CX_API/api/knowledge/articles/import" \
  -H "X-Admin-Key: $CX_ADMIN_KEY" \
  -F "file=@sample-data/knowledge-import.json"
```

## Inspect operational evidence

```bash
curl "$CX_API/api/handoffs" -H "X-Admin-Key: $CX_ADMIN_KEY"
curl "$CX_API/api/audit/events" -H "X-Admin-Key: $CX_ADMIN_KEY"
```
