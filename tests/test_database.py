
from app.database import normalize_issue, search_repairs
from app.models import Repair

def test_normalize_issue_converts_leaking_to_leak():
    result = normalize_issue("Kitchen sink is leaking")

    assert result == "kitchen sink is leak"

def test_search_finds_existing_leak(monkeypatch):
    existing_repair = Repair(
        repair_id="HF-1001",
        property_id="P101",
        location="Kitchen",
        issue="Kitchen sink is dripping",
        priority="Medium",
        status="Open"
    )

    monkeypatch.setattr(
        "app.database.get_repairs",
        lambda: [existing_repair]
    )

    results = search_repairs(
        "P101",
        "Kitchen",
        "Kitchen sink is leaking"
    )

    assert len(results) == 1
    assert results[0].repair_id == "HF-1001"

def test_search_does_not_return_other_property_repairs(monkeypatch):
    existing_repair = Repair(
        repair_id="HF-1001",
        property_id="P101",
        location="Kitchen",
        issue="Kitchen sink is leaking",
        priority="Medium",
        status="Open"
    )

    monkeypatch.setattr(
        "app.database.get_repairs",
        lambda: [existing_repair]
    )

    results = search_repairs(
        "P102",
        "Kitchen",
        "Kitchen sink is leaking"
    )

    assert results == []