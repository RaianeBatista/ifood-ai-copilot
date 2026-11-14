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
