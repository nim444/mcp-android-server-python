from fastmcp import FastMCP
import uiautomator2 as u2
from typing import Optional, TypedDict, List, Dict, Any
import shutil
import subprocess
import asyncio

# Create a basic server instance
mcp = FastMCP(
    name="Android Device Operator",
    instructions="""You are an expert Android device automation specialist using uiautomator2.

🚀 **AUTOMATIC DEVICE HANDLING**
All tools now automatically validate device connections and handle device_id intelligently.
- If no device_id is specified, tools will connect to the first available device
- Tools include built-in validation and clear error messages
- Never need to manually check connection state - tools handle it for you

📱 **RECOMMENDED WORKFLOWS**

**For device status and setup:**
1. `get_device_status()` - Get complete device readiness (recommended first step)
2. `connect_device()` - Establish connection with detailed validation
3. `unlock_screen()` + `screen_on()` - Prepare device for automation

**For app management:**
1. `get_installed_apps()` - Auto-connects and returns complete app list
2. `start_app()` - Launch apps with validation
3. `get_current_app()` - Check foreground app

**For UI automation:**
1. `wait_for_element()` - Wait for elements to appear
2. `click()`/`long_click()` - Interact with UI elements
3. `send_text()` - Input text with validation
4. `swipe()`/`drag()` - Perform gestures

**For debugging:**
1. `dump_hierarchy()` - Get complete UI structure
2. `screenshot()` - Capture current screen
3. `get_element_info()` - Detailed element properties
4. `get_toast()` - Check system messages

⚡ **SMART FEATURES**
- Automatic device connection management
- Built-in error handling and validation
- Detailed success/failure responses
- Clear guidance for troubleshooting
- No manual device ID management required

🎯 **RESPONSE FORMAT**
Always explain what you're doing, show results clearly, and suggest next steps.
When tools return structured responses, present the information in an organized, readable way.""",
)

# Type definitions for better type hints
class DeviceInfo(TypedDict):
    manufacturer: str
    model: str
    serial: str
    version: str
    sdk: int
    display: str
    product: str

class AppInfo(TypedDict):
    package_name: str
    version_name: str
    version_code: int
    first_install_time: str
    last_update_time: str

class ElementInfo(TypedDict):
    text: str
    resourceId: str
    description: str
    className: str
    enabled: bool
    clickable: bool
    bounds: Dict[str, Any]
    selected: bool
    focused: bool




# Health check tool for testing connection
@mcp.tool(name="mcp_health", description="Simple health check tool to verify MCP server is running")
def mcp_health() -> str:
    """Check if the MCP server is running and responsive.

    Returns:
        A greeting message confirming the server is operational
    """
    return "Hello, world! MCP Android Device Operator server is running."

# Smart workflow helper tools
@mcp.tool(
    name="get_device_status",
    description="Get complete device status including connection, ADB availability, and basic device info. This is the recommended first step to ensure everything is working before performing other operations."
)
def get_device_status() -> Dict[str, Any]:
    """Get comprehensive device status and connectivity information.

    This tool performs a complete check of the Android device setup including:
    - ADB availability and system status
    - Connected devices enumeration
    - Device connection and basic information
    - Screen state and readiness for automation

    Returns:
        Dictionary containing complete status information:
            - adb_available: Boolean indicating if ADB is accessible
            - connected_devices: List of available device IDs
            - device_connected: Boolean indicating if device connection succeeded
            - device_info: Basic device information (if connected)
            - screen_on: Boolean indicating if device screen is on
            - error: Any error messages (if applicable)
            - ready_for_automation: Boolean indicating if device is ready

    This is the perfect starting point for any Android automation workflow.
    It will guide you through any connection issues and provide clear next steps.
    """
    try:
        # Check ADB availability directly
        adb_path = shutil.which("adb")
        if not adb_path:
            return {
                "adb_available": False,
                "connected_devices": [],
                "device_connected": False,
                "device_info": {},
                "screen_on": False,
                "error": "ADB not available in PATH. Please install Android SDK platform-tools.",
                "ready_for_automation": False
            }

        # Check for connected devices
        try:
            result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().splitlines()
            devices = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "device":
                        devices.append(parts[0])
        except Exception as e:
            return {
                "adb_available": True,
                "connected_devices": [],
                "device_connected": False,
                "device_info": {},
                "screen_on": False,
                "error": f"Failed to check connected devices: {str(e)}",
                "ready_for_automation": False
            }

        status = {
            "adb_available": True,
            "connected_devices": devices,
            "device_connected": False,
            "device_info": {},
            "screen_on": False,
            "error": None,
            "ready_for_automation": False
        }

        if not devices:
            status["error"] = "No devices connected. Please connect device and enable USB debugging."
            return status

        # Try to connect and get basic info
        try:
            d = u2.connect()
            info = d.info
            device_info = {
                "manufacturer": info.get("manufacturer", ""),
                "model": info.get("model", ""),
                "serial": info.get("serial", ""),
                "version": info.get("version", {}).get("release", ""),
                "sdk": info.get("version", {}).get("sdk", 0),
            }

            status["device_connected"] = True
            status["device_info"] = device_info

            # Check screen state
            status["screen_on"] = d.screen_on()
            status["ready_for_automation"] = True

        except Exception as e:
            status["error"] = f"Device connection failed: {str(e)}"

        return status
    except Exception as e:
        return {
            "adb_available": False,
            "connected_devices": [],
            "device_connected": False,
            "device_info": {},
            "screen_on": False,
            "error": f"Status check failed: {str(e)}",
            "ready_for_automation": False
        }

# Device connection and information tools
@mcp.tool(
    name="connect_device",
    description="Connect to an Android device using uiautomator2 and return comprehensive device information. If device_id is not provided, automatically connects to the first available device."
)
def connect_device(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Connect to an Android device and retrieve detailed device information.

    This function establishes a connection to an Android device using uiautomator2
    and gathers comprehensive device information useful for automation and testing.
    If no device_id is provided, it will automatically connect to the first available device.

    Args:
        device_id: Optional device identifier (serial number). If not provided, connects to the first available device.

    Returns:
        Dictionary containing device details and connection status:
            - success: Boolean indicating if connection was successful
            - device_info: Dictionary with device details (if successful)
            - error: Error message (if connection failed)
            - device_id: The device ID that was connected to

    Device Info includes:
            - manufacturer: Device manufacturer (e.g., "Samsung", "Google")
            - model: Device model name (e.g., "Pixel 7", "Galaxy S23")
            - serial: Device serial number
            - version: Android version string (e.g., "13", "14")
            - sdk: Android SDK level (e.g., 33, 34)
            - display: Display density information
            - product: Product name identifier

    Note:
        - If no device_id is provided, connects to the first available device
        - Automatically checks ADB availability
        - Returns detailed success/failure information for debugging
    """
    try:
        # Check ADB availability directly (not calling MCP tool)
        adb_path = shutil.which("adb")
        if not adb_path:
            return {
                "success": False,
                "device_info": {},
                "error": "ADB is not available in PATH",
                "device_id": device_id
            }

        # Check for connected devices directly
        try:
            result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().splitlines()
            devices = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "device":
                        devices.append(parts[0])

            if not devices:
                return {
                    "success": False,
                    "device_info": {},
                    "error": "No Android devices connected. Please connect a device and ensure USB debugging is enabled.",
                    "device_id": device_id
                }
        except:
            return {
                "success": False,
                "device_info": {},
                "error": "Failed to check connected devices via ADB",
                "device_id": device_id
            }

        # Connect to device
        d = u2.connect(device_id)
        info = d.info
        device_info = {
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "serial": info.get("serial", ""),
            "version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0),
            "display": info.get("display", {}).get("density", ""),
            "product": info.get("productName", ""),
        }

        return {
            "success": True,
            "device_info": device_info,
            "error": None,
            "device_id": d.serial or device_id
        }
    except Exception as e:
        return {
            "success": False,
            "device_info": {},
            "error": f"Failed to connect to device: {str(e)}",
            "device_id": device_id
        }

@mcp.tool(
    name="get_device_info",
    description="Get comprehensive device information including serial number, screen resolution, Android version, SDK level, battery status, WiFi IP address, manufacturer, model, and current screen state"
)
def get_device_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve detailed information about the connected Android device.

    This function provides extensive device information useful for debugging,
    automation scripting, and device status monitoring.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device.

    Returns:
        Dictionary containing comprehensive device information:
            - success: Boolean indicating if operation was successful
            - device_info: Dictionary with device details (if successful)
            - error: Error message (if operation failed)
            - device_id: The device ID that was used

        Device info includes:
            - serial: Device serial number
            - resolution: Screen resolution as "WIDTHxHEIGHT" string
            - version: Android version number
            - sdk: Android SDK level
            - battery: Battery information dictionary (level, health, status)
            - wifi_ip: Device's WiFi IP address
            - manufacturer: Device manufacturer
            - model: Device model name
            - is_screen_on: Boolean indicating if screen is currently on
            - product: Product name

    Note:
        Returns error information if unable to retrieve device information.
    """
    try:
        d = u2.connect(device_id)
        info = d.info
        display = d.window_size()

        device_info = {
            "serial": d.serial,
            "resolution": f"{display[0]}x{display[1]}",
            "version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0),
            "battery": d.battery_info,
            "wifi_ip": d.wlan_ip,
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "is_screen_on": d.screen_on(),
            "product": info.get("productName", ""),
        }

        return {
            "success": True,
            "device_info": device_info,
            "error": None,
            "device_id": d.serial or device_id
        }
    except Exception as e:
        return {
            "success": False,
            "device_info": {},
            "error": f"Failed to get device info: {str(e)}",
            "device_id": device_id
        }

@mcp.tool(
    name="check_adb_and_list_devices",
    description="Check if ADB (Android Debug Bridge) is available in the system PATH and list all connected Android devices with their status"
)
def check_adb_and_list_devices() -> Dict[str, Any]:
    """Verify ADB availability and enumerate connected Android devices.

    This utility function checks if ADB is properly installed and accessible,
    then lists all Android devices currently connected via USB or network.

    Returns:
        Dictionary containing:
            - adb_exists: Boolean indicating if ADB command is found in PATH
            - devices: List of device serial numbers that are ready for automation
            - error: Error message if ADB check fails, None otherwise

    The devices list only includes devices with "device" status (ready for commands).
    Devices in "unauthorized" or other states are excluded.
    """
    adb_path = shutil.which("adb")
    if not adb_path:
        return {
            "adb_exists": False,
            "devices": [],
            "error": "adb command not found in PATH",
        }
    try:
        result = subprocess.run(
            [adb_path, "devices"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        devices = []
        for line in lines[1:]:
            if line.strip():
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    devices.append(parts[0])
        return {"adb_exists": True, "devices": devices, "error": None}
    except Exception as e:
        return {"adb_exists": True, "devices": [], "error": str(e)}

# Application management tools
@mcp.tool(
    name="get_installed_apps",
    description="Get a complete list of all installed applications on your Android device. Automatically connects to the first available device if no device_id is specified. Returns package names for all system and user-installed apps."
)
def get_installed_apps(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve a comprehensive list of all installed applications on the device.

    This function enumerates all applications installed on the Android device,
    including both system pre-installed apps and user-installed applications.
    Automatically handles device connection and validation.

    Args:
        device_id: Optional device identifier. If not provided, connects to the first available device.

    Returns:
        Dictionary containing:
            - success: Boolean indicating if operation was successful
            - apps: List of package names (if successful)
            - count: Total number of installed apps (if successful)
            - error: Error message (if operation failed)
            - device_id: The device ID that was used

    Example output:
        {
            "success": true,
            "apps": ["com.android.settings", "com.example.app", ...],
            "count": 245,
            "error": null,
            "device_id": "ABC123DEF456"
        }

    Note:
        - This may take several seconds on devices with many installed applications
        - Returns package names only, not detailed app information
        - Includes both system apps and user-installed apps
        - Automatically validates device connection before proceeding
    """
    try:
        # Direct ADB check first
        adb_path = shutil.which("adb")
        if not adb_path:
            return {
                "success": False,
                "apps": [],
                "count": 0,
                "error": "ADB is not available in PATH",
                "device_id": device_id
            }

        # Connect directly to device
        d = u2.connect(device_id)

        # Get installed apps
        apps = d.app_list()

        return {
            "success": True,
            "apps": apps,
            "count": len(apps),
            "error": None,
            "device_id": d.serial or device_id
        }
    except Exception as e:
        return {
            "success": False,
            "apps": [],
            "count": 0,
            "error": f"Failed to get installed apps: {str(e)}",
            "device_id": device_id
        }

@mcp.tool(
    name="get_current_app",
    description="Get detailed information about the currently active/foreground application including package name, activity, and version information"
)
def get_current_app(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve information about the application currently in the foreground.

    This function provides details about the app that the user is currently
    interacting with or which is running in the foreground.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device.

    Returns:
        Dictionary containing app information:
            - package: Package name of the foreground app
            - activity: Current activity name
            - pid: Process ID
            - Other app metadata as provided by uiautomator2
    """
    d = u2.connect(device_id)
    return d.app_current()

@mcp.tool(
    name="start_app",
    description="Launch an Android application by its package name with optional wait for the app to appear in foreground"
)
def start_app(
    package_name: str, device_id: Optional[str] = None, wait: bool = True
) -> bool:
    """Start an Android application using its package name.

    This function launches the specified app and optionally waits for it
    to appear in the foreground before returning.

    Args:
        package_name: The package name of the application to start (e.g., "com.example.app")
        device_id: Optional device identifier. If not provided, uses the first available device
        wait: Whether to wait for the app to come to the foreground (default: True)

    Returns:
        bool: True if the app was started successfully, False otherwise.
              When wait=True, returns True only if the app appears in foreground.

    Examples:
        >>> start_app("com.android.chrome")  # Launch Chrome and wait
        >>> start_app("com.example.app", wait=False)  # Launch immediately, don't wait
    """
    try:
        d = u2.connect(device_id)
        d.app_start(package_name)
        if wait:
            pid = d.app_wait(package_name, front=True)
            return pid is not None
        return True
    except Exception as e:
        print(f"Failed to start app {package_name}: {str(e)}")
        return False

@mcp.tool(
    name="stop_app",
    description="Force stop an Android application by its package name. Useful for closing apps that are misbehaving or for testing app restart scenarios."
)
def stop_app(package_name: str, device_id: Optional[str] = None) -> bool:
    """Stop a running Android application by its package name.

    This function force-stops the specified application, terminating all
    its processes and clearing it from memory.

    Args:
        package_name: The package name of the application to stop (e.g., "com.example.app")
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the app was stopped successfully, False otherwise

    Note:
        This is equivalent to the "Force Stop" action in Android app settings.
        The app will need to be relaunched to be used again.
    """
    try:
        d = u2.connect(device_id)
        d.app_stop(package_name)
        return True
    except Exception as e:
        print(f"Failed to stop app {package_name}: {str(e)}")
        return False

@mcp.tool(
    name="stop_all_apps",
    description="Force stop all running applications on the device to free up memory and start with a clean slate for testing"
)
def stop_all_apps(device_id: Optional[str] = None) -> bool:
    """Stop all running applications on the Android device.

    This function terminates all user applications running on the device,
    which is useful for testing scenarios that require a clean state.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if all apps were stopped successfully, False otherwise

    Note:
        This will not stop essential system services, only user applications.
        The device may take a few seconds to fully close all apps.
    """
    try:
        d = u2.connect(device_id)
        d.app_stop_all()
        return True
    except Exception as e:
        print(f"Failed to stop all apps: {str(e)}")
        return False

@mcp.tool(
    name="clear_app_data",
    description="Clear all data and cache for a specific app. This is equivalent to 'Clear Data' in Android app settings and will reset the app to its initial state."
)
def clear_app_data(package_name: str, device_id: Optional[str] = None) -> bool:
    """Clear all user data and cache for the specified application.

    This function completely resets an app to its initial installed state,
    clearing all preferences, databases, cache, and user data.

    Args:
        package_name: The package name of the application (e.g., "com.example.app")
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if app data was cleared successfully, False otherwise

    Warning:
        This action is irreversible and will delete all app data including
        login credentials, preferences, saved files, and databases.
        The app will behave as if freshly installed on next launch.
    """
    try:
        d = u2.connect(device_id)
        d.app_clear(package_name)
        return True
    except Exception as e:
        print(f"Failed to clear app data for {package_name}: {str(e)}")
        return False

# Screen control tools
@mcp.tool(
    name="screen_on",
    description="Turn the device screen on. Useful when the device has gone to sleep during automated testing."
)
def screen_on(device_id: Optional[str] = None) -> bool:
    """Turn on the device screen if it is currently off.

    This function wakes up the device and turns on the display,
    allowing UI automation to continue.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the screen was turned on successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screen_on()
        return True
    except Exception as e:
        print(f"Failed to turn screen on: {str(e)}")
        return False

@mcp.tool(
    name="screen_off",
    description="Turn the device screen off. Useful for testing how apps behave when device goes to sleep."
)
def screen_off(device_id: Optional[str] = None) -> bool:
    """Turn off the device screen.

    This function turns off the device display, putting it in sleep mode.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the screen was turned off successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screen_off()
        return True
    except Exception as e:
        print(f"Failed to turn screen off: {str(e)}")
        return False

@mcp.tool(
    name="unlock_screen",
    description="Unlock the device screen. This will wake the device if it's asleep and attempt to unlock it using the default method (swipe up or press home button)."
)
def unlock_screen(device_id: Optional[str] = None) -> bool:
    """Unlock the device screen if it is locked.

    This function will turn on the screen if it's off and attempt to unlock
    the device using the standard unlock method.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the screen was unlocked successfully, False otherwise

    Note:
        This may not work with complex security methods like PIN, pattern,
        password, or biometric authentication.
    """
    try:
        d = u2.connect(device_id)
        if not d.info["screenOn"]:
            d.screen_on()
        d.unlock()
        return True
    except Exception as e:
        print(f"Failed to unlock screen: {str(e)}")
        return False

@mcp.tool(
    name="wait_for_screen_on",
    description="Wait until the device screen is turned on. Useful for asynchronous operations where screen activation is expected."
)
async def wait_for_screen_on(device_id: str) -> str:
    """Asynchronously wait for the device screen to turn on.

    This function polls the device screen state and returns when the screen
    becomes active. Useful for scenarios where the screen state change
    might take time.

    Args:
        device_id: The device identifier to connect to

    Returns:
        str: Message confirming that the screen is now on

    Note:
        This is an async function that checks every second for the screen to turn on.
        It may wait indefinitely if the screen never turns on.
    """
    d = u2.connect(device_id)
    while not d.screen_on():
        await asyncio.sleep(1)
    return "Screen is now on"

# Input and gesture tools
@mcp.tool(
    name="press_key",
    description="Press a hardware or software key on the device. Common keys include: home, back, menu, volume_up, volume_down, power, enter, delete"
)
def press_key(key: str, device_id: Optional[str] = None) -> bool:
    """Simulate pressing a key on the Android device.

    This function sends a key event to the device, simulating both hardware
    button presses and software key presses.

    Args:
        key: The key to press. Common values include:
            - 'home': Home button
            - 'back': Back button
            - 'menu': Menu button
            - 'volume_up', 'volume_down': Volume buttons
            - 'power': Power button
            - 'enter': Enter key
            - 'delete': Delete/backspace key
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the key press was sent successfully, False otherwise

    Examples:
        >>> press_key("home")  # Press home button
        >>> press_key("back")  # Go back
    """
    try:
        d = u2.connect(device_id)
        d.press(key)
        return True
    except Exception as e:
        print(f"Failed to press key {key}: {str(e)}")
        return False

@mcp.tool(
    name="click",
    description="Click on a UI element identified by text, resource ID, or content description. Supports multiple selector types for flexible element targeting."
)
def click(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Click on a UI element on the device screen using various selector types.

    This function finds and clicks on UI elements using different identification
    methods. It's one of the most commonly used automation actions.

    Args:
        selector: The value to search for (text, resource ID, or content description)
        selector_type: The type of selector to use:
            - 'text': Search by visible text on the element
            - 'resourceId': Search by Android resource ID (e.g., "com.app:id/button")
            - 'description': Search by content description/accessibility label
        timeout: Maximum time in seconds to wait for the element to appear (default: 10.0)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the element was found and clicked successfully, False otherwise

    Examples:
        >>> click("Submit", "text")  # Click element with text "Submit"
        >>> click("com.app:id/login_btn", "resourceId")  # Click by resource ID
        >>> click("Login button", "description")  # Click by content description

    Raises:
        ValueError: If an invalid selector_type is provided
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector).wait(timeout=timeout)
        elif selector_type == "resourceId":
            el = d(resourceId=selector).wait(timeout=timeout)
        elif selector_type == "description":
            el = d(description=selector).wait(timeout=timeout)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            el.click()
            return True
        return False
    except Exception as e:
        print(f"Failed to click element {selector}: {str(e)}")
        return False

@mcp.tool(
    name="long_click",
    description="Perform a long click (press and hold) on a UI element. Useful for context menus, drag operations, or long press actions."
)
def long_click(
    selector: str,
    selector_type: str = "text",
    duration: float = 1.0,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a long click gesture on a UI element.

    This function simulates pressing and holding an element for a specified duration,
    which can trigger context menus, activate drag modes, or perform other long-press actions.

    Args:
        selector: The value to search for (text, resource ID, or content description)
        selector_type: The type of selector ('text', 'resourceId', or 'description')
        duration: Duration of the long click in seconds (default: 1.0)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the long click was performed successfully, False otherwise

    Examples:
        >>> long_click("Item", "text", 2.0)  # Long click for 2 seconds
        >>> long_click("com.app:id/draggable", "resourceId")  # Long click by ID
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector)
        elif selector_type == "resourceId":
            el = d(resourceId=selector)
        elif selector_type == "description":
            el = d(description=selector)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            el.long_click(duration=duration)
            return True
        return False
    except Exception as e:
        print(f"Failed to long click element {selector}: {str(e)}")
        return False

@mcp.tool(
    name="swipe",
    description="Perform a swipe gesture from one coordinate to another. Useful for scrolling, paging, or custom swipe actions."
)
def swipe(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    duration: float = 0.5,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a swipe gesture on the device screen.

    This function simulates a finger swipe from a start point to an end point,
    with control over the swipe duration for natural movement.

    Args:
        start_x: Starting X coordinate (0 to screen width)
        start_y: Starting Y coordinate (0 to screen height)
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Swipe duration in seconds (default: 0.5)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the swipe was performed successfully, False otherwise

    Examples:
        >>> swipe(100, 500, 100, 100)  # Swipe up
        >>> swipe(100, 100, 500, 100, 0.3)  # Swipe right quickly
        >>> swipe(300, 400, 300, 1000, 1.0)  # Slow swipe down

    Note:
        Coordinates are relative to the device screen resolution.
        Use (0, 0) for top-left corner.
    """
    try:
        d = u2.connect(device_id)
        d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        return True
    except Exception as e:
        print(f"Failed to perform swipe: {str(e)}")
        return False

@mcp.tool(
    name="drag",
    description="Drag a specific UI element to a target location on the screen. Useful for drag-and-drop operations, reordering items, or custom interactions."
)
def drag(
    selector: str,
    selector_type: str,
    to_x: int,
    to_y: int,
    device_id: Optional[str] = None,
) -> bool:
    """Drag a UI element to a specific location on the screen.

    This function finds an element and drags it to the specified coordinates,
    useful for drag-and-drop operations and custom UI interactions.

    Args:
        selector: The value to identify the element to drag
        selector_type: The type of selector ('text', 'resourceId', or 'description')
        to_x: Target X coordinate to drag the element to
        to_y: Target Y coordinate to drag the element to
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the drag operation was successful, False otherwise

    Examples:
        >>> drag("Item", "text", 200, 300)  # Drag text "Item" to coordinates (200, 300)
        >>> drag("com.app:id/card", "resourceId", 100, 100)  # Drag by resource ID
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector)
        elif selector_type == "resourceId":
            el = d(resourceId=selector)
        elif selector_type == "description":
            el = d(description=selector)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            el.drag_to(to_x, to_y)
            return True
        return False
    except Exception as e:
        print(f"Failed to drag element {selector}: {str(e)}")
        return False

# Text input tools
@mcp.tool(
    name="send_text",
    description="Send text input to the currently focused UI element. Can optionally clear existing text before sending. Perfect for form filling, search boxes, and text fields."
)
def send_text(text: str, clear: bool = True, device_id: Optional[str] = None) -> bool:
    """Send text to the currently focused input element on the device.

    This function types text into whatever UI element currently has focus,
    such as text fields, search boxes, or forms.

    Args:
        text: The text to send to the focused element
        clear: Whether to clear any existing text before sending (default: True)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the text was sent successfully, False otherwise

    Examples:
        >>> send_text("Hello World")  # Clear field and type "Hello World"
        >>> send_text("additional text", clear=False)  # Append to existing text
        >>> send_text("user@example.com")  # Type an email address

    Note:
        Make sure the target text field is focused before calling this function.
        Use click() to focus a text field if needed.
    """
    try:
        d = u2.connect(device_id)
        d.send_keys(text, clear=clear)
        return True
    except Exception as e:
        print(f"Failed to send text: {str(e)}")
        return False

# Element inspection and waiting tools
@mcp.tool(
    name="get_element_info",
    description="Get detailed information about a UI element including its properties, bounds, text, resource ID, class name, and interaction capabilities."
)
def get_element_info(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> ElementInfo:
    """Retrieve detailed information about a UI element.

    This function finds an element and returns comprehensive information about
    its properties, useful for debugging automation scripts or element inspection.

    Args:
        selector: The value to search for (text, resource ID, or content description)
        selector_type: The type of selector ('text', 'resourceId', or 'description')
        timeout: Maximum time in seconds to wait for the element (default: 10.0)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        ElementInfo dictionary containing:
            - text: Visible text on the element
            - resourceId: Android resource ID
            - description: Content description/accessibility label
            - className: Android class name (e.g., "android.widget.Button")
            - enabled: Whether the element is enabled
            - clickable: Whether the element can be clicked
            - bounds: Element position and size {"left": x, "top": y, "right": x2, "bottom": y2}
            - selected: Whether the element is selected
            - focused: Whether the element has focus

        Returns empty dictionary if element not found.
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            el = d(text=selector).wait(timeout=timeout)
        elif selector_type == "resourceId":
            el = d(resourceId=selector).wait(timeout=timeout)
        elif selector_type == "description":
            el = d(description=selector).wait(timeout=timeout)
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")

        if el and el.exists:
            info = el.info
            return {
                "text": info.get("text", ""),
                "resourceId": info.get("resourceId", ""),
                "description": info.get("contentDescription", ""),
                "className": info.get("className", ""),
                "enabled": info.get("enabled", False),
                "clickable": info.get("clickable", False),
                "bounds": info.get("bounds", {}),
                "selected": info.get("selected", False),
                "focused": info.get("focused", False),
            }
        return {}
    except Exception as e:
        print(f"Failed to get element info for {selector}: {str(e)}")
        return {}

@mcp.tool(
    name="wait_for_element",
    description="Wait for a UI element to appear on the screen. Essential for handling loading screens, animations, and dynamic content."
)
def wait_for_element(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Wait for a UI element to appear on the device screen.

    This function pauses execution until the specified element becomes visible
    or the timeout is reached. Essential for reliable automation.

    Args:
        selector: The value to search for (text, resource ID, or content description)
        selector_type: The type of selector ('text', 'resourceId', or 'description')
        timeout: Maximum time in seconds to wait (default: 10.0)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the element appeared within the timeout, False otherwise

    Examples:
        >>> wait_for_element("Loading complete", "text", 30)  # Wait up to 30 seconds
        >>> wait_for_element("com.app:id/result", "resourceId")  # Wait for resource ID
        >>> wait_for_element("Submit button", "description")  # Wait by content description

    Note:
        Use this function when dealing with dynamic content, loading screens,
        or network-dependent elements that may take time to appear.
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            return d(text=selector).wait(timeout=timeout)
        elif selector_type == "resourceId":
            return d(resourceId=selector).wait(timeout=timeout)
        elif selector_type == "description":
            el = d(description=selector).wait(timeout=timeout)
            return el is not None and el.exists
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")
    except Exception as e:
        print(f"Failed to wait for element {selector}: {str(e)}")
        return False

@mcp.tool(
    name="scroll_to",
    description="Scroll to a specific element on the screen. Automatically finds scrollable containers and scrolls until the target element is visible."
)
def scroll_to(
    selector: str, selector_type: str = "text", device_id: Optional[str] = None
) -> bool:
    """Scroll to make a UI element visible on the screen.

    This function automatically finds scrollable containers and scrolls until
    the target element becomes visible. Useful for long lists and pages.

    Args:
        selector: The value to search for (text, resource ID, or content description)
        selector_type: The type of selector ('text', 'resourceId', or 'description')
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the element was found and scrolled into view, False otherwise

    Examples:
        >>> scroll_to("Settings", "text")  # Scroll to element with text "Settings"
        >>> scroll_to("com.app:id/footer", "resourceId")  # Scroll by resource ID
        >>> scroll_to("Contact Us", "description")  # Scroll by content description

    Note:
        This function will scroll through all scrollable containers on the screen
        to find the target element. It may not work if the element is in a
        non-scrollable area or requires specific scroll directions.
    """
    try:
        d = u2.connect(device_id)
        if selector_type == "text":
            return d(scrollable=True).scroll.to(text=selector)
        elif selector_type == "resourceId":
            return d(scrollable=True).scroll.to(resourceId=selector)
        elif selector_type == "description":
            el = d(scrollable=True).scroll.to(description=selector)
            return el is not None and el.exists
        else:
            raise ValueError(f"Invalid selector_type: {selector_type}")
    except Exception as e:
        print(f"Failed to scroll to element {selector}: {str(e)}")
        return False

# Screenshot and visualization tools
@mcp.tool(
    name="screenshot",
    description="Capture a screenshot of the device screen and save it to the specified file path. Essential for debugging and visual verification."
)
def screenshot(filename: str, device_id: Optional[str] = None) -> bool:
    """Take a screenshot of the device screen and save it to a file.

    This function captures the current screen state and saves it as an image file,
    which is useful for debugging automation failures and creating visual documentation.

    Args:
        filename: The file path where the screenshot will be saved (e.g., "screenshot.png")
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the screenshot was saved successfully, False otherwise

    Examples:
        >>> screenshot("login_screen.png")  # Save as PNG
        >>> screenshot("/path/to/screenshots/error.png")  # Save with full path
        >>> screenshot(f"test_{timestamp}.jpg")  # Dynamic filename

    Note:
        Supported formats include PNG, JPG, and other common image formats.
        The directory must exist and be writable.
    """
    try:
        d = u2.connect(device_id)
        d.screenshot(filename)
        return True
    except Exception as e:
        print(f"Failed to take screenshot: {str(e)}")
        return False

@mcp.tool(
    name="dump_hierarchy",
    description="Dump the complete UI hierarchy of the current screen as XML. Essential for understanding screen structure, finding elements, and debugging automation issues."
)
def dump_hierarchy(
    compressed: bool = False,
    pretty: bool = True,
    max_depth: int = 50,
    device_id: Optional[str] = None,
) -> str:
    """Export the current screen's UI hierarchy as XML.

    This function provides a complete XML representation of all UI elements
    currently visible on the screen, which is invaluable for:
    - Finding elements for automation
    - Understanding screen structure
    - Debugging automation failures
    - Analyzing app UI changes

    Args:
        compressed: If True, excludes less important nodes for smaller output (default: False)
        pretty: If True, formats the XML with proper indentation (default: True)
        max_depth: Maximum depth of XML hierarchy to include (default: 50)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        str: XML string representing the complete UI hierarchy

    Examples:
        >>> dump_hierarchy()  # Full pretty-formatted hierarchy
        >>> dump_hierarchy(compressed=True)  # Smaller output for debugging
        >>> dump_hierarchy(max_depth=10)  # Limited depth for faster processing

    Note:
        The output can be very large for complex screens. Use compressed=True
        for quicker analysis when you don't need all details.
    """
    try:
        d = u2.connect(device_id)
        xml = d.dump_hierarchy(
            compressed=compressed, pretty=pretty, max_depth=max_depth
        )
        return xml
    except Exception as e:
        print(f"Failed to dump UI hierarchy: {str(e)}")
        return ""

# Advanced tools
@mcp.tool(
    name="get_toast",
    description="Retrieve the text of the last toast message displayed on the device. Useful for verifying notifications, error messages, and user feedback."
)
def get_toast(device_id: Optional[str] = None) -> str:
    """Get the text content of the most recent toast message.

    This function captures toast messages (temporary popup notifications) that
    appear briefly on screen, which can be useful for verifying operations
    or capturing system messages.

    Args:
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        str: The text content of the last toast message, or empty string if none found

    Examples:
        >>> get_toast()  # Get the last toast message
        # Returns: "Download completed successfully"

    Note:
        Toast messages are temporary and may disappear quickly.
        Call this function promptly after the action that triggers the toast.
        The function waits up to 10 seconds for a toast message.
    """
    try:
        d = u2.connect(device_id)
        return d.toast.get_message(10.0) or ""
    except Exception as e:
        print(f"Failed to get toast message: {str(e)}")
        return ""

@mcp.tool(
    name="wait_activity",
    description="Wait for a specific Android activity to appear on the screen. Useful for navigation verification and app state validation."
)
def wait_activity(
    activity: str, timeout: float = 10.0, device_id: Optional[str] = None
) -> bool:
    """Wait for a specific Android activity to become the current foreground activity.

    This function monitors the device and waits until the specified activity
    appears in the foreground, which is useful for verifying navigation
    and app state transitions.

    Args:
        activity: The full activity name to wait for (e.g., "com.example.app.MainActivity")
        timeout: Maximum time in seconds to wait (default: 10.0)
        device_id: Optional device identifier. If not provided, uses the first available device

    Returns:
        bool: True if the activity appeared within the timeout, False otherwise

    Examples:
        >>> wait_activity("com.android.settings.Settings")  # Wait for Settings
        >>> wait_activity("com.example.app.MainActivity", 30)  # Wait 30 seconds
        >>> wait_activity(".LoginActivity")  # Relative activity name

    Note:
        Activity names can be fully qualified (package + activity) or
        relative to the app package starting with a dot (.).
    """
    try:
        d = u2.connect(device_id)
        return d.wait_activity(activity, timeout=timeout)
    except Exception as e:
        print(f"Failed to wait for activity {activity}: {str(e)}")
        return False

if __name__ == "__main__":
    mcp.run(
        transport="stdio",
        show_banner=False,
    )

