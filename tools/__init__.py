"""
Android Device Operator - Tools Package

This package contains modular tools for Android device automation using uiautomator2.
Each module focuses on a specific category of device operations.

Modules:
- device_tools: Device connection, status, and information tools
- app_tools: Application management (install, start, stop, clear data)
- screen_tools: Screen control (on/off, unlock, wait for screen)
- input_tools: User input simulation (click, swipe, text input, key press)
- inspection_tools: UI element inspection and hierarchy analysis
- advanced_tools: Advanced features (toast messages, activity waiting)
"""

# Import all tool modules
from . import device_tools
from . import app_tools
from . import screen_tools
from . import input_tools
from . import inspection_tools
from . import advanced_tools


# Convenience function to register all tools at once
def register_all_tools(mcp):
    """Register all tool modules with the MCP server.

    Args:
        mcp: The FastMCP server instance
    """
    device_tools.register_device_tools(mcp)
    app_tools.register_app_tools(mcp)
    screen_tools.register_screen_tools(mcp)
    input_tools.register_input_tools(mcp)
    inspection_tools.register_inspection_tools(mcp)
    advanced_tools.register_advanced_tools(mcp)


# Export the registration function
__all__ = ["register_all_tools"]
