from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..integrations.handoff import dispatch_handoff
from ..repositories import audit
from ..repositories import handoffs as repository
from ..schemas import HandoffRead, HandoffRequest
from ..security.admin import require_admin_key
from ..security.guardrails import redact_pii
from ..security.rate_limit import enforce_rate_limit


router = APIRouter(prefix="/handoffs", tags=["Human Handoff"])
Database = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=HandoffRead,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(enforce_rate_limit)],
)
async def create_handoff(request: HandoffRequest, database: Database):
    safe_transcript = [
        {**entry, "content": redact_pii(entry.get("content", ""))}
        for entry in request.transcript
    ]
    safe_request = request.model_copy(update={"transcript": safe_transcript})
    ticket = repository.create_ticket(database, safe_request)
    integration_status = await dispatch_handoff(ticket)
    ticket = repository.update_integration_status(
        database, ticket, integration_status
    )
    audit.record_event(
        database,
        action="handoff.create",
        entity_type="handoff_ticket",
        entity_id=ticket.id,
        outcome="success",
        details={"priority": ticket.priority, "integration": integration_status},
    )
    return ticket


@router.get(
    "",
    response_model=list[HandoffRead],
    dependencies=[Depends(require_admin_key)],
)
def list_handoffs(database: Database, limit: int = 100):
    return repository.list_tickets(database, limit=min(max(limit, 1), 200))
