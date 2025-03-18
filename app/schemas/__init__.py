# Import schemas for easy access
from app.schemas.user import User, UserCreate, UserUpdate, Token, TokenData
from app.schemas.inventory import Product, ProductCreate, ProductUpdate, InventoryItem, InventoryItemCreate
from app.schemas.transaction import Transaction, TransactionCreate, TransactionItem, TransactionItemCreate
from app.schemas.report import NaturalLanguageQuery, QueryResult