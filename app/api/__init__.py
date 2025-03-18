# Import routers for easy access in main.py
from app.api.authentication import router as authentication_router
from app.api.inventory import router as inventory_router
from app.api.transaction import router as transaction_router
from app.api.report import router as report_router