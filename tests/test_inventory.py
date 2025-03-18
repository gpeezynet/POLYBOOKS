import pytest
from datetime import datetime, timedelta

from app.models.inventory import Product, InventoryItem
from app.schemas.inventory import ProductCreate, InventoryItemCreate
from app.services.inventory import InventoryService

def test_create_product(db):
    # Create service
    service = InventoryService()
    
    # Create test product
    product = ProductCreate(
        sku="TEST001",
        name="Test Product",
        description="Test Description",
        category="Test Category",
        unit_price=10.0,
        cost_price=5.0
    )
    
    # Add the product
    db_product = service.create_product(db, product)
    
    # Check the product was created with the correct values
    assert db_product.id is not None
    assert db_product.sku == "TEST001"
    assert db_product.name == "Test Product"
    assert db_product.unit_price == 10.0
    assert db_product.cost_price == 5.0

def test_get_product(db):
    # Create service
    service = InventoryService()
    
    # Create test product
    product = ProductCreate(
        sku="TEST002",
        name="Test Product 2",
        description="Test Description 2",
        category="Test Category",
        unit_price=20.0,
        cost_price=10.0
    )
    
    # Add the product
    db_product = service.create_product(db, product)
    
    # Get the product
    retrieved_product = service.get_product(db, db_product.id)
    
    # Check the product was retrieved correctly
    assert retrieved_product is not None
    assert retrieved_product.id == db_product.id
    assert retrieved_product.sku == "TEST002"

def test_add_inventory(db):
    # Create service
    service = InventoryService()
    
    # Create test product
    product = ProductCreate(
        sku="TEST003",
        name="Test Product 3",
        description="Test Description 3",
        category="Test Category",
        unit_price=30.0,
        cost_price=15.0
    )
    
    # Add the product
    db_product = service.create_product(db, product)
    
    # Add inventory
    inventory_item = InventoryItemCreate(
        product_id=db_product.id,
        quantity=10,
        location="Warehouse A",
        status="available"
    )
    
    db_inventory = service.add_inventory(db, inventory_item)
    
    # Check the inventory was created correctly
    assert db_inventory is not None
    assert db_inventory.product_id == db_product.id
    assert db_inventory.quantity == 10
    assert db_inventory.location == "Warehouse A"
    assert db_inventory.status == "available"