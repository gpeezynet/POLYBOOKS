import openai
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime, timedelta
import os

from app.models.inventory import Product, InventoryItem
from app.models.transaction import Transaction, TransactionItem
from app.schemas.report import NaturalLanguageQuery, QueryResult

class ReportGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key
    
    def generate_inventory_report(self, db: Session) -> Dict[str, Any]:
        """Generate a comprehensive inventory report"""
        # Fetch all products with their inventory levels
        products = db.query(Product).all()
        
        inventory_data = []
        for product in products:
            total_quantity = sum(item.quantity for item in product.inventory_items)
            inventory_value = total_quantity * product.cost_price
            
            inventory_data.append({
                "sku": product.sku,
                "name": product.name,
                "category": product.category,
                "quantity": total_quantity,
                "unit_cost": product.cost_price,
                "total_value": inventory_value
            })
        
        df = pd.DataFrame(inventory_data)
        
        # Calculate summary statistics
        total_value = df["total_value"].sum() if not df.empty else 0
        low_stock_items = df[df["quantity"] < 10].shape[0] if not df.empty else 0
        zero_stock_items = df[df["quantity"] == 0].shape[0] if not df.empty else 0
        
        summary = {
            "report_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "total_products": len(products),
            "total_inventory_value": total_value,
            "low_stock_items": low_stock_items,
            "zero_stock_items": zero_stock_items
        }
        
        return {
            "summary": summary,
            "details": inventory_data
        }
    
    def generate_sales_report(self, db: Session, start_date=None, end_date=None) -> Dict[str, Any]:
        """Generate a sales report for a given period"""
        if not start_date:
            start_date = datetime.utcnow() - timedelta(days=30)
        if not end_date:
            end_date = datetime.utcnow()
        
        # Get sales transactions for the period
        sales = db.query(Transaction).filter(
            Transaction.transaction_type == "sale",
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ).all()
        
        sales_data = []
        for sale in sales:
            for item in sale.items:
                sales_data.append({
                    "date": sale.transaction_date,
                    "reference": sale.reference_number,
                    "product_id": item.product_id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price
                })
        
        df = pd.DataFrame(sales_data)
        
        # Calculate summary statistics
        total_sales = df["total_price"].sum() if not df.empty else 0
        total_items_sold = df["quantity"].sum() if not df.empty else 0
        
        # Group by product to find top selling items
        if not df.empty:
            product_sales = df.groupby("product_name").agg({
                "quantity": "sum",
                "total_price": "sum"
            }).reset_index().sort_values("total_price", ascending=False)
            
            top_products = product_sales.head(5).to_dict("records")
        else:
            top_products = []
        
        summary = {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "total_sales": total_sales,
            "total_items_sold": total_items_sold,
            "transaction_count": len(sales),
            "top_products": top_products
        }
        
        return {
            "summary": summary,
            "details": sales_data
        }
    
    def process_natural_language_query(self, db: Session, query: str) -> Dict[str, Any]:
        """Process natural language queries using OpenAI API"""
        # Create a system message that explains the context and available data
        system_message = """
        You are an AI assistant for PolyBooks, an accounting and inventory management system.
        You can access data about products, inventory, sales, purchases, and other transactions.
        Please interpret the user's query and return the appropriate SQL query to extract the requested information.
        """
        
        # Send the query to OpenAI
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Generate a SQL query for: {query}"}
            ]
        )
        
        # Extract the SQL query from the response
        sql_query = completion.choices[0].message.content.strip()
        
        try:
            # Execute the SQL query with safety precautions
            if "drop" in sql_query.lower() or "delete" in sql_query.lower() or "update" in sql_query.lower():
                return {"error": "Query contains potentially harmful operations"}
            
            # Execute the query
            result = db.execute(sql_query)
            data = [dict(row) for row in result.fetchall()]
            
            return {
                "query": query,
                "sql": sql_query,
                "results": data
            }
        except Exception as e:
            return {
                "query": query,
                "sql": sql_query,
                "error": str(e)
            }