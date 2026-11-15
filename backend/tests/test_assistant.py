import asyncio

import httpx

from app.services.assistant import MAX_RESPONSE_TOKENS, generate_grounded_answer


def test_local_ollama_uses_scoped_concise_prompt_and_disables_thinking(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "ollama")
    monkeypatch.setenv("LLM_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen3:1.7b")
    captured_request = {}

    class MockAsyncClient:
        def __init__(self, timeout):
            assert timeout == 30.0

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_value, traceback):
            return None

        async def post(self, url, *, headers, json):
            captured_request.update(url=url, headers=headers, payload=json)
            return httpx.Response(
                200,
                json={"message": {"content": "Foram registrados dois pedidos."}},
            )

    monkeypatch.setattr("app.services.assistant.httpx.AsyncClient", MockAsyncClient)

    answer = asyncio.run(
        generate_grounded_answer(
            "Quantos pedidos foram registrados?",
            [("Resumo", "Nos últimos 90 dias foram registrados dois pedidos.")],
        )
    )

    assert answer == "Foram registrados dois pedidos."
    assert captured_request["url"] == "http://localhost:11434/api/chat"
    assert captured_request["payload"]["think"] is False
    assert captured_request["payload"]["options"]["num_predict"] == MAX_RESPONSE_TOKENS
    system_prompt = captured_request["payload"]["messages"][0]["content"]
    assert "Seu nome é Prato" in system_prompt
    assert "pRATu" in system_prompt
    assert "PTRAOO" in system_prompt
    assert "pratooo" in system_prompt
    assert "marketing" in system_prompt
    assert "proponha um próximo passo concreto" in system_prompt
    assert "no máximo quatro frases" in system_prompt
    assert "Não invente números" in system_prompt


def test_assistant_retrieves_operational_context(client, monkeypatch):
    client.post(
        "/orders",
        json={
            "restaurant_id": "restaurante-1",
            "amount": "42.50",
            "items_count": 2,
            "status": "delivered",
        },
    )

    async def fake_answer(question, context):
        assert any(source == "Resumo dos últimos 90 dias" for source, _ in context)
        return "O faturamento recuperado foi R$ 42,50."

    monkeypatch.setattr(
        "app.routes.assistant.generate_grounded_answer",
        fake_answer,
    )
    response = client.post(
        "/assistant/ask",
        json={"restaurant_id": "restaurante-1", "question": "Qual foi o faturamento?"},
    )
    assert response.status_code == 200
    assert "Resumo dos últimos 90 dias" in response.json()["sources"]


def test_assistant_requires_provider_key(client, monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    response = client.post(
        "/assistant/ask",
        json={"restaurant_id": "restaurante-1", "question": "Qual foi o faturamento?"},
    )
    assert response.status_code == 503
    assert "LLM_API_KEY" in response.json()["detail"]
