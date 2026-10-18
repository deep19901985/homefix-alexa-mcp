# from mcp_server.server import change_repair_priority


# def test_priority_change_requires_confirmation():
#     result = change_repair_priority(
#         repair_id="HF-1001",
#         priority="Urgent",
#         confirmed=False
#     )

#     assert result == {
#         "message": "Confirmation required before updating repair"
#     }
# ---
from mcp_server.server import change_repair_priority

from mcp_server.server import add_repair_update

from mcp_server.server import report_repair

def test_priority_change_requires_confirmation(monkeypatch):

    def forbidden_update(*args, **kwargs):
        raise AssertionError("Database update was attempted!")

    monkeypatch.setattr(
        "mcp_server.server.update_repair",
        forbidden_update
    )

    result = change_repair_priority(
        repair_id="HF-1001",
        priority="Urgent",
        confirmed=False
    )

    assert result == {
        "message": "Confirmation required before updating repair"
    }

def test_add_repair_update_requires_confirmation(monkeypatch):

    def forbidden_update(*args, **kwargs):
        raise AssertionError("Database update was attempted!")

    monkeypatch.setattr(
        "mcp_server.server.update_repair_issue",
        forbidden_update
    )

    result = add_repair_update(
        repair_id="HF-1001",
        update_text="Water is spreading onto the floor",
        confirmed=False
    )

    assert result == {
        "message": "Confirmation required before adding update"
    }

# ---
def test_report_repair_requires_confirmation(monkeypatch):

    # Pretend no duplicate repairs exist
    monkeypatch.setattr(
        "mcp_server.server.search_repairs",
        lambda *args, **kwargs: []
    )

    # Fail the test if a repair is created
    def forbidden_create(*args, **kwargs):
        raise AssertionError("Repair created without confirmation!")

    monkeypatch.setattr(
        "mcp_server.server.create_repair",
        forbidden_create
    )

    result = report_repair(
        property_id="P101",
        location="Bathroom",
        issue="Water leaking",
        priority="High",
        confirmed=False
    )

    assert result == {
        "message": "Confirmation required before creating repair"
    }

    # --

def test_missing_repair_cannot_change_priority(monkeypatch):

    # Simulate an empty database
    monkeypatch.setattr(
        "app.database.get_repairs",
        lambda: []
    )

    # Raise an error if HomeFix tries to save anything
    def forbidden_save(*args, **kwargs):
        raise AssertionError("Unexpected database write!")

    monkeypatch.setattr(
        "app.database.save_repairs",
        forbidden_save
    )

    result = change_repair_priority(
        repair_id="HF-9999",
        priority="Urgent",
        confirmed=True
    )

    assert result == {
        "error": "Repair not found"
    }