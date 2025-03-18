from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class TransactionItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

class TransactionItemCreate(TransactionItemBase):
    pass

class TransactionItem(TransactionItemBase):
    id: int
    total_price: float

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    transaction_type: str
    reference_number: Optional[str] = None
    customer_id: Optional[int] = None
    vendor_id: Optional[int] = None
    total_amount: float
    status: str = "pending"
    notes: Optional[str] = None

class TransactionCreate(TransactionBase):
    items: List[TransactionItemCreate]

class Transaction(TransactionBase):
    id: int
    transaction_date: datetime
    items: List[TransactionItem]

    class Config:
        orm_mode = True

class CustomerBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    balance: float = 0.0
    is_active: bool = True

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int

    class Config:
        orm_mode = True

class VendorBase(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    balance: float = 0.0
    is_active: bool = True

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int

    class Config:
        orm_mode = True