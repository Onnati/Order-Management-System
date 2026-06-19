"""Order management API tests."""


def test_create_order(client, sample_product, sample_customer):
    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": sample_product["id"], "quantity": 2}],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == sample_customer["id"]
    assert data["total_amount"] == "50.00"
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == sample_product["id"]
    assert data["items"][0]["quantity"] == 2
    assert data["status"] == "pending"
    assert "order_number" in data


def test_create_order_multiple_products(client, sample_customer):
    product_a = client.post(
        "/products",
        json={"sku": "MULTI-A", "name": "A", "price": "10.00", "quantity_in_stock": 20},
    ).json()
    product_b = client.post(
        "/products",
        json={"sku": "MULTI-B", "name": "B", "price": "15.00", "quantity_in_stock": 20},
    ).json()

    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [
                {"product_id": product_a["id"], "quantity": 3},
                {"product_id": product_b["id"], "quantity": 1},
            ],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["total_amount"] == "45.00"
    assert len(data["items"]) == 2


def test_create_order_customer_not_found(client, sample_product):
    response = client.post(
        "/orders",
        json={
            "customer_id": 999,
            "items": [{"product_id": sample_product["id"], "quantity": 1}],
        },
    )

    assert response.status_code == 404


def test_create_order_product_not_found(client, sample_customer):
    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": 999, "quantity": 1}],
        },
    )

    assert response.status_code == 404


def test_create_order_insufficient_stock(client, sample_customer):
    product = client.post(
        "/products",
        json={"sku": "LOW-STOCK", "name": "Low", "price": "5.00", "quantity_in_stock": 1},
    ).json()

    response = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": product["id"], "quantity": 5}],
        },
    )

    assert response.status_code == 400


def test_create_order_deducts_inventory(client, sample_product, sample_customer):
    client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": sample_product["id"], "quantity": 10}],
        },
    )

    product = client.get(f"/products/{sample_product['id']}").json()
    assert product["quantity_in_stock"] == 40


def test_list_orders(client, sample_product, sample_customer):
    client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": sample_product["id"], "quantity": 1}],
        },
    )

    response = client.get("/orders")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_id"] == sample_customer["id"]


def test_get_order_by_id(client, sample_product, sample_customer):
    created = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": sample_product["id"], "quantity": 2}],
        },
    ).json()

    response = client.get(f"/orders/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["total_amount"] == "50.00"
    assert data["items"][0]["quantity"] == 2


def test_get_order_not_found(client):
    response = client.get("/orders/999")
    assert response.status_code == 404


def test_cancel_order(client, sample_product, sample_customer):
    created = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": sample_product["id"], "quantity": 5}],
        },
    ).json()

    response = client.delete(f"/orders/{created['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Order cancelled and inventory restored"

    order = client.get(f"/orders/{created['id']}").json()
    assert order["status"] == "cancelled"

    product = client.get(f"/products/{sample_product['id']}").json()
    assert product["quantity_in_stock"] == 50


def test_cancel_order_already_cancelled(client, sample_product, sample_customer):
    created = client.post(
        "/orders",
        json={
            "customer_id": sample_customer["id"],
            "items": [{"product_id": sample_product["id"], "quantity": 1}],
        },
    ).json()

    client.delete(f"/orders/{created['id']}")
    response = client.delete(f"/orders/{created['id']}")

    assert response.status_code == 400
