import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import httpx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Order


class MissingLLMConfigurationError(Exception):
    pass


class LLMProviderError(Exception):
    pass


def retrieve_operational_context(
    db: Session, restaurant_id: str, question: str, limit: int = 4
) -> list[tuple[str, str]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    statement = select(Order).where(
        Order.restaurant_id == restaurant_id,
        Order.created_at >= cutoff,
    )
    orders = list(db.scalars(statement.order_by(Order.created_at.desc())))

    documents = [
        (
            "Definições dos indicadores",
            "Faturamento considera pedidos entregues. Pedidos cancelados não entram no faturamento nem na contagem de demanda. "
            "Ticket médio é o faturamento dividido pela quantidade de pedidos entregues. "
            "Os indicadores são calculados para o restaurante informado.",
        )
    ]
    if orders:
        revenue = sum(
            (order.amount for order in orders if order.status == "delivered"),
            start=Decimal("0.00"),
        )
        status_counts = Counter(order.status for order in orders)
        documents.append(
            (
                "Resumo dos últimos 90 dias",
                f"Nos últimos 90 dias foram registrados {len(orders)} pedidos. "
                f"Faturamento dos pedidos entregues: R$ {revenue:.2f}. "
                f"Pedidos por status: {dict(status_counts)}.",
            )
        )
        by_date = Counter(order.created_at.date().isoformat() for order in orders)
        for day, count in by_date.most_common(30):
            documents.append((f"Pedidos em {day}", f"No dia {day} houve {count} pedidos."))
        by_hour = Counter(
            order.created_at.hour for order in orders if order.status != "cancelled"
        )
        for hour, count in by_hour.most_common(5):
            documents.append(
                (f"Movimento às {hour:02d}h", f"Às {hour:02d}h houve {count} pedidos não cancelados.")
            )

    vectorizer = TfidfVectorizer()
    matrix = vectorizer.fit_transform([question, *(content for _, content in documents)])
    scores = cosine_similarity(matrix[0:1], matrix[1:]).ravel()
    ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
    return [
        documents[index]
        for index, score in ranked[:limit]
        if score > 0
    ]


async def generate_grounded_answer(question: str, context: list[tuple[str, str]]) -> str:
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise MissingLLMConfigurationError("LLM_API_KEY não está configurada.")

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    context_text = "\n\n".join(f"[{source}] {text}" for source, text in context)
    if not context_text:
        context_text = "Não há informações relevantes nos dados para responder."
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Responda em português usando somente o contexto recuperado abaixo. "
                    "Se ele não contiver a resposta, diga claramente que não há dados suficientes. "
                    "Não invente métricas nem recomendações sem evidência.\n\n"
                    f"Contexto:\n{context_text}"
                ),
            },
            {"role": "user", "content": question},
        ],
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json=payload,
            )
    except httpx.RequestError as exc:
        raise LLMProviderError("Não foi possível conectar ao provedor de IA.") from exc

    if not response.is_success:
        raise LLMProviderError(f"O provedor de IA retornou HTTP {response.status_code}.")
    try:
        data: Any = response.json()
    except ValueError as exc:
        raise LLMProviderError("O provedor de IA retornou uma resposta inválida.") from exc

    if not isinstance(data, dict):
        raise LLMProviderError("O provedor de IA retornou uma resposta inválida.")
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise LLMProviderError("O provedor de IA retornou uma resposta inválida.")
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise LLMProviderError("O provedor de IA retornou uma resposta inválida.")
    answer = message["content"].strip()
    if not answer:
        raise LLMProviderError("O provedor de IA retornou uma resposta vazia.")
    return answer
