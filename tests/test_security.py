from mcp_server.server import get_repair_status
from app.models import Repair
from mcp_server.server import change_repair_priority
from mcp_server.server import add_repair_update

def test_other_property_cannot_view_repair(monkeypatch):

    existing_repair = Repair(
        repair_id="HF-1001",
        property_id="P101",
        location="Kitchen",
        issue="Water leaking",
        priority="High",
        status="Open"
    )

    monkeypatch.setattr(
        "mcp_server.server.get_repair_by_id",
        lambda repair_id: existing_repair
    )

    result = get_repair_status(
        repair_id="HF-1001",
        requester_property_id="P102"
    )

    assert result == {
        "error": "Repair not found"
    }
def test_own_property_can_view_repair(monkeypatch):

    existing_repair = Repair(
        repair_id="HF-1001",
        property_id="P101",
        location="Kitchen",
        issue="Water leaking",
        priority="High",
        status="Open"
    )

    monkeypatch.setattr(
        "mcp_server.server.get_repair_by_id",
        lambda repair_id: existing_repair
    )

    result = get_repair_status(
        repair_id="HF-1001",
        requester_property_id="P101"
    )

    assert result["repair_id"] == "HF-1001"
    assert result["property_id"] == "P101"

# ---
def test_other_property_cannot_change_priority(monkeypatch):

    existing_repair = Repair(
        repair_id="HF-1001",
        property_id="P101",
        location="Kitchen",
        issue="Water leaking",
        priority="Medium",
        status="Open"
    )

    # Simulate finding the existing repair
    monkeypatch.setattr(
        "mcp_server.server.get_repair_by_id",
        lambda repair_id: existing_repair
    )

    # Prevent any actual database modification
    def forbidden_update(*args, **kwargs):
        raise AssertionError("Unauthorised update attempted!")

    monkeypatch.setattr(
        "mcp_server.server.update_repair",
        forbidden_update
    )

    result = change_repair_priority(
        repair_id="HF-1001",
        priority="Urgent",
        confirmed=True,
        requester_property_id="P102"
    )

    assert result == {
        "error": "Repair not found"
    }

    # ---
def test_other_property_cannot_add_update(monkeypatch):

    existing_repair = Repair(
        repair_id="HF-1001",
        property_id="P101",
        location="Kitchen",
        issue="Water leaking",
        priority="Medium",
        status="Open"
    )

    monkeypatch.setattr(
        "mcp_server.server.get_repair_by_id",
        lambda repair_id: existing_repair
    )

    def forbidden_update(*args, **kwargs):
        raise AssertionError("Unauthorized update attempted!")

    monkeypatch.setattr(
        "mcp_server.server.update_repair_issue",
        forbidden_update
    )

    result = add_repair_update(
        repair_id="HF-1001",
        update_text="Water is spreading",
        confirmed=True,
        requester_property_id="P102"
    )

    assert result == {"error": "Repair not found"}