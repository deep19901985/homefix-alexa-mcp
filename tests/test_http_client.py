
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():
    url = "http://127.0.0.1:8000/mcp"

    async with streamable_http_client(url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()

            print("Available HTTP MCP tools:")
            for tool in tools.tools:
                print("-", tool.name)

            result = await session.call_tool(
                "get_repair_status",
                {"repair_id": "HF-1045"}
            )

            print("\nRepair result:")
            print(result)


asyncio.run(main())
