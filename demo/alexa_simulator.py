"""HomeFix guided Alexa+-style demo, backed by the deployed AWS MCP tools.

This is a simulation, NOT a connection to Alexa+ or an authenticated tenant app.
Use only synthetic records and run locally.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import streamlit as st

RUNTIME = "HomeFixMCP"
TARGET = "default"
REGION = "eu-west-2"
PROFILE = "homefix-admin"
PROPERTY = "DEMO-001"  # Synthetic tenant/property only
PROJECT_DIR = Path.home() / "homefix-agentcore" / "HomeFixDeploy"


def invoke_tool(tool_name: str, arguments: dict):
    """Call an actual MCP tool in the existing AWS AgentCore runtime."""
    executable = shutil.which("agentcore")
    if executable is None:
        raise RuntimeError("AgentCore CLI not found. Check `agentcore --help` in PowerShell.")
    if not PROJECT_DIR.exists():
        raise RuntimeError(f"AgentCore project folder not found: {PROJECT_DIR}")

    payload = json.dumps(arguments, separators=(",", ":"))
    command = [
        executable, "invoke", "call-tool", "--tool", tool_name,
        "--input", payload, "--runtime", RUNTIME, "--target", TARGET,
    ]
    env = os.environ.copy()
    env["AWS_PROFILE"] = PROFILE
    env["AWS_REGION"] = REGION

    result = subprocess.run(
        command,
        cwd=str(PROJECT_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
        shell=False,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise RuntimeError(details[-900:] or "AgentCore invocation failed.")
    try:
        return json.loads(result.stdout.strip())
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Unexpected AgentCore output: {result.stdout[-600:]}") from exc


def repair_list(response):
    if isinstance(response, list):
        return [item for item in response if isinstance(item, dict)]
    if isinstance(response, dict):
        if "repair_id" in response:
            return [response]
        for field in ("repairs", "existing_repairs", "result"):
            value = response.get(field)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def reset():
    st.session_state.stage = "issue"
    st.session_state.repair_id = None
    st.session_state.severity = ""
    st.session_state.messages = [
        {"role": "assistant", "content":
         "Hello! I'm HomeFix, your simulated Alexa+ repair assistant. "
         "What repair problem can I help you with?"}
    ]


st.set_page_config(page_title="HomeFix | Alexa+ Simulation", page_icon="🏠")
st.title("🏠 HomeFix")
st.caption("Alexa+-style guided conversation · Real AWS AgentCore MCP tools · Synthetic data only")
st.info("This is a local hackathon simulation, **not** a real Alexa+ device integration or authenticated tenant service.")

if "stage" not in st.session_state:
    reset()

with st.sidebar:
    st.subheader("Demo environment")
    st.write("**Property:** DEMO-001 (synthetic)")
    st.write("**Runtime:** HomeFixMCP")
    st.write("**AWS region:** London (eu-west-2)")
    st.write("**Scenario:** Kitchen sink leak")
    if st.button("Start a new conversation"):
        reset()
        st.rerun()
    st.caption("Run locally only. Tenant identity is not independently authenticated.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if user_text := st.chat_input("Type a tenant message..."):
    st.session_state.messages.append({"role": "user", "content": user_text})
    answer = ""
    stage = st.session_state.stage
    lower = user_text.lower().strip()

    try:
        with st.spinner("HomeFix is responding..."):
            if stage == "issue":
                if "sink" in lower and ("leak" in lower or "water" in lower or "drip" in lower):
                    st.session_state.stage = "severity"
                    answer = "Is the water contained under the sink, or is it spreading onto the floor?"
                else:
                    answer = "For this demo, try: 'There's water leaking under my kitchen sink.'"

            elif stage == "severity":
                st.session_state.severity = user_text
                found = invoke_tool("find_repairs", {
                    "property_id": PROPERTY, "location": "Kitchen", "issue": ""
                })
                candidates = repair_list(found)
                existing = next((r for r in candidates
                                 if "sink" in r.get("issue", "").lower()
                                 and ("leak" in r.get("issue", "").lower()
                                      or "drip" in r.get("issue", "").lower())), None)
                if existing:
                    st.session_state.repair_id = existing["repair_id"]
                    st.session_state.stage = "confirm_update"
                    answer = (f"I found an existing kitchen sink repair: **{existing['repair_id']}**. "
                              "Would you like me to record your update and mark it **Urgent**?")
                else:
                    st.session_state.stage = "confirm_create"
                    answer = ("I didn't find an existing kitchen sink repair for this demonstration property. "
                              "Would you like me to create an **Urgent** repair report?")

            elif stage in ("confirm_update", "confirm_create"):
                yes = lower in ("yes", "yes please", "sure", "ok", "okay", "confirm", "please do") or lower.startswith("yes,")
                if not yes:
                    if lower in ("no", "cancel", "no thanks"):
                        st.session_state.stage = "complete"
                        answer = "No change made. I haven't updated or created a repair."
                    else:
                        answer = "Please reply 'yes' to confirm, or 'no' to cancel."
                elif stage == "confirm_update":
                    repair_id = st.session_state.repair_id
                    priority = invoke_tool("change_repair_priority", {
                        "repair_id": repair_id,
                        "priority": "Urgent",
                        "confirmed": True,
                        "requester_property_id": PROPERTY,
                    })
                    if isinstance(priority, dict) and priority.get("error"):
                        raise RuntimeError(str(priority["error"]))
                    updated = invoke_tool("add_repair_update", {
                        "repair_id": repair_id,
                        "update_text": f"Tenant says: {st.session_state.severity} (synthetic Alexa-style demo)",
                        "confirmed": True,
                        "requester_property_id": PROPERTY,
                    })
                    if isinstance(updated, dict) and updated.get("error"):
                        raise RuntimeError(str(updated["error"]))
                    st.session_state.stage = "complete"
                    answer = (f"Done! Repair **{repair_id}** is marked **Urgent**, "
                              "and your update has been recorded in DynamoDB through AWS AgentCore.")
                else:
                    created = invoke_tool("report_repair", {
                        "property_id": PROPERTY,
                        "location": "Kitchen",
                        "issue": "Kitchen sink leaking (synthetic Alexa-style demo)",
                        "priority": "Urgent",
                        "confirmed": True,
                    })
                    if isinstance(created, dict) and created.get("error"):
                        raise RuntimeError(str(created["error"]))
                    if isinstance(created, dict) and created.get("repair_id"):
                        st.session_state.stage = "complete"
                        answer = f"Done! Your urgent repair reference is **{created['repair_id']}**."
                    else:
                        answer = f"The backend responded: {created}. Please review before continuing."

            else:
                answer = "The demo is complete. Use **Start a new conversation** to try again."
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        answer = (f"**AWS tool call could not complete:** {exc}. "
                  "Check your `homefix-admin` login and AgentCore runtime. No success is being claimed.")

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
