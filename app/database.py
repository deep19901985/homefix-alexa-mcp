
# import json
# from pathlib import Path

# DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "repairs.json"

# def get_repairs():
#     with open(DATA_FILE, "r", encoding="utf-8") as file:
#         repairs = json.load(file)
#     return repairs

import json
from pathlib import Path
from app.models import Repair

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "repairs.json"

def get_repairs():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        repairs = json.load(file)

    return [Repair(**repair) for repair in repairs]


# search repair by id
def get_repair_by_id(repair_id: str):
    repairs = get_repairs()

    for repair in repairs:
        if repair.repair_id == repair_id:
            return repair

    return None


# def search_repairs(property_id: str, location: str):
#     repairs = get_repairs()
#     results = []

#     for repair in repairs:
#         if (
#             repair.property_id == property_id
#             and repair.location.lower() == location.lower()
#             and repair.status.lower() == "open"
#         ):
#             results.append(repair)

#     return results
# def search_repairs(property_id: str, location: str, issue: str = ""):
#     repairs = get_repairs()
#     results = []

#     for repair in repairs:
#         if (
#             repair.property_id == property_id
#             and repair.location.lower() == location.lower()
#             and repair.status.lower() == "open"
#             and issue.lower() in repair.issue.lower()
#         ):
#             results.append(repair)

#     return results
# Normalize issue descriptions
def normalize_issue(text: str):
    text = text.lower()

    replacements = {
        "dripping": "leak",
        "leaking": "leak",
        "leaks": "leak",
        "broken": "not working",
        "faulty": "not working"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text

#  search repairs by various parameter

def search_repairs(property_id: str, location: str, issue: str = ""):
    repairs = get_repairs()
    results = []

    stop_words = {"the", "a", "an", "is", "under", "in", "on", "and"}

    search_words = set(normalize_issue(issue).split()) - stop_words

    for repair in repairs:
        if (
            repair.property_id == property_id
            and repair.location.lower() == location.lower()
            and repair.status.lower() == "open"
        ):
            if not search_words:
                results.append(repair)
                continue

            repair_words = (
                set(normalize_issue(repair.issue).split()) - stop_words
            )

            if search_words.issubset(repair_words):
                results.append(repair)

    return results

# def search_repairs(property_id: str, location: str, issue: str = ""):
#     repairs = get_repairs()
#     results = []

#     for repair in repairs:
#         if (
#             repair.property_id == property_id
#             and repair.location.lower() == location.lower()
#             and repair.status.lower() == "open"
#             and issue.lower() in repair.issue.lower()
#         ):
#             results.append(repair)

#     return results

# save the records

def save_repairs(repairs: list[Repair]):
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            [repair.model_dump() for repair in repairs],
            file,
            indent=2
        )

# save repair

def create_repair(repair: Repair):
    repairs = get_repairs()

    for existing in repairs:
        if existing.repair_id == repair.repair_id:
            raise ValueError("Repair ID already exists")

    repairs.append(repair)
    save_repairs(repairs)

    return repair

# update an existing pair

def update_repair(repair_id: str, priority: str):
    repairs = get_repairs()

    for repair in repairs:
        if repair.repair_id == repair_id:
            repair.priority = priority
            save_repairs(repairs)
            return repair

    return None


#  update repair issues description

# def update_repair_issue(repair_id: str, new_issue: str):
#     repairs = get_repairs()

#     for repair in repairs:
#         if repair.repair_id == repair_id:
#             repair.issue = new_issue
#             save_repairs(repairs)
#             return repair

#     return None

def update_repair_issue(repair_id: str, new_issue: str):
    repairs = get_repairs()

    for repair in repairs:
        if repair.repair_id == repair_id:
            repair.updates.append(new_issue)
            save_repairs(repairs)
            return repair

    return None


# auto id generation

def generate_repair_id():
    repairs = get_repairs()

    numbers = []

    for repair in repairs:
        number = int(repair.repair_id.split("-")[1])
        numbers.append(number)

    next_number = max(numbers, default=1000) + 1

    return f"HF-{next_number}"
