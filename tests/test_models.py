from importlib.util import find_spec


def test_database_defines_restaurant_tables():
    assert find_spec("app.models") is not None, "app.models ainda não foi implementado"

    from app.database import Base
    import app.models  # noqa: F401

    assert set(Base.metadata.tables) == {"produtos", "pedidos", "itens_pedido"}
