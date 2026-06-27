from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str = Field(validation_alias="name")
    descricao: str = Field(validation_alias="description")
    preco: Decimal = Field(validation_alias="price", decimal_places=2)
