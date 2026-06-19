from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

STRICT_SCHEMA = ConfigDict(extra="forbid")


class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    price: Decimal = Field(..., ge=0)


class ProductCreate(ProductBase):
    model_config = STRICT_SCHEMA

    quantity_in_stock: int = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    model_config = STRICT_SCHEMA

    sku: str | None = Field(default=None, min_length=1, max_length=64)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    price: Decimal | None = Field(default=None, ge=0)
    quantity_in_stock: int | None = Field(default=None, ge=0)


class ProductSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    name: str


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    quantity_in_stock: int
    created_at: datetime
    updated_at: datetime


class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=32)


class CustomerCreate(CustomerBase):
    model_config = STRICT_SCHEMA


class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime


class InventoryBase(BaseModel):
    quantity_on_hand: int = Field(..., ge=0)
    reorder_level: int = Field(default=10, ge=0)


class InventoryUpdate(BaseModel):
    quantity_on_hand: int | None = Field(default=None, ge=0)
    reorder_level: int | None = Field(default=None, ge=0)


class InventoryAdjust(BaseModel):
    adjustment: int = Field(..., description="Positive to add stock, negative to remove")
    reason: str | None = None


class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    updated_at: datetime
    product: ProductSummaryResponse | None = None


class OrderItemCreate(BaseModel):
    model_config = STRICT_SCHEMA

    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderCreate(BaseModel):
    model_config = STRICT_SCHEMA

    customer_id: int = Field(..., gt=0, description="Customer reference")
    items: list[OrderItemCreate] = Field(
        ..., min_length=1, description="Product references with quantities"
    )


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse] = []


class MessageResponse(BaseModel):
    message: str
