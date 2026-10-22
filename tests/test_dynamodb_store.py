from app import dynamodb_store


def test_get_repair_by_id(monkeypatch):

    class FakeTable:
        def get_item(self, Key, ConsistentRead):
            assert Key == {"repair_id": "HF-1001"}
            assert ConsistentRead is True

            return {
                "Item": {
                    "repair_id": "HF-1001",
                    "property_id": "TEST-001",
                    "location": "kitchen",
                    "issue": "leaking sink",
                    "priority": "high",
                    "status": "open",
                    "updates": []
                }
            }

    monkeypatch.setattr(
        dynamodb_store,
        "get_table",
        lambda: FakeTable()
    )

    repair = dynamodb_store.get_repair_by_id("HF-1001")

    assert repair.repair_id == "HF-1001"
    assert repair.priority == "high"
    assert repair.location == "kitchen"

def test_create_repair_uses_conditional_write(monkeypatch):
        captured = {}

        class FakeTable:
             def put_item(self, **kwargs):
                  captured.update(kwargs)

        monkeypatch.setattr(
            dynamodb_store,
            "get_table",
             lambda: FakeTable()
        )

        repair = dynamodb_store.Repair(
            repair_id="HF-1002",
            property_id="TEST-001",
            location="kitchen",
            issue="broken tap",
            priority="medium",
            status="open"
            )

        result = dynamodb_store.create_repair(repair)

        assert result == repair
        assert captured["Item"] == repair.model_dump()
        assert captured["ConditionExpression"] == (
            "attribute_not_exists(repair_id)"
    )

def test_create_repair_rejects_duplicate(monkeypatch):
    import pytest
    from botocore.exceptions import ClientError

    class FakeTable:
        def put_item(self, **kwargs):
            raise ClientError(
                {
                    "Error": {
                        "Code": "ConditionalCheckFailedException",
                        "Message": "Repair already exists"
                    }
                },
                "PutItem"
            )

    monkeypatch.setattr(
        dynamodb_store,
        "get_table",
        lambda: FakeTable()
    )

    repair = dynamodb_store.Repair(
        repair_id="HF-1002",
        property_id="TEST-001",
        location="kitchen",
        issue="broken tap",
        priority="medium",
        status="open"
    )

    with pytest.raises(
        ValueError,
        match="Repair ID already exists"
    ):
        dynamodb_store.create_repair(repair)

def test_search_repairs(monkeypatch):
    calls = []

    class FakeTable:
        def scan(self, **kwargs):
            calls.append(kwargs)

            if len(calls) == 1:
                return {
                    "Items": [
                        {
                            "repair_id": "HF-1001",
                            "property_id": "TEST-001",
                            "location": "kitchen",
                            "issue": "Sink is leaking",
                            "priority": "high",
                            "status": "open",
                            "updates": []
                        }
                    ],
                    "LastEvaluatedKey": {
                        "repair_id": "HF-1001"
                    }
                }

            return {
                "Items": [
                    {
                        "repair_id": "HF-1002",
                        "property_id": "TEST-001",
                        "location": "bathroom",
                        "issue": "Tap leaking",
                        "priority": "medium",
                        "status": "open",
                        "updates": []
                    }
                ]
            }

    monkeypatch.setattr(
        dynamodb_store,
        "get_table",
        lambda: FakeTable()
    )

    results = dynamodb_store.search_repairs(
        "TEST-001", "kitchen", "leak"
    )

    assert len(results) == 1
    assert results[0].repair_id == "HF-1001"
    assert len(calls) == 2
    assert calls[1]["ExclusiveStartKey"] == {
        "repair_id": "HF-1001"
    }

def test_update_repair_priority(monkeypatch):
    captured = {}

    class FakeTable:
        def update_item(self, **kwargs):
            captured.update(kwargs)

            return {
                "Attributes": {
                    "repair_id": "HF-1001",
                    "property_id": "TEST-001",
                    "location": "kitchen",
                    "issue": "leaking sink",
                    "priority": "urgent",
                    "status": "open",
                    "updates": []
                }
            }

    monkeypatch.setattr(
        dynamodb_store,
        "get_table",
        lambda: FakeTable()
    )

    result = dynamodb_store.update_repair_priority(
        "HF-1001",
        "TEST-001",
        "urgent"
    )

    assert result.priority == "urgent"
    assert captured["Key"] == {"repair_id": "HF-1001"}

    assert captured["ExpressionAttributeValues"] == {
        ":priority": "urgent",
        ":property_id": "TEST-001"
    }

    assert captured["ConditionExpression"] == (
        "attribute_exists(repair_id) "
        "AND #property = :property_id"
    )

    assert captured["ReturnValues"] == "ALL_NEW"

def test_priority_update_rejects_other_property(monkeypatch):
    from botocore.exceptions import ClientError

    class FakeTable:
        def update_item(self, **kwargs):
            assert kwargs["ExpressionAttributeValues"][
                ":property_id"
            ] == "OTHER-001"

            assert "#property = :property_id" in (
                kwargs["ConditionExpression"]
            )

            raise ClientError(
                {
                    "Error": {
                        "Code": "ConditionalCheckFailedException",
                        "Message": "Property mismatch"
                    }
                },
                "UpdateItem"
            )

    monkeypatch.setattr(
        dynamodb_store,
        "get_table",
        lambda: FakeTable()
    )

    result = dynamodb_store.update_repair_priority(
        "HF-1001",
        "OTHER-001",
        "urgent"
    )

    assert result is None

def test_add_repair_update(monkeypatch):
    captured = {}

    class FakeTable:
        def update_item(self, **kwargs):
            captured.update(kwargs)

            return {
                "Attributes": {
                    "repair_id": "HF-1001",
                    "property_id": "TEST-001",
                    "location": "kitchen",
                    "issue": "leaking sink",
                    "priority": "high",
                    "status": "open",
                    "updates": [
                        "Original report",
                        "Water spreading onto floor"
                    ]
                }
            }

    monkeypatch.setattr(
        dynamodb_store,
        "get_table",
        lambda: FakeTable()
    )

    result = dynamodb_store.add_repair_update(
        "HF-1001",
        "TEST-001",
        "Water spreading onto floor"
    )

    assert len(result.updates) == 2
    assert result.updates[-1] == "Water spreading onto floor"

    assert captured["Key"] == {"repair_id": "HF-1001"}

    assert "list_append" in captured["UpdateExpression"]

    assert captured["ExpressionAttributeValues"][
        ":new_update"
    ] == ["Water spreading onto floor"]

    assert "#property = :property_id" in (
        captured["ConditionExpression"]
    )

def test_generate_repair_id():
    repair_id_1 = dynamodb_store.generate_repair_id()
    repair_id_2 = dynamodb_store.generate_repair_id()

    assert repair_id_1.startswith("HF-")
    assert len(repair_id_1) == 15
    assert repair_id_1 != repair_id_2