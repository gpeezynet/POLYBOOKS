from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
import uuid

from app.models.transaction import Transaction, TransactionItem, Customer, Vendor
from app.schemas.transaction import TransactionCreate, TransactionItemCreate
from app.repositories.base import BaseRepository

class CustomerRepository(BaseRepository):
    def __init__(self):
        super().__init__(Customer)

class VendorRepository(BaseRepository):
    def __init__(self):
        super().__init__(Vendor)

class TransactionRepository:
    def create_transaction(self, db: Session, transaction: TransactionCreate) -> Transaction:
        # Generate a unique reference number if not provided
        if not transaction.reference_number:
            transaction.reference_number = f"TX-{uuid.uuid4().hex[:8].upper()}"
        
        # Create transaction
        db_transaction = Transaction(
            transaction_type=transaction.transaction_type,
            reference_number=transaction.reference_number,
            customer_id=transaction.customer_id,
            vendor_id=transaction.vendor_id,
            total_amount=transaction.total_amount,
            status=transaction.status,
            notes=transaction.notes
        )
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)
        
        # Create transaction items
        for item in transaction.items:
            db_item = TransactionItem(
                transaction_id=db_transaction.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.quantity * item.unit_price
            )
            db.add(db_item)
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    def get_transaction(self, db: Session, transaction_id: int) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()

    def get_transaction_by_reference(self, db: Session, reference: str) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.reference_number == reference).first()

    def get_transactions(self, db: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return db.query(Transaction).order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()

    def update_transaction_status(self, db: Session, transaction_id: int, status: str) -> Optional[Transaction]:
        db_transaction = self.get_transaction(db, transaction_id)
        if db_transaction:
            db_transaction.status = status
            db.commit()
            db.refresh(db_transaction)
        return db_transaction