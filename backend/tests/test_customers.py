def test_create_customer(client):
    response = client.post(
        "/customers",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1-555-0100",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["full_name"] == "Jane Doe"
    assert data["email"] == "jane@example.com"
    assert data["phone"] == "+1-555-0100"
    assert "id" in data


def test_create_customer_missing_phone(client):
    response = client.post(
        "/customers",
        json={
            "full_name": "Jane Doe",
            "email": "jane@example.com",
        },
    )

    assert response.status_code == 422


def test_list_customers(client):
    client.post(
        "/customers",
        json={"full_name": "Alice", "email": "alice@example.com", "phone": "111"},
    )
    client.post(
        "/customers",
        json={"full_name": "Bob", "email": "bob@example.com", "phone": "222"},
    )

    response = client.get("/customers")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {customer["full_name"] for customer in data}
    assert names == {"Alice", "Bob"}


def test_get_customer_by_id(client):
    created = client.post(
        "/customers",
        json={"full_name": "Get Me", "email": "get@example.com", "phone": "333"},
    ).json()

    response = client.get(f"/customers/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["full_name"] == "Get Me"
    assert data["email"] == "get@example.com"


def test_get_customer_not_found(client):
    response = client.get("/customers/999")
    assert response.status_code == 404


def test_delete_customer(client):
    created = client.post(
        "/customers",
        json={"full_name": "Delete Me", "email": "del@example.com", "phone": "444"},
    ).json()

    response = client.delete(f"/customers/{created['id']}")

    assert response.status_code == 200
    assert response.json()["message"] == "Customer deleted successfully"
    assert client.get(f"/customers/{created['id']}").status_code == 404


def test_create_customer_duplicate_email(client):
    payload = {"full_name": "First", "email": "dup@example.com", "phone": "555"}
    client.post("/customers", json=payload)

    response = client.post(
        "/customers",
        json={"full_name": "Second", "email": "dup@example.com", "phone": "666"},
    )

    assert response.status_code == 409
