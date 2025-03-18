import sys
import os
import random
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.user import User, Role
from app.models.inventory import Product, InventoryItem
from app.models.transaction import Transaction, TransactionItem, Customer, Vendor
from app.services.authentication import AuthService

def seed_data():
    print("Seeding database with sample data...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed roles
        roles = {
            "admin": "Administrator with full access",
            "manager": "Manager with access to most features",
            "clerk": "Inventory clerk with limited access"
        }
        
        for role_name, description in roles.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=description)
                db.add(role)
        
        db.commit()
        
        # Get roles
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        manager_role = db.query(Role).filter(Role.name == "manager").first()
        clerk_role = db.query(Role).filter(Role.name == "clerk").first()
        
        # Seed users
        auth_service = AuthService()
        
        users = [
            {
                "username": "admin",
                "email": "admin@example.com",
                "full_name": "Admin User",
                "password": "Admin123!",
                "roles": [admin_role]
            },
            {
                "username": "manager",
                "email": "manager@example.com",
                "full_name": "Manager User",
                "password": "Manager123!",
                "roles": [manager_role]
            },
            {
                "username": "clerk",
                "email": "clerk@example.com",
                "full_name": "Clerk User",
                "password": "Clerk123!",
                "roles": [clerk_role]
            }
        ]
        
        for user_data in users:
            existing_user = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing_user:
                roles = user_data.pop("roles")
                password = user_data.pop("password")
                user = User(
                    **user_data,
                    hashed_password=auth_service.get_password_hash(password),
                    is_active=True
                )
                user.roles = roles
                db.add(user)
        
        db.commit()
        
        # Seed products
        products = [
            {
                "sku": "PROD001",
                "name": "Office Chair",
                "description": "Ergonomic office chair with lumbar support",
                "category": "Furniture",
                "unit_price": 199.99,
                "cost_price": 120.00
            },
            {
                "sku": "PROD002",
                "name": "Desk Lamp",
                "description": "LED desk lamp with adjustable brightness",
                "category": "Office Supplies",
                "unit_price": 49.99,
                "cost_price": 25.00
            },
            {
                "sku": "PROD003",
                "name": "Notebook",
                "description": "Hardcover notebook, 100 pages",
                "category": "Stationery",
                "unit_price": 9.99,
                "cost_price": 3.50
            },
            {
                "sku": "PROD004",
                "name": "Laptop",
                "description": "15-inch laptop with 16GB RAM",
                "category": "Electronics",
                "unit_price": 999.99,
                "cost_price": 750.00
            },
            {
                "sku": "PROD005",
                "name": "Headphones",
                "description": "Noise-cancelling wireless headphones",
                "category": "Electronics",
                "unit_price": 149.99,
                "cost_price": 80.00
            }
        ]
        
        db_products = []
        for product_data in products:
            existing_product = db.query(Product).filter(Product.sku == product_data["sku"]).first()
            if not existing_product:
                product = Product(**product_data)
                db.add(product)
                db_products.append(product)
            else:
                db_products.append(existing_product)
        
        db.commit()
        
        # Seed inventory
        for product in db_products:
            # Check if inventory exists
            existing_inventory = db.query(InventoryItem).filter(InventoryItem.product_id == product.id).first()
            if not existing_inventory:
                inventory = InventoryItem(
                    product_id=product.id,
                    quantity=random.randint(10, 100),
                    location="Main Warehouse",
                    last_count_date=datetime.utcnow() - timedelta(days=random.randint(0, 60)),
                    status="available"
                )
                db.add(inventory)
        
        db.commit()
        
        # Seed customers
        customers = [
            {
                "name": "Acme Corp",
                "email": "contact@acme.com",
                "phone": "555-1234",
                "address": "123 Main St, City",
                "balance": 0.0,
                "is_active": True
            },
            {
                "name": "XYZ Industries",
                "email": "info@xyz.com",
                "phone": "555-5678",
                "address": "456 Oak Ave, Town",
                "balance": 0.0,
                "is_active": True
            },
            {
                "name": "ABC Company",
                "email": "hello@abc.com",
                "phone": "555-9012",
                "address": "789 Pine Rd, Village",
                "balance": 0.0,
                "is_active": True
            }
        ]
        
        db_customers = []
        for customer_data in customers:
            existing_customer = db.query(Customer).filter(Customer.name == customer_data["name"]).first()
            if not existing_customer:
                customer = Customer(**customer_data)
                db.add(customer)
                db_customers.append(customer)
            else:
                db_customers.append(existing_customer)
        
        db.commit()
        
        # Seed vendors
        vendors = [
            {
                "name": "Supplier Inc",
                "email": "orders@supplier.com",
                "phone": "555-2468",
                "address": "321 Elm St, City",
                "balance": 0.0,
                "is_active": True
            },
            {
                "name": "Wholesale Co",
                "email": "sales@wholesale.com",
                "phone": "555-1357",
                "address": "654 Maple Ave, Town",
                "balance": 0.0,
                "is_active": True
            }
        ]
        
        db_vendors = []
        for vendor_data in vendors:
            existing_vendor = db.query(Vendor).filter(Vendor.name == vendor_data["name"]).first()
            if not existing_vendor:
                vendor = Vendor(**vendor_data)
                db.add(vendor)
                db_vendors.append(vendor)
            else:
                db_vendors.append(existing_vendor)
        
        db.commit()
        
        # Seed transactions
        # Create a few sales
        for i in range(5):
            customer = random.choice(db_customers)
            transaction_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            transaction = Transaction(
                transaction_date=transaction_date,
                transaction_type="sale",
                reference_number=f"SALE{1000 + i}",
                customer_id=customer.id,
                total_amount=0,
                status="completed",
                notes="Sample sale transaction"
            )
            db.add(transaction)
            db.flush()
            
            # Add 1-3 products to the transaction
            total_amount = 0
            for _ in range(random.randint(1, 3)):
                product = random.choice(db_products)
                quantity = random.randint(1, 5)
                
                transaction_item = TransactionItem(
                    transaction_id=transaction.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.unit_price,
                    total_price=quantity * product.unit_price
                )
                total_amount += quantity * product.unit_price
                db.add(transaction_item)
            
            transaction.total_amount = total_amount
        
        # Create a few purchases
        for i in range(3):
            vendor = random.choice(db_vendors)
            transaction_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            transaction = Transaction(
                transaction_date=transaction_date,
                transaction_type="purchase",
                reference_number=f"PURCH{1000 + i}",
                vendor_id=vendor.id,
                total_amount=0,
                status="completed",
                notes="Sample purchase transaction"
            )
            db.add(transaction)
            db.flush()
            
            # Add 1-3 products to the transaction
            total_amount = 0
            for _ in range(random.randint(1, 3)):
                product = random.choice(db_products)
                quantity = random.randint(5, 20)
                
                transaction_item = TransactionItem(
                    transaction_id=transaction.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.cost_price,
                    total_price=quantity * product.cost_price
                )
                total_amount += quantity * product.cost_price
                db.add(transaction_item)
            
            transaction.total_amount = total_amount
        
        db.commit()
        
        print("Database seeded successfully!")
    
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()