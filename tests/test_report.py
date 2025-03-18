import pytest
from datetime import datetime, timedelta
import pandas as pd

from app.models.inventory import Product, InventoryItem
from app.models.transaction import Transaction, TransactionItem
from app.schemas.inventory import ProductCreate
from app.services.inventory import InventoryService
from app.services.report import ReportGenerator

@pytest.fixture
def setup_test_data(db):
    # Create service
    inventory_service = InventoryService()
    
    # Create test products
    products = []
    for i in range(1, 4):
        product = ProductCreate(
            sku=f"PROD00{i}",
            name=f"Product {i}",
            description=f"Description {i}",
            category="Test Category",
            unit_price=10.0 * i,
            cost_price=5.0 * i
        )
        
        db_product = inventory_service.create_product(db, product)
        products.append(db_product)
        
        # Add inventory
        inventory_item = InventoryItem(
            product_id=db_product.id,
            quantity=50 * i,
            location="Main Warehouse",
            last_count_date=datetime.utcnow(),
            status="available"
        )
        db.add(inventory_item)
    
    # Create some sale transactions
    for i in range(1, 4):
        transaction = Transaction(
            transaction_date=datetime.utcnow() - timedelta(days=i),
            transaction_type="sale",
            reference_number=f"SALE00{i}",
            total_amount=0,
            status="completed"
        )
        db.add(transaction)
        db.flush()
        
        # Add transaction items
        total = 0
        for j, product in enumerate(products):
            quantity = (i + j) % 3 + 1  # 1, 2, or 3
            item = TransactionItem(
                transaction_id=transaction.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.unit_price,
                total_price=quantity * product.unit_price
            )
            total += quantity * product.unit_price
            db.add(item)
        
        transaction.total_amount = total
    
    db.commit()
    return products

def test_generate_inventory_report(db, setup_test_data):
    # Create service
    service = ReportGenerator()
    
    # Generate report
    report = service.generate_inventory_report(db)
    
    # Check report structure
    assert "summary" in report
    assert "details" in report
    
    # Check summary values
    assert report["summary"]["total_products"] == 3
    
    # Check details
    assert len(report["details"]) == 3
    
    # Verify product details
    for product_data in report["details"]:
        assert "sku" in product_data
        assert "name" in product_data
        assert "quantity" in product_data
        assert "total_value" in product_data

def test_generate_sales_report(db, setup_test_data):
    # Create service
    service = ReportGenerator()
    
    # Generate report for the last 7 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    report = service.generate_sales_report(db, start_date, end_date)
    
    # Check report structure
    assert "summary" in report
    assert "details" in report
    
    # Check summary values
    assert report["summary"]["transaction_count"] == 3
    
    # Check details
    assert len(report["details"]) > 0
    
    # Verify transaction details
    for sale_data in report["details"]:
        assert "date" in sale_data
        assert "reference" in sale_data
        assert "product_name" in sale_data
        assert "quantity" in sale_data
        assert "total_price" in sale_data