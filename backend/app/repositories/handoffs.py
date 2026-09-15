from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import HandoffTicket
from ..schemas import HandoffRequest


def create_ticket(database: Session, payload: HandoffRequest) -> HandoffTicket:
    ticket = HandoffTicket(**payload.model_dump())
    database.add(ticket)
    database.commit()
    database.refresh(ticket)
    return ticket


def update_integration_status(
    database: Session, ticket: HandoffTicket, integration_status: str
) -> HandoffTicket:
    ticket.integration_status = integration_status
    database.add(ticket)
    database.commit()
    database.refresh(ticket)
    return ticket


def list_tickets(database: Session, limit: int = 100) -> list[HandoffTicket]:
    statement = (
        select(HandoffTicket).order_by(HandoffTicket.created_at.desc()).limit(limit)
    )
    return list(database.scalars(statement))


def count_open_tickets(database: Session) -> int:
    statement = select(func.count(HandoffTicket.id)).where(
        HandoffTicket.status.in_(["queued", "assigned"])
    )
    return database.scalar(statement) or 0
