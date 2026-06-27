from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import ProductResponse
from app.services import list_products

router = APIRouter(prefix="/api/produtos", tags=["Produtos"])
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[ProductResponse])
def get_products(session: DatabaseSession) -> list[ProductResponse]:
    return list_products(session)
