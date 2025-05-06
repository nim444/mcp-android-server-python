# server.py
from mcp.server.fastmcp import FastMCP
import uiautomator2 as u2
from typing import List, Optional, Dict, Any
import shutil
import subprocess
import asyncio
from typing import TypedDict

# Create an MCP server
mcp = FastMCP("MCP Server Android")


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


@mcp.tool(name="mcp_health", description="Simple mcp health tool")
def mcp_health() -> str:
    return "Hello, world!"


@mcp.tool(
    name="connect_device",
    description="Connect to an Android device and return device info with uiautomator2",
)
def connect_device(device_id: Optional[str] = None) -> DeviceInfo:
    """Connect to an Android device and get its information.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        Device information including manufacturer, model, etc.
    """
    try:
        d = u2.connect(device_id)
        info = d.info
        return {
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "serial": info.get("serial", ""),
            "version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0),
            "display": info.get("display", {}).get("density", ""),
            "product": info.get("productName", ""),
        }
    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to device with ID '{device_id}': {str(e)}"
        )


@mcp.tool(name="get_installed_apps", description="List installed apps")
def get_installed_apps(device_id: Optional[str] = None) -> List[AppInfo]:
    """Get a list of all installed applications on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        List of application information including package names and versions
    """
    d = u2.connect(device_id)
    return d.app_list()


@mcp.tool(name="get_current_app", description="Get info about the foreground app")
def get_current_app(device_id: Optional[str] = None) -> AppInfo:
    """Get information about the currently active application.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        Information about the current foreground application
    """
    d = u2.connect(device_id)
    return d.app_current()


@mcp.tool(name="start_app", description="Start an app by package name")
def start_app(
    package_name: str, device_id: Optional[str] = None, wait: bool = True
) -> bool:
    """Start an application by its package name.

    Args:
        package_name: The package name of the application to start
        device_id: Optional device ID to connect to
        wait: Whether to wait for the app to come to the foreground

    Returns:
        True if the app was started successfully, False otherwise
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


@mcp.tool(name="stop_app", description="Stop an app by package name")
def stop_app(package_name: str, device_id: Optional[str] = None) -> bool:
    """Stop an application by its package name.

    Args:
        package_name: The package name of the application to stop
        device_id: Optional device ID to connect to

    Returns:
        True if the app was stopped successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_stop(package_name)
        return True
    except Exception as e:
        print(f"Failed to stop app {package_name}: {str(e)}")
        return False


@mcp.tool(name="stop_all_apps", description="Stop all running apps")
def stop_all_apps(device_id: Optional[str] = None) -> bool:
    """Stop all running applications on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if all apps were stopped successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_stop_all()
        return True
    except Exception as e:
        print(f"Failed to stop all apps: {str(e)}")
        return False


@mcp.tool(name="screen_on", description="Turn screen on")
def screen_on(device_id: Optional[str] = None) -> bool:
    """Turn the device screen on.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if the screen was turned on successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screen_on()
        return True
    except Exception as e:
        print(f"Failed to turn screen on: {str(e)}")
        return False


@mcp.tool(name="screen_off", description="Turn screen off")
def screen_off(device_id: Optional[str] = None) -> bool:
    """Turn the device screen off.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if the screen was turned off successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screen_off()
        return True
    except Exception as e:
        print(f"Failed to turn screen off: {str(e)}")
        return False


@mcp.tool(name="get_device_info", description="Get detailed device information")
def get_device_info(device_id: Optional[str] = None) -> Dict[str, Any]:
    """Get detailed information about the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        A dictionary containing detailed device information
    """
    try:
        d = u2.connect(device_id)
        info = d.info
        display = d.window_size()
        return {
            "serial": d.serial,
            "resolution": f"{display[0]}x{display[1]}",
            "version": info.get("version", {}).get("release", ""),
            "sdk": info.get("version", {}).get("sdk", 0),
            "battery": d.battery_info,
            "wifi_ip": d.wlan_ip,
            "manufacturer": info.get("manufacturer", ""),
            "model": info.get("model", ""),
            "is_screen_on": d.screen_on(),
        }
    except Exception as e:
        print(f"Failed to get device info: {str(e)}")
        return {}


@mcp.tool(name="press_key", description="Press a key on the device")
def press_key(key: str, device_id: Optional[str] = None) -> bool:
    """Press a key on the device.

    Args:
        key: The key to press (e.g., 'home', 'back', 'menu', etc.)
        device_id: Optional device ID to connect to

    Returns:
        True if the key was pressed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.press(key)
        return True
    except Exception as e:
        print(f"Failed to press key {key}: {str(e)}")
        return False


@mcp.tool(name="unlock_screen", description="Unlock the device screen")
def unlock_screen(device_id: Optional[str] = None) -> bool:
    """Unlock the device screen.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        True if the screen was unlocked successfully, False otherwise
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


@mcp.tool(name="check_adb", description="Check ADB and list devices")
def check_adb_and_list_devices() -> Dict[str, Any]:
    """Check if ADB is available and list connected devices.

    Returns:
        A dictionary containing ADB status and connected devices
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


@mcp.tool(name="wait_for_screen_on", description="Wait until device screen is on")
async def wait_for_screen_on(device_id: str) -> str:
    """Wait until the device screen is turned on.

    Args:
        device_id: The device ID to connect to

    Returns:
        A message indicating the screen is now on
    """
    d = u2.connect(device_id)
    while not d.screen_on():
        await asyncio.sleep(1)
    return "Screen is now on"


@mcp.tool(
    name="click", description="Click on an element by text, description, or resource ID"
)
def click(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Click on an element on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the element was clicked successfully, False otherwise
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
    name="send_text",
    description="Send text to current focused element or clear and send if clear=True",
)
def send_text(text: str, clear: bool = True, device_id: Optional[str] = None) -> bool:
    """Send text to the currently focused element on the device.

    Args:
        text: The text to send
        clear: Whether to clear the existing text before sending
        device_id: Optional device ID to connect to

    Returns:
        True if the text was sent successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.send_keys(text, clear=clear)
        return True
    except Exception as e:
        print(f"Failed to send text: {str(e)}")
        return False


@mcp.tool(
    name="get_element_info",
    description="Get information about an element by text, description, or resource ID",
)
def get_element_info(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> ElementInfo:
    """Get information about an element on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        A dictionary containing information about the element
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


@mcp.tool(name="swipe", description="Perform a swipe gesture from one point to another")
def swipe(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    duration: float = 0.5,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a swipe gesture on the device screen.

    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        duration: Duration of the swipe
        device_id: Optional device ID to connect to

    Returns:
        True if the swipe was performed successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.swipe(start_x, start_y, end_x, end_y, duration=duration)
        return True
    except Exception as e:
        print(f"Failed to perform swipe: {str(e)}")
        return False


@mcp.tool(
    name="wait_for_element", description="Wait for an element to appear on screen"
)
def wait_for_element(
    selector: str,
    selector_type: str = "text",
    timeout: float = 10.0,
    device_id: Optional[str] = None,
) -> bool:
    """Wait for an element to appear on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        timeout: Timeout for waiting for the element
        device_id: Optional device ID to connect to

    Returns:
        True if the element appeared successfully, False otherwise
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
    name="screenshot", description="Take a screenshot and save it to the specified path"
)
def screenshot(filename: str, device_id: Optional[str] = None) -> bool:
    """Take a screenshot of the device screen.

    Args:
        filename: The file path to save the screenshot
        device_id: Optional device ID to connect to

    Returns:
        True if the screenshot was taken successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.screenshot(filename)
        return True
    except Exception as e:
        print(f"Failed to take screenshot: {str(e)}")
        return False


@mcp.tool(name="long_click", description="Long click on an element")
def long_click(
    selector: str,
    selector_type: str = "text",
    duration: float = 1.0,
    device_id: Optional[str] = None,
) -> bool:
    """Perform a long click on an element on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        duration: Duration of the long click
        device_id: Optional device ID to connect to

    Returns:
        True if the long click was performed successfully, False otherwise
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


@mcp.tool(name="scroll_to", description="Scroll to an element")
def scroll_to(
    selector: str, selector_type: str = "text", device_id: Optional[str] = None
) -> bool:
    """Scroll to an element on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        device_id: Optional device ID to connect to

    Returns:
        True if the scroll was performed successfully, False otherwise
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


@mcp.tool(name="drag", description="Drag an element to a specific location")
def drag(
    selector: str,
    selector_type: str,
    to_x: int,
    to_y: int,
    device_id: Optional[str] = None,
) -> bool:
    """Drag an element to a specific location on the device screen.

    Args:
        selector: The selector to identify the element
        selector_type: The type of selector ('text', 'resourceId', 'description')
        to_x: The X coordinate to drag to
        to_y: The Y coordinate to drag to
        device_id: Optional device ID to connect to

    Returns:
        True if the drag was performed successfully, False otherwise
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


@mcp.tool(name="get_toast", description="Get the text of the last toast message")
def get_toast(device_id: Optional[str] = None) -> str:
    """Get the text of the last toast message displayed on the device.

    Args:
        device_id: Optional device ID to connect to

    Returns:
        The text of the last toast message
    """
    try:
        d = u2.connect(device_id)
        return d.toast.get_message(10.0) or ""
    except Exception as e:
        print(f"Failed to get toast message: {str(e)}")
        return ""


@mcp.tool(name="clear_app_data", description="Clear an app's data")
def clear_app_data(package_name: str, device_id: Optional[str] = None) -> bool:
    """Clear the data of an application on the device.

    Args:
        package_name: The package name of the application
        device_id: Optional device ID to connect to

    Returns:
        True if the app data was cleared successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        d.app_clear(package_name)
        return True
    except Exception as e:
        print(f"Failed to clear app data for {package_name}: {str(e)}")
        return False


@mcp.tool(name="wait_activity", description="Wait for a specific activity to appear")
def wait_activity(
    activity: str, timeout: float = 10.0, device_id: Optional[str] = None
) -> bool:
    """Wait for a specific activity to appear on the device.

    Args:
        activity: The name of the activity to wait for
        timeout: Timeout for waiting for the activity
        device_id: Optional device ID to connect to

    Returns:
        True if the activity appeared successfully, False otherwise
    """
    try:
        d = u2.connect(device_id)
        return d.wait_activity(activity, timeout=timeout)
    except Exception as e:
        print(f"Failed to wait for activity {activity}: {str(e)}")
        return False


if __name__ == "__main__":
    # using uvicorn to run the server
    mcp.run(transport="stdio")
