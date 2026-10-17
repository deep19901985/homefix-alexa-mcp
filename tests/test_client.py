
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mcp_server.server"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print("Available MCP tools:")
            for tool in tools.tools:
                print("-", tool.name)

            result = await session.call_tool(
                "get_repair_status",
                {"repair_id": "HF-1045"}
            )

            print("\nRepair result:")
            print(result)


asyncio.run(main())
