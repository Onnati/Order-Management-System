from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.http_errors import APIError
from app.models import Customer, Order
from app.schemas import CustomerCreate, CustomerResponse, MessageResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


def _to_customer_response(customer: Customer) -> CustomerResponse:
    return CustomerResponse(
        id=customer.id,
        full_name=customer.name,
        email=customer.email,
        phone=customer.phone,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )


@router.get("", response_model=list[CustomerResponse])
def list_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = db.query(Customer).offset(skip).limit(limit).all()
    return [_to_customer_response(customer) for customer in customers]


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return _to_customer_response(customer)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.email == payload.email).first():
        raise APIError(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists",
            error_code="duplicate_email",
        )

    customer = Customer(
        name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return _to_customer_response(customer)


@router.delete("/{customer_id}", response_model=MessageResponse)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    if db.query(Order).filter(Order.customer_id == customer_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete customer with existing orders",
        )

    db.delete(customer)
    db.commit()
    return MessageResponse(message="Customer deleted successfully")
