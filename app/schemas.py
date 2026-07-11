from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str = Field(validation_alias="name")
    descricao: str = Field(validation_alias="description")
    preco: Decimal = Field(validation_alias="price", decimal_places=2)


class OrderItemCreate(BaseModel):
    produto_id: int = Field(gt=0)
    quantidade: int = Field(gt=0)


class OrderCreate(BaseModel):
    itens: list[OrderItemCreate] = Field(min_length=1)


class OrderItemResponse(BaseModel):
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: int
    status: str
    total: Decimal
    criado_em: datetime
    itens: list[OrderItemResponse]


class OrderSummaryResponse(BaseModel):
    total: int
    por_status: dict[str, int]


class OrderStatusUpdate(BaseModel):
    status: Literal["recebido", "preparando", "pronto", "entregue"]
