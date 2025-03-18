# Import repositories for easy access
from app.repositories.base import BaseRepository
from app.repositories.inventory import ProductRepository, InventoryRepository
from app.repositories.transaction import TransactionRepository, CustomerRepository, VendorRepository
from app.repositories.user import UserRepository, RoleRepository