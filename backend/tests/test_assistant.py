import asyncio

import httpx

from app.services.assistant import (
    MAX_GROQ_COMPLETION_TOKENS,
    MAX_RESPONSE_TOKENS,
    generate_grounded_answer,
)


def test_local_ollama_uses_history_and_concise_interactive_prompt(monkeypatch):
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
            "E no fim de semana?",
            [("Resumo", "Nos últimos 90 dias foram registrados dois pedidos.")],
            [("Quantos pedidos foram registrados?", "Foram registrados dois pedidos.")],
        )
    )

    assert answer == "Foram registrados dois pedidos."
    assert captured_request["url"] == "http://localhost:11434/api/chat"
    assert captured_request["payload"]["think"] is False
    assert captured_request["payload"]["options"]["num_predict"] == MAX_RESPONSE_TOKENS
    messages = captured_request["payload"]["messages"]
    system_prompt = messages[0]["content"]
    assert "Seu nome é Prato" in system_prompt
    assert "pRATu" in system_prompt
    assert "PTRAOO" in system_prompt
    assert "pratooo" in system_prompt
    assert "marketing" in system_prompt
    assert "uma única pergunta curta e relevante" in system_prompt
    assert "45 palavras" in system_prompt
    assert "histórico apenas para manter a continuidade" in system_prompt
    assert "Não invente números" in system_prompt
    assert messages[1:] == [
        {"role": "user", "content": "Quantos pedidos foram registrados?"},
        {"role": "assistant", "content": "Foram registrados dois pedidos."},
        {"role": "user", "content": "E no fim de semana?"},
    ]


def test_groq_gpt_oss_requests_hidden_reasoning_and_completion_budget(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-oss-20b")
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
                json={
                    "choices": [
                        {"message": {"content": "Oi! Como posso ajudar?"}}
                    ]
                },
            )

    monkeypatch.setattr("app.services.assistant.httpx.AsyncClient", MockAsyncClient)

    answer = asyncio.run(generate_grounded_answer("Oi Prato", []))

    assert answer == "Oi! Como posso ajudar?"
    assert captured_request["url"] == (
        "https://api.groq.com/openai/v1/chat/completions"
    )
    assert captured_request["payload"]["max_completion_tokens"] == (
        MAX_GROQ_COMPLETION_TOKENS
    )
    assert captured_request["payload"]["reasoning_effort"] == "low"
    assert captured_request["payload"]["reasoning_format"] == "hidden"
    assert "max_tokens" not in captured_request["payload"]


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

    async def fake_answer(question, context, history):
        period_summary = next(
            content for source, content in context if source == "Resumo por período"
        )
        assert "último mês (últimos 30 dias)" in period_summary
        assert "faturamento de pedidos entregues R$ 42.50" in period_summary
        assert history == [
            ("Quantos pedidos houve?", "Foram registrados 10 pedidos.")
        ]
        return "O faturamento recuperado foi R$ 42,50."

    monkeypatch.setattr(
        "app.routes.assistant.generate_grounded_answer",
        fake_answer,
    )
    response = client.post(
        "/assistant/ask",
        json={
            "restaurant_id": "restaurante-1",
            "question": "E quanto foi o faturamento?",
            "history": [
                {
                    "question": "Quantos pedidos houve?",
                    "answer": "Foram registrados 10 pedidos.",
                }
            ],
        },
    )
    assert response.status_code == 200
    assert "Resumo por período" in response.json()["sources"]


def test_assistant_requires_provider_key(client, monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    response = client.post(
        "/assistant/ask",
        json={"restaurant_id": "restaurante-1", "question": "Qual foi o faturamento?"},
    )
    assert response.status_code == 503
    assert "LLM_API_KEY" in response.json()["detail"]


def test_assistant_limits_conversation_history(client):
    history = [
        {"question": f"Pergunta {index}?", "answer": f"Resposta {index}."}
        for index in range(5)
    ]

    response = client.post(
        "/assistant/ask",
        json={
            "restaurant_id": "restaurante-1",
            "question": "Qual o próximo passo?",
            "history": history,
        },
    )

    assert response.status_code == 422
