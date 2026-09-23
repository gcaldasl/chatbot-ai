from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents
from app.config import get_settings
from app.db.database import Database


def create_app() -> FastAPI:
    settings = get_settings()
    database = Database(dsn=settings.database_url, embedding_dimensions=settings.embedding_dimensions)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await database.connect()
        app.state.db_pool = database.pool
        yield
        await database.disconnect()

    app = FastAPI(title="Agente de Conhecimento API", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_origin],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(documents.router)
    app.include_router(chat.router)

    return app


app = create_app()
