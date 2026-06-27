from decimal import Decimal


def product(client, position=0):
    return client.get("/api/produtos").json()[position]


def create_order(client, items=None):
    chosen = product(client)
    payload = items or [{"produto_id": chosen["id"], "quantidade": 2}]
    return client.post("/api/pedidos", json={"itens": payload})


def test_creates_order_and_calculates_total_on_server(client):
    chosen = product(client)

    response = create_order(
        client,
        [{"produto_id": chosen["id"], "quantidade": 2}],
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "recebido"
    assert Decimal(body["total"]) == Decimal(chosen["preco"]) * 2
    assert body["itens"][0]["nome_produto"] == chosen["nome"]
    assert body["itens"][0]["quantidade"] == 2


def test_consolidates_repeated_products(client):
    chosen = product(client)

    response = create_order(
        client,
        [
            {"produto_id": chosen["id"], "quantidade": 1},
            {"produto_id": chosen["id"], "quantidade": 2},
        ],
    )

    assert response.status_code == 201
    assert len(response.json()["itens"]) == 1
    assert response.json()["itens"][0]["quantidade"] == 3


def test_rejects_unknown_product(client):
    response = create_order(
        client,
        [{"produto_id": 99999, "quantidade": 1}],
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Produto 99999 não encontrado."


def test_rejects_empty_order(client):
    response = client.post("/api/pedidos", json={"itens": []})

    assert response.status_code == 422


def test_rejects_non_positive_quantity(client):
    chosen = product(client)

    response = create_order(
        client,
        [{"produto_id": chosen["id"], "quantidade": 0}],
    )

    assert response.status_code == 422


def test_lists_and_gets_created_order(client):
    created = create_order(client).json()

    listing = client.get("/api/pedidos")
    found = client.get(f"/api/pedidos/{created['id']}")

    assert listing.status_code == 200
    assert [order["id"] for order in listing.json()] == [created["id"]]
    assert found.status_code == 200
    assert found.json() == created


def test_returns_404_for_unknown_order(client):
    response = client.get("/api/pedidos/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Pedido 99999 não encontrado."
