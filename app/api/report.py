from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.schemas.report import NaturalLanguageQuery, QueryResult
from app.services.report import ReportGenerator
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/reports", tags=["reports"])
report_service = ReportGenerator()

@router.get("/inventory")
async def generate_inventory_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return report_service.generate_inventory_report(db)

@router.get("/sales")
async def generate_sales_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return report_service.generate_sales_report(db, start_date, end_date)

@router.post("/query", response_model=QueryResult)
async def process_report_query(
    query: NaturalLanguageQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return report_service.process_natural_language_query(db, query.query)