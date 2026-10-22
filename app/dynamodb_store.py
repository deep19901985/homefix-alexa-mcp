import os
import boto3
import uuid
from botocore.exceptions import ClientError
from app.models import Repair
from boto3.dynamodb.conditions import Attr
from app.database import normalize_issue


def get_table():
    """Connect to the configured DynamoDB table."""

    table_name = os.getenv("HOMEFIX_DYNAMODB_TABLE")

    if not table_name:
        raise RuntimeError(
            "HOMEFIX_DYNAMODB_TABLE is not configured"
        )

    region = os.getenv("AWS_REGION", "eu-west-2")

    dynamodb = boto3.resource(
        "dynamodb",
        region_name=region
    )

    return dynamodb.Table(table_name)


def get_repair_by_id(repair_id: str):
    """Find a repair by its unique reference."""

    table = get_table()

    response = table.get_item(
        Key={"repair_id": repair_id},
        ConsistentRead=True
    )

    item = response.get("Item")

    if item is None:
        return None

    return Repair(**item)

def create_repair(repair: Repair):
    """Create a repair without overwriting an existing one."""

    table = get_table()

    try:
        table.put_item(
            Item=repair.model_dump(),
            ConditionExpression="attribute_not_exists(repair_id)"
        )

    except ClientError as error:
        error_code = error.response["Error"]["Code"]

        if error_code == "ConditionalCheckFailedException":
            raise ValueError("Repair ID already exists") from error

        raise

    return repair

def search_repairs(property_id: str, location: str, issue: str = ""):
    """Search open repairs belonging to a property."""

    table = get_table()
    results = []

    stop_words = {"the", "a", "an", "is", "under", "in", "on", "and"}
    search_words = set(normalize_issue(issue).split()) - stop_words

    scan_args = {
        "FilterExpression": Attr("property_id").eq(property_id)
    }

    while True:
        response = table.scan(**scan_args)

        for item in response.get("Items", []):
            repair = Repair(**item)

            if repair.location.lower() != location.lower():
                continue

            if repair.status.lower() != "open":
                continue

            repair_words = (
                set(normalize_issue(repair.issue).split()) - stop_words
            )

            if not search_words or search_words.issubset(repair_words):
                results.append(repair)

        last_key = response.get("LastEvaluatedKey")

        if not last_key:
            break

        scan_args["ExclusiveStartKey"] = last_key

    return results

def update_repair_priority(
    repair_id: str,
    requester_property_id: str,
    priority: str
):
    """Safely update a repair's priority."""

    if not priority.strip():
        raise ValueError("Priority cannot be empty")

    table = get_table()

    try:
        response = table.update_item(
            Key={"repair_id": repair_id},
            UpdateExpression="SET #priority = :priority",
            ConditionExpression=(
                "attribute_exists(repair_id) "
                "AND #property = :property_id"
            ),
            ExpressionAttributeNames={
                "#priority": "priority",
                "#property": "property_id"
            },
            ExpressionAttributeValues={
                ":priority": priority,
                ":property_id": requester_property_id
            },
            ReturnValues="ALL_NEW"
        )

    except ClientError as error:
        if error.response["Error"]["Code"] == (
            "ConditionalCheckFailedException"
        ):
            return None

        raise

    return Repair(**response["Attributes"])

def add_repair_update(
    repair_id: str,
    requester_property_id: str,
    update_text: str
):
    """Append a repair update without overwriting previous updates."""

    if not update_text.strip():
        raise ValueError("Update cannot be empty")

    table = get_table()

    try:
        response = table.update_item(
            Key={"repair_id": repair_id},
            UpdateExpression=(
                "SET #updates = list_append("
                "if_not_exists(#updates, :empty_list), :new_update)"
            ),
            ConditionExpression=(
                "attribute_exists(repair_id) "
                "AND #property = :property_id"
            ),
            ExpressionAttributeNames={
                "#updates": "updates",
                "#property": "property_id"
            },
            ExpressionAttributeValues={
                ":empty_list": [],
                ":new_update": [update_text.strip()],
                ":property_id": requester_property_id
            },
            ReturnValues="ALL_NEW"
        )

    except ClientError as error:
        if error.response["Error"]["Code"] == (
            "ConditionalCheckFailedException"
        ):
            return None

        raise

    return Repair(**response["Attributes"])

def generate_repair_id():
    """Generate a collision-resistant repair reference."""
    return f"HF-{uuid.uuid4().hex[:12].upper()}"