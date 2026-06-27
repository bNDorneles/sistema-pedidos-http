def test_lists_seeded_products(client):
    response = client.get("/api/produtos")

    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 5
    assert {"id", "nome", "descricao", "preco"} <= products[0].keys()


def test_returns_prices_as_two_decimal_strings(client):
    products = client.get("/api/produtos").json()

    assert all(product["preco"].count(".") == 1 for product in products)
    assert all(len(product["preco"].split(".")[1]) == 2 for product in products)


def test_serves_accessible_frontend(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "Mesa Rápida" in response.text
    assert 'id="cardapio"' in response.text
    assert 'aria-live="polite"' in response.text


def test_serves_frontend_assets(client):
    css = client.get("/static/styles.css")
    javascript = client.get("/static/app.js")

    assert css.status_code == 200
    assert "--color-primary" in css.text
    assert javascript.status_code == 200
    assert "/api/pedidos" in javascript.text
