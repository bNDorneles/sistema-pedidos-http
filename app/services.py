from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product


INITIAL_PRODUCTS = (
    ("Xis Gaúcho", "Pão, carne, queijo, ovo, salada e milho.", Decimal("28.90")),
    ("Hambúrguer Clássico", "Pão, carne, queijo, alface e tomate.", Decimal("22.50")),
    ("Pizza Margherita", "Molho de tomate, muçarela e manjericão.", Decimal("42.00")),
    ("Batata Frita", "Porção crocante de 300 g.", Decimal("18.00")),
    ("Refrigerante", "Lata de 350 ml.", Decimal("7.50")),
    ("Suco Natural", "Copo de 400 ml.", Decimal("10.00")),
)


def seed_products(session: Session) -> None:
    if session.scalar(select(Product.id).limit(1)) is not None:
        return

    session.add_all(
        Product(name=name, description=description, price=price)
        for name, description, price in INITIAL_PRODUCTS
    )
    session.commit()


def list_products(session: Session) -> list[Product]:
    return list(session.scalars(select(Product).order_by(Product.id)))
