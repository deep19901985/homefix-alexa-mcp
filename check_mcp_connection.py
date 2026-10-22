import os
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_URL = os.getenv(
    "MCP_URL",
    "http://127.0.0.1:8000/mcp"
)
async def main():
    # async with streamable_http_client(
    #     "http://127.0.0.1:8001/mcp"
    # ) as (read, write, _):
    async with streamable_http_client(
          MCP_URL
     ) as (read, write, _):
        async with ClientSession(read, write) as session:
            # await session.initialize()

            # result = await session.list_tools()
            init_result = await session.initialize()

            print("MCP Protocol Version:", init_result.protocolVersion)

            result = await session.list_tools()

            # for tool in result.tools:
            #     print(tool.name)
            # for tool in result.tools:
            #       print(tool.name)
            #       if tool.name == "find_repairs":
            #           print("Input schema:", tool.inputSchema)

            # ---python .\check_mcp_connection.py
            for tool in result.tools:
                print(tool.name)
                if tool.name == "find_repairs":
                    print("Input schema:", tool.inputSchema)

            # Test the find_repairs MCP tool
            print("\nTesting find_repairs...")

            response = await session.call_tool(
                "find_repairs",
                arguments={
                    "property_id": "TEST-001",
                    "location": "kitchen",
                    "issue": "leak"
                }
            )

            print("Tool error:", response.isError)
            print("Tool response:", response.content)
asyncio.run(main())