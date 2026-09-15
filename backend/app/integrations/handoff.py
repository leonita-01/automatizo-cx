import httpx

from ..config import settings
from ..models import HandoffTicket


async def dispatch_handoff(ticket: HandoffTicket) -> str:
    if not settings.handoff_webhook_url:
        return "stored_locally"

    payload = {
        "ticket_id": ticket.id,
        "conversation_id": ticket.conversation_id,
        "reason": ticket.reason,
        "priority": ticket.priority,
        "transcript": ticket.transcript,
        "created_at": ticket.created_at.isoformat(),
    }
    headers = {
        "Content-Type": "application/json",
        "Idempotency-Key": ticket.id,
        "User-Agent": "AutomatizoCX/2.0",
    }
    for attempt in range(2):
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    settings.handoff_webhook_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                return "webhook_delivered"
        except httpx.HTTPError:
            if attempt == 1:
                return "webhook_failed"
    return "webhook_failed"
