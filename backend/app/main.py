from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.exceptions import (
    api_error_handler,
    http_exception_handler,
    integrity_error_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.http_errors import APIError
from app.routers import customers, inventory, orders, products

app = FastAPI(
    title="Order Management API",
    description="Inventory & Order Management System backend",
    version="0.1.0",
    debug=settings.debug,
)

app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(customers.router)
app.include_router(inventory.router)
app.include_router(orders.router)


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "order-management-api"}
