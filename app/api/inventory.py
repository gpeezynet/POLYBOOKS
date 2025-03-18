from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.inventory import Product, ProductCreate, ProductUpdate, InventoryItem, InventoryItemCreate
from app.services.inventory import InventoryService
from app.api.dependencies import get_current_active_user

router = APIRouter(prefix="/inventory", tags=["inventory"])
inventory_service = InventoryService()

@router.get("/products/", response_model=List[Product])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    products = inventory_service.get_products(db, skip=skip, limit=limit)
    return products

@router.post("/products/", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return inventory_service.create_product(db, product)

@router.get("/products/{product_id}", response_model=Product)
async def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = inventory_service.get_product(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    updated_product = inventory_service.update_product(db, product_id, product)
    if updated_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/products/{product_id}", response_model=bool)
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = inventory_service.delete_product(db, product_id)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return True

@router.post("/items/", response_model=InventoryItem)
async def add_inventory(
    inventory_item: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = inventory_service.add_inventory(db, inventory_item)
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return result

@router.get("/count/", response_model=List[InventoryItem])
async def get_inventory_count_list(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return inventory_service.generate_daily_count_list(db, days)