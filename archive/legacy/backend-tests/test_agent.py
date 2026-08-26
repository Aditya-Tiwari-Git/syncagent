from backend.agents.root_agent import (
    root_agent
)


print(
    "Agent loaded successfully"
)

print(
    f"Agent name: {root_agent.name}"
)

print(
    f"Tools: {len(root_agent.tools)}"
)