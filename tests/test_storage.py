from app import storage


def test_json_is_default_backend(monkeypatch):
    monkeypatch.delenv(
        "HOMEFIX_STORAGE_BACKEND",
        raising=False
    )

    assert storage.get_backend() is storage.database


def test_dynamodb_backend_selected(monkeypatch):
    monkeypatch.setenv(
        "HOMEFIX_STORAGE_BACKEND",
        "dynamodb"
    )

    assert storage.get_backend() is storage.dynamodb_store


def test_priority_update_routes_to_dynamodb(monkeypatch):
    monkeypatch.setenv(
        "HOMEFIX_STORAGE_BACKEND",
        "dynamodb"
    )

    captured = {}

    def fake_update(repair_id, property_id, priority):
        captured["repair_id"] = repair_id
        captured["property_id"] = property_id
        captured["priority"] = priority
        return "updated"

    monkeypatch.setattr(
        storage.dynamodb_store,
        "update_repair_priority",
        fake_update
    )

    result = storage.update_repair(
        "HF-1001",
        "TEST-001",
        "High"
    )

    assert result == "updated"
    assert captured == {
        "repair_id": "HF-1001",
        "property_id": "TEST-001",
        "priority": "High"
    }