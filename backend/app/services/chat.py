from time import perf_counter
from uuid import uuid4

from sqlalchemy.orm import Session

from ..integrations.handoff import dispatch_handoff
from ..integrations.llm import enhance_grounded_answer
from ..repositories import audit, conversations, handoffs, knowledge
from ..schemas import ChatRequest, ChatResponse, HandoffRequest, SourceReference
from ..security.guardrails import (
    assess_prompt_security,
    hash_identifier,
    redact_pii,
)
from .retrieval import rank_articles


ESCALATION_INTENTS = {"cancellation"}
MINIMUM_RELEVANCE = 0.48


def localized_unknown(language: str) -> str:
    if language == "de":
        return (
            "Ich konnte keine ausreichend verlässliche Antwort in der "
            "Wissensdatenbank finden. Die Anfrage wird an einen Mitarbeiter übergeben."
        )
    return (
        "I could not find a sufficiently reliable answer in the knowledge base. "
        "The request will be passed to a support specialist."
    )


def localized_security_response(language: str) -> str:
    if language == "de":
        return (
            "Diese Anfrage kann aus Sicherheitsgründen nicht automatisiert bearbeitet "
            "werden. Ein Mitarbeiter kann Ihnen weiterhelfen."
        )
    return (
        "For security reasons, this request cannot be handled automatically. "
        "A support specialist can assist you."
    )


async def answer_chat(database: Session, request: ChatRequest) -> ChatResponse:
    started_at = perf_counter()
    conversation_id = request.conversation_id or str(uuid4())
    redacted_message = redact_pii(request.message)
    security = assess_prompt_security(redacted_message)

    if not security.safe:
        answer = localized_security_response(request.language)
        response = ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            intent="security_review",
            confidence=1.0,
            automated=False,
            escalation_required=True,
            escalation_reason="Potential prompt-injection attempt",
            sources=[],
            security_flags=security.flags,
            latency_ms=round((perf_counter() - started_at) * 1000),
        )
        audit.record_event(
            database,
            action="chat.security_block",
            entity_type="conversation",
            entity_id=conversation_id,
            outcome="blocked",
            details={"flags": security.flags},
        )
    else:
        articles = knowledge.list_articles(database)
        ranked = rank_articles(redacted_message, articles, request.language)
        relevant = ranked and ranked[0].relevance >= MINIMUM_RELEVANCE

        if not relevant:
            response = ChatResponse(
                conversation_id=conversation_id,
                answer=localized_unknown(request.language),
                intent="unknown",
                confidence=ranked[0].relevance if ranked else 0.0,
                automated=False,
                escalation_required=True,
                escalation_reason="Knowledge confidence below threshold",
                sources=[],
                latency_ms=round((perf_counter() - started_at) * 1000),
            )
        else:
            top_result = ranked[0]
            context = (
                top_result.article.content_en
                if request.language == "en"
                else top_result.article.content_de
            )
            answer = await enhance_grounded_answer(
                question=redacted_message,
                verified_context=context,
                language=request.language,
            )
            escalation_required = top_result.article.intent in ESCALATION_INTENTS
            response = ChatResponse(
                conversation_id=conversation_id,
                answer=answer,
                intent=top_result.article.intent,
                confidence=top_result.relevance,
                automated=not escalation_required,
                escalation_required=escalation_required,
                escalation_reason=(
                    "Identity verification required"
                    if escalation_required
                    else None
                ),
                sources=[
                    SourceReference(
                        article_id=result.article.id,
                        title=result.article.title,
                        relevance=result.relevance,
                    )
                    for result in ranked
                    if result.relevance >= MINIMUM_RELEVANCE
                ],
                latency_ms=round((perf_counter() - started_at) * 1000),
            )

    conversations.save_turn(
        database,
        conversation_id=conversation_id,
        customer_id_hash=hash_identifier(request.customer_id),
        message_redacted=redacted_message,
        answer=response.answer,
        language=request.language,
        intent=response.intent,
        confidence=response.confidence,
        automated=response.automated,
        escalated=response.escalation_required,
        latency_ms=response.latency_ms,
    )

    if response.escalation_required:
        ticket = handoffs.create_ticket(
            database,
            HandoffRequest(
                conversation_id=conversation_id,
                reason=response.escalation_reason or "Human review requested",
                priority="high" if response.security_flags else "normal",
                transcript=[
                    {"role": "customer", "content": redacted_message},
                    {"role": "assistant", "content": response.answer},
                ],
            ),
        )
        integration_status = await dispatch_handoff(ticket)
        handoffs.update_integration_status(database, ticket, integration_status)
        audit.record_event(
            database,
            action="handoff.auto_create",
            entity_type="handoff_ticket",
            entity_id=ticket.id,
            outcome="success",
            details={"integration": integration_status, "priority": ticket.priority},
        )
    return response
