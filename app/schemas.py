from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: str = "customer"


class UserRead(UserBase):
    id: int
    role: str
    is_active: bool
    wallet_balance: Decimal
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ProductBase(BaseModel):
    name: str
    sku: str
    category: str
    description: str = ""
    price: Decimal


class ProductCreate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1


class OrderCreate(BaseModel):
    notes: str = ""
    items: list[OrderItemCreate]


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    unit_price: Decimal
    model_config = ConfigDict(from_attributes=True)


class OrderRead(BaseModel):
    id: int
    user_id: int
    total_amount: Decimal
    status: str
    notes: str
    items: list[OrderItemRead]
    model_config = ConfigDict(from_attributes=True)


class WalletTopUp(BaseModel):
    amount: Decimal = Field(..., gt=0)


class WalletTransactionRead(BaseModel):
    id: int
    type: str
    amount: Decimal
    description: str
    created_at: str
    model_config = ConfigDict(from_attributes=True)


class WalletSummary(BaseModel):
    user_id: int
    wallet_balance: Decimal
    recent_transactions: list[WalletTransactionRead]


class DebtSettlement(BaseModel):
    amount: Decimal = Field(..., gt=0)


class DebtRead(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    remaining_amount: Decimal
    status: str
    notes: str
    created_at: str
    model_config = ConfigDict(from_attributes=True)


class DashboardSummary(BaseModel):
    total_users: int
    total_orders: int
    total_sales: Decimal
    outstanding_debt: Decimal
    available_wallet_value: Decimal
