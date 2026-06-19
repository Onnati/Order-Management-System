# Order Management System

Inventory & Order Management backend built with **FastAPI**, **PostgreSQL**, and **Docker Compose**.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend API | Python 3.12 + FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Containers | Docker + Docker Compose |

## Project Structure

```
order-management/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI application entry point
│   │   ├── config.py        # Environment settings
│   │   ├── database.py      # DB engine & session
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   └── routers/         # API route handlers
│   ├── alembic/             # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Run with Docker

```bash
# Copy environment file
cp .env.example .env

# Start PostgreSQL + API
docker compose up --build
```

The API will be available at:

- **API**: http://localhost:8000
- **Swagger docs**: http://localhost:8000/docs
- **Health check**: http://localhost:8000/health

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products` | List all products |
| GET | `/products/{id}` | Get product by ID |
| POST | `/products` | Create product (+ initial inventory) |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |

### Customers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/customers` | List all customers |
| GET | `/customers/{id}` | Get customer by ID |
| POST | `/customers` | Create customer |
| PUT | `/customers/{id}` | Update customer |
| DELETE | `/customers/{id}` | Delete customer |

### Inventory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | List all inventory records |
| GET | `/inventory/low-stock` | Products at or below reorder level |
| GET | `/inventory/product/{id}` | Inventory for a product |
| PUT | `/inventory/product/{id}` | Update stock levels |
| POST | `/inventory/product/{id}/adjust` | Add/remove stock |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/orders` | List all orders |
| GET | `/orders/{id}` | Get order by ID |
| POST | `/orders` | Create order (deducts inventory) |
| PATCH | `/orders/{id}/status` | Update order status |
| DELETE | `/orders/{id}` | Cancel order (restores inventory) |

## Example Workflow

```bash
# 1. Create a product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{"sku":"WIDGET-01","name":"Blue Widget","price":29.99,"initial_quantity":100}'

# 2. Create a customer
curl -X POST http://localhost:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{"name":"Jane Doe","email":"jane@example.com"}'

# 3. Place an order
curl -X POST http://localhost:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"items":[{"product_id":1,"quantity":2}]}'

# 4. Check low stock
curl http://localhost:8000/api/v1/inventory/low-stock
```

## Local Development (without Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Ensure PostgreSQL is running and DATABASE_URL is set
export DATABASE_URL=postgresql://orderapp:orderapp_secret@localhost:5432/order_management
alembic upgrade head
uvicorn app.main:app --reload
```
