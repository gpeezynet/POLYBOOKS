from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.inventory import Product, InventoryItem
from app.schemas.inventory import ProductCreate, ProductUpdate, InventoryItemCreate
from app.repositories.base import BaseRepository

class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    def get_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku).first()

class InventoryRepository:
    def create_inventory_item(self, db: Session, item_in: InventoryItemCreate) -> InventoryItem:
        db_item = InventoryItem(
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            location=item_in.location,
            last_count_date=datetime.utcnow(),
            status=item_in.status
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    def get_by_product(self, db: Session, product_id: int) -> List[InventoryItem]:
        return db.query(InventoryItem).filter(InventoryItem.product_id == product_id).all()

    def update_quantity(self, db: Session, item_id: int, quantity: int) -> InventoryItem:
        db_item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
        if db_item:
            db_item.quantity = quantity
            db_item.last_count_date = datetime.utcnow()
            db.commit()
            db.refresh(db_item)
        return db_item

    def get_items_due_for_count(self, db: Session, days: int = 30) -> List[InventoryItem]:
        count_date = datetime.utcnow() - timedelta(days=days)
        return db.query(InventoryItem).filter(
            InventoryItem.last_count_date < count_date
        ).all()