import uuid
from collections import defaultdict
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Customer, Inventory, Order, OrderItem, OrderStatus, Product
from app.schemas import MessageResponse, OrderCreate, OrderItemResponse, OrderResponse

router = APIRouter(prefix="/orders", tags=["Orders"])


def _generate_order_number() -> str:
    return f"ORD-{uuid.uuid4().hex[:8].upper()}"


def _to_order_item_response(item: OrderItem) -> OrderItemResponse:
    return OrderItemResponse(
        id=item.id,
        product_id=item.product_id,
        quantity=item.quantity,
        unit_price=item.unit_price,
        line_total=item.line_total,
    )


def _to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        order_number=order.order_number,
        customer_id=order.customer_id,
        status=order.status.value,
        total_amount=order.total_amount,
        created_at=order.created_at,
        updated_at=order.updated_at,
        items=[_to_order_item_response(item) for item in order.items],
    )


def _aggregate_item_quantities(items) -> dict[int, int]:
    totals: dict[int, int] = defaultdict(int)
    for item in items:
        totals[item.product_id] += item.quantity
    return totals


@router.get("", response_model=list[OrderResponse])
def list_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_order_response(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _to_order_response(order)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    quantity_by_product = _aggregate_item_quantities(payload.items)
    products_by_id: dict[int, Product] = {}
    inventory_by_product: dict[int, Inventory] = {}

    for product_id, required_quantity in quantity_by_product.items():
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {product_id} not found",
            )

        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory or inventory.quantity_on_hand < required_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.sku}",
            )

        products_by_id[product_id] = product
        inventory_by_product[product_id] = inventory

    order_items: list[OrderItem] = []
    total_amount = Decimal("0.00")

    for item in payload.items:
        product = products_by_id[item.product_id]
        unit_price = Decimal(str(product.price))
        line_total = unit_price * item.quantity
        total_amount += line_total

        order_items.append(
            OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    for product_id, required_quantity in quantity_by_product.items():
        inventory_by_product[product_id].quantity_on_hand -= required_quantity

    order = Order(
        order_number=_generate_order_number(),
        customer_id=payload.customer_id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        items=order_items,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return _to_order_response(order)


@router.delete("/{order_id}", response_model=MessageResponse)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if order.status == OrderStatus.CANCELLED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order already cancelled")

    for item in order.items:
        inventory = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
        if inventory:
            inventory.quantity_on_hand += item.quantity

    order.status = OrderStatus.CANCELLED
    db.commit()
    return MessageResponse(message="Order cancelled and inventory restored")
