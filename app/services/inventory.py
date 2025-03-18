from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.inventory import Product, InventoryItem
from app.schemas.inventory import ProductCreate, ProductUpdate, InventoryItemCreate
from app.repositories.inventory import ProductRepository, InventoryRepository

class InventoryService:
    def __init__(self):
        self.product_repository = ProductRepository(Product)
        self.inventory_repository = InventoryRepository()
    
    def get_product(self, db: Session, product_id: int) -> Optional[Product]:
        return self.product_repository.get(db, product_id)
    
    def get_product_by_sku(self, db: Session, sku: str) -> Optional[Product]:
        return self.product_repository.get_by_sku(db, sku)
    
    def get_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        return self.product_repository.get_multi(db, skip=skip, limit=limit)
    
    def create_product(self, db: Session, product: ProductCreate) -> Product:
        return self.product_repository.create(db, obj_in=product)
    
    def update_product(self, db: Session, product_id: int, product: ProductUpdate) -> Optional[Product]:
        db_product = self.product_repository.get(db, id=product_id)
        if db_product:
            return self.product_repository.update(db, db_obj=db_product, obj_in=product)
        return None
    
    def delete_product(self, db: Session, product_id: int) -> bool:
        db_product = self.product_repository.get(db, id=product_id)
        if db_product:
            self.product_repository.remove(db, id=product_id)
            return True
        return False
    
    def add_inventory(self, db: Session, inventory_item: InventoryItemCreate) -> Optional[InventoryItem]:
        # Check if product exists
        product = self.product_repository.get(db, id=inventory_item.product_id)
        if not product:
            return None
        
        return self.inventory_repository.create_inventory_item(db, inventory_item)
    
    def update_inventory(self, db: Session, item_id: int, quantity: int) -> Optional[InventoryItem]:
        return self.inventory_repository.update_quantity(db, item_id, quantity)