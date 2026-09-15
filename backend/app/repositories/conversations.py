from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import ConversationTurn


def save_turn(database: Session, **values) -> ConversationTurn:
    turn = ConversationTurn(**values)
    database.add(turn)
    database.commit()
    database.refresh(turn)
    return turn


def get_history(database: Session, conversation_id: str) -> list[ConversationTurn]:
    statement = (
        select(ConversationTurn)
        .where(ConversationTurn.conversation_id == conversation_id)
        .order_by(ConversationTurn.created_at)
    )
    return list(database.scalars(statement))


def get_metrics(database: Session) -> dict:
    totals = database.execute(
        select(
            func.count(ConversationTurn.id),
            func.sum(ConversationTurn.automated),
            func.sum(ConversationTurn.escalated),
            func.avg(ConversationTurn.confidence),
            func.avg(ConversationTurn.latency_ms),
        )
    ).one()
    intent_rows = database.execute(
        select(ConversationTurn.intent, func.count(ConversationTurn.id).label("count"))
        .group_by(ConversationTurn.intent)
        .order_by(func.count(ConversationTurn.id).desc())
        .limit(5)
    ).all()
    return {
        "total": totals[0] or 0,
        "automated": totals[1] or 0,
        "escalated": totals[2] or 0,
        "average_confidence": totals[3] or 0,
        "average_latency_ms": totals[4] or 0,
        "top_intents": [{"intent": row[0], "count": row[1]} for row in intent_rows],
    }
