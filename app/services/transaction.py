from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.transaction import Transaction, TransactionItem
from app.schemas.transaction import TransactionCreate, TransactionItemCreate
from app.repositories.transaction import TransactionRepository
from app.services.inventory import InventoryService

class TransactionService:
    def __init__(self):
        self.repository = TransactionRepository()
        self.inventory_service = InventoryService()
    
    def get_transaction(self, db: Session, transaction_id: int) -> Optional[Transaction]:
        return self.repository.get_transaction(db, transaction_id)
    
    def get_transactions(self, db: Session, skip: int = 0, limit: int = 100) -> List[Transaction]:
        return self.repository.get_transactions(db, skip, limit)
    
    def create_transaction(self, db: Session, transaction: TransactionCreate) -> Transaction:
        # Create the transaction
        db_transaction = self.repository.create_transaction(db, transaction)
        
        # Update inventory based on transaction type
        if transaction.transaction_type == "sale":
            self._process_sale(db, db_transaction)
        elif transaction.transaction_type == "purchase":
            self._process_purchase(db, db_transaction)
        elif transaction.transaction_type == "return":
            self._process_return(db, db_transaction)
        elif transaction.transaction_type == "adjustment":
            self._process_adjustment(db, db_transaction)
        
        return db_transaction
    
    def update_transaction_status(self, db: Session, transaction_id: int, status: str) -> Optional[Transaction]:
        return self.repository.update_transaction_status(db, transaction_id, status)
    
    def _process_sale(self, db: Session, transaction: Transaction) -> None:
        """Reduce inventory quantities for sale transactions"""
        for item in transaction.items:
            inventory_items = self.inventory_service.get_inventory_items_by_product(db, item.product_id)
            remaining_quantity = item.quantity
            
            for inv_item in inventory_items:
                if inv_item.quantity >= remaining_quantity:
                    inv_item.quantity -= remaining_quantity
                    break
                else:
                    remaining_quantity -= inv_item.quantity
                    inv_item.quantity = 0
            
            db.commit()
    
    def _process_purchase(self, db: Session, transaction: Transaction) -> None:
        """Increase inventory quantities for purchase transactions"""
        for item in transaction.items:
            # Check if inventory item exists for this product
            inventory_items = self.inventory_service.get_inventory_items_by_product(db, item.product_id)
            
            if inventory_items:
                # Add to existing inventory
                inventory_items[0].quantity += item.quantity
            else:
                # Create new inventory item
                from app.schemas.inventory import InventoryItemCreate
                inventory_item = InventoryItemCreate(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    location="Main Warehouse",
                    status="available"
                )
                self.inventory_service.add_inventory(db, inventory_item)
    
    def _process_return(self, db: Session, transaction: Transaction) -> None:
        """Process return: increase inventory for returned items"""
        for item in transaction.items:
            inventory_items = self.inventory_service.get_inventory_items_by_product(db, item.product_id)
            
            if inventory_items:
                # Add to existing inventory
                inventory_items[0].quantity += item.quantity
            else:
                # Create new inventory item
                from app.schemas.inventory import InventoryItemCreate
                inventory_item = InventoryItemCreate(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    location="Returns",
                    status="returned"
                )
                self.inventory_service.add_inventory(db, inventory_item)
    
    def _process_adjustment(self, db: Session, transaction: Transaction) -> None:
        """Process inventory adjustment"""
        for item in transaction.items:
            inventory_items = self.inventory_service.get_inventory_items_by_product(db, item.product_id)
            
            if inventory_items:
                # Update existing inventory
                inventory_items[0].quantity = item.quantity  # Set to the adjusted quantity
                inventory_items[0].last_count_date = datetime.utcnow()
            else:
                # Create new inventory item with the adjusted quantity
                from app.schemas.inventory import InventoryItemCreate
                inventory_item = InventoryItemCreate(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    location="Main Warehouse",
                    status="available"
                )
                self.inventory_service.add_inventory(db, inventory_item)