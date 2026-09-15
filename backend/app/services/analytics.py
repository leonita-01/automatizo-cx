from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..repositories.conversations import get_metrics
from ..repositories.handoffs import count_open_tickets
from ..schemas import AnalyticsResponse


def build_analytics(database: Session) -> AnalyticsResponse:
    metrics = get_metrics(database)
    total = metrics["total"]
    automated = metrics["automated"]
    return AnalyticsResponse(
        total_conversations=total,
        automated_conversations=automated,
        escalated_conversations=metrics["escalated"],
        automation_rate=round(automated / total * 100, 1) if total else 0.0,
        average_confidence=round(metrics["average_confidence"], 3),
        average_latency_ms=round(metrics["average_latency_ms"]),
        open_handoffs=count_open_tickets(database),
        top_intents=metrics["top_intents"],
        generated_at=datetime.now(timezone.utc),
    )
