from datetime import datetime, timedelta, timezone


def create_order(client, restaurant_id="restaurante-1", **overrides):
    payload = {
        "restaurant_id": restaurant_id,
        "amount": "42.50",
        "items_count": 2,
        "status": "delivered",
    }
    payload.update(overrides)
    return client.post("/orders", json=payload)


def test_order_crud_and_restaurant_isolation(client):
    created = create_order(client)
    assert created.status_code == 201
    order = created.json()

    listed = client.get("/orders", params={"restaurant_id": "restaurante-1"})
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [order["id"]]

    hidden = client.get(
        f"/orders/{order['id']}", params={"restaurant_id": "outro-restaurante"}
    )
    assert hidden.status_code == 404

    updated = client.patch(
        f"/orders/{order['id']}",
        params={"restaurant_id": "restaurante-1"},
        json={"status": "cancelled"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "cancelled"

    deleted = client.delete(
        f"/orders/{order['id']}", params={"restaurant_id": "restaurante-1"}
    )
    assert deleted.status_code == 204
    assert client.get(
        f"/orders/{order['id']}", params={"restaurant_id": "restaurante-1"}
    ).status_code == 404


def test_order_validation_and_empty_update(client):
    invalid = create_order(client, amount="-1")
    assert invalid.status_code == 422

    created = create_order(client)
    empty_update = client.patch(
        f"/orders/{created.json()['id']}",
        params={"restaurant_id": "restaurante-1"},
        json={},
    )
    assert empty_update.status_code == 422


def test_operational_summary_and_date_filter(client):
    now = datetime.now(timezone.utc)
    create_order(
        client,
        amount="40.00",
        created_at=(now - timedelta(days=1)).isoformat(),
    )
    create_order(
        client,
        status="cancelled",
        amount="100.00",
        created_at=(now - timedelta(days=1)).isoformat(),
    )
    create_order(
        client,
        status="pending",
        amount="70.00",
        created_at=(now - timedelta(days=3)).isoformat(),
    )

    response = client.get(
        "/analytics/summary",
        params={
            "restaurant_id": "restaurante-1",
            "start_date": (now - timedelta(days=2)).date().isoformat(),
        },
    )
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_orders"] == 2
    assert summary["completed_orders"] == 1
    assert summary["cancelled_orders"] == 1
    assert summary["revenue"] == "40.00"
    assert len(summary["orders_by_hour"]) == 24


def test_demand_forecast_requires_history_and_returns_requested_horizon(client):
    response = client.get(
        "/analytics/forecast", params={"restaurant_id": "restaurante-1"}
    )
    assert response.status_code == 422

    now = datetime.now(timezone.utc)
    create_order(
        client,
        created_at=(now - timedelta(days=1)).isoformat(),
    )
    create_order(
        client,
        created_at=(now - timedelta(days=3)).isoformat(),
    )
    forecast = client.get(
        "/analytics/forecast",
        params={"restaurant_id": "restaurante-1", "days": 3, "history_days": 7},
    )
    assert forecast.status_code == 200
    assert len(forecast.json()["forecast"]) == 3
    assert all(point["predicted_orders"] >= 0 for point in forecast.json()["forecast"])
