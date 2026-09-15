from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AuditEvent


def record_event(
    database: Session,
    *,
    action: str,
    entity_type: str,
    outcome: str,
    entity_id: str | None = None,
    details: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        outcome=outcome,
        details=details or {},
    )
    database.add(event)
    database.commit()
    database.refresh(event)
    return event


def list_events(database: Session, limit: int = 100) -> list[AuditEvent]:
    statement = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
    return list(database.scalars(statement))
