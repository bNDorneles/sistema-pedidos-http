from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services import (
    BusinessRuleError,
    ResourceNotFoundError,
    create_order,
    delete_order,
    get_order,
    list_orders,
    order_to_dict,
    update_order_status,
)

router = APIRouter(prefix="/api/pedidos", tags=["Pedidos"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def not_found(error: ResourceNotFoundError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error))


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def post_order(data: OrderCreate, session: DatabaseSession) -> dict:
    try:
        return order_to_dict(create_order(session, data))
    except ResourceNotFoundError as error:
        raise not_found(error) from error


@router.get("", response_model=list[OrderResponse])
def get_orders(session: DatabaseSession) -> list[dict]:
    return [order_to_dict(order) for order in list_orders(session)]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(order_id: int, session: DatabaseSession) -> dict:
    try:
        return order_to_dict(get_order(session, order_id))
    except ResourceNotFoundError as error:
        raise not_found(error) from error


@router.patch("/{order_id}/status", response_model=OrderResponse)
def patch_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    session: DatabaseSession,
) -> dict:
    try:
        return order_to_dict(update_order_status(session, order_id, data.status))
    except ResourceNotFoundError as error:
        raise not_found(error) from error
    except BusinessRuleError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_order(order_id: int, session: DatabaseSession) -> None:
    try:
        delete_order(session, order_id)
    except ResourceNotFoundError as error:
        raise not_found(error) from error
