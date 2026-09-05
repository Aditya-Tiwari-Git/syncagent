import os


def create_clickhouse_mcp_toolset():
    """Create the optional ClickHouse MCP toolset when ADK supports it.

    The deterministic Python ClickHouse search remains the local fallback. This
    keeps the agent importable when the installed ADK and MCP releases have
    incompatible protocol helper versions.
    """
    if os.getenv("CLICKHOUSE_MCP_ENABLED", "false").lower() != "true":
        return None

    try:
        from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import (
            StdioConnectionParams,
        )
        from mcp import StdioServerParameters
    except ImportError:
        return None

    return McpToolset(
        connection_params=(
            StdioConnectionParams(
                server_params=(
                    StdioServerParameters(
                        command="uv",

                        args=[
                            "run",
                            "--with",
                            "mcp-clickhouse",
                            "--python",
                            "3.11",
                            "mcp-clickhouse",
                        ],

                        env={
                            "CLICKHOUSE_HOST": os.getenv(
                                "CLICKHOUSE_HOST"
                            ),

                            "CLICKHOUSE_USER": os.getenv(
                                "CLICKHOUSE_USER"
                            ),

                            "CLICKHOUSE_PASSWORD": os.getenv(
                                "CLICKHOUSE_PASSWORD"
                            ),

                            "CLICKHOUSE_SECURE": os.getenv(
                                "CLICKHOUSE_SECURE",
                                "true",
                            ),

                            "CLICKHOUSE_CONNECT_TIMEOUT": "30",

                            "CLICKHOUSE_SEND_RECEIVE_TIMEOUT": "30",
                        },
                    )
                ),

                # ADK's default is 5 seconds.
                # uv + mcp-clickhouse can take longer to start.
                timeout=60.0,
            )
        )
    )
