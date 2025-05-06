[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/)

# MCP Android Agent

This project provides an **MCP (Model Context Protocol)** server for automating Android devices using [uiautomator2](https://github.com/openatx/uiautomator2). It's designed to be easily plugged into AI agents like GitHub Copilot Chat, Claude, or Open Interpreter to control Android devices through natural language.

## Quick Demo

![Demo](.docs/demo.gif)
---

## 🚀 Features

- Start, stop, and manage apps by package name
- Retrieve installed apps and current foreground app
- Tap, swipe, scroll, drag, and perform UI interactions
- Get device info, screen resolution, battery status, and more
- Capture screenshots or last toast messages
- Programmatically unlock, wake, or sleep the screen
- Clear app data and wait for activities
- Includes a health check and `adb` diagnostic tool

---

## ✅ Use Case

Perfect for:

- AI agents that need to interact with real devices
- Remote device control setups
- Automated QA tools
- Android bot frameworks

---

## 🤖 Available MCP Tools

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

---

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/nim444/mcp-android.git
cd mcp-android
```

### 2. Create and activate virtual environment

```bash
# Using uv (https://github.com/astral-sh/uv)
uv venv
source .venv/bin/activate
```

### 3. Install dependencies (from pyproject.toml)

```bash
uv pip install
```

### 4. Run with uvicorn (recommended)

```bash
uvicorn server:app --factory --host 0.0.0.0 --port 8000
```

Alternatively, run with MCP stdio (for AI agent integration):

```bash
python server.py
```
