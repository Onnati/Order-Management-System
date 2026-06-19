from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Inventory, Product
from app.schemas import (
    InventoryAdjust,
    InventoryResponse,
    InventoryUpdate,
    MessageResponse,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryResponse])
def list_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return (
        db.query(Inventory)
        .options(joinedload(Inventory.product))
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/low-stock", response_model=list[InventoryResponse])
def list_low_stock(db: Session = Depends(get_db)):
    return (
        db.query(Inventory)
        .options(joinedload(Inventory.product))
        .filter(Inventory.quantity_on_hand <= Inventory.reorder_level)
        .all()
    )


@router.get("/product/{product_id}", response_model=InventoryResponse)
def get_inventory_by_product(product_id: int, db: Session = Depends(get_db)):
    inventory = (
        db.query(Inventory)
        .options(joinedload(Inventory.product))
        .filter(Inventory.product_id == product_id)
        .first()
    )
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")
    return inventory


@router.put("/product/{product_id}", response_model=InventoryResponse)
def update_inventory(product_id: int, payload: InventoryUpdate, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")

    if payload.quantity_on_hand is not None:
        inventory.quantity_on_hand = payload.quantity_on_hand
    if payload.reorder_level is not None:
        inventory.reorder_level = payload.reorder_level

    db.commit()
    db.refresh(inventory)
    return inventory


@router.post("/product/{product_id}/adjust", response_model=InventoryResponse)
def adjust_inventory(product_id: int, payload: InventoryAdjust, db: Session = Depends(get_db)):
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inventory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory not found")

    new_quantity = inventory.quantity_on_hand + payload.adjustment
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient inventory for this adjustment",
        )

    inventory.quantity_on_hand = new_quantity
    db.commit()
    db.refresh(inventory)
    return inventory
