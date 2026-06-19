from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.http_errors import APIError
from app.models import Inventory, Product
from app.schemas import MessageResponse, ProductCreate, ProductResponse, ProductUpdate

router = APIRouter(prefix="/products", tags=["Products"])


def _to_product_response(product: Product) -> ProductResponse:
    quantity = product.inventory.quantity_on_hand if product.inventory else 0
    return ProductResponse(
        id=product.id,
        sku=product.sku,
        name=product.name,
        description=product.description,
        price=product.price,
        quantity_in_stock=quantity,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


@router.get("", response_model=list[ProductResponse])
def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .options(joinedload(Product.inventory))
        .offset(skip)
        .limit(limit)
        .all()
    )
    return [_to_product_response(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.inventory))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return _to_product_response(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    if db.query(Product).filter(Product.sku == payload.sku).first():
        raise APIError(
            status_code=status.HTTP_409_CONFLICT,
            detail="SKU already exists",
            error_code="duplicate_sku",
        )

    product = Product(
        sku=payload.sku,
        name=payload.name,
        description=payload.description,
        price=payload.price,
    )
    db.add(product)
    db.flush()

    inventory = Inventory(
        product_id=product.id,
        quantity_on_hand=payload.quantity_in_stock,
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)
    return _to_product_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.inventory))
        .filter(Product.id == product_id)
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    if payload.sku and payload.sku != product.sku:
        if db.query(Product).filter(Product.sku == payload.sku).first():
            raise APIError(
                status_code=status.HTTP_409_CONFLICT,
                detail="SKU already exists",
                error_code="duplicate_sku",
            )
        product.sku = payload.sku

    if payload.name is not None:
        product.name = payload.name
    if payload.description is not None:
        product.description = payload.description
    if payload.price is not None:
        product.price = payload.price

    if payload.quantity_in_stock is not None:
        if product.inventory:
            product.inventory.quantity_on_hand = payload.quantity_in_stock
        else:
            db.add(
                Inventory(
                    product_id=product.id,
                    quantity_on_hand=payload.quantity_in_stock,
                )
            )

    db.commit()
    db.refresh(product)
    return _to_product_response(product)


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()
    return MessageResponse(message="Product deleted successfully")
