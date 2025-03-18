import pytest
from datetime import datetime

from app.models.inventory import Product, InventoryItem
from app.models.transaction import Transaction, TransactionItem
from app.schemas.inventory import ProductCreate
from app.schemas.transaction import TransactionCreate, TransactionItemCreate
from app.services.inventory import InventoryService
from app.services.transaction import TransactionService

@pytest.fixture
def test_product(db):
    # Create service
    service = InventoryService()
    
    # Create test product
    product = ProductCreate(
        sku="PROD001",
        name="Test Product",
        description="Test Description",
        category="Test Category",
        unit_price=10.0,
        cost_price=5.0
    )
    
    # Add the product
    db_product = service.create_product(db, product)
    
    # Add inventory
    inventory_item = InventoryItem(
        product_id=db_product.id,
        quantity=100,
        location="Main Warehouse",
        last_count_date=datetime.utcnow(),
        status="available"
    )
    db.add(inventory_item)
    db.commit()
    
    return db_product

def test_create_sale_transaction(db, test_product):
    # Create service
    service = TransactionService()
    
    # Create transaction items
    transaction_item = TransactionItemCreate(
        product_id=test_product.id,
        quantity=5,
        unit_price=test_product.unit_price
    )
    
    # Create transaction
    transaction = TransactionCreate(
        transaction_type="sale",
        reference_number="SALE001",
        customer_id=None,
        vendor_id=None,
        total_amount=5 * test_product.unit_price,
        status="completed",
        notes="Test sale transaction",
        items=[transaction_item]
    )
    
    # Create the transaction
    db_transaction = service.create_transaction(db, transaction)
    
    # Check transaction was created correctly
    assert db_transaction is not None
    assert db_transaction.transaction_type == "sale"
    assert db_transaction.reference_number == "SALE001"
    assert db_transaction.total_amount == 5 * test_product.unit_price
    
    # Check inventory was updated
    inventory = db.query(InventoryItem).filter(InventoryItem.product_id == test_product.id).first()
    assert inventory.quantity == 95  # 100 - 5