from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AnalyticsResponse, ProcessAssessment, ProcessInput
from ..services.analytics import build_analytics
from ..services.processes import assess_process


router = APIRouter(tags=["Operate Insights"])
Database = Annotated[Session, Depends(get_db)]


@router.post("/processes/assess", response_model=ProcessAssessment)
def process_assessment(request: ProcessInput) -> ProcessAssessment:
    return assess_process(request)


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(database: Database) -> AnalyticsResponse:
    return build_analytics(database)
