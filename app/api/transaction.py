from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.transaction import Transaction, TransactionCreate
from app.services.transaction import TransactionService
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/transactions", tags=["transactions"])
transaction_service = TransactionService()

@router.post("/", response_model=Transaction)
async def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return transaction_service.create_transaction(db, transaction)

@router.get("/", response_model=List[Transaction])
async def read_transactions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    transactions = transaction_service.get_transactions(db, skip=skip, limit=limit)
    return transactions

@router.get("/{transaction_id}", response_model=Transaction)
async def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    transaction = transaction_service.get_transaction(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/{transaction_id}/status", response_model=Transaction)
async def update_transaction_status(
    transaction_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Validate status
    valid_statuses = ["pending", "completed", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    transaction = transaction_service.update_transaction_status(db, transaction_id, status)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction