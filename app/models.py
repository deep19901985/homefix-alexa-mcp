
from pydantic import BaseModel, Field


class Repair(BaseModel):
    repair_id: str
    property_id: str
    location: str
    issue: str
    priority: str
    status: str
    updates: list[str] = Field(default_factory=list)