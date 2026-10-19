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
            await session.initialize()

            result = await session.list_tools()

            for tool in result.tools:
                print(tool.name)


asyncio.run(main())