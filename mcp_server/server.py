
from mcp.server.fastmcp import FastMCP
# from app.database import search_repairs
from app.database import search_repairs, get_repair_by_id, create_repair,  update_repair, generate_repair_id, update_repair_issue
from app.models import Repair
# Create our MCP server
mcp = FastMCP("HomeFix")


@mcp.tool()
def find_repairs(
    property_id: str,
    location: str,
    issue: str = ""
) -> list[dict]:
    """Find open repair reports for a property, room and issue."""

    repairs = search_repairs(property_id, location, issue)

    return [repair.model_dump() for repair in repairs]


#  mcp tool 2 getrepair status

@mcp.tool()
def get_repair_status(repair_id: str) -> dict:
    """Retrieve the details and current status of a repair."""

    repair = get_repair_by_id(repair_id)

    if repair is None:
        return {"error": "Repair not found"}

    return repair.model_dump()

# tool 3  reportrepair
@mcp.tool()
def report_repair(
    # repair_id: str,
    property_id: str,
    location: str,
    issue: str,
    priority: str = "Medium",
    confirmed: bool = False
) -> dict:
    """Create a new repair report after tenant confirmation."""

    existing = search_repairs(property_id, location, issue)

    if existing:
        return {
            "message": "Possible existing repair found",
            "existing_repairs": [
                repair.model_dump() for repair in existing
            ]
        }

    if not confirmed:
        return {
            "message": "Confirmation required before creating repair"
        }
    
    repair_id = generate_repair_id()

    repair = Repair(
    # repair = Repair(
        repair_id=repair_id,
        property_id=property_id,
        location=location,
        issue=issue,
        priority=priority,
        status="Open"
    )

    try:
        created = create_repair(repair)
        return created.model_dump()
    except ValueError as error:
        return {"error": str(error)}
# tool 4 

@mcp.tool()
def change_repair_priority(
    repair_id: str,
    priority: str,
    confirmed: bool = False
) -> dict:
    """Change repair priority only after explicit confirmation."""

    if not confirmed:
        return {
            "message": "Confirmation required before updating repair"
        }

    if priority not in ["Low", "Medium", "High", "Urgent"]:
        return {"error": "Invalid priority"}

    updated = update_repair(repair_id, priority)

    if updated is None:
        return {"error": "Repair not found"}

    return updated.model_dump()

# ---tool 5


@mcp.tool()
def add_repair_update(
    repair_id: str,
    update_text: str,
    confirmed: bool = False
) -> dict:
    """Add a tenant update to an existing repair after confirmation."""

    if not confirmed:
        return {
            "message": "Confirmation required before adding update"
        }

    if not update_text.strip():
        return {"error": "Update cannot be empty"}

    updated = update_repair_issue(repair_id, update_text)

    if updated is None:
        return {"error": "Repair not found"}

    return updated.model_dump()


# if __name__ == "__main__":
#     mcp.run()

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
