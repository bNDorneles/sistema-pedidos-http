from datetime import timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate


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


class ResourceNotFoundError(Exception):
    pass


class BusinessRuleError(Exception):
    pass


def create_order(session: Session, data: OrderCreate) -> Order:
    quantities: dict[int, int] = {}
    for item in data.itens:
        quantities[item.produto_id] = quantities.get(item.produto_id, 0) + item.quantidade

    products = list(
        session.scalars(
            select(Product)
            .where(Product.id.in_(quantities))
            .order_by(Product.id)
        )
    )
    products_by_id = {product.id: product for product in products}

    for product_id in quantities:
        if product_id not in products_by_id:
            raise ResourceNotFoundError(f"Produto {product_id} não encontrado.")

    order = Order(status="recebido", total=Decimal("0.00"))
    for product_id, quantity in quantities.items():
        product = products_by_id[product_id]
        order.items.append(
            OrderItem(
                product=product,
                quantity=quantity,
                unit_price=product.price,
            )
        )

    order.total = sum(
        (item.unit_price * item.quantity for item in order.items),
        start=Decimal("0.00"),
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def _orders_query():
    return select(Order).options(
        selectinload(Order.items).selectinload(OrderItem.product)
    )


def list_orders(session: Session) -> list[Order]:
    return list(session.scalars(_orders_query().order_by(Order.created_at.desc())))


def summarize_orders(session: Session) -> dict:
    counts = {
        "recebido": 0,
        "preparando": 0,
        "pronto": 0,
        "entregue": 0,
    }
    rows = session.execute(
        select(Order.status, func.count(Order.id)).group_by(Order.status)
    )
    for status, amount in rows:
        counts[status] = amount

    return {
        "total": sum(counts.values()),
        "por_status": counts,
    }


def get_order(session: Session, order_id: int) -> Order:
    order = session.scalar(_orders_query().where(Order.id == order_id))
    if order is None:
        raise ResourceNotFoundError(f"Pedido {order_id} não encontrado.")
    return order


NEXT_STATUS = {
    "recebido": "preparando",
    "preparando": "pronto",
    "pronto": "entregue",
}


def update_order_status(session: Session, order_id: int, new_status: str) -> Order:
    order = get_order(session, order_id)
    expected = NEXT_STATUS.get(order.status)
    if new_status != expected:
        expected_message = expected or "nenhum (pedido finalizado)"
        raise BusinessRuleError(
            f"Transição inválida: de '{order.status}' para '{new_status}'. "
            f"Próximo estado permitido: {expected_message}."
        )

    order.status = new_status
    session.commit()
    session.refresh(order)
    return order


def delete_order(session: Session, order_id: int) -> None:
    order = get_order(session, order_id)
    session.delete(order)
    session.commit()


def order_to_dict(order: Order) -> dict:
    created_at = order.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    else:
        created_at = created_at.astimezone(timezone.utc)

    return {
        "id": order.id,
        "status": order.status,
        "total": order.total,
        "criado_em": created_at,
        "itens": [
            {
                "produto_id": item.product_id,
                "nome_produto": item.product.name,
                "quantidade": item.quantity,
                "preco_unitario": item.unit_price,
                "subtotal": item.unit_price * item.quantity,
            }
            for item in order.items
        ],
    }
