from fastapi import FastAPI

from app.routes.health import router as health_router

app = FastAPI(
    title="iFood AI Copilot",
    description="Assistente inteligente para análise operacional de restaurantes.",
    version="0.1.0",
)

app.include_router(health_router)
