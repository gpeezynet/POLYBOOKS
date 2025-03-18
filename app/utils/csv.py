import pandas as pd
import io
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.models.inventory import Product, InventoryItem
from app.models.transaction import Transaction, TransactionItem

class CSVUtil:
    def import_products(self, db: Session, file_content: bytes) -> Dict[str, Any]:
        """Import products from CSV file"""
        try:
            # Read CSV content
            df = pd.read_csv(io.BytesIO(file_content))
            
            # Validate required columns
            required_columns = ['sku', 'name', 'unit_price', 'cost_price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {
                    "success": False,
                    "message": f"Missing required columns: {', '.join(missing_columns)}"
                }
            
            # Process each row
            products_added = 0
            products_updated = 0
            errors = []
            
            for _, row in df.iterrows():
                try:
                    # Check if product exists
                    existing_product = db.query(Product).filter(
                        Product.sku == row['sku']
                    ).first()
                    
                    product_data = {
                        "sku": row['sku'],
                        "name": row['name'],
                        "description": row.get('description', ''),
                        "category": row.get('category', 'Uncategorized'),
                        "unit_price": float(row['unit_price']),
                        "cost_price": float(row['cost_price'])
                    }
                    
                    if existing_product:
                        # Update existing product
                        for key, value in product_data.items():
                            setattr(existing_product, key, value)
                        products_updated += 1
                    else:
                        # Create new product
                        new_product = Product(**product_data)
                        db.add(new_product)
                        products_added += 1
                
                except Exception as e:
                    errors.append(f"Error processing row {row['sku']}: {str(e)}")
            
            db.commit()
            
            return {
                "success": True,
                "products_added": products_added,
                "products_updated": products_updated,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to import CSV: {str(e)}"
            }
    
    def export_products(self, db: Session) -> bytes:
        """Export products to CSV file"""
        products = db.query(Product).all()
        
        data = []
        for product in products:
            data.append({
                "id": product.id,
                "sku": product.sku,
                "name": product.name,
                "description": product.description,
                "category": product.category,
                "unit_price": product.unit_price,
                "cost_price": product.cost_price,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            })
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        output = io.BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()
    
    def export_inventory(self, db: Session) -> bytes:
        """Export inventory to CSV file"""
        # Join inventory with products
        inventory_items = db.query(InventoryItem, Product).join(
            Product, InventoryItem.product_id == Product.id
        ).all()
        
        data = []
        for item, product in inventory_items:
            data.append({
                "product_id": product.id,
                "sku": product.sku,
                "name": product.name,
                "quantity": item.quantity,
                "location": item.location,
                "status": item.status,
                "last_count_date": item.last_count_date
            })
        
        df = pd.DataFrame(data)
        
        # Convert to CSV
        output = io.BytesIO()
        df.to_csv(output, index=False)
        return output.getvalue()