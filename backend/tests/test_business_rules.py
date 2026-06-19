"""Business logic requirement tests."""


def test_product_sku_must_be_unique(client):
    payload = {"sku": "UNIQUE-01", "name": "Widget", "price": "10.00", "quantity_in_stock": 5}
    first = client.post("/products", json=payload)
    second = client.post("/products", json={**payload, "name": "Another Widget"})

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error_code"] == "duplicate_sku"


def test_customer_email_must_be_unique(client):
    payload = {"full_name": "User One", "email": "unique@example.com", "phone": "111"}
    first = client.post("/customers", json=payload)
    second = client.post("/customers", json={**payload, "full_name": "User Two", "phone": "222"})

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["error_code"] == "duplicate_email"


def test_product_quantity_cannot_be_negative_on_create(client):
    response = client.post(
        "/products",
        json={"sku": "NEG-01", "name": "Negative", "price": "10.00", "quantity_in_stock": -1},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


def test_product_quantity_cannot_be_negative_on_update(client):
    product = client.post(
        "/products",
        json={"sku": "NEG-02", "name": "Widget", "price": "10.00", "quantity_in_stock": 5},
    ).json()

    response = client.put(f"/products/{product['id']}", json={"quantity_in_stock": -5})

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


def test_order_rejected_when_inventory_insufficient(client, sample_customer):
    product = client.post(
        "/products",
        json={"sku": "LOW-01", "name": "Low Stock", "price": "10.00", "quantity_in_stock": 2},
    ).json()

    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": product["id"], "quantity": 5}],
        },
    )

    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_order_rejected_when_duplicate_lines_exceed_stock(client, sample_customer):
    product = client.post(
        "/products",
        json={"sku": "LOW-02", "name": "Low Stock", "price": "10.00", "quantity_in_stock": 5},
    ).json()

    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [
                {"product_id": product["id"], "quantity": 3},
                {"product_id": product["id"], "quantity": 3},
            ],
        },
    )

    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]


def test_creating_order_reduces_available_stock(client, sample_customer):
    product = client.post(
        "/products",
        json={"sku": "STOCK-01", "name": "Stock Test", "price": "10.00", "quantity_in_stock": 20},
    ).json()

    order = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": product["id"], "quantity": 7}],
        },
    )

    assert order.status_code == 201
    updated = client.get(f"/products/{product['id']}").json()
    assert updated["quantity_in_stock"] == 13


def test_total_order_amount_calculated_by_backend(client, sample_customer):
    product_a = client.post(
        "/products",
        json={"sku": "CALC-A", "name": "A", "price": "12.50", "quantity_in_stock": 10},
    ).json()
    product_b = client.post(
        "/products",
        json={"sku": "CALC-B", "name": "B", "price": "7.25", "quantity_in_stock": 10},
    ).json()

    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [
                {"product_id": product_a["id"], "quantity": 2},
                {"product_id": product_b["id"], "quantity": 4},
            ],
        },
    )

    assert response.status_code == 201
    assert response.json()["total_amount"] == "54.00"


def test_client_cannot_set_total_amount(client, sample_customer, sample_product):
    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "total_amount": "1.00",
            "items": [{"product_id": sample_product["id"], "quantity": 1}],
        },
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


def test_invalid_request_data_returns_422(client):
    response = client.post(
        "/products",
        json={"sku": "", "name": "", "price": "-5.00"},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"


def test_not_found_resources_return_404(client):
    assert client.get("/products/999").status_code == 404
    assert client.get("/customers/999").status_code == 404
    assert client.get("/orders/999").status_code == 404


def test_invalid_email_returns_422(client):
    response = client.post(
        "/customers",
        json={"full_name": "Bad Email", "email": "not-an-email", "phone": "123"},
    )

    assert response.status_code == 422
    assert response.json()["error_code"] == "validation_error"
