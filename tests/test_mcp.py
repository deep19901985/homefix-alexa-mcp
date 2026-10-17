
# import asyncio
# from mcp_server.server import mcp


# async def main():
#     result = await mcp.call_tool(
#         "find_repairs",
#         {
#             "property_id": "P-101",
#             "location": "Kitchen",
#             "issue": "leaking"
#         }
#     )

#     print(result)


# asyncio.run(main())

# async def main():
#     result = await mcp.call_tool(
#         "report_repair",
#         {
#             "repair_id": "HF-1044",
#             "property_id": "P-101",
#             "location": "Kitchen",
#             "issue": "leaking",
#             "priority": "High"
#         }
#     )

#     print(result)

# 22

# async def main():
#     result = await mcp.call_tool(
#         "report_repair",
#         {
#             "repair_id": "HF-1044",
#             "property_id": "P-101",
#             "location": "Bedroom",
#             "issue": "Radiator not heating",
#             "priority": "Medium"
#         }
#     )

#     print(result)


# ----

# async def main():
#     result = await mcp.call_tool(
#         "change_repair_priority",
#         {
#             "repair_id": "HF-1044",
#             "priority": "High",
#             "confirmed": True
#         }
#     )

#     print(result)

# ----


# import asyncio
# from mcp_server.server import mcp


# async def main():
#     result = await mcp.call_tool(
#         "report_repair",
#         {
#             "repair_id": "HF-1045",
#             "property_id": "P-101",
#             "location": "Living Room",
#             "issue": "Window not closing properly",
#             "priority": "Medium"
#         }
#     )

#     print(result)



# asyncio.run(main())

# -----


# import asyncio
# from mcp_server.server import mcp


# async def main():
#     result = await mcp.call_tool(
#         "report_repair",
#         {
#             "repair_id": "HF-1045",
#             "property_id": "P-101",
#             "location": "Living Room",
#             "issue": "Window not closing properly",
#             "priority": "Medium",
#             "confirmed": True
#         }
#     )

#     print(result)


# asyncio.run(main())


# ------
# import asyncio
# from mcp_server.server import mcp


# async def main():
#     result = await mcp.call_tool(
#         "report_repair",
#         {
#             "property_id": "P-101",
#             "location": "Hallway",
#             "issue": "Ceiling light flickering",
#             "priority": "Medium",
#             "confirmed": True
#         }
#     )

#     print(result)


# asyncio.run(main())
# ---

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
