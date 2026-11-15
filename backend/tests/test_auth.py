def test_login_and_current_account_are_scoped_to_demo_restaurant(client):
    response = client.get("/auth/me")

    assert response.status_code == 200
    assert response.json() == {
        "username": "tester",
        "restaurant_id": "restaurante-1",
    }


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        json={"username": "tester", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Usuário ou senha inválidos."


def test_protected_routes_require_a_bearer_token(client):
    del client.headers["Authorization"]

    response = client.get(
        "/orders",
        params={"restaurant_id": "restaurante-1"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_account_cannot_read_or_create_orders_for_another_restaurant(client):
    other_restaurant = client.get(
        "/orders",
        params={"restaurant_id": "outro-restaurante"},
    )
    other_order = client.post(
        "/orders",
        json={
            "restaurant_id": "outro-restaurante",
            "amount": "42.50",
            "items_count": 2,
            "status": "delivered",
        },
    )

    assert other_restaurant.status_code == 403
    assert other_order.status_code == 403


def test_account_cannot_query_another_restaurant_analytics_or_assistant(client):
    analytics = client.get(
        "/analytics/summary",
        params={"restaurant_id": "outro-restaurante"},
    )
    assistant = client.post(
        "/assistant/ask",
        json={
            "restaurant_id": "outro-restaurante",
            "question": "Como estão meus pedidos?",
        },
    )

    assert analytics.status_code == 403
    assert assistant.status_code == 403


def test_login_returns_service_unavailable_when_not_configured(client, monkeypatch):
    monkeypatch.delenv("PROTOTYPE_PASSWORD")

    response = client.post(
        "/auth/login",
        json={"username": "tester", "password": "test-password"},
    )

    assert response.status_code == 503
    assert "PROTOTYPE_PASSWORD" in response.json()["detail"]
