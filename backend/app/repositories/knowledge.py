from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..models import KnowledgeArticle
from ..schemas import KnowledgeArticleCreate, KnowledgeArticleUpdate


def list_articles(
    database: Session,
    *,
    query: str | None = None,
    include_inactive: bool = False,
) -> list[KnowledgeArticle]:
    statement = select(KnowledgeArticle)
    if not include_inactive:
        statement = statement.where(KnowledgeArticle.active.is_(True))
    if query:
        pattern = f"%{query.strip()}%"
        statement = statement.where(
            or_(
                KnowledgeArticle.title.ilike(pattern),
                KnowledgeArticle.intent.ilike(pattern),
                KnowledgeArticle.content_en.ilike(pattern),
                KnowledgeArticle.content_de.ilike(pattern),
            )
        )
    return list(database.scalars(statement.order_by(KnowledgeArticle.title)))


def get_article(database: Session, article_id: int) -> KnowledgeArticle | None:
    return database.get(KnowledgeArticle, article_id)


def get_article_by_title(database: Session, title: str) -> KnowledgeArticle | None:
    statement = select(KnowledgeArticle).where(KnowledgeArticle.title == title)
    return database.scalar(statement)


def create_article(
    database: Session, payload: KnowledgeArticleCreate
) -> KnowledgeArticle:
    article = KnowledgeArticle(**payload.model_dump())
    database.add(article)
    database.commit()
    database.refresh(article)
    return article


def update_article(
    database: Session,
    article: KnowledgeArticle,
    payload: KnowledgeArticleUpdate,
) -> KnowledgeArticle:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(article, field, value)
    database.add(article)
    database.commit()
    database.refresh(article)
    return article


def deactivate_article(database: Session, article: KnowledgeArticle) -> None:
    article.active = False
    database.add(article)
    database.commit()
