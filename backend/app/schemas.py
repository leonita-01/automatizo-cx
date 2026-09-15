from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)
    language: str = Field(default="en", pattern="^(en|de)$")
    customer_id: str | None = Field(default=None, max_length=120)
    conversation_id: str | None = Field(default=None, max_length=36)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        return " ".join(value.split())


class SourceReference(BaseModel):
    article_id: int
    title: str
    relevance: float


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    intent: str
    confidence: float = Field(ge=0, le=1)
    automated: bool
    escalation_required: bool
    escalation_reason: str | None = None
    sources: list[SourceReference]
    security_flags: list[str] = Field(default_factory=list)
    latency_ms: int


class ConversationTurnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: str
    message_redacted: str
    answer: str
    language: str
    intent: str
    confidence: float
    automated: bool
    escalated: bool
    latency_ms: int
    created_at: datetime


class ProcessInput(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    monthly_volume: int = Field(ge=0, le=10_000_000)
    average_handle_minutes: float = Field(gt=0, le=480)
    rule_based_percentage: int = Field(ge=0, le=100)
    systems_count: int = Field(ge=1, le=20)
    sensitive_data: bool = False


class ProcessAssessment(BaseModel):
    process_name: str
    automation_score: int = Field(ge=0, le=100)
    recommendation: str
    estimated_hours_saved_monthly: float
    estimated_fte_capacity: float
    risk_level: str
    rationale: list[str]


class KnowledgeArticleBase(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    intent: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9_]+$")
    keywords: list[str] = Field(min_length=1, max_length=30)
    content_en: str = Field(min_length=10, max_length=5000)
    content_de: str = Field(min_length=10, max_length=5000)

    @field_validator("keywords")
    @classmethod
    def normalize_keywords(cls, values: list[str]) -> list[str]:
        normalized = {value.strip().lower() for value in values if value.strip()}
        if not normalized:
            raise ValueError("At least one non-empty keyword is required")
        return sorted(normalized)


class KnowledgeArticleCreate(KnowledgeArticleBase):
    pass


class KnowledgeArticleUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=160)
    intent: str | None = Field(default=None, pattern=r"^[a-z0-9_]+$")
    keywords: list[str] | None = None
    content_en: str | None = Field(default=None, min_length=10, max_length=5000)
    content_de: str | None = Field(default=None, min_length=10, max_length=5000)
    active: bool | None = None

    @field_validator("keywords")
    @classmethod
    def normalize_optional_keywords(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        normalized = {value.strip().lower() for value in values if value.strip()}
        if not normalized:
            raise ValueError("At least one non-empty keyword is required")
        return sorted(normalized)


class KnowledgeArticleRead(KnowledgeArticleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool
    created_at: datetime
    updated_at: datetime


class ImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[str]


class HandoffRequest(BaseModel):
    conversation_id: str | None = Field(default=None, max_length=36)
    reason: str = Field(min_length=3, max_length=500)
    transcript: list[dict[str, str]] = Field(default_factory=list, max_length=100)
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")


class HandoffRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str | None
    reason: str
    priority: str
    status: str
    integration_status: str
    transcript: list[dict[str, str]]
    created_at: datetime


class AnalyticsResponse(BaseModel):
    total_conversations: int
    automated_conversations: int
    escalated_conversations: int
    automation_rate: float
    average_confidence: float
    average_latency_ms: int
    open_handoffs: int
    top_intents: list[dict[str, int | str]]
    generated_at: datetime


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    action: str
    entity_type: str
    entity_id: str | None
    outcome: str
    details: dict
    created_at: datetime
