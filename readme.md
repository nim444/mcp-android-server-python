[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/) [![CI Pipeline](https://github.com/nim444/mcp-android-server-python/actions/workflows/ci.yml/badge.svg?branch=main&label=CI%20Pipeline)](https://github.com/nim444/mcp-android-server-python/actions/workflows/ci.yml) [![Coverage: 90%](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](https://codecov.io/gh/nim444/sdet-django-api) [![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# MCP Android Agent

This project provides an **MCP (Model Context Protocol)** server for automating Android devices using [uiautomator2](https://github.com/openatx/uiautomator2). It's designed to be easily plugged into AI agents like GitHub Copilot Chat, Claude, or Open Interpreter to control Android devices through natural language.

## Quick Demo

![Demo](.docs/demo.gif)


![Demo](.docs/amazon.gif)
 


- Python 3.13 or higher
- Android Debug Bridge (adb) installed and in PATH
- Connected Android device with USB debugging enabled
- [uiautomator2](https://github.com/openatx/uiautomator2) compatible Android device

## Features

- Start, stop, and manage apps by package name
- Retrieve installed apps and current foreground app
- Tap, swipe, scroll, drag, and perform UI interactions
- Get device info, screen resolution, battery status, and more
- Capture screenshots or last toast messages
- Programmatically unlock, wake, or sleep the screen
- Clear app data and wait for activities
- Includes a health check and `adb` diagnostic tool

## Use Cases

Perfect for:

- AI agents that need to interact with real devices
- Remote device control setups
- Automated QA tools
- Android bot frameworks
- UI testing and automation
- Device management and monitoring

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/nim444/mcp-android-server-python.git
cd mcp-android-server-python
```

### 2. Create and activate virtual environment

```bash
# Using uv (https://github.com/astral-sh/uv)
uv venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
uv pip install .
```

## Running the Server

This server supports two transport modes: **stdio** (for local AI agent integration) and **TCP** (for remote or network access).

### Option 1: stdio (Default - for AI agents)

This is the default mode for local integration with Claude Desktop, VS Code, etc.

```bash
# Default stdio mode
python server.py

# Or using module form
python -m server
```

### Option 2: TCP/SSE (for network access)

Run the server over TCP using Server-Sent Events (SSE) for remote access:

```bash
# Start server on default host (127.0.0.1:8000)
python server.py --tcp

# Customize host and port via environment variables
MCP_HOST=0.0.0.0 MCP_PORT=8080 python server.py --tcp

# Or set MCP_TRANSPORT environment variable
MCP_TRANSPORT=tcp python server.py
```

The server will display the SSE endpoint URL when started in TCP mode:

```text
Starting MCP server over TCP at 127.0.0.1:8000
SSE endpoint: http://127.0.0.1:8000/sse
```

**TCP Mode Configuration:**

- **Host**: Set via `MCP_HOST` environment variable (default: `127.0.0.1`)
- **Port**: Set via `MCP_PORT` environment variable (default: `8000`)
- **SSE Path**: Fixed at `/sse` (MCP standard)

**Note**: TCP mode uses SSE (Server-Sent Events) transport, which is supported by MCP clients that can connect to remote servers.

## Usage

An MCP client is needed to use this server. The Claude Desktop app is an example of an MCP client.

### Using stdio mode (Local AI agents)

#### With Claude Desktop

Locate your Claude Desktop configuration file:

- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add the Android MCP server configuration to the mcpServers section:

```json
{
  "mcpServers": {
    "mcp-android": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/mcp-android-server-python && source .venv/bin/activate && python -m server"
      ]
    }
  }
}
```

Replace `/path/to/mcp-android-server-python` with the absolute path to where you cloned this repository. For example: `/home/username/Projects/mcp-android-server-python`

#### With VS Code

You can also use this MCP server with VS Code's agent mode (requires VS Code 1.99 or newer). To set up:

1. Create a `.vscode/mcp.json` file in your workspace:

```json
{
  "servers": {
    "mcp-android": {
      "type": "stdio",
      "command": "bash",
      "args": [
        "-c",
        "cd /path/to/mcp-android-server-python && source .venv/bin/activate && python -m server"
      ]
    }
  }
}
```

Replace `/path/to/mcp-android-server-python` with the absolute path to where you cloned this repository.

After adding the configuration, you can manage the server using:

- Command Palette → `MCP: List Servers` to view and manage configured servers
- Command Palette → `MCP: Start Server` to start the server
- The server's tools will be available in VS Code's agent mode chat

![Vscode](.docs/mcp-vscode.png)

### Using TCP mode (Remote/Network access)

For clients that support SSE transport (like custom MCP clients or remote setups), you can connect to the TCP endpoint.

1. Start the server in TCP mode:

```bash
# Start on localhost
python server.py --tcp

# Or bind to all interfaces for remote access
MCP_HOST=0.0.0.0 MCP_PORT=8080 python server.py --tcp
```

1. Configure your MCP client to connect to the SSE endpoint:
   - **Endpoint URL**: `http://host:port/sse` (e.g., `http://127.0.0.1:8000/sse`)
   - **Transport**: SSE (Server-Sent Events)

**Security Note**: When binding to `0.0.0.0`, the server will be accessible from the network. Consider using firewall rules or running behind a reverse proxy for production use.

## UI Inspector

The project includes support for uiauto.dev, a powerful UI inspection tool for viewing and analyzing your device's interface structure.

1. Install the UI inspector:

```bash
uv pip install uiautodev
```

1. Start the inspector:

```bash
uiauto.dev
```

1. Open your browser and navigate to <https://uiauto.dev>

![Ui](.docs/ui.png)

## Available MCP Tools

| Tool Name             | Description                                                              |
|-----------------------|--------------------------------------------------------------------------|
| `mcp_health`          | Check if the MCP server is running properly                              |
| `connect_device`      | Connect to an Android device and get basic info                          |
| `get_installed_apps`  | List all installed apps with version and package info                    |
| `get_current_app`     | Get info about the app currently in the foreground                       |
| `start_app`           | Start an app by its package name                                         |
| `stop_app`            | Stop an app by its package name                                          |
| `stop_all_apps`       | Stop all currently running apps                                          |
| `screen_on`           | Turn on the screen                                                       |
| `screen_off`          | Turn off the screen                                                      |
| `get_device_info`     | Get detailed device info: serial, resolution, battery, etc.              |
| `press_key`           | Simulate hardware key press (e.g. `home`, `back`, `menu`, etc.)          |
| `unlock_screen`       | Unlock the screen (turn on and swipe if necessary)                       |
| `check_adb`           | Check if ADB is installed and list connected devices                     |
| `wait_for_screen_on`  | Wait asynchronously until the screen is turned on                        |
| `click`               | Tap on an element by `text`, `resourceId`, or `description`              |
| `long_click`          | Perform a long click on an element                                       |
| `send_text`           | Input text into currently focused field (optionally clearing before)     |
| `get_element_info`    | Get info on UI elements (text, bounds, clickable, etc.)                  |
| `swipe`               | Swipe from one coordinate to another                                     |
| `wait_for_element`    | Wait for an element to appear on screen                                  |
| `screenshot`          | Take and save a screenshot from the device                               |
| `scroll_to`           | Scroll until a given element becomes visible                             |
| `drag`                | Drag an element to a specific screen location                            |
| `get_toast`           | Get the last toast message shown on screen                               |
| `clear_app_data`      | Clear user data/cache of a specified app                                 |
| `wait_activity`       | Wait until a specific activity appears                                   |
| `dump_hierarchy`      | Dump the UI hierarchy of the current screen as XML                       |

## License


This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
