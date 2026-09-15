from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories.conversations import get_history
from ..schemas import ChatRequest, ChatResponse, ConversationTurnRead
from ..security.admin import require_admin_key
from ..security.rate_limit import enforce_rate_limit
from ..services.chat import answer_chat


router = APIRouter(prefix="/chat", tags=["Conversational AI"])
Database = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=ChatResponse,
    dependencies=[Depends(enforce_rate_limit)],
)
async def chat(request: ChatRequest, database: Database) -> ChatResponse:
    return await answer_chat(database, request)


@router.get(
    "/conversations/{conversation_id}",
    response_model=list[ConversationTurnRead],
    dependencies=[Depends(require_admin_key)],
)
def conversation_history(
    conversation_id: str, database: Database
) -> list[ConversationTurnRead]:
    return get_history(database, conversation_id)
