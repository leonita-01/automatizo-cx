from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories.audit import list_events
from ..schemas import AuditEventRead
from ..security.admin import require_admin_key


router = APIRouter(prefix="/audit", tags=["Security & Audit"])
Database = Annotated[Session, Depends(get_db)]


@router.get(
    "/events",
    response_model=list[AuditEventRead],
    dependencies=[Depends(require_admin_key)],
)
def audit_events(database: Database, limit: int = 100):
    return list_events(database, limit=min(max(limit, 1), 200))
