def test_create_product(client):
    response = client.post(
        "/products",
        json={
            "sku": "WIDGET-01",
            "name": "Blue Widget",
            "price": "29.99",
            "quantity_in_stock": 100,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["sku"] == "WIDGET-01"
    assert data["name"] == "Blue Widget"
    assert data["price"] == "29.99"
    assert data["quantity_in_stock"] == 100
    assert "id" in data


def test_list_products(client):
    client.post(
        "/products",
        json={"sku": "A-001", "name": "Product A", "price": "10.00", "quantity_in_stock": 5},
    )
    client.post(
        "/products",
        json={"sku": "B-002", "name": "Product B", "price": "20.00", "quantity_in_stock": 15},
    )

    response = client.get("/products")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["quantity_in_stock"] in (5, 15)


def test_get_product_by_id(client):
    created = client.post(
        "/products",
        json={"sku": "GET-01", "name": "Get Me", "price": "9.99", "quantity_in_stock": 42},
    ).json()

    response = client.get(f"/products/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["name"] == "Get Me"
    assert data["quantity_in_stock"] == 42


def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404


def test_update_product(client):
    created = client.post(
        "/products",
        json={"sku": "UPD-01", "name": "Old Name", "price": "5.00", "quantity_in_stock": 10},
    ).json()

    response = client.put(
        f"/products/{created['id']}",
        json={
            "name": "New Name",
            "price": "7.50",
            "quantity_in_stock": 25,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["price"] == "7.50"
    assert data["quantity_in_stock"] == 25
    assert data["sku"] == "UPD-01"


def test_delete_product(client):
    created = client.post(
        "/products",
        json={"sku": "DEL-01", "name": "Delete Me", "price": "1.00", "quantity_in_stock": 3},
    ).json()

    response = client.delete(f"/products/{created['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Product deleted successfully"
    assert client.get(f"/products/{created['id']}").status_code == 404


def test_create_product_duplicate_sku(client):
    payload = {"sku": "DUP-01", "name": "First", "price": "1.00", "quantity_in_stock": 1}
    client.post("/products", json=payload)

    response = client.post("/products", json={**payload, "name": "Second"})

    assert response.status_code == 409
