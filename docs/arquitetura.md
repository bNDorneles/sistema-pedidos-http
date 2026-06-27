# Arquitetura e fluxo HTTP

## Componentes

```mermaid
flowchart TB
    subgraph Cliente
        UI["Interface HTML/CSS"]
        JS["JavaScript + fetch"]
        UI --> JS
    end

    subgraph Servidor FastAPI
        STATIC["Arquivos estáticos"]
        API["Roteadores REST"]
        VALID["Pydantic"]
        SERVICE["Serviços"]
        ORM["SQLAlchemy"]
        API --> VALID
        VALID --> SERVICE
        SERVICE --> ORM
    end

    DB[("SQLite")]

    JS -->|"GET /api/produtos"| API
    JS -->|"POST /api/pedidos"| API
    JS -->|"PATCH /api/pedidos/{id}/status"| API
    JS -->|"DELETE /api/pedidos/{id}"| API
    STATIC --> UI
    ORM --> DB
```

## Responsabilidades

| Unidade | Responsabilidade |
| --- | --- |
| `database.py` | Configurar engine, base e sessões |
| `models.py` | Representar tabelas e relacionamentos |
| `schemas.py` | Validar JSON e definir respostas |
| `services.py` | Aplicar regras independentemente do transporte |
| `routers/` | Associar regras a métodos, URLs e códigos HTTP |
| `static/` | Apresentar e consumir os recursos da API |

## Sequência de criação

```mermaid
sequenceDiagram
    actor U as Usuário
    participant B as Navegador
    participant A as FastAPI
    participant S as Serviço
    participant D as SQLite

    U->>B: Seleciona itens
    B->>A: POST /api/pedidos (JSON)
    A->>A: Valida corpo com Pydantic
    A->>S: create_order()
    S->>D: Consulta produtos e preços
    D-->>S: Produtos encontrados
    S->>S: Consolida itens e calcula total
    S->>D: INSERT pedido e itens
    D-->>S: Confirma transação
    S-->>A: Pedido persistido
    A-->>B: 201 Created + JSON
    B-->>U: Exibe confirmação
```

## Modelo de dados

```mermaid
erDiagram
    PRODUTOS ||--o{ ITENS_PEDIDO : compoe
    PEDIDOS ||--|{ ITENS_PEDIDO : possui

    PRODUTOS {
        int id PK
        string nome
        string descricao
        decimal preco
    }

    PEDIDOS {
        int id PK
        string status
        decimal total
        datetime criado_em
    }

    ITENS_PEDIDO {
        int id PK
        int pedido_id FK
        int produto_id FK
        int quantidade
        decimal preco_unitario
    }
```

O preço unitário é copiado para o item no momento da criação. Assim, o histórico do pedido não muda caso o preço do cardápio seja alterado posteriormente.

## Decisões

- O total é calculado no servidor, nunca aceito do cliente.
- Todos os produtos são validados antes do `commit`.
- Itens repetidos são consolidados.
- Os estados seguem uma máquina simples e não podem pular etapas.
- A exclusão usa `204 No Content`.
- O SQLite reduz dependências externas, sem esconder o uso real de um banco relacional.
