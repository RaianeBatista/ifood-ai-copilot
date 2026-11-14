from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routes.analytics import router as analytics_router
from app.routes.assistant import router as assistant_router
from app.routes.health import router as health_router
from app.routes.orders import router as orders_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="iFood AI Copilot",
    description="Assistente inteligente para análise operacional de restaurantes.",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(orders_router)
app.include_router(analytics_router)
app.include_router(assistant_router)
