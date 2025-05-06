<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# MCP-UIAutomator2 Server Instructions

This workspace contains a Model Context Protocol (MCP) server that integrates with UIAutomator2 for Android automation.

## Key Information

- This is an MCP server project. You can find more info and examples at <https://github.com/modelcontextprotocol/python-sdk>
- The server uses UIAutomator2 for Android automation: <https://github.com/openatx/uiautomator2>
- The main server implementation is in `src/server.py`
- The server exposes MCP functions to interact with Android devices via UIAutomator2
- Tests are located in the `tests` directory

## Development Guidelines

- Maintain compatibility with the Model Context Protocol specification
- Keep function signatures consistent with UIAutomator2 API
- Ensure proper error handling for all device interactions
- Add docstrings for all MCP functions describing parameters and return values
- Write unit tests for new functions
