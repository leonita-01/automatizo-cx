import json
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories import audit
from ..repositories import knowledge as repository
from ..schemas import (
    ImportResult,
    KnowledgeArticleCreate,
    KnowledgeArticleRead,
    KnowledgeArticleUpdate,
)
from ..security.admin import require_admin_key
from ..services.importer import import_articles, parse_import


router = APIRouter(prefix="/knowledge/articles", tags=["Knowledge Management"])
Database = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[KnowledgeArticleRead])
def list_knowledge_articles(
    database: Database,
    q: str | None = Query(default=None, max_length=100),
) -> list[KnowledgeArticleRead]:
    return repository.list_articles(database, query=q)


@router.get("/{article_id}", response_model=KnowledgeArticleRead)
def get_knowledge_article(article_id: int, database: Database):
    article = repository.get_article(database, article_id)
    if not article or not article.active:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    return article


@router.post(
    "",
    response_model=KnowledgeArticleRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin_key)],
)
def create_knowledge_article(
    payload: KnowledgeArticleCreate, database: Database
):
    try:
        article = repository.create_article(database, payload)
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=409, detail="Article title already exists") from error
    audit.record_event(
        database,
        action="knowledge.create",
        entity_type="knowledge_article",
        entity_id=str(article.id),
        outcome="success",
        details={"title": article.title},
    )
    return article


@router.patch(
    "/{article_id}",
    response_model=KnowledgeArticleRead,
    dependencies=[Depends(require_admin_key)],
)
def update_knowledge_article(
    article_id: int,
    payload: KnowledgeArticleUpdate,
    database: Database,
):
    article = repository.get_article(database, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    try:
        article = repository.update_article(database, article, payload)
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(status_code=409, detail="Article title already exists") from error
    audit.record_event(
        database,
        action="knowledge.update",
        entity_type="knowledge_article",
        entity_id=str(article.id),
        outcome="success",
        details={"changed_fields": sorted(payload.model_dump(exclude_unset=True))},
    )
    return article


@router.delete(
    "/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin_key)],
)
def delete_knowledge_article(article_id: int, database: Database) -> None:
    article = repository.get_article(database, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge article not found")
    repository.deactivate_article(database, article)
    audit.record_event(
        database,
        action="knowledge.deactivate",
        entity_type="knowledge_article",
        entity_id=str(article.id),
        outcome="success",
    )


@router.post(
    "/import",
    response_model=ImportResult,
    dependencies=[Depends(require_admin_key)],
)
async def import_knowledge_articles(
    database: Database,
    file: UploadFile = File(...),
) -> ImportResult:
    content = await file.read(2_000_001)
    if len(content) > 2_000_000:
        raise HTTPException(status_code=413, detail="Import file exceeds 2 MB")
    try:
        rows = parse_import(content, file.filename or "")
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    result = import_articles(database, rows)
    audit.record_event(
        database,
        action="knowledge.import",
        entity_type="knowledge_article",
        outcome="success" if not result.errors else "partial",
        details={"imported": result.imported, "skipped": result.skipped},
    )
    return result
