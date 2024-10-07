import json
import os

vcap_services = json.loads(os.getenv("VCAP_SERVICES", "{}"))

user_agent_service = next(
    ups
    for ups in vcap_services["user-provided"]
    if ups["name"] == "user-agent"
)

USER_AGENT = user_agent_service["credentials"]["USER_AGENT"]
