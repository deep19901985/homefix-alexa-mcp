


import asyncio
from mcp_server.server import mcp


async def main():
    result = await mcp.call_tool(
        "add_repair_update",
        {
            "repair_id": "HF-1042",
            "update_text": "Water is spreading further into the hallway",
            "confirmed": True
        }
    )

    print(result)


asyncio.run(main())
