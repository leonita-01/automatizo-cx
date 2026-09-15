import math
import re
from collections import Counter
from dataclasses import dataclass

from ..models import KnowledgeArticle


TOKEN_PATTERN = re.compile(r"\w+", re.UNICODE)
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "der",
    "die",
    "das",
    "ein",
    "eine",
    "for",
    "how",
    "ich",
    "in",
    "ist",
    "mein",
    "me",
    "my",
    "of",
    "please",
    "the",
    "to",
    "und",
    "was",
    "with",
    "where",
    "you",
    "your",
}


@dataclass(frozen=True)
class RetrievalResult:
    article: KnowledgeArticle
    relevance: float


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in TOKEN_PATTERN.findall(text.lower())
        if len(token) > 1 and token not in STOP_WORDS
    ]


def article_document(article: KnowledgeArticle, language: str) -> list[str]:
    content = article.content_en if language == "en" else article.content_de
    weighted_metadata = " ".join(
        [article.title, article.intent, article.intent]
        + article.keywords
        + article.keywords
        + article.keywords
    )
    return tokenize(f"{weighted_metadata} {content}")


def rank_articles(
    query: str,
    articles: list[KnowledgeArticle],
    language: str,
    limit: int = 3,
) -> list[RetrievalResult]:
    query_tokens = tokenize(query)
    if not query_tokens or not articles:
        return []

    documents = [article_document(article, language) for article in articles]
    average_length = sum(len(document) for document in documents) / len(documents)
    document_frequency = Counter(
        token for token in set(query_tokens) for document in documents if token in document
    )
    query_counts = Counter(query_tokens)
    scored: list[tuple[float, KnowledgeArticle]] = []

    for article, document in zip(articles, documents, strict=True):
        frequencies = Counter(document)
        metadata_tokens = set(
            tokenize(
                " ".join([article.title, article.intent, *article.keywords])
            )
        )
        metadata_matches = set(query_tokens) & metadata_tokens
        content_matches = set(query_tokens) & set(document)
        if not metadata_matches and len(content_matches) < 2:
            continue
        score = 0.0
        for token, query_frequency in query_counts.items():
            if not frequencies[token]:
                continue
            inverse_document_frequency = math.log(
                1 + (len(documents) - document_frequency[token] + 0.5)
                / (document_frequency[token] + 0.5)
            )
            term_frequency = frequencies[token]
            denominator = term_frequency + 1.5 * (
                1 - 0.75 + 0.75 * len(document) / max(average_length, 1)
            )
            score += (
                inverse_document_frequency
                * (term_frequency * 2.5 / denominator)
                * min(query_frequency, 2)
            )
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda item: item[0], reverse=True)
    if not scored:
        return []

    top_score = scored[0][0]
    results = []
    for score, article in scored[:limit]:
        relative_score = score / top_score
        query_coverage = len(set(query_tokens) & set(article_document(article, language)))
        query_coverage /= max(len(set(query_tokens)), 1)
        relevance = min(0.99, 0.55 * relative_score + 0.44 * query_coverage)
        results.append(RetrievalResult(article=article, relevance=round(relevance, 3)))
    return results
