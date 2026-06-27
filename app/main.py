from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.database import Base, SessionLocal, engine
from app.routers.orders import router as orders_router
from app.routers.products import router as products_router
from app.services import seed_products

STATIC_DIR = Path(__file__).resolve().parent / "static"


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
    application.include_router(orders_router)
    application.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @application.get("/", include_in_schema=False)
    def frontend() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    return application


app = create_app()
