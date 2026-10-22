import os

from app import database
from app import dynamodb_store
from app.models import Repair


def get_backend():
    """Select the storage backend."""

    backend = os.getenv(
        "HOMEFIX_STORAGE_BACKEND", "json"
    ).strip().lower()

    if backend == "dynamodb":
        return dynamodb_store

    if backend == "json":
        return database

    raise ValueError("Invalid storage backend")


def search_repairs(property_id, location, issue=""):
    return get_backend().search_repairs(
        property_id, location, issue
    )


def get_repair_by_id(repair_id):
    return get_backend().get_repair_by_id(repair_id)


def create_repair(repair: Repair):
    return get_backend().create_repair(repair)


def generate_repair_id():
    return get_backend().generate_repair_id()


def update_repair(repair_id, requester_property_id, priority):
    backend = get_backend()

    if backend is dynamodb_store:
        return backend.update_repair_priority(
            repair_id, requester_property_id, priority
        )

    repair = backend.get_repair_by_id(repair_id)

    if repair is None or repair.property_id != requester_property_id:
        return None

    return backend.update_repair(repair_id, priority)


def update_repair_issue(repair_id, requester_property_id, update_text):
    backend = get_backend()

    if backend is dynamodb_store:
        return backend.add_repair_update(
            repair_id, requester_property_id, update_text
        )

    repair = backend.get_repair_by_id(repair_id)

    if repair is None or repair.property_id != requester_property_id:
        return None

    return backend.update_repair_issue(repair_id, update_text)