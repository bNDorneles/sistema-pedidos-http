# Sistema de Pedidos HTTP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir uma aplicação web completa que demonstre HTTP por meio de uma API REST para pedidos de restaurante.

**Architecture:** Uma aplicação FastAPI servirá uma API JSON e arquivos estáticos. SQLAlchemy persistirá produtos, pedidos e itens no SQLite; serviços concentrarão regras de negócio e os roteadores mapearão resultados para semântica HTTP.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Pydantic, pytest, HTTPX, HTML, CSS e JavaScript.

---

## Estrutura de arquivos

- `app/main.py`: criação da aplicação, ciclo de vida, rotas e frontend.
- `app/database.py`: engine, sessão e base SQLAlchemy.
- `app/models.py`: entidades persistentes.
- `app/schemas.py`: contratos de entrada e saída da API.
- `app/services.py`: regras de criação, consulta, transição e cancelamento.
- `app/routers/products.py`: endpoints de cardápio.
- `app/routers/orders.py`: endpoints de pedidos.
- `app/static/index.html`: estrutura da interface.
- `app/static/styles.css`: identidade visual e responsividade.
- `app/static/app.js`: consumo da API e interações.
- `tests/conftest.py`: banco isolado e cliente de testes.
- `tests/test_products.py`: comportamento do cardápio.
- `tests/test_orders.py`: ciclo de vida e erros dos pedidos.
- `README.md`: entrega acadêmica completa.
- `requirements.txt`, `.gitignore`, `LICENSE`: reprodução e distribuição.

### Task 1: Base da aplicação e persistência

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `app/__init__.py`
- Create: `app/database.py`
- Create: `app/models.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Declarar dependências e ignorar artefatos**

```text
fastapi
uvicorn[standard]
sqlalchemy
pytest
httpx
```

Ignorar `.venv/`, `__pycache__/`, `.pytest_cache/`, `*.pyc` e `restaurante.db`.

- [ ] **Step 2: Escrever fixture que exige tabelas isoladas**

```python
@pytest.fixture
def db_session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

- [ ] **Step 3: Rodar o teste para verificar a falha inicial**

Run: `python -m pytest tests/conftest.py -v`

Expected: FAIL de importação porque `app.database` e `app.models` ainda não existem.

- [ ] **Step 4: Implementar banco e modelos**

Criar `Base`, engine SQLite, `SessionLocal` e `get_db`. Modelar `Product`, `Order` e `OrderItem` com relacionamentos, `Decimal` para valores e `created_at` em UTC.

- [ ] **Step 5: Confirmar carregamento da fixture**

Run: `python -m pytest tests/conftest.py -v`

Expected: processo encerra com código 0 e nenhum erro de importação.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .gitignore app tests/conftest.py
git commit -m "chore: estrutura aplicação e persistência"
```

### Task 2: Cardápio e inicialização

**Files:**
- Create: `app/schemas.py`
- Create: `app/services.py`
- Create: `app/routers/__init__.py`
- Create: `app/routers/products.py`
- Create: `app/main.py`
- Create: `tests/test_products.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Escrever teste de listagem do cardápio**

```python
def test_lists_seeded_products(client):
    response = client.get("/api/produtos")
    assert response.status_code == 200
    products = response.json()
    assert len(products) >= 5
    assert {"id", "nome", "descricao", "preco"} <= products[0].keys()
```

- [ ] **Step 2: Confirmar que o endpoint ainda não existe**

Run: `python -m pytest tests/test_products.py -v`

Expected: FAIL com status `404`.

- [ ] **Step 3: Implementar contrato, seed e endpoint**

Definir `ProductResponse`, uma lista fixa com ao menos cinco produtos e `seed_products(session)`, idempotente quando já houver registros. Expor `GET /api/produtos` com `response_model=list[ProductResponse]`.

- [ ] **Step 4: Criar a aplicação testável**

Criar `create_app()`; no lifespan, criar tabelas e executar o seed. Sobrescrever `get_db` em `tests/conftest.py` para usar a sessão isolada.

- [ ] **Step 5: Rodar o teste**

Run: `python -m pytest tests/test_products.py -v`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add app tests
git commit -m "feat: adiciona cardápio HTTP"
```

### Task 3: Criação, listagem e consulta de pedidos

**Files:**
- Modify: `app/schemas.py`
- Modify: `app/services.py`
- Create: `app/routers/orders.py`
- Modify: `app/main.py`
- Create: `tests/test_orders.py`

- [ ] **Step 1: Escrever testes de criação e total**

```python
def test_creates_order_and_calculates_total(client):
    products = client.get("/api/produtos").json()
    response = client.post("/api/pedidos", json={
        "itens": [{"produto_id": products[0]["id"], "quantidade": 2}]
    })
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "recebido"
    assert Decimal(body["total"]) == Decimal(products[0]["preco"]) * 2

def test_rejects_unknown_product(client):
    response = client.post("/api/pedidos", json={
        "itens": [{"produto_id": 99999, "quantidade": 1}]
    })
    assert response.status_code == 404
```

Também testar lista vazia, quantidade zero, consolidação de itens repetidos, listagem, consulta e pedido inexistente.

- [ ] **Step 2: Confirmar falhas dos testes**

Run: `python -m pytest tests/test_orders.py -v`

Expected: FAIL porque `/api/pedidos` ainda retorna `404`.

- [ ] **Step 3: Implementar esquemas e regras**

Criar `OrderItemCreate`, `OrderCreate`, `OrderItemResponse` e `OrderResponse`. O serviço agrupará produtos repetidos, validará todos antes de persistir, copiará o preço unitário e calculará o total com `Decimal`.

- [ ] **Step 4: Implementar endpoints**

Expor:

```text
POST /api/pedidos       -> 201
GET  /api/pedidos       -> 200
GET  /api/pedidos/{id}  -> 200 ou 404
```

Converter exceções de domínio em respostas JSON claras.

- [ ] **Step 5: Rodar testes**

Run: `python -m pytest tests/test_orders.py -v`

Expected: todos os testes deste arquivo passam.

- [ ] **Step 6: Commit**

```bash
git add app tests/test_orders.py
git commit -m "feat: implementa criação e consulta de pedidos"
```

### Task 4: Estado e cancelamento

**Files:**
- Modify: `app/schemas.py`
- Modify: `app/services.py`
- Modify: `app/routers/orders.py`
- Modify: `tests/test_orders.py`

- [ ] **Step 1: Escrever testes do ciclo de vida**

```python
def test_advances_order_status(client, created_order):
    response = client.patch(
        f"/api/pedidos/{created_order['id']}/status",
        json={"status": "preparando"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "preparando"

def test_rejects_invalid_status_transition(client, created_order):
    response = client.patch(
        f"/api/pedidos/{created_order['id']}/status",
        json={"status": "pronto"},
    )
    assert response.status_code == 400

def test_deletes_order(client, created_order):
    response = client.delete(f"/api/pedidos/{created_order['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/pedidos/{created_order['id']}").status_code == 404
```

Adicionar casos para estado desconhecido, pedido inexistente e sequência completa até `entregue`.

- [ ] **Step 2: Verificar falhas**

Run: `python -m pytest tests/test_orders.py -v`

Expected: novos testes falham com `404` ou ausência de regra.

- [ ] **Step 3: Implementar transições e exclusão**

Definir o mapa:

```python
NEXT_STATUS = {
    "recebido": "preparando",
    "preparando": "pronto",
    "pronto": "entregue",
}
```

Expor `PATCH /api/pedidos/{id}/status` e `DELETE /api/pedidos/{id}`; impedir transições que não correspondam ao próximo estado.

- [ ] **Step 4: Rodar a suíte**

Run: `python -m pytest -v`

Expected: todos os testes passam.

- [ ] **Step 5: Commit**

```bash
git add app tests
git commit -m "feat: adiciona fluxo de status e cancelamento"
```

### Task 5: Interface web

**Files:**
- Create: `app/static/index.html`
- Create: `app/static/styles.css`
- Create: `app/static/app.js`
- Modify: `app/main.py`

- [ ] **Step 1: Escrever teste de entrega da página**

```python
def test_serves_frontend(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Painel de Pedidos" in response.text
```

- [ ] **Step 2: Confirmar falha**

Run: `python -m pytest tests/test_products.py::test_serves_frontend -v`

Expected: FAIL até a rota estática ser adicionada.

- [ ] **Step 3: Implementar interface**

Criar uma página acessível e responsiva com cardápio, carrinho, formulário de cliente, resumo, lista de pedidos e feedback de operações. Usar `fetch` para os seis endpoints, `Intl.NumberFormat("pt-BR", {currency: "BRL"})` para valores e escapar conteúdo dinâmico.

- [ ] **Step 4: Servir arquivos estáticos**

Montar `/static` e responder `/` com `FileResponse(index.html)`.

- [ ] **Step 5: Verificar automaticamente e no navegador**

Run: `python -m pytest -v`

Expected: todos os testes passam.

Run: `uvicorn app.main:app --reload`

Expected: página abre em `http://127.0.0.1:8000`, sem erros no console, e o fluxo criar → preparar → pronto → entregar funciona.

- [ ] **Step 6: Commit**

```bash
git add app tests
git commit -m "feat: adiciona painel web de pedidos"
```

### Task 6: Documentação acadêmica e verificação final

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `docs/arquitetura.md`
- Create: `docs/screenshots/painel.png`
- Create: `docs/screenshots/swagger.png`

- [ ] **Step 1: Escrever README completo**

Incluir:

- identificação de Bernardo Gomes Dorneles, matrícula 2410103114, professor Silvio Ereno Quincozes;
- cenário, problema e objetivos;
- requisitos de comunicação;
- justificativa técnica do HTTP;
- tabela comparativa com MQTT, CoAP, AMQP e MCP;
- arquitetura, estrutura e modelo de dados;
- instalação para PowerShell e shells POSIX;
- execução, Swagger, exemplos `curl` e códigos HTTP;
- testes, resultados, limitações e melhorias futuras;
- capturas do painel e Swagger.

- [ ] **Step 2: Documentar arquitetura**

Criar um diagrama Mermaid mostrando navegador → FastAPI → serviços → SQLAlchemy → SQLite e registrar o fluxo completo de uma requisição.

- [ ] **Step 3: Executar verificações finais**

Run: `python -m pytest -v`

Expected: todos os testes passam.

Run: `python -m compileall app`

Expected: código 0, sem erros de sintaxe.

Run: `git diff --check`

Expected: nenhuma saída.

- [ ] **Step 4: Capturar evidências**

Iniciar o servidor, executar o fluxo completo no painel, capturar `painel.png`; abrir `/docs`, executar uma requisição e capturar `swagger.png`.

- [ ] **Step 5: Revisar reprodução**

Seguir o README em ambiente limpo: criar venv, instalar dependências, iniciar servidor, abrir a página e rodar testes. Confirmar que nenhuma instrução depende de estado não documentado.

- [ ] **Step 6: Commit**

```bash
git add README.md LICENSE docs app tests requirements.txt .gitignore
git commit -m "docs: conclui entrega acadêmica HTTP"
```
