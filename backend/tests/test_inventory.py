def test_low_stock_inventory(client):
    client.post(
        "/products",
        json={"sku": "LOW-STOCK-1", "name": "Low Item", "price": "5.00", "quantity_in_stock": 3},
    )

    response = client.get("/inventory/low-stock")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    item = data[0]
    assert "product" in item
    assert item["product"]["sku"] == "LOW-STOCK-1"
    assert item["product"]["name"] == "Low Item"
    assert "quantity_in_stock" not in item["product"]
