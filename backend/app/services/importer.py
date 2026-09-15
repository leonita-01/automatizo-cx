import csv
import io
import json

from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..repositories.knowledge import create_article, get_article_by_title
from ..schemas import ImportResult, KnowledgeArticleCreate


REQUIRED_FIELDS = {"title", "intent", "keywords", "content_en", "content_de"}


def parse_import(content: bytes, filename: str) -> list[dict]:
    decoded = content.decode("utf-8-sig")
    if filename.lower().endswith(".json"):
        payload = json.loads(decoded)
        if not isinstance(payload, list):
            raise ValueError("JSON import must contain a list of articles")
        return payload
    if filename.lower().endswith(".csv"):
        rows = list(csv.DictReader(io.StringIO(decoded)))
        for row in rows:
            row["keywords"] = [
                keyword.strip() for keyword in row.get("keywords", "").split("|")
            ]
        return rows
    raise ValueError("Only .json and .csv files are supported")


def import_articles(database: Session, rows: list[dict]) -> ImportResult:
    imported = 0
    skipped = 0
    errors: list[str] = []
    for index, row in enumerate(rows, start=1):
        missing = REQUIRED_FIELDS - set(row)
        if missing:
            errors.append(f"Row {index}: missing {', '.join(sorted(missing))}")
            skipped += 1
            continue
        try:
            payload = KnowledgeArticleCreate(**row)
            if get_article_by_title(database, payload.title):
                errors.append(f"Row {index}: title already exists")
                skipped += 1
                continue
            create_article(database, payload)
            imported += 1
        except (ValidationError, IntegrityError, TypeError) as error:
            database.rollback()
            errors.append(f"Row {index}: {error}")
            skipped += 1
    return ImportResult(imported=imported, skipped=skipped, errors=errors)
