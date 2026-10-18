
from mcp_server.server import change_repair_priority, report_repair

from mcp_server.server import add_repair_update

def test_invalid_priority_is_rejected(monkeypatch):

    def forbidden_update(*args, **kwargs):
        raise AssertionError("Invalid priority reached database!")

    monkeypatch.setattr(
        "mcp_server.server.update_repair",
        forbidden_update
    )

    result = change_repair_priority(
        repair_id="HF-1001",
        priority="Critical",
        confirmed=True
    )

    assert result == {
        "error": "Invalid priority"
    }
    # ---
def test_new_repair_rejects_invalid_priority(monkeypatch):

    monkeypatch.setattr(
        "mcp_server.server.search_repairs",
        lambda *args, **kwargs: []
    )

    monkeypatch.setattr(
        "mcp_server.server.generate_repair_id",
        lambda: "HF-9999"
    )

    monkeypatch.setattr(
        "mcp_server.server.create_repair",
        lambda repair: repair
    )

    result = report_repair(
        property_id="P101",
        location="Kitchen",
        issue="Broken sink",
        priority="Critical",
        confirmed=True
    )

    assert result == {"error": "Invalid priority"}

    # ---

def test_new_repair_rejects_empty_issue(monkeypatch):

    monkeypatch.setattr(
        "mcp_server.server.search_repairs",
        lambda *args, **kwargs: []
    )

    monkeypatch.setattr(
        "mcp_server.server.generate_repair_id",
        lambda: "HF-9999"
    )

    # Simulate saving without touching the real JSON file
    monkeypatch.setattr(
        "mcp_server.server.create_repair",
        lambda repair: repair
    )

    result = report_repair(
        property_id="P101",
        location="Kitchen",
        issue="   ",
        priority="Medium",
        confirmed=True
    )

    assert result == {
        "error": "Issue cannot be empty"
    }

    # ---
def test_empty_repair_update_is_rejected(monkeypatch):

    def forbidden_update(*args, **kwargs):
        raise AssertionError("Empty update reached database!")

    monkeypatch.setattr(
        "mcp_server.server.update_repair_issue",
        forbidden_update
    )

    result = add_repair_update(
        repair_id="HF-1001",
        update_text="   ",
        confirmed=True
    )

    assert result == {
        "error": "Update cannot be empty"
    }