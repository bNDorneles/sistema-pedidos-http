from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, SessionLocal, engine
from app.routers.products import router as products_router
from app.services import seed_products


def create_app(initialize_database: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        if initialize_database:
            Base.metadata.create_all(engine)
            with SessionLocal() as session:
                seed_products(session)
        yield

    application = FastAPI(
        title="API de Pedidos do Restaurante",
        description="Prova de conceito do protocolo HTTP com uma API REST.",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.include_router(products_router)
    return application


app = create_app()
